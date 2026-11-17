"""Read JVM class bytes as data using Python only. Does not load/execute classes."""
import struct,json,hashlib
from pathlib import Path
from zipfile import ZipFile
P=Path(__file__).resolve().parent;R=P.parents[2]
assert not(P/'RECEIPT.json').exists()
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def parse(raw):
 assert raw[:4]==b'\xca\xfe\xba\xbe'
 pos=8
 def u(n=2):
  nonlocal pos
  v=int.from_bytes(raw[pos:pos+n],'big');pos+=n;return v
 count=u();cp=[None]*count;i=1
 while i<count:
  t=u(1)
  if t==1:
   n=u();cp[i]=(t,raw[pos:pos+n].decode('utf-8',errors='replace'));pos+=n
  elif t in [3,4]:
   cp[i]=(t,int.from_bytes(raw[pos:pos+4],'big',signed=t==3));pos+=4
  elif t in [5,6]:cp[i]=(t,raw[pos:pos+8].hex());pos+=8;i+=1
  elif t in [7,8,16,19,20]:cp[i]=(t,u())
  elif t in [9,10,11,12,17,18]:cp[i]=(t,u(),u())
  elif t==15:cp[i]=(t,u(1),u())
  else:raise ValueError(t)
  i+=1
 def resolve(i):
  c=cp[i];t=c[0]
  if t in [1,3,4,5,6]:return c[1]
  if t in [7,8,16,19,20]:return resolve(c[1])
  if t==12:return str(resolve(c[1]))+str(resolve(c[2]))
  if t in [9,10,11]:return str(resolve(c[1]))+'.'+str(resolve(c[2]))
  if t==15:return dict(reference_kind=c[1],target=resolve(c[2]))
  if t in [17,18]:return dict(bootstrap_index=c[1],name_and_type=resolve(c[2]))
  return str(c)
 access=u();this=u();super_=u();interfaces=[u()for _ in range(u())]
 def attrs():
  nonlocal pos
  out=[]
  for _ in range(u()):
   name=resolve(u());n=u(4);b=raw[pos:pos+n];pos+=n;out.append((name,b))
  return out
 fields=[]
 for _ in range(u()):
  flags=u();name=resolve(u());desc=resolve(u());at=attrs();fields.append(dict(flags=flags,name=name,descriptor=desc))
 methods=[]
 for _ in range(u()):
  flags=u();name=resolve(u());desc=resolve(u());at=attrs();method=dict(flags=flags,name=name,descriptor=desc)
  for key,b in at:
   if key=='Code':
    stack,locals_,n=struct.unpack_from('>HHI',b);code=b[8:8+n]
    method.update(max_stack=stack,max_locals=locals_,code_bytes=n,instructions=disassemble(code,resolve))
  methods.append(method)
 class_attrs=attrs();assert pos==len(raw);bootstraps=[]
 for name,b in class_attrs:
  if name=='BootstrapMethods':
   n=int.from_bytes(b[:2],'big');q=2
   for index in range(n):
    ref,count=struct.unpack_from('>HH',b,q);q+=4;args=[int.from_bytes(b[q+i*2:q+i*2+2],'big')for i in range(count)];q+=count*2
    bootstraps.append(dict(index=index,method=resolve(ref),arguments=[resolve(i)for i in args]))
   assert q==len(b)
 return dict(class_name=resolve(this),super_class=resolve(super_),class_major=int.from_bytes(raw[6:8],'big'),fields=fields,methods=methods,bootstrap_methods=bootstraps,constant_pool=[dict(index=i,tag=c[0],resolved=resolve(i))for i,c in enumerate(cp)if c],parser_consumed_entire_file=True,executed=False)
def disassemble(code,resolve):
 names={0:'nop',1:'aconst_null',2:'iconst_m1',3:'iconst_0',4:'iconst_1',5:'iconst_2',6:'iconst_3',7:'iconst_4',8:'iconst_5',16:'bipush',17:'sipush',18:'ldc',19:'ldc_w',20:'ldc2_w',21:'iload',22:'lload',23:'fload',24:'dload',25:'aload',46:'iaload',50:'aaload',54:'istore',58:'astore',79:'iastore',83:'aastore',87:'pop',88:'pop2',89:'dup',90:'dup_x1',91:'dup_x2',92:'dup2',95:'swap',96:'iadd',100:'isub',104:'imul',108:'idiv',112:'irem',116:'ineg',120:'ishl',122:'ishr',124:'iushr',126:'iand',128:'ior',130:'ixor',132:'iinc',133:'i2l',134:'i2f',135:'i2d',153:'ifeq',154:'ifne',155:'iflt',156:'ifge',157:'ifgt',158:'ifle',159:'if_icmpeq',160:'if_icmpne',161:'if_icmplt',162:'if_icmpge',163:'if_icmpgt',164:'if_icmple',165:'if_acmpeq',166:'if_acmpne',167:'goto',168:'jsr',169:'ret',170:'tableswitch',171:'lookupswitch',172:'ireturn',173:'lreturn',174:'freturn',175:'dreturn',176:'areturn',177:'return',178:'getstatic',179:'putstatic',180:'getfield',181:'putfield',182:'invokevirtual',183:'invokespecial',184:'invokestatic',185:'invokeinterface',186:'invokedynamic',187:'new',188:'newarray',189:'anewarray',190:'arraylength',191:'athrow',192:'checkcast',193:'instanceof',194:'monitorenter',195:'monitorexit',196:'wide',197:'multianewarray',198:'ifnull',199:'ifnonnull',200:'goto_w',201:'jsr_w'}
 for base,kind in [(26,'iload'),(30,'lload'),(34,'fload'),(38,'dload'),(42,'aload'),(59,'istore'),(63,'lstore'),(67,'fstore'),(71,'dstore'),(75,'astore')]:
  for i in range(4):names[base+i]=f'{kind}_{i}'
 one={16,18,21,22,23,24,25,54,55,56,57,58,169,188}
 two={17,19,20,132,*range(153,169),*range(178,185),187,189,192,193,198,199}
 cpops={18,19,20,*range(178,190),192,193,197}-{188}
 out=[];pc=0
 while pc<len(code):
  start=pc;op=code[pc];pc+=1;n=1 if op in one else 2 if op in two else 4 if op in [185,186,200,201]else 3 if op==197 else 0
  if op in [170,171]:
   pc+=(4-pc%4)%4
   default=int.from_bytes(code[pc:pc+4],'big',signed=True);pc+=4
   if op==170:
    lo,hi=struct.unpack_from('>ii',code,pc);pc+=8;offsets=[int.from_bytes(code[pc+i*4:pc+i*4+4],'big',signed=True)for i in range(hi-lo+1)];pc+=4*len(offsets);special=dict(default_target=start+default,cases={str(lo+i):start+x for i,x in enumerate(offsets)})
   else:
    count=int.from_bytes(code[pc:pc+4],'big');pc+=4;pairs=[struct.unpack_from('>ii',code,pc+i*8)for i in range(count)];pc+=8*count;special=dict(default_target=start+default,cases={str(k):start+v for k,v in pairs})
   out.append(dict(pc=start,op=names[op],**special));continue
  if op==196:
   n=5 if code[pc]==132 else 3
  operands=code[pc:pc+n];pc+=n;assert pc<=len(code)
  row=dict(pc=start,op=names.get(op,f'op_{op:02x}'),bytes=code[start:pc].hex())
  if n:row['operands']=list(operands)
  if op in cpops:
   index=operands[0]if op==18 else int.from_bytes(operands[:2],'big');row['constant_index']=index;row['constant']=resolve(index)
  if op in [16,17]:row['signed_value']=int.from_bytes(operands,'big',signed=True)
  if op in {*range(153,169),198,199,200,201}:row['branch_target']=start+int.from_bytes(operands,'big',signed=True)
  out.append(row)
 starts={x['pc']for x in out}
 for row in out:
  if 'branch_target'in row:assert row['branch_target']in starts
  if 'cases'in row:assert row['default_target']in starts and all(x in starts for x in row['cases'].values())
 return out
def main():
 old=R/'docs/architecture/research-20261102-dungeons-034/boundary-evidence.json';prior=json.loads(old.read_text());arc=bind(prior['archive']['path']);assert arc['sha256']==prior['archive']['sha256']
 outputs=[]
 with ZipFile(arc['path'])as z:
  for suffix in ['StructureGuling','StructureGuling$Piece']:
   member='com/eeeab/eeeabsmobs/sever/world/structure/'+suffix+'.class';raw=z.read(member);d=parse(raw)
   d.update(source=dict(archive=arc,member=member,sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw)),limits='Python static classfile decoding only; no JVM execution/native placement. Unnamed opcodes retain exact bytes; parsing does not certify assembly interpretation.')
   path=P/(suffix+'-static.json');path.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');outputs.append(bind(path))
   print(suffix,[(v['name'],v['descriptor'],v.get('code_bytes'))for v in d['methods']])
 (P/'active-checkpoint.json').write_text(json.dumps(dict(batch=310,status='GULING_STATIC_METHOD_BYTES_DECODED_PENDING_ACTUAL_READING',prior034=bind(old),archive=arc,class_reports=outputs,classfiles_executed=False,PNGs=0,new_complete_whole_studies=0,formal_credit_added=0,next='Read actual placement methods/rotation and perpiece origin; do not infer offsets from class strings or count four templates as four buildings.'),ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
