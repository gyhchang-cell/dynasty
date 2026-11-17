"""Desktop-only correction restoring native right input. Never activates combat."""
from pathlib import Path
from datetime import datetime
import hashlib
import importlib.util
import json
import os
import plistlib
import signal
import subprocess
import time

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'.build/candidates/native-right-1104'
SOURCE=OUT/'app/mcPvPmax.app'
DEST=Path('/Users/a15356015027/Desktop/mcPvPmax.app')
OLD='b5d4c27e0fef3e3a71e60fb8189956b0ee573ab4a0a222960589cdb6a21bdedb'

def main():
    spec=importlib.util.spec_from_file_location('helpers',ROOT/'research/held-item-20261104/install.py')
    h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
    if SOURCE.is_symlink() or DEST.is_symlink():raise SystemExit('Refusing symlink app')
    if h.digest(DEST/'Contents/MacOS/MCMacro')!=OLD:raise SystemExit('Desktop no longer matches 1.10.3')
    m=plistlib.loads((SOURCE/'Contents/Info.plist').read_bytes())
    if (m['CFBundleIdentifier'],m['CFBundleShortVersionString'],m['CFBundleVersion'])!=('local.mc-macro.assistant','1.10.4','34'):
        raise SystemExit('Unexpected candidate metadata')
    validation=json.loads((OUT/'validation-exit.json').read_text())
    if validation['exit_code']!=0 or not validation['event_handlers_tested']:raise SystemExit('Validation incomplete')
    for p,sha in json.loads((OUT/'verified-source.json').read_text()).items():
        if hashlib.sha256(Path(p).read_bytes()).hexdigest()!=sha:raise SystemExit('Changed since validation: '+p)
    h.verify(SOURCE);h.verify(DEST)
    expected=h.manifest(SOURCE);previous=h.manifest(DEST)
    backup=ROOT/'.build/backups'/('desktop-1104-'+datetime.now().strftime('%Y%m%d-%H%M%S'))
    backup.mkdir(parents=True,exist_ok=False)
    stage=backup/'staged.app';old_app=backup/'mcPvPmax-1.10.3-withdrawn.app'
    subprocess.run(['/usr/bin/ditto',str(SOURCE),str(stage)],check=True)
    h.verify(stage)
    if h.manifest(stage)!=expected:raise SystemExit('Staged bundle mismatch')
    dist_hash=h.digest(ROOT/'dist/mcPvPmax.app/Contents/MacOS/MCMacro')
    for pid,path in h.instances():
        if path!=str(DEST/'Contents/MacOS/MCMacro'):raise SystemExit('Unexpected running candidate')
        os.kill(pid,signal.SIGTERM)
    for _ in range(50):
        if not h.instances():break
        time.sleep(0.1)
    if h.instances():raise SystemExit('App did not exit normally; no forced kill')
    if h.manifest(DEST)!=previous:raise SystemExit('Desktop changed before replacement')
    record={'time':datetime.now().astimezone().isoformat(),'version':'1.10.4','build':34,
            'desktop':str(DEST),'source':str(SOURCE),'backup':str(old_app),
            'old_sha256':OLD,'new_sha256':h.digest(SOURCE/'Contents/MacOS/MCMacro'),
            'scope':'desktop only','native_right_restored':True,'pure_visual':False,
            'live_game_acceptance':False,'status':'prepared'}
    h.save(backup/'install.json',record);h.save(backup/'previous-manifest.json',previous)
    try:
        DEST.rename(old_app)
        if h.manifest(old_app)!=previous:raise RuntimeError('Backup verification failed')
        stage.rename(DEST);h.verify(DEST)
        if h.manifest(DEST)!=expected:raise RuntimeError('Installed files differ from candidate')
        if h.digest(ROOT/'dist/mcPvPmax.app/Contents/MacOS/MCMacro')!=dist_hash:raise RuntimeError('Unexpected dist modification')
        record['status']='installed_and_verified';record['bundle_entries']=len(expected)
        h.save(backup/'install.json',record)
    except BaseException as error:
        if old_app.exists():
            if DEST.exists():DEST.rename(backup/'failed.app')
            old_app.rename(DEST)
        record['status']='rolled_back';record['error']=str(error);h.save(backup/'install.json',record)
        raise
    h.save(ROOT/'research/native-right-1104/install.json',record)
    print(json.dumps(record,ensure_ascii=False,indent=2))

if __name__=='__main__':main()