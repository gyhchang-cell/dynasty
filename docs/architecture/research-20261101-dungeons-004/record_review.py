#!/usr/bin/env python3
"""Human semantic observations following actual inspection of 32 new images."""
import hashlib
import json
from pathlib import Path

OUT=Path(__file__).resolve().parent
FIELDS=['layout','proportion','facade','roof','materials','circulation','terrain']
NOTES={
 'F01':[
  '集中多层主楼有L形展开的房间与侧向附厅，旁边另有一座独立低屋，共用一片泥地；研究整组酒馆设计一次，不能主楼与附屋拆两例。',
  '48×37×48保存边界，实际最高y35；主楼高、外附屋低且距主楼留空，二者不是等大的双院。',
  '木柱、石横带和外挑楼层分开底层公共入口与上层较小门窗，单门和双门对应不同界面，不能仅以门数推断客房数。',
  '集中主楼上多组交叉高山墙坡顶，独立低屋只有一条低长脊；屋面复杂来自房间体量，不用零碎檐口增加建筑数。',
  'spruce_trapdoor、spruce_fence_gate、spruce_stairs、oak_wood、rooted_dirt、jungle_planks为主；有大量木栅门，整方块图夸大了实墙密度。',
  '底门位于y2，y17补平面见主楼内分室和多处门；x14/z23剖面见约y9/16/23楼板与高低厅关系。无梯子状态，不能断言没有楼梯，也不把屋檐台阶自动当通关路。',
  '泥地院面较宽，terrain_large承托；独立低屋靠地面院道联系，未验证地下埋深或与枉死城连续街面的接缝。'],
 'F02':[
  '多翼房间沿U形组织，中部留开院，侧楼与长翼在上层连接；与F01集中主楼加独立附屋的设计不同，整组旅店只计一个候选。',
  '44×48×43保存边界，但实际占用仅y0..30；48格保存高度不能写成48格高旅馆或相应可用层数。',
  '石基、木框、成排窗及底层多侧入口围院，房间侧与开院侧的界面不同；覆绿分类色不证明整栋荒废。',
  '三向长坡顶与端部高山墙围开院，低连接顶和较高端楼顶并存；屋盖没有封闭整个院心。',
  'dried_kelp_block1324格是重要绿色屋面材料，另有spruce_trapdoor、spruce_stairs、spruce_planks、stripped_spruce_log和moss_block；绿色不能一律写成苔藓。',
  '底门y1，上门集中y6/7及一处y13；y7/13平面见U形层次。两段短梯在x31,z5的y7..9和x37,z18的y7..8，不是两条通顶长梯。剖面可读楼板约y5/12，完整楼梯碰撞未验。',
  '不规则草泥裙和terrain_large底接口；只研究街区旅店围院与楼层关系，不把单座地上旅店当完整地下阴城或中式官衙。'],
 'F03':[
  '紧凑上下两层小宅，底层轮廓不规则，上层分隔较零碎，外部碎石与缺损屋盖突出；保留为破损住宅研究，未按完整可用民居提出计数。',
  '23×20×21保存边界，实际最高y18，屋体主要约y3..14；宽草裙和孤立高块不应计为房间净面积或新楼层。',
  '灰石、红褐砖泥和木构交错，边角有破损与外露墙芯；乱色不是额外墙厚，植物也不是支柱。',
  '屋盖局部木石平框有缺口、散块及突出竖件；无法仅凭old名称确认每个开洞属于设计意图或安全采光口。',
  'spruce_slab、polished_granite、mud_bricks、polished_andesite、packed_mud、granite与bricks混用；红色并非统一红砖。',
  '底门(12,3,15)，上门多在y8；x12,z12梯仅y8/9，补剖看见上下分室与约y6楼板，底层到上层的连续可靠路径仍未锁定，不假定可从外部残块一路上楼。',
  'terrain_small底接口和草泥裙，不等于已验证街巷贴地或地下落位；暂不计入完整民居范围。'],
 'F04':[
  '横向宽主屋向前伸一条窄翼，构成T形多层住宅；不同于F03不规则小破宅，也不同于F02围开院的旅店。',
  '27×37×31保存边界，实际最高y34；宽后屋高脊、窄前翼较低，屋顶占据相当高度，不能按保存高度分出多层完整客房。',
  '深色基座、木柱及水平腰带分层，前翼长边有成排门状构件；这些门状态与屋面、窄走道混用，不能按门扇数量宣称同样多的独立房间。',
  '后屋长高山墙顶与前翼低坡顶垂直相接，z9补剖显示长脊屋盖及其下大空腔；屋盖中的成排门也不能当对外入口。',
  'dark_oak_planks、spruce_planks、grass_block、dark_oak_trapdoor、spruce_trapdoor、spruce_stairs与soul_soil为主；石木构造与草泥基裙分开。',
  '底门y3，内门另在y9/14，高门集中y19/25；y14/19补平面确认T形分区和前翼窄层，x13剖面可见约y2/7/12/17/22层次。无ladder，成排高门不自动证明彼此独立或全部可达。',
  'terrain_large接口，基座高差在模板内；可借鉴街区多层住宅体量与屋面高差，未验证中式街面立面或屋顶跑酷连接。'],
 'F05':[
  '宽中央厅体连前后两块较窄厅翼，底层两端可见独立分室，y7形成相连的整组宅院；不按三组屋顶拆多份。',
  '35×31×48，宽而长、屋脊高低适中；公共中厅与两端小厅尺度不同，不是紧凑街铺或高塔堡。',
  '石柱基、木横带、开窗与覆绿层共同构成立面，厅口比次室更通透；外部枝叶遮挡台脚但不是新墙。',
  '中央横脊与两端纵脊相交，端翼较低；y14中心已切到屋面，而端屋还留上层内腔，不能用统一层高描述整组。',
  'oak_leaves、spruce_stairs、dirt、spruce_planks、spruce_wood、dark_oak_trapdoor与moss_block为主。',
  '底门一处y2，多数连接门y7；x20/z35剖面见主厅及端室层板。多处梯仅y3/4，另单梯y3，不可称纵贯三层的完整梯网；只提炼厅翼相接的局部原则。',
  'terrain_large底承托，未证明其为地下判官厅或中式官署；整组虽完整，功能/规模与目标内衙不足以直接对应，暂不提出整例信用。'],
 'F06':[
  '长高主厅与多座角塔、低连接体围出偏侧空院，方塔与圆形塔平面并存；整座连体城馆一个候选，不按角塔数计数。',
  '48³保存边界，实际最高y47，长厅与高塔压住一侧、院与较低房屋留在另一侧；非对称高低体量形成方向性。',
  '浅色柱、红褐腰带、密窗与深石边强调逐层界面，长厅窗和塔窗尺度有别；大量白色块不证明用真正大理石模组。',
  '主厅长陡坡顶配多种尖塔帽和低露台垛口，x13/z11补剖显示约y36以上屋架；露台不是另一独立屋顶设计。',
  'polished_andesite、white_wool、diorite、calcite、birch_wood、white_concrete_powder、birch_planks与quartz_bricks混用；名称marble不能代替原始材质核查。',
  '门分y1/2、10、16、26/28，长厅内y10平面有连续柱列和侧向通道，y26见高层塔室与厅。x13剖面见约y9/25层板；唯一梯x32,z17仅y1..3，不宣称全部高塔已可登顶。',
  'terrain_large底接口，无待拼接侧房；只提案DUN03大型守军城馆的主厅、塔和院组织，不充当完整战场或判官殿，不认证白混凝土粉的生成稳定性。'],
 'F07':[
  '低长厅连一座偏置细方塔/高小室，下层有多个门口；整体为紧凑小宅，与F08低储棚布局不同，也非历史ocean寺的同心退台方体。',
  '17×15×13，主厅低、局部塔室高，保存最高y14；小尺度住房不能升级称大型防御堡垒。',
  '灰石墙、少量木门窗和深色屋面边组成朴素界面，低厅入口与窄塔上下关系分开，植被仅沿台脚。',
  '低厅分段斜坡顶与窄塔平帽组合，塔帽短垛突出；不是F08小坡棚的换色，亦非海底寺的多级四边同心屋顶。',
  'andesite、stone、grass_block、dead_fire_coral_block、gravel、glow_lichen、polished_andesite和cobbled_deepslate_stairs为主。',
  '四个底门均y1，x9,z2梯y1..12连续，x13,z8另有y1/2短梯；y3/8平面和x9剖面可区分低厅、高小室及长梯。未把细塔内部称宽大阁楼或进行原生梯口净空验收。',
  'terrain_small接口，草泥边裙直接包小宅；可作街区小民居与附高室的空间参考，不因illager名称就认作军事设施。'],
 'F08':[
  '一侧较开敞作业棚与一侧小储室并置，短通道联系，整体低矮；不把开放作业区误写成整块封闭大仓。',
  '17×11×13，实际最高y10，小坡屋面和两端墙尖占上部；不适用于DUN02巨兵库或整片机械工场的规模。',
  '灰石端墙、木横梁和局部木门围储室，开棚侧更通透；与F07窄高塔和低厅的比例不同。',
  '短坡棚顶与一侧较高山墙端组合，y6补平面仍可见开棚与小室的不同边界；屋顶块不能当完整上层仓房。',
  'grass_block、dead_fire_coral_block、andesite、stone、spruce_trapdoor、gravel、spruce_stairs、spruce_fence和spruce_slab混用。',
  '底门(4,1,4)/(10,1,6)，x13,z5梯y1..4连续；补剖只见低室与棚内高差，未证明可承担城内连续屋顶路线或大型垂直货运。',
  'terrain_small承托，无外接房间。可借鉴街铺后侧储棚局部，不按原始17×13脚印相近就归为旧stray_ruins的材质变体；旧例是雪覆残墙开院，本例有木棚/储室功能分化。'],
}
PROPOSE={'F01','F02','F04','F06','F07'}
SUBSPACE={'F05','F08'}
TARGET={
 'F01':'DUN05街区大型客栈/公共商屋：公共底层与上层分室；48×37×48保存边界，不覆盖棺材铺机关、官衙或全城。',
 'F02':'DUN05街区围院旅店：U形多翼和开院；44×48×43保存边界、实际高31格，不覆盖整城。',
 'F03':'DUN05破损街宅的材质与上下室局部，完整可用住房范围待核，不计数。',
 'F04':'DUN05街区多层住宅：T形体量与屋面高差；27×37×31保存边界，不覆盖屋顶跑酷路径验收。',
 'F05':'DUN05厅翼相接局部原则；35×31×48的地上宅院，不能直接算中式判官内衙。',
 'F06':'DUN03大型守军城馆：长厅、角塔和侧院组织；48³保存边界，不覆盖全战场或中式瓮城。',
 'F07':'DUN05街区小民居：低厅与偏置高室；17×15×13保存边界，不覆盖军事城堡或大街区。',
 'F08':'DUN05街铺附属小储棚局部；17×11×13保存边界，不覆盖商店完整经营空间、巨兵库或工场。',
}
COMPARISONS=['continuation-20261022/references/whole-candidates-004/D008.png','research-20261101-dungeons-001/F06-whole.png']

def evidence(p):return dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest())

def main():
 source=json.loads((OUT/'sources.json').read_text());entries=[]
 for c in source['candidates']:
  ident=c['id'];assert len(NOTES[ident])==7
  entries.append(dict(id=ident,member=c['member'],nbt_sha256=c['nbt_sha256'],
   observations=dict(zip(FIELDS,NOTES[ident])),independent_design_basis=NOTES[ident][0]+' '+NOTES[ident][3],
   images_actually_viewed=[evidence(OUT/f) for f in c['images']+[ident+'-details.png']],
   proposed_target=TARGET[ident],status='SCOPED_WHOLE_BUILDING_PROPOSAL' if ident in PROPOSE else 'SUBSPACE_PRINCIPLES_ONLY' if ident in SUBSPACE else 'HELD_COMPLETENESS_OR_ROUTE',
   credit_proposal=int(ident in PROPOSE),formal_credit_added=0,native_acceptance=False))
 review=dict(date='2026-11-01',entries=entries,
  method='Manual study of 32 new whole/plan/vertical/detail images and two historical comparison images; original NBT states, occupied bounds and interfaces cross-checked.',
  historical_comparison_views=[evidence(OUT.parent/p) for p in COMPARISONS],
  counts=dict(templates_studied=8,new_images_actually_viewed=32,historical_images_reviewed_again=2,
   proposals=5,dun05_urban_proposals=4,dun03_large_fortified_hall_proposals=1,subspace_only=2,held=1,formal_credit_added=0),
  scope_boundary='Five proposals span different purpose and scale scopes. Do not automatically sum them toward any single scope. They are not implemented assets; no scope is at 1000.',
  principles=[
   '同为旅店，集中主楼加独立附屋与U形连翼开院的进入顺序不同；不能仅学习坡顶和石木配色。',
   '保存边界与实际占用边界都要保留，空余高度、尖饰、屋面内腔不能折算成可用客房。',
   '门状态可用于房间、屋面或装饰；必须结合楼板、墙与净空判断，不按门数数房间。',
   '绿顶可能是干海带块而非苔藓；浅色城馆可能含羊毛、混凝土粉、方解石，名称不替代材料观察。',
   '宅院大中厅只能提供厅翼原则，不能因为体量大就对应判官殿；住宅带塔也不自动成为军堡。',
   '相近占地的小宅和储棚要比较功能分区、竖向连接与屋盖，不靠名称、换色或截图判断重复。',
   '完整建筑最多一例；只有局部相关性或路线缺证时保留研究，不以组件与未核实例填1000门槛。'])
 (OUT/'manual-review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
 print('Recorded eight seven-aspect reviews; five scope-specific proposals, two limited studies, one held; zero formal credit.')

if __name__=='__main__':main()
