#!/usr/bin/env python3
"""Manually studied observations; proposals are separate from formal credit."""
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
FIELDS = ['layout', 'proportion', 'facade', 'roof', 'materials', 'circulation', 'terrain']
NOTES = {
 'F01': [
  '两端厅楼与两条长边城墙围成长院；边墙有短塔，整个连院城堡为一个设计，不拆成端楼与六塔多份参考。',
  '保存边界20×20×41，长宽约2.05；中院长度大于端楼深度，低长墙和两端高屋面形成长向秩序。',
  '灰石塔身以短窗、垛口和木圈梁分层，端楼坡顶藏在方角塔之间；立面节奏来自房间和塔位而非贴满装饰。',
  '两端是深色长坡屋面，边塔是露天垛口平顶；y12剖面仍有端楼上室，不能将全部塔顶当成屋脊。',
  'cobblestone、stone、stone_bricks配grass_block，含dead_bubble_coral_block；分类灰色不意味着全为同一种石砖。',
  '底门y1及南端双门y3对应不同底层；y6边廊连接多座短塔，x3纵剖见z12梯井y6..9及z20梯井y6..11。y12端楼双门仍可辨；未把每个门当独立副本入口。',
  '两个terrain_small接口为底部承托，仍属于同一城堡；草院平底不是已验证的坡地适配，未拼接接口或启动地形生成。'],
 'F02': [
  '高矩形主堡旁接低围合入口附院；y12为主室及外挑通廊，y20收成单个上层主室，非单一空心塔壳。',
  '20×35×22，高度显著大于平面宽；底部附院压低入口，主堡屋盖形成一个集中重心。',
  '深石角柱、窄窗与木挑台形成竖横两种尺度；同层外廊并不等于另一个房屋设计。',
  '主堡尖坡顶及角部短尖饰围合一顶，上层x7/z7截面显示屋架与独立楼板；屋尖不能计作新楼层。',
  'cobbled_deepslate、deepslate_bricks、deepslate、smooth_basalt、deepslate_tiles构成深石壳，木层与玻璃窗为另一材料组。',
  '六个底门位于y2，另有y12与y20门；剖面见y11、19木楼板，水平图的阶梯簇位于主室内。无梯子不等于没有楼梯；尚未作真实台阶碰撞或逐层通关验证。',
  '一个terrain_small接口，没有外接房间池；低院与高堡在模板内完成，基座对山坡仍未验证。'],
 'F03': [
  '低矮主屋连两座短方塔，双梯井嵌在同一侧；y7房间和木构条带保持分区，形体不是另一高堡的缩放换色。',
  '23×17×23，宽高比约1.35，重心低；双塔高于主屋，但没有占满整个屋面。',
  '深浅石壳与木横带围小窗，塔口短垛与主屋木边分开；不能把树叶或泥裙当承重外墙。',
  '塔部短平顶垛口配主屋较低折坡顶；y13仅两塔及少量突件仍在，不是全平面三层大堡。',
  'smooth_basalt、mud、moss_block、cobbled_deepslate及大量spruce_trapdoor；苔泥层和主石壳材料不同。',
  'x8纵剖确有z6、z16两条y2..12梯井，穿过约y6、9楼板；底门在y1/2，上门y7。梯井支持上下联系意图，梯口落脚净空未以游戏验证。',
  '泥苔不规则底裙加terrain_small承托；边界内没有可证明的悬崖或天然洞口连接。'],
 'F04': [
  '主体偏东的高层主堡与西侧独立门塔、南侧小塔围合大院；中央剖面切中空院曾漏掉主室，x39与z35补剖才显示实际楼层。',
  '48×48×48是保存上限，主要高堡到约y42，宽院与偏侧高体形成非对称重心；不能将空院误作缺失建筑。',
  '方塔层层木石腰带、开窗和立柱分节，高主堡立面有多级外挑；门塔与主堡共享构造语言但占地和用途不同。',
  '主屋平顶、垛口及小塔帽组合，上部另有小室；高低屋顶关系清楚，不是三个同高方块叠加。',
  'smooth_stone_slab、smooth_stone、dripstone_block、rooted_dirt和light_gray_concrete_powder等混合；原始状态有77格lava，不能把橙色竖列都当箱子。',
  '东主堡底门(39,1,11)/(39,1,18)，院侧门(33,6,26)，西门塔门y8/20；补剖有多层地板及x32,z35的y27..29梯段。楼梯广布y1..34，屋顶装饰阶梯不可自动算路线。',
  'terrain_large底接口未展开；院内高差、门塔台脚和主堡承台属于模板内，不等于已连上自然山崖。'],
 'F05': [
  '三座不同直径圆塔通过高位桥相连；小侧塔先有独立底部，y20桥连向大圆塔，是完整塔堡组合而非三种圆塔组件。',
  '48³保存边界，圆塔大小和高度不一，桥宽明显小于塔径；塔间留空使组合有主次，不能按三次重复计数。',
  '圆壳用分层黑石、木圈梁与雪沿形成横带，弧面边界随高度收分，不是方墙简单涂白。',
  '三塔阶梯尖帽和雪覆宽檐；侧塔剖面出现木层和上方坡顶，雪沿不代表可用室内。',
  'smooth_basalt、deepslate_bricks、snow_block、snow及polished_blackstone_bricks为主，白色确有雪状态。',
  '底铁门(12,4,32)进入小塔；小塔高门(12,20,32)与大塔门(23,20,32)位于同一桥轴，z32剖面可见桥和两端门。x8,z32梯井y20..23上行；完整防御布局已见，未声称所有桥的游戏碰撞已验。',
  '雪裙与圆台在模板内，terrain_large为承托；未获得雪地实际生成或悬空桥端着地证据。'],
 'F06': [
  '一座高窄塔与两块低厅相接，底层房间紧密组合；高塔与矮厅通过侧门联系，非F02主堡加入口院的同平面变色。',
  '17×38×23，x11补剖可见尖饰达到约y37，实际房间集中下部和塔中部；尖饰长度不能折算成人可用净高。',
  '红褐砌体、木柱和横带混用，塔窗与矮厅窗口尺度不同；高塔一角突出形成方向性。',
  '高塔深色陡尖顶配低厅缓坡屋面，顶脊有细长装饰；屋顶形式区别于森林小礼拜堂的双山墙坡顶。',
  'spruce_trapdoor、mud_bricks、spruce_stairs、oak_wood和spruce_planks占主导；原图红褐不应误记成红砖。',
  '底门y1，上门y7/12；x11,z10梯段仅y1..3，不能把它写为通顶长梯。补图见矮厅y7及高塔y12分室，塔内阶梯仍需与装饰台阶区分。',
  'terrain_small的final_state为spruce_planks；不是泥土承托的默认实例，未验证实际地形接缝。'],
 'F07': [
  '围廊包空院，两个对角高楼与低角部体量围成一堡；y10为连续环院层，y20只保留两座分开的高楼。',
  '43×40×43宽基座，中院宽、外围廊低，高楼位于对角；高低屋面有均衡而非完全等高镜像。',
  '石墙木腰带、成排内院开口和角楼窗形成分层界面，苔屋面与墙边植被并非额外楼体。',
  '角楼大坡顶覆苔与灰石边，低屋顶围院连续，高层屋面只在两角；不能将一圈檐拆作四栋建筑。',
  'stone_bricks、spruce_trapdoor、moss_block、oak_planks、stone配多种叶与泥；苔绿不是现成贴图观感。',
  '主双门(13/14,2,25)，上层门集中y10以及y18/20；y10平面和z32剖面确认上层围廊与侧房关系，y20两楼要经下层联系，不能在院上凭空假定一座高桥。',
  '宽草泥台裙和terrain_large承托；植物遮挡真实台脚，未证明适用于天然悬崖。'],
 'F08': [
  '两座并排高厅/塔体用中段交通相接，主厅更高、更长；y17两门相对，通过同层中部地板联系。',
  '30×47×17长窄占地，高主屋及极细尖饰决定高度；主副屋高差明显，不能按47格都作功能层。',
  '石柱与木腰带夹高窄窗，warped门窗件形成细部差异；同一长立面先用体量分段再用材质。',
  '主屋高坡顶与副屋较低坡顶并排，脊顶尖饰有高度差；无大庭院或多座独立神殿。',
  'polished_andesite、dark_oak_planks、andesite、gravel、warped_trapdoor为主；名称wither不证明是凋灵Boss场地。',
  '底层warped门多在y1，连接门在(8,17,8)/(16,17,8)，z8剖面见双门同层及下方中央楼梯状构造；楼层约0/6/12/16/23。无梯状态，不把外檐台阶自动当楼梯。',
  'terrain_small底承托final_state为polished_andesite，底脚贴合未知；不是已验证跨峡谷楼。'],
 'F09': [
  '宽平台上围廊式厅楼，中央小上阁叠于大下层，台阶与柱廊属于同一整栋道场，不拆屋顶计多例。',
  '35×40×29，低层宽、上阁窄，檐口逐级收分；最高脊饰到约y37，主体可用空间远低于保存上限。',
  '石台、木柱与出檐逐层分开，底层内隔间和外周通廊并存；柱距支持廊道而非仅墙面装饰。',
  '两级主要坡檐加高脊，黑色屋面与木檐托出；y17上阁平面仅中央一块，不将四角檐计作四阁。',
  'dark_oak_planks、blackstone、spruce_trapdoor、stripped_spruce_wood和spruce_stairs；台脚多灰石，屋面非全木。',
  '三门均在y3，y11可见下层两处分区及围廊，y17见上阁，剖面有多级地板与阶梯状部件；无ladder。可研究单栋厅楼分层，但不是三岛之间的完整路径。',
  '台阶从石基多侧伸出，terrain_large承托；未证明崖边栈道或浮岛地形。'],
 'F10': [
  '中央小厅与两端细塔构成一栋宗教建筑，两塔平面落在同一长轴；布局完整，但题材及用途不足以直接作为阴城、墓园或崖寺的相近实例。',
  '17×26×26，塔高于中央屋盖，主体厅较小；两塔不等于两座不同设计。',
  '浅砂石、木带与小窗分节，中央厅侧入口与轴端塔门区别明显。',
  '中央折坡小顶、两端尖帽，细塔高低分层；不是中式千佛崖塔或大雄宝殿范式。',
  'sand、birch_planks、brown_mushroom_block、spruce_stairs和sandstone混合；不能按分类色将全部褐块记成木。',
  '侧厅门(3,1,12)/(13,1,12)，塔门(8,1,6)/(8,1,18)；两条连续梯(x8,z4/20,y1..14)通上平台。交通意图比仅凭高塔外观更明确，但相关性不足仍不计数。',
  '砂地底座，无jigsaw；并未核实沙漠生成或砂块承托更新效果。'],
 'F11': [
  '45×45平面均匀柱网围连续低厅，开放边界与横纵通道交错；一座水厅不能按64柱或9条水柱计成多栋建筑。',
  '45×11×45，极宽低，主要净空在y2..9；与多层帝陵或细高舍利塔比例不同。',
  '外围以柱和栏杆形成开放重复界面，没有高大封闭正立面；柱距构成室内方向节奏。',
  '单层平厚顶有规律小孔，水柱由顶到底；没有完整多重坡屋面或塔冠。',
  'stone_bricks、cracked_stone_bricks、moss_block、mossy_cobblestone及1525格water，含chain和soul_lantern。',
  'x10/z10剖面确认y1浅水与y1..10水柱，y2平面为柱间网状空隙；无门、无梯，不用水柱自动推断可游到外部安全出口。仅作水下柱厅局部原则。',
  '无拼接接口，底面为平底承托；埋地高度、外界水位及出入口切口没有生成证据。'],
 'F12': [
  '三层方形地下迷宫托上部阶梯金字塔与顶冠，y2/y8/y14的平面均有不同走廊分隔；不是单座实心金字塔，也不能按三层计三例。',
  '48³，地下主体约y0..19，上部大收分体约y20..35，顶冠至y47；高度分配中功能走廊只占下半。',
  '下层连续深石墙、上层对称退台，顶冠与主台之间是离轴支撑，中心截面留空不等于顶冠完全悬浮。',
  '阶梯收分顶与方形顶冠组合，不是中式陵墓覆土或木坡屋面，能学层级不能照搬题材。',
  'sculk、smooth_basalt、reinforced_deepslate、polished_basalt、deepslate_tiles；含7TNT和410sculk_sensor。',
  'z1补剖确有角部阶梯由底部上行；中心多层也有楼梯状连接。无门无梯，现有平面未锁定可靠外部入口与全部楼层回程，保留待核，不能把箱位当入口或通关证据。',
  '无jigsaw；下层外壳完整但实际埋深与外侧接地未核，生成规则尚未作为正式入场证据。'],
 'F13': [
  '阶梯砂岩金字塔包下部低腔及上层多室，四角外部立件属同一祭祀墓体；y8有八扇内部门围四周分室。',
  '40×24×43，低宽塔体，内腔主要在y1..14，顶部另有小空间；不是沈沙三层天井、九玄室与圆棺台完整同构。',
  '砂岩连续退台配蓝色陶瓦强调方位，外立面少窗；不能凭塔外轮廓认定可入内。',
  '连续阶梯形金字塔屋盖，小顶腔位于收分尽端；四角立件不是四座建筑。',
  'sandstone、sand、chiseled_sandstone、sandstone_stairs、blue_terracotta，含9TNT与陷阱箱。',
  '八个y8门均在内部，不是八个外部入口；x20剖面见z32梯y3..7及z10梯y4..6连接下腔/上室。外部入口位置及下层回程未完全确定，保留墓体候选而不计完整路线信用。',
  '无房间接口，模板自含墓体；沙丘埋藏、入口露出高度及陷沙更新未核。'],
 'F14': [
  '四向台阶包阶梯神庙，内部分上下几处洞室和中隔，中心有熔岩；外部礼台与内部机关房不能拆成不同完整建筑。',
  '31×15×31，低矮宽台，顶上细突件对比例影响小；不属于高层吊脚楼或大型婚堂。',
  '灰石退台和草苔边点分层，四面主要靠阶梯变化而非窗带形成正面。',
  '截顶台与四向台阶形成连续屋盖，上方短柱不构成可用独立阁楼。',
  'stone、stone_bricks、cobblestone、grass_block配bone_block与sticky_piston；原始状态确有126格lava，无chest，橙色不能误记成宝箱。',
  'y4洞室南北分布，y7出现较大上室；中心剖面见y2..3及y9熔岩，不证明安全穿越。7个jigsaw全是husk/skeleton实体池，不是7个缺失房间；入口安全路径保留待核。',
  '草泥裙与台阶在本体，无地基池；没有雨林树根、苗窟水位或天然钟乳桥的完整证据。'],
 'F15': [
  '低层多室环廊围中央分区，带农地、储物和居住功能；一侧细竖塔与地下面网相接。完整低层布局不等于地上完整城市群。',
  '48×44×48保存边界被x42..47/z29..34的细塔拉高，主体房网到约y5；不能以44格称多层全城。',
  '地下外围低墙与少量门口，竖塔外壳几乎无窗；外立面不足以推断塔内楼层。',
  '房网平顶有数个缺口，竖塔是高空心井加顶部小帽；不是宽街上多栋完整有顶住宅。',
  'stone_bricks占6044格，另有farmland/wheat、iron_bars、水及功能块；并非整座淹水城市，water只有44格。',
  'y1..4平面有连续环巷和内部分区，外围五条y1..4短梯连接低顶；x45/z31补剖显示长塔井无连续ladder，仅部分横梁。不能虚报可从主房网登到塔顶的路线。11接口为实体。',
  '原始模板没有地形接口，裂化苔化处理器只改变方块效果；不证明生成后的下沉、埋藏或安全入场位置。'],
 'F16': [
  '低层围墙院内接前后不等高双塔与主屋，y6围墙步道绕院，y22仅双塔占地仍在；是一个完整小型院堡。',
  '25×43×30，双塔细、院低；保存高度含尖帽上方细件，不能用全高推算各层人数容量。',
  '石柱、木腰带与小窗形成横向环带，院墙上口连续，双塔位置不对称；不同于上一批单偏主塔围小院。',
  '两塔各有木石尖帽，低主屋坡顶及院墙平顶形成三种屋面层级；塔帽不单独计设计。',
  'stone、stone_bricks、spruce_stairs、grass_block、spruce_planks构成石木堡；含少量lava/TNT不能忽略真实碰撞与危险差异。',
  '底层门y1接院内房，y6门接墙廊；(16,5)梯y10..21与(6,26)梯y11..26可从补剖确认。12个接口为村民/马，非外接房间。墙廊与双塔上下交通意图充分，未宣称游戏通关验收。',
  '草泥底与院墙脚完整保存，没有房间地基拼接；真实地形高差仍须后续验证。'],
}

FAMILY = {
 'F01': '长院两端厅楼，不是旧catalonian_castle的偏侧厚主堡加短前院。',
 'F02': '矩形高堡加低附院；旧dark_tower为近圆鼓形平顶，F06为窄高塔接矮厅，都非同壳换材。',
 'F03': '双短塔加低厅及双长梯；已重看rotting_temple，其多级方台中心高台与此双塔围房不同。',
 'F04': '偏侧高方堡、独立门塔与宽院；旧ancient_temple为中央台塔加对称整方多层，非同设计。',
 'F05': '三个异径雪覆圆塔和高桥；旧ruined_castle为密集方塔残墙和单外桥，非同壳破损版。',
 'F06': '窄尖塔与低厅簇；重看forest_chapel为两块相连山墙厅，平面、主塔和屋顶组织不同。',
 'F07': '空院环廊加两座对角高楼；旧ruined_castle中心密室多塔，旧villager_castle为宽墙院加一侧高坡主厅。',
 'F08': '长窄双高厅同层连接；旧catalonian_castle偏侧主堡+前院，与之无同一院落/主体拓扑。',
 'F09': '上下叠置围廊式道场；旧TREK castle为院墙围单偏塔，不是同一设计。',
 'F10': '轴上双细塔夹小厅，非desert chapel单宽塔式礼拜堂；相关性不足仍排除。',
 'F11': '单层水柱网大厅，非ancient_temple中台塔与多层分室；柱格重复不是独立建筑。',
 'F12': '三层迷宫加阶梯金字塔，重看the_mausoleum为高方楼层环圈及中心开敞空间，非同一换色。',
 'F13': '低宽金字塔与上下腔室；与旧ruined_castle即使占用相似度最高，语义及分室组织仍不同，未据相似度自动判新。',
 'F14': '四向台阶祭台及熔岩内室，非fortified church的独塔礼拜厅。',
 'F15': '低层环巷房网加单细竖井；sinking_temple是祭祀厅房布局，名称相近不合并，亦不据城市名加分。',
 'F16': '细双塔围院与低墙廊；旧castle单偏高主塔加门楼，旧villager_castle是宽大围城与单侧高厅。',
}

STRONG = {'F01', 'F02', 'F03', 'F04', 'F05', 'F06', 'F07', 'F08', 'F16'}
SUBSPACE = {'F09', 'F11', 'F15'}
COMPARISON_VIEWS = [
 'continuation-20261022/references/whole-candidates-002/B003.png',
 'continuation-20261022/references/whole-candidates-002/B006.png',
 'continuation-20261022/references/whole-candidates-002/B001.png',
 'continuation-20261022/references/whole-candidates/W028.png',
 'research-20261101-dungeons-001/F01-whole.png',
 'research-20261101-dungeons-001/F02-whole.png',
 'research-20261101-dungeons-001/F07-whole.png',
 'research-20261101-dungeons-001/F08-whole.png',
]


def evidence(path):
 return dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def main():
 source = json.loads((OUT / 'sources.json').read_text())
 entries = []
 for c in source['candidates']:
  ident = c['id']; assert len(NOTES[ident]) == 7
  status = 'WHOLE_FORTIFICATION_RESEARCH_PROPOSAL' if ident in STRONG else 'WHOLE_LAYOUT_SUBSPACE_STUDY_ONLY' if ident in SUBSPACE else 'HELD_ENTRANCE_OR_RELEVANCE'
  entries.append(dict(id=ident, member=c['member'], nbt_sha256=c['nbt_sha256'],
   observations=dict(zip(FIELDS, NOTES[ident])), independent_design_basis=FAMILY[ident],
   images_actually_viewed=[evidence(OUT / f) for f in c['images'] + [ident + '-details.png']],
   completeness_and_relevance=status,
   proposed_target='DUN03 万骨枯寂·血海古战场：完整城防建筑的院落、门塔、堡体与城墙廊组织参考' if ident in STRONG else {
    'F09': 'DUN04寺院厅楼/DUN07单阁的分层局部原则；不代表崖寺或三岛整体',
    'F10': '无足够具体相近用途，不计数',
    'F11': 'DUN05地下水厅/DUN08底潭柱厅局部空间原则，不覆盖城池或冰窟整体',
    'F12': 'DUN01多层迷宫与上部礼台候选，入口、回程待核',
    'F13': 'DUN01墓体候选，外部入口与下腔回程待核',
    'F14': 'DUN06祭祀机关房局部原则，安全入口待核',
    'F15': 'DUN05街巷房网局部原则，竖井交通缺证，不当完整枉死城设计',
   }.get(ident),
   credit_proposal=1 if ident in STRONG else 0, formal_credit_added=0,
   route_evidence_standard='Studied original stored layout and connectors; not a native collision/playthrough certificate. Known route gaps remain explicit.'))
 review = dict(date='2026-11-01',
  method='Manual visual study of 64 newly generated whole/plan/vertical/detail sheets plus re-view of 8 historical comparison sheets; original NBT states cross-checked.',
  counts=dict(templates_studied=16, new_images_actually_viewed=64, historical_comparison_images_reviewed_again=8,
   whole_fortification_proposals=9, whole_layout_subspace_only=3, held=4, formal_credit_added=0),
  entries=entries, historical_comparison_views=[evidence(OUT.parent / p) for p in COMPARISON_VIEWS],
  proposal_boundary='9 proposals are complete defensive-building references for DUN03 only. They are not 9 implemented buildings, not 9 whole battlefields, and not additions to the COD4 mortuary 148 or COD6 0. A new target ledger must retain its own denominator and source identities.',
  principles=[
   '长院、环院、并排高厅和圆塔桥堡有不同的进入顺序；先借鉴空间关系，不能只搬石木配色。',
   '偏置主堡用偏轴剖面研究；中央剖面落在空院时，不能直接判整栋无室或无梯。',
   '高位桥用两端门位、桥层与地板共同确认，不用单张外观猜连接。',
   '保存高度含屋尖、竖井及散块；可用楼层要从平面和地板净空另读。',
   '火、浅水、粉雪、活板门、阶梯和栏杆不能用通用整方块色图推断安全碰撞。',
   '底部terrain接口和实体接口分别记录；有接口不自动缺房间，无接口不自动可安全生成。',
   '完整实例仍是一栋或一个院堡；分室、楼层、重复柱、不同视图及同设计旋转不增加参考数。',
  ], formal_registry_modified=False, new_architecture_started=False)
 (OUT / 'manual-review.json').write_text(json.dumps(review, ensure_ascii=False, indent=2) + '\n')
 print('Recorded 16 seven-aspect reviews and 9 narrowly scoped research proposals; formal credit remains unchanged.')


if __name__ == '__main__': main()
