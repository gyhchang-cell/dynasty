"""Prepare one isolated native TCP pair from a stopped, owned QA checkpoint; never launch Java."""
from pathlib import Path
import argparse, hashlib, json, re, shutil, subprocess, sys, uuid
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools/cod4/ecology-native-acceptance'))
from prepare_inputs import manifest,sha
from launch_once import command as installed_command
BASE=ROOT/'build/cod4-sweep-native-20261029'
PRODUCTION=ROOT/'modpack/mods/dynasty-1.4.0.jar'
EXPECTED='0e4fb4f244381ffe5589573e228c3bdf91ab6c2e55e29a6fcf7bfb95e760d9ba'

def identity(role):
    return str(uuid.UUID(bytes=hashlib.md5(('OfflinePlayer:Cod4Mob'+role.title()).encode()).digest(),version=3))

def prepare(run,driver):
    if not re.fullmatch(r'sweep[0-9]{2,25}',run):raise ValueError('Fresh sweepNN label of at most 30 characters required')
    if BASE.resolve(strict=True)!=BASE or ROOT.resolve(strict=True)!=ROOT:raise RuntimeError('Canonical project and private destination parent required')
    driver=driver.resolve(strict=True)
    if not driver.is_relative_to(BASE) or driver.suffix!='.jar':raise ValueError('Private built driver Jar required')
    if sha(PRODUCTION)!=EXPECTED:raise RuntimeError('Production changed; independently review current bundle before preparing')
    paths={
        'production':BASE/'current-bundle/dynasty-1.4.0.jar',
        'qa':BASE/'helper-build03/libs/dynasty-sweep-native-acceptance-2.0.jar',
        'quiet':ROOT/'build/cod4-ecology-native-20261028/inputs-01/host/mods/dynasty-ecology-native-acceptance-1.4.0.jar',
        'driver':driver,
    }
    receipts={
        'production':ROOT/'docs/cod4/audit-20261022/sweep-native-acceptance/current-bundle-private-integration.json',
        'qa':ROOT/'docs/cod4/audit-20261022/sweep-native-acceptance/coordinator-reobf03.json',
        'quiet':ROOT/'docs/cod4/audit-20261022/ecology-native-acceptance/inputs-01/helper-integration-compile20.json',
        'driver':ROOT/'docs/cod4/audit-20261022/sweep-native-acceptance/driver/coordinator-reobf01.json',
    }
    expected={
        'production':json.loads(receipts['production'].read_text())['private_jar_sha256'],
        'qa':json.loads(receipts['qa'].read_text())['jar_sha256'],
        'quiet':json.loads(receipts['quiet'].read_text())['to_helper_sha256'],
        'driver':json.loads(receipts['driver'].read_text())['jar_sha256'],
    }
    for key,digest in expected.items():
        if sha(paths[key])!=digest:raise RuntimeError('Private artifact changed: '+key)
    source=ROOT/'build/cod4-mob-network-20261023/run-12/host/saves/mob-qa-1793198631800'
    if source.resolve(strict=True)!=source or not(source/'level.dat').is_file():raise RuntimeError('Exact existing internal owned checkpoint required')
    processes=subprocess.check_output(['ps','-axo','comm=,args='],text=True,errors='replace')
    if any('/bin/java ' in line and str(ROOT) in line and 'cod4-' in line for line in processes.splitlines()):raise RuntimeError('Own QA JVM still present; checkpoint must be stopped')
    root=BASE/run
    if root.exists() or root.is_symlink():raise FileExistsError('Never overwrite prior prepared pair')
    source_before=manifest(source)
    production_folders={}
    for folder in ['mods','config','defaultconfigs','resourcepacks']:
        p=ROOT/'modpack'/folder
        if p.is_symlink() or (p.exists() and p.resolve(strict=True)!=p):raise RuntimeError('Canonical production folder required: '+folder)
        production_folders[folder]=manifest(p) if p.exists() else None
    root.mkdir();bridge=root/'bridge';bridge.mkdir()
    for role in ['host','peer']:
        instance=root/role;instance.mkdir();out=root/(role+'-evidence');out.mkdir()
        for folder in ['mods','config','defaultconfigs','resourcepacks']:
            p=ROOT/'modpack'/folder
            if p.exists():
                # Preserve (rather than dereference) any raced symlink; manifest rejects it.
                shutil.copytree(p,instance/folder,symlinks=True)
                if manifest(instance/folder)!=production_folders[folder] or manifest(p)!=production_folders[folder]:raise RuntimeError('Source/copy changed during snapshot: '+folder)
        for key,p in paths.items():
            dest=instance/'mods'/p.name
            if dest.exists() and key!='production':raise RuntimeError('Unexpected private mod collision: '+str(dest))
            shutil.copy2(p,dest)
        (instance/'options.txt').write_text('soundCategory_master:0.0\npauseOnLostFocus:false\nlang:zh_cn\nguiScale:3\nmaxFps:30\nrenderDistance:3\nsimulationDistance:5\ntutorialStep:none\nresourcePacks:["vanilla","mod_resources","file/dynasty-quest-guides-v3.zip"]\n')
        (instance/'config/dynamic_fps.json').write_text('{"enabled":false}\n')
        fml=instance/'config/fml.toml';text=fml.read_text() if fml.exists() else ''
        text=re.sub(r'(?m)^earlyWindowControl\s*=.*$','earlyWindowControl=false',text)
        if not re.search(r'(?m)^earlyWindowControl\s*=',text):text+='\nearlyWindowControl=false\n'
        fml.write_text(text)
        if role=='host':
            saves=instance/'saves';saves.mkdir()
            subprocess.run(['/bin/cp','-cR',str(source),str(saves/'sweep-world')],check=True)
            if manifest(saves/'sweep-world')!=source_before:raise RuntimeError('APFS own checkpoint copy differs')
    if manifest(source)!=source_before:raise RuntimeError('Read-only own checkpoint changed during preparation')
    for folder,before in production_folders.items():
        p=ROOT/'modpack'/folder
        if p.is_symlink() or (p.exists() and p.resolve(strict=True)!=p) or (manifest(p) if p.exists() else None)!=before:raise RuntimeError('Read-only production folder changed: '+folder)
    plan={'run':run,'private_root':str(root),'host_instance':str(root/'host'),'peer_instance':str(root/'peer'),'host_output':str(root/'host-evidence'),'peer_output':str(root/'peer-evidence'),'host_uuid':identity('host'),'peer_uuid':identity('peer'),'saved_world':'sweep-world','bootstrap_existing_world':True,'qa_sha256':sha(paths['qa']),'driver_sha256':sha(driver),'production_sha256':sha(paths['production'])}
    (bridge/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    (root/'sweep-driver-private.json').write_text(json.dumps({'run':run,'plan_sha256':sha(bridge/'plan.json')},indent=2)+'\n')
    receipt={'status':'PREPARED_ONLY_NOT_REVIEWED_OR_RUNTIME_READY','run':run,'source_own_world':str(source),'source_files_sha256':source_before,'source_unchanged':True,'human_world_touched':False,'production_unchanged':True,'production_source_folders_sha256':production_folders,'artifact_sha256':{k:sha(p) for k,p in paths.items()},'input_files_sha256':{},'argv':{},'game_started':False,'source_receipts_sha256':{str(p.relative_to(ROOT)):sha(p) for p in receipts.values()},'preparation_sources_sha256':{str(p.relative_to(ROOT)):sha(p) for p in [Path(__file__).resolve(),ROOT/'tools/cod4/ecology-native-acceptance/launch_once.py',ROOT/'tools/cod4/ecology-native-acceptance/prepare_inputs.py']},'pending':['Independent driver source/reobf review','Exact final launch-source/artifact/input/world bindings','Owned bounded two-process controller and normal stop/save evidence']}
    for role in ['host','peer']:
        instance=root/role;out=root/(role+'-evidence');original=installed_command(instance,out)
        argv=[s for s in original['argv'] if not s.startswith('-Decology.')]
        for flag,value in [('--username','Cod4Mob'+role.title()),('--uuid',identity(role).replace('-',''))]:
            if argv.count(flag)!=1:raise RuntimeError('Installed metadata does not have exact '+flag)
            argv[argv.index(flag)+1]=value
        props={'dynasty.sweepqa.enabled':'true','dynasty.sweepqa.instance':str(instance),'dynasty.sweepqa.output':str(out),'dynasty.sweepdriver.enabled':'true','dynasty.sweepdriver.role':role,'dynasty.sweepdriver.bridge':str(bridge),'ecology.nativeqa.enabled':'false','ecology.nativegate.observe':'false','ecology.bounded.observe':'false'}
        argv=argv[:1]+['-D'+k+'='+v for k,v in props.items()]+argv[1:]
        receipt['argv'][role]=argv
        receipt.setdefault('installed_metadata_sha256',{})[role]=original['installed_version_sha256']
        receipt['input_files_sha256'][role]={folder+'/'+k:v for folder in ['mods','config','defaultconfigs','resourcepacks'] for k,v in manifest(instance/folder).items()}
        receipt['input_files_sha256'][role]['options.txt']=sha(instance/'options.txt')
    (root/'prepared-inputs.json').write_text(json.dumps(receipt,indent=2)+'\n')
    return {'status':receipt['status'],'root':str(root),'plan_sha256':sha(bridge/'plan.json'),'game_started':False}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('run');p.add_argument('driver',type=Path);a=p.parse_args();print(json.dumps(prepare(a.run,a.driver)))
