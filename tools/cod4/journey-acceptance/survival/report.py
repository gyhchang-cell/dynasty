"""Summarize only observed survival action/events; never certify all stages by plan."""
from pathlib import Path
import json,collections,datetime,hashlib
ROOT=Path(__file__).resolve().parents[4];BASE=Path(__file__).resolve().parent
records=[];events=[];errors=[];sessions=[]
for run in sorted((BASE/'evidence').glob('run-*')):
 if not (run/'READY.json').exists():continue
 ready=json.loads((run/'READY.json').read_text());live=json.loads((run/('FINISHED.json' if (run/'FINISHED.json').exists() else 'live-state.json')).read_text())
 sessions.append({'run':run.name,'initial':ready,'last_observation':live,'exit_code':int((run/'exit-code.txt').read_text()) if (run/'exit-code.txt').exists() else None})
 for p in sorted(run.glob('*-result.json')):
  d=json.loads(p.read_text());a=d['command'];before=d['before'];after=d['after'];records.append({'run':run.name,'id':a['id'],'op':a['op'],'outcome':d['outcome'],'wall_seconds':(after['monotonicNanos']-before['monotonicNanos'])/1e9,'from':before.get('client',{}).get('position'),'to':after.get('client',{}).get('position'),'evidence':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 for p in sorted(run.glob('*-FAIL.json')):errors.append({'run':run.name,'evidence':str(p.relative_to(ROOT)),'error':json.loads(p.read_text())['error'],'production_defect_claimed':False})
 p=run/'native-events.jsonl'
 for line in p.read_text().splitlines() if p.exists() else []:
  try:d=json.loads(line)
  except json.JSONDecodeError:continue
  if d['kind']!='server_observation':events.append({'run':run.name,**d})
counts=collections.Counter(x['kind'] for x in events);crafted=collections.Counter();picked=collections.Counter()
for e in events:
 if e['kind']=='native_item_crafted':crafted[e['data']['output']['item']]+=e['data']['output']['count']
 if e['kind']=='native_item_pickup':picked[e['data']['picked']['item']]+=e['data']['picked']['count']
report={'status':'NATURAL_ROUTE_STARTED_PARTIAL_NOT_SIX_STAGE_PASS','generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'qa_supplied_materials':0,'qa_supplied_progress':0,'natural_picked_items':dict(picked),'native_crafted_outputs':dict(crafted),'event_counts':dict(counts),'native_actions':records,'input_failures':errors,'sessions':sessions,'events':events,'clock_limits':'Per-action monotonic wall times recorded. Startup/relaunch, menu pause, investigation and idle are not target2-3h play. Server tick and full category counts retained in session snapshots. No hourly pacing conclusion.','can_remove_six_stage_or_pacing_todo':False}
(BASE/'progress.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
p=ROOT/'docs/cod4/audit-20261022/journey-acceptance.json';d=json.loads(p.read_text());d['natural_survival_client'].update({'status':report['status'],'progress':'tools/cod4/journey-acceptance/survival/progress.json','natural_picked_items':dict(picked),'native_crafted_outputs':dict(crafted),'input_failures':len(errors),'todo_can_close':False});p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['status','natural_picked_items','native_crafted_outputs','event_counts']},ensure_ascii=False))
