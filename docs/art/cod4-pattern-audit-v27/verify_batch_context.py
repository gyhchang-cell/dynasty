"""Validate full AST method boundaries and uncounted context evidence for selected batches.
Use the bundled Python runtime with build/pattern-research-python installed.
No game, asset or todo mutations. Source provenance verification is not runtime acceptance.
"""
import json,pathlib,hashlib,sys
D=pathlib.Path(__file__).resolve().parent;R=D.parents[2];sys.path.insert(0,str(R/'build/pattern-research-python'))
from tree_sitter import Language,Parser
import tree_sitter_java
parser=Parser(Language(tree_sitter_java.language()));totals={'acceptedMethods':0,'contextMethods':0,'contextFiles':0};seen=set()
for name in (sys.argv[1:] or ['manual-method-reviews-v36.json','manual-method-reviews-v37.json','manual-method-reviews-v38.json']):
 d=json.loads((D/name).read_text())
 for r in d['rows']:
  for role,items in [('acceptedMethods',[r]),('contextMethods',r.get('callContext',[])+r.get('supportingMethods',[])),('contextFiles',r.get('contextEvidence',[]))]:
   for c in items:
    assert c.get('local'),(name,c.get('method'),role)
    data=(R/c['local']).read_bytes();assert hashlib.sha256(data).hexdigest()==c.get('sourceSha256',c.get('sha256'))
    if role!='contextFiles':
     tree=parser.parse(data);todo=[tree.root_node];found=False
     while todo:
      n=todo.pop();todo.extend(n.children)
      if n.type in ['method_declaration','constructor_declaration'] and n.start_point.row+1==c['start'] and n.end_point.row+1==c['end']:
       assert n.child_by_field_name('name').text.decode()==c['method'];assert not n.has_error
       assert data[n.start_byte:n.end_byte].decode().strip()==c['source'].strip();found=True;break
     assert found,(name,c.get('method'),c['start'],c['end'])
    k=(role,c['local'],c.get('start'),c.get('end'))
    if k not in seen:totals[role]+=1;seen.add(k)
print(json.dumps(dict(status='PASS',**totals)))
