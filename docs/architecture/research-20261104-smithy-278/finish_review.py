"""Seal private read-only architecture study; no product/master writes."""
import json,hashlib,sys
from pathlib import Path
from zipfile import ZipFile
P=Path(__file__).resolve().parent;R=P.parents[2];PRE=P.parent/'research-20261104-smithy-277'
assert not (P/'RECEIPT.json').exists()
def read(n):return json.loads((P/n).read_text())
def put(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
src=read('raw-source-audit.json')['candidates'][0];d=src['nbt_decoded_original'];pal=d['palette'];m={tuple(b['pos']):b for b in d['blocks']}
obs={
'layout':'原作制图师架高工住单体。主使用面floor3/top石slab,use4；南封闭门4,4/5,11接带盖前廊，东封闭门7,4/5,5接东侧长窄廊。北侧室外五级向西上升外阶接北门2,9/10,3，再进入北侧上层单床房；不是室内梯串联的三层住宅。制图桌4,4,7是下层中心陈设，未证明药材处理。',
'proportion':'11×16×16/DV3953，2816声明位；990存储=762非air+228显式air，1826省略未知。101palette，22BE，entities[]。下层占x1..7/z3..11较长矩形，上层x1..7/z3..7缩短；高度16不是16层。',
'facade':'oak_log105/terracotta78/stripped_oak_log17、oak_planks38/spruce_planks20组成柱梁与填墙；藤76只薄附着，不当绿实体墙。10玻璃pane、三对闭门、南Map Collector挂签构成原职业立面；原牌不是中文任务信息。',
'roof':'主层南段低屋盖与北部高屋盖分级，spruce_slab98/stairs45与木梁混合，木阶/slab同时用于屋盖、平台和陈设。灰色分类格图不代表石瓦，也不精确显示半块碰撞。上层局部y11有slab陈设/顶盖，不能增称第三可用楼层。',
'materials_work_storage':'原制图桌1，下层箱3,6,4和6,7,10，上层箱5,9,4；三单箱均只保存village_cartographer LootTable及各自seed，未读取该vanilla表。上层4/5,9,5 east脚/头合一张床。两个scaffolding分别2,4,10上托盆栽、2,9,6上托灯笼；不存在垂直相连脚手架通道。无熔炉、营火、炼药锅或酿造台。',
'circulation':'北外阶7,4,2→6,5,2→5,6,2→4,7,2→3,8,2均west/bottom，每级上方1..3格air；2,8,2 east/top是顶端落脚，不是第六级bottom。2,9/10,2air接2,9/10,3 north闭门，内地板8/use9。东廊8,3,5top oak slab上4/5air，西向门7,4/5,5闭合需操作。南7,3,13 north/bottom接7,3,12double slab，再沿floor3廊到4,3,12top slab及南门；局部头顶air不证明完整寻路、碰撞或安全护栏。',
'ground_support':'十四down_west bottom支柱socket指向trek:feature/block_column/oak_log，final_state structure_void；原包缺该池，不能把接口当落地木柱。南4,1,15入口socket final north/bottom oak stair，与可见东绕入户路线不能直接等同；连续地形连接未闭合。上居民接口4,3,6 final top cobblestone slab，居民池1/1/10 nitwit/baby/unemployed不等于NPC06或实际居民。地表仅四块稀疏土，省略不补水或承台。'
}
limits=[
'完整单体形态研究1不等有效相关参考1。本例原职业制图，缺炼药工作区；与125F02、208、210既有多层沼泽居作家族存在交集，仅换职业、床层或楼梯方向不足以独立计数。保持作者HOLD0，不把已接受269辅助范围追溯套用到本例或旧HOLD。',
'当前源swamp/houses，原包字符串全查未找到精确选择它的houses池；swamp_vanilla相邻池不适用本源权重或处理器。结构root/biome/structure_set和实际拼接未闭合。',
'十四支柱接口指向缺失oak_log池；这是当前固定包缺项，不证明用户整合包运行时必然缺失。final structure_void不等实际地形支柱。',
'101palette及Properties、22BE/entities[]读核；11分类PNG覆盖16层已看，whole/cut当前续接重看不加栋数。完整2816位RLE只可复核表示，不声称逐位人工读取。52个唯一额外路线probe不等额外案例。',
'读取保存的居民池全文及三metadata；vanilla cartographer loot原包缺失，未读取其实现。entities[]不证明世界无居民，居民接口不是任务角色。',
'三箱LootTable/seed不等实际库存或已付款；一对床只一床。挂签Map Collector保留原文，不称中文同步完成。',
'外阶局部headspace明确，但开门、门框碰撞、横向落脚、护栏、NPC路线与原地形未运行。两单层脚手架为陈设支座，不能误报内部上楼通道。',
'DV3953与pack声明跨版本支持不是当前1.20.1兼容验收。分类全格图非原材质、灯光、性能、UV或实机验收，不复制原资产。',
'旧125自身七维、208七维/9限制、210七维/8限制保存比较；嵌套旧家族未当本次重新全文研究，未重新打开旧NBT/PNG。269仅277首次计数，本批复用0；NPC累计仍null、COD4仍153/gap847。',
'无Java/游戏/网络/UI/声音亮度唤醒/用户实例原档/共享Jar/生产资产/主清单/任务删除/Git操作；未达适用1000不制作，不声称全部完成或主动工时。'
]
# Exact full-cell representation: omitted -1 distinguished from explicit air26.
runs=[]
for y in range(d['size'][1]):
 for z in range(d['size'][2]):
  line=[m[(x,y,z)]['state']if(x,y,z)in m else -1 for x in range(d['size'][0])];rr=[];start=0
  for x in range(1,len(line)+1):
   if x==len(line)or line[x]!=line[start]:rr.append([start,x-1,line[start]]);start=x
  runs.append({'y':y,'z':z,'runs':rr})
put('full-cell-rle.json',{'size':d['size'],'unknown_state':-1,'explicit_air_state':26,'rows':runs,'machine_representation_not_additional_manual_credit':True})
put('manual-review.json',{'batch':278,'id':'F01','status':'WHOLE_SOURCE_NPC06_RELEVANCE_AND_GENERATION_HOLD_ZERO','source':{k:v for k,v in src.items()if k not in ['nbt_decoded_original','material_counts']},'seven_dimensions':obs,'limits':limits,'new_complete_whole_studies':1,'new_qualifying_proposals_maximum':0,'formal_credit_added':0,'main_independent_acceptance':False,'future269_reuse_increment':0})
s=json.loads((PRE/'session.json').read_text());s.update(batch=278,status='WHOLE_SOURCE_NPC06_RELEVANCE_AND_GENERATION_HOLD_ZERO',new_complete_whole_studies=1,new_qualifying_proposals_maximum=0,formal_credit_added=0,first_carry_added=0,old269_carry_added=0,next='继续寻找用途明确、完整且有独立布局的适用本地整栋；本278HOLD0；269仅277首次1，其后0；273/275仍待审。')
s['research_holds'].append('278F01_CARTOGRAPHER_NPC06_RELEVANCE_AND_GENERATION0');s['previous277_receipt']=bind(PRE/'RECEIPT.json');put('session.json',s)
put('active-checkpoint.json',{'batch':278,'status':s['status'],'session':bind(P/'session.json'),'manual':bind(P/'manual-review.json'),'new_complete_whole_studies':1,'new_qualifying_proposals_maximum':0,'formal_credit_added':0,'first_carry_added':0,'old269_carry_added':0,'269_first_carry_batch':277,'COD4_accepted':153,'COD4_gap':847,'NPC_cumulative':None,'native_acceptance':False,'tasks_deleted':0,'all_tasks_complete':False})
checks={}
sys.path.insert(0,str(R/'tools/architecture'));from nbt_read import read as nbtread
with ZipFile(src['source_archive'])as z:
 raw=z.read(src['member']);checks['source_NBT_SHA']=hashlib.sha256(raw).hexdigest()==src['nbt_sha256'];checks['fresh_decode_same']=nbtread(raw)==d
 ctx=read('source-context.json')['candidates'][0];checks['context_original_hashes']=all(hashlib.sha256(z.read(c['member'])).hexdigest()==c['sha256']for c in ctx['contexts']);checks['context_missing_exact']=all(n not in z.namelist()for n in ctx['missing'])
checks['fixed_archive_SHA']=bind(src['source_archive'])['sha256']==src['source_archive_sha256']
checks['RLE_exact']=all([v for start,end,v in row['runs']for _ in range(start,end+1)]==[m[(x,row['y'],row['z'])]['state']if(x,row['y'],row['z'])in m else -1 for x in range(11)]for row in runs)
checks['route_cells_exact']=all(c['state']==(m[tuple(c['pos'])]['state']if tuple(c['pos'])in m else None)for c in read('key-route-cells.json')['cells'])
protected=[]
for item in json.loads((PRE/'protected-inputs-current.json').read_text())['files']:
 old=item['current277'];now=bind(old['path']);protected.append({'previous277':old,'current278':now,'unchanged':now==old,'this_chat_wrote_file':False})
put('protected-inputs-current.json',{'files':protected,'cod5_missing_not_invented':True,'this_chat_product_writes':0})
checks['protected8_unchanged']=all(x['unchanged']for x in protected)
checks['sealed277_immutable']=all(bind(f['path'])==f for f in json.loads((PRE/'RECEIPT.json').read_text())['files'])
checks['session_carry_reset']=s['first_carry_added']==s['old269_carry_added']==0 and s['269_first_carry_batch']==277
checks['consistent_hold0']=s['new_qualifying_proposals_maximum']==0 and s['formal_credit_added']==0
assert all(checks.values()),checks
put('verification.json',{'checks':checks,'all_passed':True,'qualification':'local reproducibility only; not Main independent or game acceptance'})
files=[bind(p)for p in sorted(P.iterdir())if p.is_file()and p.name!='RECEIPT.json']
put('RECEIPT.json',{'batch':278,'status':s['status'],'files':files,'checks':checks,'new_complete_whole_studies':1,'new_qualifying_proposals_maximum':0,'formal_credit_added':0,'first_carry_added':0,'old269_carry_added':0,'COD4_accepted':153,'COD4_gap':847,'NPC_cumulative':None,'tasks_deleted':0,'all_tasks_complete':False})
receipt=read('RECEIPT.json');assert all(bind(f['path'])==f for f in receipt['files'])
print(json.dumps({'receipt':bind(P/'RECEIPT.json'),'manual':bind(P/'manual-review.json'),'checks':checks,'bound_files':len(files),'route_probes':len(read('key-route-cells.json')['cells'])},ensure_ascii=False))
