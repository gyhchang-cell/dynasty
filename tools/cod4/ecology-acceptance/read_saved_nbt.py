"""Read a saved private-QA NBT file without loading Minecraft or mutating the save."""
from pathlib import Path
import gzip,struct

def read_saved_nbt(path):
 b=Path(path).read_bytes()
 if b[:2]==b'\x1f\x8b':b=gzip.decompress(b)
 i=0
 def take(n):
  nonlocal i
  x=b[i:i+n];i+=n;return x
 def num(f):return struct.unpack('>'+f,take(struct.calcsize('>'+f)))[0]
 def text():return take(num('H')).decode('utf8',errors='replace')
 def v(t):
  if 1<=t<=6:return num({1:'b',2:'h',3:'i',4:'q',5:'f',6:'d'}[t])
  if t==7:return list(take(num('i')))
  if t==8:return text()
  if t==9:
   kind=num('b');return [v(kind) for _ in range(num('i'))]
  if t==10:
   out={}
   while True:
    kind=num('b')
    if kind==0:return out
    name=text();out[name]=v(kind)
  if t in [11,12]:return [num('i' if t==11 else 'q') for _ in range(num('i'))]
  raise ValueError(t)
 t=num('b');text();return v(t)
