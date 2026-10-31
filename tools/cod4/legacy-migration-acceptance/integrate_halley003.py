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
source=O/'helpers/halley-migration/batch-003/batch-003.json';rs=json.loads(source.read_text())['records']
B=Path(__file__).parent/'helpers/halley-migration/batch-003';blobs={}
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
choices={0: 'Master read16 complete contexts: version mismatch and any invalid skill refund entire saved list, not partial recovery; on join learn(false) rebinds transient modifiers while GrantItem ignores repeat. One own capability Clone+skills+refund chain; no field-by-field credit. TreeReset writer lacks reader, ID parse exception and duplicate skill refund boundary retained.', 1: 'Master read27 complete contexts: explicit two own capabilities before isWasDeath guard, then death-only configured heart/difficulty mutators. Independent actual crystal progression owner from skill tree. AFK/time/pos/exempt excluded by serializer; never copy all ForgeData. Reflection valid workaround not suitable for project, no server guard/try-finally guarantee. One combined Clone family, world mirror same codec0.', 2: 'Master read full persisted pair/tick/process/randomization and actual mob attribute consumer: saved blight influences later difficulty multiplier while processed=false triggers rerandomization and replacement. Concrete mixed persistent/derived state owner differs from Botania417a routing settings even though two-scalar AST identical. Not merely different key; actual restart semantics and gameplay target traced. One all mob species, no helper count.', 3: 'Master read full pet pair/tick/paid HeartCrystal+XP interaction and modifier replacement. Different source/custody/lifetime from random mob difficulty: purchased cumulative bonus survives, refreshed is runtime, restored total replaces UUID modifier without paying again. Different from Botania36db mana spawner service despite one-float reader AST. Shared modifier helpers with mob0extra, missing capability can still cost item/XP.', 4: 'Master read25 complete methods: real crafted/upgrade item payload with typed nested serializers and equipment-change consumer, independently owned from skill capability. Both tags and every wrapper one family; invalid nested child can drop group, raw top-level type parse outside catch; copy upgrade merges two categories into one and retains old crafting tag potential duplicate. No complete arbitrary serializer preservation claim.', 5: 'Master read12 complete contexts: finite paid weapon poison payload plus remaining-use receipt, not transient player combat cooldown. Infinite -1 special and zero removes both tags. Actual attack handler not final damage success, no server guard; poisoning recipe new stack loses prior original components. One entire recipe/reader/consumer chain, distinct nested bonuses owner.'}
idxfile=O/'candidates.jsonl';idx={r['candidate_id']:r for r in map(json.loads,idxfile.read_text().splitlines())};added=[]
for i,e in verified.items():
 if i not in idx:
  q={k:e[k] for k in ('candidate_id','repo','revision','path','private_file','start_line','end_line','method','file_sha256','method_sha256','structural_fingerprint','source_url_or_coordinate','context','parse_has_error')};idx[i]=q;added.append(q)
with idxfile.open('a') as f:
 for q in added:f.write(json.dumps(q,ensure_ascii=False)+'\n')
rows=[]
for n,note in choices.items():
 r=rs[n];row=accepted(r['candidate_id'],r['family'],r['trigger'],r['input'],r['output'],r['observation']+' Master: '+note,r['limits']+' Static source only; helper originals unchanged; Daripher/Passive-Skill-Tree and SilentChaos512/ScalingHealth revisions are pinned; no direct cross-version API port or native runtime claim.',[e['candidate_id'] for e in r['evidence'][1:]])
 row['helper_provenance']={'path':str(source),'sha256':sha(source.read_bytes()),'helper_credit_before_master':0,'record_index':n};rows.append(row)
rows[2]['structural_collision_review']={'compared_candidate':'417a16c6384a498a940a','distinct_gameplay_owner_reason':choices[2],'reviewed_consumers':['DifficultyAffectedCapability.tick','MobDifficultyHandler.process/setEntityProperties','BlightHandler.startTrackingBlight']}
rows[3]['structural_collision_review']={'compared_candidate':'36db7ba873c72c837574','distinct_gameplay_owner_reason':choices[3],'reviewed_consumers':['PetEventHandler.onPetInteraction','StatBoosterItem.increasePetHp','PetHealthCapability.tick/addHealth']}
record(125,rows,files)
(O/'halley003-master-integration-review.json').write_text(json.dumps(dict(source=str(source),source_sha256=sha(source.read_bytes()),verified_unique_complete_ast_nodes=len(verified),verified_files=len(files),accepted_new=6,decisions=choices,credit_not_given_to_helpers_or_libraries=True,gui_started=False,production_java_changed=False,scope='Full supplied methods and named additional field/slot context read; not claiming all complete files manually reviewed or external runtime'),ensure_ascii=False,indent=2)+'\n')
print('Verified',len(verified),'contexts',len(files),'files; explicit owner decisions6')
