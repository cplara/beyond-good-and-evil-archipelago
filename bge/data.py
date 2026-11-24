"""
Datos compartidos entre el world (generacion) y el cliente (memoria del juego).

Todos los offsets son offsets del .sav, confirmados en vivo.
Los flags viven en el segmento de flags: direccion viva = inv_base - 0x286C + offset.
"""
from typing import NamedTuple, Optional

GAME_NAME = "Beyond Good and Evil"
BASE_ID = 0xBE6000

# Nombres de lugares por spawn (buffer del save +0x264). El mismo spawn vale en zona 1 (prologo) y 9.
PLACES = {
    31: "Hangar del faro",
    32: "Taller de Zerdy",
    33: "Faro",
    34: "Isla del faro (exterior)",
    72: "Taller Mammago",
    90: "Hillys (mar)",
    130: "Mina de Isla Negra",
    131: "Mina abandonada",
    132: "Galeria principal",
    133: "Galeria secundaria",
    150: "Centro de Hillys",
    220: "Cueva de ladrones 1",
    228: "Guarida de Vorax",
    1103: "Lector de mdisk",
}


# Spawns que no son lugares fisicos: el juego "cambia" a ellos y vuelve al lugar anterior (no se anuncian).
TRANSIENT_SPAWNS = {1103}   # pantalla del lector de mdisk (leer un mdisk, guardar)


def place_name(spawn) -> str:
    return PLACES.get(spawn, f"zona desconocida (spawn {spawn})")


# Regiones
MENU = "Menu"
ISLA = "Isla del faro"      # taller de Zerdy, hangar, faro (a pie)
MAMMAGO = "Taller Mammago"  # se llega siempre: el deslizador averiado es remolcado hasta aqui
MAR = "Hillys - Mar"        # requiere el deslizador con turbomotor (cueva de ladrones, guarida de Vorax, centro)
NEGRA = "Isla Negra"        # mina de Isla Negra, mina abandonada, galeria secundaria (desde el mar)


class LocationData(NamedTuple):
    name: str
    region: str
    offset: int             # offset del .sav dentro del segmento de flags
    mask: int
    kind: str               # "object" (desaparece del mundo), "photo", "event", "shop"
    vanilla: Optional[str]  # recompensa vanilla que el cliente revierte al recogerla
    # Locations intercambiables: el cliente cuenta cuantos bits del grupo estan encendidos y envia
    # las primeras N del grupo, sin importar cual bit fue (ej. dos entradas iguales en una tienda).
    group: Optional[str] = None


LOCATIONS = [
    # IMPORTANTE: solo agregar al FINAL de la lista (el id depende de la posicion).
    LocationData("Taller de Zerdy - Mdisk de Castelac", ISLA, 0x38A0, 0x80, "object", None),
    LocationData("Hangar - Capsula turbo 1",            ISLA, 0x3873, 0x10, "object", "turbo"),
    LocationData("Hangar - Capsula turbo 2",            ISLA, 0x3873, 0x20, "object", "turbo"),
    LocationData("Hangar - Servoreparador 1",           ISLA, 0x39F4, 0x10, "object", "servo"),
    LocationData("Hangar - Servoreparador 2",           ISLA, 0x39F4, 0x20, "object", "servo"),
    LocationData("Faro - Starkos 1",                    ISLA, 0x396A, 0x01, "object", "starkos"),
    LocationData("Faro - Starkos 2",                    ISLA, 0x396A, 0x02, "object", "starkos"),
    LocationData("Faro - Starkos 3",                    ISLA, 0x3969, 0x10, "object", "starkos"),
    LocationData("Faro - Starkos 4",                    ISLA, 0x3969, 0x20, "object", "starkos"),
    LocationData("Faro - Starkos 5",                    ISLA, 0x3969, 0x80, "object", "starkos"),
    LocationData("Faro - Starkos de la chimenea",       ISLA, 0x3969, 0x01, "object", "starkos"),
    LocationData("Faro - K-Bups del perro",             ISLA, 0x3969, 0x04, "object", "kbups"),
    LocationData("Faro - Corazon extra",                ISLA, 0x3968, 0x80, "object", "heart"),
    # Fotos: el flag se enciende en el instante de la foto. El album (JPEG en el save) no se toca.
    LocationData("Foto - Armadillo",                    ISLA, 0x3879, 0x01, "photo", None),
    LocationData("Foto - Gaviota",                      ISLA, 0x3879, 0x40, "photo", None),
    LocationData("Foto - Perro",                        ISLA, 0x3878, 0x02, "photo", None),
    LocationData("Foto - Luciernagas",                  ISLA, 0x387A, 0x01, "photo", None),
    LocationData("Foto - Dipnoi",                       ISLA, 0x387C, 0x01, "photo", None),
    LocationData("Foto - Mosca",                        ISLA, 0x387C, 0x02, "photo", None),
    LocationData("Foto - Nutria bipeda",                ISLA, 0x387D, 0x10, "photo", None),
    LocationData("Foto - Humano",                       ISLA, 0x387D, 0x40, "photo", None),
    LocationData("Foto - Capra sapiens",                ISLA, 0x387E, 0x80, "photo", None),
    LocationData("Foto - Zerdy",                        ISLA, 0x387E, 0x02, "photo", None),
    LocationData("Fotos - Carrete completo",            ISLA, 0x393A, 0x01, "event", "zoom"),
    # Pelea Domz al tener el turbomotor; la perla es el check y la meta del prototipo.
    LocationData("Hillys - Perla de la criatura Domz",  MAR,  0x397E, 0x40, "event", None),
    # Agregados 2026-10-22 (partida nueva). Las perlas aun no se randomizan: no se revierten.
    LocationData("Faro - Perla de la criatura Domz del faro", ISLA, 0x397E, 0x20, "event", None),
    LocationData("Foto - Mariquita",                    ISLA, 0x3879, 0x02, "photo", None),
    LocationData("Foto - Vorax",                        ISLA, 0x387A, 0x80, "photo", None),
    LocationData("Foto - Rhinoceros sapiens",           MAMMAGO, 0x3879, 0x04, "photo", None),
    # Tienda de articulos de Mammago: cada compra enciende su propio bit (confirmado comprando en 2 ordenes:
    # Starkos y K-Bups tienen bit fijo; los 2 Mechaimpulsores intercambian bits -> grupo).
    LocationData("Tienda Mammago - Starkos",            MAMMAGO, 0x3875, 0x02, "shop", "starkos"),
    LocationData("Tienda Mammago - K-Bups",             MAMMAGO, 0x39F5, 0x01, "shop", "kbups"),
    LocationData("Tienda Mammago - Mechaimpulsor 1",    MAMMAGO, 0x3996, 0x40, "shop", "mechaimpulsor",
                 "mammago_mechaimpulsor"),
    LocationData("Tienda Mammago - Mechaimpulsor 2",    MAMMAGO, 0x3875, 0x01, "shop", "mechaimpulsor",
                 "mammago_mechaimpulsor"),

    # ---- Agregados 2026-10-26 (sesion de Hillys e Isla Negra) ----
    # Tienda de Mammago tras la pelea DomZ: aparecen servos, turbos y sets de servos. Se reabastece en cada visita:
    # el premio vanilla solo se revierte la primera vez. Unidades iguales = grupo.
    LocationData("Tienda Mammago - Servoreparador 1",   MAR, 0x3971, 0x08, "shop", "servo", "mammago_servos"),
    LocationData("Tienda Mammago - Servoreparador 2",   MAR, 0x3971, 0x10, "shop", "servo", "mammago_servos"),
    LocationData("Tienda Mammago - Servoreparador 3",   MAR, 0x3971, 0x20, "shop", "servo", "mammago_servos"),
    LocationData("Tienda Mammago - Capsula turbo 1",    MAR, 0x3875, 0x04, "shop", "turbo", "mammago_turbos"),
    LocationData("Tienda Mammago - Capsula turbo 2",    MAR, 0x39F5, 0x02, "shop", "turbo", "mammago_turbos"),
    LocationData("Tienda Mammago - Set de servos 1",    MAR, 0x3993, 0x08, "shop", "setservos", "mammago_setservos"),
    LocationData("Tienda Mammago - Set de servos 2",    MAR, 0x3993, 0x10, "shop", "setservos", "mammago_setservos"),
    LocationData("Tienda Mammago - Set de servos 3",    MAR, 0x3993, 0x20, "shop", "setservos", "mammago_setservos"),
    # Hillys (mar) y Cueva de ladrones 1 (spawn 220)
    LocationData("Foto - Pez escorpion",                MAR, 0x387B, 0x80, "photo", None),
    LocationData("Cueva de ladrones 1 - Caja 1",        MAR, 0x39A2, 0x01, "object", None),
    LocationData("Cueva de ladrones 1 - Caja 2",        MAR, 0x39A2, 0x02, "object", None),
    LocationData("Cueva de ladrones 1 - Caja 3",        MAR, 0x39A2, 0x04, "object", None),
    LocationData("Cueva de ladrones 1 - Caja 4",        MAR, 0x39A2, 0x08, "object", None),
    LocationData("Cueva de ladrones 1 - Caja 5",        MAR, 0x39A2, 0x10, "object", None),
    LocationData("Cueva de ladrones 1 - Caja 6",        MAR, 0x39A2, 0x40, "object", None),
    LocationData("Cueva de ladrones 1 - Caja 7",        MAR, 0x39A2, 0x80, "object", None),
    LocationData("Cueva de ladrones 1 - Caja 8",        MAR, 0x39A3, 0x01, "object", None),
    LocationData("Cueva de ladrones 1 - Caja 9",        MAR, 0x39A3, 0x02, "object", None),
    LocationData("Cueva de ladrones 1 - Caja 10",       MAR, 0x39A3, 0x04, "object", None),
    LocationData("Cueva de ladrones 1 - Caja 11",       MAR, 0x39A3, 0x08, "object", None),
    LocationData("Cueva de ladrones 1 - Botin del final", MAR, 0x3A0E, 0x80, "object", None),
    LocationData("Cueva de ladrones 1 - Perla de los ladrones", MAR, 0x397E, 0x80, "event", None),
    # Guarida de Vorax (spawn 228). Los 2 turbos estan en el armario (boton 0x388C bit 5).
    LocationData("Foto - Bufo erectus",                 MAR, 0x387D, 0x04, "photo", None),
    LocationData("Guarida de Vorax - Corazon extra",    MAR, 0x39B0, 0x08, "object", "heart"),
    LocationData("Guarida de Vorax - Capsula turbo 1",  MAR, 0x388C, 0x08, "object", "turbo"),
    LocationData("Guarida de Vorax - Capsula turbo 2",  MAR, 0x388C, 0x10, "object", "turbo"),
    # Mina de Isla Negra (spawn 130)
    LocationData("Mina de Isla Negra - Starkos",        NEGRA, 0x3979, 0x04, "object", "starkos"),
    LocationData("Mina de Isla Negra - Capsula turbo",  NEGRA, 0x3979, 0x02, "object", "turbo"),
    LocationData("Foto - Cangrejo de rio de dos patas", NEGRA, 0x387C, 0x40, "photo", None),
    LocationData("Fotos - Perla del carrete 2",         NEGRA, 0x397F, 0x01, "event", None),
    # Mina abandonada (spawn 131): botas cohete de Zerdy, dinamitas, Crochax
    LocationData("Mina abandonada - Starkos 1",         NEGRA, 0x3873, 0x08, "object", "starkos"),
    LocationData("Mina abandonada - Starkos 2",         NEGRA, 0x3920, 0x02, "object", "starkos"),
    LocationData("Mina abandonada - Capsula turbo",     NEGRA, 0x3920, 0x04, "object", "turbo"),
    LocationData("Mina abandonada - Cristal de esencia grande 1", NEGRA, 0x3897, 0x20, "object", None),
    LocationData("Mina abandonada - Cristal de esencia grande 2", NEGRA, 0x3898, 0x20, "object", None),
    LocationData("Mina abandonada - Maquina expendedora - Starkos 1", NEGRA, 0x3990, 0x08, "shop", "starkos",
                 "mina_maquina_starkos"),
    LocationData("Mina abandonada - Maquina expendedora - Starkos 2", NEGRA, 0x3990, 0x20, "shop", "starkos",
                 "mina_maquina_starkos"),
    LocationData("Mina abandonada - Maquina expendedora - Starkos 3", NEGRA, 0x3990, 0x40, "shop", "starkos",
                 "mina_maquina_starkos"),
    LocationData("Foto - Anemona mutante",              NEGRA, 0x3878, 0x20, "photo", None),
    LocationData("Foto - Crochax",                      NEGRA, 0x387A, 0x40, "photo", None),
    LocationData("Foto - Caracol gigante",              NEGRA, 0x387A, 0x02, "photo", None),
    # Galeria secundaria (spawn 133)
    LocationData("Foto - Medusa",                       NEGRA, 0x3879, 0x20, "photo", None),
    LocationData("Foto - Alicia",                       NEGRA, 0x387E, 0x04, "photo", None),
    LocationData("Foto - Medusa mutante",               NEGRA, 0x387A, 0x10, "photo", None),

    # ---- Agregados 2026-10-31 (resto de Isla Negra y jefe de la mina) ----
    # Mina abandonada
    LocationData("Mina abandonada - Alicates",          NEGRA, 0x3926, 0x80, "event", None),
    LocationData("Mina abandonada - Capsula turbo (armario)", NEGRA, 0x396C, 0x01, "object", "turbo"),
    LocationData("Mina abandonada - K-Bups (armario)",  NEGRA, 0x3873, 0x04, "object", "kbups"),
    LocationData("Foto - Esponja gigante",              NEGRA, 0x387F, 0x01, "photo", None),
    LocationData("Foto - Hongo",                        NEGRA, 0x387C, 0x08, "photo", None),
    LocationData("Fotos - Perla del carrete 3",         NEGRA, 0x397F, 0x08, "event", None),
    LocationData("Mina abandonada - Maquina expendedora 2 - Corazon extra", NEGRA, 0x395E, 0x08, "shop", "heart"),
    LocationData("Mina abandonada - Maquina expendedora 2 - Starkos 1", NEGRA, 0x39F5, 0x40, "shop", "starkos",
                 "mina_maquina2_starkos"),
    LocationData("Mina abandonada - Maquina expendedora 2 - Starkos 2", NEGRA, 0x3873, 0x02, "shop", "starkos",
                 "mina_maquina2_starkos"),
    LocationData("Mina abandonada - Cristal de esencia grande 3", NEGRA, 0x3897, 0x40, "object", None),
    LocationData("Foto - Ameba polypodia",              NEGRA, 0x3878, 0x10, "photo", None),
    LocationData("Foto - Planaria",                     NEGRA, 0x387C, 0x04, "photo", None),
    # Galeria principal (spawn 132)
    LocationData("Foto - Palinuro",                     NEGRA, 0x3879, 0x10, "photo", None),
    LocationData("Foto - Nautilus",                     NEGRA, 0x387A, 0x20, "photo", None),
    LocationData("Galeria principal - Maquina expendedora - K-Bups 1", NEGRA, 0x3979, 0x10, "shop", "kbups",
                 "galeria_maquina_kbups"),
    LocationData("Galeria principal - Maquina expendedora - K-Bups 2", NEGRA, 0x3979, 0x08, "shop", "kbups",
                 "galeria_maquina_kbups"),
    LocationData("Galeria principal - Maquina expendedora - Starkos", NEGRA, 0x3979, 0x20, "shop", "starkos"),
    LocationData("Galeria principal - Cristal de esencia grande 1", NEGRA, 0x3898, 0x01, "object", None),
    LocationData("Galeria principal - Cristal de esencia grande 2", NEGRA, 0x3897, 0x80, "object", None),
    LocationData("Galeria principal - Cristal de esencia grande 3", NEGRA, 0x3898, 0x08, "object", None),
    LocationData("Galeria principal - Cristal de esencia grande 4", NEGRA, 0x3898, 0x02, "object", None),
    LocationData("Galeria principal - Cristal de esencia grande 5", NEGRA, 0x3898, 0x10, "object", None),
    LocationData("Galeria principal - Cristal de esencia grande 6", NEGRA, 0x3898, 0x04, "object", None),
    # Jefe de la mina
    LocationData("Mision Castellac - Foto de la pareja de criaturas", NEGRA, 0x38D5, 0x80, "event", None),
    LocationData("Foto - Pterolimax",                   NEGRA, 0x387B, 0x40, "photo", None),
    LocationData("Mina - Perla del jefe",               NEGRA, 0x397F, 0x40, "event", None),
    # Mina de Isla Negra, detras de la puerta de alambre (alicates)
    LocationData("Foto - Oruga gigante",                NEGRA, 0x387D, 0x08, "photo", None),
    LocationData("Mina de Isla Negra - Corazon extra",  NEGRA, 0x396C, 0x02, "object", "heart"),
]
for _i, _loc in enumerate(LOCATIONS):
    assert 0x3840 <= _loc.offset < 0x3B00, _loc.name
LOCATION_IDS = {loc.name: BASE_ID + i for i, loc in enumerate(LOCATIONS)}
GOAL_LOCATION = "Hillys - Perla de la criatura Domz"


class ItemData(NamedTuple):
    name: str
    classification: str    # "progression", "useful", "filler"
    count: int             # copias en el pool (0 = solo relleno)


# Slots de la tabla viva de la tienda de Mammago (inv_base + 0x1D08 + 4*slot).
SHOP_PERMITS = {
    "Permiso: Estabilizador de vuelo": 0,
    "Permiso: Motor estelar":          1,
    "Permiso: Canon neutralizador":    3,
    "Permiso: Equipo de salto":        4,
    "Permiso: Turbomotor":             5,
}

ITEMS = [
    # IMPORTANTE: solo agregar al FINAL de la lista (el id depende de la posicion).
    ItemData("Permiso: Turbomotor",             "progression", 1),
    ItemData("Permiso: Canon neutralizador",    "useful",      1),
    ItemData("Permiso: Equipo de salto",        "useful",      1),
    ItemData("Permiso: Estabilizador de vuelo", "useful",      1),
    ItemData("Permiso: Motor estelar",          "useful",      1),
    ItemData("Zoom de camara",                  "useful",      0),   # entra al pool por VANILLA_ITEMS
    ItemData("Corazon extra",                   "useful",      0),   # idem
    ItemData("Starkos",                         "filler",      0),
    ItemData("Servoreparador",                  "filler",      0),
    ItemData("Capsula turbo",                   "filler",      0),
    ItemData("200 creditos",                    "filler",      0),
    ItemData("Mechaimpulsor",                   "filler",      0),
    ItemData("K-Bups",                          "filler",      0),
    ItemData("Set de servos",                   "filler",      0),
]
ITEM_IDS = {item.name: BASE_ID + i for i, item in enumerate(ITEMS)}
FILLER_ITEMS = [item.name for item in ITEMS if item.classification == "filler"]

# El pool se arma con la recompensa vanilla de cada location (asi hay tantos starkos como en el juego).
# Locations sin objeto vanilla (fotos, mdisk, perlas) aportan creditos; los permisos reemplazan creditos.
VANILLA_ITEMS = {
    "turbo": "Capsula turbo",
    "servo": "Servoreparador",
    "starkos": "Starkos",
    "kbups": "K-Bups",
    "heart": "Corazon extra",
    "mechaimpulsor": "Mechaimpulsor",
    "setservos": "Set de servos",
    "zoom": "Zoom de camara",
    None: "200 creditos",
}
CREDITS_FILLER = "200 creditos"
