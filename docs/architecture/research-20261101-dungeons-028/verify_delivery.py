#!/usr/bin/env python3
"""Verify sources, exact aligned join, scope update and receipts without Java."""
import ast
from collections import Counter,defaultdict
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
def dump(name,d):(OUT/name).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
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
 preserved=[original]+[BASE/f'research-20261101-dungeons-{n:03d}'for n in range(16,28)]
 for folder in preserved:
  for e in get(folder/'RECEIPT.json')['files']:
   p=folder/e['path'];assert p.stat().st_size==e['bytes']and sha(p.read_bytes())==e['sha256'],p
 src=get(OUT/'sources.json');rawstates={};cells={};rawnbt={}
 assert len(src['candidates'])==1 and len(src['component_templates'])==2
 for a in src['source_archives']:assert sha(Path(a['path']).read_bytes())==a['sha256']
 for c in src['candidates']+src['component_templates']:
  with ZipFile(c['source_archive'])as z:raw=z.read(c['member'])
  assert sha(raw)==c['nbt_sha256'];d=read(raw);pal=d.get('palette')or d['palettes'][0]
  assert c['size']==d['size'];rawnbt[c['id']]=d
  states={tuple(b['pos']):pal[b['state']]for b in d['blocks']}
  assert len(states)==len(d['blocks'])
  assert all(0<=p[i]<d['size'][i]for p in states for i in range(3))
  rawstates[c['id']]=states;cs={p:s for p,s in states.items()if s['Name']not in AIR};cells[c['id']]=cs
  assert len(cs)==c['nonair']and dict(Counter(s['Name']for s in cs.values()))==c['materials']
  assert [dict(position=b['pos'],state=pal[b['state']],data=b.get('nbt',{}))for b in d['blocks']if pal[b['state']]['Name']=='minecraft:jigsaw']==c['sockets']
 assembly=get(OUT/'assembly-evidence.json');stored=get(OUT/'assembly-original-states.json')
 assert assembly['source_components']==[dict(component_id='C01',translation=[0,0,0],rotation_y_quarter_turns=0),dict(component_id='C02',translation=[0,48,0],rotation_y_quarter_turns=0)]
 assert assembly['stored_size']==[18,58,18]and not assembly['native_jigsaw_generation_verified']and not assembly['nbt_exported']and assembly['building_credit']==0
 a,b=[c['sockets'][0]for c in src['component_templates']]
 assert a['position']==[0,47,0]and b['position']==[0,0,0]
 assert a['state']['Properties']['orientation']=='up_south'and b['state']['Properties']['orientation']=='down_south'
 assert a['data']['joint']==b['data']['joint']=='aligned'
 assert a['data']['target']==b['data']['name']and b['data']['target']==a['data']['name']
 assert a['data']['pool']=='totw_modded:aether/aether_skyroot_2'and b['data']['pool']=='totw_modded:aether/aether_skyroot_1'
 assert a['data']['final_state']==b['data']['final_state']=='minecraft:air'
 combined={}
 for part in assembly['source_components']:
  for p,s in rawstates[part['component_id']].items():
   pos=tuple(p[i]+part['translation'][i]for i in range(3))
   if s['Name']=='minecraft:jigsaw':s=dict(Name='minecraft:air')
   if s['Name']not in AIR:assert pos not in combined;combined[pos]=s
 assert [dict(position=list(p),state=s)for p,s in sorted(combined.items())]==stored['states']
 assert len(combined)==assembly['nonair']and dict(Counter(s['Name']for s in combined.values()))==assembly['materials']
 assert assembly['occupied_bounds']==[[min(p[i]for p in combined),max(p[i]for p in combined)]for i in range(3)]==[[1,17],[0,57],[1,17]]
 with ZipFile(src['component_templates'][0]['source_archive'])as z:
  for e in assembly['definitions']:
   raw=z.read(e['member']);assert sha(raw)==e['sha256']and json.loads(raw)==e['data']
  for e in assembly['local_author_metadata']:
   raw=z.read(e['member']);assert sha(raw)==e['sha256']and raw.decode()==e['text']
 assert assembly['definitions'][0]['data']['start_pool']=='totw_modded:aether/aether_skyroot_1'
 for e,c in zip(assembly['definitions'][1:],src['component_templates']):
  p=e['data'];assert len(p['elements'])==1 and p['fallback']=='minecraft:empty'
  element=p['elements'][0]['element'];assert element['projection']=='rigid'and element['processors']=='minecraft:empty'
  ident=c['member'].split('/structures/')[0].split('/')[-1]+':'+c['member'].split('/structures/')[1][:-4]
  assert element['location']==ident
 dedup=get(OUT/'dedup-evidence.json');ad=get(OUT/'assembly-dedup-evidence.json')
 assert dedup['historical_unique_local_archive_member_pairs']==ad['historical_unique_archive_member_pairs']==214
 assert not dedup['within_batch_exact_duplicate_pairs']and not dedup['entries'][0]['historical_exact_matches']and not ad['historical_geometry_matches']
 assert ad['occupancy_sha256']==geometry_hash({p:1 for p in combined},[18,58,18])
 assert ad['role_sha256']==geometry_hash({p:role(s['Name'])for p,s in combined.items()},[18,58,18])
 f=src['candidates'][0];audit=get(OUT/'raw-source-audit.json')['entries'][0]
 assert audit['occupied_bounds']==[[min(p[i]for p in cells['F01']),max(p[i]for p in cells['F01'])]for i in range(3)]
 assert dedup['entries'][0]['occupancy_sha256']==geometry_hash({p:1 for p in cells['F01']},f['size'])
 assert dedup['entries'][0]['role_sha256']==geometry_hash({p:role(s['Name'])for p,s in cells['F01'].items()},f['size'])
 author=get(OUT/'author-placement-evidence.json')
 with ZipFile(f['source_archive'])as z:
  for e in author['documents']:
   raw=z.read(e['member']);assert sha(raw)==e['sha256']and json.loads(raw)==e['data']
  for e in author['actor_template_metadata']:
   raw=z.read(e['member']);assert sha(raw)==e['nbt_sha256'];d=read(raw)
   assert d['size']==e['size']and [dict(pos=x.get('pos'),id=x.get('nbt',{}).get('id'))for x in d.get('entities',[])]==e['entities']
   assert not e['actual_image_reading']and not e['placed_or_assembled']and e['building_credit']==0
  for e in audit['archive_json_identity_mentions']:
   raw=z.read(e['member']);assert sha(raw)==e['sha256']and json.loads(raw)==e['data']and exact(e['data'],'trek:overworld/medium/offshore_platform_pillager')
  assert len(f['sockets'])==7 and len(audit['outgoing_pools'])==2
  for e in audit['outgoing_pools']:
   raw=z.read(e['member']);assert sha(raw)==e['sha256']and json.loads(raw)==e['data']
   assert e['pool']in ['trek:mobs/pillagers/pillager','trek:mobs/pillagers/vindicator']and not e['assembled']and e['building_credit']==0
   assert e['data']['elements'][0]['element']['location']==e['pool']
 structure=author['documents'][0]['data'];assert structure['biomes']=='#trek:ocean/is_not_frozen_ocean'and structure['start_height']==dict(absolute=-6)
 assert structure['start_pool']=='trek:overworld/medium/offshore_platform_pillager'and structure['terrain_adaptation']=='none'
 assert {e['type']for e in structure['spawn_overrides']['monster']['spawns']}=={'minecraft:pillager','minecraft:vindicator'}
 assert any(e['position']==[13,40,8]and e['data']['pool']=='trek:mobs/pillagers/pillager'for e in f['sockets'])
 de=get(OUT/'detail-evidence.json');planes=get(OUT/'selected-plane-states.json')
 assert de['entries'][0]['cuts'][0]['coordinate']==9 and de['entries'][0]['cuts'][1]['coordinate']==41
 ladders=defaultdict(list)
 for p,s in combined.items():
  if s['Name']=='minecraft:ladder':ladders[(p[0],p[2])].append(p[1])
 assert de['assembly_entries'][0]['ladder_runs']==[dict(x=x,z=z,ys=sorted(ys))for(x,z),ys in sorted(ladders.items())]
 for row in planes['entries']:
  states=rawstates['F01']if row['id']=='F01'else combined
  for e in row['planes']:
   observed={tuple(v['position']):v['state']for v in e['original_or_rigid_translated_states']}
   assert len(observed)==len(e['original_or_rigid_translated_states'])
   assert observed=={p:s for p,s in states.items()if p[1]==e['y']}
 review=get(OUT/'manual-review.json');assert len(review['entries'])==len(review['assembly_entries'])==1
 assert review['entries'][0]['source']==f and review['entries'][0]['credit']==review['independent_references_added']==1
 assert review['assembly_entries'][0]['credit']==0 and review['actual_new_images_viewed']==4
 assert review['whole_design_candidates_reviewed']==2 and review['architectural_source_templates_read']==3 and review['actor_templates_metadata_only']==2
 assert len(review['semantic_comparisons'])==8 and not review['independent_human_review_claimed']
 images=set()
 for row in review['entries']+review['assembly_entries']:
  assert set(row['observations'])=={'layout','proportion','facade','roof','materials','circulation','terrain'}and not row['native_acceptance']
  for e in row['actual_images_viewed']:evidence(e,True);images.add(e['path'])
 for e in review['prior_comparison_evidence']:evidence(e)
 assert len(images)==4
 scope=get(OUT/'scoped-reference-update.json');evidence(scope['prior_update']);evidence(scope['original_scope_definitions']);evidence(scope['previous_hold_evidence'])
 prior=get(Path(scope['prior_update']['path']))
 assert scope['added_ids']==['028-F01']and scope['added_credit']==1 and not scope['scope_definitions_changed']
 assert scope['previous_two_holds_retained']==['011-F04','012-F03']and scope['other_holds_retained']==['016-F01','019-F02']
 assert scope['recent_holds_retained']==['025-F01','025-F02','027-F01']
 for s,old,original_s in zip(scope['scopes'],prior['scopes'],definitions['scopes']):
  assert s['scope_id']==old['scope_id']==original_s['scope_id']and s['scope_definition']==original_s['scope_definition']
  assert s['accepted_ids']==old['accepted_ids']+(['028-F01']if s['scope_id']=='DUN03-SINGLE-WATCHPOST'else[])
  assert len(s['accepted_ids'])==len(set(s['accepted_ids']))==s['accepted_references']
  assert s['target']==1000 and s['remaining']==1000-s['accepted_references']and not s['construction_allowed']
 assert [s['accepted_references']for s in scope['scopes']]==[6,9,1]
 assert scope['production_tasks_completed']==scope['production_changes']==scope['checklist_deletions']==0 and not scope['independent_human_reviewer_claimed']
 boundary=get(OUT/'discovery-boundary.json')
 for e in boundary['indices_checked']:evidence(e)
 assert boundary['local_only']and boundary['network_requests']==0 and not boundary['java_run']and not boundary['game_run']
 assert boundary['production_changes']==boundary['checklist_deletions']==boundary['sound_brightness_window_save_changes']==0
 for p in OUT.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
 report=dict(status='PASS_TWO_WHOLE_DESIGN_CANDIDATES_ONE_SCOPED_REFERENCE',batch=28,
  whole_design_candidates_actually_reviewed=2,architecture_source_templates_read=3,actor_templates_metadata_only=2,
  actual_new_images_viewed=4,new_valid_references=1,accepted_ids=['028-F01'],scoped_counts=[6,9,1],remaining=[994,991,999],
  source_bytes_original_states_author_pool_values_and_aligned_transform_verified=True,authored_58_block_tower_excluded=True,
  component_building_credit=0,actor_building_credit=0,construction_allowed=False,
  prior_receipt_packages_unchanged=len(preserved),other_scope_registries_unchanged=True,all_old_holds_retained=True,
  native_collision_terrain_jigsaw_or_gameplay_acceptance=False,independent_human_review_claimed=False,
  java_run=False,game_run=False,network_requests=0,production_changes=0,checklist_deletions=0,sound_brightness_window_save_changes=0)
 dump('verification.json',report)
 files=sorted(p for p in OUT.rglob('*')if p.is_file()and p.name!='RECEIPT.json')
 dump('RECEIPT.json',dict(status=report['status'],files=[dict(path=str(p.relative_to(OUT)),bytes=p.stat().st_size,sha256=sha(p.read_bytes()))for p in files]))
 for e in get(OUT/'RECEIPT.json')['files']:
  p=OUT/e['path'];assert p.stat().st_size==e['bytes']and sha(p.read_bytes())==e['sha256']
 print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()
