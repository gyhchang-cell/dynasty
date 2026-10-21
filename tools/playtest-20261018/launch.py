from pathlib import Path
import subprocess,shlex,shutil,json,hashlib,uuid,os
R=Path(__file__).resolve().parents[2];root=R/'build/playtest-full-20261018-e';out=R/'docs/playtest-20261018';profile=Path('/Users/a15356015027/Public/.minecraft/versions/Dynasty')
assert not root.exists(),'Fresh disposable runtime required'
line=next(l for l in subprocess.check_output(['ps','-axo','command'],text=True).splitlines() if 'BootstrapLauncher' in l and '--gameDir '+str(profile)+' ' in l)
args=shlex.split(line)
main=args.index("cpw.mods.bootstraplauncher.BootstrapLauncher")
args=[a for i,a in enumerate(args) if not (i<main and a=="Dynasty")]
for flag,value in {'--gameDir':str(root),'--username':'AuditPlayer','--accessToken':'0','--uuid':uuid.uuid4().hex,'--userType':'legacy','--width':'1280','--height':'800','--clientId':'0','--xuid':'0'}.items():
 if flag in args:args[args.index(flag)+1]=value
args=[('-Xmx3G' if a.startswith('-Xmx') else a) for a in args]
args.insert(1,'-Ddynasty.audit.output='+str(out/'native'))
args.insert(1,'-XX:ActiveProcessorCount=2')
root.mkdir();(out/'native').mkdir(exist_ok=True)
for folder in ['mods','config','defaultconfigs','resourcepacks']:
 if (profile/folder).is_dir():shutil.copytree(profile/folder,root/folder)
# Only the audited recipe/atlas resources differ from the installed production jar.
import zipfile
jar=root/'mods/dynasty-1.4.0.jar';tmp=jar.with_suffix('.tmp')
keys=[x['file'].removeprefix('src/main/resources/') for x in json.loads((out/'recipe-fixes.json').read_text())]+['assets/minecraft/atlases/blocks.json','assets/dynasty/models/item/evocation_talisman.json','assets/dynasty/lang/zh_cn.json','assets/dynasty/lang/en_us.json']
with zipfile.ZipFile(jar) as z,zipfile.ZipFile(tmp,'w') as w:
 for info in z.infolist():w.writestr(info,(R/'src/main/resources'/info.filename).read_bytes() if info.filename in keys else z.read(info.filename))
os.replace(tmp,jar)
helper=next((R/'build/libs').glob('dynasty-playtest-helper*.jar'));shutil.copy2(helper,root/'mods'/helper.name)
(root/'options.txt').write_text('soundCategory_master:0.0\nlang:zh_cn\nguiScale:3\ngamma:0.0\nmaxFps:30\nrenderDistance:2\nsimulationDistance:5\ntutorialStep:none\n')
manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (profile/'mods').glob('*.jar')}
(out/'runtime-manifest.json').write_text(json.dumps({'source':str(profile),'isolated':str(root),'mods':manifest,'helper':helper.name},indent=2))
with (out/'full-client.log').open('w') as log:
 proc=subprocess.Popen(args,cwd=root,stdout=log,stderr=subprocess.STDOUT);(out/'pid.txt').write_text(str(proc.pid));print('Started isolated full-pack client; PID',proc.pid,'mods',len(manifest),flush=True);code=proc.wait();print('Client exit',code)
