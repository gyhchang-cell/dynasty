"""Literal graph/phase and published scalar expressions only; no pose, Java or native test."""
from pathlib import Path
import json,re
b=Path(__file__).resolve().parent
m=(b/'sources/ModelAnteater.java').read_text(); e=(b/'sources/EntityAnteater.java').read_text()
fields=re.findall(r'public final AdvancedModelBox (\w+);',m)
constructor=m.split('public Iterable<BasicModelPart> parts()')[0]
edges=re.findall(r'(\w+)\.addChild\((\w+)\)',constructor)
clips=[]
for name,s in re.findall(r'animator.setAnimation\(EntityAnteater\.(\w+)\);(.*?)(?=animator.setAnimation|\n    }\n)',m,re.S):
    t=0;ph=[]
    for kind,n in re.findall(r'animator\.(startKeyframe|setStaticKeyframe|resetKeyframe)\((\d+)\)',s):
        end=t+int(n);ph.append({'kind':kind,'start':t,'end':end});t=end
    declared=int(re.search(name+r' = Animation.create\((\d+)\)',e).group(1))
    clips.append({'name':name,'keyframe_sum':t,'declared_ticks':declared,'relative_target_tail':declared-t,'phases':ph})
assert len(fields)==15 and len(edges)==14 and constructor.count('.addBox(')==16
assert [c['keyframe_sum'] for c in clips]==[12,12]
# Compare literal progress scalars at sin(age*.15)=-1, NOT a verified scene.
checks=[]
for prev,curr,partial in [(0,1,.5),(4,5,.5),(5,4,.5),(5,5,.5),(1,0,.5)]:
    body=.2*(prev+(curr-prev)*partial)
    layer=.2*(prev+(curr-prev)*partial*.2)
    checks.append({'prev':prev,'current':curr,'partial':partial,'model_normalized_feed':body,'layer_scale_sine_minus_one':layer,'difference':layer-body})
result={'parts':fields,'edges':edges,'part_count':len(fields),'addBox_calls':16,'animations':clips,'tongue_idle':'declared10; no explicit animator.setAnimation branch; tongueProgress drives procedural tongue','layer_scalar_examples':checks,'scope':'literal fields/phase sums/scalar arithmetic only; not interpolated bone poses, contact or actual render','native_verified':False}
(b/'literal-inventory.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
