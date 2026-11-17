#!/usr/bin/env python3
"""Record five visually studied designs and bounded, unaccepted proposals."""
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from zipfile import ZipFile
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
sys.path.insert(0,str(ROOT/'tools/architecture'))
from nbt_read import read
FIELDS=['layout','proportion','facade','roof','materials','circulation','terrain']
NOTES={
 'F01':[
  '石质断墙围出近矩形露天院，角部塔墙残段高低不同，木门/栅栏缺口和院内小云杉共同形成完整的作者遗址布局；按整座遗址研究，不补想原有完整城堡。',
  '29×17×22，占用y0..16；低墙和高角残段有层级，y8的唯一普通门在高处，不可拿默认门层当院地入口。',
  '石砖、圆石与破损墙垛组成不连续外沿，木栅与木构开口较轻；残断轮廓是原模板特征，不是因渲染漏掉待接房间。',
  '大部分院落和塔残段露天，只有少量残余木构/上缘；研究坍塌后的开放空间，不称全封闭塔楼或完整覆顶厅房。',
  'dirt222、stone_bricks190、grass_block184、stone165、cobblestone145、gravel79、spruce_leaves78、spruce_stairs58；绿冠是院中小树，不是屋顶。',
  '补看y2/y8平面及x3/z3剖面，x3,z3梯y2..7连续，x16,z2梯y2..4；地面木栅开口与高处普通门分记，未认证残墙全程可绕行。',
  '土草、碎石和院树在模板内；8个外接点为7grunt和1captain实体池，不是缺8座楼。只提案DUN03小型石堡遗址围院，不自动并入既有三类前哨。'],
 'F02':[
  '方形厚木柱围起叠层守备平台，低层封闭/笼状小室，中层环行平台，高层开放瞭望台配大屋盖；不是露天中央院加四个低棚。',
  '31×30×31，占用y0..29，低层门y2、中层门y10；高处旗杆不算新楼层，平台与屋盖高度分别观察，不把30格全算可用房间。',
  '深色粗木柱与石砌下层形成重基座，笼栏、侧棚、开敞上台依次减轻；紫色高点为拼图接口，不能读成上层门。',
  '高层宽木屋盖覆盖中央瞭望平台，周边较低小棚与楼层平台外伸；屋盖与平台是同一叠层建筑，不分拆计数。',
  'stone860、stripped_dark_oak_log585、stone_bricks518、oak_planks425、mossy_stone_bricks297、cracked_stone_bricks265、cobblestone251、dark_oak_slab200；按原始方块核实承重柱与屋盖。',
  '低门7处y2、中门4处y10；x7,z16及x23,z14两梯都仅y6..9。补看y10/y17和梯侧剖，局部梯不证明地面至顶层全路线已通。',
  '15接口为13grunt、1captive_jungle、1captain；俘虏模板实为1×3×1单村民实体，不是独立囚室。提案DUN03中型叠层守备平台堡，结构完整但原生路径/地形未验。'],
 'F03':[
  '近圆多边形木围栅包住中央长条营厅，围栅与厅房之间留周边院带；中央低层较宽、上层长室较窄，没有四角独立塔。',
  '35×17×35，占用y0..16，主要长厅低矮横向，最高细构件含烟囱；不能用17格盒高判为17格高瞭望塔。',
  '连续竖木围栅和中央木柱横带区分外围防护与内厅立面；周边杆件和木厅不拆成多个建筑。',
  '中央高长双坡顶加低层宽檐形成两段屋面，烟囱超过主脊；高低屋面只表现层次，不靠屋顶不同给旧木屋加数。',
  'dirt438、spruce_planks409、stripped_spruce_wood293、dark_oak_planks271、stripped_spruce_log246、dark_oak_slab168、dark_oak_stairs156；灰色边饰不凭分类色全称石瓦。',
  '唯一普通门(16,2,12)，无梯方块；补看y3/y8与门侧剖，保留中央上下空间及外围院带证据，未凭无梯断言上室不可达，台阶全量另存。',
  '土、粗土、缠根土与灰化土铺成围栅内外地裙，13点为11grunt和2captains。提案DUN03近圆木围栅中央营厅，不借用旧四棚或角塔L厅范围。'],
 'F04':[
  '紧凑驻所本体由低房、开放柱廊、端部较高小室组成；两处外接field地块不在本体视图，不把一栋房和未装配外围称已完成堡垒园区。',
  '16×15×19，占用y0..14，细烟囱贡献最高高度；房间主体远低于15格，不按盒高归入高塔。',
  '浅色石英墙柱与红砖檐组合，周边藤叶遮局部门廊；开放柱间入口和普通门区别记录，原模板无普通门。',
  '低主体砖双坡盖连小型抬高端帽，门廊小檐更低；主檐、端帽、烟囱与实际房间分别判断，不把细烟囱算可用阁楼。',
  'brick_slab279、oak_planks274、quartz_bricks166、quartz_pillar141、bricks80、grass_block59、spruce_trapdoor53、vine36；外接field原始材料无作物，不能叫已完成农田。',
  '梯(4,6)y2..7，(6,4)/(11,5)y2..4；补看y3/y7及x4/z6，能观察局部上下连接，不保证所有高小室或外接场地可达。',
  '10点为7grunt、1captain及2field；两种field实际为围栏草地/储料地块，含各4grunt和1empty接口，未装配也未计建筑。驻所本体可供门廊小室研究，当前完整守备堡/园区提案暂缓。'],
 'F05':[
  '不规则低围栏院内是高窄长厅加一侧较低工作/入口翼楼，中央高厅有纵深；不同于单角方塔连接L形低厅，也不同于圆围栅中央低长营厅。',
  '36×21×34，占用y0..20，高窄主厅与低附翼形成显著主次；上部陡顶占高度，不当21格全是实用楼层。',
  '浅方解石墙填在深木框间，低层石基、烟囱/竖带和高厅端面构成重点；周界低栅不称连续高城墙。',
  '中央陡长双坡顶，侧翼低双坡/门廊顶顺轴伸出；高低屋脊和低围栏共同决定轮廓，不靠石木换材判新设计。',
  'spruce_stairs373、stone_bricks236、stripped_spruce_log230、spruce_trapdoor212、oak_planks211、spruce_slab184、calcite146、spruce_fence138；浅墙为方解石，不是凭黄色分类读成砂岩。',
  '底门(23,1,12)/(25,1,16)；梯(13,15)y7..9、(15,11)y7..12、(17,16)y7..9。补看y7/y12及主梯剖，确认上段连通线索，不声称地面到y6或全屋路径已验。',
  '不规则草土地裙、低栅和附翼均在模板内；13点是12grunt和1captain，没有额外房间池。提案DUN03低栅院高长守备厅加低附翼，按整组一次。']}
TARGET={'F01':'DUN03小型石堡遗址围院，29×17×22；保留完整遗址原貌，不重建想象屋顶。',
 'F02':'DUN03中型叠层守备平台堡，31×30×31；下部小室/上部瞭望平台。',
 'F03':'DUN03近圆木围栅中央低长营厅，35×17×35。',
 'F04':'小驻所本体门廊/端部小室研究；堡垒用途不符及外接场地未装配，暂不提案完整堡。',
 'F05':'DUN03低栅院高长守备厅加低附翼，36×21×34。'}
COMPARE=[('research-20261101-dungeons-007','F08-whole.png'),('research-20261101-dungeons-002','F09-whole.png'),('research-20261101-dungeons-005','F01-whole.png'),('research-20261101-dungeons-001','F04-whole.png')]
def dump(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def ev(p):return dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def main():
 s=json.loads((OUT/'sources.json').read_text());entries=[];states=[];components={}
 for c in s['candidates']:
  i=c['id'];entries.append(dict(id=i,member=c['member'],nbt_sha256=c['nbt_sha256'],
   observations=dict(zip(FIELDS,NOTES[i])),proposed_target=TARGET[i],independent_design_basis=NOTES[i][0]+' '+NOTES[i][3],
   status='WHOLE_RESIDENCE_FORT_PURPOSE_AND_COMPOUND_HOLD' if i=='F04' else 'SCOPED_WHOLE_FORT_PROPOSAL',
   images_actually_viewed=[ev(OUT/n) for n in c['images']+[i+'-details.png']],
   credit_proposal=int(i!='F04'),formal_credit_added=0,native_acceptance=False))
  with ZipFile(c['source_archive']) as z:
   d=read(z.read(c['member']));p=d.get('palette') or d['palettes'][0]
   states.append(dict(id=i,nbt_sha256=c['nbt_sha256'],stairs_doors_ladders=[dict(position=b['pos'],state=p[b['state']]) for b in d['blocks'] if p[b['state']]['Name'].endswith(('_stairs','_door')) or p[b['state']]['Name']=='minecraft:ladder']))
   audit=json.loads((OUT/'interface-audit.json').read_text())
   for pool in next(a for a in audit['entries'] if a['id']==i)['outgoing_pools']:
    for comp in pool['component_identities_only']:
     m=comp['member'];raw=z.read(m);cd=read(raw);cp=cd.get('palette') or cd['palettes'][0]
     components[m]=dict(member=m,sha256=hashlib.sha256(raw).hexdigest(),size=cd['size'],
      entity_ids=[e['nbt']['id'] for e in cd.get('entities',[])],
      materials=dict(Counter(cp[b['state']]['Name'] for b in cd['blocks'])),
      sockets=[dict(position=b['pos'],data=b.get('nbt',{})) for b in cd['blocks'] if cp[b['state']]['Name']=='minecraft:jigsaw'],
      role='actor' if '/pillagers/' in m else 'fenced_grass_or_storage_plot_not_crop_farm',
      images_viewed=False,assembled=False,building_credit=0)
 dump('manual-review.json',dict(entries=entries,counts=dict(templates_studied=5,new_images_actually_viewed=20,historical_images_reviewed_again=4,proposals=4,scope_held=1,formal_credit_added=0),
  historical_comparison_views=[ev(OUT.parent/f/n) for f,n in COMPARE],
  semantic_deduplication=[
   'F01最近旧007-F08是封闭书房及完整平顶围院；新为断石墙、残角段、小院树的作者完整遗址，不只是图像旋转或换材。',
   'F02最近旧002-F09道场是双层四坡大檐和下廊；新为粗角木柱、笼状下室、叠层开放台和高瞭望棚，差别在房室/平台组织。',
   'F03/F05最近旧005-F01小屋有园篱和不规则住屋屋面，但无环形高木围栅的中央营厅，亦无低栅院内高窄守备长厅+低工作翼；不能仅以hash不同证明。',
   'F04最近旧001-F04是覆岩水下地牢，本体的柱廊砖顶驻所明显不同；几何最近分数本身不提供用途相近证明。',
   'F03与F05虽都有木围护和中央房，但围护高度/形状、主厅长宽高、附翼组织和屋面层级不同；前者近圆高栅中央低长厅，后者低栅不规则院高长厅连低翼。',
   '四项提案均不直接计入旧双高塔、单角高塔L厅、四低棚范围；完整遗址、叠层台堡、围栅营厅、高厅附翼分别限用途和规模复核。'],
  principles=['完整遗址可以按作者实际完整构图研究，但不能想象缺顶后的原堡规模。',
   '先区分围院、围栅营厅与叠层平台；单个组合的房间、塔、院、旗杆不拆数。',
   '地面入口、上层门、拼图接口分别看；默认最低普通门可能在高处。',
   '高细烟囱和旗杆不增加楼层，局部梯段不等于从地面到顶部的完整可达证明。',
   'field只是源命名，必须看原始材料和布置；草地围栏/储料地块不冒称农田。',
   '原始实体模板可核验配置而不计建筑；室内功能和外接园区完整性分开记录。']))
 dump('vertical-original-states.json',dict(entries=states,formal_credit_added=0,limits='Raw stair/door/ladder states only; no native collision or full route certification.'))
 dump('secondary-component-boundary.json',dict(entries=list(components.values()),formal_credit_added=0,
  limits='Four one-actor templates and two fenced grass/storage plots; source identities/materials only, no rendered assembly or reference credit.'))
 print('Recorded five visual studies, four pending proposals, one compound/purpose hold; formal credit zero.')
if __name__=='__main__':main()
