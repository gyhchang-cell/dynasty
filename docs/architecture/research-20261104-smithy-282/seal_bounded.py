import json,hashlib,sys
from pathlib import Path
from zipfile import ZipFile
P=Path(__file__).resolve().parent;R=P.parents[2];PRE=P.parent/'research-20261104-smithy-281';assert not(P/'RECEIPT.json').exists()
def load(n):return json.loads((P/n).read_text())
def put(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p);bb=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(bb).hexdigest(),bytes=len(bb))
a=load('additional-smith-history-screen.json')['rows'];eligible=[r for r in a if r['eligible_for_new_source_study']]
put('manual-review.json',{'batch':282,'status':'BOUNDED_SMITH_NAMES_INTERNAL_CHAMBER_AND_PROFESSION_UNITS_ZERO','scope':'131 fixed local name-matched archive/member entries only; not exhaustive semantic search of all local buildings','actual_screen_counts':{'name_matches':len(a),'machine_eligible_unseen_sources':len(eligible),'name_index_initial_unindexed':len(load('smith-purpose-bounded-index.json')['unindexed'])},'observations':{
'layout':'Trials chamber_smith 15×8×15厚石铜壳平顶房，中央凹低工作场、侧岩浆和两高炉；父chambers池/走廊与spawner/reward接口明确为试炼母体内房。不把整件房间外形称完整独立铁匠铺。Goety abandoned_tower19×20×19有地块、破败墙体及局部高木地，whole仅两向/低cut两向看过，未读全层，不称完整原作研究或适用烽火台。',
'proportion':'Trials1800全部保存=1041nonair759air；Goety7074保存=2675nonair4399air，声明7220，146省略未知。四3×2×3职业小件与一5×12×5 rustic小炉台不按高度/烟囱/组件数累加。',
'facade':'Trials tuff/copper内房外壳；Goety goety石木混用破墙与旗帜，现存用途不等边塞守军。S019 rustic为小炉台、竖向烟囱与顶棚，不凭profession路径判必为内部组件，也不凭有独立顶棚就认完整铁匠铺。',
'roof_ventilation':'Trials铜平封顶是内房壳；未证独立外屋面和通风烟道。S019图中小顶棚/烟囱只是几何，通烟、炉热与实机防雨未验；Goety破损顶及局部木面不称有完整避雨上亭。',
'material_work_storage':'Trials原损坏铁砧1、lava30/两高炉；两炉Items[]/BurnTime/CookTime/CookTimeTotal0/RecipesUsed{}不是实际生产。S012/037原高炉空；S014有lava_cauldron与砂轮，S039砂轮；S019高炉空Items及一随机armorer箱，各保留原BE不推交易领取。Goety原voidfluid/flame/传播方块及endersent_generator不称安全烽火，不运行其实现；两原箱Items[]不等处理后有奖励。',
'circulation':'Trials北7,3,0hallway接头，两个floor0spawnerplacer及四rewardplacer，各pool/final原样保存已读，非普通外客入口。Goety原根startabsolute-5使部分地块埋入的意图不证明实际地形落位；原破塔楼梯/上下层链未完整读，不能称已通瞭望。S019仅whole/cut两图，未全层/完整站位读，整体工作动线及独立性待核，不作整栋提案。',
'ground_use':'Trials父chamber选择权8/single/rigid/trials:generic是内部母体，不套外村房上下文。Goety root size7/max80/start-5/WORLD_SURFACE_WG/expansionfalse，单选权1/rigid/abandoned_tower_loot；biome tag、processor实现及自然地形未读。小职业件bottomsocket不等实际地面/村民已生成。'},
'limits':['131名称条目只机器排除与有界核查；已有完整/有限/待审/HOLD历史不因本轮重置，不用缺actual_full_reference_study_complete字段把旧完整研究误当未研究。','六新机器候选不等六完整建筑：四3×2×3职业件实际材料/BE读，S0195×12×5两图读及BE核，Trial内房两图及父池/九BE核。均没有完整新增whole验收，提案0；S019保留待补独立范围证据，不先定不可独立或先计数。','六PNG实际看：F01/F02/S019各whole/cut；没有新全层/全palette/全实体人工阅读。Goety头颅纹理NBT长字段只捕获，本轮输出片段不当全文阅读。','直接root/父池原JSON实际读，仅这一子范围；Trials generic/其他接口pool，Goety lootprocessor/biome tag及依赖实现未读，不能从Items空推最终loot或把生成器当NPC。','131项中其余125有known/历史/同batch命中，只作机器排除；机器角色/占用相同是去重依据，绝不直接等语义完整研究或接受。282主筛F01与追加S106是同一个Trial源，不重复计任何study。','当前有界查找合格完整铁匠铺新增0，COD4153/gap847；这不是声称全库所有匿名建筑不存在锻造空间。可继续固定源匿名屋的功能预筛或其他直接适用整栋；普通空炉住宅不提升用途。','269仅277首次已验NPC06辅助1以后0，273/275仍待Main，NPC累计未知；本轮不编辑任何session、主清单或正式资产，以私有active-checkpoint保存。无Java游戏网络UI/音亮唤醒/用户实例存档/共享Jar/Git；未达1000不制作不删任务，不声称全部完成或工时。'],
'images_actually_viewed':[bind(p)for p in sorted(P.glob('*.png'))],'new_complete_whole_studies':0,'new_qualifying_proposals_maximum':0,'formal_credit_added':0,'first_carry_added':0,'Main_independent_acceptance':False})
# Private checkpoint only; no session writes in this batch.
put('active-checkpoint.json',{'batch':282,'status':'BOUNDED_SMITH_NAMES_INTERNAL_CHAMBER_AND_PROFESSION_UNITS_ZERO','manual':bind(P/'manual-review.json'),'previous281_receipt':bind(PRE/'RECEIPT.json'),'previous_private_session_unchanged':bind(PRE/'session.json'),'new_complete_whole_studies':0,'new_qualifying_proposals_maximum':0,'formal_credit_added':0,'first_carry_added':0,'old269_carry_added':0,'269_first_carry_batch':277,'COD4_accepted':153,'COD4_gap':847,'NPC_cumulative':None,'273_275_still_pending':True,'tasks_deleted':0,'all_tasks_complete':False,'next':'S019范围/全层待核不先计数；其他固定本地匿名屋功能预筛或直接适用完整建筑，按实际证据选择；不重看旧图加数。'})
checks={};sys.path.insert(0,str(R/'tools/architecture'));from nbt_read import read
for b in load('bounded-source-audit.json')['rows']:
 with ZipFile(b['source']['source_archive'])as z:
  raw=z.read(b['source']['member']);checks[b['id']+'_NBT_SHA']=hashlib.sha256(raw).hexdigest()==b['source']['nbt_sha256'];checks[b['id']+'_context_SHA']=all(hashlib.sha256(z.read(c['member'])).hexdigest()==c['sha256']for c in b['direct_references'])
for b in load('additional-profession-components.json')['rows']:
 with ZipFile(b['source']['source_archive'])as z:raw=z.read(b['source']['member']);checks[b['id']+'_NBT_SHA_decode']=hashlib.sha256(raw).hexdigest()==b['source']['nbt_sha256']and read(raw)==b['decoded_original']
checks['131_screen_six_new_machine_only']=len(a)==131 and len(eligible)==6
checks['six_PNG_saved_and_viewed']=len(list(P.glob('*.png')))==6
protected=[]
for f in json.loads((PRE/'protected-inputs-current.json').read_text())['files']:
 old=f['current281'];now=bind(old['path']);protected.append({'previous281':old,'current282':now,'unchanged':old==now,'this_chat_wrote_file':False})
put('protected-inputs-current.json',{'files':protected,'cod5_missing_not_invented':True,'this_chat_product_writes':0});checks['protected8_unchanged']=all(f['unchanged']for f in protected);checks['sealed281_all_unchanged_including_session']=all(bind(f['path'])==f for f in json.loads((PRE/'RECEIPT.json').read_text())['files']);checks['no_session_written']=not(P/'session.json').exists()
assert all(checks.values()),checks
put('verification.json',{'checks':checks,'all_passed':True,'not_Main_independent_or_game_acceptance':True})
put('RECEIPT.json',{'batch':282,'status':'BOUNDED_SMITH_NAMES_INTERNAL_CHAMBER_AND_PROFESSION_UNITS_ZERO','files':[bind(p)for p in sorted(P.iterdir())if p.is_file()and p.name!='RECEIPT.json'],'checks':checks,'new_complete_whole_studies':0,'new_qualifying_proposals_maximum':0,'formal_credit_added':0,'first_carry_added':0,'tasks_deleted':0,'all_tasks_complete':False})
assert all(bind(f['path'])==f for f in load('RECEIPT.json')['files']);print({'receipt':bind(P/'RECEIPT.json'),'manual':bind(P/'manual-review.json'),'files':len(load('RECEIPT.json')['files']),'checks':len(checks)})
