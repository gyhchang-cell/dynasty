#!/usr/bin/env python3
"""Verify local metadata coverage and candidate evidence, never auto-admit designs."""
import ast
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
from zipfile import ZipFile
from PIL import Image
OUT=Path(__file__).resolve().parent;BASE=OUT.parent;ROOT=OUT.parents[2]
sys.path.insert(0,str(ROOT/'tools/architecture'))
from nbt_read import read
from reference_components import geometry_hash,role
from whole_building_candidates import AIR
def sha(b):return hashlib.sha256(b).hexdigest()
def get(p):return json.loads(p.read_text())
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def evidence(e,image=False):
 p=Path(e['path']);assert sha(p.read_bytes())==e['sha256'],p
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
 preserved=[original]+[BASE/f'research-20261101-dungeons-{n:03d}'for n in range(16,24)]
 for folder in preserved:
  for e in get(folder/'RECEIPT.json')['files']:
   p=folder/e['path'];assert p.stat().st_size==e['bytes']and sha(p.read_bytes())==e['sha256'],p
 screen=get(BASE/'research-20261101-dungeons-024/fixed-source-screen.json')
 metadata=get(OUT/'all-structure-metadata.json');evidence(metadata['fixed_archive_inventory'])
 assert screen['archives_enumerated']==metadata['archive_count']==len(screen['archives'])==292
 assert screen['keyword_candidates']==len(screen['entries'])==1270
 assert screen['newly_parsed']==1189 and screen['historical_unique_archive_member_pairs']==204
 assert not screen['errors']and not metadata['errors']
 assert metadata['structure_members_enumerated']==metadata['all_structure_members_parsed']==len(metadata['entries'])==7139
 assert metadata['newly_covered_keyword_negative_members']==sum(not r['keyword_match']for r in metadata['entries'])==5869
 for e in screen['historical_indices']:evidence(e)
 allrows={(r['source_archive'],r['member']):r for r in metadata['entries']}
 assert len(allrows)==7139
 for a in screen['archives']:
  jar=Path(a['path']);assert sha(jar.read_bytes())==a['sha256']
  with ZipFile(jar)as z:
   members=[n for n in z.namelist()if n.endswith('.nbt')and '/structures/'in n]
   assert len(members)==a['structure_nbt_members']
   for member in members:
    r=allrows[(str(jar),member)];assert sha(z.read(member))==r['nbt_sha256']
    assert not r['actual_visual_reading']and r['building_credit']==0
 assert len([r for r in allrows.values()if r.get('size_prefilter_scopes')])==489
 assert len([r for r in allrows.values()if not r['keyword_match']and r.get('size_prefilter_scopes')])==374
 for r in screen['entries']:
  if 'nbt_sha256'in r:assert r['nbt_sha256']==allrows[(r['source_archive'],r['member'])]['nbt_sha256']
 folders=[BASE/f'research-20261101-dungeons-{n:03d}'for n in [24,25,26,27]]
 parent=BASE/'research-20261101-dungeons-023/scoped-reference-update.json'
 images=set();rawcells={};selected=set();reports=[]
 for n,folder in zip([24,25,26,27],folders):
  scope=get(folder/'scoped-reference-update.json');rev=get(folder/'manual-review.json')
  evidence(scope['prior_update']);assert scope['prior_update']['path']==str(parent)
  evidence(scope['original_scope_definitions']);evidence(scope['previous_hold_evidence'])
  assert scope['scopes']==get(parent)['scopes']and [s['accepted_references']for s in scope['scopes']]==[6,8,1]
  assert scope['added_ids']==[]and scope['added_credit']==0 and not scope['scope_definitions_changed']
  assert scope['previous_two_holds_retained']==['011-F04','012-F03']and scope['other_holds_retained']==['016-F01','019-F02']
  assert not scope['independent_human_reviewer_claimed']and scope['production_changes']==scope['production_tasks_completed']==scope['checklist_deletions']==0
  for s,old in zip(scope['scopes'],definitions['scopes']):
   assert s['scope_id']==old['scope_id']and s['scope_definition']==old['scope_definition']
   assert len(s['accepted_ids'])==len(set(s['accepted_ids']))==s['accepted_references']
   assert s['target']==1000 and s['remaining']==1000-s['accepted_references']and not s['construction_allowed']
  count={24:3,25:3,26:0,27:4}[n]
  assert len(rev['entries'])==rev['previously_unregistered_templates_visually_reviewed']==count
  assert rev['actual_images_viewed']==count*2 and rev['independent_references_added']==0
  if n!=26:
   src=get(folder/'sources.json');audit=get(folder/'raw-source-audit.json');detail=get(folder/'detail-evidence.json');dd=get(folder/'dedup-evidence.json')
   boundary=get(folder/'discovery-boundary.json')
   assert boundary['local_only']and boundary['network_requests']==0 and not boundary['java_run']and not boundary['game_run']
   for e in boundary['indices_checked']:evidence(e)
   assert dd['historical_unique_local_archive_member_pairs']==(207 if n in [24,25] else 210)
   assert dd['within_batch_exact_duplicate_pairs']==([['F01','F02']]if n==27 else[])
   assert all(len(x)==count for x in [src['candidates'],audit['entries'],detail['entries'],dd['entries']])
   for c,r,a,de,ded in zip(src['candidates'],rev['entries'],audit['entries'],detail['entries'],dd['entries']):
    assert c['id']==r['id']==a['id']==de['id']==ded['id']and c==r['source']
    assert r['credit']==0 and not r['native_acceptance']and not r['independent_human_review']
    assert set(r['observations'])=={'layout','proportion','facade','roof','materials','circulation','terrain'}
    assert not ded['historical_exact_matches']
    with ZipFile(c['source_archive'])as z:
     raw=z.read(c['member']);assert sha(raw)==c['nbt_sha256']==a['nbt_sha256']==ded['nbt_sha256']
     d=read(raw);pal=d.get('palette')or d['palettes'][0]
     assert d['size']==c['size']==a['size']==allrows[(c['source_archive'],c['member'])]['size']
     cells={tuple(b['pos']):pal[b['state']]for b in d['blocks']if pal[b['state']]['Name']not in AIR};rawcells[(n,c['id'])]=cells
     assert len(cells)==c['nonair']and dict(Counter(s['Name']for s in cells.values()))==c['materials']==a['materials']
     bounds=[[min(p[i]for p in cells),max(p[i]for p in cells)]for i in range(3)]
     assert bounds==a['occupied_bounds']==de['occupied_bounds']==allrows[(c['source_archive'],c['member'])]['occupied_bounds']
     assert geometry_hash({p:1 for p in cells},d['size'])==ded['occupancy_sha256']
     assert geometry_hash({p:role(s['Name'])for p,s in cells.items()},d['size'])==ded['role_sha256']
     openings=[dict(position=list(p),state=s)for p,s in cells.items()if s['Name'].endswith(('_stairs','_door','_trapdoor','_fence_gate'))or s['Name']=='minecraft:ladder']
     assert openings==a['original_vertical_opening_states']
     ident=c['member'].split('/structures/')[0].split('/')[-1]+':'+c['member'].split('/structures/')[1][:-4]
     assert {e['member']for e in c['pool_references']}=={e['member']for e in a['archive_json_identity_mentions']if '/worldgen/template_pool/'in e['member']}
     for e in a['archive_json_identity_mentions']:
      raw=z.read(e['member']);assert sha(raw)==e['sha256']and json.loads(raw)==e['data']and exact(e['data'],ident)
     for e in a['outgoing_pools']:assert not e['assembled']and e['building_credit']==0
    for e in r['actual_images_viewed']:evidence(e,True);images.add(e['path'])
    selected.add((c['source_archive'],c['member']))
   for e in get(folder/'local-mod-metadata.json')['entries']:
    with ZipFile(e['source_archive'])as z:
     for doc in e['documents']:
      raw=z.read(doc['member']);assert sha(raw)==doc['sha256']and raw.decode()==doc['text']
   if n==25:assert src['source_archives'][0]['publisher_url']is None
   if n==27:
    assert src['source_archives'][0]['publisher_url']=='https://github.com/k1sak1/goetyawaken/issues'
  for p in folder.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
  reports.append(dict(batch=n,status='PASS_LOCAL_SCREEN_AND_SCOPE_BOUNDARIES',new_candidates_actually_viewed=count,
   actual_images_viewed=count*2,new_valid_references=0,scope_counts=[6,8,1],scope_remaining=[994,992,999],
   construction_allowed=False,network_requests=0,java_run=False,game_run=False,production_changes=0,checklist_deletions=0))
  parent=folder/'scoped-reference-update.json'
 assert len(images)==20 and len(selected)==10
 # Verify exact pair measurements without treating them as semantic approval.
 for n in [25,27]:
  data=get(BASE/f'research-20261101-dungeons-{n:03d}/pair-evidence.json')
  if n==25:
   pairs=[dict(pair=['F02','F03'],**row)for row in data['measurements']]
  else:pairs=data['pairs']
  for row in pairs:
   left,right=row['pair'];a=rawcells[(n,left)];b=rawcells[(n,right)]
   if 'y_band_inclusive'in row:
    lo,hi=row['y_band_inclusive'];a={p:s for p,s in a.items()if lo<=p[1]<=hi};b={p:s for p,s in b.items()if lo<=p[1]<=hi}
   common=a.keys()&b.keys();union=a.keys()|b.keys()
   assert row['left_nonair']==len(a)and row['right_nonair']==len(b)
   assert row['common_positions']==len(common)and row['union_positions']==len(union)
   assert row['occupancy_jaccard']==len(common)/len(union)
   assert row['same_original_name_and_properties']==sum(a[p]==b[p]for p in common)
   if 'differences'in row:assert row['differences']==[dict(position=list(p),left=a.get(p),right=b.get(p))for p in sorted(union)if a.get(p)!=b.get(p)]
 queue=get(OUT/'remaining-size-review-queue.json');assert len(queue['entries'])==queue['count']==479
 assert {(r['source_archive'],r['member'])for r in queue['entries']}=={key for key,r in allrows.items()if r.get('size_prefilter_scopes')}-selected
 needs=get(BASE/'research-20261101-dungeons-027/source-needs.json');assert not needs['source_exhaustion_claimed']and needs['building_credit_added']==0
 assert [s['missing']for s in needs['scopes']]==[994,992,999]
 reports[2].update(status='PASS_FIXED_SOURCE_METADATA_COVERAGE_NOT_SEMANTIC_EXHAUSTION',fixed_archives=292,structure_nbt_metadata_rows=7139,
  keyword_negative_metadata_rows=5869,size_only_hits=489,keyword_negative_size_only_hits=374,remaining_size_queue_rows=479,
  parse_errors=0,source_exhaustion_claimed=False)
 reports[-1].update(status='PASS_FOUR_BATCHES_TEN_NEW_CANDIDATES_ZERO_VALID_REFERENCES',
  joint_new_candidates_actually_viewed=10,joint_actual_images_viewed=20,joint_valid_references_added=0,
  old_acceptance_packages_preserved=len(preserved),old_other_scope_registries_unchanged=True,original_scope_definitions_unchanged=True,
  old_holds_retained=True,source_exhaustion_claimed=False,independent_human_review_claimed=False,
  no_native_collision_terrain_or_gameplay_acceptance=True,sound_brightness_window_save_changes=0)
 for folder,report in zip(folders,reports):
  dump(folder/'verification.json',report)
  files=sorted(p for p in folder.rglob('*')if p.is_file()and p.name!='RECEIPT.json')
  dump(folder/'RECEIPT.json',dict(status=report['status'],files=[dict(path=str(p.relative_to(folder)),bytes=p.stat().st_size,sha256=sha(p.read_bytes()))for p in files]))
  for e in get(folder/'RECEIPT.json')['files']:
   p=folder/e['path'];assert p.stat().st_size==e['bytes']and sha(p.read_bytes())==e['sha256']
 print(json.dumps(reports[-1],ensure_ascii=False))
 print(json.dumps(reports[2],ensure_ascii=False))
if __name__=='__main__':main()
