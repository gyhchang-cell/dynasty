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
source=O/'helpers/halley-migration/batch-047/batch-047.json';rs=json.loads(source.read_text())['records']
B=Path(__file__).parent/'helpers/halley-migration/batch-047';blobs={}
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
declaration_checks=[]
for r in rs:
 for e in r.get('source_declarations',[]):
  raw=Path(e['source']).read_bytes();assert sha(raw)==e['sourceSha256']
  assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==e['source_blob']==blobs[e['repo']][e['path']]
  ns=[n for n in walk(parser.parse(raw).root_node) if n.type in ('field_declaration','static_initializer') and n.start_point.row+1==e['start'] and n.end_point.row+1==e['end']]
  assert len(ns)==1
  n=ns[0];assert not n.has_error and raw[n.start_byte:n.end_byte].decode()==e['context'] and sha(e['context'].encode())==e['excerptSha256'] and norm(n,raw)==e['normalizedSha256']
  declaration_checks.append(dict(path=e['source'],start=e['start'],end=e['end'],context_sha256=e['excerptSha256'],credit=0));files.add(e['source'])
(O/'halley047-field-integrity.json').write_text(json.dumps(declaration_checks,ensure_ascii=False,indent=2)+'\n')
# Actual independent owner/consumer judgments after complete context reading; method count is not credit.
choices={0: '主责全文审180独立方法2372行与70声明（三条共享者只读/记一次）。实际dropAll前按条件/slot暂存原ItemStack引用并移空，dropAll后原slot恢复，copyFrom再复制死亡后剩余inventory；alive参数未过滤，选择发生在死亡阶段。和CorpseComplex bc41...比较：本例power条件临时抽取/恢复和额外能力仓库onLost链，不是同代码换键，不拆每slot/尺寸/物品；合并为一个死亡库存责任族。InventoryPower复合tag缺型返回不清旧，正确型先clear读；drop先remove再原生spawn，vanishing只删，未核成功回滚；recoverable onLost offerOrDrop但不clear可能重复callbacks风险。holder磁盘重载旧power onLost会触发副作用，不能泛拷ForgeData。nativeInventories/PlayerInventory.clone细节及CCA未全文审，明确静态边界不称游戏实证。', 1: '独立游戏entity_set资格集合：Entities永久UUID与TempEntities临时成员同时写，截止时间map不写；磁盘onAdded显式剔除临时UUID并clear临时集合，网络fromTag(false)不调用同清理。removedTemps首tick同步并return；剩余TTL不是跨加载续期。add_to_set真实注册动作/positive time_limit与in_set条件消费者已全文读，非纯容器。ENTITY_LOAD按当前可查世界实体校验，未加载目标也可能被删（不force chunk），destructive unload移除但Player特判不移除；onRemove可拿null实体。原生NbtHelper UUID解码异常未包catch；未知旧payload不保留。永久/临时同容器必须按语义过滤正是本修复边界，不把通用UUID读写/holder重复算。', 2: '独立旧PAL power_source授予所有权撤销→每PowerType ID source重建与ShouldRefresh持久标记链1，不拆飞行等能力。实际onAdded仅撤本ability的legacy source；constructor以type ID获新source，serverTick先refresh(true)清flag并return，随后tick按active/hasAbility grant/revoke。onRemoved设refresh=true，onLost撤当前source，新增onGained直接grant但磁盘reader不调onGained；不能把旧来源撤销说成同tick即时恢复。真实LoginMixin remove/respawn head调旧onRemoved，新角色onRespawn仅!alive，holder ALWAYS_COPY为声明，CCA/PAL库机制待helper补全，不能断言底层权属无竞态。与046来源资格迁移不同：具体既有PAL来源撤销/能力实际授权消费而非层选择或换键列表；共享holder不另计。'}

idxfile=O/'candidates.jsonl';idx={r['candidate_id']:r for r in map(json.loads,idxfile.read_text().splitlines())};added=[]
for i,e in verified.items():
 if i not in idx:
  q={k:e[k] for k in ('candidate_id','repo','revision','path','private_file','start_line','end_line','method','file_sha256','method_sha256','structural_fingerprint','source_url_or_coordinate','context','parse_has_error')};idx[i]=q;added.append(q)
with idxfile.open('a') as f:
 for q in added:f.write(json.dumps(q,ensure_ascii=False)+'\n')
rows=[]
for n,note in choices.items():
 r=rs[n];row=accepted(r['candidate_id'],r['family'],r['trigger'],r['input'],r['output'],r['observation']+' Master: '+note,r['limits']+' 固定上游源码静态审阅，不直接移植跨版本API，不宣称原生运行验证。未执行上游操作或游戏；固定Origins/Apoli MC1.20.2源码静态研究；外部CCA/PAL原生机制尚未在本批全文核验，不能替代Dynasty死亡/存档验收。',[e['candidate_id'] for e in r['evidence'][1:]])
 row['helper_provenance']={'path':str(source),'sha256':sha(source.read_bytes()),'helper_credit_before_master':0,'record_index':n};rows.append(row)
record(252,rows,files)
(O/'halley047-master-integration-review.json').write_text(json.dumps(dict(source=str(source),source_sha256=sha(source.read_bytes()),verified_unique_complete_ast_nodes=len(verified),verified_files=len(files),accepted_new=3,decisions=choices,credit_not_given_to_helpers_or_libraries=True,gui_started=False,production_java_changed=False,scope='180 unique supplied full methods and70 declarations read in7 chunks. Three actual owners: conditional death inventory and extra cargo combined, durable membership vs TTL purge, legacy PAL ability ownership refresh. Shared holder and per-slot/per-ability clones zero extra credit.'),ensure_ascii=False,indent=2)+'\n')
print('Verified',len(verified),'contexts',len(files),'files; explicit owner decisions3')
