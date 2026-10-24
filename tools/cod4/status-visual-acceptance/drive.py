from pathlib import Path
import json,sys,time
R=Path(__file__).resolve().parents[3];D=R/'docs/cod4/audit-20261022/status-visual-acceptance'/sys.argv[1]
def wait(p,timeout=600):
 end=time.time()+timeout
 while time.time()<end:
  if p.exists():return json.loads(p.read_text())
  fail=list(D.glob('*-FAIL.json'))
  if fail:raise RuntimeError(fail[-1].read_text())
  if (D/'exit-code.txt').exists():raise RuntimeError('own client exited')
  time.sleep(.3)
 raise TimeoutError(p)
cases=[]
for effect in ['yin_qi','yang_qi','sha_qi','thunder_mark','soul_burn','frost_vein','armor_break','stagger']:
 cases.append(dict(id=effect+'-two-entities',effect=effect,pixels=True,duration=100,move=effect=='stagger',amplifier=1 if effect in ['yin_qi','yang_qi'] else 0,fps=10 if effect in ['yang_qi','frost_vein'] else 60))
cases += [dict(id='yin-immune-day',effect='yin_qi',set='tiangang',light='day'),dict(id='yang-immune-night',effect='yang_qi',set='disha',light='night'),dict(id='yin-day-night-equip',effect='yin_qi',set='tiangang',light='night',phase='swap'),dict(id='yang-day-night-equip',effect='yang_qi',set='disha',light='day',phase='swap')]
for phase in ['fire','warm','cold']:cases.append(dict(id='frost-'+phase,effect='frost_vein',phase=phase))
if len(sys.argv)>2 and sys.argv[2]=='repair':cases=[c for c in cases if c['id'] in ['yin-day-night-equip','yang-day-night-equip','frost-fire','frost-warm','frost-cold']]
wait(D/'READY.json')
for c in cases:
 c.setdefault('pixels',True);c.setdefault('duration',120)
 if (D/(c['id']+'-result.json')).exists():continue
 t=D/'command.tmp';t.write_text(json.dumps(c));t.replace(D/'command.json');r=wait(D/(c['id']+'-result.json'),180)
 es=json.loads((D/(c['id']+'-events.json')).read_text());fs=json.loads((D/(c['id']+'-frames.json')).read_text())
 print(c['id'],'frames',len(fs),'geometry',sorted({k for f in fs for k in f['geometry']}),'wire',sorted({e['data']['sequence'] for e in es if e['kind']=='actual-s2c-handle'}),'feedback',[e['data']['type'] for e in es if e['kind']=='actual-combat-feedback'],flush=True)
(D/'DRIVER-COMPLETE.json').write_text(json.dumps(cases,indent=2))
t=D/'command.tmp';t.write_text(json.dumps(dict(id='finish-status',op='finish')));t.replace(D/'command.json')
