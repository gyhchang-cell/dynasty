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
source=O/'helpers/halley-migration/batch-053/batch-053.json';rs=json.loads(source.read_text())['records']
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
(O/'halley053-field-integrity.json').write_text(json.dumps(declaration_checks,ensure_ascii=False,indent=2)+'\n')
# Actual independent owner/consumer judgments after complete context reading; method count is not credit.
choices={0: '主责全文审227独立AST方法（嵌套父子源码有重合不重复信用）及134相关字段/初始化；其余ItemRegistry food/装备静态声明只机械核验不称全读。旧gecko/firefly ItemMobFixer重建new stack仅Entity.id，Count/原tag/caps并未merge，两个旧ID一族负例1；MissingMappings只目标remap不能替代NBTfix的payload。真正createEntityFromNBT改新UUID清速度，spawnCapturedEntity忽略world.spawnEntity返回true/false，调用端仍shrink。借鉴别名不能重造栈，不移植上游跨版本DataFixer。', 1: '主责全文已核固定历史表、原地id rewrite、真实TE注册及Purifier继承库存和water/progress完整reader/writer/update；保其余NBT的观察有效。但该条转换仅固定旧名→新名，33映射项/注册与继承consumer不令其成为额外独立payload迁移；作为相关支持0，不以改ID表凑门槛。', 2: '手册物品真实持久discovery集合、多手册union与server付材料发现完整1。reader clear后未知AspectType可null仍进列表，writer随后type.writeToNBT可能NPE；未知item key null会write时删除。completed按list长度而非当前集合差，旧null/重复可能误判END/LAST；merge直接共享otherTypes列表，临时merged发现可能先改原container引用但不自动各provider持久，后续addDiscoveryToContainers才写所有手册。非playerClone能力，不把通用Discovery接口再计。', 3: '世界静态随机元素分配是独立world truth owner1，不是手册用户已发现子字段。load先清map、逐item读全部aspects，一未知type整item跳过；update只跳过已恢复item并补新注册，坏item会重随机而非隔离保留。hasKey entries无typedguard然后cast可能ClassCast/NPE；loadAndPopulate已有元素不随seed刷新，保世界既有值的规则可借鉴。实际World capability read/write与Infuser使用匹配数量和入槽完整。通用AspectContainer余额schema只支持0，本批不作为另一个独立profile计数。'}

idxfile=O/'candidates.jsonl';idx={r['candidate_id']:r for r in map(json.loads,idxfile.read_text().splitlines())};added=[]
for i,e in verified.items():
 if i not in idx:
  q={k:e[k] for k in ('candidate_id','repo','revision','path','private_file','start_line','end_line','method','file_sha256','method_sha256','structural_fingerprint','source_url_or_coordinate','context','parse_has_error')};idx[i]=q;added.append(q)
with idxfile.open('a') as f:
 for q in added:f.write(json.dumps(q,ensure_ascii=False)+'\n')
rows=[]
for n,note in choices.items():
 r=rs[n];row=accepted(r['candidate_id'],r['family'],r['trigger'],r['input'],r['output'],r['observation']+' Master: '+note,r['limits']+' 固定上游源码静态审阅，不直接移植跨版本API，不宣称原生运行验证。未执行上游操作或游戏；固定TheBetweenlands MC1.12.2/mod3.9.6源码静态研究，不移植平台API或上游死亡惩罚，不等同Dynasty原生验收。',[e['candidate_id'] for e in r['evidence'][1:]])
 if n==1:row['status']='rejected'
 row['helper_provenance']={'path':str(source),'sha256':sha(source.read_bytes()),'helper_credit_before_master':0,'record_index':n};rows.append(row)
record(260,rows,files)
(O/'halley053-master-integration-review.json').write_text(json.dumps(dict(source=str(source),source_sha256=sha(source.read_bytes()),verified_unique_complete_ast_nodes=len(verified),verified_files=len(files),accepted_new=3,decisions=choices,credit_not_given_to_helpers_or_libraries=True,gui_started=False,production_java_changed=False,scope='227 distinct complete supplied method contexts read;134 relevant declarations read. All422 declaration hashes mechanically verified only; unrelated ItemRegistry constant declarations not claimed read.3 accepted independent gameplay owners; pure TE ID table1 support/rejected no credit.'),ensure_ascii=False,indent=2)+'\n')
print('Verified',len(verified),'contexts',len(files),'files; explicit owner decisions3')
