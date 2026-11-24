"""
Prueba sin Archipelago ni servidor: simula los modulos de AP, valida los datos del apworld y ejecuta la logica
del cliente en modo solo lectura (dry_run). Si el juego esta abierto con una partida, muestra los checks detectados.

    python tests/offline_smoke_test.py
"""
import os, sys, types, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
class Any:
    def __init__(self, *a, **k): pass
for n in ['BaseClasses','worlds','worlds.AutoWorld','worlds.LauncherComponents','Options','Utils','CommonClient','NetUtils']:
    sys.modules[n]=types.ModuleType(n)
B=sys.modules['BaseClasses']
for k in ['Item','Location','Region','Tutorial']: setattr(B,k,type(k,(Any,),{}))
B.ItemClassification=types.SimpleNamespace(progression=1,useful=2,filler=0)
A=sys.modules['worlds.AutoWorld']; A.WebWorld=type('WebWorld',(Any,),{}); A.World=type('World',(Any,),{})
L=sys.modules['worlds.LauncherComponents']; L.Component=Any; L.Type=types.SimpleNamespace(CLIENT=0); L.components=[]; L.launch_subprocess=None
C=sys.modules['CommonClient']; C.ClientCommandProcessor=Any; C.CommonContext=Any; C.get_base_parser=C.server_loop=None; C.gui_enabled=False; C.logger=None
sys.modules['NetUtils'].ClientStatus=None
O=sys.modules['Options']; O.DeathLink=int; O.PerGameCommonOptions=object
from bge.data import LOCATIONS, ITEMS, LOCATION_IDS
print(len(LOCATIONS),'locations,', sum(i.count for i in ITEMS),'items no-relleno; ids unicos:', len(set(LOCATION_IDS.values()))==len(LOCATIONS))
from bge.client.game import BGEGame
g=BGEGame(dry_run=True)
for _ in range(12):
    r=g.tick(received=[], server_checked=[]); time.sleep(0.25)
names={v:k for k,v in LOCATION_IDS.items()}
print('status:',r.status,' zona:',r.zone)
print('checks encendidos:', sorted(names[i] for i in r.checked))

# --- prueba de grupos ---
from bge.client.game import _locations_from_flags
flags = bytearray(0x3B00 - 0x3840)
flags[0x3875 - 0x3840] |= 0x01           # solo el bit que antes llamabamos "Mechaimpulsor 2"
print('grupo, 1 bit  ->', sorted(names[i] for i in _locations_from_flags(bytes(flags))))
flags[0x3996 - 0x3840] |= 0x40
print('grupo, 2 bits ->', sorted(names[i] for i in _locations_from_flags(bytes(flags))))
