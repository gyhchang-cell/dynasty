"""Static source extraction only. No pose simulation or runtime execution."""
from pathlib import Path
import hashlib
import json
import re

B=Path(__file__).resolve().parent
model=(B/'sources/ModelGrottol.java').read_text()
constructor=model.split('public ModelGrottol() {',1)[1].split('updateDefaultPose();',1)[0]
names=re.findall(r'this\.(\w+) = new AdvancedModelRenderer\(this',constructor)
fields=re.findall(r'public AdvancedModelRenderer (\w+);',model)
assert set(names)==set(fields) and len(names)==len(set(names))
parents={name:None for name in names}
for parent,child in re.findall(r'this\.(\w+)\.addChild\(this\.(\w+)\)',constructor):
    assert parents[child] is None
    parents[child]=parent
chains={}
for n in names:
    path=[];cursor=n
    while cursor:
        assert cursor not in path
        path.append(cursor);cursor=parents[cursor]
    chains[n]=path
clips=[]
for name in ['IDLE_ANIMATION','DIE_ANIMATION','BURROW_ANIMATION']:
    marker='if (entity.getAnimation() == EntityGrottol.'+name+') {'
    start=model.index(marker);end=model.index('{',start)+1;depth=1
    while depth:
        depth+=(model[end]=='{')-(model[end]=='}');end+=1
    block=re.sub(r'//[^\n]*','',model[start:end])
    tick=0;phases=[];current=None
    for line in block.splitlines():
        m=re.search(r'animator\.(startKeyframe|setStaticKeyframe|resetKeyframe)\((\d+)\)',line)
        if m:
            current={'kind':m[1],'start':tick,'end':tick+int(m[2]),'target':{}}
            tick=current['end'];phases.append(current)
        m=re.search(r'animator\.(rotate|move)\((\w+), ([^;]+)\);',line)
        if m:
            values=[float(v.strip().rstrip('fF')) for v in m[3].split(',')]
            key=m[2]+':'+m[1];old=current['target'].get(key,[0.,0.,0.])
            current['target'][key]=[a+b for a,b in zip(old,values)]
    clips.append({'name':name,'read_lines':[model[:start].count('\n')+1,model[:end].count('\n')+1],
                  'keyframe_sum':tick,'phases':phases})
assert [c['keyframe_sum'] for c in clips]==[47,53,60]
assert len([n for n in names if n.startswith('foot')])==6
assert [c['phases'][-1]['kind'] for c in clips]==['resetKeyframe','setStaticKeyframe','setStaticKeyframe']
out={'kind':'Static full selected model extraction; no pose/runtime simulation',
     'source_sha256':hashlib.sha256((B/'sources/ModelGrottol.java').read_bytes()).hexdigest(),
     'parts':len(names),'declared_box_calls':len(re.findall(r'\.addBox\(',constructor)),
     'field_set_equals_constructors':True,'all_parent_chains_acyclic':True,
     'unparented_parts':[n for n,p in parents.items() if p is None],
     'selected_chains':{n:chains[n] for n in ['head','eyeLeft','clawLeft','foot1Left','foot2Left','foot3Left','foot1Right','foot2Right','foot3Right']},
     'clips':clips,'declared_entity_durations':{'IDLE_ANIMATION':47,'DIE_ANIMATION':73,'HURT_ANIMATION':10,'BURROW_ANIMATION':20},
     'effective_death_removal_from_selected_parent':53,
     'hurt_has_dedicated_model_branch':False,'dedicated_socket_names':[n for n in names if 'socket' in n.lower()],
     'new_accepted_credit':0}
(B/'source-observation.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:out[k] for k in ['parts','declared_box_calls','unparented_parts','dedicated_socket_names']}))
print(json.dumps([{'clip':c['name'],'sum':c['keyframe_sum'],'boundaries':[p['end'] for p in c['phases']]} for c in clips]))
