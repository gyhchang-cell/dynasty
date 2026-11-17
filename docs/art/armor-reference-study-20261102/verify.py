"""Verify source protection, exact local references and semantic review coverage."""
from pathlib import Path
from contextlib import ExitStack
from datetime import datetime,timezone
import hashlib,json,zipfile

D=Path(__file__).resolve().parent
R=D.parents[2]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    baseline=read(D/'source-baseline.json');changes=[p for p,h in baseline.items() if not(R/p).is_file() or sha(R/p)!=h]
    prov=read(D/'provenance.json');review=read(D/'semantic-review.json')
    receipt=read(next(D.glob('texture-requirements-receipt-*.json')))
    assert len(receipt['targets'])==len(set(receipt['targets']))==24
    assert receipt['sha256']==sha(R/receipt['snapshot'])==sha(R/'docs/art/USER_TEXTURE_REQUIREMENTS.md')==sha(Path('/Users/a15356015027/.codex/user-preferences/texture-requirements.md'))
    assert len(prov['cases'])==45 and sum(len(c['icons']) for c in prov['cases'])==144 and len(prov['worn_textures'])==101
    flat=[c for g in review['observations'] for c in g['cases']]
    assert len(flat)==len(set(flat))==45 and set(flat)=={c['case_key'] for c in prov['cases']}
    assert len(review['observations'])==34 and review['combined_conservative_learning_groups']==57
    assert review['combined_name_families']==120 and not review['gate_met'] and not review['production_allowed']
    assert len(review['icon_pages_opened'])==7 and len(review['worn_pages_opened'])==17
    assert all((D/p).is_file() for p in review['icon_pages_opened']+review['worn_pages_opened'])
    assets=[a for c in prov['cases'] for a in c['icons']]+prov['worn_textures']
    native=read(D/'native-geometry-study.json');assets+=native['models']
    with ExitStack() as stack:
        jars={j['path']:stack.enter_context(zipfile.ZipFile(j['path'])) for j in prov['archives']}
        for index in prov['indexes']:assert sha(R/index['path'])==index['sha256']
        for jar in prov['archives']:assert sha(Path(jar['path']))==jar['sha256']
        for a in assets:
            assert sha(D/a['local'])==a['sha256']==hashlib.sha256(jars[a['jar']].read(a['entry'])).hexdigest()
    for model in native['models']:
        geo=read(D/model['local'])['minecraft:geometry'][0]
        assert geo['description']['texture_width']==geo['description']['texture_height']==96
        assert model['runtime_binding_proven'] is False
    application=read(D/'application-principles.json')
    assert len(application['principles'])==3 and application['production_edits']==0 and not application['gate_met']
    for material,row in application['protected_selected_materials'].items():
        assert len(row['icons_to_preserve'])==4
        for p in row['icons_to_preserve']:assert sha(R/p['path'])==p['sha256']
    result={'checked_at':datetime.now(timezone.utc).isoformat(),'status':'PASS_RESEARCH_EVIDENCE' if not changes else 'SOURCE_CHANGED_REVIEW_REQUIRED',
        'source_protected_paths':len(baseline),'source_unchanged':not changes,'changed_paths':changes,
        'new_icon_name_families_viewed':45,'new_icon_png_viewed':144,'worn_png_viewed':101,'native_geo_read':2,
        'new_conservative_learning_groups':34,'prior_groups_reused':23,'combined_groups':57,'reference_gate_met':False,
        'rules_sha256':receipt['sha256'],'new_artwork':0,'production_changes':0,'game_starts':0,'checklist_deletions':0,
        'scope':'Actual local reference research and application principles; not completed wearing repair or game validation.'}
    (D/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False));assert not changes

if __name__=='__main__':main()
