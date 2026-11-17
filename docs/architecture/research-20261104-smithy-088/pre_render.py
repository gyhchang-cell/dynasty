import json,importlib.util
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
assert not (OUT/'RECEIPT.json').exists()
spec=importlib.util.spec_from_file_location('dedup',ROOT/'docs/architecture/research-20261101-dungeons-002/check_dedup.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
ref=ROOT/'docs/architecture/continuation-20261022/references';indices=[ref/'full-buildings.json']+sorted(ref.glob('whole-candidates*/candidates.json'))
for f in sorted((ROOT/'docs/architecture').glob('research-*')):
 if f==OUT:continue
 for n in ['sources.json','scope-expansion-sources.json','manual-review.json']:
  if (f/n).is_file():indices.append(f/n)
history={}
for p in indices:mod.find_records(json.loads(p.read_text()),str(p),history)

import hashlib
from zipfile import ZipFile
s=json.loads((OUT.parent/'research-20261104-smithy-087/sources.json').read_text())['candidates'][0];jar=s['source_archive'];b=Path(jar).read_bytes();assert hashlib.sha256(b).hexdigest()==s['source_archive_sha256']
rows=[]
with ZipFile(jar)as z:
 hashes={n:hashlib.sha256(z.read(n)).hexdigest()for n in z.namelist()if n.endswith('.nbt')and '/structures/'in n}
 for member in ['data/kaisyn/structures/village/snowy_taiga_viking/houses/snowy_taiga_armorer_1.nbt','data/kaisyn/structures/village/forest_ruins/houses/forest_toolsmith_1.nbt']:
  sha=hashes[member];aliases=[n for n,h in hashes.items()if h==sha and n!=member];members=[member]+aliases;known=[h for h in history.values()if h['archive']==jar and h['member']in members]
  rows.append({'canonical_member':member,'same_bytes_aliases':aliases,'original_nbt_sha256':sha,'known_history':known,'eligible_for_new_source_study':not known,'credit':0})
obj={'fixed_archive':{'path':jar,'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)},'history_unique_archive_member_pairs':len(history),'historical_indices':list(map(str,indices)),'rows':rows,'not_semantic_admission':True,'new_reference_credit':0,'scope':'Actual source and same-byte aliases excluded BEFORE rendering; filenames not reference credit.'}
(OUT/'pre-render-history-screen.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
print('HISTORY',len(history));print(json.dumps(rows,ensure_ascii=False))
