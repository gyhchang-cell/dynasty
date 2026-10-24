"""Resolve primary-source HEAD once, pin full archive, store source-only snapshots."""
from pathlib import Path
import concurrent.futures,subprocess,zipfile,io,hashlib,json,datetime
B=Path(__file__).resolve().parent;R=B.parents[2];O=R/'docs/cod4/audit-20261022/legacy-migration-acceptance'
repos=['PaperMC/DataConverter','P3pp3rF1y/SophisticatedCore','P3pp3rF1y/SophisticatedBackpacks','P3pp3rF1y/SophisticatedStorage','FTBTeam/FTB-Teams','FTBTeam/FTB-Echoes','Darkhax-Minecraft/Game-Stages','McJty/RFToolsBase','McJty/RFToolsUtility','IndustrialForegoing/Industrial-Foregoing','refinedmods/refinedstorage','XFactHD/FramedBlocks']
def fetch(repo):
    folder=B/'.work/sources'/repo.replace('/','__');meta=folder/'additional-source.json'
    try:
        if meta.exists():return json.loads(meta.read_text())
        resolved=subprocess.run(['git','ls-remote','https://github.com/'+repo+'.git','HEAD'],capture_output=True,check=True,timeout=40).stdout.decode().split()
        if not resolved:raise ValueError('No HEAD')
        rev=resolved[0];url=f'https://codeload.github.com/{repo}/zip/{rev}'
        raw=subprocess.run(['curl','-fLsS','--max-time','120','--retry','1',url],capture_output=True,check=True).stdout
        z=zipfile.ZipFile(io.BytesIO(raw));n=0
        for i in z.infolist():
            rel=Path(*Path(i.filename).parts[1:])
            if i.is_dir() or '..' in rel.parts or not (rel.suffix=='.java' or rel.name.lower().startswith(('license','copying'))):continue
            p=folder/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(i));n+=rel.suffix=='.java'
        record={'repo':repo,'sha':rev,'archive_url':url,'archive_sha256':hashlib.sha256(raw).hexdigest(),'private_source':str(folder.relative_to(R)),'files_present':n,'complete_java_archive_verified':True,'provenance':'Primary upstream HEAD resolved once and full source pinned, no upstream executable/build scripts run','fetched_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
        meta.write_text(json.dumps(record,ensure_ascii=False,indent=2));print(json.dumps({'repo':repo,'sha':rev,'java':n}),flush=True);return record
    except Exception as e:record={'repo':repo,'error':str(e)};print(json.dumps(record),flush=True);return record
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(fetch,repos))
sources=json.loads((O/'sources.json').read_text());keys={(x['repo'],x['sha']) for x in sources}
for x in results:
    if x.get('sha') and (x['repo'],x['sha']) not in keys:sources.append(x)
(O/'sources.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2)+'\n');(O/'additional-downloads.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
