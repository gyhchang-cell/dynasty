"""Bounded dependency class-file reader; never loads JVM/classes or executes jar code."""
from pathlib import Path
import json,struct,hashlib,zipfile
HERE=Path(__file__).resolve().parent
NAMES='nop aconst_null iconst_m1 iconst_0 iconst_1 iconst_2 iconst_3 iconst_4 iconst_5 lconst_0 lconst_1 fconst_0 fconst_1 fconst_2 dconst_0 dconst_1 bipush sipush ldc ldc_w ldc2_w iload lload fload dload aload iload_0 iload_1 iload_2 iload_3 lload_0 lload_1 lload_2 lload_3 fload_0 fload_1 fload_2 fload_3 dload_0 dload_1 dload_2 dload_3 aload_0 aload_1 aload_2 aload_3 iaload laload faload daload aaload baload caload saload istore lstore fstore dstore astore istore_0 istore_1 istore_2 istore_3 lstore_0 lstore_1 lstore_2 lstore_3 fstore_0 fstore_1 fstore_2 fstore_3 dstore_0 dstore_1 dstore_2 dstore_3 astore_0 astore_1 astore_2 astore_3 iaload_store laload_store faload_store daload_store aastore bastore castore sastore pop pop2 dup dup_x1 dup_x2 dup2 dup2_x1 dup2_x2 swap iadd ladd fadd dadd isub lsub fsub dsub imul lmul fmul dmul idiv ldiv fdiv ddiv irem lrem frem drem ineg lneg fneg dneg ishl lshl ishr lshr iushr lushr iand land ior lor ixor lxor iinc i2l i2f i2d l2i l2f l2d f2i f2l f2d d2i d2l d2f i2b i2c i2s lcmp fcmpl fcmpg dcmpl dcmpg ifeq ifne iflt ifge ifgt ifle if_icmpeq if_icmpne if_icmplt if_icmpge if_icmpgt if_icmple if_acmpeq if_acmpne goto jsr ret tableswitch lookupswitch ireturn lreturn freturn dreturn areturn return getstatic putstatic getfield putfield invokevirtual invokespecial invokestatic invokeinterface invokedynamic new newarray anewarray arraylength athrow checkcast instanceof monitorenter monitorexit wide multianewarray ifnull ifnonnull goto_w jsr_w'.split()
assert NAMES[0xb1]=='return' and NAMES[0xb4]=='getfield'
class Reader:
 def __init__(self,data):self.data=data;self.p=0
 def take(self,n):b=self.data[self.p:self.p+n];self.p+=n;assert len(b)==n;return b
 def u(self,n):return int.from_bytes(self.take(n),'big')
def read_class(data, selected=None):
 r=Reader(data);assert r.u(4)==0xcafebabe;minor=r.u(2);major=r.u(2);cp=[None]*r.u(2);i=1
 while i<len(cp):
  t=r.u(1)
  if t==1:cp[i]=r.take(r.u(2)).decode('utf-8','replace')
  elif t in [3,4,5,6]:
   raw=r.take(8 if t in [5,6] else 4);cp[i]=(t,struct.unpack({3:'>i',4:'>f',5:'>q',6:'>d'}[t],raw)[0]);i+=int(t in[5,6])
  elif t in[7,8,16,19,20]:cp[i]=(t,r.u(2))
  elif t in[9,10,11,12,17,18]:cp[i]=(t,r.u(2),r.u(2))
  elif t==15:cp[i]=(t,r.u(1),r.u(2))
  else:raise ValueError(t)
  i+=1
 def ref(i):
  c=cp[i]
  if isinstance(c,str):return c
  if c[0] in[3,4,5,6]:return str(c[1])
  if c[0] in[7,8,16,19,20]:return ref(c[1])
  if c[0] in[9,10,11,12]:return ' / '.join(ref(j) for j in c[1:])
  return str(c)
 def attrs(rr):
  result=[]
  for _ in range(rr.u(2)):name=ref(rr.u(2));result.append((name,rr.take(rr.u(4))))
  return result
 access=r.u(2);name=ref(r.u(2));parent=ref(r.u(2));r.take(2*r.u(2))
 fields=[]
 for _ in range(r.u(2)):
  a=r.u(2);n=ref(r.u(2));d=ref(r.u(2));at=attrs(r);fields.append({'name':n,'descriptor':d,'access':a})
 methods=[]
 for _ in range(r.u(2)):
  a=r.u(2);n=ref(r.u(2));d=ref(r.u(2));at=attrs(r);m={'name':n,'descriptor':d,'access':a}
  for an,b in at:
   if an!='Code' or (selected is not None and n not in selected):continue
   cr=Reader(b);m['max_stack']=cr.u(2);m['locals']=cr.u(2);code=cr.take(cr.u(4));br=Reader(code);ops=[]
   while br.p<len(code):
    start=br.p;op=br.u(1);s=NAMES[op];operand=''
    if op in[0x12]:operand=ref(br.u(1))
    elif op in[0x13,0x14,0xb2,0xb3,0xb4,0xb5,0xb6,0xb7,0xb8,0xbb,0xbd,0xc0,0xc1]:operand=ref(br.u(2))
    elif op in[0xb9,0xba]:operand=ref(br.u(2))+' extra='+br.take(2).hex()
    elif 0x99<=op<=0xa8 or op in[0xc6,0xc7]:operand='->'+str(start+int.from_bytes(br.take(2),'big',signed=True))
    elif op in[0xc8,0xc9]:operand='->'+str(start+int.from_bytes(br.take(4),'big',signed=True))
    elif op in[0x10,0x15,0x16,0x17,0x18,0x19,0x36,0x37,0x38,0x39,0x3a,0xa9,0xbc]:operand=str(br.u(1))
    elif op in[0x11,0x84]:operand=br.take(2).hex()
    elif op==0xc5:operand=ref(br.u(2))+' dims='+str(br.u(1))
    elif op in[0xaa,0xab,0xc4]:raise ValueError('Not supported in selected classes: '+s)
    ops.append(f'{start:04d} {s} {operand}'.rstrip())
   m['code_sha256']=hashlib.sha256(code).hexdigest();m['instructions']=ops
   ex=[]
   for _ in range(cr.u(2)):ex.append([cr.u(2),cr.u(2),cr.u(2),cr.u(2)])
   m['exceptions']=ex
  methods.append(m)
 return {'name':name,'parent':parent,'major':major,'fields':fields,'methods':methods}
if __name__=='__main__':
 jar=HERE/'citadel-5633260.jar';rows=[]
 with zipfile.ZipFile(jar) as z:
  for name in ['animation/AnimationHandler','client/model/ModelAnimator','animation/IAnimatedEntity','server/message/AnimationMessage']:
   entry='com/github/alexthe666/citadel/'+name+'.class';b=z.read(entry);p=HERE/'classes'/Path(entry).name;p.parent.mkdir(exist_ok=True);p.write_bytes(b);d=read_class(b);d['entry']=entry;d['class_sha256']=hashlib.sha256(b).hexdigest();rows.append(d)
 (HERE/'selected-bytecode.json').write_text(json.dumps(rows,indent=2)+'\n')
 for d in rows:
  print(d['name'],[(m['name'],len(m.get('instructions',[]))) for m in d['methods']])
