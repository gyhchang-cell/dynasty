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
source=O/'helpers/halley-migration/batch-016/batch-016.json';rs=json.loads(source.read_text())['records']
B=Path(__file__).parent/'helpers/halley-migration/batch-016';blobs={}
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
(O/'halley016-field-integrity.json').write_text(json.dumps(declaration_checks,ensure_ascii=False,indent=2)+'\n')
# Actual independent owner/consumer judgments after complete context reading; method count is not credit.
choices={
0:'主责分5段完整读217唯一方法及14声明；确认UUID命名WorldSavedData才是长期研究真值，登录/维度同步重取，不把缺Clone误当数据丢失；成功登记mutation才减笔记，但handIn读取与扣主手currentItem不匹配。Set增量并集保未知历史字符串，UID组合变化不自动识别；SPECIES笔记没有成功register分支，TYP无界直接数组索引。实际研究owner+一次消费笔记合一，网络及profile/helper0额外。registerSpecies无直接dirty，不能承诺离线增量必刷盘；未见死亡同步入口，不宣称。',
1:'主责追到完整Genome/Chromosome/Bee父类读写、蜂箱canWork/doWork和queenWorkTick/produceStacks实际生产，计1遗传蜂物品恢复链。染色体坏allele按当前已知物种/默认模板补，但缺整槽仍null；列表顺序决定fallback上下文，空Genome与缺Genome不同。替换后新compound写有效UID丢未知原值，不是无损恢复。deprecatedAllele API未有本批实际填表证据，0额外；构造器/缓存/每染色体/样本health/helper不另计。batch015分析机仅电量兼容，这里是独立样本genome owner及产出消费者，分析状态父类支持不重计。',
2:'主责完整读实际玩家投信→邮资processed判定→邮箱WorldSavedData→取信/改附件写回链，计1独立已支付信件/附件托管owner。UUID equals与name hash/含name文件名不一致，改名不会据此自动迁旧箱；worldload清静态缓存不等于全时世界隔离。玩家deliver忽略doDeliver即使false也写；真实tile传true，本次未执行。先改目标副本PRC/清邮票再尝试入箱，上层成功才扣源，但并非原子事务或所有Count无损。通用InventoryUtil与meta外观/每附件0额外，不扩大到trader分支或原生磁盘flush。'
}
idxfile=O/'candidates.jsonl';idx={r['candidate_id']:r for r in map(json.loads,idxfile.read_text().splitlines())};added=[]
for i,e in verified.items():
 if i not in idx:
  q={k:e[k] for k in ('candidate_id','repo','revision','path','private_file','start_line','end_line','method','file_sha256','method_sha256','structural_fingerprint','source_url_or_coordinate','context','parse_has_error')};idx[i]=q;added.append(q)
with idxfile.open('a') as f:
 for q in added:f.write(json.dumps(q,ensure_ascii=False)+'\n')
rows=[]
for n,note in choices.items():
 r=rs[n];row=accepted(r['candidate_id'],r['family'],r['trigger'],r['input'],r['output'],r['observation']+' Master: '+note,r['limits']+' 固定上游源码静态审阅，不直接移植跨版本API，不宣称原生运行验证。未执行上游操作或游戏；固定Forestry源码不能替代当前Dynasty原生验收。',[e['candidate_id'] for e in r['evidence'][1:]])
 row['helper_provenance']={'path':str(source),'sha256':sha(source.read_bytes()),'helper_credit_before_master':0,'record_index':n};rows.append(row)
record(174,rows,files)
(O/'halley016-master-integration-review.json').write_text(json.dumps(dict(source=str(source),source_sha256=sha(source.read_bytes()),verified_unique_complete_ast_nodes=len(verified),verified_files=len(files),accepted_new=3,decisions=choices,credit_not_given_to_helpers_or_libraries=True,gui_started=False,production_java_changed=False,scope='217 unique complete supplied methods and14 declarations read in5 compact chunks; UUID research, genetic bee payload and player mail owners. Exact Git/source/AST validation grants no credit by itself. Common Forge and inventory helpers grant no independent credit. No runtime or production changes.'),ensure_ascii=False,indent=2)+'\n')
print('Verified',len(verified),'contexts',len(files),'files; explicit owner decisions3')
