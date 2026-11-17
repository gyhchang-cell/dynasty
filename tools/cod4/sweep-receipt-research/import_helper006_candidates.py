"""Index four explicitly read proposals; indexing confers no credit."""
import json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[3];O=R/'docs/cod4/audit-20261022/sweep-receipt-research';d=json.loads((O/'helpers/apugli-rpginventory/batch-006.json').read_text());p='/Users/a15356015027/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3'
for i in [0,1,2,4]:
 e=d['entries'][i];subprocess.run([p,str(R/'tools/cod4/sweep-receipt-research/add_methods.py'),e['source_local'],e['method'],'--at-line',str(e['line']+2)],cwd=R,check=True)
