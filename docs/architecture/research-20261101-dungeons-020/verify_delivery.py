#!/usr/bin/env python3
"""Verify source bytes, exact pool identities, scope chain, observed-file receipts.

This is mechanical evidence verification, not proof of visual reading, native
routes, design novelty, independent human review or completed production work.
"""
import ast
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
from zipfile import ZipFile
from PIL import Image
OUT=Path(__file__).resolve().parent
BASE=OUT.parent
ROOT=OUT.parents[2]
sys.path.insert(0,str(ROOT/'tools/architecture'))
from nbt_read import read
from reference_components import geometry_hash,role
from whole_building_candidates import AIR
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(b):return hashlib.sha256(b).hexdigest()
def get(p):return json.loads(p.read_text())
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def evidence(e,is_image=False):
 p=Path(e['path']);assert sha(p)==e['sha256'],p
 if is_image:
  with Image.open(p) as im:im.verify()
def exact(value,ident):
 if isinstance(value,str):return value==ident
 if isinstance(value,dict):return any(exact(v,ident) for v in value.values())
 if isinstance(value,list):return any(exact(v,ident) for v in value)
 return False
def main():
 previous=BASE/'research-20261101-proposal-semantic-acceptance-010-015'
 original=get(previous/'scoped-reference-register.json')
 for e in original['preserved_registries']:evidence(e)
 for folder in [previous,BASE/'research-20261101-dungeons-016']:
  for e in get(folder/'RECEIPT.json')['files']:
   p=folder/e['path'];assert p.stat().st_size==e['bytes'] and sha(p)==e['sha256'],p
 folders=[BASE/f'research-20261101-dungeons-{n:03d}' for n in [17,18,19,20]]
 archive_cache={};all_raw={};images=set();oldimages=set();credit=[];reports=[]
 expected_scope_counts=[[4,7,1],[4,7,1],[5,7,1],[6,7,1]]
 for n,folder in zip([17,18,19,20],folders):
  src=get(folder/'sources.json');rev=get(folder/'manual-review.json');audit=get(folder/'raw-source-audit.json')
  details=get(folder/'detail-evidence.json');dd=get(folder/'dedup-evidence.json');scope=get(folder/'scoped-reference-update.json')
  count={17:4,18:4,19:2,20:1}[n]
  assert all(len(x)==count for x in [src['candidates'],rev['entries'],audit['entries'],details['entries'],dd['entries']])
  assert dd['historical_unique_local_archive_member_pairs']=={17:197,18:197,19:201,20:203}[n]
  assert not dd['within_batch_exact_duplicate_pairs']
  discovery=get(folder/'discovery-boundary.json')
  assert discovery['local_only'] and discovery['network_requests']==0 and not discovery['java_run'] and not discovery['game_run']
  for e in discovery['indices_checked']:evidence(e)
  evidence(scope['prior_update']);evidence(scope['original_scope_definitions']);evidence(scope['previous_hold_evidence'])
  assert not scope['scope_definitions_changed'] and scope['previous_two_holds_retained']==['011-F04','012-F03']
  assert not scope['previous_hold_evidence_reopened_this_batch'] and not scope['independent_human_reviewer_claimed']
  assert scope['production_changes']==scope['production_tasks_completed']==scope['checklist_deletions']==0
  assert [s['accepted_references'] for s in scope['scopes']]==expected_scope_counts[n-17]
  for new,old in zip(scope['scopes'],original['scopes']):
   assert new['scope_id']==old['scope_id'] and new['scope_definition']==old['scope_definition']
   assert new['target']==1000 and new['remaining']==1000-new['accepted_references'] and not new['construction_allowed']
   assert len(new['accepted_ids'])==len(set(new['accepted_ids']))==new['accepted_references']
  for a in src['source_archives']:
   if a['path'] not in archive_cache:archive_cache[a['path']]=sha(Path(a['path']))
   assert archive_cache[a['path']]==a['sha256']
  batch_images=set()
  for c,r,a,de,ded in zip(src['candidates'],rev['entries'],audit['entries'],details['entries'],dd['entries']):
   ident=f"{n:03d}-{c['id']}";assert c['id']==r['id']==a['id']==de['id']==ded['id']
   assert c==r['source'] and not r['native_acceptance'] and not ded['historical_exact_matches']
   assert set(r['observations'])=={'layout','proportion','facade','roof','materials','circulation','terrain'}
   with ZipFile(c['source_archive']) as z:
    raw=z.read(c['member']);nbt=read(raw);pal=nbt.get('palette')or nbt['palettes'][0]
    assert digest(raw)==c['nbt_sha256']==a['nbt_sha256']==ded['nbt_sha256'] and nbt['size']==c['size']==a['size']
    cells={tuple(b['pos']):pal[b['state']]for b in nbt['blocks']if pal[b['state']]['Name']not in AIR};all_raw[ident]=cells
    assert len(cells)==c['nonair'] and dict(Counter(s['Name']for s in cells.values()))==c['materials']==a['materials']
    assert a['occupied_bounds']==de['occupied_bounds']==[[min(p[i]for p in cells),max(p[i]for p in cells)]for i in range(3)]
    assert geometry_hash({p:1 for p in cells},nbt['size'])==ded['occupancy_sha256']
    assert geometry_hash({p:role(s['Name'])for p,s in cells.items()},nbt['size'])==ded['role_sha256']
    opening=[dict(position=list(p),state=s)for p,s in cells.items()if s['Name'].endswith(('_stairs','_door','_trapdoor','_fence_gate'))or s['Name']=='minecraft:ladder']
    assert opening==a['original_vertical_opening_states']
    sockets=[dict(position=b['pos'],state=pal[b['state']],data=b.get('nbt',{}))for b in nbt['blocks']if pal[b['state']]['Name']=='minecraft:jigsaw']
    assert sockets==c['sockets']==a['sockets']
    source_id=c['member'].split('/structures/')[0].split('/')[-1]+':'+c['member'].split('/structures/')[1][:-4]
    assert {x['member']for x in c['pool_references']}=={x['member']for x in a['archive_json_identity_mentions']}
    for e in a['archive_json_identity_mentions']:
     b=z.read(e['member']);assert digest(b)==e['sha256'] and json.loads(b)==e['data'] and exact(e['data'],source_id)
    assert {e['pool']for e in a['outgoing_pools']}=={e['data']['pool']for e in sockets}
    for e in a['outgoing_pools']:
     assert not e['assembled'] and e['building_credit']==0
     if e['status']=='FOUND_LOCAL':
      b=z.read(e['member']);assert digest(b)==e['sha256'] and json.loads(b)==e['data']
     elif e['status']=='EMPTY_TERMINAL':assert e['pool']=='minecraft:empty'
     else:assert e['status']=='NOT_PRESENT_IN_FIXED_SOURCE_ARCHIVE' and e['member']not in z.namelist()
   for e in r['actual_images_viewed']:evidence(e,True);images.add(e['path']);batch_images.add(e['path'])
   assert len(r['actual_images_viewed'])==({17:2,18:2,19:4,20:4}[n])
   if r['credit']:credit.append(ident)
   if n==17:assert max(c['size'][0],c['size'][2])<15 and r['credit']==0
   if n==18:assert a['occupied_bounds'][1]==[0,20] and r['credit']==0
  for e in rev.get('historical_comparison_views',[]):evidence(e,True);oldimages.add(e['path'])
  assert len(batch_images)==rev['actual_new_images_viewed']
  assert sum(e['credit']for e in rev['entries'])==rev['independent_references_added']==scope['added_credit']
  for p in folder.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
  reports.append(dict(batch=n,templates_studied=count,actual_images_viewed=len(batch_images),independent_references_added=scope['added_credit'],
   scope_counts=[dict(scope_id=s['scope_id'],accepted=s['accepted_references'],remaining=s['remaining'],construction_allowed=False)for s in scope['scopes']],
   source_bytes_original_states_exact_pool_values_verified=True,production_changes=0,checklist_deletions=0,java_run=False,game_run=False,network_requests=0))
 assert len(all_raw)==11 and len(images)==28 and len(oldimages)==8 and credit==['019-F01','020-F01']
 # A lower-band match is not silently expanded into whole-template equality.
 f=get(folders[0]/'family-evidence.json')['evidence']
 a={(x,y-1,z):s for (x,y,z),s in all_raw['017-F03'].items()if 3<=y<=6}
 b={p:s for p,s in all_raw['017-F04'].items()if 2<=p[1]<=5}
 assert len(a)==len(b)==len(a.keys()&b.keys())==f['common_positions']==168
 assert sum(a[p]==b[p]for p in a.keys()&b.keys())==f['same_original_name_and_properties']==167
 assert [dict(translated_position=list(p),left=a.get(p),right=b.get(p))for p in sorted(a.keys()|b.keys())if a.get(p)!=b.get(p)]==f['differences']
 assert not any(s['Name'].endswith(('_stairs','_door'))or s['Name']=='minecraft:ladder' for s in all_raw['018-F04'].values())
 for row in get(folders[1]/'family-evidence.json')['evidence']['pairs']:
  left,right=row['pair'];a=all_raw['018-'+left];b=all_raw['018-'+right];common=a.keys()&b.keys();union=a.keys()|b.keys()
  assert row['common_positions']==len(common) and row['union_positions']==len(union) and row['occupancy_jaccard']==len(common)/len(union)
  assert row['same_original_name_and_properties']==sum(a[p]==b[p]for p in common)
 assert get(folders[2]/'manual-review.json')['entries'][1]['credit']==0
 # Regression check: exact "forest_fort" must not match "forest_fort_ground".
 ground=get(OUT/'ground-boundary.json')
 assert ground['size']==[22,1,29] and ground['building_credit']==0 and not ground['assembled'] and not ground['component_images_viewed']
 with ZipFile(ground['source_archive']) as z:
  raw=z.read(ground['member']);assert digest(raw)==ground['sha256'];d=read(raw);pal=d['palette']
  assert dict(Counter(pal[b['state']]['Name']for b in d['blocks']))==ground['materials']
  for e in ground['exact_definition_documents']:
   raw=z.read(e['member']);assert digest(raw)==e['sha256'] and json.loads(raw)==e['data']
 start=next(e['data']for e in ground['exact_definition_documents']if e['member'].endswith('forest_fort_start.json'))
 assert not exact(start,'simply_houses:forest_fort/forest_fort') and exact(start,'simply_houses:forest_fort/forest_fort_ground')
 assert len(get(OUT/'sources.json')['candidates'][0]['pool_references'])==1
 legacy=get(OUT/'prior-prefix-audit.json');evidence(legacy['original_index'])
 assert legacy['new_visual_readings']==legacy['new_buildings']==legacy['credit_change']==0 and not legacy['previous_files_modified']
 assert [len(e['false_prefix_pool_records'])for e in legacy['entries']]==[4,0,0,0,0]
 assert legacy['entries'][0]['original_credit']==0 and legacy['entries'][1]['original_credit']==1
 assert all(len(e['valid_exact_pool_records'])==1 for e in legacy['entries'])
 for e in legacy['entries']:
  old=next(c for c in get(Path(legacy['original_index']['path']))['candidates']if c['member']==e['body_member'])
  with ZipFile(old['source_archive'])as z:
   assert digest(z.read(e['body_member']))==e['body_nbt_sha256']
   for valid,key in [(True,'valid_exact_pool_records'),(False,'false_prefix_pool_records')]:
    for r in e[key]:
     raw=z.read(r['member']);assert digest(raw)==r['sha256'] and json.loads(raw)==r['data'] and exact(r['data'],e['exact_identity'])==valid
 for folder,report in zip(folders,reports):
  if folder==OUT:
   report.update(status='PASS_FOUR_BATCHES_ELEVEN_CANDIDATES_TWO_SCOPED_REFERENCES',joint_templates_studied=11,
    joint_actual_new_images_viewed=28,joint_unique_historical_images_viewed=8,joint_independent_references_added=2,accepted_ids=credit,
    prior_acceptance_and_batch016_receipts_unchanged=True,other_scope_registry_hashes_unchanged=True,
    old_two_holds_retained=True,old_two_holds_reopened=False,new_ruin_hold_retained=True,
    original_scope_definitions_unchanged=True,ground_component_building_credit=0,
    exact_resource_identifier_regression_pass=True,legacy_016_F01_four_prefix_pool_records_corrected_in_appendix=True,legacy_credit_change=0,independent_human_review_claimed=False,
    no_native_collision_terrain_or_gameplay_acceptance=True,sound_brightness_window_save_changes=0)
  else:report['status']='PASS_SOURCE_AND_SCOPE_BOUNDARIES'
  write(folder/'verification.json',report)
  files=sorted(p for p in folder.rglob('*')if p.is_file() and p.name!='RECEIPT.json')
  write(folder/'RECEIPT.json',dict(status=report['status'],files=[dict(path=str(p.relative_to(folder)),bytes=p.stat().st_size,sha256=sha(p))for p in files]))
  for e in get(folder/'RECEIPT.json')['files']:
   p=folder/e['path'];assert p.stat().st_size==e['bytes'] and sha(p)==e['sha256']
 print(json.dumps(get(OUT/'verification.json'),ensure_ascii=False))
if __name__=='__main__':main()
