"""Bounded lexical inventory; no Java execution, interpolation, IK or rendered-contact claim."""
from pathlib import Path
import re,json
base=Path(__file__).resolve().parent
model=(base/'sources/ModelKangaroo.java').read_text()
entity=(base/'sources/EntityKangaroo.java').read_text()
fields=re.findall(r'public final AdvancedModelBox (\w+);',model)
children=re.findall(r'(\w+)\.addChild\((\w+)\);',model)
constructor=model.split('public void animate')[0]
clips=[]
for name,body in re.findall(r'animator.setAnimation\(EntityKangaroo\.(\w+)\);(.*?)(?=animator.setAnimation|\n\t}\n)',model,re.S):
    phase=re.findall(r'animator\.(startKeyframe|setStaticKeyframe|resetKeyframe)\((\d+)\)',body)
    total=0; steps=[]
    for kind,n in phase:
        start=total;total+=int(n);steps.append({'kind':kind,'start':start,'end':total})
    declaration=re.search(re.escape(name)+r' = Animation.create\((\d+)\)',entity)
    declared=int(declaration.group(1))
    clips.append({'animation':name,'declared_ticks':declared,'keyframe_ticks':total,'declaration_tail_ticks':declared-total,'phases':steps})
result={'scope':'lexical constructor graph and literal phase durations only','fields':fields,'part_count':len(fields),'add_box_calls':constructor.count('.addBox('),'edges':[{'parent':a,'child':b} for a,b in children],'animations':clips,'native_verified':False,'pose_evaluated':False}
assert len(fields)==19 and len(children)==18 and result['add_box_calls']==18
assert [c['keyframe_ticks'] for c in clips]==[20,15,11,11]
(base/'literal-inventory.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'parts':len(fields),'boxes':result['add_box_calls'],'clips':[(c['animation'],c['keyframe_ticks'],c['declared_ticks']) for c in clips]}))
