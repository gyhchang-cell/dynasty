"""Run an isolated real Forge client using an already prepared Forge launch.

Example: python run_native.py path/to/launch.json solo-1
Uses the current dedicated Gradle art build, copies every mod class/resource
directory before launching, and never opens the user's normal Minecraft world.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
import zipfile

REPO=Path(__file__).resolve().parents[3]
p=argparse.ArgumentParser();p.add_argument('launch',type=Path);p.add_argument('run');p.add_argument('--ids',default='river_imp,tree_spirit,shrimp_soldier');p.add_argument('--boss-audit',action='store_true');p.add_argument('--boss-final',action='store_true');p.add_argument('--boss-lifecycle',action='store_true');args=p.parse_args()
assert args.run and all(c.isalnum() or c in '-_' for c in args.run)
production={}
if args.boss_final or args.boss_lifecycle:
    # Refuse stale build outputs after a source edit or failed compilation.
    jar=REPO/'build/libs/dynasty-1.4.0.jar'
    assert jar.read_bytes()==(REPO/'build/reobfJar/output.jar').read_bytes(),'Production remap mismatch'
    production['jarSha256']=hashlib.sha256(jar.read_bytes()).hexdigest()
    production['sources']={}
    for name in ['DynastyClientEvents','BossCuboidRenderer','BossCuboidAura']:
        src=REPO/f'src/main/java/com/dynasty/client/{name}.java'
        if not src.exists():continue
        assert src.stat().st_mtime_ns<=jar.stat().st_mtime_ns,'Java source newer than JAR: '+name
        production['sources'][str(src.relative_to(REPO))]=hashlib.sha256(src.read_bytes()).hexdigest()
    with zipfile.ZipFile(jar) as z:
        for id in args.ids.split(','):
            for entry in [f'geo/boss_cuboid/{id}.geo.json',f'animations/boss_cuboid/{id}.animation.json',f'textures/entity/boss_cuboid/{id}.png']:
                path='assets/dynasty/'+entry;data=(REPO/'src/main/resources'/path).read_bytes()
                assert data==z.read(path)==(REPO/'build/resources/main'/path).read_bytes(),'Boss resource newer than build: '+id
root=REPO/'build/secondary-art-native'/args.run
root.mkdir(parents=True,exist_ok=False)
if production:
    frozen_jar=root/'production.jar';shutil.copy2(jar,frozen_jar)
    assert hashlib.sha256(frozen_jar.read_bytes()).hexdigest()==production['jarSha256'],'JAR changed while freezing'
output=REPO/'docs/art/secondary-cuboid-v1/native'/args.run
output.mkdir(parents=True,exist_ok=False)
cfg=json.loads(args.launch.read_text());old_roots=cfg['environment']['MOD_CLASSES'].split(os.pathsep)
sources=[REPO/'build/resources/main',REPO/'build/classes/java/main',
         None,REPO/'build/classes/java/secondaryArtQa']
mapping={};manifest=[]
for i,(entry,src) in enumerate(zip(old_roots,sources)):
    old=entry.split('%%',1)[1];dst=root/'runtime'/f'tree-{i}'
    if src is None:dst.mkdir(parents=True)
    else:shutil.copytree(src,dst)
    mapping[old]=str(dst)
    manifest.append({'source':str(src),'snapshot':str(dst),'files':[{'path':str(f.relative_to(dst)),
        'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in sorted(dst.rglob('*')) if f.is_file()]})
def remap(s):
    for old,new in sorted(mapping.items(),key=lambda kv:-len(kv[0])):s=s.replace(old,new)
    return s
cfg['classpath']=remap(cfg['classpath']);cfg['environment']={k:remap(v) for k,v in cfg['environment'].items()}
jvm=[]
for a in cfg['jvmArgs']:
    if a.startswith('-Ddynasty.') or a.startswith('-Xmx') or a.startswith('-XX:ActiveProcessorCount='):continue
    if a.startswith('-DlegacyClassPath.file='):
        path=root/'legacy-classpath.txt';path.write_text(remap(Path(a.split('=',1)[1]).read_text()));a='-DlegacyClassPath.file='+str(path)
    jvm.append(remap(a))
jvm+=['-Xmx2G','-XX:ActiveProcessorCount=2','-Ddynasty.secondaryArtQa=true',
      '-Ddynasty.secondaryArtQa.ids='+args.ids,'-Ddynasty.secondaryArtQa.output='+str(output),'-javaagent:'+str(REPO/'build/secondary-art-agent/quiet-window-agent.jar')]
if args.boss_audit:jvm+=['-Ddynasty.secondaryArtQa.bossAudit=true']
if args.boss_final:jvm+=['-Ddynasty.secondaryArtQa.bossFinal=true']
if args.boss_lifecycle:jvm+=['-Ddynasty.secondaryArtQa.bossLifecycle=true']
work=root/'host';work.mkdir();(work/'options.txt').write_text('soundCategory_master:0.0\nfullscreen:false\n')
(work/'config').mkdir();(work/'config/fml.toml').write_text('earlyWindowControl=false\n')
cfg.update(jvmArgs=jvm,directory=str(work));(root/'launch.json').write_text(json.dumps(cfg,indent=2)+'\n')
(output/'runtime-manifest.json').write_text(json.dumps({'run':args.run,'trees':manifest,'production':production},indent=2)+'\n')
log=(root/'client.log').open('w');child=subprocess.Popen([cfg['executable'],*jvm,'-cp',cfg['classpath'],cfg['main'],*cfg['args']],
    cwd=work,env=dict(os.environ,**cfg['environment']),stdout=log,stderr=subprocess.STDOUT)
print('Started native art QA:',child.pid,root,flush=True)
try:
    deadline=time.monotonic()+660
    while child.poll() is None:
        time.sleep(1)
        tail=(root/'client.log').read_text(errors='replace')[-16000:]
        if any(s in tail for s in ['Failed to create mod instance.','LoadingFailedException']):raise RuntimeError('Forge loading failed; inspect '+str(root/'client.log'))
        if time.monotonic()>deadline:raise RuntimeError('Native QA timed out')
    passed=output/'PASS.txt'
    if child.returncode!=0 or not passed.exists():raise RuntimeError('Native QA did not pass; inspect '+str(root/'client.log'))
    shutil.copy2(root/'client.log',output/'client.log')
    print(passed.read_text().splitlines()[-1],flush=True)
finally:
    if child.poll() is None:
        child.terminate()
        try:child.wait(timeout=10)
        except subprocess.TimeoutExpired:child.kill();child.wait()
    log.close()
