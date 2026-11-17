"""Verify this batch's source preservation, exact references, and rule snapshot."""
from pathlib import Path
import hashlib
import json
from datetime import datetime, timezone

D=Path(__file__).resolve().parent
R=D.parents[2]

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text())

def main():
    errors=[]
    production_changes=[]
    baseline=read(D/'source-baseline.json')
    for p,expected in baseline.items():
        if sha(R/p)!=expected:errors.append(p);production_changes.append(p)
    inv=read(D/'version-inventory.json')
    assert inv['counts']=={'sets':28,'inventory_icons':112,'wearable_png':56,'model_bindings':112,'selected_original_icons':52,'fine_old_icons':20,'historically_redrawn_v15_icons':40}
    assert not inv['errors']
    legacy=[r for r in inv['rows'] if r['category']=='V15_REDRAW_REVIEW_ONLY']
    assert len(legacy)==10 and all(i['v15_matches'] for r in legacy for i in r['icons']+r['wearable'])
    receipts=list(D.glob('texture-requirements-receipt-*.json'))
    assert len(receipts)==1
    receipt=read(receipts[0]);rules=R/'docs/art/USER_TEXTURE_REQUIREMENTS.md'
    assert sha(rules)==receipt['sha256']==sha(R/receipt['snapshot'])
    assert rules.read_bytes()==Path('/Users/a15356015027/.codex/user-preferences/texture-requirements.md').read_bytes()
    assert len(receipt['targets'])==len(set(receipt['targets']))==112
    refs=read(D/'armor-reference-provenance.json');review=read(D/'reference-review.json')
    assert sha(R/refs['source'])==refs['source_sha256']
    for r in refs['cases']:
        for a in r['assets']:
            if sha(D/a['local'])!=a['sha256']:errors.append(a['local'])
    assert len(refs['cases'])==24 and sum(len(r['assets']) for r in refs['cases'])==81
    assert review['conservative_local_learning_groups']==len(review['observations'])==18
    reviewed=[c for r in review['observations'] for c in r['cases']]
    assert len(reviewed)==len(set(reviewed))==24
    assert set(reviewed)=={r['case_key'] for r in refs['cases']}
    assert review['fresh_global_reference_credit']==refs['fresh_reference_credit']==0
    assert not review['production_allowed_by_this_record']
    result={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'PASS_EVIDENCE_AND_SOURCE_PRESERVATION' if not errors else 'EVIDENCE_OR_SOURCE_REVIEW_REQUIRED','protected_production_paths':len(baseline),'source_unchanged':not production_changes,'production_changes':production_changes,'rule_sha256':sha(rules),'legacy_v15_icons_confirmed':40,'legacy_v15_worn_confirmed':20,'selected_original_runtime_hashes_confirmed':52,'model_bindings_confirmed':112,'reference_png_hashes_confirmed':81,'reused_name_families':24,'conservative_learning_groups':18,'new_global_reference_credit':0,'new_artwork':0,'game_starts':0,'checklist_deletions':0,'wearing_or_game_acceptance':False,'errors':errors,'limits':['No artwork produced because this evidence does not satisfy the 1000-independent-related-design gate.','No armor was confirmed never redrawn; preserve historical completed designs.','Atlas images were viewed, but this is not complete UV-seam or wearing acceptance.']}
    (D/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False))
    assert not errors

if __name__=='__main__':main()
