from pathlib import Path
import zipfile,re,json,hashlib
B=Path(__file__).resolve().parent
prior=Path('docs/art/armor-modular-consumers-20261112/combined-semantic-ledger.json');pool=json.loads(prior.read_text());known=set(pool['reviewed_case_keys'])
patterns=[{'helmet':'head','chestplate':'chest','leggings':'legs','boots':'feet'},{'head':'head','chest':'chest','legs':'legs','feet':'feet'},{'hood':'head','robe':'chest','pants':'legs','boots':'feet'},{'helmet':'head','chestplate':'chest','pants':'legs','boots':'feet'}]
seen=set(); candidates=[];errors=[]
for raw in Path('/tmp/dynasty-armor-source-paths-d51.txt').read_text().splitlines():
 p=Path(raw)
 try:
  key=(p.name,p.stat().st_size)
  if key in seen:continue
  seen.add(key)
  with zipfile.ZipFile(p) as z:
   names=[n for n in z.namelist() if re.match(r'assets/[^/]+/textures/(?:item|items)/',n) and n.endswith('.png')]
   for pattern in patterns:
    groups={}
    for n in names:
     m=re.match(r'assets/([^/]+)/textures/(?:item|items)/(.*)/?([^/]+)\.png$',n)
     # Match suffix against the final basename, with directory retained in identity.
     ns=n.split('/')[1]; stem=Path(n).stem
     for suffix,slot in pattern.items():
      if stem.endswith('_'+suffix):
       prefix=stem[:-len(suffix)-1]; k=(ns,str(Path(n).parent),prefix);groups.setdefault(k,{})[slot]=n
    for (ns,folder,prefix),slots in groups.items():
     if len(slots)==4 and ns+':'+prefix not in known and ns not in ['dynasty','geotetraarmor']:
      record={'archive':str(p),'namespace':ns,'prefix':prefix,'provisional_key':ns+':'+prefix,'entries':slots}
      if not any(x['archive']==record['archive'] and x['entries']==slots for x in candidates):candidates.append(record)
 except (OSError,zipfile.BadZipFile) as e:errors.append({'path':str(p),'error':str(e)})
result={'scope':'Filename-based four-slot candidate screen only, not viewed designs or exhaustive semantic proof','prior_ledger':str(prior),'prior_sha256':hashlib.sha256(prior.read_bytes()).hexdigest(),'unique_name_size_archives_scanned':len(seen),'candidates':candidates,'errors':errors,'reference_credit':0}
(B/'candidate-screen.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print('candidate_count',len(candidates),'archives',len(seen),'errors',len(errors))
for x in candidates[:35]:print(x['provisional_key'],Path(x['archive']).name)
