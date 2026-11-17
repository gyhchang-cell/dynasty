"""Print complete source methods for manual review; grants no credit."""
from pathlib import Path
import re,sys,json,hashlib
p=Path(sys.argv[1]);raw=p.read_text()
mask=re.sub(r'/\*[\s\S]*?\*/|//[^\n]*|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'',lambda m:''.join('\n' if c=='\n' else ' ' for c in m.group()),raw)
for name in sys.argv[2:]:
 pat=r'(?m)^[ \t]*(?:(?:public|protected|private|static|final|abstract|default|synchronized|native)\s+)*(?:[\w.$<>?\[\],]+\s+)+'+re.escape(name)+r'\s*\('
 for m in re.finditer(pat,mask):
  i=mask.find('{',m.end());semi=mask.find(';',m.end())
  if i<0 or (semi>=0 and semi<i):continue
  depth=1;j=i+1
  while j<len(mask) and depth:
   depth+=(mask[j]=='{')-(mask[j]=='}');j+=1
  assert depth==0
  a=raw.count('\n',0,m.start())+1;z=raw.count('\n',0,j)+1
  print(json.dumps({'path':str(p),'method':name,'lines':[a,z],'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'credit':0}))
  print(raw[m.start():j])
