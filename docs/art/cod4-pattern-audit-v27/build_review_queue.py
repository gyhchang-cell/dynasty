"""AST method inventory. Candidates do not count as reviewed references."""
from pathlib import Path
import sys,re,json,hashlib,collections
D=Path(__file__).resolve().parent;R=D.parents[2];sys.path.insert(0,str(R/'build/pattern-research-python'))
from tree_sitter import Language,Parser
import tree_sitter_java
language=Language(tree_sitter_java.language())
parser=Parser(language)
roots=[R/'build/creature-reference-1000',R/'build/item-use-references']
methods=[];seen=set();repo_seen=set()
for root in roots:
 for repo_dir in sorted(root.iterdir()):
  meta=repo_dir/'source.json'
  if not meta.exists():continue
  j=json.loads(meta.read_text());repo=j.get('repo');revision=j.get('sha',j.get('commit'))
  if not repo or not revision:continue
  for p in sorted(repo_dir.rglob('*.java')):
   rel=p.relative_to(repo_dir).as_posix();identity=(repo,revision,rel)
   if identity in repo_seen:continue
   repo_seen.add(identity)
   if not re.search(r'(client|particle|render|vfx|effect|fx|visual_effects)/',rel,re.I):continue
   if re.search(r'(model|datagen|data|mixin|gui|screen|config|test|jei|rei|emi|compat)/',rel,re.I):continue
   data=p.read_bytes();tree=parser.parse(data);stack=[tree.root_node]
   while stack:
    node=stack.pop();stack.extend(reversed(node.children))
    if node.type not in ('method_declaration','constructor_declaration'):continue
    body=node.child_by_field_name('body');name=node.child_by_field_name('name')
    if not body or not name or node.has_error:continue
    text=data[node.start_byte:node.end_byte].decode('utf8',errors='replace');plain=re.sub(r'/\*.*?\*/|//[^\n]*','',text,flags=re.S)
    lines=[s.strip() for s in plain.splitlines() if s.strip()]
    if len(lines)<9:continue
    subnodes=[body];calls=[]
    while subnodes:
     sub=subnodes.pop();subnodes.extend(sub.children)
     if sub.type=='method_invocation':
      called=sub.child_by_field_name('name')
      if called:calls.append(called.text.decode())
    ops=[x for x in calls if re.search(r'render|vertex|addVertex|pos$|color|alpha|scale|rotate|Rotation|mulPose|translate|Sprite|[uU][vV]|setAge|setLifetime|setParticle|remove|cross|normalize|sin|cos|lerp|lerpDegrees|atan2|curve|beam|light',x,re.I)]
    if len(ops)<4 or len(set(ops))<3:continue
    # ID/color changes alone cannot create distinct reference methods.
    body_text=data[body.start_byte:body.end_byte].decode('utf8',errors='replace')
    body_text=re.sub(r'/\*.*?\*/|//[^\n]*','',body_text,flags=re.S)
    normalized=re.sub(r'"(?:\\.|[^"\\])*"','"ID"',body_text)
    normalized=re.sub(r'\b0x[0-9a-fA-F]+[Ll]?\b','COLOR',normalized)
    normalized=re.sub(r'\b(?:0\.\d+|\d+\.\d*|\d+)[fFdDlL]?\b','N',normalized)
    normalized=re.sub(r'\b[A-Za-z_$][\w$]*\b',lambda m:m.group() if m.group() in set(calls)|{'if','else','for','while','return','new','try','finally','switch','case','true','false','null','this','super'} else 'v',normalized)
    norm=re.sub(r'\s+','',normalized);digest=hashlib.sha256(norm.encode()).hexdigest()
    if digest in seen:continue
    seen.add(digest)
    methods.append({'id':len(methods)+1,'repo':repo,'revision':revision,'path':rel,'method':name.text.decode(),'start':node.start_point.row+1,'end':node.end_point.row+1,'sourceSha256':hashlib.sha256(data).hexdigest(),'semanticHash':digest,'local':str(p.relative_to(R)),'url':f'https://github.com/{repo}/blob/{revision}/{rel}#L{node.start_point.row+1}-L{node.end_point.row+1}','operations':dict(collections.Counter(ops)),'source':text})
(D/'method-candidates.json').write_text(json.dumps({'status':'CANDIDATES_NOT_REVIEWED','count':len(methods),'methods':methods},ensure_ascii=False,indent=2)+'\n');print('AST candidates:',len(methods),'repositories:',len(set(r['repo'] for r in methods)))
print(collections.Counter(r['repo'] for r in methods))
