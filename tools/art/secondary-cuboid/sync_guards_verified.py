"""Publish only this locally verified guard pose/evidence; protect concurrent primary files."""
import hashlib,json,shutil,subprocess,sys
from pathlib import Path
from verify_guards import REPO,OUT,main as verify
PRIMARY=Path('/Users/a15356015027/Desktop/dynasty')
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
 verify();proof=json.loads((OUT/'validation.json').read_text());ownership=json.loads((OUT/'source-ownership.json').read_text())
 model='src/main/java/com/dynasty/client/character/DynastyCharacterModel.java'
 items=[REPO/model]
 for rel in ['docs/art/secondary-cuboid-v1/README.md','docs/art/secondary-cuboid-v1/progress.json','docs/art/cod6-cuboid-v1/README.md','docs/art/cod6-cuboid-v1/progress.json','docs/art/cod6-cuboid-v1/prompt-edits.json','tools/art/secondary-cuboid/run_native.py','tools/art/secondary-cuboid/verify_guards.py','tools/art/secondary-cuboid/sync_guards_verified.py','tools/art/secondary-cuboid/qa/com/dynasty/client/GuardArtClientQa.java']:
  items.append(REPO/rel)
 items.extend(p for p in OUT.iterdir() if p.is_file() and p.name!='primary-sync.json')
 for run in ['guard-equipped-baseline-02',proof['acceptedNative']]:items.extend(p for p in (OUT/'native'/run).rglob('*') if p.is_file() and p.name!='client.log')
 before={}
 for source in items:
  rel=str(source.relative_to(REPO));dest=PRIMARY/rel;old=dest.read_bytes() if dest.exists() else None;data=source.read_bytes()
  if old is not None and old!=data:
   if rel==model:assert sha(old)==ownership['primary'][model],'Concurrent guard model change'
   else:
    prior=subprocess.run(['git','-C',str(PRIMARY),'show','98f8bb68:'+rel],capture_output=True)
    assert prior.returncode==0 and prior.stdout==old,('Concurrent evidence change',rel)
  before[rel]=old
 for source in items:
  rel=str(source.relative_to(REPO));dest=PRIMARY/rel;assert (dest.read_bytes() if dest.exists() else None)==before[rel],('Changed while copying',rel)
  dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest)
 artifact=PRIMARY/'build/maintenance-artifacts/art-guard-18/dynasty-1.4.0.jar';artifact.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(REPO/'build/libs/dynasty-1.4.0.jar',artifact);assert sha(artifact.read_bytes())==proof['production']['jarSha256']
 record={'files':{str(p.relative_to(REPO)):sha(p.read_bytes()) for p in items},'artifact':str(artifact),'artifactSha256':sha(artifact.read_bytes()),'nativeRun':proof['acceptedNative'],'scope':'Frozen 23:33 source, unchanged31 secondary and5 boss art, guard crossbow pose only. No server/gameplay/other developer edits copied.'}
 (OUT/'primary-sync.json').write_text(json.dumps(record,indent=2)+'\n');shutil.copy2(OUT/'primary-sync.json',PRIMARY/'docs/art/guard-art-v1/primary-sync.json')
 # Keep the shared evidence hashes current without altering the earlier Boss acceptance/JAR identity.
 p=PRIMARY/'docs/art/cod6-cuboid-v1/primary-sync.json';old=p.read_bytes();j=json.loads(old)
 for path,digest in record['files'].items():
  if path.startswith('tools/art/secondary-cuboid/') or path.startswith('docs/art/cod6-cuboid-v1/'):
   j.setdefault('docHashes',{})[path]=digest
 j['laterGuardEvidence']='docs/art/guard-art-v1/validation.json';j['laterGuardArtifact']=str(artifact)
 assert p.read_bytes()==old
 text=json.dumps(j,indent=2)+'\n';p.write_text(text);(REPO/'docs/art/cod6-cuboid-v1/primary-sync.json').write_text(text)
 print('Guard pose and exact evidence synced to local main; artifact',artifact)
if __name__=='__main__':main()
