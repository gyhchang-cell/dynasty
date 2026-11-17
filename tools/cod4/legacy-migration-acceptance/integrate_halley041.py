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
source=O/'helpers/halley-migration/batch-041/batch-041.json';rs=json.loads(source.read_text())['records']
B=Path(__file__).parent/'helpers/halley-migration/batch-041';blobs={}
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
(O/'halley041-field-integrity.json').write_text(json.dumps(declaration_checks,ensure_ascii=False,indent=2)+'\n')
# Actual independent owner/consumer judgments after complete context reading; method count is not credit.
choices={0:'主责读79完整方法654行2块+9字段/初始化，已审040/038共享桥再次补读不加信用。PlayerRiftTracker独立持久玩家知识UUID集合→真实菜单snapshot→server useRift1，与040世界NPC关系对象和038身份资格分开，非同代码换键。addRift在无电/非灵体可用性检查前，永久已知不等同即时能传；CCA ALWAYS_COPY声明未读底层不说原生死亡验证。fetch遇未就绪或invalid record都iterator.remove，缺依赖会永久丢资格；reader无坏UUID逐项隔离。menu存snapshot，receiver只判断currenthandler类别不显式canUse，useRift只核snapshot与非source；target含dimension但实际用player.world找respawn/teleport，未消费目标维度。仅静态具体风险不称漏洞或运行复现。Attrition实际规则只解释consumer不适用本项目不加死亡惩罚。未知记录与保存桥040支持0。'}

idxfile=O/'candidates.jsonl';idx={r['candidate_id']:r for r in map(json.loads,idxfile.read_text().splitlines())};added=[]
for i,e in verified.items():
 if i not in idx:
  q={k:e[k] for k in ('candidate_id','repo','revision','path','private_file','start_line','end_line','method','file_sha256','method_sha256','structural_fingerprint','source_url_or_coordinate','context','parse_has_error')};idx[i]=q;added.append(q)
with idxfile.open('a') as f:
 for q in added:f.write(json.dumps(q,ensure_ascii=False)+'\n')
rows=[]
for n,note in choices.items():
 r=rs[n];row=accepted(r['candidate_id'],r['family'],r['trigger'],r['input'],r['output'],r['observation']+' Master: '+note,r['limits']+' 固定上游源码静态审阅，不直接移植跨版本API，不宣称原生运行验证。未执行上游操作或游戏；固定Requiem MC1.19.3源码不能替代Dynasty原生验收。',[e['candidate_id'] for e in r['evidence'][1:]])
 row['helper_provenance']={'path':str(source),'sha256':sha(source.read_bytes()),'helper_credit_before_master':0,'record_index':n};rows.append(row)
record(240,rows,files)
(O/'halley041-master-integration-review.json').write_text(json.dumps(dict(source=str(source),source_sha256=sha(source.read_bytes()),verified_unique_complete_ast_nodes=len(verified),verified_files=len(files),accepted_new=1,decisions=choices,credit_not_given_to_helpers_or_libraries=True,gui_started=False,production_java_changed=False,scope='79 full supplied methods plus9 declarations read in2 chunks. Durable player discovered-rift whitelist and real menu/server navigation one owner; world records and respawn strategy declarations reused zero credit. Static only.'),ensure_ascii=False,indent=2)+'\n')
print('Verified',len(verified),'contexts',len(files),'files; explicit owner decisions1')
