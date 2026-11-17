"""Fill partial item-only snapshots at EXACT original commits. Source text only."""
from pathlib import Path
import concurrent.futures,subprocess,zipfile,io,hashlib,json,datetime
B=Path(__file__).resolve().parent;R=B.parents[2];O=R/'docs/cod4/audit-20261022/legacy-migration-acceptance'
sources=json.loads((O/'sources.json').read_text());todo=[x for x in sources if 'item-use-references' in x.get('original_cache','') and not x.get('complete_java_archive_verified')]
def fill(x):
    root=R/x['private_source'];url=f'https://codeload.github.com/{x["repo"]}/zip/{x["sha"]}'
    try:
        data=subprocess.run(['curl','-fLsS','--max-time','120','--retry','1',url],capture_output=True,check=True).stdout
        z=zipfile.ZipFile(io.BytesIO(data));files=[];missing=[]
        for i in z.infolist():
            rel=Path(*Path(i.filename).parts[1:])
            if i.is_dir() or '..' in rel.parts or not (rel.suffix=='.java' or rel.name.lower().startswith(('license','copying'))):continue
            p=root/rel;content=z.read(i)
            if p.exists():
                if p.read_bytes()!=content:raise ValueError('Pinned file mismatch; not replacing '+str(rel))
            else:missing.append((p,content))
            files.append(str(rel))
        for p,content in missing:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(content)
        record={'repo':x['repo'],'sha':x['sha'],'archive_url':url,'complete_java_archive_sha256':hashlib.sha256(data).hexdigest(),'complete_java_archive_verified':True,'complete_java_files':sum(p.endswith('.java') for p in files),'added_source_files':len(missing),'completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files_manifest_sha256':hashlib.sha256('\n'.join(sorted(files)).encode()).hexdigest()}
        print(json.dumps({k:record[k] for k in ['repo','complete_java_files','added_source_files']}),flush=True);return record
    except Exception as e:
        record={'repo':x['repo'],'sha':x['sha'],'error':str(e)};print(json.dumps(record),flush=True);return record
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(fill,todo))
by={(x['repo'],x['sha']):x for x in sources}
for result in results:
    if result.get('complete_java_archive_verified'):by[(result['repo'],result['sha'])].update(result)
(O/'sources.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2)+'\n')
(O/'completed-pinned-downloads.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'completed':sum(x.get('complete_java_archive_verified',False) for x in results),'failed':sum('error' in x for x in results),'research_credit':0}),flush=True)
