"""Reuse fixed previous direct-use screening and check only the new147 source delta."""
import json,hashlib,importlib.util
from pathlib import Path
p=Path(__file__).resolve().parent;root=p.parents[2];prev=p.parent/'research-20261104-smithy-147'
assert not (p/'RECEIPT.json').exists()
def bind(f):
 f=Path(f);v=f.read_bytes();return dict(path=str(f),sha256=hashlib.sha256(v).hexdigest(),bytes=len(v))
s=json.loads((prev/'direct-use-fingerprint-prefilter.json').read_text())
a=next(x for x in s['rows']if x['member']=='data/repurposed_structures/structures/villages/birch/houses/armorer_house_1.nbt');assert a['eligible_for_new_source_study']
spec=importlib.util.spec_from_file_location('dedup',root/'docs/architecture/research-20261101-dungeons-002/check_dedup.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
old=json.loads((prev/'sources.json').read_text())['candidates'][0]
newfp=m.load(dict(archive=a['source_archive'],member=a['member']));oldfp=m.load(dict(archive=old['source_archive'],member=old['member']))
keys=[k for k in ['nbt_sha256','role_sha256','occupancy_sha256']if newfp[k]==oldfp[k]]
assert not keys
a['id']='F01';s['rows']=[a];s['historical_indices'] += [str(prev/'sources.json'),str(prev/'manual-review.json')];s['history_unique_archive_member_pairs']+=1
s['reused_prior_direct_screen']=bind(prev/'direct-use-fingerprint-prefilter.json');s['new_history_delta_only']={'previous_source':bind(prev/'sources.json'),'exact_matches':keys,'no_old_passed_rescan':True}
(p/'pre-render-history-screen.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
print('F01 direct birch armorer eligible, reused old screen +147only delta')
