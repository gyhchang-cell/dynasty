"""Read master decisions; emit helper-only handoff classification, never credit."""
from pathlib import Path
import json,hashlib,collections,datetime
ROOT=Path('/Users/a15356015027/Desktop/dynasty')
BASE=Path(__file__).parent
DOC=ROOT/'docs/cod4/audit-20261022/legacy-migration-acceptance/helpers/halley-migration'
def main():
    records=json.loads((DOC/'batch-001.json').read_text())['records']
    raw=(ROOT/'docs/cod4/audit-20261022/legacy-migration-acceptance/reviewed.jsonl').read_bytes()
    master=[json.loads(l) for l in raw.splitlines() if l.strip()]
    byid={}
    for m in master:
        for e in m.get('evidence',[]):byid.setdefault(e.get('candidate_id'),[]).append(m)
    groups=collections.defaultdict(list);details=[]
    for r in records:
        matches=byid.get(r['candidate_id'],[])
        # A different entry point of these exact, already counted full chains.
        if r['id']=='halley-migration-08':matches += [m for m in master if m.get('family')=='framedblocks-tank-material-preserving-block-to-item-component']
        if r['id']=='halley-migration-22':matches += [m for m in master if m.get('family')=='icefire-bestiary-owned-unlocked-page-progress-through-lectern']
        imported=[m for m in matches if m.get('family')==r['family'] and m.get('status')=='accepted']
        if imported:group='coordinator_already_accepted_helper_family'
        elif matches:group='prior_or_parallel_overlap_or_decision_do_not_recredit'
        else:group='reviewed_unmerged_suggestion_credit0'
        groups[group].append(r)
        details.append(dict(id=r['id'],family=r['family'],classification=group,helper_credit=0,master_matches=[dict(candidate_id=m.get('candidate_id'),status=m.get('status'),family=m.get('family'),credit=m.get('credit',0)) for m in matches],semantic_duplicate_risk=r['semantic_duplicate_risk']))
    imported=len(groups['coordinator_already_accepted_helper_family']);unmerged=len(groups['reviewed_unmerged_suggestion_credit0'])
    report=dict(timestamp_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),helper='halley-migration',target_new_suggestions=30,reviewed_chain_records=len(records),credit=0,master_read_only=True,master_decisions_read=len(master),master_read_sha256=hashlib.sha256(raw).hexdigest(),classification_counts={k:len(v) for k,v in groups.items()},helper_family_accepted_elsewhere=imported,unmerged_reviewed_suggestions=unmerged,nonoverlap_helper_family_suggestions_upper_bound=imported+unmerged,gap_to_30_nonoverlap_suggestions=max(0,30-imported-unmerged),records=details,limits='Imported counts report coordinator decisions only. Unmerged are researched suggestions, not accepted credit. Structural and semantic dedup by Kepler still required; this snapshot is not a live master ledger.')
    (DOC/'reconciliation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    (DOC/'suggestions-to-merge.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in groups['reviewed_unmerged_suggestion_credit0']))
    (DOC/'overlap-and-decisions.json').write_text(json.dumps(dict(credit=0,note='Supporting review only; existing coordinator decision; never new credit',records=groups['prior_or_parallel_overlap_or_decision_do_not_recredit']),ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ['records','limits']},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
