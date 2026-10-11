"""Snapshot actual compiled resources/classes and run one silent native Forge client."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

REPO=Path(__file__).resolve().parents[3]
parser=argparse.ArgumentParser();parser.add_argument('run');parser.add_argument('--batch',choices=['first','floaters','mechanicals','mechanical-details','beasts-priest','beast-details','armies-tree','army-details','shield-skull-guard-scout','shield-skull-details','corpse-ghost-palanquin-flag','ape-dao','ape-wall','child-paper','elites','art-load'],default='first');parser.add_argument('--only-index',type=int,default=-1);args=parser.parse_args()
assert args.run and all(c.isalnum() or c in '-_' for c in args.run)
root=REPO/'build/cod2-voxel-client'/args.run;root.mkdir(parents=True,exist_ok=False)
out=REPO/'docs/art/cod2-voxel-v1/native'/args.run;out.mkdir(parents=True,exist_ok=False)
config=json.loads((REPO/'build/cod2-voxel-client/launch.json').read_text())
# A failed QA compilation must never launch a previous successful class set.
qa_source=REPO/'tools/art/cod2-voxel/qa'
qa_classes=REPO/'build/cod2-voxel-build/classes/java/cod2VoxelQa'
for source in qa_source.rglob('*.java'):
    compiled=qa_classes/source.relative_to(qa_source).with_suffix('.class')
    assert compiled.exists() and compiled.stat().st_mtime>=source.stat().st_mtime,'Stale/uncompiled optional QA: '+str(source)
from resource_paths import resource_paths
for name in json.loads((REPO/'tools/art/cod2-voxel/owned-models.json').read_text())['ids']:
    for source in resource_paths(name):
        compiled=REPO/'build/cod2-voxel-build/resources/main'/source.relative_to(REPO/'src/main/resources')
        assert compiled.read_bytes()==source.read_bytes(),'Authored resource not prepared: '+str(source)
mapping={};manifest=[]
for index,entry in enumerate(config['environment']['MOD_CLASSES'].split(os.pathsep)):
    source=Path(entry.split('%%',1)[1]);target=root/'runtime'/str(index)
    source.relative_to(REPO/'build/cod2-voxel-build')
    if source.exists():shutil.copytree(source,target)
    else:target.mkdir(parents=True)
    mapping[str(source)]=str(target)
    hashes=[]
    for path in sorted(target.rglob('*')):
        if path.is_file():
            digest=hashlib.sha256(path.read_bytes()).hexdigest()
            assert digest==hashlib.sha256((source/path.relative_to(target)).read_bytes()).hexdigest(), 'Concurrent build'
            hashes.append(dict(path=str(path.relative_to(target)),sha256=digest))
    manifest.append(dict(source=str(source),runtime=str(target),files=hashes))
def remap(value):
    for old,new in sorted(mapping.items(),key=lambda pair:-len(pair[0])):value=value.replace(old,new)
    return value
config['classpath']=remap(config['classpath']);config['environment']={k:remap(v) for k,v in config['environment'].items()}
jvm=[]
for arg in config['jvmArgs']:
    if arg.startswith('-Ddynasty.cod2VoxelQa.output='):continue
    if arg.startswith('-DlegacyClassPath.file='):
        dest=root/'legacy-classpath.txt';dest.write_text(remap(Path(arg.split('=',1)[1]).read_text()));arg='-DlegacyClassPath.file='+str(dest)
    jvm.append(remap(arg))
jvm.append('-Ddynasty.cod2VoxelQa.output='+str(out))
jvm.append('-Ddynasty.cod2VoxelQa.batch='+args.batch)
if args.only_index>=0:jvm.append('-Ddynasty.cod2VoxelQa.onlyIndex='+str(args.only_index))
work=root/'game';work.mkdir();(work/'options.txt').write_text('soundCategory_master:0.0\n')
(out/'runtime-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
config.update(jvmArgs=jvm,directory=str(work));(root/'launch.json').write_text(json.dumps(config,indent=2)+'\n')
log=(root/'client.log').open('w');process=subprocess.Popen([config['executable'],*jvm,'-cp',config['classpath'],config['main'],*config['args']],cwd=work,
    env=dict(os.environ,**config['environment']),stdout=log,stderr=subprocess.STDOUT)
print('Actual Forge client:',process.pid,root,flush=True)
try:
    deadline=time.monotonic()+660
    while process.poll() is None:
        time.sleep(1)
        text=(root/'client.log').read_text(errors='replace')[-12000:]
        if any(v in text for v in ['Failed to create mod instance.','LoadingFailedException',"Can't find a primary monitor"]):raise RuntimeError('Forge loading failed; see actual client log')
        if time.monotonic()>deadline:raise RuntimeError('Native client timed out')
    shutil.copy2(root/'client.log',out/'client.log')
    if process.returncode!=0 or not (out/'PASS.txt').exists():raise RuntimeError('Native QA failed; inspect '+str(root/'client.log'))
    print((out/'PASS.txt').read_text(),flush=True)
finally:
    if process.poll() is None:
        process.terminate()
        try:process.wait(timeout=10)
        except subprocess.TimeoutExpired:process.kill();process.wait()
    log.close()
    shutil.copy2(root/'client.log',out/'client.log')
