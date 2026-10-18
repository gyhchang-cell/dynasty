"""Muted disposable Forge fixture; never opens or closes a user's save."""
from pathlib import Path
import json,os,shutil,subprocess,time,hashlib,zipfile,sys
from refine import R,SPECS,old
path=old.path
name=sys.argv[1] if len(sys.argv)>1 else 'creature-v33-final';root=R/'build/boss-eight-native'/name;root.mkdir(parents=True,exist_ok=False)
out=R/'docs/art/creature-mc-v35/native'/name;out.mkdir(parents=True,exist_ok=False)
launch=Path('/Users/a15356015027/Desktop/dynasty/build/guiche-art-native/strict16-final/launch.json');cfg=json.loads(launch.read_text());old=cfg['environment']['MOD_CLASSES'].split(os.pathsep)
manifest={'launchTemplate':str(launch),'resources':{},'note':'AI disabled, existing synchronized skill controllers; natural combat and multiplayer are separate.'}
with zipfile.ZipFile(R/'build/libs/dynasty-1.4.0.jar') as jar:
 assert not any('Cod1CreatureQa' in n for n in jar.namelist())
 for id in SPECS:
  for kind in ['geo','texture','anim']:
   src=path(id,kind);rel=src.relative_to(R/'src/main/resources');b=src.read_bytes();assert b==jar.read(str(rel))==(R/'build/resources/main'/rel).read_bytes();manifest['resources'][str(rel)]=hashlib.sha256(b).hexdigest()
mapping={}
for i,(entry,src) in enumerate(zip(old,[R/'build/resources/main',R/'build/classes/java/main',None,R/'build/classes/java/bossEightQa'])):
 dst=root/'runtime'/str(i);dst.parent.mkdir(parents=True,exist_ok=True)
 if src:shutil.copytree(src,dst)
 else:dst.mkdir()
 mapping[entry.split('%%',1)[1]]=str(dst)
def remap(s):
 for a,b in sorted(mapping.items(),key=lambda kv:-len(kv[0])):s=s.replace(a,b)
 return s
cfg['classpath']=remap(cfg['classpath']);cfg['environment']={k:remap(v) for k,v in cfg['environment'].items()};jvm=[]
for a in cfg['jvmArgs']:
 if a.startswith(('-Ddynasty.','-Xmx','-XX:ActiveProcessorCount=','-javaagent:')):continue
 if a.startswith('-DlegacyClassPath.file='):
  p=root/'legacy-classpath.txt';p.write_text(remap(Path(a.split('=',1)[1]).read_text()));a='-DlegacyClassPath.file='+str(p)
 jvm.append(remap(a))
if len(sys.argv)>2:jvm.append('-Ddynasty.cod1CreatureQa.only='+sys.argv[2])
jvm+=['-Xmx2G','-XX:ActiveProcessorCount=2','-Ddynasty.cod1CreatureQa=true','-Ddynasty.cod1CreatureQa.output='+str(out),'-javaagent:'+str(R/'build/boss-eight-agent/quiet-window-agent.jar')]
work=root/'host';work.mkdir();(work/'options.txt').write_text('soundCategory_master:0.0\nfullscreen:false\n');(work/'config').mkdir();(work/'config/fml.toml').write_text('earlyWindowControl=false\n')
cfg.update(jvmArgs=jvm,directory=str(work));(root/'launch.json').write_text(json.dumps(cfg,indent=2));(out/'runtime-manifest.json').write_text(json.dumps(manifest,indent=2))
with (root/'client.log').open('w') as log:
 child=subprocess.Popen([cfg['executable'],*jvm,'-cp',cfg['classpath'],cfg['main'],*cfg['args']],cwd=work,env=dict(os.environ,**cfg['environment']),stdout=log,stderr=subprocess.STDOUT);print('Native isolated, muted fixture PID',child.pid,flush=True)
 try:
  deadline=time.monotonic()+900
  while child.poll() is None:
   time.sleep(1)
   if time.monotonic()>deadline:raise RuntimeError('QA timed out')
  assert child.returncode==0 and (out/'PASS.txt').exists(),str(root/'client.log')
  print((out/'PASS.txt').read_text().splitlines()[-1],flush=True)
 finally:
  if child.poll() is None:child.terminate();child.wait(timeout=15)
