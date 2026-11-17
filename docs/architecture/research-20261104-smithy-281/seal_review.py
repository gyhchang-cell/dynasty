import json,hashlib,sys
from pathlib import Path
from zipfile import ZipFile
P=Path(__file__).resolve().parent;R=P.parents[2];PRE=P.parent/'research-20261104-smithy-280';assert not(P/'RECEIPT.json').exists()
def load(n):return json.loads((P/n).read_text())
def put(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
src=load('raw-source-audit.json')['candidates'][0];d=src['nbt_decoded_original'];pal=d['palette'];m={tuple(b['pos']):b for b in d['blocks']}
obs={
'layout':'完整紧凑雪地制革单室。西门入floor0/use1单层木地小工作间，北偏东水锅、南部抬高双箱。无床/炉/梯/独立夜宿区或上生活层，不能从制革职业推猎户生活组织。与270下织机/上睡/院圈、275公共厅/低床/内阶上床原七维及全部限制对比，本件为更小单室湿作角，不用家具差异认新适用整体，作者HOLD0。',
'proportion':'7×8×9/DV3337，504声明位，233存储=206nonair/27显式air，271省略unknown。27palette/4BE/entities[]；实际顶构到y5，y6/7全省略，不把8高写8楼或把屋盖上未知写air。7PNG覆盖8层；252低四层索引矩阵+20附加probe有重叠，不合计272唯一格。',
'facade':'spruceplanks26、sprucelog8/strippedsprucelog23框墙；西1,1/2,4west/right/closed单门，东5,2,4单glasspane。原白壁旗4,2,3south/Patterns[]不是中文皮货招牌；一挂灯4,3,4非NPC。薄门窗和活板在类色全格图中不表达真实碰撞。',
'roof':'73spruce stairs与5spruce slab组成南北坡、东西长脊；含top内衬，低檐压小工室，不因灰图称石屋盖。9层数1的薄snow在低地外围，4snowblock在四地边，不把灰坡顶一律称白雪厚盖。y4中央木脊/y5slab顶脊不是第二储藏层。',
'materials':'水锅4,1,3 level3为原满水锅，未证明清洗皮革配方、猎获处理或熬药。南箱3,2,6north/left与4,2,6north/right为一对双箱半体，各保存vanilla village_tannery loot及不同64位seed(-3703783393073367599/8729664041551628537)，不能称两单箱/两份已取奖励。无床、炉、campfire、brewingstand；不补夜烤火/酒/任务人物。',
'circulation':'西0,0,4path上入口0,1,4jigsaw finalair、上0,2,4air；1,0,4plank上1,1/2,4闭门；内2,0,4plank上2,y1..3,4air，静态入口清楚，未验开门碰撞。双箱下3/4,1,6是TOP/north/closed薄活板，前3/4,2,5air，箱上3/4,3,6bottom/north屋盖阶；箱盖可开/实际操作不可据此断言。没有阶梯上楼链。',
'ground_support':'floor0 dirt36、grass9、path1与室内木板，四边snowblock；271省略和y-1模板外不补完整山坡基底。唯一jigsaw为空池入口finalair，无必需续屋socket/居民口，不等原世界道路已接或保证没有居民。精确houses池选本件weight1/single/rigid/empty；固定Trek缺vanilla tannery loot，不推用户全环境缺失。'
}
limits=[
'完整原作研究1，不申请NPC13有效参考，HOLD0。原制革湿作与处理材料相邻，但本例无夜宿/火源/完整猎居生活分区；与普通低单室近族不独立加数，也不转套NPC06炼药。',
'27palette全部Properties、4BE/entities[]读核，7PNG全看覆盖8层。252矩阵与20probe重叠，仅机器生成72行RLE/504位表示，不宣全部位置逐格人工读。省略271与air27分开。',
'精确house选择条目实际读；池其余条目只捕获不当全文新研究。三个metadata从270精确同hash复用0新全文阅读；本批没有新读root/center/道路/biome/structure_set或vanilla loot，不称生成依赖全部闭合。',
'两个半箱type left/right朝北相邻只一对双箱，seed分别保留；引用不等库存/制作付款/原生领取。箱上bottom坡阶及薄托板不证开盖，门/窄室/水锅碰撞和NPC路线未运行。白旗空Patterns不补中文。',
'270/275自身七维及全部10/9限制先读保存，旧原图/NBT未重开。其原文含269待审等历史表述只保留原始记录，当前生效状态为269首次277唯一1以后0，不据旧快照倒退或重计。',
'F01 mountains armorer_2与既有cherry armorer_2/mountains armorer_house_2等role+occupancy相同，仅排除，不声称新语义整栋研究。不能用盔甲铺换材版本凑NPC01。',
'DV3337/metadata声明非兼容/运行验收，分类整格图非实际木纹、半块碰撞、光照防雨性能或原生材质效果；没有复制原资产。',
'COD4仍153/gap847、NPC累计null；本批firstcarry0，273/275仍待Main，269仅277首次1。未满适用1000不制作不删任务。无Java/游戏/网络/UI/音亮唤醒/用户实例存档/共享Jar/正式资产/主清单/Git操作，不宣全部完成或工时。'
]
put('manual-review.json',{'batch':281,'id':'F02','status':'COMPLETE_SMALL_TANNERY_NPC13_RELEVANCE_AND_FAMILY_HOLD_ZERO','source':{k:v for k,v in src.items()if k not in ['nbt_decoded_original','material_counts']},'seven_dimensions':obs,'limits':limits,'images_actually_viewed':[bind(p)for p in sorted(P.glob('*.png'))],'new_complete_whole_studies':1,'new_qualifying_proposals_maximum':0,'formal_credit_added':0,'first_carry_added':0,'Main_independent_acceptance':False})
runs=[]
for y in range(8):
 for z in range(9):
  line=[m[(x,y,z)]['state']if(x,y,z)in m else -1 for x in range(7)];rr=[];start=0
  for x in range(1,8):
   if x==7 or line[x]!=line[start]:rr.append([start,x-1,line[start]]);start=x
  runs.append({'y':y,'z':z,'runs':rr})
put('full-cell-rle.json',{'size':d['size'],'unknown_state':-1,'explicit_air_state':13,'rows':runs,'machine_representation_not_extra_manual_reading':True})
s=json.loads((PRE/'session.json').read_text());s.update(batch=281,status='COMPLETE_SMALL_TANNERY_NPC13_RELEVANCE_AND_FAMILY_HOLD_ZERO',new_complete_whole_studies=1,new_qualifying_proposals_maximum=0,first_carry_added=0,old269_carry_added=0,next='继续下一真实相关完整本地源；280内部组件0，281小制革屋适用性HOLD0；269仅277首次1以后0，273/275仍待Main。');s['research_holds'].append('281F02_SMALL_TANNERY_NPC13_RELEVANCE_AND_FAMILY0');s['previous280_receipt']=bind(PRE/'RECEIPT.json');put('session.json',s)
put('active-checkpoint.json',{'batch':281,'status':s['status'],'session':bind(P/'session.json'),'manual':bind(P/'manual-review.json'),'new_complete_whole_studies':1,'new_qualifying_proposals_maximum':0,'formal_credit_added':0,'first_carry_added':0,'old269_carry_added':0,'269_first_carry_batch':277,'COD4_accepted':153,'COD4_gap':847,'NPC_cumulative':None,'tasks_deleted':0,'all_tasks_complete':False})
sys.path.insert(0,str(R/'tools/architecture'));from nbt_read import read
checks={}
with ZipFile(src['source_archive'])as z:
 bb=z.read(src['member']);checks['NBT_SHA_and_freshdecode']=hashlib.sha256(bb).hexdigest()==src['nbt_sha256']and read(bb)==d
 checks['context_SHA']=all(hashlib.sha256(z.read(c['member'])).hexdigest()==c['sha256']for c in load('source-context.json')['candidates'][0]['contexts'])
 checks['metadata_reuse_exact']=all(hashlib.sha256(z.read(c['original']['member'])).hexdigest()==c['original']['sha256']for c in load('exact-context-reuse.json')['rows'])
checks['fixed_archive_SHA']=bind(src['source_archive'])['sha256']==src['source_archive_sha256']
checks['RLE_exact']=all([v for start,end,v in r['runs']for _ in range(start,end+1)]==[m[(x,r['y'],r['z'])]['state']if(x,r['y'],r['z'])in m else -1 for x in range(7)]for r in runs)
checks['route_cells_exact']=all(c['state']==(m[tuple(c['pos'])]['state']if tuple(c['pos'])in m else None)for c in load('key-route-cells.json')['cells'])
protected=[]
for f in json.loads((PRE/'protected-inputs-current.json').read_text())['files']:
 old=f['current280'];now=bind(old['path']);protected.append({'previous280':old,'current281':now,'unchanged':old==now,'this_chat_wrote_file':False})
put('protected-inputs-current.json',{'files':protected,'cod5_missing_not_invented':True,'this_chat_product_writes':0});checks['protected8_unchanged']=all(f['unchanged']for f in protected);checks['sealed280_immutable']=all(bind(f['path'])==f for f in json.loads((PRE/'RECEIPT.json').read_text())['files']);checks['seven_PNG_saved_and_viewed']=len(list(P.glob('*.png')))==7
checks['hold0_carry0']=s['new_qualifying_proposals_maximum']==s['formal_credit_added']==s['first_carry_added']==s['old269_carry_added']==0
assert all(checks.values()),checks
put('verification.json',{'checks':checks,'all_passed':True,'not_Main_independent_or_game_acceptance':True})
put('RECEIPT.json',{'batch':281,'status':s['status'],'files':[bind(p)for p in sorted(P.iterdir())if p.is_file()and p.name!='RECEIPT.json'],'checks':checks,'new_complete_whole_studies':1,'new_qualifying_proposals_maximum':0,'formal_credit_added':0,'first_carry_added':0,'old269_carry_added':0,'tasks_deleted':0,'all_tasks_complete':False})
assert all(bind(f['path'])==f for f in load('RECEIPT.json')['files']);print({'receipt':bind(P/'RECEIPT.json'),'manual':bind(P/'manual-review.json'),'files':len(load('RECEIPT.json')['files']),'checks':checks})
