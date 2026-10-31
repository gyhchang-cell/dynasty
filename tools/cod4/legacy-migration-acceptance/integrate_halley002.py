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
source=O/'helpers/halley-migration/batch-002/batch-002.json';rs=json.loads(source.read_text())['records']
B=Path(__file__).parent/'helpers/halley-migration/batch-002';blobs={}
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
choices={
0:'Master read complete29 supplied contexts: outer Death new representation preferred, inner UUID pair legacy preferred. Actual authenticated current-menu transfer preserves conflicts as remaining items, not a generic inventory accessor. No existing corpse/death owner family in main ledger. Full snapshot and corelib helpers one owner credit only; remove ignores removal reason and does not establish unload safety.',
1:'Master read complete10 supplied methods: profession/full-moon transforms actual villager additional fields and stores them through monster disk then restores to new villager. Selective cross-species domain distinct from player skill Clone and full horn snapshot. Old removed before new added and read occurs after replacement; no atomicity or full identity/trade preservation claim.',
2:'Master read supplied8 methods plus actual getSlots/getStackInSlot source. Concrete wooden-crafter owned inventory legacy index versus Slot with mutation rewrite, distinct existing general inventory helper. Empower copies tag but new Count defaults1; no full quantity preservation. EnderChest supplementary inventory remains player-owned, not copied into crafter.',
3:'Master read complete17 supplied methods including full mounted movement and payment: independently earned parts/modifier equipment reconstruction, different from ef2ac8 Goety broom carrier permission/return chain. Same broom item/entity forms and base/modifier readers all one credit. Only fully empty parts list defaulted; partial invalid list not padded, Count1 and cachedModifiers not invalidated in setter are explicit boundaries.',
4:'Master read complete supplied file-reader/writer/UI-request/removal contexts. Independent death-history files remain after corpse world entity is absent; actual creative-only restoration consumer distinguishes storage owner, not duplicate codec algorithm. Death.fromNBT shared with corpse0extra; no exactly-once history consumption claim, files directly rewritten, corrupt single file skipped and retained by cleanup.',
5:'Master read complete15 methods: actual resource acquisition copies full thrown stack into local inventory but subtracts1 from world source; deferred recipeId resolves in tick, writer only saves resolved recipe. Paid job stage/output/clear span ticks. Concrete machine task durable owner independent generic inventory or fluid converter; whole stage pipeline1, not per degradation clock. No new Java or native exploit claim.',
6:'Master read complete6 methods: actual consumable biome registry reference read by projectile then canonical Holder chosen for world PalettedContainer save, explicit chunk.setUnsaved. Distinct gameplay restoration owner, not generic registry utility. Invalid string can throw and unknown ID returnsnull; untraced parent projectile save not claimed lossless. Biome variants one family.',
7:'Master read complete9 methods: persistent weather enum drives real world weather consumption, missing/invalid name EMPTY. Exact reader has no damage-ordinal migration despite comment, so no invented fallback. onFill can dereference EMPTY.type null when no active type; thrown stack parent persistence untraced. All weather enum variants1.',
8:'Master read complete47 contexts and actual disk lifecycle registration. World shared chalice content is sole persistent owner; item/BE retain tankID only, library reflection/storage helpers0. Distinct from generic UUID inventory map: fluid fill/drain read/write world bank and replaceInnerFluid=false prevents local duplication. Same-amount fluid/tag updates omitted by shouldRefresh amount-only; static reset lifecycle not transferable to player Clone.',
9:'Master read complete47 contexts plus actual annotated field declarations. Spirit type/lifetime/swarm/player identity are selective payload, not full captured player entity: inner player represented as zombie+UUID/name only. Distinct actual spirit box owner and state reconstruction compared to full dragon horn/MobJar snapshots; box/entity/item/loot and reflectionhelpers all1. Spawn acknowledgement ignored before clear, targetSpiritId remains runtime identity even though saved; not a player durable key recipe.'}
idxfile=O/'candidates.jsonl';idx={r['candidate_id']:r for r in map(json.loads,idxfile.read_text().splitlines())};added=[]
for i,e in verified.items():
 if i not in idx:
  q={k:e[k] for k in ('candidate_id','repo','revision','path','private_file','start_line','end_line','method','file_sha256','method_sha256','structural_fingerprint','source_url_or_coordinate','context','parse_has_error')};idx[i]=q;added.append(q)
with idxfile.open('a') as f:
 for q in added:f.write(json.dumps(q,ensure_ascii=False)+'\n')
rows=[]
for n,note in choices.items():
 r=rs[n];row=accepted(r['candidate_id'],r['family'],r['trigger'],r['input'],r['output'],r['observation']+' Master: '+note,r['limits']+' Static source only; helper originals unchanged; corelib/CyclopsCore are pinned support, no binary build750 equivalence claim.',[e['candidate_id'] for e in r['evidence'][1:]])
 row['helper_provenance']={'path':str(source),'sha256':sha(source.read_bytes()),'helper_credit_before_master':0,'record_index':n};rows.append(row)
record(122,rows,files)
(O/'halley002-master-integration-review.json').write_text(json.dumps(dict(source=str(source),source_sha256=sha(source.read_bytes()),verified_unique_complete_ast_nodes=len(verified),verified_files=len(files),accepted_new=10,decisions=choices,credit_not_given_to_helpers_or_libraries=True,gui_started=False,production_java_changed=False,scope='Full supplied methods and named additional field/slot context read; not claiming all complete files manually reviewed or external runtime'),ensure_ascii=False,indent=2)+'\n')
print('Verified',len(verified),'contexts',len(files),'files; explicit owner decisions10')
