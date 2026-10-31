"""Reclassify handwritten rejected source as excluded, never an accepted suggestion."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json
ROOT=Path('/Users/a15356015027/Desktop/dynasty')
D=ROOT/'docs/cod4/audit-20261022/legacy-migration-acceptance/helpers/halley-migration/batch-045'
p=D/'batch-045.json';data=json.loads(p.read_text())
records=data.pop('records',[])+data.get('excluded_records',[])
for row in records:row.update(status='excluded_not_durable_migration_evidence',credit=0,accepted=False)
data.update(records=[],excluded_records=records,reviewed_chains=0,reviewed_exclusion_chains=len(records))
p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
(D/'reviewed-suggestions.jsonl').write_text('')
(D/'excluded-candidates.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
