from pathlib import Path
import zipfile,hashlib,json,datetime
B=Path(__file__).resolve().parent;R=B.parent;archive=R/'batch-08/source-archives/forge-47.3.0-sources.zip';rows=[]
with zipfile.ZipFile(archive) as z:
 for p in ['net/minecraftforge/common/extensions/IForgeFriendlyByteBuf.java','net/minecraftforge/fluids/FluidStack.java','net/minecraftforge/fluids/capability/templates/FluidHandlerItemStack.java']:
  raw=z.read(p);f=B/'framework/forge-47.3.0'/p;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(raw);rows.append(dict(id=Path(p).stem,entry=p,local=str(f.relative_to(B)),sha256=hashlib.sha256(raw).hexdigest(),lines=len(raw.splitlines()),reviewed_ranges=[],status='EXTRACTED_NOT_REVIEWED'))
(B/'framework-consumers.json').write_text(json.dumps(dict(saved_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),archive=str(archive.relative_to(B.parent)),archive_relative_to='research-root',source_sha1=hashlib.sha1(archive.read_bytes()).hexdigest(),source_url='https://maven.minecraftforge.net/net/minecraftforge/forge/1.20.1-47.3.0/forge-1.20.1-47.3.0-sources.jar',files=rows,new_reference_credit=0),ensure_ascii=False,indent=2)+'\n');print([(r['id'],r['lines']) for r in rows])
