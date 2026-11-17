"""Decode fixed local class bytes with Python only; never execute/load Java."""
import hashlib
import json
from pathlib import Path
import struct
from zipfile import ZipFile
OUT=Path(__file__).resolve().parent
def sha(b):return hashlib.sha256(b).hexdigest()
class Reader:
    def __init__(self,b):self.b=b;self.p=0
    def take(self,n):b=self.b[self.p:self.p+n];assert len(b)==n;self.p+=n;return b
    def u1(self):return self.take(1)[0]
    def u2(self):return int.from_bytes(self.take(2),'big')
    def u4(self):return int.from_bytes(self.take(4),'big')
def parse(raw):
    r=Reader(raw);assert r.take(4)==b'\xca\xfe\xba\xbe';minor,major=r.u2(),r.u2();n=r.u2();cp=[None]*n;i=1
    while i<n:
        tag=r.u1()
        if tag==1:cp[i]=(tag,r.take(r.u2()).decode('utf-8',errors='replace'))
        elif tag in (3,4):cp[i]=(tag,r.take(4).hex())
        elif tag in (5,6):cp[i]=(tag,r.take(8).hex());i+=1
        elif tag in (7,8,16,19,20):cp[i]=(tag,r.u2())
        elif tag in (9,10,11,12,17,18):cp[i]=(tag,r.u2(),r.u2())
        elif tag==15:cp[i]=(tag,r.u1(),r.u2())
        else:raise ValueError(('constant tag',tag))
        i+=1
    def resolve(i,depth=0):
        assert depth<10
        e=cp[i]
        if e[0]==1:return e[1]
        if e[0] in (7,8,16,19,20):return resolve(e[1],depth+1)
        if e[0] in (9,10,11):return resolve(e[1],depth+1)+'.'+resolve(e[2],depth+1)
        if e[0]==12:return resolve(e[1],depth+1)+resolve(e[2],depth+1)
        return str(e)
    def attrs(rr):
        result=[]
        for _ in range(rr.u2()):
            name=resolve(rr.u2());b=rr.take(rr.u4());result.append((name,b))
        return result
    flags,this,parent=r.u2(),r.u2(),r.u2()
    for _ in range(r.u2()):r.u2()
    for _ in range(r.u2()):r.take(6);attrs(r)
    methods=[]
    for _ in range(r.u2()):
        access,name,desc=r.u2(),resolve(r.u2()),resolve(r.u2());a=attrs(r)
        method=dict(name=name,descriptor=desc,access=access)
        for k,b in a:
            if k!='Code':continue
            q=Reader(b);stack,locals_=q.u2(),q.u2();code=q.take(q.u4())
            exceptions=[q.take(8).hex() for _ in range(q.u2())];sub=attrs(q);assert q.p==len(b)
            method.update(max_stack=stack,max_locals=locals_,code_sha256=sha(code),code_hex=code.hex(),exception_table=exceptions)
        methods.append(method)
    attrs(r);assert r.p==len(raw)
    return dict(major=major,minor=minor,class_name=resolve(this),super_name=resolve(parent),constant_pool=cp,methods=methods),resolve

MN={0:'nop',1:'aconst_null',2:'iconst_m1',3:'iconst_0',4:'iconst_1',5:'iconst_2',6:'iconst_3',7:'iconst_4',8:'iconst_5',9:'lconst_0',10:'lconst_1',11:'fconst_0',12:'fconst_1',13:'fconst_2',14:'dconst_0',15:'dconst_1',16:'bipush',17:'sipush',18:'ldc',19:'ldc_w',20:'ldc2_w',21:'iload',22:'lload',23:'fload',24:'dload',25:'aload',46:'iaload',47:'laload',48:'faload',49:'daload',50:'aaload',51:'baload',52:'caload',53:'saload',54:'istore',55:'lstore',56:'fstore',57:'dstore',58:'astore',79:'iastore',80:'lastore',81:'fastore',82:'dastore',83:'aastore',84:'bastore',85:'castore',86:'sastore',87:'pop',88:'pop2',89:'dup',90:'dup_x1',91:'dup_x2',92:'dup2',93:'dup2_x1',94:'dup2_x2',95:'swap',96:'iadd',97:'ladd',98:'fadd',99:'dadd',100:'isub',101:'lsub',102:'fsub',103:'dsub',104:'imul',108:'idiv',112:'irem',116:'ineg',120:'ishl',122:'ishr',124:'iushr',126:'iand',128:'ior',130:'ixor',132:'iinc',133:'i2l',134:'i2f',135:'i2d',136:'l2i',140:'f2l',142:'d2i',143:'d2l',151:'dcmpl',152:'dcmpg',153:'ifeq',154:'ifne',155:'iflt',156:'ifge',157:'ifgt',158:'ifle',159:'if_icmpeq',160:'if_icmpne',161:'if_icmplt',162:'if_icmpge',163:'if_icmpgt',164:'if_icmple',165:'if_acmpeq',166:'if_acmpne',167:'goto',168:'jsr',169:'ret',170:'tableswitch',171:'lookupswitch',172:'ireturn',173:'lreturn',174:'freturn',175:'dreturn',176:'areturn',177:'return',178:'getstatic',179:'putstatic',180:'getfield',181:'putfield',182:'invokevirtual',183:'invokespecial',184:'invokestatic',185:'invokeinterface',186:'invokedynamic',187:'new',188:'newarray',189:'anewarray',190:'arraylength',191:'athrow',192:'checkcast',193:'instanceof',194:'monitorenter',195:'monitorexit',196:'wide',197:'multianewarray',198:'ifnull',199:'ifnonnull',200:'goto_w',201:'jsr_w'}
for start,prefix in [(26,'iload'),(30,'lload'),(34,'fload'),(38,'dload'),(42,'aload'),(59,'istore'),(63,'lstore'),(67,'fstore'),(71,'dstore'),(75,'astore')]:
    for i in range(4):MN[start+i]=prefix+'_'+str(i)
def decode(code,resolve):
    r=Reader(code);out=[]
    while r.p<len(code):
        pc=r.p;op=r.u1();args=[];ref=None;targets=[]
        if op==16:args=[int.from_bytes(r.take(1),'big',signed=True)]
        elif op==17:args=[int.from_bytes(r.take(2),'big',signed=True)]
        elif op in (18,21,22,23,24,25,54,55,56,57,58,169,188):args=[r.u1()]
        elif op in (19,20,178,179,180,181,182,183,184,187,189,192,193):args=[r.u2()]
        elif op==132:args=[r.u1(),int.from_bytes(r.take(1),'big',signed=True)]
        elif 153<=op<=168 or op in (198,199):args=[int.from_bytes(r.take(2),'big',signed=True)];targets=[pc+args[0]]
        elif op in (185,186):args=[r.u2(),r.u1(),r.u1()]
        elif op in (200,201):args=[int.from_bytes(r.take(4),'big',signed=True)];targets=[pc+args[0]]
        elif op==197:args=[r.u2(),r.u1()]
        elif op in (170,171):
            while r.p%4:r.u1()
            default=int.from_bytes(r.take(4),'big',signed=True);targets=[pc+default]
            if op==170:
                low=int.from_bytes(r.take(4),'big',signed=True);high=int.from_bytes(r.take(4),'big',signed=True)
                cases=[int.from_bytes(r.take(4),'big',signed=True) for _ in range(high-low+1)];args=[default,low,high,*cases];targets.extend(pc+c for c in cases)
            else:
                n=r.u4();pairs=[(int.from_bytes(r.take(4),'big',signed=True),int.from_bytes(r.take(4),'big',signed=True)) for _ in range(n)]
                args=[default,pairs];targets.extend(pc+p[1] for p in pairs)
        elif op==196:
            inner=r.u1();args=[inner,r.u2()]
            if inner==132:args.append(int.from_bytes(r.take(2),'big',signed=True))
        elif op not in MN:raise ValueError(('unsupported opcode',op,pc))
        if op in (18,19,20,178,179,180,181,182,183,184,185,187,189,192,193,197):ref=resolve(args[0])
        out.append(dict(pc=pc,opcode=op,mnemonic=MN[op],operands=args,reference=ref,branch_targets=targets))
    offsets={e['pc'] for e in out}
    assert all(t in offsets for e in out for t in e['branch_targets'])
    return out
def main():
    jar=next(Path('/Users/a15356015027/Desktop/专业剪辑软件/虚饰作品 v1.3/overrides/mods').glob('*twilightforest*jar'))
    member='twilightforest/world/components/feature/templates/GraveyardFeature.class'
    with ZipFile(jar) as z:raw=z.read(member)
    d,resolve=parse(raw);lines=[]
    for m in d['methods']:
        if 'code_hex' not in m:continue
        m['instructions']=decode(bytes.fromhex(m['code_hex']),resolve)
        lines.append('\n'+m['name']+m['descriptor'])
        lines.extend(f"{e['pc']:4d} {e['mnemonic']:18s} {str(e['operands']):18s} {e['reference'] or ''} {'->'+str(e['branch_targets']) if e['branch_targets'] else ''}" for e in m['instructions'])
    report=dict(source_archive=str(jar),source_archive_sha256=sha(jar.read_bytes()),member=member,class_sha256=sha(raw),class_data=d,
        java_run=False,classes_loaded=False,code_executed=False,building_credit_added=0)
    (OUT/'class-evidence.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    (OUT/'class-reading.txt').write_text('\n'.join(lines)+'\n')
    print('Decoded',d['class_name'],'version',d['major'],'methods',[(m['name'],len(m.get('instructions',[]))) for m in d['methods']])
if __name__=='__main__':main()
