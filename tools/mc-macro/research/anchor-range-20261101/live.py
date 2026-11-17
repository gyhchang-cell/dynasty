from pathlib import Path
import subprocess,os,json,time,math,sys,shutil
root=Path(__file__).resolve().parents[2];game=root/'.build/anchor-singleplayer';out=root/'research/anchor-range-20261101';pid=(game/'pid').read_text().strip();env={**os.environ,'MC_TEST_PID':pid}
samples=[]
def probe(*a):
 assert '/.build/anchor-singleplayer/saves/mcPvPmax_Anchor_Test/' in subprocess.check_output(['lsof','-F','n','-p',pid],text=True)
 if a[0]=='trigger':
  samples.clear()
  p=subprocess.Popen([str(game/'probe'),*a],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
  while p.poll() is None:
   try:
    s=json.loads((game/'state.json').read_text());samples.append({k:s.get(k) for k in ['received','tick','position','velocity','yaw','pitch','hit','selected','ground','health','movementDown']})
   except (OSError,ValueError):pass
   time.sleep(.015)
  stdout,stderr=p.communicate()
  if p.returncode:raise RuntimeError(stdout+stderr)
  return
 r=subprocess.run([str(game/'probe'),*a],env=env,capture_output=True,text=True)
 if r.returncode:raise RuntimeError(r.stdout+r.stderr)
def fresh():
 for _ in range(60):
  s=json.loads((game/'state.json').read_text())
  if s.get('active') and s.get('singleplayer') and time.monotonic()-s.get('received',0)<.25:return s
  time.sleep(.05)
 raise RuntimeError('Inactive game; exclude this trial')
cases={
 'baseline':((.5,65,.5),(.5,65,3.5),(0,64,3),'survival',None),
 'near':((.5,65,.5),(.5,65,2.5),(0,64,2),'survival',None),
 'far-survival':((.5,65,.2),(.5,65,4.2),(0,64,4),'survival',None),
 'offaxis-far':((.5,65,.5),(1.5,65,4.5),(1,64,4),'survival',None),
 'offaxis-33':((.5,65,.5),(2.5,65,3.5),(2,64,3),'survival',None),
 'side':((.5,65,.5),(.5,65.8,3.0),(0,65,3),'survival','/setblock 0 65 3 stone'),
 'creative-edge':((.5,65,.5),(.5,65,5.03),(0,64,5),'creative',None),
 'lower-one':((.5,66,.5),(.5,65,3.5),(0,64,3),'survival','/setblock 0 65 0 obsidian'),
 'higher-one':((.5,65,.5),(.5,66,3.5),(0,65,3),'survival','/setblock 0 65 3 stone'),
 'higher-two':((.5,65,.5),(.5,67.1,4.0),(0,67,4),'survival','/fill 0 65 4 0 67 4 stone'),
 'higher-one-east':((.5,65,.5),(3.5,66,.5),(3,65,0),'survival','/setblock 3 65 0 stone'),
 'higher-one-north':((.5,65,.5),(.5,66,-2.5),(0,65,-3),'survival','/setblock 0 65 -3 stone'),
 'higher-one-west':((.5,65,.5),(-2.5,66,.5),(-3,65,0),'survival','/setblock -3 65 0 stone'),
 'higher-one-offset':((.75,65,.65),(.5,66,3.5),(0,65,3),'survival','/setblock 0 65 3 stone'),
 'wall-shield':((.5,65,.5),(.5,65,3.5),(0,64,3),'survival',['/fill -8 64 1 8 64 2 air','/setblock 1 65 2 stone']),
 'reuse-shield':((.5,65,.5),(.5,65,3.5),(0,64,3),'survival','/setblock 0 65 2 stone'),
}
probe('resume')
probe('command','/effect give @s minecraft:instant_health 1 10 true')
probe('command','/item replace entity @s hotbar.1 with minecraft:respawn_anchor 64')
probe('command','/item replace entity @s hotbar.2 with minecraft:glowstone 64')
probe('command','/item replace entity @s hotbar.3 with minecraft:obsidian 64')
for label in (sys.argv[1:] or list(cases)):
 p,target,hit,mode,extra=cases[label]
 delta=[target[i]-(p[i]+(1.62 if i==1 else 0)) for i in range(3)]
 yaw=math.degrees(math.atan2(-delta[0],delta[2]));pitch=-math.degrees(math.atan2(delta[1],math.hypot(delta[0],delta[2])))
 extras=extra if isinstance(extra,list) else [extra]
 for cmd in ['/gamemode '+mode,'/effect give @s minecraft:instant_health 1 10 true','/fill -8 64 -8 8 64 40 obsidian','/fill -8 65 -8 8 68 40 air',*extras,f'/tp @s {p[0]} {p[1]} {p[2]} {yaw} {pitch}']:
  if cmd:probe('command',cmd)
 probe('key','19');time.sleep(.3);before=fresh()
 assert tuple(before.get('hit',{}).get('pos',()))==hit,('Unexpected target',label,before.get('hit'))
 assert max(abs(a-b) for a,b in zip(before['position'],p))<.04,('Position changed',label)
 log=game/'app.log';offset=log.stat().st_size
 probe('trigger','.06');after=fresh();lines=log.read_bytes()[offset:].decode()
 label=os.environ.get('MC_ANCHOR_CASE_PREFIX','')+label
 record={'case':label,'before':before,'after':after,'log':lines,'samples':list(samples)}
 (out/(label+'.json')).write_text(json.dumps(record,ensure_ascii=False,indent=2));shutil.copy2(game/'raw.png',out/(label+'.png'))
 print(json.dumps({'case':label,'log':[l for l in lines.splitlines() if 'ANCHOR' in l],'view_before':[before['yaw'],before['pitch']],'view_after':[after['yaw'],after['pitch']]},ensure_ascii=False),flush=True)
 assert lines.count('ANCHOR SUCCESS')==1 and lines.count('ANCHOR BEGIN')==1,('Incomplete sequence',label)
 assert abs((after['yaw']-before['yaw']+180)%360-180)<.3 and abs(after['pitch']-before['pitch'])<.3,('View not restored',label)
 assert after['selected']==before['selected'] and not after['rightDown'],('Input or slot not restored',label)
