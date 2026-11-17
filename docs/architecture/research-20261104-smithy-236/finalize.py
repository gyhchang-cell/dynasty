import json, hashlib
from pathlib import Path
P=Path(__file__).resolve().parent;PRE=P.parent/'research-20261104-smithy-235'
assert not(P/'RECEIPT.json').exists()
def read(p):return json.loads(Path(p).read_text())
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def put(n,o):(P/n).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n')
screen=read(P/'pre-render-history-screen.json');rows=screen['rows'];checks=[]
def ck(k,v):
 checks.append(dict(check=k,passed=bool(v)));assert v,k
ck('bounded2new cherry machine candidates only',len(rows)==2 and all('/cherry/houses/'in r['member']and not r['known_history']for r in rows))
ck('both role and occupancy exact with prior mountains',all(not r['eligible_for_new_source_study']and len(r['historical_exact_matches'])==1 and '/mountains/houses/'in r['historical_exact_matches'][0]['source']['member']and set(r['historical_exact_matches'][0]['exact_keys'])=={'role_sha256','occupancy_sha256'}for r in rows))
ck('source bytes distinct not claimed exact NBT',all('nbt_sha256'not in r['historical_exact_matches'][0]['exact_keys']for r in rows))
for r in rows:ck(r['id']+'fixed source archive remains exact',bind(r['fixed_archive']['path'])==r['fixed_archive'])
put('bounded-exclusions.json',dict(batch=236,status='BOUNDED_MACHINE_DUPLICATE_PREFILTER_ONLY_NOT_WHOLE_STUDY',rows=[dict(id=r['id'],source_archive=r['source_archive'],member=r['member'],size=r['size'],source_fingerprints=r['current_source_fingerprints'],prior_match=r['historical_exact_matches'][0],reason='新源字节不同，但四向归一用途/占格指纹与已有山地源相同；在当前筛选中保守不投入整栋重读，不据樱花材质/新文件名提出新参考。',source_NBT_machine_decoded=True,source_NBT_full_human_read=False,new_palette_BE_entities_full_read=False,new_positions_actually_read=0,new_PNG_generated=0,new_PNG_viewed=0,whole_reference_studies=0,proposed_reference_credit=0,formal_reference_credit=0)for r in rows],limits=['这是2条机器预筛排除，非2栋实际完整阅读，不声称语义逐格等同或全历史穷尽；没有从哈希直接获得建筑信用。','不改169/170/066历史研究状态与既有接受，不重开旧NBT/PNG。','未生成新建筑、未修改游戏内容/主清单，未运行Java；当前独立待审与1000门槛保留。']))
put('previous-checkpoint.json',dict(receipt=bind(PRE/'RECEIPT.json'),cumulative_not_reset=True))
protected=[]
for o in read(PRE/'protected-inputs-current.json')['files']:
 b=o['current235'];now=bind(b['path']);protected.append(dict(last235_checkpoint=b,current236=now,unchanged=b==now))
put('protected-inputs-current.json',dict(files=protected,this_chat_product_writes=False,concurrent_changes_not_reverted=True));ck('8protected unchanged',len(protected)==8 and all(o['unchanged']for o in protected))
s=dict(batch=236,status='TWO_CHERRY_EXACT_ROLE_OCCUPANCY_PREFILTER_EXCLUSIONS_ZERO_WHOLE_READS',formal_credit_added=0,COD4_accepted=153,COD4_gap=847,NPC01_total=None,NPC05_total=None,NPC06_total=None,new_complete_whole_studies=0,new_qualifying_proposals=0,active_pending=read(PRE/'session.json')['active_pending'],java_run=False,game_run=False,network_used=False,production=False,masterlists_edited=False,all_tasks_complete=False,actual_active_work_hours=None,next='235 max1 and226/229/232 pending Main. Continue new genuinely related complete sources/material organization; role/occupancy duplicates, ordinary houses and chambers are not new complete references. Never count filename variants or repeat oldcarry; no construction before accepted1000.')
for f in ['session.json','active-checkpoint.json','latest-independent-admissions.json','carried-forward-pending.json']:put(f,{**s,'previous235_binding':bind(PRE/f),'old_accepted_carries_added':0,'not_master_todo_backup':True})
put('verification.json',dict(status='PASS',checks=checks,machine_checks_not_reference_credit=True))
files=[bind(f)for f in sorted(P.iterdir())if f.is_file()and f.name!='RECEIPT.json'];put('RECEIPT.json',dict(**s,files=files,verification_checks=len(checks)));print(json.dumps(dict(receipt=bind(P/'RECEIPT.json'),files=len(files),checks=len(checks)),ensure_ascii=False))
