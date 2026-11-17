"""Verify exact local research inputs; no production assets or game execution."""
from pathlib import Path
from contextlib import ExitStack
from datetime import datetime, timezone
import hashlib
import json
import zipfile
from PIL import Image
D=Path(__file__).resolve().parent
R=D.parents[2]
def read(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x): (D/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def main():
 ctx=read(D/'collection-context.json')
 for k in ['collector','prior_ledger','chart_collector','icon_chart_collector','candidate_inventory']:
  assert sha(R/ctx[k])==ctx[k+'_sha256'],k
 prior=read(R/ctx['prior_ledger'])
 assert (len(prior['groups']),len(prior['case_to_group']),len(prior['reviewed_case_keys']))==(190,457,471)
 assert set(ctx['skipped_previously_reviewed_cases'])==set(prior['reviewed_case_keys'])
 for x in prior['source_reviews']: assert sha(R/x['path'])==x['sha256']
 baseline=read(D/'source-baseline.json'); assert len(baseline)==289
 changes=[p for p,h in baseline.items() if not (R/p).is_file() or sha(R/p)!=h]
 receipt=read(next(D.glob('texture-requirements-receipt-*.json')))
 assert len(receipt['targets'])==len(set(receipt['targets']))==24
 assert receipt['sha256']==sha(R/receipt['snapshot'])==sha(R/'docs/art/USER_TEXTURE_REQUIREMENTS.md')==sha(Path('/Users/a15356015027/.codex/user-preferences/texture-requirements.md'))
 p=read(D/'provenance.json'); decl=read(D/'resource-declarations.json'); rev=read(D/'semantic-review.json'); anim=read(D/'animation-source.json')
 icons=[a for c in p['cases'] for a in c['icons']]; worn=p['worn_textures']; cases={c['case_key'] for c in p['cases']}
 assert len(cases)==20 and not cases & set(prior['reviewed_case_keys']) and cases==set(ctx['selected_case_keys'])
 assert len(icons)==len(decl)==80 and len(worn)==26 and len(anim)==8
 assert len(rev['pages_opened'])==9 and len(rev['extra_raw_images_opened'])==1
 assert all((D/f).is_file() for f in rev['pages_opened']+rev['extra_raw_images_opened'])
 with ExitStack() as st:
  jars={a['path']:st.enter_context(zipfile.ZipFile(a['path'])) for a in p['archives']}
  assert len(jars)==7
  for a in p['archives']: assert sha(Path(a['path']))==a['sha256']
  for a in icons+worn+[d['model'] for d in decl]+[x['metadata'] for x in anim]:
   assert sha(D/a['local'])==a['sha256']==hashlib.sha256(jars[a['jar']].read(a['entry'])).hexdigest()
   if 'size' in a:
    with Image.open(D/a['local']) as im: assert list(im.size)==a['size']
  for d in decl:
   m=read(D/d['model']['local']); assert m['parent']==d['parent'] and m['textures']['layer0']==d['texture_location']
   ns,t=d['texture_location'].split(':'); assert d['texture']['entry']==f'assets/{ns}/textures/{t}.png'
   assert d['texture'] in next(c['icons'] for c in p['cases'] if c['case_key']==d['case_key'])
  for c in cases: assert {d['part'] for d in decl if d['case_key']==c}=={'helmet','chestplate','leggings','boots'}
  for a in anim:
   meta=read(D/a['metadata']['local'])['animation']; im=Image.open(D/a['source']['local']).convert('RGBA'); assert a['source'] in icons
   assert a['frame_size']==[16,16] and im.width==16 and im.height in [32,192]
   seq=meta.get('frames',list(range(im.height//16))); assert a['sequence']==seq
   assert a['frametime']==meta.get('frametime',1) and a['interpolate']==meta.get('interpolate',False)
   indices={x['index'] if isinstance(x,dict) else x for x in seq}
   assert {f['index'] for f in a['frames']}==indices
   for f in a['frames']:
    assert f['source_rectangle']==[0,16*f['index'],16,16*(f['index']+1)]
    assert hashlib.sha256(im.crop(f['source_rectangle']).tobytes()).hexdigest()==f['rgba_sha256']
   assert not a['source_pixels_changed'] and a['additional_design_credit']==0
   if a['case_key']=='enigmaticlegacy:etherium': assert len(seq)==27
 assert sum(len(x['frames']) for x in anim)==56 and len({x['case_key'] for x in anim})==2
 facts=[]
 for a in worn:
  im=Image.open(D/a['local']).convert('RGBA'); alpha=im.getchannel('A')
  assert not a['binding_proven']
  facts.append({'source':a,'alpha_extrema':list(alpha.getextrema()),'alpha_nonzero':sum(v>0 for v in alpha.getdata()),'bbox':im.getbbox(),'binding_proven':False})
 blank=[x for x in facts if x['source']['case_key']=='enigmaticlegacy:etherium']
 assert len(blank)==2 and len({x['source']['sha256'] for x in blank})==1 and all(x['alpha_nonzero']==0 for x in blank)
 save('native-layer-facts.json',{'layers':facts,'blank_candidate_entries':2,'binding_proof':False,'blank_candidates_provide_uv_credit':False,'game_invisibility_inferred':False})
 groups={g['semantic_group']:g for g in prior['groups']}; new=append=0
 flat=[c for row in rev['observations'] for c in row['cases']]; assert len(flat)==len(set(flat))==20 and set(flat)==cases and not rev['excluded_cases']
 for row in rev['observations']:
  k=row['semantic_group']
  if row['credit']=='NEW_CONSERVATIVE_LEARNING_GROUP':
   assert k not in groups; groups[k]={'semantic_group':k,'cases':[],'observations':[]}; new+=1
  else:
   assert row['credit']=='APPEND_TO_PRIOR_GROUP_ZERO_NEW_DESIGNS' and row['prior_group']==k and k in groups; append+=1
  groups[k]['cases']=sorted(set(groups[k]['cases'])|set(row['cases']))
  groups[k]['observations'].append({'source':str((D/'semantic-review.json').relative_to(R)),'observation':row['observation']})
 owners={}
 for k,g in groups.items():
  for c in g['cases']: assert c not in owners; owners[c]=k
 reviewed=sorted(set(owners)|{e['case_key'] for e in prior['excluded_cases']})
 assert (new,append,len(groups),len(owners),len(reviewed))==(10,5,200,477,491)
 save('combined-semantic-ledger.json',{**prior,'source_reviews':prior['source_reviews']+[{'path':str((D/'semantic-review.json').relative_to(R)),'sha256':sha(D/'semantic-review.json')}],'groups':[g for _,g in sorted(groups.items())],'case_to_group':dict(sorted(owners.items())),'reviewed_case_keys':reviewed,'name_families':491,'armor_name_families':477,'conservative_learning_groups':200})
 save('reference-gate-accounting.json',{'required_valid_related_independent_designs':1000,'reviewed_name_families':491,'armor_name_families_after_exclusion':477,'excluded_from_full_armor_gate':14,'conservative_learning_groups_in_current_subset':200,'validated_independent_design_total':None,'maximum_credit_under_current_one_per_group_policy':200,'unfilled_minimum_under_current_policy':800,'reference_gate_met':False,'gap_limit':'200学习组含局部、变体和反例，不等于200个已验完整独立设计；800仅为所有组合格时最低缺口。'})
 assert all(rev[k]==0 for k in ['new_artwork','production_changes','game_starts','animation_additional_design_credit']) and not rev['gate_met']
 result={'checked_at':datetime.now(timezone.utc).isoformat(),'status':'PASS_RESEARCH_EVIDENCE' if not changes else 'SOURCE_CHANGED_REVIEW_REQUIRED','source_protected_paths':289,'source_unchanged':not changes,'changed_paths':changes,'native_icon_entries_viewed':80,'distinct_icon_payloads':len({a['sha256'] for a in icons}),'model_json_declarations_checked':80,'native_layer_candidate_entries_viewed':26,'distinct_layer_payloads':len({a['sha256'] for a in worn}),'blank_layer_candidates_without_uv_credit':2,'worn_item_binding_proven':False,'animation_metadata_read':8,'source_animation_frame_slots_reviewed':56,'animation_additional_design_credit':0,'new_learning_groups':10,'combined_learning_groups':200,'combined_reviewed_names':491,'validated_independent_design_total':None,'reference_gate_met':False,'new_artwork':0,'production_changes':0,'game_starts':0,'checklist_deletions':0,'evidence_scripts':{f:sha(D/f) for f in ['collect.py','read_animations.py','draw_review_icons.py','record_review.py','verify.py']}}
 save('verification.json',result); print(json.dumps(result,ensure_ascii=False)); assert not changes
if __name__=='__main__': main()
