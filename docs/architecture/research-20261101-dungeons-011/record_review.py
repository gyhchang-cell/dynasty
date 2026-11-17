#!/usr/bin/env python3
"""Record actually viewed tower volumes, semantic differences and original states."""
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
  '单一细颈木石塔身托起宽大的上层瞭望室/环缘，底部散石与工作角不形成外城院；整座上大下收的塔一次，不拆四向门廊。',
  '21×31×21，占用y0..30；大上层木板约y18，普通门全在y19，主檐约y21/22，细旗到y30；31格不等于31格房间高度。',
  '中央木柱、逐层外收/外撑木石轮廓与上层四向突出门湾分工明显，低段窄于上层；不是旧dark_keep厚石方体加侧门堡的立面组织。',
  '宽低坡多边形主盖配中央小抬帽，上缘灰色包含地毯与木半砖，不称全石屋顶；屋顶变化本身不作为独立设计证据。',
  'oak_slab652、stripped_oak_log351、stone_bricks252、oak_planks245、oak_fence157、birch_planks154、light_gray_carpet42；屋缘灰投影不能掩盖木构件主材。',
  '六个普通门均y19；无梯方块。补看y6/y18与x9/z10剖，见中央竖柱周边升降构件和较大上层板，但未原生验证从底部至全部高门/平台的碰撞净空。',
  '模板自带草、碎石与较开阔地脚，没有封闭围院；12点是11grunt和1captain。提案DUN03细颈宽顶单瞭望塔，不能计入双高塔或四低棚围院。'],
 'F02':[
  '多边形低围栏场地围中央逐级收分的高塔，中下段平台与更小上段室沿竖轴叠置；不同于010-F02粗角柱包笼室的等宽叠层台堡。',
  '27×44×27，占用y0..43，约y9、y18和y23有平台/室层，约y30以上继续收为细上构；不能把全部44格视作宽大可用塔室。',
  '浅砂岩柱、横向环檐和较宽木平台交替，低处围栏与高塔体分开；研究竖向尺度收分，不把源文件oriental名字当中国塔风格已验。',
  '多层外挑环檐逐级变小，上部是小帽、细颈及旗饰；不是三座独立塔，也不能将每道檐线当一层完整居室。',
  'sandstone867、oak_slab335、cut_sandstone287、sandstone_stairs286、sand282、oak_planks248、stripped_oak_log182、oak_stairs149、cyan_terracotta62；砂岩与木步阶/木平台各自承担不同层次。',
  '无普通门；中央木步阶原状态见y1..18，x12,z11及x14,z11梯均仅y19..23。补看y9/y23与梯侧剖，不能从此推定细上颈都能登顶。',
  '沙土碎石与多边低围栏含在本体；10点为8grunt、1captain及1minecraft:village/common/cats。猫池不在当前JAR，未取得其定义，不声称生成依赖全验；本体完整形态提案与该配置缺口分开。'],
 'F03':[
  '横向长厅上穿入一高一低两处尖顶竖段，另有两侧低门廊/小挑间；用途源属前哨，但空间更接近长厅连偏置高望楼，不是独立圆/方单塔。',
  '24×37×15，占用y0..36，长厅屋脊约y13，小尖顶约y22，高竖段屋帽约y26后接细旗到y36；高旗与尖帽不算宽房层。',
  '深木框、黑石地脚、灰玻璃长窗和两端较窄突部形成强横轴，高竖段偏在一端；与旧W007雪地寺庙对称叠坡居中上室不同。',
  '长双坡顶被大小不同竖段穿破，各有独立尖帽与细旗，低门廊坡顶向侧面落下；整个连厅望楼算一次，不拆两尖顶。',
  'stripped_dark_oak_log620、polished_blackstone_bricks141、dark_oak_stairs136、deepslate_brick_stairs115、spruce_planks105、dark_oak_trapdoor95、deepslate_tile_stairs95；暗色不是统一深木贴图。',
  '无普通门；x13,z5及x13,z9梯y1..7。补看y8/y19、x13/z7，低梯只连接较低空间，不能冒称高竖段y19乃至旗顶原生可达。',
  '底部近建筑足印，少量草叶与凹入门廊，不是大围城场地；7点为6grunt和1captain。提案DUN03横长厅连偏置高望楼，限定24×37×15整个组合。'],
 'F04':[
  '紧凑近方塔由下部石木骨架、中部较封闭浅墙房和上部环缘空间组成，中央柱及升降构件贯穿；没有F01宽大多边上室的显著蘑菇状外挑。',
  '15×39×15，占用y0..38；主要中层板约y13，上缘/檐约y19/20，屋盖至约y32后是细旗；不能按39格认成多层高楼全是房。',
  '下段灰石骨架、上段方解石木框填墙与细立柱形成分区，转角/横带在同一方塔边界内；与旧dark_keep厚实体石墙四角与侧门堡不同。',
  '大砖四坡帽上接逐级缩小尖端和旗杆，中层墙房在檐下；屋顶及红白配色本身不够作为与F01不同的证明，结合层板位置、塔身收分和上室足印判断。',
  'bricks296、stripped_spruce_log179、andesite_slab174、stone_slab167、spruce_slab167、spruce_fence156、brick_slab121、calcite96；白墙为方解石，不能凭浅色笼统称石英。',
  '无普通门；中央周边木阶在y7..13循环分布，x6,z7梯y14..20。补看y13/y20及x6/z7剖，保留原始上升序列，不把檐上尖顶或旗杆认作到达楼层。',
  '地脚较小，仅少量草地和侧边点位，11点是10grunt和1captain。提案DUN03紧凑方形分层守望塔，独立性须复核主体空间，不能当F01换屋顶自动多一例。']}
TARGET={'F01':'DUN03细颈宽顶单瞭望塔，21×31×21。','F02':'DUN03低围栏内逐级收分高塔，27×44×27；外接猫池定义缺口保留。',
 'F03':'DUN03横长厅连偏置高望楼，24×37×15。','F04':'DUN03紧凑方形分层守望塔，15×39×15；主体布局独立性待范围负责人复核。'}
COMPARE=[('research-20261101-dungeons-002','F02-whole.png'),('research-20261101-dungeons-010','F02-whole.png'),('continuation-20261022/references/whole-candidates','W007.png')]
def ev(p):return dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def dump(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def main():
 s=json.loads((OUT/'sources.json').read_text());a=json.loads((OUT/'interface-audit.json').read_text());entries=[];states=[];actors={}
 for c in s['candidates']:
  i=c['id'];entries.append(dict(id=i,member=c['member'],nbt_sha256=c['nbt_sha256'],observations=dict(zip(FIELDS,NOTES[i])),
   proposed_target=TARGET[i],independent_design_basis=NOTES[i][0]+' '+NOTES[i][1],
   status='SCOPED_WHOLE_TOWER_PROPOSAL_PENDING_FAMILY_REVIEW',images_actually_viewed=[ev(OUT/n) for n in c['images']+[i+'-details.png']],
   credit_proposal=1,formal_credit_added=0,native_acceptance=False))
  with ZipFile(c['source_archive']) as z:
   d=read(z.read(c['member']));p=d.get('palette') or d['palettes'][0]
   states.append(dict(id=i,nbt_sha256=c['nbt_sha256'],stairs_doors_ladders=[dict(position=b['pos'],state=p[b['state']]) for b in d['blocks'] if p[b['state']]['Name'].endswith(('_stairs','_door')) or p[b['state']]['Name']=='minecraft:ladder']))
   for pool in next(x for x in a['entries'] if x['id']==i)['outgoing_pools']:
    for comp in pool.get('component_identities_only',[]):
     raw=z.read(comp['member']);cd=read(raw);cp=cd.get('palette') or cd['palettes'][0]
     actors[comp['member']]=dict(member=comp['member'],sha256=hashlib.sha256(raw).hexdigest(),size=cd['size'],
      entity_ids=[e['nbt']['id'] for e in cd.get('entities',[])],materials=dict(Counter(cp[b['state']]['Name'] for b in cd['blocks'])),
      images_viewed=False,building_credit=0,assembled=False)
 dump('manual-review.json',dict(entries=entries,counts=dict(templates_studied=4,new_images_actually_viewed=16,historical_images_reviewed_again=3,proposals=4,formal_credit_added=0),
  historical_comparison_views=[ev(OUT.parent/f/n) for f,n in COMPARE],semantic_deduplication=[
   'F01/F04最近旧dark_keep是厚石方堡和侧门堡连块；新例分别细颈宽顶、多层窄方柱框，没有旧两块厚墙堡组织。',
   'F02最近010-F02为粗四角柱、下层笼室及等宽台堡；新例是多边外围低场地、中央层层收分高塔。不是仅把台堡换砂岩。',
   'F03最近旧W007是居中对称上层与连续叠坡；新例横长厅带两处不等高偏置竖段、侧门廊及高望楼，不因同用暗木屋顶判新/重复。',
   'F01/F04同属中心柱单塔，不能只凭屋顶不同计数。F01上板y18且21格宽、下收细颈/四向高门；F04方形板y13、紧凑15格界内分层浅墙室及上段梯。此主体区别随提案交独立复核，不宣称已经通过家族验收。'],
  principles=['模板最高点包括旗杆、尖帽，不等于有效室高或楼层数。',
   '看上室足印与下部塔颈关系，再看是否扩大、收分或同宽叠置；不要只比较屋顶和配色。',
   '较高层普通门不充当地面入口，无普通门也不能直接说建筑缺入口。',
   '分开记录螺旋步阶、短梯与屋面台阶，局部路线不代替全塔碰撞验收。',
   '缺少外接池定义要据实保留缺口，来源命名不证明该池内容，实体权重不增加建筑计数。',
   '单体塔、长厅连望楼和围院堡各限规模用途，不自动拼成一个1000例账本。']))
 dump('vertical-original-states.json',dict(entries=states,formal_credit_added=0,limits='Original states only, not native route certification.'))
 dump('actor-component-boundary.json',dict(entries=list(actors.values()),formal_credit_added=0,
  unresolved_pools=['minecraft:village/common/cats'],limits='Three source actor templates read; vanilla cat pool absent locally and not resolved or credited.'))
 print('Four whole tower studies recorded, all unaccepted and requiring purpose/scale/family review.')
if __name__=='__main__':main()
