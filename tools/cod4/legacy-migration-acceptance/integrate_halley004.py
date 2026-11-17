"""Master's explicit semantic decisions after full supplied-context review. Idempotent; no helper edits."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib
from review_batch import accepted,record,O
sys.path.insert(0,str(Path(__file__).parent/'.work/python312'))
from tree_sitter import Language,Parser
import tree_sitter_java
parser=Parser(Language(tree_sitter_java.language()))
def sha(b):return hashlib.sha256(b).hexdigest()
def walk(n):
 yield n
 for c in n.children:yield from walk(c)
def norm(n,raw):
 ids={};tokens=[]
 for a in walk(n):
  if a.children or a.type in ('line_comment','block_comment'):continue
  t=raw[a.start_byte:a.end_byte].decode()
  if a.type=='identifier':t=ids.setdefault(t,'I'+str(len(ids)))
  elif 'literal' in a.type or a.type=='string_fragment':t=a.type
  tokens.append(t)
 return sha(' '.join(tokens).encode())
source=O/'helpers/halley-migration/batch-004/batch-004.json';rs=json.loads(source.read_text())['records']
B=Path(__file__).parent/'helpers/halley-migration/batch-004';blobs={}
for s in json.loads((B/'source-manifest.json').read_text()):
 p=B/'provenance'/s['repo'].replace('/','__');cb=(p/'commit.json').read_bytes();tb=(p/'tree.json').read_bytes();commit=json.loads(cb);tree=json.loads(tb)
 assert sha(cb)==s['commit_metadata_sha256'] and sha(tb)==s['tree_metadata_sha256']
 assert commit['sha']==s['commit'] and commit['tree']['sha']==s['git_tree']==tree['sha'] and not tree.get('truncated')
 blobs[s['repo']]={x['path']:x['sha'] for x in tree['tree'] if x['type']=='blob'}
verified={};files=set()
for r in rs:
 for e in r['evidence']:
  raw=Path(e['private_file']).read_bytes();assert sha(raw)==e['file_sha256'];assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==e['source_blob']==blobs[e['repo']][e['path']]
  nodes=[n for n in walk(parser.parse(raw).root_node) if n.type in ('method_declaration','constructor_declaration') and n.start_point.row+1==e['start_line'] and n.end_point.row+1==e['end_line']];assert len(nodes)==1
  n=nodes[0];assert not n.has_error and raw[n.start_byte:n.end_byte].decode()==e['context'] and sha(e['context'].encode())==e['method_sha256'] and norm(n,raw)==e['structural_fingerprint']
  assert sha((e['repo']+e['revision']+e['path']+str(n.start_byte)).encode())[:20]==e['candidate_id'];verified[e['candidate_id']]=e;files.add(e['private_file'])
# Actual independent owner/consumer judgments, not same-library or method-count credit.
choices={0:'Master read all31 supplied complete contexts including platform mirrors0: actual carried player root snapshot transfers object custody before world removal, death keepInventory/End nondeath handoff versus placement and clear. Distinct player-owned carry domain and placement loss policy from corpse/spiritbox. Invalid type/script throws; entity-create failure clears local snapshot into cloud placeholder; add/set result not confirmed before unique custody cleared. Setter stamps new selected/tick before selected inventory copy; no whitelist template from entire interaction domain.', 1:'Master read all supplied tool inventory writer/reader and real upgrade/swap/menu consumers: item-owned stable slot format, first matching duplicate reader/writer, hidden out-of-capacity records retained; upgrade copies stack, sewing merge prioritizes new output fields. Distinct long-lived carried tool list owner from EvilCraft station and from player extra slot. One all bag sizes/GUI/upgrade chain. External SewingKit superclass not reviewed; no count guarantee from sewing.', 2:'Master read complete extra-slot serializer, attach/Clone/drop/tick/config-disable-return and Forge support methods: player owns belt stack whereas belt owns tools; LivingDrops removes loss/vanishing before Clone carries remainder, missing target cap drops. This actual equipment owner and disable-return/preceding-drop semantics differ from ScalingHealth stat Clone and existing Curios wrapper. One lifecycle all players/stands; support codec0. Shared stack ref, original not cleared in Clone; no crash atomicity or event priority proof; oldPlayer.revive distinct reviveCaps.'}
idxfile=O/'candidates.jsonl';idx={r['candidate_id']:r for r in map(json.loads,idxfile.read_text().splitlines())};added=[]
for i,e in verified.items():
 if i not in idx:
  q={k:e[k] for k in ('candidate_id','repo','revision','path','private_file','start_line','end_line','method','file_sha256','method_sha256','structural_fingerprint','source_url_or_coordinate','context','parse_has_error')};idx[i]=q;added.append(q)
with idxfile.open('a') as f:
 for q in added:f.write(json.dumps(q,ensure_ascii=False)+'\n')
rows=[]
for n,note in choices.items():
 r=rs[n];row=accepted(r['candidate_id'],r['family'],r['trigger'],r['input'],r['output'],r['observation']+' Master: '+note,r['limits']+' Static source only; helper originals unchanged; CarryOn/ToolBelt/Forge pinned sources; declared Forge47.1.3 sourcejar differs in bytes and source-git release equality not asserted. No direct cross-version API port/native runtime claim.',[e['candidate_id'] for e in r['evidence'][1:]])
 row['helper_provenance']={'path':str(source),'sha256':sha(source.read_bytes()),'helper_credit_before_master':0,'record_index':n};rows.append(row)
record(128,rows,files)
(O/'halley004-master-integration-review.json').write_text(json.dumps(dict(source=str(source),source_sha256=sha(source.read_bytes()),verified_unique_complete_ast_nodes=len(verified),verified_files=len(files),accepted_new=3,decisions=choices,credit_not_given_to_helpers_or_libraries=True,gui_started=False,production_java_changed=False,scope='Full supplied methods and named additional field/slot context read; not claiming all complete files manually reviewed or external runtime'),ensure_ascii=False,indent=2)+'\n')
print('Verified',len(verified),'contexts',len(files),'files; explicit owner decisions3')
