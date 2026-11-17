"""Verify new evidence and immutable history; no semantic credit automation."""
import ast
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
from zipfile import ZipFile
OUT=Path(__file__).resolve().parent
BASE=OUT.parent
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def sha(b):return hashlib.sha256(b).hexdigest()
def get(p):return json.loads(p.read_text())
def dump(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def evidence(p):return dict(path=str(p.resolve()),sha256=sha(p.read_bytes()))
def main():
    v=module('helpers036',BASE/'research-20261103-dungeons-036/verify_delivery.py')
    original=BASE/'research-20261101-proposal-semantic-acceptance-010-015'
    for e in get(original/'scoped-reference-register.json')['preserved_registries']:v.check(e)
    old=[original]+[BASE/f'research-20261101-dungeons-{n:03d}' for n in range(16,33)]+[BASE/f'research-20261102-dungeons-{n:03d}' for n in range(33,36)]+[BASE/f'research-20261103-dungeons-{n:03d}' for n in range(36,41)]
    for folder in old:
        for e in get(folder/'RECEIPT.json')['files']:
            p=folder/e['path'];assert p.stat().st_size==e['bytes'] and sha(p.read_bytes())==e['sha256'],p
    src=get(OUT/'sources.json');audit=get(OUT/'raw-source-audit.json');dedup=get(OUT/'dedup-evidence.json');review=get(OUT/'manual-review.json');author=get(OUT/'author-and-family-evidence.json')
    assert src['automatic_credit']==0 and len(src['candidates'])==3 and len(review['entries'])==3
    assert dedup['historical_unique_local_archive_member_pairs']==230 and not dedup['within_batch_exact_duplicate_pairs']
    cache={}
    for archive in src['source_archives']:
        assert sha(Path(archive['path']).read_bytes())==archive['sha256']
        with ZipFile(archive['path']) as z:
            for c,a,h in zip(src['candidates'],audit['entries'],dedup['entries']):
                raw=z.read(c['member']);assert sha(raw)==c['nbt_sha256'];d=v.read(raw);assert d['size']==c['size']
                pal=d.get('palette') or d['palettes'][0];ss={tuple(x['pos']):pal[x['state']] for x in d['blocks']};cache[c['id']]=ss
                assert len(ss)==len(d['blocks']) and all(0<=p[i]<d['size'][i] for p in ss for i in range(3))
                cs={p:s for p,s in ss.items() if s['Name'] not in v.AIR};assert len(cs)==c['nonair'] and Counter(s['Name'] for s in cs.values())==c['materials']==a['materials']
                assert a['occupied_bounds']==[[min(p[i] for p in cs),max(p[i] for p in cs)] for i in range(3)]
                assert not c['sockets'] and not c['doors'] and not any(s['Name']=='minecraft:jigsaw' for s in ss.values())
                assert c['entities']==[dict(pos=e.get('pos'),id=e.get('nbt',{}).get('id')) for e in d.get('entities',[])]
                for r in c['pool_references']:assert json.loads(z.read(r['member']))==r['data'] and any(x['element'].get('location')==c['member'].split('/')[1]+':'+c['member'].split('/structures/')[1][:-4] for x in r['data']['elements'])
                for r in a['archive_json_identity_mentions']:assert sha(z.read(r['member']))==r['sha256'] and json.loads(z.read(r['member']))==r['data']
                assert h['occupancy_sha256']==v.geometry_hash({p:1 for p in cs},c['size']) and h['role_sha256']==v.geometry_hash({p:v.role(s['Name']) for p,s in cs.items()},c['size']) and not h['historical_exact_matches']
            for e in author['author_resources']:assert sha(z.read(e['member']))==e['sha256'] and json.loads(z.read(e['member']))==e['data']
            manifest=z.read('META-INF/mods.toml');assert sha(manifest)==author['manifest_sha256'] and manifest.decode()==author['manifest_text']
    a,b=cache['F02'],cache['F03'];changes=[dict(position=list(p),left=a.get(p),right=b.get(p)) for p in sorted(a.keys()|b.keys()) if a.get(p)!=b.get(p)]
    assert changes==author['changes'] and len(changes)==author['changed_raw_states']
    names=set(author['preserved_shell_names']);sa={p:s for p,s in a.items() if s['Name'] in names};sb={p:s for p,s in b.items() if s['Name'] in names}
    assert sa==sb and len(sa)==author['preserved_shell_cells'] and author['shell_states_identical']
    actual=[]
    for r in review['entries']:
        v.check(r['source_evidence']);assert r['credit']==0 and r['template_body_boundary_confirmed'] and not r['native_acceptance'] and not r['independent_human_review']
        assert set(r['observations'])=={'layout','proportion','facade','roof','materials','circulation','terrain'}
        for e in r['actual_images_viewed']:v.check(e,True);actual.append(e['path'])
    assert len(actual)==len(set(actual))==review['actual_images_viewed']==5
    scope=get(OUT/'scope-status.json');fun=scope['funerary'];guard=scope['guard']
    v.check(fun['baseline']);assert len(get(Path(fun['baseline']['path']))['entries'])==fun['formal_baseline']==148 and fun['batch_proposed_credit']==0 and not fun['formal_register_written']
    v.check(guard['prior_local_observation_scope']);v.check(guard['coordinator_review']);cr=get(Path(guard['coordinator_review']['path']))
    assert cr['scope_review']['coordinator_applied_formal_credit']==guard['reference_036_F01_formal_credit']==0
    assert guard['historical_local_counts_are_not_coordinator_formal_counts'] and not guard['original_scope_definition_changed'] and not guard['flag_cropped']
    discovery=get(OUT/'discovery-boundary.json')
    for e in discovery['indices_checked']:v.check(e)
    assert discovery['local_only'] and discovery['network_requests']==0 and not discovery['java_run'] and not discovery['game_run']
    for p in OUT.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
    report=dict(status='PASS_FUNERARY_RELEVANCE_HOLD_AND_VARIANT_DEDUP',date='2026-11-03',batch=41,
        new_source_templates=3,actual_images_viewed=5,new_reference_credit=0,funerary_formal_baseline=148,remaining_formal=852,
        frost_shell_cells_identical=len(sa),raw_variant_changes=len(changes),prior_receipt_packages_unchanged=len(old),
        reference_036_F01_coordinator_formal_credit=0,old_local9_not_formal9=True,production_allowed=False,
        java_run=False,game_run=False,network_requests=0,production_changes=0,checklist_deletions=0)
    dump('verification.json',report)
    session=get(OUT/'session.json');session.update(status=report['status'],verification=evidence(OUT/'verification.json'));dump('session.json',session)
    dump('active-checkpoint.json',dict(date='2026-11-03',owner='做建筑的',batch=41,
        session=evidence(OUT/'session.json'),verification=evidence(OUT/'verification.json'),scope=evidence(OUT/'scope-status.json'),review=evidence(OUT/'manual-review.json'),
        shared_coordinator_session_not_overwritten=True,production_changes=0,checklist_deletions=0,duration_hours_claimed=0,no_automation=True))
    files=sorted(p for p in OUT.rglob('*') if p.is_file() and p.name!='RECEIPT.json')
    dump('RECEIPT.json',dict(status=report['status'],files=[dict(path=str(p.relative_to(OUT)),bytes=p.stat().st_size,sha256=sha(p.read_bytes())) for p in files]))
    print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()
