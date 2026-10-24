"""Pin and cache primary-source Java for the language-lifecycle study, never install it."""
from pathlib import Path
import concurrent.futures,hashlib,io,json,ssl,subprocess,urllib.request,zipfile
ROOT=Path(__file__).resolve().parents[4]
CACHE=ROOT/'build/cod4-pack-20261022/language-sources'
OUT=ROOT/'docs/cod4/audit-20261022/pack-acceptance/language-study'
REPOS=['mezz/JustEnoughItems','shedaniel/RoughlyEnoughItems','emilyploszaj/emi','mekanism/Mekanism','Creators-of-Create/Create','BluSunrize/ImmersiveEngineering','AppliedEnergistics/Applied-Energistics-2','GregTechCEu/GregTech-Modern','VazkiiMods/Botania','TeamPneumatic/pnc-repressurized','Team-EnderIO/EnderIO','SlimeKnights/TinkersConstruct']
REPOS += ['VazkiiMods/Patchouli','FTBTeam/FTB-Library','shedaniel/cloth-config','Snownee/Jade','baileyholl/Ars-Nouveau','VazkiiMods/Quark']
CTX=ssl.create_default_context(cafile='/etc/ssl/cert.pem')
def fetch(repo):
 dest=CACHE/repo.replace('/','__');meta=dest/'source.json'
 if meta.exists():return json.loads(meta.read_text())
 try:
  # Reuse pinned existing study versions when available, but fetch missing client sources.
  previous=ROOT/'build/item-use-references'/repo.replace('/','__')/'source.json'
  sha=json.loads(previous.read_text())['sha'] if previous.exists() else subprocess.check_output(['git','ls-remote','https://github.com/'+repo+'.git','HEAD'],text=True,timeout=30).split()[0]
  url='https://codeload.github.com/'+repo+'/zip/'+sha
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Dynasty-language-study'}),context=CTX,timeout=100) as r:data=r.read()
  archive=zipfile.ZipFile(io.BytesIO(data));count=0
  for info in archive.infolist():
   rel=Path(*Path(info.filename).parts[1:])
   if rel.suffix!='.java' or '..' in rel.parts:continue
   target=dest/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(archive.read(info));count+=1
  record={'repo':repo,'sha':sha,'archive_url':url,'archive_sha256':hashlib.sha256(data).hexdigest(),'java_files':count}
  meta.write_text(json.dumps(record,indent=2));return record
 except Exception as e:return {'repo':repo,'error':str(e)}
if __name__=='__main__':
 CACHE.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
 results=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
  for result in pool.map(fetch,REPOS):results.append(result);print(json.dumps(result),flush=True)
 (OUT/'sources.json').write_text(json.dumps(results,indent=2))
