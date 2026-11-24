"""
Acceso a la memoria de BGE.exe (32-bit, sin ASLR) via ReadProcessMemory/WriteProcessMemory.
Sin dependencias externas: el Archipelago congelado no trae numpy ni pymem.

Mapa (todo relativo a inv_base = [BGE.exe+0x793DF4]):
    inventario   inv_base + offset_save            (save 0x400-0xD40)
    flags        inv_base - 0x286C + offset_save   (save 0x3840-0x3B00)
    creditos     inv_base + 0x2CC
    vida_max     inv_base + 0x288 (float, 40 por corazon)
    vida         inv_base + 0x2BC (float)
    tienda       inv_base + 0x1D08 + 4*slot (u32, 1 = a la venta)
    buffer save  inv_base + 0x9E2C (zona +0x258, spawn +0x264)
"""
import ctypes
import ctypes.wintypes as wt
import struct
from typing import Optional

PROCESS_NAME = "BGE.exe"

INV_PTR = 0xB93DF4                                  # BGE.exe+0x793DF4
CREDIT_PTRS = (0xB9A6C0, 0xB9AC68, 0xB9E8B0, 0xB9F0B4)
CREDITS_FROM_INV = 0x2CC

INV_START, INV_END = 0x400, 0xD40
FLAGS_DELTA = -0x286C
FLAGS_START, FLAGS_END = 0x3840, 0x3B00
SAVEBUF = 0x9E2C
SHOP_TABLE = 0x1D08
VIDA_MAX = 0x288
VIDA = 0x2BC

# Bytes libres al final del segmento de inventario, usados por el cliente AP.
# Viven en la partida: se guardan con el save y vuelven atras al recargar.
AP_ITEM_INDEX = 0xD38      # cuantos items de AP ya se aplicaron
AP_SHOP_BOUGHT = 0xD3C     # mascara de mejoras ya compradas (bit = slot de la tienda)

_k32 = ctypes.WinDLL("kernel32", use_last_error=True)
_PROCESS_ACCESS = 0x0010 | 0x0020 | 0x0008 | 0x0400   # VM_READ | VM_WRITE | VM_OPERATION | QUERY_INFORMATION
_STILL_ACTIVE = 259


class _PE32(ctypes.Structure):
    _fields_ = [("dwSize", wt.DWORD), ("cntUsage", wt.DWORD), ("th32ProcessID", wt.DWORD),
                ("th32DefaultHeapID", ctypes.c_void_p), ("th32ModuleID", wt.DWORD),
                ("cntThreads", wt.DWORD), ("th32ParentProcessID", wt.DWORD),
                ("pcPriClassBase", ctypes.c_long), ("dwFlags", wt.DWORD), ("szExeFile", ctypes.c_char * 260)]


_k32.OpenProcess.restype = wt.HANDLE
_k32.CreateToolhelp32Snapshot.restype = wt.HANDLE
_k32.ReadProcessMemory.argtypes = [wt.HANDLE, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t,
                                   ctypes.POINTER(ctypes.c_size_t)]
_k32.WriteProcessMemory.argtypes = _k32.ReadProcessMemory.argtypes


def _find_pid(name: str) -> Optional[int]:
    snap = _k32.CreateToolhelp32Snapshot(0x2, 0)
    entry = _PE32()
    entry.dwSize = ctypes.sizeof(_PE32)
    try:
        ok = _k32.Process32First(snap, ctypes.byref(entry))
        while ok:
            if entry.szExeFile.decode(errors="ignore").lower() == name.lower():
                return entry.th32ProcessID
            ok = _k32.Process32Next(snap, ctypes.byref(entry))
    finally:
        _k32.CloseHandle(snap)
    return None


class GameMemory:
    def __init__(self):
        self.handle = None
        self.pid = None

    # --- proceso -------------------------------------------------------------
    def attach(self) -> bool:
        if self.alive():
            return True
        self.detach()
        pid = _find_pid(PROCESS_NAME)
        if not pid:
            return False
        handle = _k32.OpenProcess(_PROCESS_ACCESS, False, pid)
        if not handle:
            return False
        self.handle, self.pid = handle, pid
        return True

    def alive(self) -> bool:
        if not self.handle:
            return False
        code = wt.DWORD()
        return bool(_k32.GetExitCodeProcess(self.handle, ctypes.byref(code))) and code.value == _STILL_ACTIVE

    def detach(self) -> None:
        if self.handle:
            _k32.CloseHandle(self.handle)
        self.handle, self.pid = None, None

    # --- lectura / escritura ---------------------------------------------------
    def read(self, addr: int, size: int) -> Optional[bytes]:
        buf = ctypes.create_string_buffer(size)
        got = ctypes.c_size_t()
        if not self.handle or not _k32.ReadProcessMemory(self.handle, addr, buf, size, ctypes.byref(got)):
            return None
        return buf.raw[:got.value] if got.value == size else None

    def write(self, addr: int, data: bytes) -> bool:
        got = ctypes.c_size_t()
        return bool(self.handle) and bool(_k32.WriteProcessMemory(self.handle, addr, data, len(data),
                                                                   ctypes.byref(got)))

    def u32(self, addr: int) -> Optional[int]:
        d = self.read(addr, 4)
        return struct.unpack("<I", d)[0] if d else None

    def f32(self, addr: int) -> Optional[float]:
        d = self.read(addr, 4)
        return struct.unpack("<f", d)[0] if d else None

    def write_u32(self, addr: int, value: int) -> bool:
        return self.write(addr, struct.pack("<I", max(0, value) & 0xFFFFFFFF))

    def write_f32(self, addr: int, value: float) -> bool:
        return self.write(addr, struct.pack("<f", value))

    # --- estructura del juego ----------------------------------------------------
    def inv_base(self) -> Optional[int]:
        """Resuelve inv_base y lo valida contra los punteros de creditos (si no coinciden, no hay partida)."""
        inv = self.u32(INV_PTR)
        if not inv:
            return None
        for ptr in CREDIT_PTRS:
            if self.u32(ptr) == inv + CREDITS_FROM_INV:
                return inv
        return None
