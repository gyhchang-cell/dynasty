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
source=O/'helpers/halley-migration/batch-022/batch-022.json';rs=json.loads(source.read_text())['records']
B=Path(__file__).parent/'helpers/halley-migration/batch-022';blobs={}
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
(O/'halley022-field-integrity.json').write_text(json.dumps(declaration_checks,ensure_ascii=False,indent=2)+'\n')
# Actual independent owner/consumer judgments after complete context reading; method count is not credit.
choices={
0:'主责分3段全文读99唯一方法与17声明。Reaper独立持久仪式任务和显式旧position回退计1，虽内嵌021VillageManager但业务owner是位置/祭火/图腾/倒计时→Boss生成，不重复地产声望建筑任务。新writer totems是list，reader getCompound再toStream强转list，静态类型冲突准确，不声称原生读盘复现。任一富字段存在就新分支，partial新格式无逐字段回退；旧回退必须仍有中央InfernalFlame才能继续。任务tick异常catch后丢任务，spawn返回null仍完成，非安全消费事务。父容器/坐标codec/闪电/分支不分计，未展开Boss战斗AI。',
1:'主责完整读CivilRegistry entries→JSON Text→世界存储→书页请求/响应→实际render，独立不可由现有居民图重建的历史所有者计1。死亡/婚姻只两个实际追加来源，不按事件/书页数计。VillageManager每维度独立id，CivilRegistry主世界仅village int ID文件键，条件性跨维同ID共享而非已复现串档。缺entries/错type直接cast、坏JSON无隔离；Text JSON保留和020墓碑纯名不同；from无下界且索引分页无snapshot，不能当完整历史事务。客户端open清cache证实它不是历史真值，通用helpers0。',
2:'主责完整读外置UUID→GlobalPos已保存注册表及实际追踪物品持久targetUUID/position→原生指南针provider和同维距离消费，计具体跟踪道具数据所有者1；MaxSizeHashMap泛用缓存和每UUID/维度/位置键均0额外。不等同于019家谱身份或020转换载荷。decodeGlobalPos日志后null过滤可兼容坏位置但坏UUID仍无catch；set/update不dirty，仅remove dirty，支持源码搜索未见外部remove调用，不保证更新落盘。死亡仍写最后位置，换目标或查不到不清旧position，允许陈旧位置是实际载荷边界，不能拿来证明永久进度可靠。有限插入序map不是LRU，重载HashMap遍历也不承诺淘汰顺序保存。未打开GUI或验证原生角度算法。'
}
idxfile=O/'candidates.jsonl';idx={r['candidate_id']:r for r in map(json.loads,idxfile.read_text().splitlines())};added=[]
for i,e in verified.items():
 if i not in idx:
  q={k:e[k] for k in ('candidate_id','repo','revision','path','private_file','start_line','end_line','method','file_sha256','method_sha256','structural_fingerprint','source_url_or_coordinate','context','parse_has_error')};idx[i]=q;added.append(q)
with idxfile.open('a') as f:
 for q in added:f.write(json.dumps(q,ensure_ascii=False)+'\n')
rows=[]
for n,note in choices.items():
 r=rs[n];row=accepted(r['candidate_id'],r['family'],r['trigger'],r['input'],r['output'],r['observation']+' Master: '+note,r['limits']+' 固定上游源码静态审阅，不直接移植跨版本API，不宣称原生运行验证。未执行上游操作或游戏；固定MCA Reborn源码不能替代当前Dynasty原生验收。',[e['candidate_id'] for e in r['evidence'][1:]])
 row['helper_provenance']={'path':str(source),'sha256':sha(source.read_bytes()),'helper_credit_before_master':0,'record_index':n};rows.append(row)
record(196,rows,files)
(O/'halley022-master-integration-review.json').write_text(json.dumps(dict(source=str(source),source_sha256=sha(source.read_bytes()),verified_unique_complete_ast_nodes=len(verified),verified_files=len(files),accepted_new=3,decisions=choices,credit_not_given_to_helpers_or_libraries=True,gui_started=False,production_java_changed=False,scope='99 unique complete supplied methods and17 declarations read in3 compact full-context chunks. Official MCA Reborn fixed source; reaper ritual legacy position, civil history JSON and actual tracker gameplay payload reviewed independently; generic cache and shared019-021 helper contexts0 additional credit. Platform wrappers, generic field codecs and shared owner helpers0 extra. No game, tests, production or original save operations.'),ensure_ascii=False,indent=2)+'\n')
print('Verified',len(verified),'contexts',len(files),'files; explicit owner decisions3')
