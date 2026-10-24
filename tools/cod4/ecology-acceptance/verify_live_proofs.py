"""Review actual source event links against the original denominators; never manufactures proof."""
from pathlib import Path
import csv,hashlib,json,datetime
R=Path(__file__).resolve().parents[3];D=R/'docs/cod4/audit-20261022/ecology-acceptance';L=D/'live-run1'
s=json.loads((L/'summary.json').read_text());source=json.loads((D/'source-audit.json').read_text())
original_species={x['id'] for x in source['species']}
original_materials={x['id'] for x in csv.DictReader((D/'material-natural-results.tsv').open(),delimiter='\t')}
lines=(L/'events.jsonl').read_text().splitlines();events={}
for n,line in enumerate(lines,1):
 try:events[n]=json.loads(line)
 except json.JSONDecodeError:pass
rows=[]
for m in s['material_proofs']:
 p=next((x for x in m['proofs'] if x['pickup_exact_uuid_verified']),None)
 if p is None:rows.append({'id':m['id'],'status':'PENDING_NO_EXACT_NATIVE_PICKUP'});continue
 birth=events[p['natural_spawn_event_line']];death=events[p['death_event_line']]
 drop=next(x for x in death['drops'] if x['entity_uuid']==p['actual_drop_entity_uuid'])
 pickups=[events[n] for n in p['pickup_event_lines'] if events[n].get('pickup_item_entity_uuid')==drop['entity_uuid']]
 checks={'original_material':m['id'] in original_materials,'original_species':birth['species'].split(':')[-1] in original_species,'native_natural_spawner_stack':any('NaturalSpawner.spawnCategoryForPosition' in x for x in birth.get('native_spawn_stack',[])),'fresh_native_birth':not birth.get('loaded_from_disk',True),'same_mob_uuid':birth['uuid']==death['uuid']==p['natural_mob_uuid'],'actual_player_damage':death.get('actual_player_damage') is True,'same_material':drop['item']=='dynasty:'+m['id'],'exact_entity_owner_item_after_death':bool(pickups) and all(x['player']==death['owner'] and x['item']==drop['item'] and x['game_tick']>=death['game_tick'] for x in pickups)}
 if m['id'] in {'qimen_cable','qimen_gear'}:
  xyz=[float(x) for x in birth['pos'].strip('()').split(',')]
  checks['natural_birth_inside_actual_clockwork_city']=1604<=xyz[0]<=1803 and 51<=xyz[1]<=130 and -17980<=xyz[2]<=-17781
 rows.append({'id':m['id'],'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks,'source_event_lines':[p['natural_spawn_event_line'],p['death_event_line'],*p['pickup_event_lines']],'natural_mob_uuid':birth['uuid'],'item_entity_uuid':drop['entity_uuid'],'death_game_tick':death['game_tick'],'pickup_game_ticks':[x['game_tick'] for x in pickups],'pickup_delay_world_ticks':[x['game_tick']-death['game_tick'] for x in pickups]})
assert original_materials=={m['id'] for m in s['material_proofs']} and len(original_materials)==10 and len(original_species)==30
r={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'SPECIALIZED_10_MATERIAL_PROOFS_PASS' if all(x['status']=='PASS' for x in rows) else 'PARTIAL_NATIVE_EVIDENCE','species_denominator':30,'materials_denominator':10,'pass':sum(x['status']=='PASS' for x in rows),'fail':sum(x['status']=='FAIL' for x in rows),'pending':sum(x['status'].startswith('PENDING') for x in rows),'baseline':'normal-run2 historical 19/30 positions and 2 natural structures unchanged','full_survival_or_all_original_scenes_pass':False,'rows':rows,'events_sha256':hashlib.sha256((L/'events.jsonl').read_bytes()).hexdigest()}
(L/'proof-review-receipt.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print({k:r[k] for k in ['status','pass','fail','pending']})
