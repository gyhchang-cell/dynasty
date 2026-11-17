"""Independent ledger byte/range/uniqueness check; semantic decisions remain authored."""
import hashlib,json,datetime
from pathlib import Path
R=Path(__file__).resolve().parents[3];O=R/'docs/cod4/audit-20261022/sweep-receipt-research';rows=[json.loads(l) for l in (O/'accepted.jsonl').read_text().splitlines()];errors=[];cache={};ranges=set();structs=set()
for r in rows:
 p=R/r['source_local'];b=cache.setdefault(str(p),p.read_bytes())
 if hashlib.sha256(b).hexdigest()!=r['source_sha256']:errors.append(['source',r['candidate_index']])
 ex=r['excerpt'];lines=b.decode().splitlines()[r['line']-1:r['end_line']]
 if '\n'.join(lines).strip()!='\n'.join(ex.splitlines()).strip() or hashlib.sha256(ex.encode()).hexdigest()!=r['snippet_sha256']:errors.append(['excerpt',r['candidate_index']])
 key=(r['repo'],r['revision'],r['path'],r['line'],r['end_line'])
 if key in ranges or r['structural_fingerprint'] in structs:errors.append(['duplicate',r['candidate_index']])
 ranges.add(key);structs.add(r['structural_fingerprint'])
 if len(r['revision'])!=40 or r['revision'] not in r['url']:errors.append(['pin',r['candidate_index']])
 if r['repo'].startswith(('netty/','PaperMC/Velocity')):errors.append(['scope',r['candidate_index']])
assert len(rows)==1000 and not errors,(len(rows),errors)
receipt=dict(checked_at=datetime.datetime.now().astimezone().isoformat(),accepted=len(rows),unique_sources=len(cache),errors=errors,accepted_sha256=hashlib.sha256((O/'accepted.jsonl').read_bytes()).hexdigest(),semantic_review='人工原裁定/补充裁定及明确同链合并；本程序仅独立完整性检查，不产生语义信用',line_comparison='splitlines normalized LF and outer strip; raw source/excerpt hashes remain byte exact',prior_status_corpus_credit=0,infrastructure_credit=0,newest_batches=['188','189','190'],newest_support_chains=['094','095','096'])
(O/'gate-1000-integrity.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n');print(receipt)
