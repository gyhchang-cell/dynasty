"""Plan or run one reviewed foreground private JVM, under the owned-child watchdog.

Planning never launches Java. Running additionally requires a final reviewed
readiness receipt, final-file hashes, current helper, and a never-used run marker.
"""
from pathlib import Path
import argparse
import ctypes
import hashlib
import json
import os
import re
import subprocess
import uuid
import zipfile
from lint_mixin_boundary import inspect as inspect_mixin_boundary
from prepare_inputs import ROOT,EVIDENCE,BUILD,sha,manifest
from watchdog import run_owned

BASE=Path('/Users/a15356015027/Public/.minecraft')
PROFILE=BASE/'versions/Dynasty'
JAVA=Path('/Library/Java/JavaVirtualMachines/liberica-jdk-17.jdk/Contents/Home/bin/java')

def command(instance,output):
    version_path=PROFILE/'Dynasty.json';v=json.loads(version_path.read_text())
    features={'has_custom_resolution':True}
    def allowed(item):
        if 'rules' not in item:return True
        result=False
        for rule in item['rules']:
            system=rule.get('os',{})
            match=(not system.get('name') or system['name']=='osx') and (not system.get('arch') or system['arch'] in ['arm64','aarch64']) and all(features.get(k,False)==val for k,val in rule.get('features',{}).items())
            if 'version' in system:
                import platform
                match=match and bool(re.search(system['version'],platform.release()))
            if match:result=rule['action']=='allow'
        return result
    libraries=[]
    for entry in v['libraries']:
        if not allowed(entry):continue
        path=entry.get('downloads',{}).get('artifact',{}).get('path')
        if not path:
            group,name,ver,*classifier=entry['name'].split(':');path=group.replace('.','/')+'/'+name+'/'+ver+'/'+name+'-'+ver+('-'+classifier[0] if classifier else '')+'.jar'
        lib=BASE/'libraries'/path
        if not lib.is_file():raise FileNotFoundError(lib)
        libraries.append(str(lib))
    libraries.append(str(PROFILE/'Dynasty.jar'))
    player=bytearray(hashlib.md5(b'OfflinePlayer:EcologyQA').digest());player[6]=(player[6]&15)|48;player[8]=(player[8]&63)|128
    identity=str(uuid.UUID(bytes=bytes(player)))
    if identity!='817f74c6-1403-3509-b336-db7c734bf8f6':raise RuntimeError('Saved-player identity mismatch')
    variables={'natives_directory':str(PROFILE/'natives-macos-arm64'),'launcher_name':'COD4IsolatedEcologyQA','launcher_version':'1','classpath':os.pathsep.join(libraries),'library_directory':str(BASE/'libraries'),'classpath_separator':os.pathsep,'version_name':'Dynasty','primary_jar_name':'Dynasty.jar','auth_player_name':'EcologyQA','game_directory':str(instance),'assets_root':str(BASE/'assets'),'assets_index_name':v.get('assetIndex',{}).get('id','5'),'auth_uuid':identity.replace('-',''),'auth_access_token':'0','clientid':'0','auth_xuid':'0','user_type':'legacy','version_type':'release','resolution_width':'1440','resolution_height':'900'}
    def expand(value):
        result=re.sub(r'\$\{(.*?)\}',lambda m:variables[m[1]],value)
        if '${' in result:raise ValueError('Unresolved installed metadata variable')
        return result
    def args(group):
        result=[]
        for entry in v['arguments'][group]:
            if isinstance(entry,str):result.append(expand(entry))
            elif allowed(entry):result.extend(expand(s) for s in (entry['value'] if isinstance(entry['value'],list) else [entry['value']]))
        return result
    flags={'ecology.nativeqa.enabled':'true','ecology.nativeqa.projectRoot':str(ROOT),'ecology.nativeqa.instance':str(instance),'ecology.nativeqa.output':str(output),'ecology.nativeqa.openCopiedWorld':'true','ecology.nativeqa.worldFolder':'ecology-checkpoint','ecology.nativeqa.driveScenes':'true','ecology.nativegate.observe':'true','ecology.nativegate.output':str(output/'native-gates'),'ecology.bounded.observe':'true','ecology.bounded.output':str(output/'passive')}
    argv=[str(JAVA),'-Xmx4G','-XX:ActiveProcessorCount=2','-Dapple.awt.UIElement=true','-Dfml.earlyWindowControl=false']+['-D'+k+'='+val for k,val in flags.items()]+args('jvm')+[v['mainClass']]+args('game')
    return {'argv':argv,'instance':str(instance),'output':str(output),'offline_identity':identity,'installed_version_sha256':sha(version_path),'foreground_java_child':True,'runtime_ready':False,'does_not_prove_client_or_world_loaded':True}

def run_once(label,attempt='runtime-01'):
    if not re.fullmatch(r'runtime-(?:0[1-9]|[1-9][0-9]+)',attempt):raise ValueError('Explicit fresh runtime-NN attempt required')
    suffix='' if attempt=='runtime-01' else '-'+attempt
    receipt=EVIDENCE/label/('reviewed-launch-ready'+suffix+'.json')
    ready=json.loads(receipt.read_text())
    if ready.get('status')!='READY_FOR_ONE_BOUNDED_ECOLOGY_RUN':raise RuntimeError('Final action/launcher readiness not established')
    if ready.get('attempt','runtime-01')!=attempt:raise RuntimeError('Readiness is for a different single attempt')
    instance=BUILD/label/'host'
    if instance.resolve(strict=True)!=instance:raise RuntimeError('Instance path escape')
    # Readiness is a concrete engineering receipt, never inferred from compile success.
    expected=ready['final_private_files_sha256'];actual={}
    for folder in ['mods','config','defaultconfigs','resourcepacks']:
        if (instance/folder).exists():actual.update({folder+'/'+k:v for k,v in manifest(instance/folder).items()})
    actual['options.txt']=sha(instance/'options.txt')
    if expected!=actual:raise RuntimeError('Final reviewed private files changed')
    for relative,digest in ready['tool_sources_sha256'].items():
        path=ROOT/relative
        if not path.resolve().is_relative_to(ROOT/'tools/cod4/ecology-native-acceptance') or sha(path)!=digest:raise RuntimeError('Reviewed tool source changed')
    required_sources=['launch_once.py','watchdog.py','prepare_inputs.py','src/com/dynasty/ecologyqa/EcologyNativeQa.java','src/com/dynasty/ecologyqa/NativeSceneDriver.java','src/com/dynasty/ecologyqa/NativeCreatureGateObserver.java','src/com/dynasty/ecologyqa/observer/EcologyOpportunityObserver.java','src/com/dynasty/ecologyqa/mixin/QuietWindowMixin.java','src/com/dynasty/ecologyqa/mixin/NativeSpawnLoopMixin.java','src/com/dynasty/ecologyqa/mixin/NativeCategoryGateMixin.java','src/com/dynasty/ecologyqa/mixin/NativeLocalGateMixin.java','resources/ecology-native-qa.mixins.json','resources/pack.mcmeta','prepare_helper.py','helper-source-bindings.json','lint_mixin_boundary.py']
    for relative in required_sources:
        if 'tools/cod4/ecology-native-acceptance/'+relative not in ready['tool_sources_sha256']:raise RuntimeError('Incomplete reviewed source binding')
    review=ROOT/ready['review_report']
    if not review.resolve().is_relative_to(EVIDENCE.parent) or sha(review)!=ready['review_report_sha256']:raise RuntimeError('Review report changed')
    preparation=json.loads((EVIDENCE/'preparation-20261028/verification.json').read_text())
    helper=instance/'mods/dynasty-ecology-native-acceptance-1.4.0.jar'
    if sha(helper)!=preparation['jar_sha256']:raise RuntimeError('Inspected current helper not integrated into private instance')
    boundary=inspect_mixin_boundary(helper)
    if boundary['errors']:raise RuntimeError('Packaged Mixin namespace or inventory invalid')
    config_path='tools/cod4/ecology-native-acceptance/resources/ecology-native-qa.mixins.json'
    if preparation['source_sha256'].get(config_path)!=sha(ROOT/config_path):raise RuntimeError('Mixin config not bound to compiled receipt')
    with zipfile.ZipFile(helper) as archive:
        metadata_path='tools/cod4/ecology-native-acceptance/resources/pack.mcmeta'
        if preparation['source_sha256'].get(metadata_path)!=sha(ROOT/metadata_path) or archive.read('pack.mcmeta')!=(ROOT/metadata_path).read_bytes():raise RuntimeError('Private pack metadata not bound to build')
        if json.loads(archive.read('pack.mcmeta'))['pack']['pack_format']!=15:raise RuntimeError('Expected MC1.20.1 pack metadata')
        if archive.read('ecology-native-qa.mixins.json')!=(ROOT/config_path).read_bytes():raise RuntimeError('Packaged Mixin config differs from reviewed source')
        for relative in required_sources:
            if relative.endswith('.java'):
                entry=relative.removeprefix('src/').removesuffix('.java')+'.class'
                if entry not in archive.namelist():raise RuntimeError('Required compiled class missing: '+entry)
    for private in [instance/'saves',instance/'saves/ecology-checkpoint']:
        if private.resolve(strict=True)!=private:raise RuntimeError('Copied world path escape')
    if manifest(instance/'saves/ecology-checkpoint')!=ready['world_files_sha256']:raise RuntimeError('Copied pre-run world changed')
    for relative in required_sources:
        key='tools/cod4/ecology-native-acceptance/'+relative
        if relative.endswith('.java') and preparation['source_sha256'].get(key)!=sha(ROOT/key):raise RuntimeError('Current Java source not bound to inspected compiled helper')
    if sha(PROFILE/'Dynasty.json')!=ready['installed_version_sha256']:raise RuntimeError('Reviewed installed launch metadata changed')
    # Read display state only; do not wake, unlock or focus a window.
    cg=ctypes.CDLL('/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics');cg.CGMainDisplayID.restype=ctypes.c_uint32
    for name in ['CGDisplayIsActive','CGDisplayIsAsleep']:
        getattr(cg,name).argtypes=[ctypes.c_uint32];getattr(cg,name).restype=ctypes.c_uint32
    display=cg.CGMainDisplayID()
    if not cg.CGDisplayIsActive(display) or cg.CGDisplayIsAsleep(display):raise RuntimeError('Display inactive/asleep; no wake attempted, no game started')
    processes=subprocess.check_output(['ps','-axo','comm=,args='],text=True,errors='replace')
    if any('/bin/java ' in line and str(ROOT) in line and 'cod4-' in line for line in processes.splitlines()):raise RuntimeError('An existing private project JVM is present; no second launch')
    out=EVIDENCE/label/attempt
    if out.exists() or out.is_symlink() or out.parent.resolve(strict=True)!=out.parent:raise RuntimeError('Fresh internal runtime evidence leaf required')
    plan=command(instance,out)  # Resolve metadata/libraries before consuming the single attempt.
    marker=EVIDENCE/label/('execution-started'+suffix+'.json')
    with marker.open('x') as stream:json.dump({'readiness_sha256':sha(receipt),'one_attempt_only':True},stream)
    out.mkdir()
    if out.resolve(strict=True)!=out:raise RuntimeError('Runtime evidence leaf escaped private root')
    (out/'launch-plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    # Direct foreground JVM; no wrapper, shell, detach, PID attachment or auto retry.
    return run_owned(plan['argv'],instance=instance,evidence=out,
        startup_seconds=240,runtime_seconds=300,absolute_seconds=600,
        save_grace_seconds=60,term_grace_seconds=15)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['plan','run']);p.add_argument('label');p.add_argument('--attempt',default='runtime-01');a=p.parse_args()
    if not re.fullmatch(r'inputs-\d{2,}',a.label):raise ValueError('Input label required')
    if not re.fullmatch(r'runtime-(?:0[1-9]|[1-9][0-9]+)',a.attempt):raise ValueError('Explicit fresh runtime-NN attempt required')
    if a.mode=='run':print(json.dumps(run_once(a.label,a.attempt)))
    else:
        instance=BUILD/a.label/'host';out=EVIDENCE/a.label/a.attempt
        plan=command(instance,out)
        with (EVIDENCE/a.label/('launch-plan-not-ready.json' if a.attempt=='runtime-01' else 'launch-plan-'+a.attempt+'-not-ready.json')).open('x') as stream:json.dump(plan,stream,indent=2);stream.write('\n')
        print('Planned installed offline foreground JVM; no launch; final reviewed readiness still required')
