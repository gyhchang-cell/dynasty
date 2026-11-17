"""Publish only individually reviewed, deduplicated sites; extraction never grants acceptance.

Reads existing pinned source caches without modifying them. --verify-missing-pins checks
raw GitHub bytes where the cache has no Git tree; only verification receipts are saved.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import argparse, collections, datetime, hashlib, json, re, subprocess
BASE=Path(__file__).resolve().parent; ROOT=BASE.parents[2]; E=BASE/'evidence'
sha=lambda value:hashlib.sha256(value).hexdigest()
MASK=re.compile(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'')
args=argparse.ArgumentParser();args.add_argument('--verify-missing-pins',action='store_true');args=args.parse_args()
candidates=json.loads((E/'armor-reference-candidates.json').read_text())
reviews=json.loads((BASE/'research/reviewed-sites.json').read_text());by_index={r['candidate_index']:r for r in reviews}
assert len(by_index)==len(reviews)
remote_path=E/'armor-remote-pin-verification.json'
remote=json.loads(remote_path.read_text()) if remote_path.exists() else {}
trees={};missing={};accepted=[];ledger=[]
for i,c in enumerate(candidates):
 review=by_index.get(i);decision=review['decision'] if review else 'not_accepted_unreviewed'
 entry={k:v for k,v in c.items() if k not in ('excerpt','actions','item_scoped')}
 entry.update(candidate_index=i,decision=decision)
 if review:
  assert review['snippet_sha256']==c['snippet_sha256']
  entry['observation']=review['observation']
 ledger.append(entry)
 if decision!='accepted':continue
 source=ROOT/c['source_local'];raw_bytes=source.read_bytes();raw=source.read_text()
 assert sha(raw_bytes)==c['source_sha256'],source
 start=raw.find(c['excerpt']);assert start>=0,source
 assert raw[:start].count('\n')+1==c['line'],source
 assert raw[:start+len(c['excerpt'])].count('\n')+1==c['end_line'],source
 assert sha(re.sub(r'\s+','',MASK.sub('',c['excerpt'])).encode())==c['snippet_sha256']
 folder=next(p for p in source.parents if (p/'source.json').exists());meta=json.loads((folder/'source.json').read_text())
 assert meta['repo']==c['repo'] and meta['sha']==c['revision']
 key=f"{c['repo']}@{c['revision']}:{c['path']}"
 pin={'source_metadata':str((folder/'source.json').relative_to(ROOT)), 'source_metadata_sha256':sha((folder/'source.json').read_bytes())}
 tree_path=folder/'tree.json'
 if tree_path.exists():
  if folder not in trees:trees[folder]=json.loads(tree_path.read_text())
  tree=trees[folder];assert tree['sha']==c['revision']
  match=next(t for t in tree['tree'] if t['path']==c['path'])
  blob=hashlib.sha1(b'blob '+str(len(raw_bytes)).encode()+b'\0'+raw_bytes).hexdigest()
  assert match['sha']==blob
  pin.update(kind='cached_pinned_git_tree_blob_match',git_blob_sha1=blob,tree_sha256=sha(tree_path.read_bytes()))
 else:
  pin.update(kind='raw_commit_bytes_match',receipt_key=key)
  missing[key]=(c,sha(raw_bytes))
 accepted.append({**entry,'pin_verification':pin,'excerpt':c['excerpt'],'independent_external_runtime_tested':False})

def verify(item):
 key,(c,digest)=item;url=f"https://raw.githubusercontent.com/{c['repo']}/{c['revision']}/{c['path']}"
 try:
  response=subprocess.run(['curl','--fail','--location','--silent','--show-error','--max-time','25','--retry','1',url],capture_output=True,check=True)
  content=response.stdout
  actual=sha(content)
  return key,{'url':url,'retrieved_at':datetime.datetime.now().astimezone().isoformat(),'curl_exit_code':response.returncode,'transport':'system curl with TLS verification enabled','expected_sha256':digest,'retrieved_sha256':actual,'matches':digest==actual}
 except Exception as exc:
  return key,{'url':url,'expected_sha256':digest,'matches':False,'error':str(exc)}
if args.verify_missing_pins:
 with ThreadPoolExecutor(max_workers=6) as pool:
  pending=[(key,value) for key,value in missing.items() if not (remote.get(key,{}).get('matches') and remote[key].get('retrieved_sha256')==value[1])]
  for key,value in pool.map(verify,pending):remote[key]=value
 remote_path.write_text(json.dumps(remote,ensure_ascii=False,indent=2)+'\n')
for key,(_,digest) in missing.items():
 assert key in remote and remote[key].get('matches') and remote[key]['retrieved_sha256']==digest, f'Pin not verified: {key}; use --verify-missing-pins'
assert len(accepted)==len({x['snippet_sha256'] for x in accepted})
# No two accepted records count overlapping ranges in the same pinned source file.
for n,a in enumerate(accepted):
 for b in accepted[n+1:]:
  if (a['repo'],a['revision'],a['path'])==(b['repo'],b['revision'],b['path']):
   assert a['end_line']<b['line'] or b['end_line']<a['line'],(a['candidate_index'],b['candidate_index'])
counts=collections.Counter(x['decision'] for x in ledger)
round_file=E/'discovery-rounds.json'
rounds=json.loads(round_file.read_text()) if round_file.exists() else []
applications=[
 {'principle':'失去门槛即撤销当前授权，使用入口仍需读实时装备','candidate_indices':[98,145,158,478,550,572,573],'cod4_relation':'四种三件临时窗、北斗实时四件判断；现有修复保持冻结'},
 {'principle':'临时状态必须绑定原玩家、原手或原装备；仅同类型不够','candidate_indices':[61,68,107,217,327,418,448],'cod4_relation':'玄武/双钺反击源和卸副手；不把测试角色隔离当真人联机'},
 {'principle':'短效果、一次性标记、长期冷却分别撤销/消费/保存','candidate_indices':[4,5,6,120,193,216,219,362,386,387,434,438,440,538],'cod4_relation':'反击窗口可撤销，保命长冷却不可随卸装清空；NBT测试不替代真实重登重启'},
 {'principle':'效果来源必须明确，时长猜测不能证明归属','candidate_indices':[23,75,228,388,389,441,442],'cod4_relation':'现有外来药水保留断言与装备自有增益撤销边界'},
 {'principle':'失败、取消、资源不足、提前结束都需要清理；按实际成功结算','candidate_indices':[49,51,186,245,272,410,545],'cod4_relation':'拒绝提前开窗/保存失败授权；不在本轮追加正式代码'},
 {'principle':'代码中的潜在反例也必须原样记录，不能当正确性背书','candidate_indices':[69,224,265,358,373,523,529,575],'cod4_relation':'Item字段共享、资格未复核、只比修饰存在性和目标混用均需警惕'}]
assert all(i in {x['candidate_index'] for x in accepted} for a in applications for i in a['candidate_indices'])
result={
 'created_at':datetime.datetime.now().astimezone().isoformat(),
 'summary':{'required':1000,'accepted_implementation_sites':len(accepted),'shortfall':max(0,1000-len(accepted)),
 'gate_met':len(accepted)>=1000,'status':'事后专属研究已补足；不追溯制作前完成，不追加正式改动' if len(accepted)>=1000 else '研究持续进行，门槛未满足；按实际逐段阅读去重结果计数，不追加正式改动',
 'source_files_scanned':rounds[-1]['source_files_scanned'] if rounds else 11835,'candidate_methods':len(candidates),'review_decisions':dict(counts),
 'original_340_unreviewed_now_resolved':all(i in by_index for i in range(593)),
 'distinct_repositories':len({x['repo'] for x in accepted}),'distinct_pinned_files':len({(x['repo'],x['revision'],x['path']) for x in accepted}),
 'original_status_1000_counted_toward_gate':0,'initial_five_ranges_added_as_five':False},
 'scope':{
 'count_unit':'一个完整且互不重叠的运行时方法片段；需有具体装备/物品状态的授予撤销、来源/换手约束，或有条件的冷却/持久计时实现。函数中多个分支只计一处。',
 'sources':['build/item-use-references','build/creature-reference-1000','tools/cod4/armor-acceptance/.work/research-sources'],
 'manual_review':'accepted条目均读完整所列方法并记录具体条件、所有者和状态变化；未接受的候选不计有效数。不是全部外部项目的穷尽审计。',
 'deduplication':['固定repo+commit+path+行范围身份','整方法去注释、字符串和空白的SHA256去重','逐段人工合并近似模板；仅效果ID/常量/少量包装差异不重复计','同文件同版本已接受范围禁止重叠；初始5范围不额外加数'],
 'exclusions':['静态fireImmune注册、字段/注册扫描','单纯getter/setter和重复支持位置','客户端动画、外观、GUI、动物孵化、建筑和方块模式','未完成逐段相关性研究的候选'],
 'original_corpus_boundary':'原status-reference-1000.json哈希/固定版本/行号核查只能证明宽泛状态、免疫、解除源码存在，其中静态fireImmune不能满足本轮窗口/反击归属/冷却专属1000门槛。',
 'timing':'本补充研究在已有修复与63通过之后完成；不得追溯声称制作前已完成专属1000。初始5段只作补读线索，不是完整研究。',
 'limitations':['外部源码未在本仓库执行；跨Minecraft/Forge/NeoForge/Fabric版本不保证API可直接复用','原生63用例、84项条件行为、真实两人联机验收均与研究计数独立','当前仍有未接受候选，扫描不是所有潜在有效实现的上限；不能宣称已研究完全部外部源码']},
 'task_applications':applications,'sites':accepted,
 'discovery_rounds':rounds,
 'candidate_ledger':'tools/cod4/armor-acceptance/evidence/armor-reference-ledger.json',
 'manual_notes':'tools/cod4/armor-acceptance/research/reviewed-sites.json',
 'remote_pin_receipts':'tools/cod4/armor-acceptance/evidence/armor-remote-pin-verification.json',
 'input_sha256':{str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in [E/'armor-reference-candidates.json',BASE/'research/reviewed-sites.json']}}
(E/'armor-reference-ledger.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n')
(E/'armor-references.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result['summary'],ensure_ascii=False))
