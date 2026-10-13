"""Backup and sync only verified Dynasty quest definitions and our GUI pack.

Never launches Java, edits options, creates a missing profile, or touches saves.
An edited launcher configuration is rejected before any of its files are written.
"""
import argparse
import hashlib
import json
import os
import tempfile
import zipfile
from datetime import datetime,timezone
from pathlib import Path
from quest_journey import DOC,ROOT,known_removed,validate_forward
from quest_story import build_book,encode,OUT

PACK='dynasty-quest-guides-v3.zip'

def digest(data):return hashlib.sha256(data).hexdigest()

def check_baseline(target,expected):
    actual={p.relative_to(target).as_posix():digest(p.read_bytes()) for p in target.rglob('*.snbt')}
    assert actual==expected,'Launcher definitions changed; preserve and inspect: '+str(target)

def atomic_write(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    fd,name=tempfile.mkstemp(prefix='.dynasty-quest-',dir=path.parent)
    try:
        with os.fdopen(fd,'wb') as stream:stream.write(data)
        os.replace(name,path)
    finally:
        if os.path.exists(name):os.unlink(name)

def sync(round_number):
    book=build_book()
    validate_forward(book,json.loads((DOC/'last-deployed-book.json').read_text()))
    for c in book:
        assert (OUT/'chapters'/(c['file']+'.snbt')).read_text()==encode(c),'Generated source is stale'
    tests=(DOC/f'round{round_number}-tests.txt').read_text()
    validation=(DOC/f'round{round_number}-validation.txt').read_text()
    assert '\nOK\n' in tests and '任务书自检：通过' in validation,'Complete round checks before deployment'
    prior=json.loads((DOC/'DELIVERY.json').read_text())
    prefix='modpack/config/ftbquests/quests/'
    expected={k[len(prefix):]:v for k,v in prior['source_sha256'].items() if k.startswith(prefix)}
    assert len(expected)==22,'Need the complete previous 20 chapter / 2 settings manifest'
    pack_key='modpack/resourcepacks/'+PACK
    old_pack=prior['source_sha256'][pack_key]
    destinations=json.loads((DOC/'launcher-sync.json').read_text())['targets']
    plans=[];skipped=[]
    payload={p.relative_to(OUT).as_posix():p.read_bytes() for p in OUT.rglob('*.snbt')}
    pack=(ROOT/pack_key).read_bytes()
    for entry in destinations:
        target=Path(entry['target']);profile=target.parents[2]
        if not target.is_dir():skipped.append(str(target));continue
        assert '愚者' not in str(profile),'Read-only reference profile'
        check_baseline(target,expected)
        resource=profile/'resourcepacks'/PACK
        assert resource.is_file() and digest(resource.read_bytes())==old_pack,'GUI pack changed in '+str(profile)
        options=profile/'options.txt'
        plans.append((target,resource,options,options.read_bytes() if options.exists() else None))
    backup=DOC/f'launcher-config-before-round{round_number}.zip'
    assert not backup.exists(),'Never overwrite an earlier launcher backup'
    # Every live target is preflighted before making a fresh archive or mutation.
    with zipfile.ZipFile(backup,'x',zipfile.ZIP_DEFLATED) as z:
        for target,resource,options,_ in plans:
            for p in list(target.rglob('*.snbt'))+[resource]+([options] if options.exists() else []):
                z.write(p,str(p).lstrip('/'))
    report={'timestamp':datetime.now(timezone.utc).isoformat(),'round':round_number,
            'backup':str(backup),'targets':[],'skipped_missing_targets':skipped,
            'scope':'Quest SNBT and existing GUI pack only; options, Fool world and saves untouched'}
    for target,resource,options,old_options in plans:
        check_baseline(target,expected)
        assert digest(resource.read_bytes())==old_pack,'Pack changed after preflight'
        changed=[]
        for name,data in payload.items():
            p=target/name
            if not p.exists() or p.read_bytes()!=data:atomic_write(p,data);changed.append(name)
        removed=[]
        for name in set(expected)-set(payload):
            assert name.startswith('chapters/') and Path(name).name in known_removed(),'Unknown chapter removal'
            (target/name).unlink();removed.append(name)
        if resource.read_bytes()!=pack:atomic_write(resource,pack)
        assert {p.relative_to(target).as_posix():digest(p.read_bytes()) for p in target.rglob('*.snbt')}=={n:digest(v) for n,v in payload.items()}
        assert resource.read_bytes()==pack
        assert (options.read_bytes() if options.exists() else None)==old_options,'Unrelated options must stay byte-identical'
        report['targets'].append({'target':str(target),'changed_files':changed,'merged_chapters_removed':removed,
                                 'pack':str(resource),'options_unchanged':True})
    (DOC/f'launcher-sync-round{round_number}.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print('Backed up and verified',len(plans),'Dynasty configurations; options unchanged')
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--round',type=int,required=True)
    sync(parser.parse_args().round)
