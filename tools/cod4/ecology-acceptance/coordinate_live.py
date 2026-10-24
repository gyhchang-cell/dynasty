"""Drive only observer teleports/scans, using QA's existing native server and real client. Never changes world time or spawns actors."""
from pathlib import Path
import json,time,subprocess,datetime,re
from read_weather import read_weather
R=Path(__file__).resolve().parents[3];D=R/'docs/cod4/audit-20261022/ecology-acceptance/live-run1'
def state():return json.loads((D/'state.json').read_text())
def write_control(**values):
 (D/'control.json').write_text(json.dumps(values));
 with (D/'coordinator.jsonl').open('a') as f:f.write(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),**values})+'\n')
def summarize():
 subprocess.run(['python3',str(R/'tools/cod4/ecology-acceptance/summarize_live.py')],stdout=subprocess.DEVNULL,check=True)
 return json.loads((D/'summary.json').read_text())
def cityproof(m):
 for p in m['proofs']:
  xyz=[float(v) for v in p['spawn_pos'].strip('()').split(',')]
  if p['pickup_exact_uuid_verified'] and 1604<=xyz[0]<=1803 and 51<=xyz[1]<=130 and -17980<=xyz[2]<=-17781:return True
 return False
rotation=0
while not (D/'stop-coordinator.txt').exists():
 s=summarize();missing={m['id'] for m in s['material_proofs'] if not any(p['pickup_exact_uuid_verified'] for p in m['proofs'])}
 for m in s['material_proofs']:
  if m['id'] in ['qimen_cable','qimen_gear'] and not cityproof(m):missing.add(m['id'])
 if not missing and s['native_valid_position_species']==30:
  (D/'coordinator-complete.txt').write_text('30 valid species positions; 10 exact-UUID natural material acquisition proofs, including qimen materials born inside naturally generated clockwork city. Review summary and source events.\n');break
 plans=[];live=state();day=live['current_day_time']%24000;night=live.get('live_night',13000<=day<=23000)
 if missing&{'wolf_fang','sprite_jade'} or ('fox_pelt' in missing and night):plans.append('forest')
 if missing&{'qimen_cable','qimen_gear'}:plans.append('clockwork')
 if 'python_gall' in missing:plans.append('swamp')
 weather=read_weather()
 (D/'saved-world-weather.json').write_text(json.dumps(weather,indent=2)+'\n')
 if 'locust_dust' in missing and not live.get('live_raining',bool(weather.get('raining'))):plans.append('desert')
 if 'sprite_jade' in missing:plans.append('lush_caves')
 if 'lantern_oil' in missing and night:plans.append('battlefield')
 if missing&{'kappa_scale','crab_shell'}:plans.append('ocean')
 if not plans:plans=['desert'] if 'locust_dust' in missing else ['forest','battlefield','post_house','ocean','dripstone_caves']
 # Keep fox's only night window useful while preserving deterministic region rotation.
 if night and missing&{'fox_pelt','lantern_oil'}:
  nightplans=[]
  if 'fox_pelt' in missing:nightplans.append('forest')
  if 'lantern_oil' in missing:nightplans.append('battlefield')
  zone=nightplans[rotation%len(nightplans)]
 elif rotation==0 and 'clockwork' in plans:zone='clockwork'
 else:zone=plans[rotation%len(plans)]
 rotation+=1;before=state()['current_game_tick'];write_control(scan_zone=zone,note='Load genuine normal FULL terrain before using heightmap for observer; no block/biome edits')
 loaded=False
 for _ in range(90):
  time.sleep(2)
  try:
   es=[json.loads(x) for x in (D/'events.jsonl').read_text().splitlines()]
   if any(e['kind']=='zone_scan_finished' and e.get('zone')==zone and e['game_tick']>=before for e in es):loaded=True;break
  except (json.JSONDecodeError,OSError):pass
 if not loaded:
  with (D/'coordinator.jsonl').open('a') as f:f.write(json.dumps({'error':'native scan not completed within 180 wall seconds','zone':zone})+'\n')
  continue
 write_control(observe_zone=zone,hold_ticks=3000,native_weather_raining=live.get('live_raining'),native_night=night,note='Real automated client observer fixture, not a full survival journey')
 start=state()['current_game_tick']
 while state()['current_game_tick']-start<2400 and not (D/'stop-coordinator.txt').exists():
  time.sleep(10);s=summarize()
  if (D/'client-error.txt').exists():raise SystemExit('Client error: '+(D/'client-error.txt').read_text())
