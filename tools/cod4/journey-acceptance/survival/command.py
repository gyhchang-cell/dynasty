"""Submit one bounded native client action to the private natural survival run."""
from pathlib import Path
import json,sys,time,os
ROOT=Path(__file__).resolve().parents[4]
OUT=ROOT/'tools/cod4/journey-acceptance/survival/evidence'/sys.argv[1]
command=json.loads(sys.argv[2]);assert 'id' in command and 'op' in command
assert not (OUT/(command['id']+'-result.json')).exists(), 'Do not overwrite evidence'
(OUT/'command.pending').write_text(json.dumps(command));os.replace(OUT/'command.pending',OUT/'command.json')
for _ in range(240):
 for suffix in ['-result.json','-FAIL.json']:
  p=OUT/(command['id']+suffix)
  if p.exists():
   d=json.loads(p.read_text());s=d.get('after',d.get('state',{}));c=s.get('client',{});v=s.get('server',{})
   print(json.dumps({'id':command['id'],'outcome':d.get('outcome',d.get('error')),'position':c.get('position'),'health':c.get('health'),'food':c.get('food'),'worldTime':v.get('worldTime'),'menu':c.get('menuClass'),'inventory':[(i,x) for i,x in enumerate(c.get('inventory',[])) if x['count']],'completedQuests':[q['id'] for q in v.get('quests',[]) if isinstance(q,dict) and q.get('completed')],'paused':s.get('paused')},ensure_ascii=False))
   sys.exit(1 if suffix=='-FAIL.json' else 0)
 if (OUT/'exit-code.txt').exists():raise SystemExit('Client exited')
 time.sleep(.25)
raise SystemExit('No action result within60seconds; inspect live-state, do not overwrite')
