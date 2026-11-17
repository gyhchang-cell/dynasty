"""Static document provenance audit only; no build, test, game, GUI or upstream execution."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib,datetime,collections
BASE=Path(__file__).resolve().parent
ROOT=Path('/Users/a15356015027/Desktop/dynasty')
DOC=ROOT/'docs/cod4/audit-20261022/legacy-migration-acceptance/helpers/halley-migration/batch-003'
sys.path.insert(0,str(BASE.parent))
from extract import PARSER,walk,norm,sha
def record_document_integrity():
    manifests=json.loads((BASE/'source-manifest.json').read_text())
    evidence_files={};git_files={};errors=[]
    for source in manifests:
        meta=BASE/'provenance'/source['repo'].replace('/','__')
        cb=(meta/'commit.json').read_bytes();tb=(meta/'tree.json').read_bytes()
        commit=json.loads(cb);tree=json.loads(tb)
        assert sha(cb)==source['commit_metadata_sha256']
        assert sha(tb)==source['tree_metadata_sha256']
        assert commit['sha']==source['commit'] and commit['tree']['sha']==source['git_tree']==tree['sha']
        assert not tree.get('truncated')
        git_files[source['repo']]={r['path']:r['sha'] for r in tree['tree'] if r['type']=='blob'}
        for f in source['files']:
            raw=(ROOT/f['source']).read_bytes()
            assert sha(raw)==f['sourceSha256']
            assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==f['source_blob']==git_files[source['repo']][f['path']]
    batch=json.loads((DOC/'batch-003.json').read_text());rows=batch['records']
    seen_nodes={};primary=collections.defaultdict(list)
    for row in rows:
        assert row['credit']==0 and not row['accepted']
        for name in ['repo','commit','path','start','end','name','source','sourceSha256','text','excerptSha256','normalizedSha256','url','observation','application','limits','semantic_duplicate_risk']:
            assert row.get(name),(row['family'],name)
        primary[row['normalizedSha256']].append(row['family'])
        for e in row['evidence']:
            raw=(ROOT/e['source']).read_bytes();assert sha(raw)==e['sourceSha256']
            nodes=[n for n in walk(PARSER.parse(raw).root_node) if n.type in ('method_declaration','constructor_declaration') and n.start_point.row+1==e['start'] and n.end_point.row+1==e['end']]
            assert len(nodes)==1,(e['path'],e['start'],e['end'])
            n=nodes[0];text=raw[n.start_byte:n.end_byte].decode()
            assert not n.has_error
            assert text==e['text']==e['context'] and sha(text.encode())==e['excerptSha256'] and norm(n,raw)==e['normalizedSha256']
            assert e['source_blob']==git_files[e['repo']][e['path']]
            expected=sha((e['repo']+e['commit']+e['path']+str(n.start_byte)).encode())[:20]
            assert expected==e['candidate_id']
            seen_nodes[e['candidate_id']]=e
            evidence_files[e['source']]=e['sourceSha256']
    master=ROOT/'docs/cod4/audit-20261022/legacy-migration-acceptance/reviewed.jsonl'
    master_raw=master.read_bytes();master_rows=[json.loads(x) for x in master_raw.splitlines() if x]
    matches=[]
    for row in rows:
        for m in master_rows:
            match=[]
            if row['candidate_id']==m.get('candidate_id'):match.append('candidate_id')
            for e in m.get('evidence',[]):
                if row['excerptSha256']==e.get('method_sha256'):match.append('primary_excerpt')
                if row['normalizedSha256']==e.get('structural_fingerprint'):match.append('primary_normalized')
            if match:matches.append({'family':row['family'],'master_candidate_id':m.get('candidate_id'),'master_status':m.get('status'),'master_family':m.get('family'),'matches':sorted(set(match))})
    result={'document_audited_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'credit':0,'reviewed_chains':len(rows),'complete_ast_nodes':len(seen_nodes),'evidence_files':len(evidence_files),'official_pinned_repos':len(manifests),'downloaded_files_not_credit':sum(len(x['files']) for x in manifests),'parse_errors':0,'hash_errors':0,'primary_internal_normalized_collisions':{k:v for k,v in primary.items() if len(v)>1},'master_sha256_read_only':sha(master_raw),'master_rows_at_check':len(master_rows),'master_primary_matches':matches,'semantic_review_required':True,'game_started':False,'upstream_executed':False,'main_ledger_written':False,'runtime_tests_run':False,'builds_run':False,'exam_prohibition_active':True}
    (DOC/'document-integrity.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':record_document_integrity()
