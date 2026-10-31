from pathlib import Path
import zipfile,json,hashlib
B=Path(__file__).resolve().parent
names={'gradle.properties','fabric.mod.json','KlaxonItems.java','KlaxonItemProperties.java','KlaxonEntityTypes.java','KlaxonDataComponentTypes.java','KlaxonItemModelPredicates.java','KlaxonItemModelPredicateIds.java','KlaxonTextures.java','KlaxonEntityRenderers.java','KlaxonClient.java','KlaxonCommon.java','KlaxonServerPlayNetworkHandler.java','KlaxonClientPlayNetworkHandler.java','KlaxonPackets.java','KlaxonClientPackets.java','KlaxonMixinConfigPlugin.java','KlaxonNBTIds.java'}
rows=[]
with zipfile.ZipFile(B/'source-archives/klaxon-1.21.1-fixed.zip') as z:
 for n in z.namelist():
  if n.endswith('/'):continue
  p=n.split('/',1)[1]
  if not (p.startswith('src/') or p.startswith('docs/')) and p!='gradle.properties':continue
  if Path(p).name not in names and not any(t in p for t in ['grapple_winch','grapple_claw','Grapple','grapple_cable','steel_grapple_claw']):continue
  data=z.read(n);out=B/'sources/myriantics__klaxon'/p;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data);rows.append(dict(path=p,local=str(out.relative_to(B)),bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),git_blob_sha1=hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest(),read_ranges=[],status='EXTRACTED_NOT_REVIEWED'))
(B/'selected-source-manifest.json').write_text(json.dumps(dict(repo='myriantics/klaxon',commit='7d31931c1c94dc3d3e4209c6897bc77aad8c8432',branch_observed='fabric/1.21.1',archive='source-archives/klaxon-1.21.1-fixed.zip',archive_sha256=hashlib.sha256((B/'source-archives/klaxon-1.21.1-fixed.zip').read_bytes()).hexdigest(),independent_tree_blob_comparison=False,files=rows,new_reference_credit=0),ensure_ascii=False,indent=2)+'\n')
for x in rows:
 if x['path'].endswith(('.java','.mdx')) or x['path']=='gradle.properties':print(x['path'],len((B/x['local']).read_text().splitlines()))
