from pathlib import Path
import os,subprocess,time,json,datetime,sys
RUN=sys.argv[1] if len(sys.argv)>1 else "run-02"
R=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent;O=R/'docs/cod4/audit-20261022/mob-load-acceptance';O.mkdir(exist_ok=True)
env=os.environ.copy();env['JAVA_HOME']='/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home'
cmd=['./gradlew','--offline','--gradle-user-home',str(B/'.work/gradle-home'),'--project-cache-dir',str(B/'.work/project-cache'),'-I',str(B/'qa.init.gradle'),'-PmobRun='+RUN,'runClient']
if '--remaining' in sys.argv:cmd.insert(-1,'-PmobRemaining=true')
if '--geometry-only' in sys.argv:cmd.insert(-1,'-PmobGeometryOnly=true')
with (O/(RUN+'-client.log')).open('w') as log,(O/(RUN+'-host-load.jsonl')).open('w') as monitor:
 p=subprocess.Popen(cmd,cwd=R,env=env,stdout=log,stderr=subprocess.STDOUT)
 (O/(RUN+'-launcher-pid.txt')).write_text(str(p.pid))
 print('Own isolated launcher PID',p.pid,flush=True)
 while p.poll() is None:
  ps=subprocess.run(['ps','-axo','pid,pcpu,comm'],capture_output=True,text=True).stdout
  jvms=[s.strip() for s in ps.splitlines() if 'java' in s.lower()]
  monitor.write(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'loadavg':os.getloadavg(),'java_processes_without_arguments':jvms})+'\n');monitor.flush();time.sleep(5)
 (O/(RUN+'-exit-code.txt')).write_text(str(p.returncode));print('exit',p.returncode,flush=True)
