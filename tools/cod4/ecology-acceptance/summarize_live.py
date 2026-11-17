"""Aggregate immutable normal-run2 baseline and additive live native events. Never rewrites old evidence."""
from pathlib import Path
import json,collections,hashlib
R=Path(__file__).resolve().parents[3];D=R/'docs/cod4/audit-20261022/ecology-acceptance';L=D/'live-run1'
base=json.loads((D/'normal-run2-observations.json').read_text());events=[]
for n,line in enumerate((L/'events.jsonl').read_text().splitlines(),1):
 try:e=json.loads(line)
 except json.JSONDecodeError:continue # a currently writing tail is not evidence
 e['event_line']=n;events.append(e)
source=json.loads((D/'source-audit.json').read_text());species=[m['id'] for m in source['species']];mats=[m['id'] for m in source['materials']]
positions=collections.defaultdict(list)
for p in base['observations']:
 if p['kind']=='normal_world_position':
  for ident in p['native_placement_callback_pass']:positions[ident].append({'source':'normal-run2-observations.json','pos':p['pos'],'biome':p['biome']})
for e in events:
 if e['kind']=='positive_native_position':positions[e['species']].append({'source':'live-run1/events.jsonl','line':e['event_line'],'pos':e['pos'],'biome':e['biome'],'day_time':e['day_time']})
births={e['uuid']:e for e in events if e['kind']=='confirmed_natural_spawn' and not e.get('loaded_from_disk',True)}
kills=[e for e in events if e['kind']=='natural_entity_death_drops' and e.get('actual_player_damage') and e['uuid'] in births]
pickups=[e for e in events if e['kind']=='native_item_pickup']
material_records=[]
for ident in mats:
 proofs=[]
 for death in kills:
  for drop in death.get('drops',[]):
   if drop['item']!='dynasty:'+ident:continue
   matching=[p for p in pickups if p['item']==drop['item'] and p['player']==death['owner'] and death['game_tick']<=p['game_tick'] and (p.get('pickup_item_entity_uuid')==drop['entity_uuid'] or ('pickup_item_entity_uuid' not in p and p['game_tick']<=death['game_tick']+200))]
   proofs.append({'natural_spawn_event_line':births[death['uuid']]['event_line'],'natural_mob_uuid':death['uuid'],'species':death['species'],'spawn_biome':births[death['uuid']]['biome'],'spawn_pos':births[death['uuid']]['pos'],'death_event_line':death['event_line'],'death_game_tick':death['game_tick'],'actual_drop_entity_uuid':drop['entity_uuid'],'count':drop['count'],'pickup_event_lines':[p['event_line'] for p in matching],'pickup_game_ticks':[p['game_tick'] for p in matching],'pickup_delay_world_ticks':[p['game_tick']-death['game_tick'] for p in matching],'pickup_within_200_ticks':any(p['game_tick']<=death['game_tick']+200 for p in matching),'pickup_exact_uuid_verified':any(p.get('pickup_item_entity_uuid')==drop['entity_uuid'] for p in matching),'pickup_matching':'Exact same ItemEntity UUID, same owner and item after death, including delayed native recovery. Only old phase1/2 without pickup UUID use <=200 native tick fallback windows.'})
 material_records.append({'id':ident,'natural_death_drop_verified':bool(proofs),'observed_pickup_within_window':any(p['pickup_within_200_ticks'] for p in proofs),'observed_pickup_any_match':any(p['pickup_event_lines'] for p in proofs),'proofs':proofs})
structures={(x['structure'],x['start_chunk']):x for x in base['observations'] if x['kind']=='naturally_generated_start'}
for e in events:
 if e['kind']=='natural_structure_start':structures.setdefault((e['id'],e['chunk']),e)
state=json.loads((L/'state.json').read_text());result={'status':'STATIC_HANDOFF_NO_RESTART' if (D/'static-handoff.json').exists() else 'LIVE_ADDITIVE_ACCEPTANCE','baseline_preserved':{'positions_species':19,'natural_structures':2,'run':'normal-run2'},'native_valid_position_species':sum(bool(positions[s]) for s in species),'species_denominator':30,'remaining_position_species':[s for s in species if not positions[s]],'positions':dict(positions),'natural_structures':list(structures.values()),'actual_naturally_born_secondary_species':len({e['species'].split(':')[-1] for e in births.values()}&set(species)),'remaining_actual_natural_birth_species':sorted(set(species)-{e['species'].split(':')[-1] for e in births.values()}),'natural_provenance_entities':len(births),'natural_secondary_player_deaths':len([k for k in kills if k['species'].split(':')[-1] in species]),'all_actual_player_deaths':len(kills),'natural_material_death_drop_verified':sum(m['natural_death_drop_verified'] for m in material_records),'material_pickup_exact_uuid_verified':sum(any(p['pickup_exact_uuid_verified'] for p in m['proofs']) for m in material_records),'material_pickup_window_observed':sum(m['observed_pickup_within_window'] for m in material_records),'materials_denominator':10,'material_proofs':material_records,'material_species_death_attempts':dict(collections.Counter(k['species'] for k in kills)),'natural_night_reached':any(e['kind']=='natural_night_reached' for e in events),'latest_day_time':state['current_day_time'],'fixture':'real automated network client; provided unenchanted existing mandarin_duck_axe (early netherite sword), invulnerable flight, teleported observation/attack/loot locations, supplied food; NOT complete survival route','excluded':['spawn eggs','direct QA entity construction','artificial piece placement','setBiome','time/weather rewrites','environmental deaths as player kills','configuration existence as natural drops'],'events_sha256_at_summary':hashlib.sha256((L/'events.jsonl').read_bytes()).hexdigest()}
(L/'summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
(L/'species-results.tsv').write_text('id\tvalid_position\tevidence_examples\n'+''.join(f"{s}\t{'PASS' if positions[s] else 'PENDING'}\t{json.dumps(positions[s][:3],ensure_ascii=False)}\n" for s in species))
(L/'material-results.tsv').write_text('id\tnatural_player_kill_drop\tpickup_exact_item_entity_uuid\tpickup_within_200_native_ticks\tproof_count\n'+''.join(f"{m['id']}\t{m['natural_death_drop_verified']}\t{any(p['pickup_exact_uuid_verified'] for p in m['proofs'])}\t{m['observed_pickup_within_window']}\t{len(m['proofs'])}\n" for m in material_records))
print(json.dumps({k:v for k,v in result.items() if k in ['native_valid_position_species','remaining_position_species','natural_material_death_drop_verified','material_pickup_exact_uuid_verified','latest_day_time','material_species_death_attempts']},ensure_ascii=False))
