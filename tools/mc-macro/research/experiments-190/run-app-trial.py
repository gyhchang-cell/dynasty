import subprocess,os,sys,pathlib,json,shutil,time
root=pathlib.Path(__file__).resolve().parents[2];out=root/'.build/state-live';probe=pathlib.Path(os.environ.get('MC_TEST_PROBE',str(root/'.build/live-test/probe')))
label,bxs,bzs,yaws,ps,xos,zos,ss=sys.argv[1:];bx=int(bxs);bz=int(bzs);yaw=float(yaws);pitch=float(ps);ox=float(xos);oz=float(zos);seconds=float(ss)
e={**os.environ,'MC_TEST_PID':os.environ.get('MC_TEST_PID','26959'),'MC_TEST_OPTIONS':'/Users/a15356015027/Public/.minecraft/versions/1.8.9/options.txt','TEST_RISE':os.environ.get('TEST_RISE','0'),'TEST_PITCH':'45','TEST_MOVEMENT':'1'}
assert os.environ.get('MC_TEST_PID') and os.environ.get('MC_TEST_APP_LOG'), 'Set the dedicated singleplayer PID and app trace path'
# A remembered PID alone does not prove that the user is still in our test
# save. Verify open region files before any teleport, fill or key input.
expected_save=pathlib.Path(os.environ.get('MC_TEST_SAVE','/Users/a15356015027/Public/.minecraft/versions/1.8.9/saves/Codex_Pitch_Telly_1025')).resolve()
opened=subprocess.check_output(['lsof','-F','n','-p',e['MC_TEST_PID']],text=True)
regions=[pathlib.Path(line[1:]) for line in opened.splitlines() if line.startswith('n/') and '/saves/' in line and '/region/' in line]
assert regions and all(p.is_relative_to(expected_save) for p in regions), 'Dedicated test save not confirmed; no input sent'
actual_mode=subprocess.check_output(['defaults','read','local.mc-macro.assistant','bridgeMode'],text=True).strip()
expected_mode=os.environ.get('TEST_MODE') or ('level' if '-flat-' in label else None)
assert expected_mode is None or actual_mode==expected_mode, f'Wrong app mode: wanted {expected_mode}, found {actual_mode}; no input sent'
(out/f'{label}-fixture.json').write_text(json.dumps({'label':label,'save':str(expected_save),'pid':e['MC_TEST_PID'],'mode_at_start':actual_mode,'expected_mode':expected_mode,'base':[bx,bz],'offset':[ox,oz],'yaw':yaw,'pitch':pitch,'seconds':seconds},indent=2)+'\n')
axis=yaw
if axis==-90: bounds=(bx-2,bz-2,bx+75,bz+2)
elif axis==90: bounds=(bx-75,bz-2,bx+2,bz+2)
elif axis==0: bounds=(bx-2,bz-2,bx+2,bz+75)
elif abs(axis)==180: bounds=(bx-2,bz-75,bx+2,bz+2)
else: bounds=(bx-15,bz-15,bx+35,bz+35)
x0,z0,x1,z1=bounds
subprocess.run([str(probe),"resume"],env=e,stdout=subprocess.DEVNULL,check=True)
clears=[f'/fill {x0} 79 {z0} {x1} 140 {z1} air']
if yaw not in [0,90,-90,180,-180]:
 import math
 # Cover the entire possible diagonal route, including raised spans, while
 # each /fill stays under vanilla's 32768-block limit.
 ux=-math.sin(math.radians(yaw));uz=math.cos(math.radians(yaw))
 clears=[]
 for distance in range(0,int(seconds*7)+24,14):
  cx=bx+round(ux*distance);cz=bz+round(uz*distance)
  clears.append(f'/fill {cx-9} 79 {cz-9} {cx+9} 140 {cz+9} air')
commands=[f'/tp {bx+.5} 5 {bz+.5} {yaw} 0',*clears,f'/setblock {bx} 79 {bz} stone',f'/tp {bx+ox} 80 {bz+oz} {yaw} {pitch}']
if os.environ.get('TEST_OBSTACLE')=='ceiling': commands.insert(-1,f'/setblock {bx} 82 {bz} stone')
for c in commands:
 r=subprocess.run([str(probe),'command',c],env=e,capture_output=True,text=True)
 if c.startswith('/tp') and ' 5 ' in c:time.sleep(2)
 if r.returncode: print(r.stdout,flush=True);sys.exit(1)
shutil.copy(root/'.build/live-test/command.png',out/f'{label}-start.png')
recorder=None
if os.environ.get('TEST_RECORD'):
 recorder=subprocess.Popen([str(root/'.build/video-study/record-window'),os.environ.get('MC_TEST_PID','26959'),str(min(60,seconds+4)),str(root/'.build/video-study'/f'{label}.mov')],stdout=open(out/f'{label}-record.log','w'),stderr=subprocess.STDOUT);time.sleep(.5)
log=out/f'{label}.log'
appLog=pathlib.Path(os.environ['MC_TEST_APP_LOG'])
start=appLog.stat().st_size
with (out/f'{label}-probe.log').open('w') as f:
 held_probe=os.environ.get('TEST_HOLD_PROBE')
 subprocess.run(([held_probe,ss] if held_probe else [str(root/'.build/switch-test/probe'),ss] if os.environ.get('TEST_SWITCH') else [str(probe),'hold','15',ss]),env=e,stdout=f,stderr=subprocess.STDOUT,check=True)
time.sleep(1.5)
log.write_text(appLog.read_bytes()[start:].decode('utf-8'))
subprocess.run([str(probe),'inspect'],env=e,stdout=subprocess.DEVNULL,check=True)
shutil.copy(root/'.build/live-test/before.png',out/f'{label}-end.png')
if recorder: recorder.wait()
s=log.read_text().splitlines();poses=[x for x in s if ' POSE ' in x]
landed=sum(' ground true ' in v and ' ground false ' in u for u,v in zip(poses,poses[1:]))
print(json.dumps({'trial':log.name,'landings':landed,'start':poses[0] if poses else None,'end':poses[-1] if poses else None,'result':s[-1] if s else 'NO_APP_TRACE'},ensure_ascii=False),flush=True)
