"""Authored static Java text reader; never imports upstream code."""
from pathlib import Path
import re,sys,json,hashlib
ROOT=Path(__file__).resolve().parents[5]
SOURCES=ROOT/'tools/cod4/immune-feedback-research/sources'
DOC=ROOT/'docs/cod4/audit-20261022/immune-feedback-research/helpers/halley-immune'
def end_method(lines,start):
 text=''.join(lines[start-1:]);mode='code';depth=0;opened=False;i=0;nline=start
 while i<len(text):
  c=text[i];n=text[i+1] if i+1<len(text) else ''
  if mode=='line':
   if c=='\n':mode='code'
  elif mode=='block':
   if c=='*' and n=='/':mode='code';i+=1
  elif mode in ['string','char']:
   if c=='\\':i+=1
   elif c==('"' if mode=='string' else "'"):mode='code'
  else:
   if c=='/' and n=='/':mode='line';i+=1
   elif c=='/' and n=='*':mode='block';i+=1
   elif c=='"':mode='string'
   elif c=="'":mode='char'
   elif c=='{':depth+=1;opened=True
   elif c=='}':
    depth-=1
    if opened and depth==0:return nline
  if c=='\n':nline+=1
  i+=1
 raise ValueError(('no closing brace',start))
def find(repo,name):
 arr=list((SOURCES/repo).rglob(name if name.endswith('.java') else name+'.java'))
 assert len(arr)==1,(repo,name,arr)
 return arr[0]
def methods(p,pattern):
 lines=p.read_text().splitlines(keepends=True);out=[]
 for a,l in enumerate(lines,1):
  if re.match(r'\s*(?:public|protected|private|default|static)\s',l) and re.search(pattern,l) and '(' in l and not l.strip().endswith(';'):
   z=end_method(lines,a);out.append((a,z))
 return lines,out
if __name__=='__main__':
 repo,name,pat=sys.argv[1:4];p=find(repo,name);lines,spans=methods(p,pat)
 print('FILE',p.relative_to(SOURCES))
 for a,z in spans:
  print('METHOD',a,z)
  for k in range(a,z+1):print(f'{k}: {lines[k-1].rstrip()}')
