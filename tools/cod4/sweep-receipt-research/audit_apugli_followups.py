"""Check fixed source objects and complete ranges; never infer semantic credit.

Run with bundled Python 3.12. Helper directories remain read-only.
"""
from pathlib import Path
import sys, json, hashlib, datetime
assert sys.version_info[:2] == (3, 12)
R = Path(__file__).resolve().parents[3]
O = R / 'docs/cod4/audit-20261022/sweep-receipt-research'
H = O / 'helpers/apugli-rpginventory'
C = R / 'tools/cod4/sweep-receipt-research/helpers/apugli-rpginventory/sources/MerchantPug__Apugli'
sys.path.insert(0, str(R/'tools/cod4/legacy-migration-acceptance/.work/python312'))
from tree_sitter import Language, Parser
import tree_sitter_java
parser = Parser(Language(tree_sitter_java.language()))
sha = lambda b: hashlib.sha256(b).hexdigest()
obj = lambda kind, b: hashlib.sha1(kind+b' '+str(len(b)).encode()+b'\0'+b).hexdigest()
def walk(n):
    yield n
    for child in n.children:
        yield from walk(child)

trees, commits, objects = {}, {}, {}
for root, cf, tf in [('tree','commit.json','git-tree.json'),
                     ('behavior-tree-003','behavior-commit-003.json','behavior-tree-003.json'),
                     ('next-tree-003','next-commit-003.json','next-tree-003.json'),
                     ('architectury116-tree-004','architectury116-commit-004.json','architectury116-tree-004.json')]:
    commit = json.loads((C/cf).read_text())
    tree = json.loads((C/tf).read_text())
    assert not tree['truncated'] and tree['sha'] in (commit['sha'],commit['commit']['tree']['sha'])
    entries = {e['path']:e for e in tree['tree']}
    for directory in ['']+[p for p,e in entries.items() if e['type']=='tree']:
        children=[e for p,e in entries.items() if ('' if str(Path(p).parent)=='.' else str(Path(p).parent))==directory]
        children.sort(key=lambda e:Path(e['path']).name+('/' if e['type']=='tree' else ''))
        data=b''.join((e['mode'].lstrip('0')+' '+Path(e['path']).name).encode()+b'\0'+bytes.fromhex(e['sha']) for e in children)
        assert obj(b'tree',data)==(commit['commit']['tree']['sha'] if not directory else entries[directory]['sha']), directory
    trees[root]=entries; commits[root]=commit['sha']
    objects[root]={'revision':commit['sha'],'commit_metadata_sha256':sha((C/cf).read_bytes()),'tree_metadata_sha256':sha((C/tf).read_bytes()),'root_tree':commit['commit']['tree']['sha']}

spans=set(); files={}; count=0; inputs={}
for name in ['batch-002.json','batch-003.json','batch-004.json','batch-005.json','excluded-005.json']:
    inputs[name]=sha((H/name).read_bytes())
    for entry in json.loads((H/name).read_text())['entries']:
        for e in [entry,*entry['evidence']]:
            path=R/e['source_local']; raw=path.read_bytes()
            root=path.relative_to(C).parts[0]
            assert e['revision']==commits[root]
            assert sha(raw)==e['source_sha256'] and obj(b'blob',raw)==trees[root][e['path']]['sha']
            assert sha(e['excerpt'].encode())==e['snippet_sha256']
            assert '\n'.join(raw.decode().splitlines()[e['line']-1:e['end_line']]).strip()=='\n'.join(e['excerpt'].splitlines()).strip()
            nodes=[n for n in walk(parser.parse(raw).root_node) if n.type in ('method_declaration','constructor_declaration') and n.start_point.row+1<=e['line']<=n.end_point.row+1 and n.end_point.row+1==e['end_line']]
            assert len(nodes)==1 and not nodes[0].has_error, (name,e['path'],e['line'])
            spans.add((e['source_local'],e['line'],e['end_line']));files[e['source_local']]=e['source_sha256'];count+=1
report={'generated_at':datetime.datetime.now().astimezone().isoformat(),'input_hashes':inputs,'source_objects':objects,'checked_ranges_including_repeated_primary':count,'unique_ranges':len(spans),'unique_source_files':len(files),'source_hashes':files,'errors':[],'awarded_credit':0,'helper_files_modified':False,'upstream_code_executed':False,'boundary':'Only byte/range/AST/source-object integrity; semantic review decisions remain separately authored.'}
(O/'apugli-followups-main-integrity.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ('checked_ranges_including_repeated_primary','unique_ranges','unique_source_files','errors','awarded_credit')}))
