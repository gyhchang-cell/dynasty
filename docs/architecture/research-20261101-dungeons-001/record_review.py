#!/usr/bin/env python3
"""Persist manually observed research, without changing any reference credit."""
import hashlib
import json
from pathlib import Path

OUT=Path(__file__).resolve().parent
FIELDS=['layout','proportion','facade','roof','materials','circulation','terrain']
# Each observation follows actual viewing of whole, plan and vertical images.
NOTES={
'F01':[
 '低围墙院落包围高主堡，前侧门楼、角塔与后部主厅分开；不是单塔复制成城。',
 '42×32×35保存边界，主堡明显高于前院墙；高低两级形成入口到主堡的方向性。',
 '角部突出方塔、窄窗和垛口形成防御立面，主厅山墙外露木构分层。',
 '主厅有木构坡顶截面，周边塔与城墙采用可活动的平顶垛口，不能全部按平屋面复刻。',
 '原始状态以stone/stone_bricks/andesite为主体，dark_oak_wood与spruce楼板、活板门分层；图中棕色不等于真实材质贴图。',
 '底层多门连接不同房间，切开图能见院内与主堡的分隔；现有截面不足以证明每个楼层完整可达，需后续按梯位核实。',
 '底部一个terrain_large接口用于垫地；本次未拼接地基，不能据模板平底声称山地生成适配。'],
'F02':[
 '整体为密集城堡遗址，底层网状分室，上部多塔残墙，侧向伸出的桥把入口与主残堡联系。',
 '48×45×48边界；塔高与底座接近，四周低矮苔石裙边弱化方形基座。',
 '残缺墙头、不同塔高和侵蚀带贯穿立面，破损并非只在墙面随机换色。',
 '上部多处露天坍塌，残存阶梯屋面与垛口；这是完整遗址布局候选，不能当完整有顶住宅。',
 'stone、stone_bricks、mossy_cobblestone、moss_block、andesite和mossy_stone_bricks构成灰绿风化层。',
 '底层y2/3分室和iron_door很多，桥接高位入口；最低门不是主入口，完整通关连通性尚未验证。',
 '苔石堆形成不规则台脚，下方terrain_large接口未展开；桥端与原生地形的连接未知。'],
'F03':[
 '近圆形封闭塔，水平木楼板反复分层，顶部露台；外壳本身完整，不是外接房间组件。',
 '23×21×23，宽略大于高，属于厚重鼓形塔；不能用于细高八卦柱的比例范本。',
 '深色石壳竖向壁柱与木圈梁交替，外缘支撑沿周圈布置。',
 '平顶露台以短垛围合，屋面有零散构件和储物；不是尖顶塔。',
 'cobbled_deepslate/deepslate及其裂砖瓦配dark_oak/spruce木构，结构色带对应不同材料族。',
 '纵剖可见约y4、8、12、18楼板，门集中底部及y13；中心剖面不能替代楼梯全路径证明。',
 '中底terrain_small接口为地形承托，外侧底脚平齐，未获得生成后山坡证据。'],
'F04':[
 '15×10×15石块内部只有零碎水腔和刷怪/箱位置，缺乏完整入口与房间组织证据。',
 '低矮实心长方块占绝大多数体积，水腔碎小，不能当水宫或完整冰窟。',
 '外观四面连续封闭石面，未见可辨识门洞或建筑正面。',
 '顶部为整块封闭石层，不能据名称推断水下穹顶。',
 'cracked_stone_bricks、mossy_stone_bricks、tuff、mossy_cobblestone与water，含seagrass/kelp；不是冰材质。',
 '没有门；水平和纵剖内水腔被大量石块分隔，未证明能由外界进入。',
 '无拼接接口；海底埋藏与可破坏进入方式未核验，排除完整建筑计数。'],
'F05':[
 '方形塔四角粗柱围中央楼层，上部收成台阶状顶；外墙、门、内楼板均在同一模板。',
 '19×25×19，高宽约1.32，方柱厚、室内集中，比F03高窄但不是独立高阁。',
 '四角柱连贯到顶，长墙窗少，顶部木带与开孔形成一圈水平分界。',
 '阶梯状收分顶、四角短垛向上延续，剖面见上部梁和封顶；不是四座独立角楼。',
 'polished_andesite、cracked_stone_bricks、stone_bricks配spruce_planks和dark_oak_slab；基层有grass_block。',
 '北侧y5双门，剖面约y4、9、14、18楼层和中部木构，入口高于模板底；楼梯碰撞未验证。',
 '门前小台阶和底部苔草过渡，terrain_small接口尚未展开，不能直接放到任意悬崖。'],
'F06':[
 '雪覆盖的残墙与地基，只有断开的围合痕迹；没有完整楼板和入口体系。',
 '15×10×15，与F04边界相同但体量是低矮残基加单侧高墙，绝非同一换色壳。',
 '墙体大缺口、断柱和积雪形成不连续界面；不能当有意通道已验收。',
 '无连续屋顶，只有积雪覆盖残墙顶。',
 'snow_block/snow、stone_bricks、stone、andesite和powder_snow；粉雪与实心雪的碰撞差异不能从图色判断。',
 '无门和明确分层交通；两处箱位只是遗址点，不代表完整探索路线。',
 '残基平铺，未核验雪地高度和粉雪陷落；排除完整建筑计数。'],
'F07':[
 '紧凑围合堡以高主塔和低门楼包围小院，室内和环形外墙包含于一个完整模板。',
 '35×35×30，高主塔偏一侧，低矮城墙围院，明显不同F01的多方塔主厅组合。',
 '基座多层退台、窗框、木带及浅色斜撑，主塔上层外挑，门楼高度低。',
 '主塔宽顶配低门楼坡面，顶部浅色区域需按原始状态识别，不能凭图色推定积雪。',
 'stone/stone_bricks/cracked_stone_bricks配spruce楼板、楼梯、木梁，底部grass_block；整套石木构。',
 '最低双门在y3，其他门位沿y6/y8及更高层分布，纵剖主塔有多层房间；16接口全为mobs，不是16缺失建筑。',
 '底部平地基，无外接房间池；外围地面与坡脚如何贴合仍须生成验证。'],
'F08':[
 '宽大城墙围生活院落，主厅坡顶位于一侧，内有低矮房舍和围墙通道；完整围城布局而非单栋主厅。',
 '75×56×65保存边界含高屋脊，主要院墙约二十余格，院宽明显超过墙高，中心留空。',
 '立面以外凸支柱、垛口和垂藤分段，内侧木走道清楚区别于院地。',
 '主厅高坡顶和院内低坡/平顶并置；围墙自身为露天城垛。',
 'stone、spruce_planks、cracked_stone_bricks、stone_bricks、cobblestone、tuff和苔石，木屋与石墙材料分工。',
 '地面多双门分区，墙内高处有走道；21接口是村民、马、铁傀儡，不代表外接21房间。院内到每段墙顶未实测。',
 '宽平基座与外围苔藤，不含可证明的自然山地桥接；不能把藤蔓当实际交通保障。'],
'F09':[
 '小塔坐于中央岛台，外围分散小石团不与主塔连接；一个塔设计，不是多座完整建筑。',
 '54×35×68边界被远离塔的小石团撑大，实际塔平面远小于全模板，不能按54×68称大型宫殿。',
 '石脚托木石混合塔身，上层出挑，开窗与梁框分层。',
 '多级尖锥屋面逐级收束，底部入口台与上部尖顶形成高低主次。',
 'stone/cobblestone/andesite配oak_log、dark_oak_stairs、smooth_sandstone及spruce木件。',
 '门位y7/11/15表示上下室层，外侧有短台；三个接口是村民，外围石团之间不应假称已有安全桥。',
 '本模板有独立石质底台和散石，但不能单凭island文件名认定天空维度或悬空生成规则。'],
'F10':[
 '木栅围合内有两座不同高度残塔、树和破损中部木构，属于完整占地的遗址场景，内部建筑连通未证实。',
 '44×48×36，最高细塔占视觉重心，树冠占院地较多，不能以保存高度推断三层可用建筑。',
 '石塔断口、攀藤和木栅界定遗址，中央构造上半部木件暴露。',
 '没有可确认的连续主屋屋面，中央尖木轮廓也可能是残梁；本次不按完整有顶主堡计数。',
 'dark_oak_leaves/log、grass_block、stone_bricks、spruce_leaves和iron_bars占主导。',
 '无门或房间拼接接口，底层刷怪/箱位并不证明塔内可登顶，尤其不能用树叶连成假通路。',
 '整体平底、周边草坡小幅过渡，周界树叶遮挡需结合真实碰撞；保持待核/不计数。'],
'F11':[
 '冰壳内收纳窄木层与竖向梯井，顶部小台是附属层，同一冰塔不能按五刷怪位拆分。',
 '16×27×17，高宽约1.69，冰壳向上急剧收细；实用房间主要在底部几层。',
 '不规则冰柱构成锥状外缘，中高处伸出小木台，区别于F03鼓塔和F05方塔。',
 '顶部冰尖为外形终点，环台有石/金色边，不能当多层宽屋面。',
 'packed_ice/blue_ice配spruce_planks/slab、20个ladder和少量木柱；必须考虑冰面低摩擦。',
 '底门y1、上层门y5及连续梯状态支持垂直交通意图，但中心剖面中高段很窄，未验证所有到顶落脚点。',
 '冰脚向四方延伸，周边雪原/水面接地仍未知，不能证明深潭水宫或冻龙洞已被参考覆盖。'],
'F12':[
 '小方塔上下叠室，侧向悬出木件与斜屋面、烟囱构成偏心轮廓；完整塔模板非独立顶片。',
 '13×36×15边界包含烟囱上方散块，主室宽约数格，保存高宽比不等于室内净高。',
 '石柱、木梁和浅色窗格交替，二层向外挑出，烟囱偏于屋面一侧。',
 '木坡屋面与弯折烟囱组合，顶部漂浮小块是视觉尾迹，不能计为独立楼层。',
 'cobblestone及stairs、oak_fence/log、jungle_slab/planks与stone_bricks，底脚dirt/grass。',
 '门位y3/7/16，对应多个层次；两个接口仅witch，窄室内竖向交通还需核对梯与净空。',
 '底部木石脚小范围外伸，模板中没有悬崖栈道或大型院落；只能借鉴塔的局部层级。'],
}

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 source=json.loads((OUT/'sources.json').read_text())
 entries=[]
 strong={'F01','F02','F07','F08'}
 local={'F03','F05','F09','F11','F12'}
 for c in source['candidates']:
  ident=c['id'];assert len(NOTES[ident])==7
  status='COMPLETE_FORTIFICATION_LAYOUT_CANDIDATE' if ident in strong else 'COMPLETE_TOWER_SUBSPACE_ONLY' if ident in local else 'EXCLUDED_OR_INCOMPLETE_LAYOUT'
  entries.append(dict(id=ident,member=c['member'],nbt_sha256=c['nbt_sha256'],observations=dict(zip(FIELDS,NOTES[ident])),
   images_actually_viewed=[dict(path=str(OUT/f),sha256=sha(OUT/f)) for f in c['images']],
   completeness_and_relevance=status,
   applicable_target='DUN03 ruined fortifications / whole defensive layout' if ident in strong else 'vertical tower subsystem only; not a full DUN04/07/08/09 complex' if ident in local else 'no whole-related-building credit',
   independent_design_basis={
    'F01':'院落、方角塔、主厅三级体量', 'F02':'高位桥、低层密室和高塔遗址整体，非F01换色',
    'F03':'近圆鼓形多层平顶塔', 'F04':'与F06同尺寸但占用、水腔和外壳都不同；二者均不计完整建筑',
    'F05':'方形四角柱塔与阶梯收顶', 'F06':'低残基和单侧雪覆高墙，非F04换色',
    'F07':'偏侧高主塔包小院、低门楼，非F01多方塔主厅', 'F08':'宽墙院、偏侧高坡主厅和内侧墙廊',
    'F09':'中央小尖顶塔及外围散石，只计一个设计候选', 'F10':'木栅、双残塔和树木围场，非F02密室高堡',
    'F11':'收细冰壳、窄梯井、外挑环台', 'F12':'方小塔、偏心坡顶、弯烟囱'}[ident],
   formal_credit_added=0,requires_full_historical_family_dedup=True))
 review=dict(date='2026-11-01',method='Actual manual viewing of 36 offline approximations from original local NBT; no native game verification',
  counts=dict(templates_studied=12,images_actually_viewed=36,strong_whole_fortification_candidates=4,tower_subspace_only=5,excluded_or_held=3,formal_credit_added=0),
  caveats=['图像为方块占用近似与材料分类色；不是原版纹理、台阶碰撞或地形生成效果。','完整城防候选仅对DUN03用途相近；单塔不等于完整寺观、水宫或地下城。','所有不同角度、楼层和接口不重复计数；当前148例的原任务范围不能搬到十地下城。','强候选仍需全历史设计家族核对，未改正式参考台账。'],
  entries=entries,
  applicable_principles=['围墙院、主堡、门楼的高低关系先服务路径，再作表面风化。','完整遗址可保留残损，但必须有完整占地、分区与可解释的主入口；孤墙不能冒充遗址整体。','读保存边界必须剔除远处散石、烟尾等对尺度的影响。','封闭水腔与完整水宫差别在入口、可用空间、持续动线和水位转换。','尖塔上部收细时，不以外观高耸替代可站立平台、梯口和双格净空。'])
 (OUT/'manual-review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':main()
