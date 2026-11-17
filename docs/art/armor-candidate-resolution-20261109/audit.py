"""D30: actual native item-model parent/layer0 resolution, not semantic credit."""
from pathlib import Path
from io import BytesIO
from collections import Counter
import json,hashlib,zipfile
from PIL import Image
D=Path(__file__).resolve().parent;R=D.parents[2];INPUT=R/'docs/art/armor-rpg-robe-reference-20261104/standard-name-candidates.json';PRIOR=R/'docs/art/armor-crab-sunrise-reference-20261109/combined-semantic-ledger.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(D/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
 assert not (D/'candidate-resolution.json').exists()
 src=json.loads(INPUT.read_text());old=json.loads(PRIOR.read_text());candidates=src['unread_candidates'];archives={};rows=[];records={}
 for c in candidates:
  jar=c['jar']
  if jar not in archives:archives[jar]={'sha256':sha(Path(jar)),'candidates':0}
  archives[jar]['candidates']+=1
  with zipfile.ZipFile(jar) as z:
   def native(e):
    b=z.read(e);h=hashlib.sha256(b).hexdigest();loc='models/'+h[:12]+'-'+Path(e).name;key=(jar,e)
    if key not in records:
     (D/loc).parent.mkdir(parents=True,exist_ok=True);(D/loc).write_bytes(b);records[key]={'jar':jar,'entry':e,'local':loc,'sha256':h}
    return records[key]
   def model(e,seen=()):
    if e in seen:return {'error':'MODEL_PARENT_CYCLE','entry':e}
    if e not in z.namelist():return {'external_parent_not_in_this_jar':e,'textures':{},'chain':[]}
    a=native(e);m=json.loads(z.read(e));p=m.get('parent');out={'chain':[a],'textures':{},'declared_parent':p}
    if p and p not in ['item/generated','minecraft:item/generated','builtin/generated','minecraft:builtin/generated']:
     ns,t=p.split(':',1) if ':' in p else ('minecraft',p);base=model(f'assets/{ns}/models/{t}.json',seen+(e,));out['chain']+=base.get('chain',[]);out['textures'].update(base.get('textures',{}));out['inherited_resolution']=base.get('error',base.get('external_parent_not_in_this_jar'))
    out['textures'].update(m.get('textures',{}));return out
   parts=[]
   for part,e in sorted(c['item_models'].items()):
    m=model(e);textures=m['textures'];t=textures.get('layer0');visited=[]
    while t and t.startswith('#'):
     if t in visited:t=None;break
     visited.append(t);t=textures.get(t[1:])
    a={'part':part,'model_resolution':m,'layer0':t,'texture_alias_walk':visited}
    if t:
     ns,path=t.split(':',1) if ':' in t else ('minecraft',t);entry=f'assets/{ns}/textures/{path}.png';a['texture_entry']=entry
     if entry in z.namelist():
      b=z.read(entry);im=Image.open(BytesIO(b));a['native_png']={'entry':entry,'sha256':hashlib.sha256(b).hexdigest(),'size':list(im.size)}
     else:a['missing_from_native_jar']=True
    else:a['no_layer0_after_parent_resolution']=True
    parts.append(a)
   status='ALL_FOUR_NATIVE_LAYER0_PNG_PRESENT' if len(parts)==4 and all('native_png' in a for a in parts) else 'NATIVE_RESOLUTION_INCOMPLETE'
   rows.append({'case_key':c['case_key'],'jar':jar,'parts':parts,'resource_resolution':status,'visual_review_complete':False,'reference_credit':0})
 # native four-icon equality groups only: byte identity is a dedup clue, never full design credit.
 fingerprints={}
 for row in rows:
  if row['resource_resolution']=='ALL_FOUR_NATIVE_LAYER0_PNG_PRESENT':
   fp=tuple((p['part'],p['native_png']['sha256']) for p in row['parts']);fingerprints.setdefault(fp,[]).append(row['case_key'])
 out={'scope':'D30 mechanical prerequisite resolution, no visual/semantic/full-design credit','input':str(INPUT.relative_to(R)),'input_sha256':sha(INPUT),'prior_ledger':str(PRIOR.relative_to(R)),'prior_ledger_sha256':sha(PRIOR),'archives':archives,'model_source_records':list(records.values()),'candidates':rows,'equal_four_icon_byte_groups':[v for v in fingerprints.values() if len(v)>1],'counts':dict(Counter(r['resource_resolution'] for r in rows)),'native_missing_png_parts':sum(p.get('missing_from_native_jar',False) for r in rows for p in r['parts']),'no_layer0_parts':sum(p.get('no_layer0_after_parent_resolution',False) for r in rows for p in r['parts']),'reference_credit':0,'reference_gate_met':False,'game_starts':0,'production_changes':0,'checklist_deletions':0,'limits':['Not a visual review or independent design register','Native absence does not prove a game bug: external resource packs may supply files','Shared byte icons do not prove shared worn geometry, and different PNG hashes do not prove different designs','Existing names must be matched semantically against prior source reviews before any new credit']}
 save('candidate-resolution.json',out);print(json.dumps({k:out[k] for k in ['counts','native_missing_png_parts','no_layer0_parts','equal_four_icon_byte_groups','reference_credit']},ensure_ascii=False))
if __name__=='__main__':main()
