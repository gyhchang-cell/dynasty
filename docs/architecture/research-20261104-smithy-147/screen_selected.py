"""Select one eligible direct-use dry workshop from already-saved fingerprint prefilter; no duplicate rescan."""
import json
from pathlib import Path
p=Path(__file__).resolve().parent
assert not (p/'RECEIPT.json').exists()
s=json.loads((p/'direct-use-fingerprint-prefilter.json').read_text())
a=next(x for x in s['rows']if x['member']=='data/repurposed_structures/structures/villages/birch/houses/weaponsmith_1.nbt')
assert a['eligible_for_new_source_study']
a['id']='F01';s['rows']=[a]
(p/'pre-render-history-screen.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
