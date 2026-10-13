"""One frozen, silent native Forge process for all eight; never uses normal user saves."""
import json,os,shutil,subprocess,time,hashlib,zipfile,sys
from pathlib import Path
R=Path(__file__).resolve().parents[3]
reference=os.environ.get('DYNASTY_POWER_REFERENCE_QA')=='1'
power=os.environ.get('DYNASTY_HUMAN_POWER_QA')=='1'
own_reference=os.environ.get('DYNASTY_REFERENCE_OWN_ONLY')=='1'
human_presence=power or os.environ.get('DYNASTY_HUMAN_PRESENCE_QA')=='1'
human=human_presence or os.environ.get('DYNASTY_HUMAN_QA')=='1'
checklist=human or os.environ.get('DYNASTY_CHECKLIST_QA')=='1'
proportions=os.environ.get('DYNASTY_PROPORTION_QA')=='1'
materials=proportions or os.environ.get('DYNASTY_MATERIAL_QA')=='1'
spirits=materials or os.environ.get('DYNASTY_SPIRIT_QA')=='1'
presence=checklist or spirits or os.environ.get('DYNASTY_PRESENCE_QA')=='1'
name=sys.argv[1] if len(sys.argv)>1 else 'batch-1';root=R/'build/boss-eight-native'/name;root.mkdir(parents=True,exist_ok=False)
out=R/('docs/art/boss-human-v12/reference-native' if reference else 'docs/art/boss-human-v12/native' if power else 'docs/art/boss-human-v11/native' if human_presence else 'docs/art/boss-human-v10/native' if human else 'docs/art/boss-checklist-night-v9/native' if checklist else 'docs/art/boss-proportions-v8/native' if proportions else 'docs/art/boss-materials-v6/native' if materials else 'docs/art/boss-presence-v5/native' if spirits else 'docs/art/boss-presence-v4/native' if presence else 'docs/art/boss-eight-v1/native')/name;out.mkdir(parents=True,exist_ok=False)
launch=Path(sys.argv[2]) if len(sys.argv)>2 else Path('/Users/a15356015027/Desktop/dynasty/build/guiche-art-native/strict16-final/launch.json')
cfg=json.loads(launch.read_text());old=cfg['environment']['MOD_CLASSES'].split(os.pathsep)
paths=[R/'build/resources/main',R/'build/classes/java/main',None,R/'build/classes/java/bossEightQa'];mapping={}
manifest={'launchTemplate':str(launch),'productionJarSha256':hashlib.sha256((R/'build/libs/dynasty-1.4.0.jar').read_bytes()).hexdigest(),'resources':{}}
with zipfile.ZipFile(R/'build/libs/dynasty-1.4.0.jar') as jar:
 assert not any('BossEightClientQa' in n for n in jar.namelist())
 targets=json.loads((R/'tools/art/boss-eight/targets.json').read_text())
 if presence:targets={i:{'folder':'boss_forms'} for i in ('undead_first_emperor','pilin_zhijinwu','juchui_jinjia_lishi','hammer_chain')}
 if spirits:targets={i:{'folder':'boss_forms'} for i in ('eunuch_mastermind','rebel_general','xianzhen_duantoujiang')}
 if materials:targets={i:{'folder':'boss_forms'} for i in ('rebel_general','xianzhen_duantoujiang')}
 if proportions:targets={'rebel_general':{'folder':'boss_forms'}}
 if checklist:targets={i:{'folder':'boss_cuboid'} for i in ('nine_heaven_general','dragon_king','dragon_emperor')}
 for id,m in targets.items():
  for kind,ext in [('geo','.geo.json'),('animations','.animation.json'),('textures/entity','.png')]:
   p=Path('assets/dynasty')/kind/m['folder']/(id+ext);b=(R/'src/main/resources'/p).read_bytes();assert b==jar.read(str(p))==(R/'build/resources/main'/p).read_bytes();manifest['resources'][str(p)]=hashlib.sha256(b).hexdigest()
  if id=='nine_heaven_general':
   p=Path('assets/dynasty/textures/entity/boss_cuboid/nine_heaven_general_aura.png')
   if (R/'src/main/resources'/p).exists():
    b=(R/'src/main/resources'/p).read_bytes();assert b==jar.read(str(p))==(R/'build/resources/main'/p).read_bytes();manifest['resources'][str(p)]=hashlib.sha256(b).hexdigest()
if power and not reference:
 p=Path('assets/dynasty/textures/effect/tianjiang_stream.png')
 with zipfile.ZipFile(R/'build/libs/dynasty-1.4.0.jar') as jar:
  b=(R/'src/main/resources'/p).read_bytes();assert b==jar.read(str(p))==(R/'build/resources/main'/p).read_bytes();manifest['resources'][str(p)]=hashlib.sha256(b).hexdigest()
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
jvm+=['-Xmx2G','-XX:ActiveProcessorCount=2','-Ddynasty.bossEightQa='+('false' if reference else 'true'),'-Ddynasty.bossEightQa.start='+os.environ.get('DYNASTY_ART_START','0'),'-Ddynasty.bossEightQa.output='+str(out),'-javaagent:'+str(R/'build/boss-eight-agent/quiet-window-agent.jar')]
if reference:
 jvm+=['-Ddynasty.bossPowerReferenceQa=true','-Ddynasty.bossPowerReferenceQa.output='+str(out),'-Ddynasty.bossPowerReferenceQa.ownOnly='+str(own_reference).lower(),'-Ddynasty.bossPowerReferenceQa.ownEffects='+str(os.environ.get('DYNASTY_REFERENCE_OWN_EFFECTS')=='1').lower(),'-Ddynasty.bossPowerReferenceQa.both='+str(os.environ.get('DYNASTY_REFERENCE_BOTH')=='1').lower()]
 for env,prop in [('DYNASTY_REFERENCE_ENTITY','entity'),('DYNASTY_REFERENCE_DISTANCE','distance')]:
  if os.environ.get(env):jvm.append('-Ddynasty.bossPowerReferenceQa.'+prop+'='+os.environ[env])
if checklist:jvm.append('-Ddynasty.bossChecklistQa=true')
if human:jvm.append('-Ddynasty.bossHumanQa=true')
if human_presence:jvm.append('-Ddynasty.bossHumanPresenceQa=true')
if presence:jvm.append('-Ddynasty.bossPresenceQa=true')
if spirits:jvm.append('-Ddynasty.bossSpiritQa=true')
if materials:jvm.append('-Ddynasty.bossMaterialQa=true')
if os.environ.get('DYNASTY_ART_LIMIT'):jvm.append('-Ddynasty.bossEightQa.limit='+os.environ['DYNASTY_ART_LIMIT'])
if os.environ.get('DYNASTY_AURA_ENVIRONMENTS')=='1':jvm.append('-Ddynasty.tianjiangAuraEnvironments=true')
if os.environ.get('DYNASTY_AURA_SEQUENCE')=='1':jvm.append('-Ddynasty.tianjiangAuraSequence=true')
for env,prop in [('DYNASTY_ART_CAMERA_DISTANCE','cameraDistance'),('DYNASTY_ART_CAMERA_PITCH','cameraPitch')]:
 if os.environ.get(env):jvm.append('-Ddynasty.bossEightQa.'+prop+'='+os.environ[env])
work=root/'host';work.mkdir();(work/'options.txt').write_text('soundCategory_master:0.0\nfullscreen:false\n');(work/'config').mkdir();(work/'config/fml.toml').write_text('earlyWindowControl=false\n')
if reference and not own_reference:
 (work/'mods').mkdir()
 for key in ['DYNASTY_CATACLYSM_JAR','DYNASTY_LIONFISH_JAR']:
  jar=Path(os.environ[key]);assert jar.is_file();shutil.copy2(jar,work/'mods'/jar.name)
  manifest.setdefault('referenceMods',{})[jar.name]=hashlib.sha256(jar.read_bytes()).hexdigest()
 for entry in os.environ.get('DYNASTY_REFERENCE_EXTRA_JARS','').split(os.pathsep):
  if not entry:continue
  jar=Path(entry);assert jar.is_file();shutil.copy2(jar,work/'mods'/jar.name)
  manifest['referenceMods'][jar.name]=hashlib.sha256(jar.read_bytes()).hexdigest()
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
 log.close()  # Private launcher/client logs stay in ignored build/, never in the art gallery.
