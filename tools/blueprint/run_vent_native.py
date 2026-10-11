"""One silent actual Forge client; snapshot classes/resources, never use the user's saves."""
import argparse,hashlib,json,os,shutil,subprocess,time
from pathlib import Path
REPO=Path(__file__).resolve().parents[2]
parser=argparse.ArgumentParser();parser.add_argument('run');args=parser.parse_args()
assert args.run and all(c.isalnum() or c in '-_' for c in args.run)
root=REPO/'build/cod2-vent-client'/args.run;root.mkdir(parents=True,exist_ok=False)
out=REPO/'docs/art/cod2-vents-v1/native'/args.run;out.mkdir(parents=True,exist_ok=False)
config=json.loads((REPO/'build/cod2-vent-client/launch.json').read_text())
build=REPO/'build/cod2-vents-build'
qa=REPO/'tools/blueprint/vent-qa'
for source in qa.rglob('*.java'):
    compiled=build/'classes/java/cod2VentQa'/source.relative_to(qa).with_suffix('.class')
    assert compiled.exists() and compiled.stat().st_mtime>=source.stat().st_mtime,'Stale optional QA: '+str(source)
validation=json.loads((REPO/'docs/art/cod2-vents-v1/resource-validation.json').read_text())
for name,digest in validation['resource_sha256'].items():
    source=REPO/name
    assert hashlib.sha256(source.read_bytes()).hexdigest()==digest,'Authored resource changed: '+name
    if name.startswith('src/main/resources/'):
        assert (build/'resources/main'/source.relative_to(REPO/'src/main/resources')).read_bytes()==source.read_bytes(),'Unprepared resource: '+name
mapping={};manifest=[]
for index,entry in enumerate(config['environment']['MOD_CLASSES'].split(os.pathsep)):
    source=Path(entry.split('%%',1)[1]);source.relative_to(build);target=root/'runtime'/str(index)
    if source.exists():shutil.copytree(source,target)
    else:target.mkdir(parents=True)
    mapping[str(source)]=str(target);hashes=[]
    for path in sorted(target.rglob('*')):
        if path.is_file():
            digest=hashlib.sha256(path.read_bytes()).hexdigest()
            assert digest==hashlib.sha256((source/path.relative_to(target)).read_bytes()).hexdigest(),'Concurrent build'
            hashes.append(dict(path=str(path.relative_to(target)),sha256=digest))
    manifest.append(dict(source=str(source),runtime=str(target),files=hashes))
def remap(value):
    for old,new in sorted(mapping.items(),key=lambda pair:-len(pair[0])):value=value.replace(old,new)
    return value
config['classpath']=remap(config['classpath']);config['environment']={k:remap(v) for k,v in config['environment'].items()}
jvm=[]
for arg in config['jvmArgs']:
    if arg.startswith('-Ddynasty.cod2VentQa.output='):continue
    if arg.startswith('-DlegacyClassPath.file='):
        dest=root/'legacy-classpath.txt';dest.write_text(remap(Path(arg.split('=',1)[1]).read_text()));arg='-DlegacyClassPath.file='+str(dest)
    jvm.append(remap(arg))
jvm.append('-Ddynasty.cod2VentQa.output='+str(out))
work=root/'game';work.mkdir();(work/'options.txt').write_text('soundCategory_master:0.0\n')
(out/'runtime-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
config.update(jvmArgs=jvm,directory=str(work));(root/'launch.json').write_text(json.dumps(config,indent=2)+'\n')
log=(root/'client.log').open('w');process=subprocess.Popen([config['executable'],*jvm,'-cp',config['classpath'],config['main'],*config['args']],cwd=work,
    env=dict(os.environ,**config['environment']),stdout=log,stderr=subprocess.STDOUT)
(root/'owned-pid.txt').write_text(str(process.pid)+'\n');print('Actual Forge client:',process.pid,root,flush=True)
try:
    deadline=time.monotonic()+660
    while process.poll() is None:
        time.sleep(1)
        tail=(root/'client.log').read_text(errors='replace')[-12000:]
        if any(v in tail for v in ['Failed to create mod instance.','Failed to register automatic subscribers.','LoadingFailedException',"Can't find a primary monitor"]):raise RuntimeError('Actual Forge loading failed; see log')
        if time.monotonic()>deadline:raise RuntimeError('Actual client timed out')
    if process.returncode!=0 or not (out/'PASS.txt').exists():raise RuntimeError('Native QA failed; inspect '+str(root/'client.log'))
    print((out/'PASS.txt').read_text(),flush=True)
finally:
    if process.poll() is None:
        process.terminate()
        try:process.wait(timeout=10)
        except subprocess.TimeoutExpired:process.kill();process.wait()
    log.close();shutil.copy2(root/'client.log',out/'client.log')
