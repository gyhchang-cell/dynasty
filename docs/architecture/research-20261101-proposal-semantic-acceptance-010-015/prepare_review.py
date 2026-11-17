#!/usr/bin/env python3
"""Snapshot thirteen existing proposals; this does not accept or discover buildings."""
import hashlib
import json
from pathlib import Path
OUT=Path(__file__).resolve().parent
BASE=OUT.parent
BATCHES=[10,11,12,13,15]
def evidence(p):return dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def main():
 candidates=[];inputs=[]
 for batch in BATCHES:
  folder=BASE/f'research-20261101-dungeons-{batch:03d}'
  proposals=json.loads((folder/'reference-proposals.json').read_text())['entries']
  for name in ['sources.json','manual-review.json','reference-proposals.json','vertical-original-states.json','interface-audit.json','detail-evidence.json','RECEIPT.json']:
   inputs.append(evidence(folder/name))
  for proposal in proposals:
   c=proposal['source'];candidates.append(dict(id=proposal['id'],source_archive=c['source_archive'],source_archive_sha256=c['source_archive_sha256'],
    member=c['member'],nbt_sha256=c['nbt_sha256'],size=c['size'],publisher_url=c['publisher_url'],original_batch=batch,original_id=c['id'],
    proposal_input=evidence(folder/'reference-proposals.json'),actual_images_from_original_study=proposal['actual_views']))
 assert len(candidates)==len({c['id'] for c in candidates})==len({(c['source_archive'],c['member']) for c in candidates})==13
 (OUT/'sources.json').write_text(json.dumps(dict(candidates=candidates,inputs=inputs,formal_credit_added=0,
  operation='Existing-proposal reconsideration; not thirteen newly discovered source templates.'),ensure_ascii=False,indent=2)+'\n')
 print('Snapshotted thirteen existing proposals; zero acceptance decisions.')
if __name__=='__main__':main()
