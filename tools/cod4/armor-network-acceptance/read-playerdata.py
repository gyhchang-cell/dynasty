"""Read real on-disk native player NBT; never writes a game save."""
from pathlib import Path
import gzip,struct,json,sys,hashlib,shutil
class Nbt:
 def __init__(self,b):self.b=b;self.i=0
 def take(self,n):v=self.b[self.i:self.i+n];self.i+=n;return v
 def unpack(self,f):return struct.unpack('>'+f,self.take(struct.calcsize('>'+f)))[0]
 def text(self):return self.take(self.unpack('H')).decode('utf-8')
 def tag(self,t):
  if t==0:return None
  if t in [1,2,3,4,5,6]:return self.unpack({1:'b',2:'h',3:'i',4:'q',5:'f',6:'d'}[t])
  if t==7:return list(self.take(self.unpack('i')))
  if t==8:return self.text()
  if t==9:
   sub=self.unpack('B');return [self.tag(sub) for _ in range(self.unpack('i'))]
  if t==10:
   out={}
   while True:
    sub=self.unpack('B')
    if sub==0:return out
    name=self.text();out[name]=self.tag(sub)
  if t in [11,12]:return [self.unpack('i' if t==11 else 'q') for _ in range(self.unpack('i'))]
  raise ValueError(t)
def read(p):
 b=p.read_bytes();n=Nbt(gzip.decompress(b));t=n.unpack('B');name=n.text();return n.tag(t)
if __name__=='__main__':
 p=Path(sys.argv[1]);out=Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=True);data=read(p);saved=data.get('ForgeData',{}).get('PlayerPersisted',{}).get('dynastyCod4',{});digest=hashlib.sha256(p.read_bytes()).hexdigest();shutil.copy2(p,out/(digest[:16]+'.dat'));result={'source':str(p.resolve()),'sha256':digest,'rootKeys':list(data),'nativeSavedCooldowns':saved,'fixtureTimeChanged':False};(out/(digest[:16]+'.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False,indent=2))
