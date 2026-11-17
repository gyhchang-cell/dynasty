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
source=O/'helpers/halley-migration/batch-024/batch-024.json';rs=json.loads(source.read_text())['records']
B=Path(__file__).parent/'helpers/halley-migration/batch-024';blobs={}
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
(O/'halley024-field-integrity.json').write_text(json.dumps(declaration_checks,ensure_ascii=False,indent=2)+'\n')
# Actual independent owner/consumer judgments after complete context reading; method count is not credit.
choices={
0:'主责全文读162唯一方法/48声明所含图读写、创建扳手、恢复真实能量capability→模拟受能→实际投递链。readNetworkFromNBT虽然已在023 PlayerSave链作为坏子对象限制支持出现（hash相同如实保留），但图是独立持久业务对象、删除/新增/合并/拆图有自身dirty与连接表真值，不能从PlayerSave推导；新增完整图消费者确认独立族1，所有共同loader/ConnectionPair/各平台/每relay0额外。恢复坐标不含维度，世界静态data不因world参数独立隔离；缺Type保留null，而真实energy消费者按端点tile类型不是pair.type过滤，不能虚称自动迁移ENERGY。连接Mode未知异常，cachedNetwork/changeAmount非持久真值；实际range变化tick会删远端连接，故不是声称恢复后永不检查距离。equals同序任一端相同返回true且无hashCode，按静态风险记录非已复现。没有运行受能器/世界。',
1:'主责完整背包恢复→实际slot/filter/外部投递余量回写→自动捡拾消费，独立物品载荷所有者1，不按普通/虚空/filter/捡拾/slot重复计。固定28或1位置列表无Slot字段，未知id交原生ItemStack未再展开；超容量条目读不进下次重写会截去，无原NBT隔离恢复。含root tag但缺Filter时默认respectMeta=true被getBoolean覆盖false；没有tag根时保留构造默认，区分两种缺省。canInteractWith引用guard和SWAP/immovable支持正常持有，但close重取当前同类ItemBag，不重新核同一引用，不能宣称所有关闭交易安全。外部insert实际返回remain后才改源slot再重写，非跨handler磁盘原子事务；native handler异常未测。深层SlotFilter.slotClick/ContainerFilter交互未展开，限普通匹配分支，不把通用Items codec/各物品名字当新增。'
}

idxfile=O/'candidates.jsonl';idx={r['candidate_id']:r for r in map(json.loads,idxfile.read_text().splitlines())};added=[]
for i,e in verified.items():
 if i not in idx:
  q={k:e[k] for k in ('candidate_id','repo','revision','path','private_file','start_line','end_line','method','file_sha256','method_sha256','structural_fingerprint','source_url_or_coordinate','context','parse_has_error')};idx[i]=q;added.append(q)
with idxfile.open('a') as f:
 for q in added:f.write(json.dumps(q,ensure_ascii=False)+'\n')
rows=[]
for n,note in choices.items():
 r=rs[n];row=accepted(r['candidate_id'],r['family'],r['trigger'],r['input'],r['output'],r['observation']+' Master: '+note,r['limits']+' 固定上游源码静态审阅，不直接移植跨版本API，不宣称原生运行验证。未执行上游操作或游戏；固定AA 1.12.2源码不能替代当前Dynasty原生验收。',[e['candidate_id'] for e in r['evidence'][1:]])
 row['helper_provenance']={'path':str(source),'sha256':sha(source.read_bytes()),'helper_credit_before_master':0,'record_index':n};rows.append(row)
record(201,rows,files)
(O/'halley024-master-integration-review.json').write_text(json.dumps(dict(source=str(source),source_sha256=sha(source.read_bytes()),verified_unique_complete_ast_nodes=len(verified),verified_files=len(files),accepted_new=2,decisions=choices,credit_not_given_to_helpers_or_libraries=True,gui_started=False,production_java_changed=False,scope='162 unique supplied full methods and48 declarations read in5 complete context chunks. Graph independent business owner and real energy consumers distinguished from023 supporting reader; bag inventory/filter/paid transfer combined1. Common codec/accessor/library/network wrapper0 extra. No game, tests, production or original save operations.'),ensure_ascii=False,indent=2)+'\n')
print('Verified',len(verified),'contexts',len(files),'files; explicit owner decisions2')
