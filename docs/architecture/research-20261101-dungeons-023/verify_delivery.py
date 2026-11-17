#!/usr/bin/env python3
"""Mechanical verification of three local rereviews; no native/game approval."""
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
def digest(b):return hashlib.sha256(b).hexdigest()
def sha(p):return digest(p.read_bytes())
def get(p):return json.loads(p.read_text())
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def evidence(e,image=False):
 p=Path(e['path']);assert sha(p)==e['sha256'],p
 if image:
  with Image.open(p)as im:im.verify()
def exact(v,k):
 if isinstance(v,str):return v==k
 if isinstance(v,dict):return any(exact(x,k)for x in v.values())
 if isinstance(v,list):return any(exact(x,k)for x in v)
 return False
def main():
 original=BASE/'research-20261101-proposal-semantic-acceptance-010-015'
 definitions=get(original/'scoped-reference-register.json')
 for e in definitions['preserved_registries']:evidence(e)
 preserved=[original]+[BASE/f'research-20261101-dungeons-{n:03d}'for n in range(16,21)]
 for folder in preserved:
  for e in get(folder/'RECEIPT.json')['files']:
   p=folder/e['path'];assert p.stat().st_size==e['bytes']and sha(p)==e['sha256'],p
 folders=[BASE/f'research-20261101-dungeons-{n:03d}'for n in [21,22,23]]
 archives={};allcells={};identities=set();oldimages=set();newimages=set();credits=[];reports=[]
 parent=BASE/'research-20261101-dungeons-020/scoped-reference-update.json'
 for n,folder in zip([21,22,23],folders):
  src=get(folder/'sources.json');rev=get(folder/'manual-review.json');dd=get(folder/'dedup-evidence.json')
  audit=get(folder/'raw-source-audit.json');details=get(folder/'detail-evidence.json')
  planes=get(folder/'room-layer-original-states.json');scope=get(folder/'scoped-reference-update.json')
  boundary=get(folder/'discovery-boundary.json')
  assert src['new_source_templates']==rev['new_source_templates']==dd['new_source_templates']==boundary['new_source_templates']==0
  assert boundary['local_only']and boundary['network_requests']==0 and not boundary['java_run']and not boundary['game_run']
  assert not boundary['components_assembled']and boundary['generated_structure_assets']==0
  assert boundary['sound_brightness_window_save_changes']==boundary['production_changes']==boundary['checklist_deletions']==0
  for e in boundary['indices_checked']:evidence(e)
  count=5 if n==21 else 3
  assert all(len(x)==count for x in [src['candidates'],rev['entries'],dd['entries'],audit['entries'],details['entries'],planes['entries']])
  assert dd['historical_unique_local_archive_member_pairs']==204 and not dd['within_batch_exact_duplicate_pairs']
  for e in src['source_archives']:
   if e['path']not in archives:archives[e['path']]=sha(Path(e['path']))
   assert archives[e['path']]==e['sha256']
  for c,r,d,a,de,pl in zip(src['candidates'],rev['entries'],dd['entries'],audit['entries'],details['entries'],planes['entries']):
   assert c['id']==r['id']==d['id']==a['id']==de['id']==pl['id']
   assert c==r['source']and c['prior_identity']==r['prior_identity']==pl['prior_identity']
   assert c['source_is_previously_studied']and c['new_source_template_credit']==0
   assert not r['native_acceptance']and not r['independent_human_review']
   assert set(r['observations'])=={'layout','proportion','facade','roof','materials','circulation','terrain'}
   evidence(c['original_index']);evidence(c['original_whole_image'],True)
   with ZipFile(c['source_archive'])as z:
    raw=z.read(c['member']);nbt=read(raw);pal=nbt.get('palette')or nbt['palettes'][0]
    assert digest(raw)==c['nbt_sha256']==a['nbt_sha256']==d['nbt_sha256']
    assert nbt['size']==c['size']==a['size']
    states={tuple(b['pos']):pal[b['state']]for b in nbt['blocks']}
    cells={p:s for p,s in states.items()if s['Name']not in AIR}
    allcells[(n,c['id'])]=cells;identities.add((c['source_archive'],c['member']))
    assert len(cells)==c['nonair']and dict(Counter(s['Name']for s in cells.values()))==c['materials']==a['materials']
    assert a['occupied_bounds']==de['occupied_bounds']==[[min(p[i]for p in cells),max(p[i]for p in cells)]for i in range(3)]
    assert geometry_hash({p:1 for p in cells},nbt['size'])==d['occupancy_sha256']
    assert geometry_hash({p:role(s['Name'])for p,s in cells.items()},nbt['size'])==d['role_sha256']
    assert [dict(position=list(p),state=s)for p,s in states.items()if any(k in s['Name']for k in ['stairs','ladder','door','gate','jigsaw'])]==c['opening_and_vertical_states']
    assert [dict(position=list(p),state=s)for p,s in cells.items()if s['Name'].endswith(('_stairs','_door','_trapdoor','_fence_gate'))or s['Name']=='minecraft:ladder']==a['original_vertical_opening_states']
    sockets=[dict(position=b['pos'],state=pal[b['state']],data=b.get('nbt',{}))for b in nbt['blocks']if pal[b['state']]['Name']=='minecraft:jigsaw']
    assert sockets==c['sockets']==a['sockets']
    own=[e for e in d['historical_exact_matches']if e['archive']==c['source_archive']and e['member']==c['member']]
    assert len(own)==1 and 'nbt_sha256'in own[0]['reasons']
    ident=c['source_dedup_identity']
    assert {e['member']for e in c['pool_references']}=={e['member']for e in a['archive_json_identity_mentions']if '/worldgen/template_pool/'in e['member']}
    for e in a['archive_json_identity_mentions']:
     raw=z.read(e['member']);assert digest(raw)==e['sha256']and json.loads(raw)==e['data']and exact(e['data'],ident)
    for e in a['outgoing_pools']:
     assert not e['assembled']and e['building_credit']==0
     if e['status']=='FOUND_LOCAL':
      raw=z.read(e['member']);assert digest(raw)==e['sha256']and json.loads(raw)==e['data']
     elif e['status']=='EMPTY_TERMINAL':assert e['pool']=='minecraft:empty'
     else:assert e['status']=='NOT_PRESENT_IN_FIXED_SOURCE_ARCHIVE'and e['member']not in z.namelist()
    for plane in pl['selected_horizontal_planes']:
     rows=[dict(position=list(p),state=s)for p,s in states.items()if p[1]==plane['y']]
     assert rows==plane['original_states']and len(rows)==plane['stored_positions']
     assert plane['possible_positions']==nbt['size'][0]*nbt['size'][2]
     assert sum(e['state']['Name']in AIR for e in rows)==plane['explicit_air_positions']
     assert sum(e['state']['Name']not in AIR for e in rows)==plane['nonair_positions']
   assert len(r['actual_images_viewed'])==2
   for e in r['actual_images_viewed']:evidence(e,True)
   oldimages.add(r['actual_images_viewed'][0]['path']);newimages.add(r['actual_images_viewed'][1]['path'])
   if r['credit']:credits.append(r['credit_identity']);assert (n,c['id'])==(21,'T01')and r['credit']==1
  for e in rev['historical_far_controls']:
   evidence(e['image'],True);assert e['actual_image_viewed']and e['new_template_credit']==e['reference_credit']==0
   oldimages.add(e['image']['path'])
  assert rev['actual_new_section_images_viewed']==count
  assert rev['actual_unique_previous_whole_images_viewed']==count+(4 if n==21 else 0)
  evidence(scope['prior_update']);assert scope['prior_update']['path']==str(parent)
  evidence(scope['original_scope_definitions']);evidence(scope['previous_hold_evidence'])
  assert scope['previous_two_holds_retained']==['011-F04','012-F03']and scope['other_holds_retained']==['016-F01','019-F02']
  assert scope['old_holds_reopened']==(['011-F04']if n==22 else['012-F03']if n==23 else[])
  assert not scope['scope_definitions_changed']and not scope['independent_human_reviewer_claimed']
  assert scope['production_tasks_completed']==scope['production_changes']==scope['checklist_deletions']==0
  assert scope['added_ids']==(['013-F03']if n==21 else[])
  assert sum(e['credit']for e in rev['entries'])==rev['independent_references_added']==scope['added_credit']==(1 if n==21 else 0)
  oldscope=get(parent)
  for s,original_s,previous_s in zip(scope['scopes'],definitions['scopes'],oldscope['scopes']):
   assert s['scope_id']==original_s['scope_id']and s['scope_definition']==original_s['scope_definition']
   assert s['target']==1000 and not s['construction_allowed']and s['remaining']==1000-s['accepted_references']
   assert len(s['accepted_ids'])==len(set(s['accepted_ids']))==s['accepted_references']
   assert s['accepted_ids']==previous_s['accepted_ids']+(['013-F03']if n==21 and s['scope_id']=='DUN03-SINGLE-WATCHPOST'else[])
  assert [s['accepted_references']for s in scope['scopes']]==[6,8,1]
  for p in folder.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
  reports.append(dict(batch=n,status='PASS_LOCAL_REREVIEW_SOURCE_AND_SCOPE_BOUNDARIES',
   prior_source_template_rereads=count,new_source_templates=0,new_section_images=count,
   independent_references_added=scope['added_credit'],scope_counts=[6,8,1],scope_remaining=[994,992,999],
   construction_allowed=False,old_holds_retained=True,java_run=False,game_run=False,network_requests=0,
   source_bytes_original_states_exact_json_values_verified=True,independent_human_review_claimed=False,
   production_changes=0,checklist_deletions=0))
  parent=folder/'scoped-reference-update.json'
 assert len(identities)==11 and len(oldimages)==15 and len(newimages)==11 and credits==['013-F03']
 pair=get(folders[0]/'pair-evidence.json')
 a,b=allcells[(21,'T01')],allcells[(21,'T02')]
 for row in pair['measurements']:
  lo,hi=row['y_band_inclusive'];left={p:s for p,s in a.items()if lo<=p[1]<=hi};right={p:s for p,s in b.items()if lo<=p[1]<=hi}
  common=left.keys()&right.keys();union=left.keys()|right.keys()
  assert row['left_nonair']==len(left)and row['right_nonair']==len(right)
  assert row['common_positions']==len(common)and row['union_positions']==len(union)
  assert row['occupancy_jaccard']==len(common)/len(union)
  assert row['same_original_name_and_properties']==sum(left[p]==right[p]for p in common)
 assert not pair['automatic_credit']
 reports[-1].update(status='PASS_THREE_REREVIEW_BATCHES_ONE_PREVIOUSLY_HELD_REFERENCE',
  joint_previous_source_templates=11,joint_new_source_templates=0,joint_actual_new_section_images=11,
  joint_unique_previous_whole_images=15,joint_independent_references_added=1,accepted_ids=credits,
  preserved_prior_packages=len(preserved),preserved_other_scope_registries=True,
  original_scope_definitions_unchanged=True,no_native_collision_terrain_or_gameplay_acceptance=True,
  sound_brightness_window_save_changes=0)
 for folder,report in zip(folders,reports):
  dump(folder/'verification.json',report)
  files=sorted(p for p in folder.rglob('*')if p.is_file()and p.name!='RECEIPT.json')
  dump(folder/'RECEIPT.json',dict(status=report['status'],files=[dict(path=str(p.relative_to(folder)),bytes=p.stat().st_size,sha256=sha(p))for p in files]))
  for e in get(folder/'RECEIPT.json')['files']:
   p=folder/e['path'];assert p.stat().st_size==e['bytes']and sha(p)==e['sha256']
 print(json.dumps(reports[-1],ensure_ascii=False))
if __name__=='__main__':main()
