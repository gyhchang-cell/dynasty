"""Read existing pinned JAR bytes only; adds switch decoding to prior bounded reader."""
from pathlib import Path
import json,zipfile,hashlib
OLD=Path("docs/art/bestiary-v43/citadel-5633260-animation-lifecycle-20261111/read_selected_classes.py")
src=OLD.read_text()
old="    elif op in[0xaa,0xab,0xc4]:raise ValueError('Not supported in selected classes: '+s)"
new="""    elif op in[0xaa,0xab]:
     br.take((-br.p)%4)
     default=start+int.from_bytes(br.take(4),'big',signed=True)
     if op==0xaa:
      low=int.from_bytes(br.take(4),'big',signed=True);high=int.from_bytes(br.take(4),'big',signed=True)
      pairs=[(i,start+int.from_bytes(br.take(4),'big',signed=True))for i in range(low,high+1)]
     else:
      count=br.u(4);pairs=[(int.from_bytes(br.take(4),'big',signed=True),start+int.from_bytes(br.take(4),'big',signed=True))for _ in range(count)]
     operand=str({'default':default,'pairs':pairs})
    elif op==0xc4:raise ValueError('wide unsupported')"""
assert old in src
ns={'__file__':str(OLD.resolve()),'__name__':'reader_extension'}
exec(compile(src.replace(old,new),str(OLD), 'exec'),ns)
if __name__=='__main__':
 with zipfile.ZipFile(OLD.parent/'citadel-5633260.jar')as z:
  entry='com/github/alexthe666/citadel/server/entity/pathfinding/raycoms/AdvancedPathNavigate.class'
  b=z.read(entry);d=ns['read_class'](b,{'<init>'});d['entry']=entry;d['class_sha256']=hashlib.sha256(b).hexdigest()
  Path(__file__).with_name('navigation-constructors.json').write_text(json.dumps(d,indent=2)+'\n')
  for m in d['methods']:
   if m['name']=='<init>':
    print(m['descriptor']);print('\n'.join(m['instructions']))
