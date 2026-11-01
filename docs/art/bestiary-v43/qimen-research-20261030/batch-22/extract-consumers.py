from pathlib import Path
import zipfile,json,hashlib
B=Path(__file__).resolve().parent;rows=[]
with zipfile.ZipFile(B.parent/'batch-21/source-archives/klaxon-1.21.1-fixed.zip') as z:
 for n in z.namelist():
  if n.endswith('/'):continue
  p=n.split('/',1)[1]
  if not any(q in p for q in ['advanced_item_models','item_usage_lockout','ItemUsageLockoutTrigger.java']) and p!='src/main/resources/assets/klaxon/textures/item/empty.png':continue
  data=z.read(n);out=B/'sources/myriantics__klaxon'/p;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data);rows.append(dict(path=p,local=str(out.relative_to(B)),bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),git_blob_sha1=hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest(),read_ranges=[],status='EXTRACTED_NOT_REVIEWED'))
(B/'consumer-acquisition.json').write_text(json.dumps(dict(repo='myriantics/klaxon',commit='7d31931c1c94dc3d3e4209c6897bc77aad8c8432',archive='../batch-21/source-archives/klaxon-1.21.1-fixed.zip',files=rows,new_reference_credit=0),ensure_ascii=False,indent=2)+'\n')
for x in rows:
 if x['path'].endswith('.java'):print(x['path'],len((B/x['local']).read_text().splitlines()))
