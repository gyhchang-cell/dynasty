"""Desktop-only installation with verified backup; never grants OS permissions."""
from pathlib import Path
from datetime import datetime
import hashlib
import json
import os
import plistlib
import signal
import stat
import subprocess
import time

ROOT=Path('/Users/a15356015027/Desktop/dynasty/tools/mc-macro')
SOURCE=ROOT/'.build/candidates/held-item-1102/app/mcPvPmax.app'
DESKTOP=Path('/Users/a15356015027/Desktop/mcPvPmax.app')
EXPECTED_OLD='b841ce415b53ac3eb3df2286d2a61e870c628dc15d94b6f07d3de6f79284130a'

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def verify(path):subprocess.run(['/usr/bin/codesign','--verify','--deep','--strict',str(path)],check=True)
def manifest(app):
    result={}
    for path in sorted(app.rglob('*')):
        key=str(path.relative_to(app))
        if path.is_symlink():result[key]={'link':os.readlink(path)}
        elif path.is_file():result[key]={'sha256':digest(path),'mode':stat.S_IMODE(path.stat().st_mode)}
    return result
def instances():
    found=[]
    for line in subprocess.check_output(['/bin/ps','-axo','pid=,comm='],text=True).splitlines():
        fields=line.strip().split(None,1)
        if len(fields)==2 and Path(fields[1]).name=='MCMacro':found.append((int(fields[0]),fields[1]))
    return found
def save(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')

def main():
    if SOURCE.is_symlink() or DESKTOP.is_symlink():raise SystemExit('Refusing symlink application')
    metadata=plistlib.loads((SOURCE/'Contents/Info.plist').read_bytes())
    assert metadata['CFBundleIdentifier']=='local.mc-macro.assistant'
    assert (metadata['CFBundleShortVersionString'],metadata['CFBundleVersion'])==('1.10.2','32')
    assert digest(DESKTOP/'Contents/MacOS/MCMacro')==EXPECTED_OLD,'Desktop changed'
    verification=json.loads((ROOT/'.build/candidates/held-item-1102/validation-exit.json').read_text())
    assert verification['exit_code']==0,'Tests did not pass'
    verify(SOURCE);verify(DESKTOP)
    backup=ROOT/'.build/backups'/('desktop-1102-'+datetime.now().strftime('%Y%m%d-%H%M%S'))
    backup.mkdir(exist_ok=False,parents=True)
    stage=backup/'staged.app';previous=backup/'mcPvPmax-1.10.1.app'
    expected=manifest(SOURCE);before=manifest(DESKTOP)
    dist_hash=digest(ROOT/'dist/mcPvPmax.app/Contents/MacOS/MCMacro')
    subprocess.run(['/usr/bin/ditto',str(SOURCE),str(stage)],check=True)
    verify(stage);assert manifest(stage)==expected
    for pid,path in instances():
        if path!=str(DESKTOP/'Contents/MacOS/MCMacro'):
            raise SystemExit('Unexpected running candidate; no replacement: '+path)
        os.kill(pid,signal.SIGTERM)
    for _ in range(50):
        if not instances():break
        time.sleep(0.1)
    if instances():raise SystemExit('App did not exit normally; not forcibly killed')
    assert manifest(DESKTOP)==before,'Desktop changed while staging'
    report={'time':datetime.now().astimezone().isoformat(),'version':'1.10.2','build':32,
            'source':str(SOURCE),'desktop':str(DESKTOP),'backup':str(previous),
            'old_sha256':EXPECTED_OLD,'new_sha256':digest(SOURCE/'Contents/MacOS/MCMacro'),
            'pure_visual':False,'uses_existing_java_reader':True,'dist_changed':False,
            'live_game_acceptance':False,'os_permissions_granted_by_installer':False,'status':'prepared'}
    save(backup/'install.json',report);save(backup/'previous-manifest.json',before)
    try:
        DESKTOP.rename(previous)
        assert manifest(previous)==before
        stage.rename(DESKTOP)
        verify(DESKTOP);assert manifest(DESKTOP)==expected
        assert digest(ROOT/'dist/mcPvPmax.app/Contents/MacOS/MCMacro')==dist_hash
        report['status']='installed_and_verified';report['bundle_entries_verified']=len(expected)
        save(backup/'install.json',report)
    except BaseException as error:
        if previous.exists():
            if DESKTOP.exists():DESKTOP.rename(backup/'failed-install.app')
            previous.rename(DESKTOP)
        report['status']='rolled_back';report['error']=str(error);save(backup/'install.json',report)
        raise
    save(ROOT/'research/held-item-20261104/install.json',report)
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':main()