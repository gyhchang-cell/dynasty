#!/usr/bin/env python3
"""Offline verification of five studies, family exclusions and one bounded scope increment."""
import ast
from collections import Counter
import hashlib
import json
import sys
from pathlib import Path
from zipfile import ZipFile
from PIL import Image
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
BASE=OUT.parent
sys.path.insert(0,str(ROOT/'tools/architecture'))
from nbt_read import read
from reference_components import geometry_hash,role
from whole_building_candidates import AIR
from inspect_families import extract,pair
from record_review import PRIOR,SCOPE
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(b):return hashlib.sha256(b).hexdigest()
def get(n):return json.loads((OUT/n).read_text())
def dump(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def evidence(e,image=False):
 p=Path(e['path']);assert sha(p)==e['sha256'],p
 if image:
  with Image.open(p) as im:im.verify()
def canonical(v):return sorted(json.dumps(e,sort_keys=True) for e in v)
def main():
 sources=get('sources.json');review=get('manual-review.json');dedup=get('dedup-evidence.json');interface=get('interface-audit.json')
 details=get('detail-evidence.json');states=get('vertical-original-states.json');scope=get('scoped-reference-update.json')
 assert all(len(x)==5 for x in [sources['candidates'],review['entries'],dedup['entries'],interface['entries'],details['entries'],states['entries']])
 assert dedup['historical_unique_local_archive_member_pairs']==188 and not dedup['within_batch_exact_duplicate_pairs']
 assert sum(e['credit'] for e in review['entries'])==1
 assert [e['id'] for e in review['entries'] if e['credit']]==['F02']
 assert [e['id'] for e in review['entries'] if e['status']=='FAMILY_VARIANT_NO_ADDITIONAL_CREDIT']==['F03','F04']
 assert [e['id'] for e in review['entries'] if e['status']=='FAMILY_INDEPENDENCE_HOLD']==['F01','F05']
 assert review['new_templates_studied']==5 and review['new_images_actually_viewed']==20
 assert scope['scope_id']==SCOPE and scope['accepted_references']==7 and scope['previous_accepted']==6
 assert scope['remaining']==993 and scope['target']==1000 and not scope['construction_allowed']
 assert scope['old_credit_transferred']==0 and scope['production_tasks_completed']==scope['checklist_deletions']==0
 evidence(scope['prior_register'])
 prior=json.loads(PRIOR.read_text());old=next(s for s in prior['scopes'] if s['scope_id']==SCOPE)
 assert old['accepted_ids']==scope['previous_accepted_ids'] and old['accepted_references']==6
 assert scope['added'][0]['id']=='016-F02' and scope['added'][0]['credit']==1
 assert '016-F02' not in scope['previous_accepted_ids'] and len(set(scope['previous_accepted_ids']+['016-F02']))==7
 for p in prior['preserved_registries']:evidence(p)
 evidence(scope['added'][0]['source_review']);evidence(scope['added'][0]['family_comparison'])
 archive=sources['source_archives'][0]
 assert len(sources['source_archives'])==1 and sha(Path(archive['path']))==archive['sha256']
 raw_summaries=[];socket_counts={};new_image_paths=set();local_pool_records=0
 with ZipFile(archive['path']) as z:
  for c,r,d,a,de,st in zip(sources['candidates'],review['entries'],dedup['entries'],interface['entries'],details['entries'],states['entries']):
   i=c['id'];assert all(e['id']==i for e in [r,d,a,de,st])
   assert c['member'].startswith('data/minecraft/structures/pillager_outpost/pillager_watchtower')
   raw=z.read(c['member']);nbt=read(raw);p=nbt['palette']
   assert digest(raw)==c['nbt_sha256']==d['nbt_sha256']==st['nbt_sha256']
   assert c['size']==nbt['size']
   assert r['source']==c and r['native_acceptance'] is False
   assert not d['historical_exact_matches']
   assert set(r['observations'])=={'layout','proportion','facade','roof','materials','circulation','terrain'}
   cells={tuple(b['pos']):p[b['state']]['Name'] for b in nbt['blocks'] if p[b['state']]['Name'] not in AIR}
   assert dict(Counter(cells.values()))==c['materials'] and len(cells)==c['nonair']
   bounds=[[min(v[a] for v in cells),max(v[a] for v in cells)] for a in range(3)]
   assert de['occupied_bounds']==bounds
   original=[dict(position=b['pos'],state=p[b['state']]) for b in nbt['blocks'] if p[b['state']]['Name'].endswith(('_stairs','_door')) or p[b['state']]['Name']=='minecraft:ladder']
   assert st['stairs_doors_ladders']==original
   assert geometry_hash({v:1 for v in cells},nbt['size'])==d['occupancy_sha256']
   assert geometry_hash({v:role(n) for v,n in cells.items()},nbt['size'])==d['role_sha256']
   sockets=[dict(position=b['pos'],state=p[b['state']],data=b.get('nbt',{})) for b in nbt['blocks'] if p[b['state']]['Name']=='minecraft:jigsaw']
   assert sockets==c['sockets']
   pools=Counter(s['data']['pool'] for s in sockets);socket_counts[i]=dict(pools)
   assert pools['minecraft:pillager_outpost/feature_plates']==4
   assert set(pools)=={e['pool'] for e in a['outgoing_pools']}
   for e in a['outgoing_pools']:
    assert e['status']=='FOUND_LOCAL'
    assert e['socket_positions']==[s['position'] for s in sockets if s['data']['pool']==e['pool']]
    body=z.read(e['member']);assert digest(body)==e['sha256'] and json.loads(body)==e['data'];local_pool_records+=1
    for comp in e['component_identities_only']:
     assert comp['exists_in_archive'] and digest(z.read(comp['member']))==comp['sha256']
     assert not comp['studied_or_credited_as_complete_building']
   for e in c['pool_references']:assert json.loads(z.read(e['member']))==e['data']
   assert len(r['actual_images_viewed'])==4
   for e in r['actual_images_viewed']:evidence(e,image=True);new_image_paths.add(e['path'])
   raw_summaries.append(dict(id=i,size=nbt['size'],nbt_sha256=digest(raw),bounds=bounds,opening_vertical_states=len(original),sockets=len(sockets)))
  comp=get('secondary-component-boundary.json')['entries'];assert len(comp)==6
  assert Counter(e['kind'] for e in comp)=={'PATH_PLATE_WITH_FURTHER_FEATURE_SOCKETS':3,'SINGLE_ACTOR':3}
  for e in comp:
   raw=z.read(e['member']);nbt=read(raw);p=nbt['palette']
   assert digest(raw)==e['sha256'] and nbt['size']==e['size']
   assert dict(Counter(p[b['state']]['Name'] for b in nbt['blocks']))==e['materials']
   assert [v['nbt'].get('id') for v in nbt['entities']]==e['entity_ids']
   assert [dict(position=b['pos'],state=p[b['state']],data=b.get('nbt',{})) for b in nbt['blocks'] if p[b['state']]['Name']=='minecraft:jigsaw']==e['sockets']
   assert not e['images_viewed'] and not e['assembled'] and e['building_credit']==0
   if e['kind']=='PATH_PLATE_WITH_FURTHER_FEATURE_SOCKETS':
    assert set(e['materials'])=={'minecraft:air','minecraft:dirt_path','minecraft:jigsaw'} and not e['entity_ids']
   else:assert e['size']==[1,3,1] and len(e['entity_ids'])==1
 assert len(new_image_paths)==20
 assert [sum(c.values()) for c in socket_counts.values()]==[15,13,13,13,13]
 family=get('family-structural-evidence.json');cache={c['id']:extract(c) for c in sources['candidates']}
 assert family['within_batch']==[pair(a,b,cache[a],cache[b]) for a,b in [('F02','F03'),('F02','F04'),('F03','F04')]]
 assert all(e['left_structural_positions']==e['right_structural_positions']==870 and e['ladder_original_states_equal'] for e in family['within_batch'])
 oldrow=next(c for c in json.loads((BASE/'research-20261101-dungeons-013/sources.json').read_text())['candidates'] if c['id']=='F03')
 assert family['cross_source_reuse']==pair('016-F05','013-F03',cache['F05'],extract(oldrow))
 assert not family['semantic_decision_automatic'] and not family['formal_credit_added']
 hold=get('hold-review.json');assert [e['id'] for e in hold['entries']]==['011-F04','012-F03']
 assert all(e['decision']=='HOLD_FAMILY' and e['credit']==e['new_sources']==0 for e in hold['entries'])
 assert len(hold['images_actually_viewed'])==len(hold['source_identities'])==6
 for e in hold['images_actually_viewed']:evidence(e,image=True)
 for e in hold['source_identities']:
  evidence(e['original_index']);assert sha(Path(e['source_archive']))==e['source_archive_sha256']
  with ZipFile(e['source_archive']) as z:
   raw=z.read(e['member']);assert digest(raw)==e['nbt_sha256'];assert read(raw)['size']==e['size']
 assert len(review['historical_comparison_views'])==14
 for e in review['historical_comparison_views']:evidence(e,image=True)
 # Keep original acceptance package as a verifiable immutable historical snapshot.
 previous_folder=PRIOR.parent
 for e in json.loads((previous_folder/'RECEIPT.json').read_text())['files']:
  p=previous_folder/e['path'];assert p.stat().st_size==e['bytes'] and sha(p)==e['sha256']
 for p in OUT.rglob('*.py'):ast.parse(p.read_text(),filename=str(p))
 report=dict(status='PASS_ONE_WATCHPOST_REFERENCE_TWO_VARIANTS_TWO_NEW_HOLDS_TWO_PRIOR_HOLDS',new_templates_studied=5,
  independent_scoped_references_added=1,material_or_vegetation_variants_not_additional=2,new_family_holds=2,prior_holds_retained=2,
  source_images_actually_viewed=20,old_identity_supplementary_images_actually_viewed=6,historical_images_reviewed_again=14,
  historical_archive_member_pairs_screened=188,screening_identities_are_not_reference_count=True,
  selected_category_similarity_not_full_structure_equality=True,scope_id=SCOPE,previous_accepted=6,accepted_references=7,target=1000,remaining=993,
  construction_allowed=False,unchanged_scope_counts=scope['unchanged_scope_counts'],raw_sources_verified=raw_summaries,
  secondary_nonbuilding_components_verified=6,local_pool_records_verified=local_pool_records,socket_counts=socket_counts,
  previous_acceptance_snapshot_unchanged=True,network_requests=0,java_run=False,game_run=False,
  production_changes=0,production_tasks_completed=0,checklist_deletions=0,sound_brightness_save_changes=0,
  independent_human_reviewer_claimed=False)
 dump('verification.json',report)
 files=sorted(p for p in OUT.rglob('*') if p.is_file() and p!=OUT/'RECEIPT.json')
 dump('RECEIPT.json',dict(status=report['status'],files=[dict(path=str(p.relative_to(OUT)),bytes=p.stat().st_size,sha256=sha(p)) for p in files]))
 for e in get('RECEIPT.json')['files']:
  p=OUT/e['path'];assert p.stat().st_size==e['bytes'] and sha(p)==e['sha256']
 print(json.dumps({k:v for k,v in report.items() if k not in ['raw_sources_verified','socket_counts']},ensure_ascii=False))
if __name__=='__main__':main()
