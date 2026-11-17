"""Find complete candidate method bodies. This is retrieval, zero research credit."""
from pathlib import Path
import re,json,hashlib
B=Path(__file__).resolve().parent;R=B.parents[2];O=R/'docs/cod4/audit-20261022/immune-feedback-research'
# Blank comments and strings while retaining newline/offset alignment.
def mask(s):
 return re.sub(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'',lambda m:''.join('\n' if c=='\n' else ' ' for c in m.group()),s)
pat=re.compile(r'\b(?:public|protected|private)\s+(?:(?:static|final|synchronized|abstract)\s+)*[\w<>?,.\[\] @]+?\s+(\w+)\s*\([^;{}]*\)\s*(?:throws [\w., ]+)?\{')
keys=re.compile(r'(?i)immune|invulnerab|canBeAffected|knockback|isPushable|damage.*text|floating|popoff|hurtServer')
rows=[]
for meta in sorted((B/'sources').glob('*/source.json')):
 d=json.loads(meta.read_text());source=meta.parent
 for p in source.rglob('*.java'):
  s=p.read_text(errors='replace');ms=mask(s)
  for m in pat.finditer(ms):
   pos=m.end();depth=1
   while depth and pos<len(ms):
    if ms[pos]=='{':depth+=1
    elif ms[pos]=='}':depth-=1
    pos+=1
   if depth:continue
   body=s[m.start():pos]
   if not keys.search(m.group(1)+'\n'+body):continue
   start=s.count('\n',0,m.start())+1;end=s.count('\n',0,pos)+1
   normalized=re.sub(r'\s+','',ms[m.start():pos])
   rows.append({'status':'candidate_unreviewed','research_credit':0,'repo':d['repo'],'commit':d['commit'],'path':str(p.relative_to(R)),'method':m.group(1),'lines':[start,end],'method_sha256':hashlib.sha256(body.encode()).hexdigest(),'lexical_body_key':hashlib.sha256(normalized.encode()).hexdigest(),'url':f'https://github.com/{d["repo"]}/blob/{d["commit"]}/{p.relative_to(source)}#L{start}-L{end}'})
(O/'candidate-index.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'candidate_methods':len(rows),'research_credit':0,'note':'lexical dedup is not semantic dedup; all remain unreviewed'}))
