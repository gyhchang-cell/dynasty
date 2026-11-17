"""Print exact complete source methods for human/LLM review; no review decisions or counts."""
from pathlib import Path
import json,sys,re
R=Path(__file__).resolve().parents[3];O=R/'docs/cod4/audit-20261022/legacy-migration-acceptance';sys.path.insert(0,str(Path(__file__).parent/'.work/python312'))
from tree_sitter import Language,Parser
import tree_sitter_java
parser=Parser(Language(tree_sitter_java.language()));idx={r['candidate_id']:r for r in map(json.loads,(O/'candidates.jsonl').read_text().splitlines())}
def walk(n):
 yield n
 for c in n.children:yield from walk(c)
for request in sys.argv[1:]:
 i,*extra=request.split(':');r=idx[i];raw=(R/r['private_file']).read_bytes();tree=parser.parse(raw)
 names=set(extra)|{r['method'],'serializeNBT','deserializeNBT','saveAdditional','loadAdditional','addAdditionalSaveData','readAdditionalSaveData','writeToNBT','readFromNBT','readCustomNBT','writeCustomNBT'}
 print('\nSOURCE',i,r['repo'],r['path'],r['revision'])
 for n in walk(tree.root_node):
  if n.type=='field_declaration': print(raw[n.start_byte:n.end_byte].decode())
  if n.type in ['method_declaration','constructor_declaration']:
   nm=n.child_by_field_name('name');name=raw[nm.start_byte:nm.end_byte].decode() if nm else ''
   if name in names:print('METHOD',n.start_point.row+1,n.end_point.row+1,raw[n.start_byte:n.end_byte].decode())
