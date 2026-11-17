import json,hashlib,sys
from pathlib import Path
from zipfile import ZipFile
P=Path(__file__).resolve().parent;R=P.parents[2];PRE=P.parent/'research-20261104-smithy-282';assert not(P/'RECEIPT.json').exists()
def load(n):return json.loads((P/n).read_text())
def put(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
s=load('source.json');d=s['decoded_original'];pal=d['palette'];m={tuple(b['pos']):b['state']for b in d['blocks']}
obs={
'layout':'小型开放盔甲匠职业设施，floor0/standing1，背南石炉台与垂直烟囱，北部抬高箱、上方砖/花岗岩棚盖。没有门/窗/围合房体/二层生活面。完整读此300位单位，不独立计完整铁匠铺。新查原邻接证据：唯一rustic_barn_professions_1宿主接口选择本12职业池，现有221已完整研究该宿主+weaponsmith模块；换本armorer模块不新增整栋家族。',
'proportion':'5×12×5/DV3105，300全部保存=92nonair208显式air，unknown0；29palette、4BE、entities[]。棚檐y7、脊y8，实心烟囱柱y4..9/topwall10，y11全air；12高不是12使用层。7新图覆盖12层/一竖剖，282whole/cut两旧图不重开只绑定复用0。全部300索引矩阵实际逐行读，60RLE只复核表示。',
'facade':'18darkoakplanks及andesite6/polishedandesite16低地台；无独立墙柱包围。北面箱3,2,0west/single为原armorer loot，未指定seed/Items；一盔甲炉与居民接口不构成独立建筑入口。灯1,4,2/3,5,0和chain不当承重支柱或NPC。',
'roof':'y7南北两坡底阶与top砖半块、y8两侧bottom半块及砖/双granite脊，覆盖同一小工位。实心竖polishedandesite(2,y4..9,3)与(2,10,3)wall组成烟囱外形；炉上(2,2,3)air但(2,3,3)top/south阶及以上实心，未见贯通air竖烟道。不能把造型当排烟、防雨或安全已验。',
'work_storage':'blastfurnace(2,1,3)north/unlit，空Items/三计时0/RecipesUsed{}。原有明确职业热设备，但无anvil/砂轮/锻台/材料加工链；单箱village_armorer loot引用不是库存/付款/取得回执。此空炉不是泛住宅炉，但也不能凭这一设施称完整工坊。',
'circulation':'西边(0,1,2)air经(1,1,2)居民接头最终air到炉前(2,1,2)air，三位置均floor0石地，head y2air；中央前区(2,1/2,1)air，开放工位无唯一门。箱west前位(2,2,0)air/head3air，下(2,1,0)polishedandesite抬高；邻(1,1,0)top/east阶和(3,1,1)top/north阶不认连续升高楼梯，跳步/交互距离未验。北箱与火台不能拆参考。',
'ground_interfaces':'本模块(2,0,2)down_west/rollable/bottom empty finalandesite；host rustic_barn_professions_1的(5,0,4)up_west/aligned/bottom pool professions_misc finaldirt相配，按221原推导origin(3,1,2)，本模块完整box可内含host，但本批未运行拼装/当前模块全部覆撞核验。自身(1,1,2)up_west居民pool vanilla plains villagers finalair未实际生成。原misc池12项等权1/legacy/rigid/empty、自fallback；本件非直接houses选择。宿主houses条目weight6 legacy/rigid/empty已读。village root size4/max116/start0/WORLD_SURFACE_WG/beardthin/expansiontrue；center权1/street_rustic、biome16optional已读，不套同包rustic outpost的pillager spawn。'
}
limits=[
'完整职业设施source-unit研究1，完整新建筑研究0/提案0/正式0。不是因路径名字判组件，而由父池、唯一宿主原连接、真实小型工作面与旧221完整host研究共同确认；不把同host换职业添加1。',
'29palette/全部Properties、4BE/entities[]、12层300矩阵位及7新PNG实际读看，unknown0。282旧whole/cut只精确绑定复用0，不虚报9新图/新整栋；本批没有新生成whole/cut。',
'宿主邻接仅扫描匹配socket、size/SHA/该state orientation；没有重看宿主完整NBT语义和PNG。221自身7维/全部8限制原记录已全文读保存，包含weaponsmith整体最多1待审但不是已接受，嵌套家族不新全文读。',
'村root/center/直接biometag/当前misc父池全文读，宿主houses只精确选择条目读。outpost root也读作排除上下文，不能套pillager spawn到本炉台。street_rustic处理器/centerNBT/道路/structure_set/vanilla居民原NBT/loot未新读或执行；16optional生物群系不保证当前环境存在。',
'邻接坐标匹配是静态原接口依据，origin复用221，但当前armorer模块合成覆撞/processor执行/邻接世界地形未验。不能称独立临街店铺、自然生成、居民上岗或完整材料工序完成。',
'烟囱是实心连续柱，不等连续通烟道；实心屋檐半块、箱抬高及侧front空位不证明防雨/箱盖/安全跳步/炉热/NPC可达。炉未点燃、loot未开封，无制作交易奖励回执。',
'COD4仍153/gap847、NPC累计null；269仅277首次NPC06辅助1以后0，273/275待Main。本批不编辑任何session/主清单/正式建筑/共享Jar，不启动Java/game/network/UI音亮唤醒原档/Git。未满适用1000不制作、不删任务、不报工时或全部完成。'
]
put('manual-review.json',{'batch':283,'status':'FULL_PROFESSION_UNIT_INSIDE_ALREADY_STUDIED_HOST_NOT_NEW_WHOLE_ZERO','source':s['source'],'seven_dimensions':obs,'limits':limits,'new_full_source_unit_studies':1,'new_complete_whole_studies':0,'new_qualifying_proposals_maximum':0,'formal_credit_added':0,'first_carry_added':0,'Main_independent_acceptance':False,'images_new_actually_viewed':[bind(p)for p in sorted(P.glob('*.png'))],'old_views_reused':s['previous_bound_views_reused_not_new_credit']})
rows=[]
for y in range(12):
 for z in range(5):rows.append({'y':y,'z':z,'state_indices':[m[(x,y,z)]for x in range(5)]})
put('all300-state-matrix.json',{'size':d['size'],'rows':rows,'actual_matrix_read':True,'unknown_count':0,'air_state':5})
put('active-checkpoint.json',{'batch':283,'status':'FULL_PROFESSION_UNIT_INSIDE_ALREADY_STUDIED_HOST_NOT_NEW_WHOLE_ZERO','manual':bind(P/'manual-review.json'),'previous282_receipt':bind(PRE/'RECEIPT.json'),'new_full_source_unit_studies':1,'new_complete_whole_studies':0,'new_qualifying_proposals_maximum':0,'formal_credit_added':0,'first_carry_added':0,'old269_carry_added':0,'269_first_carry_batch':277,'COD4_accepted':153,'COD4_gap':847,'NPC_cumulative':None,'tasks_deleted':0,'all_tasks_complete':False,'next':'转固定本地其他匿名完整屋功能预筛；旧221母体不重新计数，rustic同母体换职业仍0。'})
checks={};sys.path.insert(0,str(R/'tools/architecture'));from nbt_read import read
with ZipFile(s['source']['source_archive'])as z:
 raw=z.read(s['source']['member']);checks['source_NBT_SHA_decode']=hashlib.sha256(raw).hexdigest()==s['source']['nbt_sha256']and read(raw)==d
 checks['context_original_SHA']=all(hashlib.sha256(z.read(c['member'])).hexdigest()==c['sha256']for n in ['direct-context.json','root-direct-dependencies.json']for c in load(n)['contexts'])
 checks['neighbor_socket_exact']=all(hashlib.sha256(z.read(c['member'])).hexdigest()==c['nbt_sha256']for c in load('neighbor-interface-audit.json')['rows'])
checks['fixed_archive_SHA']=bind(s['source']['source_archive'])==s['source']['fixed_archive'];checks['all300_matrix_exact']=all(r['state_indices']==[m[(x,r['y'],r['z'])]for x in range(5)]for r in rows);checks['old_282_views_bound_unchanged']=all(bind(f['path'])==f for f in s['previous_bound_views_reused_not_new_credit']);checks['seven_new_PNG_saved_and_viewed']=len(list(P.glob('*.png')))==7
protected=[]
for f in json.loads((PRE/'protected-inputs-current.json').read_text())['files']:
 old=f['current282'];now=bind(old['path']);protected.append({'previous282':old,'current283':now,'unchanged':old==now,'this_chat_wrote_file':False})
put('protected-inputs-current.json',{'files':protected,'cod5_missing_not_invented':True,'this_chat_product_writes':0});checks['protected8_unchanged']=all(f['unchanged']for f in protected);checks['sealed282_all_unchanged']=all(bind(f['path'])==f for f in json.loads((PRE/'RECEIPT.json').read_text())['files']);checks['no_session_written']=not(P/'session.json').exists()
assert all(checks.values()),checks
put('verification.json',{'checks':checks,'all_passed':True,'not_Main_independent_or_game_acceptance':True})
put('RECEIPT.json',{'batch':283,'status':'FULL_PROFESSION_UNIT_INSIDE_ALREADY_STUDIED_HOST_NOT_NEW_WHOLE_ZERO','files':[bind(p)for p in sorted(P.iterdir())if p.is_file()and p.name!='RECEIPT.json'],'checks':checks,'new_full_source_unit_studies':1,'new_complete_whole_studies':0,'new_qualifying_proposals_maximum':0,'formal_credit_added':0,'first_carry_added':0,'tasks_deleted':0,'all_tasks_complete':False})
assert all(bind(f['path'])==f for f in load('RECEIPT.json')['files']);print({'receipt':bind(P/'RECEIPT.json'),'manual':bind(P/'manual-review.json'),'files':len(load('RECEIPT.json')['files']),'checks':len(checks)})
