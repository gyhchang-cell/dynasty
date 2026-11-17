"""Read-only local candidate discovery. No actual visual review or semantic credit."""
from pathlib import Path
import zipfile,json,subprocess,re,concurrent.futures
D=Path(__file__).resolve().parent;R=D.parents[2];seen=set(json.loads((R/'docs/art/armor-pneumatic-reference-20261111/combined-semantic-ledger.json').read_text())['reviewed_case_keys'])
paths=subprocess.run(['rg','--files','/Users/a15356015027/Public/.minecraft/versions'],capture_output=True,text=True,check=True).stdout.splitlines();paths=[Path(p) for p in paths if '/mods/' in p and p.endswith('.jar')];unique={}
for p in paths:unique.setdefault((p.name,p.stat().st_size),p)
def scan(p):
 try:
  z=zipfile.ZipFile(p);groups={}
  for n in z.namelist():
   m=re.fullmatch(r'assets/([^/]+)/textures/(?:item|items)/(?:[^/]+/)*([^/]+)_(helmet|chestplate|leggings|boots)\.png',n)
   if not m:continue
   key=m[1]+':'+m[2]
   if key in seen or m[1] in ['minecraft','inventoryhud'] or 'empty_armor_slot' in key:continue
   groups.setdefault(key,{})[m[3]]=n
  return [{'case_key':k,'archive':str(p),'parts':v,'status':'CANDIDATE_NOT_VISUALLY_REVIEWED_ZERO_CREDIT'} for k,v in groups.items() if len(v)==4]
 except (OSError,zipfile.BadZipFile):return []
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:rows=[r for batch in ex.map(scan,unique.values()) for r in batch]
(D/'candidate-discovery.json').write_text(json.dumps({'scope':'local native item PNG four-part filename candidates only; registration/model/visual correspondence unproven','archives_metadata_scanned':len(unique),'candidate_complete_names':rows,'credit':0,'production_changes':0},ensure_ascii=False,indent=2)+'\n');print('scanned',len(unique),'candidates',len(rows));print('\n'.join(r['case_key']+' '+r['archive'] for r in rows)[:6500])
