"""One frozen, silent native Forge process for all eight; never uses normal user saves."""
import json,os,shutil,subprocess,time,hashlib,zipfile,sys
from pathlib import Path
R=Path(__file__).resolve().parents[3]
name=sys.argv[1] if len(sys.argv)>1 else 'batch-1';root=R/'build/boss-eight-native'/name;root.mkdir(parents=True,exist_ok=False)
out=R/'docs/art/boss-eight-v1/native'/name;out.mkdir(parents=True,exist_ok=False)
launch=Path(sys.argv[2]) if len(sys.argv)>2 else Path('/Users/a15356015027/Desktop/dynasty/build/guiche-art-native/strict16-final/launch.json')
cfg=json.loads(launch.read_text());old=cfg['environment']['MOD_CLASSES'].split(os.pathsep)
paths=[R/'build/resources/main',R/'build/classes/java/main',None,R/'build/classes/java/bossEightQa'];mapping={}
manifest={'launchTemplate':str(launch),'productionJarSha256':hashlib.sha256((R/'build/libs/dynasty-1.4.0.jar').read_bytes()).hexdigest(),'resources':{}}
with zipfile.ZipFile(R/'build/libs/dynasty-1.4.0.jar') as jar:
 assert not any('BossEightClientQa' in n for n in jar.namelist())
 for id,m in json.loads((R/'tools/art/boss-eight/targets.json').read_text()).items():
  for kind,ext in [('geo','.geo.json'),('animations','.animation.json'),('textures/entity','.png')]:
   p=Path('assets/dynasty')/kind/m['folder']/(id+ext);b=(R/'src/main/resources'/p).read_bytes();assert b==jar.read(str(p))==(R/'build/resources/main'/p).read_bytes();manifest['resources'][str(p)]=hashlib.sha256(b).hexdigest()
for i,(entry,src) in enumerate(zip(old,paths)):
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
jvm+=['-Xmx2G','-XX:ActiveProcessorCount=2','-Ddynasty.bossEightQa=true','-Ddynasty.bossEightQa.start='+os.environ.get('DYNASTY_ART_START','0'),'-Ddynasty.bossEightQa.output='+str(out),'-javaagent:'+str(R/'build/boss-eight-agent/quiet-window-agent.jar')]
work=root/'host';work.mkdir();(work/'options.txt').write_text('soundCategory_master:0.0\nfullscreen:false\n');(work/'config').mkdir();(work/'config/fml.toml').write_text('earlyWindowControl=false\n')
cfg.update(jvmArgs=jvm,directory=str(work));(root/'launch.json').write_text(json.dumps(cfg,indent=2));(out/'runtime-manifest.json').write_text(json.dumps(manifest,indent=2))
log=(root/'client.log').open('w');child=subprocess.Popen([cfg['executable'],*jvm,'-cp',cfg['classpath'],cfg['main'],*cfg['args']],cwd=work,env=dict(os.environ,**cfg['environment']),stdout=log,stderr=subprocess.STDOUT);print('Native batch',name,'pid',child.pid,flush=True)
try:
 deadline=time.monotonic()+900
 while child.poll() is None:
  time.sleep(1)
  if time.monotonic()>deadline:raise RuntimeError('Native timed out')
 if child.returncode or not (out/'PASS.txt').exists():raise RuntimeError('Native failed: '+str(root/'client.log'))
 print((out/'PASS.txt').read_text().splitlines()[-1],flush=True)
finally:
 if child.poll() is None:
  child.terminate()
  try:child.wait(timeout=10)
  except subprocess.TimeoutExpired:child.kill();child.wait()
 log.close();shutil.copy2(root/'client.log',out/'client.log')
