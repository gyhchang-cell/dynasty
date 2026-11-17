#!/usr/bin/env python3
"""Actual manual observations of four mining sources, not a mine-complex tally."""
import hashlib
import json
import sys
from pathlib import Path
from zipfile import ZipFile
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
sys.path.insert(0,str(ROOT/'tools/architecture'))
from nbt_read import read
FIELDS=['layout','proportion','facade','roof','materials','circulation','terrain']
NOTES={
 'F01':[
  '矩形带凹角的小型矿业支援棚：一侧窄辅助跨有炉、水锅，另一宽跨铺地毯，末侧整排桶；完整覆盖工作棚仅作一个设计提案，不把两跨拆数。',
  '保存盒12×6×9且占用y0..5；名字large不表示巨型厂房。地板y0，器具多y1，低梁顶y5，只有一层作业空间。',
  '去皮云杉柱梁配敞口边界，角柱和中部柱把长边分段；没有完整围墙和普通门，开跨为内外工作界面。',
  '低平顶用梁格和活板覆盖；凹角跟着主平面收退，不是坡屋顶或矿井顶板已验岩层。活板原始状态需区别整块投影。',
  'stone92、stripped_spruce_log66、spruce_trapdoor57、cyan_carpet20；furnace3、barrel7、damaged_anvil/grindstone/water_cauldron各1。中央灰块含20格地毯，不是厚石台。',
  '炉在x0,z1..3，桶在x11,z1..7，水锅(3,1,0)、铁砧(4,1,6)、砂轮(7,1,8)；中央地毯x6..9,z2..6。敞口连接外围与两工作跨，无梯，不宣称地下主矿道已连通。',
  '本体含石地坪与覆盖，没有外接拼图接口；来源池将其列为rigid完整单模板。只提案DUN02小型矿业维修/储料工作棚布局，不覆盖巨型工坊、运输线或COD6完整矿场。'],
 'F02':[
  '7×7单跨方形梁框，角侧桶堆、另一边双炉和水锅，中间留空；可学习附属储料/操作跨，但不与F01共用炉桶就累计两个完整覆盖工坊。',
  '7×6×7，地板y0、柱梁顶y5；与F01同高度的单跨开放构架，没有独立楼层、独立厂房大跨或多层库房。',
  '四边去皮木柱和上梁，炉桶靠边，四面大面积开敞；投影中黄块多为火把，不凭颜色判成承重金属带。',
  'y5只有7×7外周24格木梁，中央5×5为空；没有F01的覆盖顶。作为完整覆盖矿业工作棚范围证据不足，保留构架研究。',
  'stone49、stripped_spruce_log40、spruce_stairs7、wall_torch7、barrel7、furnace2、water_cauldron1；同材质器具不证明是新的完整建筑用途。',
  '水锅(1,1,6)，双炉(4,1,6)/(5,1,6)，桶堆在x4..6,z0/1、y1..3；中心5×5开敞，无门无梯，原生桶可开性和火把碰撞未验。',
  '含石地坪、无外接拼图接口；与F01在同一来源池为可替选项，不能仅以第二个NBT或小/大文件名计第二个独立相关完整工坊。当前记开放梁框/附属空间资料，正式计数0。'],
 'F03':[
  '不规则矿石岩壳围一处凹入露天作业坑，坑边有少量木踏步、炉和箱；主要组织为采掘地形，不是已建成的独立工坊房屋。',
  '13×9×14，底坑与外缘约四五格高差，最高y8是个别岩饰；不把岩石尖部称多层矿业塔。',
  '四周是玄武岩/石块和矿脉边缘，人工围护少，木件与栏边只作局部设施；岩壳不是施工厂房外墙。',
  '整体露天，无房屋连续屋盖；围坑高岩和炉台不冒充屋脊、天窗或完成的地下穹顶。',
  'basalt368、stone159、black_terracotta26、iron_ore10、gold_ore11；blast_furnace4、chest1、barrel2、campfire1。原始红石线4格不证明机关运作。',
  '入口空标识在(6,5,0)，可见木踏步向坑下，炉集中z13边y5/6，箱(1,4,2)；补剖见坑底起伏，无梯，未验边缘到坑底原生可达。',
  '自带岩壳只表明模板中有地形；单个终端入口不证明完整矿场。保留采掘坑/地形衔接观察，不提案完整建筑，不计COD6或DUN02建筑参考。'],
 'F04':[
  '矿物晶洞外壳内留高空腔，入口外置炉、桶箱和工具，侧面五格梯、局部木件；是晶洞附属采掘设施，未见完整独立工坊房屋组织。',
  '15×18×15保存、实际占用y0..16；上部单点竖饰不等于18格净高厂房。主要洞腔内高大而工作器具靠低入口。',
  '粗糙深岩与方解石带交错，局部木撑、栏杆、旗与灯；外观主要是晶洞剖壳，不能将天然壳层称为学会的房屋立面设计。',
  '上部是收拢的不规则矿物壳与顶点竖件，不是木石建筑的常规分层坡顶；没有完整多层屋顶和阁楼。',
  'smooth_basalt309、calcite309、amethyst_block214、basalt125、budding_amethyst22，另deepslate_coal_ore77/iron_ore21/gold_ore71；blast_furnace4、ladder5。矿物数量不能替代建筑参考。',
  '梯在x12,z4,y1..5连续；炉和箱桶集中入口y0..2，营火(7,4,8)。补剖定位梯顶与洞壳，不能据五梯证明能绕洞登顶或完整环廊已连通。',
  '自带晶洞、只有一入口空标识且无扩房池；原生岩壳与外围接地未验。保留洞穴采掘空间研究，不把矿体、天然洞壳和局部设施合成完整建筑信用。'],
}
DECISIONS={
 'F01':('SCOPED_COVERED_WORKSHOP_PROPOSAL','DUN02小型低平顶矿业维修/储料工作棚；12×6×9，单层，不覆盖巨型工坊或完整矿场。'),
 'F02':('OPEN_FRAME_SUPPORT_SPACE_NOT_COUNTED','开放梁框/附属储料操作跨，未作为完整覆盖工坊提案；不凭同池第二个NBT另计。'),
 'F03':('EXCAVATION_TERRAIN_NOT_COMPLETE_BUILDING','露天采掘坑及人工边缘设施，仅地形和高差研究。'),
 'F04':('GEODE_WITH_FITTINGS_NOT_COMPLETE_BUILDING','晶洞壳及入口采掘设施，仅洞腔与附属操作空间研究。'),
}
KINDS={'furnace','blast_furnace','barrel','chest','grindstone','damaged_anvil','water_cauldron','lava_cauldron','ladder','campfire','cyan_carpet'}
def ev(p):return dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def dump(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def main():
 s=json.loads((OUT/'sources.json').read_text());entries=[];fittings=[]
 for c in s['candidates']:
  ident=c['id'];assert len(NOTES[ident])==7
  status,boundary=DECISIONS[ident]
  entries.append(dict(id=ident,member=c['member'],nbt_sha256=c['nbt_sha256'],status=status,
   observations=dict(zip(FIELDS,NOTES[ident])),purpose_and_scale_boundary=boundary,
   images_actually_viewed=[ev(OUT/n) for n in c['images']+[ident+'-details.png']],
   credit_proposal=int(ident=='F01'),formal_credit_added=0,native_acceptance=False))
  with ZipFile(c['source_archive']) as z:
   d=read(z.read(c['member']));pal=d.get('palette') or d['palettes'][0]
   states=[dict(position=b['pos'],state=pal[b['state']]) for b in d['blocks'] if pal[b['state']]['Name'].split(':')[-1] in KINDS]
   top=[dict(position=b['pos'],state=pal[b['state']]) for b in d['blocks'] if b['pos'][1]==5 and pal[b['state']]['Name'] not in {'minecraft:air','minecraft:structure_void'}]
  fittings.append(dict(id=ident,nbt_sha256=c['nbt_sha256'],original_fittings=states,y5_nonair_states=top))
 comparison=ROOT/'docs/architecture/continuation-20261022/references/whole-candidates-003'
 dump('manual-review.json',dict(entries=entries,counts=dict(templates_studied=4,new_images_actually_viewed=16,
  historical_images_reviewed_again=2,proposals=1,uncovered_support_space=1,excavation_or_geode_only=2,formal_credit_added=0),
  historical_comparison_views=[ev(comparison/n) for n in ['C004.png','C004-plan.png']],
  comparison_decision='F01与最邻近旧C004寺庙不同：双工作跨、敞口木柱梁和平覆顶，对照封闭方祭室、外前院、低分层坡盖及单门。相似度0.37188仅用于筛查。',
  family_boundary='F01/F02同一来源池、同柱梁炉桶语言；只提案F01覆盖工作棚，F02裸梁跨不另提案。F03坑与F04晶洞的矿石壳不计成房屋。',
  principles=['文件名large/small与实际尺寸分别核对，不能套巨型工坊标签。',
   '覆顶棚、裸梁跨、露天坑和晶洞设施先分清，再讨论相应用途。',
   '分类投影把地毯、矿石、栏杆和活板整格显示；器具与原始方块状态复核后再作布局观察。',
   '将热工器具、储料和工作留空分边布置，可以作为小型矿业支援房的尺度参考；没有运输、加工或机器玩法验收。',
   '局部五格梯只说明模板内梯段，不能补成洞顶环廊、主矿道或索道动线。']))
 dump('fittings-and-cover.json',dict(entries=fittings,formal_credit_added=0,
  limits='Original states and y5 cover only; no native collision, interactability, terrain or building credit inferred.'))
 print('Four actual mining studies, one covered-workshop proposal, three scope/whole-building exclusions, zero formal credit.')
if __name__=='__main__':main()
