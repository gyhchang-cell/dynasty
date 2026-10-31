"""Print complete AST methods from pinned local source; no decisions/credit."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parent/'.work/python312'))
from tree_sitter import Language,Parser
import tree_sitter_java
p=Parser(Language(tree_sitter_java.language()))
def walk(n):
 yield n
 for c in n.children:yield from walk(c)
f=Path(sys.argv[1]);raw=f.read_bytes();names=set(sys.argv[2:])
for n in walk(p.parse(raw).root_node):
 if n.type in ('method_declaration','constructor_declaration'):
  a=n.child_by_field_name('name')
  if a and raw[a.start_byte:a.end_byte].decode() in names:
   print(f'{f}:{n.start_point.row+1}-{n.end_point.row+1}\n'+raw[n.start_byte:n.end_byte].decode())
