import subprocess,os,sys,pathlib,json,shutil,time
root=pathlib.Path(__file__).resolve().parents[2];out=root/'.build/state-live';probe=root/'.build/live-test/probe'
label,bxs,bzs,yaws,ps,xos,zos,ss=sys.argv[1:];bx=int(bxs);bz=int(bzs);yaw=float(yaws);pitch=float(ps);ox=float(xos);oz=float(zos);seconds=float(ss)
assert os.environ.get('MC_TEST_PID') and os.environ.get('TEST_CHECK'), 'Set MC_TEST_PID to the dedicated singleplayer instance and TEST_CHECK to the candidate binary'
os.environ['MC_TEST_AGENT']=str((root/'.build/start-189/agent-path').read_text())
e={**os.environ,'MC_TEST_PID':os.environ['MC_TEST_PID'],'MC_TEST_OPTIONS':'/Users/a15356015027/Public/.minecraft/versions/1.8.9/options.txt','TEST_RISE':os.environ.get('TEST_RISE','0'),'TEST_PITCH':'45','TEST_MOVEMENT':'1'}
if yaw==-90: bounds=(bx-2,bz-2,bx+75,bz+2)
elif yaw==90: bounds=(bx-75,bz-2,bx+2,bz+2)
elif yaw==0: bounds=(bx-2,bz-2,bx+2,bz+75)
elif abs(yaw)==180: bounds=(bx-2,bz-75,bx+2,bz+2)
else: bounds=(bx-15,bz-15,bx+35,bz+35)
x0,z0,x1,z1=bounds
subprocess.run([str(probe),"resume"],env=e,stdout=subprocess.DEVNULL,check=True)
commands=[f'/tp {bx+.5} 5 {bz+.5} {yaw} 0',f'/fill {x0} 79 {z0} {x1} {90 if yaw not in [0,90,-90,180,-180] else 140} {z1} air',f'/setblock {bx} 79 {bz} stone',f'/tp {bx+ox} 80 {bz+oz} {yaw} {pitch}']
extra=os.environ.get('TEST_OBSTACLE')
if extra=='ceiling-back': commands.insert(-1,f'/setblock {bx} 82 {bz-1} stone')
if extra=='ceiling': commands.insert(-1,f'/setblock {bx} 82 {bz} stone')
if extra=='wall': commands.insert(-1,f'/fill {bx} 80 {bz+1} {bx} 82 {bz+1} stone')
if extra=='fence': commands.insert(-1,f'/setblock {bx} 80 {bz+1} fence')
if extra=='distant': commands.insert(-1,f'/setblock {bx} 82 {bz+2} stone')
if extra=='platform': commands.insert(-1,f'/fill {bx} 79 {bz} {bx} 79 {bz+3} stone')
for c in commands:
 r=subprocess.run([str(probe),'command',c],env=e,capture_output=True,text=True)
 if c.startswith('/tp') and ' 5 ' in c: time.sleep(2)
 if r.returncode: print(r.stdout,flush=True);sys.exit(1)
shutil.copy(root/'.build/live-test/command.png',out/f'{label}-start.png')
recorder=None
if os.environ.get('TEST_RECORD'):
 recorder=subprocess.Popen([str(root/'.build/video-study/record-window'),os.environ['MC_TEST_PID'],str(min(60,seconds+4)),str(root/'.build/video-study'/f'{label}.mov')],stdout=open(out/f'{label}-record.log','w'),stderr=subprocess.STDOUT);time.sleep(.5)
log=out/f'{label}.log'
with log.open('w') as f: subprocess.run([os.environ['TEST_CHECK'],ss],env=e,stdout=f,stderr=subprocess.STDOUT,check=True)
if recorder: recorder.wait()
s=log.read_text().splitlines();poses=[x for x in s if ' pose ' in x]
landed=sum(' ground true ' in v and ' ground false ' in u for u,v in zip(poses,poses[1:]))
print(json.dumps({'trial':log.name,'landings':landed,'start':poses[0] if poses else None,'end':poses[-1] if poses else None,'result':s[-1]},ensure_ascii=False),flush=True)
