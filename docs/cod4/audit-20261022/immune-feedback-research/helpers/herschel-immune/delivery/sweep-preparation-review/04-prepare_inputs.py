"""Create and hash one fresh private input snapshot. Never launches Java or a game."""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import re
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[3]
EVIDENCE=ROOT/'docs/cod4/audit-20261022/ecology-native-acceptance'
BUILD=ROOT/'build/cod4-ecology-native-20261028'
SOURCE=ROOT/'tools/cod4/ecology-acceptance/.work/static-handoff-20261024/world'

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()

def manifest(path):
    result={}
    for p in sorted(path.rglob('*')):
        if p.is_symlink():raise RuntimeError('No symlink inputs: '+str(p))
        if p.is_file():result[p.relative_to(path).as_posix()]=sha(p)
    return result

def prepare(label):
    if not re.fullmatch(r'inputs-\d{2,}',label):raise ValueError('Fresh inputs-NN label required')
    instance=BUILD/label/'host';out=EVIDENCE/label
    if instance.parent.exists() or out.exists():raise FileExistsError('Fresh input label required; no overwrites')
    expected=json.loads((ROOT/'docs/cod4/audit-20261022/ecology-acceptance/saved-world-checkpoint-manifest.json').read_text())
    assert Path(expected['checkpoint']).resolve()==SOURCE.parent.resolve()
    before=manifest(SOURCE)
    if before!=expected['files']:raise RuntimeError('Stopped own QA checkpoint no longer matches its receipt')
    verification=json.loads((EVIDENCE/'preparation-20261028/verification.json').read_text())
    helper=ROOT/verification['jar']
    if sha(helper)!=verification['jar_sha256']:raise RuntimeError('Private helper does not match inspected bytecode receipt')
    production=ROOT/'modpack'
    shared=production/'mods/dynasty-1.4.0.jar'
    if sha(shared)!='0e4fb4f244381ffe5589573e228c3bdf91ab6c2e55e29a6fcf7bfb95e760d9ba':raise RuntimeError('Review latest accepted shared artifact before preparing a new snapshot')
    instance.mkdir(parents=True);out.mkdir(parents=True)
    frozen_sources={}
    for folder in ['mods','config','defaultconfigs','resourcepacks']:
        source=production/folder
        if not source.exists():continue
        original=manifest(source)
        # copytree's default follows symlinks; manifest above explicitly rejects them first.
        shutil.copytree(source,instance/folder)
        if manifest(source)!=original or manifest(instance/folder)!=original:raise RuntimeError('Concurrent production change during snapshot: '+folder)
        frozen_sources.update({folder+'/'+k:v for k,v in original.items()})
    destination=instance/'saves/ecology-checkpoint'
    destination.parent.mkdir()
    subprocess.run(['cp','-cR',str(SOURCE),str(destination)],check=True)
    if manifest(SOURCE)!=before or manifest(destination)!=before:raise RuntimeError('Own checkpoint or copied world changed during cloning')
    shutil.copy2(helper,instance/'mods'/helper.name)
    (instance/'options.txt').write_text('soundCategory_master:0.0\npauseOnLostFocus:false\nlang:zh_cn\nguiScale:3\nmaxFps:30\nrenderDistance:3\nsimulationDistance:5\ntutorialStep:none\nresourcePacks:["vanilla","mod_resources","file/dynasty-quest-guides-v3.zip"]\n')
    fml=instance/'config/fml.toml'
    text=fml.read_text() if fml.exists() else ''
    text=re.sub(r'(?m)^earlyWindowControl\s*=.*$','earlyWindowControl=false',text)
    if not re.search(r'(?m)^earlyWindowControl\s*=',text):text+='\nearlyWindowControl=false\n'
    fml.write_text(text)
    (instance/'config/dynamic_fps.json').write_text(json.dumps({'enabled':False})+'\n')
    result={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'status':'PREPARED_INPUTS_ONLY_NOT_RUNTIME_READY','runtime_ready':False,
        'instance':str(instance),'evidence':str(out),'copied_world':str(destination),
        'source_own_qa_checkpoint':str(SOURCE),'source_original_user_world_touched':False,
        'checkpoint_manifest':str(ROOT/'docs/cod4/audit-20261022/ecology-acceptance/saved-world-checkpoint-manifest.json'),
        'world_clone_method':'APFS cp -cR; complete before/source-after/destination SHA256 equality',
        'world_file_count':len(before),'world_files_sha256':before,
        'production_snapshot_sha256':frozen_sources,'private_helper_sha256':sha(helper),
        'private_overrides':['options.txt silent/zh_cn/no pause/3 render/5 simulation','config/fml.toml earlyWindowControl=false','config/dynamic_fps.json enabled=false'],
        'production_mod_jars':len(list((production/'mods').glob('*.jar'))),
        'total_private_mod_jars':len(list((instance/'mods').glob('*.jar'))),
        'game_started':False,'world_data_edited':False,
        'pending':['Independent private bootstrap/watchdog review','Native client action driver and four bounded natural scenes','Validated launcher wired to external watchdog','Runtime native gate/birth/drop/save checks'],
        'preparer_sha256':sha(Path(__file__))}
    (out/'session-inputs.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status','instance','world_file_count','production_mod_jars','total_private_mod_jars','game_started']}))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('label');prepare(parser.parse_args().label)
