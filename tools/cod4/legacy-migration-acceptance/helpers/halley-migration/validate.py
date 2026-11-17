"""Read-only verification of evidence; writes only this helper's audit reports."""
import sys
sys.dont_write_bytecode=True
import json, hashlib, collections
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from extract import PARSER, walk, norm
ROOT=Path('/Users/a15356015027/Desktop/dynasty')
BASE=Path(__file__).parent
DOC=ROOT/'docs/cod4/audit-20261022/legacy-migration-acceptance/helpers/halley-migration'
def sha(x):return hashlib.sha256(x).hexdigest()
def main():
    batch=json.loads((DOC/'batch-001.json').read_text());rows=batch['records'];evidence={};fail=[]
    pins={x['repo']:x for x in json.loads((BASE/'source-pins.json').read_text())}
    for pin in pins.values():
        cp=ROOT/pin['metadata_dir']/'commit.json';tp=ROOT/pin['metadata_dir']/'tree.json'
        assert sha(cp.read_bytes())==pin['commit_metadata_sha256']
        assert sha(tp.read_bytes())==pin['tree_metadata_sha256']
        c=json.loads(cp.read_bytes());t=json.loads(tp.read_bytes())
        assert c['sha']==pin['commit'] and c['tree']['sha']==pin['root_tree']==t['sha'] and not t.get('truncated')
    for r in rows:
        assert r['credit']==0 and not r['accepted'] and r['status']=='helper_reviewed_pending_coordinator'
        assert all(r.get(k) for k in ['observation','application','limits','semantic_duplicate_risk','trigger','input','output'])
        for e in r['evidence']:evidence[e['candidate_id']]=e
        e=r['evidence'][0]
        assert all(r[k]==v for k,v in [('repo',e['repo']),('commit',e['revision']),('path',e['path']),('start',e['start_line']),('end',e['end_line']),('text',e['context']),('excerptSha256',e['method_sha256']),('normalizedSha256',e['structural_fingerprint'])])
    ast_cache={}; trees={}; verified_files=set()
    for e in evidence.values():
        p=ROOT/e['source'];raw=p.read_bytes()
        assert sha(raw)==e['file_sha256']==e['sourceSha256']
        blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest();assert blob==e['blob']
        pin=pins[e['repo']]
        if e['repo'] not in trees:trees[e['repo']]={v['path']:v['sha'] for v in json.loads((ROOT/pin['metadata_dir']/'tree.json').read_text())['tree'] if v['type']=='blob'}
        assert trees[e['repo']][e['path']]==blob
        verified_files.add(str(p))
        if str(p) not in ast_cache:ast_cache[str(p)]=list(walk(PARSER.parse(raw).root_node))
        nodes=[n for n in ast_cache[str(p)] if n.type in ('method_declaration','constructor_declaration','field_declaration') and n.start_point.row+1==e['start_line'] and n.end_point.row+1==e['end_line'] and raw[n.start_byte:n.end_byte].decode()==e['context']]
        assert len(nodes)==1,(e['path'],e['method'])
        n=nodes[0];assert not n.has_error and not e['parse_has_error']
        assert sha(e['context'].encode())==e['method_sha256']
        assert norm(n,raw)==e['structural_fingerprint']
        assert sha((e['repo']+e['revision']+e['path']+str(n.start_byte)).encode())[:20]==e['candidate_id']
    ledger=ROOT/'docs/cod4/audit-20261022/legacy-migration-acceptance/reviewed.jsonl';rawledger=ledger.read_bytes();master=[json.loads(l) for l in rawledger.splitlines() if l.strip()]
    matches=[]
    for r in rows:
        p=r['evidence'][0]
        for m in master:
            for e in m.get('evidence',[]):
                kinds=[]
                if p['candidate_id']==e.get('candidate_id'):kinds.append('candidate_id')
                if p['method_sha256']==e.get('method_sha256'):kinds.append('method_sha256')
                if p['structural_fingerprint']==e.get('structural_fingerprint'):kinds.append('structural_fingerprint')
                if kinds:matches.append(dict(helper_id=r['id'],master_candidate=m.get('candidate_id'),master_family=m.get('family'),master_status=m.get('status'),match_kinds=kinds,matched_evidence_path=e.get('path'),matched_method=e.get('method'),matched_repo=e.get('repo')))
    internal=[]
    for i,r in enumerate(rows):
        for s in rows[i+1:]:
            if r['normalizedSha256']==s['normalizedSha256']:internal.append([r['id'],s['id']])
    report=dict(status='pass',reviewed_chain_records=len(rows),credit=0,unique_evidence_nodes=len(evidence),unique_source_files=len(verified_files),complete_ast_boundaries_verified=True,parse_error_nodes=0,sha256_and_git_blob_verified=True,source_pins_verified=True,master_decisions_read=len(master),master_read_sha256=sha(rawledger),primary_matches_to_master=matches,internal_primary_normalized_collisions=internal,semantic_audit_required=True,note='Static hashes and AST prove evidence integrity, not semantic independence or game behavior. Master ledger read only; no credit changes.')
    (DOC/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
