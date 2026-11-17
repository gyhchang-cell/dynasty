"""Save explicit human/model-authored TSV judgments; never classify candidates automatically."""
from pathlib import Path
import sys,json,subprocess
b=Path(__file__).resolve().parent
s=sys.stdin.read();batch={}
for l in s.splitlines():
 if not l.strip():continue
 i,d,n=l.split('|',2);assert d in ('a','x') and i not in batch
 batch[i]=['accepted' if d=='a' else 'excluded',n]
p=b/'research'/('continuation-'+sys.argv[1]+'.tsv');assert not p.exists()
p.write_text(s);q=p.with_suffix('.json');q.write_text(json.dumps(batch,ensure_ascii=False,indent=2)+'\n')
subprocess.run([sys.executable,str(b/'review_candidates.py'),'--decisions',str(q)],check=True)
