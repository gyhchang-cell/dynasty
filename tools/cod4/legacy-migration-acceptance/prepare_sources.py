from pathlib import Path
import json,subprocess,hashlib,zipfile
B=Path(__file__).resolve().parent;R=B.parents[2];O=R/'docs/cod4/audit-20261022/legacy-migration-acceptance';D=B/'.work/sources';D.mkdir(parents=True,exist_ok=True)
chosen={}
for root in [R/'build/cod4-pack-20261022/language-sources',R/'tools/cod4/armor-acceptance/.work/research-sources',R/'build/item-use-references']:
 for meta in sorted(root.glob('*/source.json')):
  j=json.loads(meta.read_text());repo=j.get('repo');rev=j.get('sha')
  if not repo or not rev:continue
  if repo not in chosen:chosen[repo]=(meta,j)
records=[]
for repo,(meta,j) in chosen.items():
 dest=D/repo.replace('/','__')
 if not dest.exists():subprocess.run(['cp','-cR',str(meta.parent),str(dest)],check=True)
 records.append({**j,'original_cache':str(meta.parent),'private_source':str(dest.relative_to(R)),'provenance':'Reused pinned upstream primary-source cache; private APFS snapshot; no upstream code executed','files_present':len(list(dest.rglob('*.java')))})
p=R/'tools/cod4/mob-load-acceptance/.work/gradle-home/caches/forge_gradle/minecraft_user_repo/net/minecraftforge/forge/1.20.1-47.4.10_mapped_official_1.20.1/forge-1.20.1-47.4.10_mapped_official_1.20.1-sources.jar'
dest=D/'minecraft-forge-1.20.1-47.4.10';dest.mkdir(exist_ok=True)
with zipfile.ZipFile(p) as z:
 for name in z.namelist():
  if name.endswith('.java') and '..' not in Path(name).parts:
   f=dest/name;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(z.read(name))
records.append({'repo':'Minecraft+MinecraftForge native mapped1.20.1','sha':hashlib.sha256(p.read_bytes()).hexdigest(),'source_archive':str(p),'maven':'net.minecraftforge:forge:1.20.1-47.4.10_mapped_official_1.20.1:sources','private_source':str(dest.relative_to(R)),'provenance':'Local native Forge sources jar, archive SHA-256; no fork used as authority','files_present':len(list(dest.rglob('*.java')))})
(O/'sources.json').write_text(json.dumps(records,ensure_ascii=False,indent=2));print('Pinned source roots',len(records),'Java files',sum(x['files_present'] for x in records))
