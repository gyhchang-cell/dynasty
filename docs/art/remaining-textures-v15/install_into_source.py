"""Install only v15 approved resource candidates into project source.

Requires exact original target hashes. Never writes jar, game instance, save,
registration code or any file outside the manifest's resources.
"""
from pathlib import Path
import hashlib,json,shutil,os,tempfile

D=Path(__file__).resolve().parent
ROOT=D.parents[2]
S=ROOT/'src/main/resources'
MAN=json.loads((D/'delivery-manifest.json').read_text())
SNAP=json.loads((D/'initial-source-hashes.json').read_text())
BACK=D/'deployment-backup'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

targets=[]
for entry in MAN['files']+MAN['models']:
 rel=entry.get('resource_path',entry.get('path'))
 src=D/'resource-pack'/rel
 target=S/rel
 assert src.is_file(),src
 assert rel.startswith('assets/dynasty/')
 assert '/textures/item/' in rel or '/textures/models/armor/' in rel or '/textures/block/bounty_board_' in rel or rel=='assets/dynasty/models/block/bounty_board.json' or '/models/item/' in rel
 expected=entry['sha256'];assert sha(src)==expected,(rel,'candidate modified')
 old=entry.get('source_sha256')
 if old is None:assert not target.exists(),(rel,'new target now exists')
 else:
  assert target.is_file(),(rel,'old target missing')
  assert sha(target)==old==SNAP[str(target.relative_to(ROOT))],(rel,'source conflict')
 targets.append((rel,src,target,old,expected))
assert len(targets)==420
assert len(set(r for r,*_ in targets))==len(targets)

# Back up the exact existing targets before touching any of them.
for rel,_,target,old,_ in targets:
 if old:
  backup=BACK/rel;backup.parent.mkdir(parents=True,exist_ok=True)
  if backup.exists():assert sha(backup)==old
  else:shutil.copy2(target,backup)
  assert sha(backup)==old

for rel,src,target,_,expected in targets:
 target.parent.mkdir(parents=True,exist_ok=True)
 fd,tmp=tempfile.mkstemp(prefix='.v15-',dir=target.parent)
 try:
  with os.fdopen(fd,'wb') as out:out.write(src.read_bytes())
  os.replace(tmp,target)
 finally:
  if os.path.exists(tmp):os.unlink(tmp)
 assert sha(target)==expected

receipt={'status':'installed_into_project_source','resource_files':len(targets),
 'png_files':len(MAN['files']),'json_models':len(MAN['models']),
 'source_root':str(S),'backup_root':str(BACK),'all_target_hashes_verified':True,
 'jar_rebuilt':False,'modpack_jar_updated':False,'game_instance_synced':False,
 'files':[{'resource_path':rel,'previous_sha256':old,'installed_sha256':new} for rel,_,_,old,new in targets]}
(D/'source-install-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(f"Installed {len(MAN['files'])} PNG and {len(MAN['models'])} JSON resources; source hashes verified.")
