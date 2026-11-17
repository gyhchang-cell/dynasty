"""Selected graph/call duration inventory; literal counter trace, not world/pose simulation."""
from pathlib import Path
import re,json
b=Path(__file__).resolve().parent
out={}
for species in ['TasmanianDevil','Jerboa']:
    s=(b/('sources/Model'+species+'.java')).read_text()
    fields=re.findall(r'(?:private|public) final AdvancedModelBox (\w+);',s)
    constructor=s.split('public Iterable')[0]
    edges=re.findall(r'(\w+)\.addChild\((\w+)\)',constructor)
    boxes=constructor.count('.addBox(')
    assert set(y for x,y in edges)==set(fields)-{'root'}
    out[species]={'part_count':len(fields),'parts':fields,'edges':edges,'addBox_calls':boxes}
assert out['TasmanianDevil']['part_count']==10 and out['TasmanianDevil']['addBox_calls']==10
assert out['Jerboa']['part_count']==9 and out['Jerboa']['addBox_calls']==8
s=(b/'sources/ModelTasmanianDevil.java').read_text();e=(b/'sources/EntityTasmanianDevil.java').read_text()
clips=[]
for name,body in re.findall(r'animator.setAnimation\(EntityTasmanianDevil\.(\w+)\);(.*?)(?=animator.setAnimation|\n\t}\n)',s,re.S):
    t=0;ph=[]
    for kind,n in re.findall(r'animator\.(startKeyframe|setStaticKeyframe|resetKeyframe)\((\d+)\)',body):
        start=t;t+=int(n);ph.append({'kind':kind,'start':start,'end':t})
    clips.append({'animation':name,'literal_durations_sum':t,'declared':int(re.search(name+r' = Animation.create\((\d+)\)',e).group(1)),'phases':ph,'endKeyframe_calls':body.count('animator.endKeyframe()')})
out['TasmanianDevil']['animations']=clips
assert [c['literal_durations_sum'] for c in clips]==[8,40]
# Fresh local counters, explicit JUMP_ACTIVE sequence; not derived from a native jump.
jump=rebound=0;trace=[]
for i,active in enumerate([True]*9+[False]*5,1):
    if active:
        if jump<5:
            jump+=1
            if rebound>0:rebound-=1
        if jump>=5:
            if rebound<5:rebound+=1
    else:
        if rebound>0:rebound=max(rebound-1,0)
        if jump>0:jump=max(jump-1,0)
    trace.append({'delivered_step':i,'assumed_active':active,'raw_jump':jump,'rebound':rebound,'effective_jump':max(0,jump-rebound)})
out['Jerboa']['literal_counter_trace']=trace
out['limits']=['No physical jump/terrain/head/foot calculation','No Java/game/native execution','Citadel helpers not executed','Duration sum is literal calls; TasmanianDevil ATTACK includes an extra endKeyframe after resetKeyframe, whose exact helper effect remains unread']
(b/'literal-inventory.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'TasmanianDevil':out['TasmanianDevil'],'Jerboa':{'part_count':9,'boxcalls':8,'counter_trace':trace}},indent=2))
