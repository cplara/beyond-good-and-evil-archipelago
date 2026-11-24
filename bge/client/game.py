"""
Logica del juego para el cliente AP, independiente de la red (se puede probar sin servidor).

Reglas acordadas (ver memoria del proyecto):
- Un check es un bit de flag que pasa a 1. Se confirma en dos lecturas seguidas (lecturas en 0 descartadas).
- Al recoger un objeto, su recompensa vanilla se revierte (el item real viene del multiworld).
- Locations recogidas por otros (collect) se marcan en vivo: el objeto desaparece del mundo.
- Mejoras de Mammago: bloqueadas en la tienda hasta recibir su "Permiso".
- No se escribe durante 2 s tras un cambio de zona (el juego recarga el bloque de flags y pisa lo escrito).
- El indice de items aplicados vive en la partida (AP_ITEM_INDEX): al morir o recargar vuelve atras solo.
"""
import time
from dataclasses import dataclass, field
from typing import Iterable, Optional

from ..data import GOAL_LOCATION, LOCATION_IDS, LOCATIONS, SHOP_PERMITS, TRANSIENT_SPAWNS, place_name
from .memory import (AP_ITEM_INDEX, AP_SHOP_BOUGHT, CREDITS_FROM_INV, FLAGS_DELTA, FLAGS_END, FLAGS_START,
                     GameMemory, INV_END, INV_START, SAVEBUF, SHOP_TABLE, VIDA, VIDA_MAX)

ZONE_SETTLE_SECONDS = 2.0
HEART = 40.0

# Offsets de inventario (save)
INV_MECHAIMPULSOR = 0xA64
INV_SERVOS = 0xA68
INV_SETSERVOS = 0xA6C
INV_KBUPS = 0xA88
INV_HEART = 0xA9C
INV_STARKOS = 0xAA4
INV_TURBO = 0xAC0
INV_TURBOMOTOR = 0xC60
STARKOS_CAP = 99

ZOOM_FLAG = (0x3937, 0x20)
DEATH_FLAG = (0x3897, 0x01)
TURBOMOTOR_SLOT = SHOP_PERMITS["Permiso: Turbomotor"]

_LOC_BY_ID = {LOCATION_IDS[loc.name]: loc for loc in LOCATIONS}
GOAL_ID = LOCATION_IDS[GOAL_LOCATION]
_GROUPS = {}
for _loc in LOCATIONS:
    if _loc.group:
        _GROUPS.setdefault(_loc.group, []).append(LOCATION_IDS[_loc.name])


def _locations_from_flags(flags: bytes) -> set:
    """Location ids encendidas. En un grupo cuenta los bits y devuelve las primeras N del grupo."""
    ids = {LOCATION_IDS[loc.name] for loc in LOCATIONS
           if not loc.group and flags[loc.offset - FLAGS_START] & loc.mask}
    for members in _GROUPS.values():
        count = sum(1 for lid in members
                    if flags[_LOC_BY_ID[lid].offset - FLAGS_START] & _LOC_BY_ID[lid].mask)
        ids.update(members[:count])
    return ids


@dataclass
class TickResult:
    status: str = ""
    in_game: bool = False
    zone: Optional[tuple] = None
    entered: Optional[str] = None                 # nombre del lugar al que se acaba de entrar
    checked: set = field(default_factory=set)     # location ids con el bit encendido (confirmados)
    applied: list = field(default_factory=list)   # nombres de items aplicados en este tick
    reverted: list = field(default_factory=list)  # recompensas vanilla revertidas
    collected: list = field(default_factory=list) # objetos marcados por collect
    goal: bool = False
    died: bool = False                            # Jade murio (para enviar DeathLink)
    killed: bool = False                          # aplicamos un DeathLink recibido


class BGEGame:
    def __init__(self, mem: Optional[GameMemory] = None, dry_run: bool = False):
        self.mem = mem or GameMemory()
        self.dry_run = dry_run
        self._reset()

    def _reset(self):
        self.inv = None
        self.zone = None
        self.zone_since = 0.0
        self.announced_spawn = None
        self.pending_bits = set()
        self.prev_bits = None
        self.self_set = set()
        self.shop_written = {}
        self.was_dead = False
        self.killing = False

    # --- helpers de memoria ------------------------------------------------------
    def _w32(self, off: int, value: int):
        if not self.dry_run:
            self.mem.write_u32(self.inv + off, value)

    def _r32(self, off: int) -> int:
        return self.mem.u32(self.inv + off) or 0

    def _add(self, off: int, delta: int, cap: Optional[int] = None):
        value = max(0, self._r32(off) + delta)
        if cap is not None:
            value = min(value, cap)
        self._w32(off, value)

    def _flag_addr(self, offset: int) -> int:
        return self.inv + FLAGS_DELTA + offset

    def _set_flag(self, offset: int, mask: int, on: bool):
        addr = self._flag_addr(offset)
        cur = self.mem.read(addr, 1)
        if cur is None or self.dry_run:
            return
        new = (cur[0] | mask) if on else (cur[0] & ~mask & 0xFF)
        if new != cur[0]:
            self.mem.write(addr, bytes([new]))

    # --- recompensas vanilla y items ------------------------------------------------
    def _revert_vanilla(self, kind: str):
        if kind == "turbo":
            self._add(INV_TURBO, -1)
        elif kind == "servo":
            self._add(INV_SERVOS, -1)
        elif kind == "starkos":
            self._add(INV_STARKOS, -1)
        elif kind == "kbups":
            self._add(INV_KBUPS, -1)
        elif kind == "mechaimpulsor":
            self._add(INV_MECHAIMPULSOR, -1)
        elif kind == "setservos":
            self._add(INV_SETSERVOS, -1)
        elif kind == "heart":
            vmax = max(HEART, (self.mem.f32(self.inv + VIDA_MAX) or HEART) - HEART)
            if not self.dry_run:
                self.mem.write_f32(self.inv + VIDA_MAX, vmax)
                self.mem.write_f32(self.inv + VIDA, min(self.mem.f32(self.inv + VIDA) or vmax, vmax))
            self._add(INV_HEART, -1)
        # "zoom" se maneja por imposicion continua en _enforce_zoom

    def _apply_item(self, name: str):
        if name == "Capsula turbo":
            self._add(INV_TURBO, 1)
        elif name == "Servoreparador":
            self._add(INV_SERVOS, 1)
        elif name == "Starkos":
            self._add(INV_STARKOS, 1, STARKOS_CAP)
        elif name == "Set de servos":
            self._add(INV_SETSERVOS, 1)
        elif name == "K-Bups":
            self._add(INV_KBUPS, 1)
        elif name == "Mechaimpulsor":
            self._add(INV_MECHAIMPULSOR, 1)
        elif name == "200 creditos":
            self._add(CREDITS_FROM_INV, 200)
        elif name == "Corazon extra":
            if not self.dry_run:
                self.mem.write_f32(self.inv + VIDA_MAX, (self.mem.f32(self.inv + VIDA_MAX) or 0) + HEART)
                self.mem.write_f32(self.inv + VIDA, (self.mem.f32(self.inv + VIDA) or 0) + HEART)
            self._add(INV_HEART, 1)
        # Permisos y zoom: se imponen en cada tick (_enforce_shop / _enforce_zoom)

    def _enforce_zoom(self, owned: set):
        self._set_flag(*ZOOM_FLAG, on="Zoom de camara" in owned)

    def _enforce_shop(self, owned: set):
        bought = self._r32(AP_SHOP_BOUGHT)
        if self._r32(INV_TURBOMOTOR) == 1:
            bought |= 1 << TURBOMOTOR_SLOT
        for permit, slot in SHOP_PERMITS.items():
            off = SHOP_TABLE + 4 * slot
            cur = self._r32(off)
            if self.shop_written.get(slot) == 1 and cur == 0:
                bought |= 1 << slot          # el juego lo puso en 0: se acaba de comprar
            desired = 1 if permit in owned and not bought & (1 << slot) else 0
            if cur != desired:
                self._w32(off, desired)
            self.shop_written[slot] = desired
        if bought != self._r32(AP_SHOP_BOUGHT):
            self._w32(AP_SHOP_BOUGHT, bought)

    # --- tick principal ------------------------------------------------------------
    def tick(self, received: list, server_checked: Iterable[int] = (), death_requested: bool = False,
             already_checked: Iterable[int] = ()) -> TickResult:
        """
        received: nombres de items de AP en orden (ctx.items_received).
        server_checked: location ids que el servidor ya tiene por chequeados (para collect).
        """
        r = TickResult()
        if not self.mem.attach():
            self._reset()
            r.status = "Esperando BGE.exe"
            return r
        inv = self.mem.inv_base()
        if inv is None:
            r.status = "Esperando una partida cargada"
            return r
        if inv != self.inv:
            self._reset()
            self.inv = inv

        flags = self.mem.read(inv + FLAGS_DELTA + FLAGS_START, FLAGS_END - FLAGS_START)
        invseg = self.mem.read(inv + INV_START, INV_END - INV_START)
        if not flags or not invseg or not any(flags) or not any(invseg):
            r.status = "Cargando..."
            return r   # lectura transitoria en cero (carga de sector)

        zone = (self.mem.u32(inv + SAVEBUF + 0x258), self.mem.u32(inv + SAVEBUF + 0x264))
        now = time.monotonic()
        if zone != self.zone:
            self.zone, self.zone_since = zone, now
            self.prev_bits = None      # no comparar flags entre partidas/zonas distintas
        r.zone = zone
        if now - self.zone_since < ZONE_SETTLE_SECONDS:
            r.status = "Cambiando de zona..."
            return r
        r.in_game = True
        r.status = "En partida"
        if zone[1] != self.announced_spawn and zone[1] not in TRANSIENT_SPAWNS:
            self.announced_spawn = zone[1]
            r.entered = place_name(zone[1])

        # 1) Checks con antirrebote
        bits = _locations_from_flags(flags)
        confirmed = bits & self.pending_bits
        self.pending_bits = bits
        if self.prev_bits is not None:
            done = set(already_checked) | set(server_checked)
            for lid in sorted(confirmed - self.prev_bits - self.self_set):
                loc = _LOC_BY_ID[lid]
                # Solo la PRIMERA vez se quita el premio vanilla. La tienda de Mammago se reabastece
                # (starkos/K-Bups vuelven a 0 al reentrar): una compra repetida debe dar el articulo normal.
                if loc.vanilla and lid not in done:
                    self._revert_vanilla(loc.vanilla)
                    r.reverted.append(f"{loc.name} ({loc.vanilla})")
        self.prev_bits = confirmed
        r.checked = confirmed
        r.goal = GOAL_ID in confirmed

        # 2) Collect: objetos que el servidor ya tiene -> desaparecen del mundo
        for lid in server_checked:
            loc = _LOC_BY_ID.get(lid)
            if loc and loc.kind == "object" and lid not in bits:
                self._set_flag(loc.offset, loc.mask, True)
                self.self_set.add(lid)
                r.collected.append(loc.name)

        # 3) Items recibidos (indice guardado en la partida)
        idx = self._r32(AP_ITEM_INDEX)
        if idx <= len(received):
            for i in range(idx, len(received)):
                self._apply_item(received[i])
                self._w32(AP_ITEM_INDEX, i + 1)
                r.applied.append(received[i])
        else:
            r.status = f"Partida con indice de items {idx} > {len(received)} (¿save de otra semilla?)"
        owned = set(received)
        self._enforce_zoom(owned)
        self._enforce_shop(owned)

        # 4) DeathLink
        dead = bool(flags[DEATH_FLAG[0] - FLAGS_START] & DEATH_FLAG[1])
        if dead and not self.was_dead:
            if self.killing:
                self.killing = False
            else:
                r.died = True
        self.was_dead = dead
        if death_requested and not dead and not self.dry_run:
            self.mem.write_f32(inv + VIDA, 0.0)
            self.killing = True
            r.killed = True
        return r
