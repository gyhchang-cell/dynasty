import struct,json,sys
from pathlib import Path
p=Path(sys.argv[1]);data=p.read_bytes();i=0
def u(n):
 global i
 v=int.from_bytes(data[i:i+n],'big');i+=n;return v
def take(n):
 global i
 v=data[i:i+n];i+=n;return v
assert u(4)==0xcafebabe;minor=u(2);major=u(2);count=u(2);cp=[None]*count;k=1
while k<count:
 t=u(1)
 if t==1:cp[k]=('utf',take(u(2)).decode('utf-8','replace'))
 elif t in [3,4]:cp[k]=(t,take(4).hex())
 elif t in [5,6]:cp[k]=(t,take(8).hex());k+=1
 elif t in [7,8,16,19,20]:cp[k]=(t,u(2))
 elif t in [9,10,11,12,17,18]:cp[k]=(t,u(2),u(2))
 elif t==15:cp[k]=(t,u(1),u(2))
 else:raise ValueError(t)
 k+=1
def sym(k,depth=0):
 if not k:return None
 x=cp[k]
 if depth>5:return str(x)
 if x[0]=='utf':return x[1]
 if x[0] in [7,8,16,19,20]:return sym(x[1],depth+1)
 if x[0]==15:return 'handle '+str(x[1])+' '+str(sym(x[2],depth+1))
 if x[0] in [9,10,11,12]:return ' / '.join(str(sym(a,depth+1)) for a in x[1:])
 return str(x)
access=u(2);this=u(2);sup=u(2);interfaces=[sym(u(2)) for _ in range(u(2))]
def attrs():
 a=[]
 for _ in range(u(2)):
  n=sym(u(2));raw=take(u(4));a.append((n,raw))
 return a
fields=[]
for _ in range(u(2)):
 ac=u(2);n=sym(u(2));d=sym(u(2));a=attrs();fields.append({'name':n,'descriptor':d})
methods=[]
# JVM fixed operand widths. All unlisted standard opcodes have no operands.
width={**{x:1 for x in [0x10,0x12,0x15,0x16,0x17,0x18,0x19,0x36,0x37,0x38,0x39,0x3a,0xa9,0xbc]},**{x:2 for x in [0x11,0x13,0x14,0x84,*range(0x99,0xa9),*range(0xb2,0xb9),0xbb,0xbd,0xc0,0xc1,0xc6,0xc7]},0xb9:4,0xba:4,0xc5:3,0xc8:4,0xc9:4}
cpops=set([0x12,0x13,0x14,*range(0xb2,0xbb),0xbb,0xbd,0xc0,0xc1,0xc5])
names={0x12:'ldc',0x13:'ldc_w',0xb2:'getstatic',0xb3:'putstatic',0xb4:'getfield',0xb5:'putfield',0xb6:'invokevirtual',0xb7:'invokespecial',0xb8:'invokestatic',0xb9:'invokeinterface',0xba:'invokedynamic',0xbb:'new',0xbd:'anewarray',0xb0:'areturn',0xb1:'return',0xc0:'checkcast',0x59:'dup'}
for _ in range(u(2)):
 ac=u(2);n=sym(u(2));d=sym(u(2));aa=attrs();row={'name':n,'descriptor':d,'instructions':[]}
 for an,raw in aa:
  if an!='Code':continue
  size=int.from_bytes(raw[4:8],'big');code=raw[8:8+size];pos=0
  while pos<len(code):
   off=pos;op=code[pos];pos+=1
   if op in [0xaa,0xab]:
    pos+=(4-pos%4)%4;pos+=4
    if op==0xaa:lo=int.from_bytes(code[pos:pos+4],'big',signed=True);hi=int.from_bytes(code[pos+4:pos+8],'big',signed=True);pos+=8+4*(hi-lo+1)
    else:nn=int.from_bytes(code[pos:pos+4],'big');pos+=4+8*nn
   elif op==0xc4:sub=code[pos];pos+=5 if sub==0x84 else 3
   else:pos+=width.get(op,0)
   assert pos<=len(code),(n,off,op,pos,len(code))
   inst={'offset':off,'op':names.get(op,f'op_{op:02x}'),'operands_hex':code[off+1:pos].hex()}
   if op in cpops:
    idx=code[off+1] if op==0x12 else int.from_bytes(code[off+1:off+3],'big');inst['constant']=sym(idx)
   row['instructions'].append(inst)
  row['code_bytes']=size
 methods.append(row)
boot=[]
for an,raw in attrs():
 if an!='BootstrapMethods':continue
 j=2
 for k in range(int.from_bytes(raw[:2],'big')):
  ref=int.from_bytes(raw[j:j+2],'big');argc=int.from_bytes(raw[j+2:j+4],'big');j+=4;args=[]
  for _ in range(argc):args.append(sym(int.from_bytes(raw[j:j+2],'big')));j+=2
  boot.append({'index':k,'handle':sym(ref),'arguments':args})
 assert j==len(raw)
print(json.dumps({'bootstrap_methods':boot,'parser_scope':'Python constantpool+instructionwalk only; no classloading, no JVM','class':sym(this),'super':sym(sup),'interfaces':interfaces,'version':[major,minor],'fields':fields,'methods':methods},ensure_ascii=False,indent=2))
