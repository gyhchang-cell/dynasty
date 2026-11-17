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
source=O/'helpers/halley-migration/batch-054/batch-054.json';rs=json.loads(source.read_text())['records']
B=Path(__file__).parent/'helpers/halley-migration/batch-053';blobs={}
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
(O/'halley054-field-integrity.json').write_text(json.dumps(declaration_checks,ensure_ascii=False,indent=2)+'\n')
# Actual independent owner/consumer judgments after complete context reading; method count is not credit.
choices={0: '主责已全文读177独立方法与88声明。比较Curios槽modifier生命周期26b804、配置reconcile3862、ToolBelt extra-slot5cbf：本项实际独立装备owner保完整最大槽库存且付耐久解锁amuletSlots，与并行gem镜像按相同keepInventory Clone，不重放onEquip；只计整链1。死亡inv.clear即使canDrop=false仍清，永久购买容量与掉落库存共包导致资格随死亡丢失，是字段分责负例。读slot只有上界负数危险，派生gem ordinal同样缺下界。setAmuletSlots无markDirty，不据静态序列化断言每次购买已落盘。', 1: '主责全文确认每种food的历史厌恶map，区别Diet acfdd的营养组衰减/属性UUID和SoL已吃奖励集合；独立真实玩法owner1而非同代码换键。read先重建map，未知Item跳过、缺list为空，Level不clamp；increase实际clamp不等于read clamp。isPersistent true使死亡也重写reader，仅hatredMap不含lastSickness反馈缓存。实际duration<=1服务端惩罚/加5不能等同消费成功receipt；不引入上游惩罚。', 2: '主责全文确认玩家携带BL实体登录重建而非一般Riding数据fix或列车路由。writeToNBTAtomically完整直接passenger载荷→read清队列→login readWorldEntity(true)→startRiding；一次1。断线mount取消保证保存时仍挂载，但未清恢复队列、未ack实体生成或骑乘，writer忽略未兑现queue，无严格一次交付。默认!wasDead只非死亡Clone，不误称真实死亡永久宠物保留。', 3: '主责全文确认付SPIRIT_FRUIT获得维度/坐标绑定祝福，实际死亡事件取消救命后clear资格。与Anthropophagy715a的真实死亡后按旧资格复制等级不同：本项不发生Clone保留，只有未死的持久有偿资格与一次消费路径。默认!wasDead，三坐标INT guard缺任一null但维度无注册校验；末尾clear中途异常有风险。源雕像是否仍存在不验证。writer新compound可正确去坐标，不能以复用旧compound风险诬称现行持续bug。不按坐标/药效/供品拆计。'}

idxfile=O/'candidates.jsonl';idx={r['candidate_id']:r for r in map(json.loads,idxfile.read_text().splitlines())};added=[]
for i,e in verified.items():
 if i not in idx:
  q={k:e[k] for k in ('candidate_id','repo','revision','path','private_file','start_line','end_line','method','file_sha256','method_sha256','structural_fingerprint','source_url_or_coordinate','context','parse_has_error')};idx[i]=q;added.append(q)
with idxfile.open('a') as f:
 for q in added:f.write(json.dumps(q,ensure_ascii=False)+'\n')
rows=[]
for n,note in choices.items():
 r=rs[n];row=accepted(r['candidate_id'],r['family'],r['trigger'],r['input'],r['output'],r['observation']+' Master: '+note,r['limits']+' 固定上游源码静态审阅，不直接移植跨版本API，不宣称原生运行验证。未执行上游操作或游戏；固定TheBetweenlands MC1.12.2/mod3.9.6源码静态研究，不移植平台API或上游死亡惩罚，不等同Dynasty原生验收。',[e['candidate_id'] for e in r['evidence'][1:]])
 row['helper_provenance']={'path':str(source),'sha256':sha(source.read_bytes()),'helper_credit_before_master':0,'record_index':n};rows.append(row)
record(262,rows,files)
(O/'halley054-master-integration-review.json').write_text(json.dumps(dict(source=str(source),source_sha256=sha(source.read_bytes()),verified_unique_complete_ast_nodes=len(verified),verified_files=len(files),accepted_new=4,decisions=choices,credit_not_given_to_helpers_or_libraries=True,gui_started=False,production_java_changed=False,scope='177 unique complete method/constructor contexts and88 unique declarations read. Framework and mirrors support0. Four independent gameplay owner chains accepted after semantic comparison; no runtime claims.'),ensure_ascii=False,indent=2)+'\n')
print('Verified',len(verified),'contexts',len(files),'files; explicit owner decisions4')
