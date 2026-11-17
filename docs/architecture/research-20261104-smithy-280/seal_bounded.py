import json,hashlib,sys
from pathlib import Path
from zipfile import ZipFile
P=Path(__file__).resolve().parent;R=P.parents[2];PRE=P.parent/'research-20261104-smithy-279';assert not(P/'RECEIPT.json').exists()
def put(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p);bb=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(bb).hexdigest(),bytes=len(bb))
old=R/'docs/architecture/research-20261104-smithy-211/manual-review.json';put('prior211-saved-comparison.json',{'binding':bind(old),'original':json.loads(old.read_text()),'read_this_turn':'all own seven observations and eight limits; not fresh nested-family reread','old_NBT_PNG_reopened':False,'credit':0})
review={'batch':280,'status':'DIRECT_ALCHEMY_INTERNAL_COMPONENTS_AND_WOOD_VARIANTS_HOLD_ZERO','cases':[
{'id':'F01','status':'INTERNAL_FORTRESS_ROOM_NOT_WHOLE_BUILDING','bounded_observations':{'layout':'7×8×14室内长房，四周厚壳/顶封，入口连接要塞halls池；whole/cut<=4两图已看，不等完整地上建筑。','circulation':'北4,1,0 north_up jigsaw name betterfortresses:halls/pool empty/finalair；原两对crimson门，仅内部房间动线研究，不证明独立外入口或连接整栋。','roof':'厚netherbrick平封顶是内房壳，不据此命名完整建筑屋面/防雨用途。','material_work':'784全位，247air/537nonair；netherbrick171/rednetherbrick71、两株netherwart及soulsand；保存8实体未全文人工读，不据家具/名称推实际炼药产出。','terrain':'没有本批证据证明地面独立选址/柱基/沼泽衔接。','use_basis':'父halls原文本明确alchemy_md_side_0选择weight1/mainprocessor/max_count1，未全文读父池。严格JSON解析遇原始非标准内容，保留原文本和错误，未修改/修复原包或推游戏加载失败。'},'complete_whole_study':False,'proposal_maximum':0},
{'id':'F02','status':'INTERNAL_ASYLUM_BREWING_ROOM_NOT_WHOLE_BUILDING','bounded_observations':{'layout':'17×9×17石木壳内走廊/分隔工位房。whole与cut<=4两图实际看，六酿造台位于同一内房，不能按六台拆数或把房间当完整精神病院。','circulation':'西/东各floor0 room接口和y1 corridor接口，以及8,1,12 witch上接头；父rooms池七等权房型，本brews1/7候选，独立外入口未证。','roof':'平顶木面加石边是内部房间封盖，不是完整建筑独立屋面验收。','material_work':'2601全存储=1670nonair/931air；六台BrewTime0/Fuel0/Items[]和has_bottle全false。三桶一箱一漏斗未全文读，不推已生产/配方/药材回执。','terrain':'未读整个plague_asylum母体、地形/root/自然衔接；内房外不补支柱地面。','use_basis':'精确room池条目、五接口、六酿造BE已读，name/pool明确内房用途；entities[]不抹去witch生成接口，也不生成NPC06。'},'complete_whole_study':False,'proposal_maximum':0}],
'limits':['16个名称关键词仅metadata筛查，非全库语义穷尽；其中已研究源不重开，1×2/3实体模板不当建筑。','五木种witch_huts与既有211 mangrove的role+occupancy同指纹；只用于排除，不宣新语义阅读或按五栋累计，原211HOLD0不复活。','本批四PNG实际看，未全层/全palette/全BE/全实体读，不称完整单体研究。两原NBT固定SHA及完整捕获只保留复核，不等人工读全。','无完整新相关炼药建筑信用，不推本地绝对不存在其他来源；转查原未完成NPC01工坊用途。','269仅277首次1以后0，273/275待Main；COD4153/gap847、NPC累计null，未满1000不制作。不改正式资产、主清单或共享Jar；无Java游戏网络UI音亮原档/Git操作，任务删除0。'],
'new_complete_whole_studies':0,'new_qualifying_proposals_maximum':0,'formal_credit_added':0,'first_carry_added':0,'images_actually_viewed':[bind(p)for p in sorted(P.glob('*.png'))]}
put('manual-review.json',review)
s=json.loads((PRE/'session.json').read_text());s.update(batch=280,status=review['status'],new_complete_whole_studies=0,new_qualifying_proposals_maximum=0,first_carry_added=0,old269_carry_added=0,next='转NPC01真实完整工坊本地候选，先历史排重及用途核查；本280组件/同构木种0，269reuse0，273/275待审。');s['research_holds'].append('280_ALCHEMY_COMPONENTS_AND_WOOD_VARIANTS0');s['previous279_receipt']=bind(PRE/'RECEIPT.json');put('session.json',s)
put('active-checkpoint.json',{'batch':280,'status':s['status'],'session':bind(P/'session.json'),'manual':bind(P/'manual-review.json'),'new_complete_whole_studies':0,'new_qualifying_proposals_maximum':0,'formal_credit_added':0,'first_carry_added':0,'old269_carry_added':0,'269_first_carry_batch':277,'COD4_accepted':153,'COD4_gap':847,'NPC_cumulative':None,'tasks_deleted':0,'all_tasks_complete':False})
checks={};sys.path.insert(0,str(R/'tools/architecture'));from nbt_read import read
for a in json.loads((P/'bounded-source-audit.json').read_text())['rows']:
 with ZipFile(a['source']['source_archive'])as z:
  bb=z.read(a['source']['member']);checks[a['id']+'_NBT_exact']=hashlib.sha256(bb).hexdigest()==a['source']['nbt_sha256']and read(bb)==a['raw_decoded_original'];checks[a['id']+'_context_original_SHA']=all(hashlib.sha256(z.read(c['member'])).hexdigest()==c['sha256']for c in a['direct_references'])
protected=[]
for f in json.loads((PRE/'protected-inputs-current.json').read_text())['files']:
 old=f['current279'];now=bind(old['path']);protected.append({'previous279':old,'current280':now,'unchanged':old==now,'this_chat_wrote_file':False})
put('protected-inputs-current.json',{'files':protected,'cod5_missing_not_invented':True,'this_chat_product_writes':0});checks['protected8_unchanged']=all(f['unchanged']for f in protected);checks['sealed279_immutable']=all(bind(f['path'])==f for f in json.loads((PRE/'RECEIPT.json').read_text())['files']);checks['four_PNG_only']=len(list(P.glob('*.png')))==4
assert all(checks.values()),checks
put('verification.json',{'checks':checks,'all_passed':True,'not_Main_independent_or_game_acceptance':True})
put('RECEIPT.json',{'batch':280,'status':s['status'],'files':[bind(p)for p in sorted(P.iterdir())if p.is_file()and p.name!='RECEIPT.json'],'checks':checks,'new_complete_whole_studies':0,'new_qualifying_proposals_maximum':0,'formal_credit_added':0,'first_carry_added':0,'old269_carry_added':0,'tasks_deleted':0,'all_tasks_complete':False})
assert all(bind(f['path'])==f for f in json.loads((P/'RECEIPT.json').read_text())['files']);print(bind(P/'RECEIPT.json'))
