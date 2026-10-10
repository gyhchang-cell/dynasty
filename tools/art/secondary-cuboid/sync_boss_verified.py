"""Copy only native-verified boss art into the primary tree; never edit gameplay/prompts."""
import hashlib,json,shutil,subprocess,zipfile
from pathlib import Path
from build_models import REPO

PRIMARY=Path('/Users/a15356015027/Desktop/dynasty')
OUT=REPO/'docs/art/cod6-cuboid-v1'
BASE_ART_COMMIT='7490bbac'
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
 accepted=json.loads((OUT/'accepted-runs.json').read_text())
 lifecycle=(json.loads((OUT/'lifecycle-validation.json').read_text()).get('acceptedRuns',{}) if (OUT/'lifecycle-validation.json').exists() else {})
 static=json.loads((OUT/'static-validation.json').read_text())
 baseline=json.loads((OUT/'source-ownership.json').read_text())
 previous=json.loads((OUT/'primary-sync.json').read_text()).get('files',{}) if (OUT/'primary-sync.json').exists() else {}
 prior_doc=(json.loads((PRIMARY/'docs/art/cod6-cuboid-v1/primary-sync.json').read_text()).get('docHashes',{})
            if (PRIMARY/'docs/art/cod6-cuboid-v1/primary-sync.json').exists() else {})
 if (OUT/'local-evidence-baseline.json').exists():
  local_doc=json.loads((OUT/'local-evidence-baseline.json').read_text())
  for path in ['docs/art/cod6-cuboid-v1/progress.json','docs/art/cod6-cuboid-v1/prompt-edits.json']:
   if path not in prior_doc and path in local_doc:prior_doc[path]=local_doc[path]
 files={};trees=[]
 for id,run in accepted.items():
  folder=REPO/'docs/art/secondary-cuboid-v1/native'/run
  assert (folder/'PASS.txt').read_text().splitlines()[-1].startswith('PASS:')
  runtime=json.loads((folder/'runtime-manifest.json').read_text());tree=runtime['trees'];trees.append(tree)
  for path,digest in runtime.get('production',{}).get('sources',{}).items():assert sha((REPO/path).read_bytes())==digest,(path,'native source changed')
  if runtime.get('production',{}).get('jarSha256'):assert sha((REPO/'build/libs/dynasty-1.4.0.jar').read_bytes())==runtime['production']['jarSha256'],'native build changed'
  entries={e['path']:e['sha256'] for e in tree[0]['files']}
  for path,digest in static[id]['resources'].items():
   assert sha((REPO/path).read_bytes())==digest
   assert entries[path.removeprefix('src/main/resources/')]==digest,(id,'current resource not tested')
   files[path]=digest
 for run in sorted(set(lifecycle.values())):
  folder=REPO/'docs/art/secondary-cuboid-v1/native'/run
  assert (folder/'PASS.txt').read_text().splitlines()[-1].startswith('PASS:')
  runtime=json.loads((folder/'runtime-manifest.json').read_text());trees.append(runtime['trees'])
  assert sha((REPO/'build/libs/dynasty-1.4.0.jar').read_bytes())==runtime['production']['jarSha256'],'lifecycle build changed'
  for path,digest in runtime['production']['sources'].items():assert sha((REPO/path).read_bytes())==digest,'lifecycle source changed'
 if lifecycle:
  assert set(lifecycle)==set(accepted),'Incomplete lifecycle coverage'
  assert all(v['stages']==7 for v in json.loads((OUT/'lifecycle-validation.json').read_text())['entities'].values())
 for path in ['src/main/java/com/dynasty/client/DynastyClientEvents.java','src/main/java/com/dynasty/client/BossCuboidRenderer.java','src/main/java/com/dynasty/client/BossCuboidAura.java']:
  files[path]=sha((REPO/path).read_bytes())
 # Runtime freezes Java output as well as assets. Check every changed renderer class.
 for tree in trees:
  entries={e['path']:e['sha256'] for e in tree[1]['files']}
  for f in (REPO/'build/classes/java/main/com/dynasty/client').glob('BossCuboid*.class'):
   key=str(f.relative_to(REPO/'build/classes/java/main'));assert sha(f.read_bytes())==entries[key],key
  key='com/dynasty/client/DynastyClientEvents.class'
  assert sha((REPO/'build/classes/java/main'/key).read_bytes())==entries[key]
 jar=REPO/'build/libs/dynasty-1.4.0.jar'
 assert sha(jar.read_bytes())==sha((REPO/'build/reobfJar/output.jar').read_bytes())
 with zipfile.ZipFile(jar) as z:
  assert not any('SecondaryArtClientQa' in n or 'LegacyCuboidExport' in n or 'QuietWindowAgent' in n for n in z.namelist())
  for path,digest in files.items():
   if path.startswith('src/main/resources/'):assert sha(z.read(path.removeprefix('src/main/resources/')))==digest
 # Guard all production destinations before any write, and recheck at the write.
 captured={}
 for path,digest in files.items():
  dest=PRIMARY/path;old=dest.read_bytes() if dest.exists() else None
  assert (sha(old) if old is not None else None) in {baseline.get(path),previous.get(path),digest},(path,'concurrent production edit')
  captured[path]=old
 for path in files:
  dest=PRIMARY/path;assert (dest.read_bytes() if dest.exists() else None)==captured[path]
  dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(REPO/path,dest)
 artifact=PRIMARY/'build/maintenance-artifacts'/('art-cod6-'+str(len(accepted))+('-lifecycle' if lifecycle else ''))/jar.name
 artifact.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(jar,artifact)
 record={'files':files,'acceptedNativeRuns':accepted,'acceptedLifecycleRuns':lifecycle,'artifact':str(artifact),'jarSha256':sha(jar.read_bytes()),
         'scope':'Frozen 23:33 source plus 31 secondary art and accepted boss art. Other primary concurrent changes are excluded.',
         'pending':'Natural skill clocks, actual gameplay anchors, AI movement, guard load and two humans; incomplete cod6 prompt clauses retained.'}
 (OUT/'primary-sync.json').write_text(json.dumps(record,indent=2)+'\n')
 # These two directories belong to this art task. Unknown changed primary bytes refuse overwrite.
 docfiles=[]
 for directory in ['docs/art/cod6-cuboid-v1','tools/art/secondary-cuboid']:
  docfiles.extend(f for f in (REPO/directory).rglob('*') if f.is_file() and '__pycache__' not in f.parts and f!=OUT/'primary-sync.json')
 for run in ['cod6-boss-baseline-01',*sorted(set(accepted.values())|set(lifecycle.values()))]:
  docfiles.extend(f for f in (REPO/'docs/art/secondary-cuboid-v1/native'/run).rglob('*') if f.is_file())
 for source in docfiles:
  path=str(source.relative_to(REPO));dest=PRIMARY/path;data=source.read_bytes()
  if dest.exists() and dest.read_bytes()!=data:
   old=dest.read_bytes();result=subprocess.run(['git','-C',str(PRIMARY),'show',BASE_ART_COMMIT+':'+path],capture_output=True)
   assert (result.returncode==0 and result.stdout==old) or sha(old)==prior_doc.get(path),(path,'concurrent evidence edit')
   assert dest.read_bytes()==old
  dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
 record['docHashes']={str(f.relative_to(REPO)):sha(f.read_bytes()) for f in docfiles if f!=OUT/'primary-sync.json'}
 (OUT/'primary-sync.json').write_text(json.dumps(record,indent=2)+'\n')
 shutil.copy2(OUT/'primary-sync.json',PRIMARY/'docs/art/cod6-cuboid-v1/primary-sync.json')
 print('Synced verified bosses:',','.join(accepted),'JAR',record['jarSha256'])
if __name__=='__main__':main()
