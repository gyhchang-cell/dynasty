"""Install the tested attack-priority fix; never grant TCC or activate combat."""
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

ROOT=Path('/Users/a15356015027/Desktop/dynasty/tools/mc-macro')
OUT=ROOT/'.build/candidates/attack-priority-1103'
SOURCE=OUT/'app/mcPvPmax.app'
DEST=Path('/Users/a15356015027/Desktop/mcPvPmax.app')
OLD='c5caa7b20d8e4246ad56235d34d5fec755ebc82802dfb586e5a01ebc7e64ff52'

def main():
    spec=importlib.util.spec_from_file_location('install_helpers',ROOT/'research/held-item-20261104/install.py')
    helpers=importlib.util.module_from_spec(spec);spec.loader.exec_module(helpers)
    if SOURCE.is_symlink() or DEST.is_symlink():raise SystemExit('Refusing symlink app')
    if helpers.digest(DEST/'Contents/MacOS/MCMacro')!=OLD:raise SystemExit('Desktop differs from known 1.10.2')
    meta=plistlib.loads((SOURCE/'Contents/Info.plist').read_bytes())
    if (meta['CFBundleIdentifier'],meta['CFBundleShortVersionString'],meta['CFBundleVersion'])!=('local.mc-macro.assistant','1.10.3','33'):
        raise SystemExit('Wrong candidate metadata')
    if json.loads((OUT/'validation-exit.json').read_text())['exit_code']!=0:raise SystemExit('Tests failed')
    source_record=json.loads((OUT/'verified-source.json').read_text())
    for name,expected in source_record.items():
        if hashlib.sha256(Path(name).read_bytes()).hexdigest()!=expected:raise SystemExit('Changed since validation: '+name)
    helpers.verify(SOURCE);helpers.verify(DEST)
    expected=helpers.manifest(SOURCE);previous=helpers.manifest(DEST)
    backup=ROOT/'.build/backups'/('desktop-1103-'+datetime.now().strftime('%Y%m%d-%H%M%S'))
    backup.mkdir(parents=True,exist_ok=False)
    stage=backup/'staged.app';old_app=backup/'mcPvPmax-1.10.2.app'
    subprocess.run(['/usr/bin/ditto',str(SOURCE),str(stage)],check=True)
    helpers.verify(stage)
    if helpers.manifest(stage)!=expected:raise SystemExit('Staged files differ')
    dist_hash=helpers.digest(ROOT/'dist/mcPvPmax.app/Contents/MacOS/MCMacro')
    for pid,path in helpers.instances():
        if path!=str(DEST/'Contents/MacOS/MCMacro'):raise SystemExit('Unexpected running candidate: '+path)
        os.kill(pid,signal.SIGTERM)
    for _ in range(50):
        if not helpers.instances():break
        time.sleep(0.1)
    if helpers.instances():raise SystemExit('Desktop did not exit normally; no forced termination')
    if helpers.manifest(DEST)!=previous:raise SystemExit('Desktop changed before replacement')
    record={'time':datetime.now().astimezone().isoformat(),'version':'1.10.3','build':33,
            'desktop':str(DEST),'source':str(SOURCE),'backup':str(old_app),'old_sha256':OLD,
            'new_sha256':helpers.digest(SOURCE/'Contents/MacOS/MCMacro'),
            'scope':'desktop only','pure_visual':False,'live_game_acceptance':False,'status':'prepared'}
    helpers.save(backup/'install.json',record);helpers.save(backup/'previous-manifest.json',previous)
    try:
        DEST.rename(old_app)
        if helpers.manifest(old_app)!=previous:raise RuntimeError('Backup verification failed')
        stage.rename(DEST);helpers.verify(DEST)
        if helpers.manifest(DEST)!=expected:raise RuntimeError('Installed bundle differs')
        if helpers.digest(ROOT/'dist/mcPvPmax.app/Contents/MacOS/MCMacro')!=dist_hash:raise RuntimeError('Unexpected dist change')
        record['status']='installed_and_verified';record['bundle_entries']=len(expected)
        helpers.save(backup/'install.json',record)
    except BaseException as error:
        if old_app.exists():
            if DEST.exists():DEST.rename(backup/'failed.app')
            old_app.rename(DEST)
        record['status']='rolled_back';record['error']=str(error);helpers.save(backup/'install.json',record)
        raise
    helpers.save(ROOT/'research/attack-priority-1103/install.json',record)
    print(json.dumps(record,ensure_ascii=False,indent=2))

if __name__=='__main__':main()