#!/usr/bin/env python3
"""Serialize one original empty64x24x64 native test template; does not launch tests/Java."""
from pathlib import Path
import gzip,struct
R=Path(__file__).resolve().parents[2]
def string(s):b=s.encode();return struct.pack('>H',len(b))+b
def tag(t,n,p):return bytes([t])+string(n)+p
size=tag(9,'size',bytes([3])+struct.pack('>i3i',3,64,24,64))
palette=tag(9,'palette',bytes([10])+struct.pack('>i',1)+tag(8,'Name',string('minecraft:air'))+b'\0')
blocks=tag(9,'blocks',bytes([10])+struct.pack('>i',0));entities=tag(9,'entities',bytes([10])+struct.pack('>i',0));version=tag(3,'DataVersion',struct.pack('>i',3465))
p=R/'src/main/resources/data/dynasty_army/structures/cauldron_pit_test.nbt';p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(gzip.compress(b'\x0a\x00\x00'+size+palette+blocks+entities+version+b'\0',mtime=0));print('Wrote native template SOURCE fixture, no JVM:',p)
