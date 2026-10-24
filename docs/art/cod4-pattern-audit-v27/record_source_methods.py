"""Record explicitly selected and actually read methods; no discovery/count inflation."""
from pathlib import Path
import json,hashlib,re,sys
D=Path(__file__).resolve().parent;R=D.parents[2]
sys.path.insert(0,str(R/'build/pattern-research-python'))
from tree_sitter import Language,Parser
import tree_sitter_java
parser=Parser(Language(tree_sitter_java.language()))
def record(repo,path,name,index,scope,observation):
 root=R/'build/item-use-references'/repo.replace('/','__');meta=json.loads((root/'source.json').read_text());p=root/path;data=p.read_bytes();tree=parser.parse(data);todo=[tree.root_node];found=[]
 while todo:
  n=todo.pop();todo.extend(reversed(n.children))
  if n.type in ('method_declaration','constructor_declaration') and n.child_by_field_name('name').text.decode()==name:found.append(n)
 n=found[index];body=n.child_by_field_name('body');assert not n.has_error;source=data[n.start_byte:n.end_byte].decode();calls=[];todo=[body]
 while todo:
  x=todo.pop();todo.extend(x.children)
  if x.type=='method_invocation':calls.append(x.child_by_field_name('name').text.decode())
 norm=re.sub(r'/\*.*?\*/|//[^\n]*','',body.text.decode(),flags=re.S)
 norm=re.sub(r'"(?:\\.|[^"\\])*"','"ID"',norm);norm=re.sub(r'\b0x[0-9a-fA-F]+[Ll]?\b','COLOR',norm);norm=re.sub(r'\b(?:0\.\d+|\d+\.\d*|\d+)[fFdDlL]?\b','N',norm)
 norm=re.sub(r'\b[A-Za-z_$][\w$]*\b',lambda m:m.group() if m.group() in set(calls)|{'if','else','for','while','return','new','try','finally','switch','case','true','false','null','this','super'} else 'v',norm);norm=re.sub(r'\s+','',norm)
 start=n.start_point.row+1;end=n.end_point.row+1
 return {'id':'explicit-source-method','repo':repo,'revision':meta['sha'],'path':path,'method':name,'start':start,'end':end,'sourceSha256':hashlib.sha256(data).hexdigest(),'semanticHash':hashlib.sha256(norm.encode()).hexdigest(),'local':str(p.relative_to(R)),'url':f'https://github.com/{repo}/blob/{meta["sha"]}/{path}#L{start}-L{end}','source':source,'targetScope':scope,'observation':observation,'reviewMode':'MANUALLY_READ_FULL_METHOD'}
if __name__=='__main__':
 specs=json.loads(Path(sys.argv[1]).read_text());rows=[record(**s) for s in specs];out=D/sys.argv[2];assert not out.exists();out.write_text(json.dumps({'reviewed':len(rows),'rows':rows,'excluded':[]},ensure_ascii=False,indent=2)+'\n');print('Recorded',len(rows),'explicitly reviewed methods')
