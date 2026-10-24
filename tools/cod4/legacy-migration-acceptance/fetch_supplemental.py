"""Download pinned primary-source snapshots only; never run upstream code."""
from pathlib import Path
import json,subprocess,zipfile,io,hashlib,concurrent.futures,datetime
B=Path(__file__).resolve().parent;R=B.parents[2];O=R/'docs/cod4/audit-20261022/legacy-migration-acceptance';D=B/'.work/sources'
SPECS=[('FTBTeam/FTB-Quests','a74ee04bf80e7fba2c8475112a07ace4a4abd0a6','1.20.1-main'),('FTBTeam/FTB-Quests','dc94c46a6a9ae806fb5921159513448fcedc8816','1.21.1-main'),('FTBTeam/FTB-Quests','85b7652bd69f3bc4c03ba9ba24909ddea0605a53','1.12')]
def fetch(spec):
 repo,rev,label=spec;folder=D/(repo.replace('/','__')+'__'+label);meta=folder/'source.json'
 if meta.exists():return json.loads(meta.read_text())
 url=f'https://codeload.github.com/{repo}/zip/{rev}'
 try:
  data=subprocess.run(['curl','-fLsS','--max-time','90','--retry','1',url],capture_output=True,check=True).stdout;z=zipfile.ZipFile(io.BytesIO(data));n=0
  for info in z.infolist():
   rel=Path(*Path(info.filename).parts[1:])
   if info.is_dir() or '..' in rel.parts or not (rel.suffix=='.java' or rel.name.lower().startswith(('license','copying'))):continue
   p=folder/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(info));n+=1
  result={'repo':repo,'sha':rev,'branch_label_not_version_proof':label,'archive_url':url,'archive_sha256':hashlib.sha256(data).hexdigest(),'private_source':str(folder.relative_to(R)),'files_present':n,'provenance':'Pinned upstream archive, source only, no upstream code executed','fetched_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()};meta.write_text(json.dumps(result,indent=2));return result
 except Exception as e:return {'repo':repo,'revision':rev,'error':str(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:result=list(pool.map(fetch,SPECS))
records=json.loads((O/'sources.json').read_text());keys={(x['repo'],x['sha']) for x in records}
for x in result:
 if 'sha' in x and (x['repo'],x['sha']) not in keys:records.append(x)
(O/'sources.json').write_text(json.dumps(records,ensure_ascii=False,indent=2));(O/'supplemental-downloads.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False))
