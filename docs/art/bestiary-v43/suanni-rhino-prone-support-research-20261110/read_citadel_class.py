"""Read selected dependency bytecode without loading a JVM or executing the jar."""
import hashlib
import json
import struct
import zipfile
from pathlib import Path

HERE=Path(__file__).resolve().parent
jar=Path('/tmp/dynasty-citadel-3681528.jar')
def inspect(data, selected):
    offset=8
    def take(n):
        nonlocal offset
        result=data[offset:offset+n];offset+=n;return result
    def u1(): return int.from_bytes(take(1),'big')
    def u2(): return int.from_bytes(take(2),'big')
    def u4(): return int.from_bytes(take(4),'big')
    count=u2();cp=[None]*count;i=1
    while i<count:
        tag=u1()
        if tag==1: cp[i]=take(u2()).decode('utf-8',errors='replace')
        elif tag in (3,4): cp[i]=(tag,take(4).hex())
        elif tag in (5,6): cp[i]=(tag,take(8).hex());i+=1
        elif tag in (7,8,16,19,20): cp[i]=(tag,u2())
        elif tag in (9,10,11,12,17,18): cp[i]=(tag,u2(),u2())
        elif tag==15: cp[i]=(tag,u1(),u2())
        else: raise ValueError(tag)
        i+=1
    def ref(i):
        x=cp[i]
        if isinstance(x,str): return x
        if x[0] in (7,8): return ref(x[1])
        if x[0] in (9,10,11,12):return ' / '.join(ref(k) for k in x[1:])
        return str(x)
    take(6);take(2*u2())
    def attributes():
        result=[]
        for _ in range(u2()):
            name=ref(u2());size=u4();result.append((name,take(size)))
        return result
    for _ in range(u2()): take(6);attributes()
    methods={}
    for _ in range(u2()):
        access=u2();name=ref(u2());descriptor=ref(u2());attrs=attributes()
        if name not in selected:continue
        for attr,raw in attrs:
            if attr!='Code':continue
            n=int.from_bytes(raw[4:8],'big');code=raw[8:8+n]
            ops=[];p=0
            simple={0x2b:'aload_1',0x59:'dup',0x24:'fload_2',0x25:'fload_3',0x6a:'fmul',0x66:'fsub',0x6e:'fdiv',0x62:'fadd',0xb1:'return'}
            while p<len(code):
                op=code[p];start=p;p+=1
                if op in (0xb4,0xb5):
                    idx=int.from_bytes(code[p:p+2],'big');p+=2;instruction=('getfield ' if op==0xb4 else 'putfield ')+ref(idx)
                elif op==0x17:instruction='fload '+str(code[p]);p+=1
                elif op in simple:instruction=simple[op]
                else: raise ValueError(f'Unsupported selected-method opcode {op:x} at {start}')
                ops.append([start,instruction])
            methods[name]={'descriptor':descriptor,'code_sha256':hashlib.sha256(code).hexdigest(),'instructions':ops}
    return methods

with zipfile.ZipFile(jar) as z:
    entry='com/github/alexthe666/citadel/client/model/AdvancedEntityModel.class'
    data=z.read(entry);(HERE/'sources/AdvancedEntityModel-3681528.class').write_bytes(data)
    result={'artifact':'curse.maven:citadel4-331936:3681528','jar_sha256':hashlib.sha256(jar.read_bytes()).hexdigest(),'class_sha256':hashlib.sha256(data).hexdigest(),'methods':inspect(data,{'progressPosition','progressRotation','progressPositionPrev','progressRotationPrev'}),'no_java_run':True}
    (HERE/'citadel-exact-helper-observation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
