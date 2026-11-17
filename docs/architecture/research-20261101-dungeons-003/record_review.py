#!/usr/bin/env python3
"""Record observations after actual manual study; never award registry credit."""
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
FIELDS = ['layout', 'proportion', 'facade', 'roof', 'materials', 'circulation', 'terrain']
NOTES = {
 'F01': [
  '两座高方塔夹低横向连接体，底层两侧分室与中央通道构成完整哨站；两塔属于同一建筑，不拆为两例。',
  '保存边界48³，主体在约z12..36内横向展开，高塔和低连接体形成明确高差；保存方盒不是整栋实心体量。',
  '浅砂岩墙以窄缝、木横带和外伸扶壁分节；底部柱墩与上层墙带有不同尺度。',
  '两塔为收进的垛口平顶，连接体较低；不是两座坡顶塔或中式楼阁。',
  'smooth_sandstone、sandstone、cut_sandstone、sand、purple_glazed_terracotta和sandstone_wall混用，颜色分类不等于原贴图。',
  '底门七处y1、上门两处y8；x11补剖见y15..24阶梯状上行，z24剖面见约6/14/21/28/35层板，顶层短梯y29..31。有空间联系意图，未认证原生碰撞与通顶通关。',
  '宽砂岩承台配terrain_large接口，模板中无待接侧房；承台如何落到自然沙坡仍未验证。'],
 'F02': [
  '高主厅、交叉侧翼与一座高尖塔构成连体厅堂；名称stronghold不能证明其为军堡，不按城防整例计入。',
  '48³边界，主屋盖约y33、尖塔至46；主厅高空腔明显，尖饰高度不等于可用楼层。',
  '灰石竖向肋柱与高窄窗强调厅堂高度，侧翼较低；与旧fortified_temple的宽厚分层台楼不同。',
  '深色陡山墙屋顶配高尖塔，侧翼坡顶分叉；不是旧寺堡多级平檐的材质变体。',
  'stone、andesite、stone_bricks、polished_andesite、moss_block及dead_fire_coral_block为主。',
  '门分y1与y10两组，x20剖面见约y9/17层及高厅，z22剖面见侧室层板；无梯子状态。楼梯状部件需区分屋面，不能凭名称宣称堡内完整战斗路线。',
  '不规则苔草台裙和terrain_large底接口；未证明为地下判官内衙或悬崖宗教建筑，只研究高厅与侧翼层次。'],
 'F03': [
  '苔石洞景中嵌下部小室、上部小房及水池、木连接构件；整组洞景不是多座完整吊脚楼。',
  '48³，高差跨底部y2小室到y39上房，细柱与藤蔓遮挡主体；自然竖柱不等于建筑承重层。',
  '苔石、藤蔓、瀑水和木构共同形成界面，不能将绿色均记为树叶或认定均可攀爬。',
  '顶部有小房屋盖及宽帽状体，非连续大型宫殿屋面；屋盖下是否有可达平台要单独核实。',
  'moss_block、mossy_cobblestone、tuff、vine、mossy_stone_bricks和stone为主，洞壁与植物不能混同木构。',
  '底门(5,2,36)，上部双门(32,39,35/36)；x32/z36补剖能定位两端房间。x43,z43的y23..38范围仅九格梯状态，有断段，不能宣称底部通上房。',
  'terrain_large承托，未拼地形；DUN06雨林洞窟层级有局部相关性，但连续路线与完整聚居建筑未确认，暂不提出计数。'],
 'F04': [
  '数座低矮小屋与中央开放厅廊围水渠、草地，整个聚落只能按一个整体候选研究，不能按屋顶数拆多例。',
  '48×17×48，主要房门y3，屋顶约y9..12，地面低层关系为主；不属于多层深坑悬崖吊脚寨。',
  '木柱、短墙与小窗围出室内，外围密集细竖杆实际多为竹，不能误称石柱列阵。',
  '多座短坡屋顶围低开厅，坡檐与中央廊顶高低相近；竹梢不是尖塔。',
  'dirt、grass_block、bamboo、grass、tall_grass及spruce_trapdoor为主；1146格bamboo是外景，不应算建筑体积。',
  '底门分布于各小屋y3，东屋另有y7门；北屋梯段y3..5。小巷由屋间空地联系，尚无地下三层飞索或吊桥路线证据。',
  'terrain接口配平缓草泥、水渠；只借鉴DUN06小屋与公共厅的组织，不把地面寨换名视为完整苗窟。'],
 'F05': [
  'L形低厅与单角高木塔相连，低层围出局部空地；不同于旧TREK castle的厚石周墙和多角塔院。',
  '27×45×35，高塔尖到约y44、塔室主要y21..31，低厅约y6..13；以高角塔控制方向而非等高对称四塔。',
  '木柱横带、深灰石边和覆绿层共同分节，塔下长柱与低厅门窗尺度不同，藤叶不替代柱脚。',
  '角塔陡尖顶及低厅坡顶相接，屋尖细长；y23平面仍是单个塔室，不能将屋尖再计一层房。',
  'oak_leaves、spruce_trapdoor、stripped_spruce_wood、grass_block、spruce_stairs和mangrove_wood混用。',
  '门在y1、6、11；x20/z10补剖见y21及y28塔内层板，x20,z10有y22..28连续梯。另一梯x11,z6仅y9..12，底门至高塔完整路线尚非游戏验收。',
  '高低台脚在模板内，terrain_large负责外部承托；可学哨塔与厅的分工，不认定已适配真实森林坡地。'],
 'F06': [
  '宽水池/庭院占一侧，多层连体厅房集中另一侧，池边柱廊与上层房间相接；steam名称不能证明机械工厂。',
  '48³，厅房主要在y7以上，右侧高屋盖约y38，池底接近y0；高低层之间有厚基座，而不是整栋漂浮。',
  '石基上木柱和成排门窗分层，上室开门密集但不代表每门一栋；池边开廊比上层封闭室更通透。',
  '多级坡檐与高脊聚在厅房一侧，宽院无整体屋盖；不是齿轮、锅炉或起重吊架造型。',
  'andesite、stone、water、spruce_trapdoor、stone_bricks和oak_log为主，有1762格水；未以名称猜浴场或蒸汽机械运行功能。',
  'y14/21补平面显示池旁通廊和多室，x39剖面见y14/20/24房层，z17剖面见底部池与高厅。仅x2,z1有y1..8梯，不能视为整个多层系统的通顶梯。',
  '水池嵌宽基座，terrain_large待接；只研究水院与厅房分层，不计入DUN02机械城完整工坊。'],
 'F07': [
  '紧凑低储屋连一侧较高小体量，房间与梯井共占16×12平面；整体一栋，箱子数不增加建筑数。',
  '16×12×12，主要地面门y1，低屋檐约y5..7，较高体量到11；适合小储屋而非巨兵收纳库。',
  '木柱、木墙与灰石/泥砖边框有明确横竖节奏，低侧门与梯井侧墙互相避让。',
  '低屋折坡边配一角高平框/短顶，不能将上层木框当另一完整仓库。',
  'spruce_planks、stripped_spruce_wood、spruce_trapdoor、mud_brick_stairs、spruce_slab及spruce_stairs为主。',
  '九扇门下半都在y1，x10,z5梯y1..4；y3补平面保留室内分隔，y5已切入屋顶。可以学小储屋内部出入，但未证实大型工场跨层货流。',
  'terrain_small承托，无侧房池；只限DUN02储存附房局部原则，不能替代机械城巨兵库。'],
 'F08': [
  '露天阶梯采石坑内有木提升架、平台和小作业构件；四侧连接stoneworks池，主坑模板不足以代表完整工场。',
  '48×26×48，坑底至坑缘约数格，高吊架显著突出；没有四层机械城深坑的完整竖向组织。',
  '阶梯石壁、木支架和堆料形成作业界面，孤立石块不是室内隔墙。',
  '主体露天，仅有小构件局部遮盖；不可把吊架横梁写成连续厂房屋顶。',
  'dirt、grass_block、dead_tube_coral_block、gravel、andesite与stone为主；缺少足以证明黄铜机械动力的材料或运行证据。',
  'x13,z14梯y4..11，x16,z27梯y2..5，另有三格孤立梯；补剖看到坑缘高差和提升架，但四个外接作业区尚未拼成可研究整体。',
  '五个接口中一个terrain，另四个stoneworks。实际外接池含11种构件，前六terrain_matching、后五rigid；fallback回自身，拼接位置、终止和道路都待核，不把11构件算11栋。'],
 'F09': [
  '完整小型方围院，四角哨棚、低石围墙和一侧入口围空院；与旧stray_ruins的破墙残台不同。',
  '16×8×16，开院大于角棚，围墙低于棚顶；这是小哨堡尺度，不夸大为整座战场。',
  '低石墙提供连续边界，木柱支角棚，入口不装门扇；不是只换色的桦木树台或冰柱。',
  '四角短平棚罩院角而院心敞开，55格campfire参与构成棚顶；通用灰色不意味着混凝土整板。',
  'stone_bricks、dirt、mossy_stone_bricks、grass_block、campfire和spruce_fence构成石木围院。',
  '无门扇、无梯；z8剖面可见入口侧低开口，y3补平面显示四边围墙和空院。无高层交通需求，不能因无梯判整堡残缺；真实棚顶碰撞未验。',
  '四个接口均为实体池（三掠夺者、一村民），不缺四个房间；草泥低基座着地仍待实际生成验证。'],
 'F10': [
  '树干式中央支柱托上部小屋，三处分散叶盖与地面绿化围绕；非F09四角棚加石围墙的材质变体。',
  '16×19×15，主屋较小、支柱细长，屋盖高于周边叶棚；不是可容大群战斗的城堡。',
  '白桦柱与白色小屋墙间有开口，灰石边框约束小室，底部没有完整高城墙。',
  '上屋叶冠和三处低叶盖，绿色确含birch_leaves；不是中式瓦顶或四角平棚。',
  'birch_leaves、grass_block、birch_log、grass、stone_bricks和birch_trapdoor为主。',
  'x8,z8梯y3..9连续，另x10,z8仅y1单格；补剖见上室与树干交通意图，未证低阶到梯脚的原生碰撞。没有门扇不等于无室。',
  '两个接口是horse和villager实体池，不是建筑拼接。仅作DUN06架高小屋构造局部研究，不能因名字fort归入城防计数。'],
 'F11': [
  '低矮破冰围边与细冰柱顶小室组成场景，不是完整多房宫殿；与F09围院、F10树台平面均不同。',
  '18×29×20，高冰柱仅数格宽，顶室很小；高度来自细柱，不能据29格高称大型冰宫。',
  '蓝冰/浮冰柱与积雪低墙形成竖向界面，围边多缺口，缺少可证明完整居住/防守功能的室墙。',
  '顶端冰帽收成小冠，下方非连续坡屋面；无大型骨船厅或水宫屋盖。',
  'packed_ice、snow_block、blue_ice、ladder、ice为主，冰材不能推断水下宫殿。',
  'x7,z11梯从y2到25范围仅17格，y7、10、14、20等高度有断段；11接口为stray/polar_bear实体。图中洋红格不是实际门。未证明安全连续登顶，不提出整建筑计数。',
  '雪基座与低冰片没有生成地形证据；仅保留DUN08冰材与竖向构件的待核研究，不代替冰窟完整路径。'],
 'F12': [
  '中央高厅连两侧低翼与外廊，整个多翼府邸是一项设计，不按三块屋顶或45实体接口拆数。',
  '33×37×42，厅高、翼低，底层与两侧次厅比例明确；保存37格含高脊，不是37格净高审判厅。',
  '石基、木框和连续廊口形成多层节奏，上层小室与下层开厅区别明显；不能凭名称认定中式官署。',
  '中央陡山墙高屋顶配前后低翼坡檐，x14补剖能见两翼低脊和中厅高脊；不是单顶大方盒。',
  'spruce_planks、spruce_trapdoor、dark_oak_planks、dark_oak_slab、farmland及wheat为主，农田属外围环境。',
  '实际门仅(22,5,20)、(21,12,20)，其余通廊多用开口；两侧梯x14,z14/26在y1..11，中央x6,z20在y11..22，剖面约有多级层板。45接口全为实体，不代表缺45间房；尚未核实判官殿双柱阵列与返殿后捷径。',
  '宽田地和台脚配独立整栋模板，未证实际地下埋深；只借鉴DUN05厅翼与廊的局部组织，不当完整枉死城或已验收内衙。'],
}
PROPOSE = {'F01', 'F05', 'F09'}
HELD = {'F03', 'F08', 'F11'}
TARGETS = {
 'F01':'DUN03 万骨枯寂·血海古战场：双塔哨站的分区与低连接体',
 'F05':'DUN03 万骨枯寂·血海古战场：高角塔与L形低厅的哨站组织',
 'F09':'DUN03 万骨枯寂·血海古战场：小型四角哨棚围院与入口组织',
 'F02':'DUN04/DUN05高厅、侧翼的局部层次；非军堡或完整寺院、城池',
 'F03':'DUN06雨林洞景及高低小室；路线缺证',
 'F04':'DUN06公共厅与低屋组织；非地下吊脚寨',
 'F06':'DUN05水院厅房的局部分层；非DUN02动力工厂',
 'F07':'DUN02小储屋内部出入；非巨兵收纳库',
 'F08':'DUN02采石坑及提升架；外接工区未形成整体',
 'F10':'DUN06架高小屋局部构造；非城防完整实例',
 'F11':'DUN08冰构件待核；非完整冰窟、水宫',
 'F12':'DUN05府邸厅翼廊局部；非判官殿及地下城整例',
}
COMPARISONS = [
 'research-20261101-dungeons-001/F06-whole.png',
 'research-20261101-dungeons-001/F06-plan.png',
 'continuation-20261022/references/whole-candidates-002/B002.png',
 'research-20261101-dungeons-001/F07-plan.png',
]

def evidence(p):
 return dict(path=str(p), sha256=hashlib.sha256(p.read_bytes()).hexdigest())

def main():
 s=json.loads((OUT/'sources.json').read_text()); entries=[]
 for c in s['candidates']:
  ident=c['id']; assert len(NOTES[ident])==7
  entries.append(dict(id=ident, member=c['member'], nbt_sha256=c['nbt_sha256'],
   observations=dict(zip(FIELDS,NOTES[ident])), proposed_target=TARGETS[ident],
   independent_design_basis=NOTES[ident][0]+' '+NOTES[ident][3],
   images_actually_viewed=[evidence(OUT/f) for f in c['images']+[ident+'-details.png']],
   status='SCOPED_COMPLETE_FORTIFICATION_PROPOSAL' if ident in PROPOSE else 'HELD_COMPLETENESS_OR_ROUTE' if ident in HELD else 'SUBSPACE_PRINCIPLES_ONLY',
   credit_proposal=int(ident in PROPOSE), formal_credit_added=0,
   native_acceptance=False))
 review=dict(date='2026-11-01', entries=entries,
  method='Actual manual study of 48 new whole/plan/vertical/detail images and four historical comparison images; original NBT states and outgoing interfaces cross-checked.',
  historical_comparison_views=[evidence(OUT.parent/f) for f in COMPARISONS],
  counts=dict(templates_studied=12,new_images_actually_viewed=48,historical_images_reviewed_again=4,scoped_proposals=3,subspace_only=6,held=3,formal_credit_added=0),
  principles=[
   '哨站、围院、树台、冰柱依空间组织和功能区分，不按文件名中的fort归为一类，也不按材质换色增加计数。',
   '高塔配低厅的比例来自实际房间和楼层，不能拿尖饰高度当净高；偏置塔必须偏轴补剖。',
   '水池、开廊、储屋和提升架可提供不同局部原则，单一元素不足以代表完整机械城或阴司城。',
   '外接建筑池、地形池与实体池分别记录；四个拼接点不是四个已完成工区，45实体点也不是缺45间房。',
   '长梯按实际逐格状态核实连续性；跨多层但有断段时，不宣称可安全通顶。',
   '竹、藤、营火、台阶与活板门保留原状态含义；分类整方块图不能替代原生材质、碰撞或地形验收。',
   '每个连体建筑或完整小围院最多是一例；分层、屋顶、截图与组件不能额外计数。'],
  proposal_boundary='Three complete defensive-building studies only; not three implemented buildings or whole battlefields. No additions to COD4 mortuary 148 or COD6 0; 1000 requirement remains unmet.')
 (OUT/'manual-review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
 print('Recorded 12 seven-aspect reviews; 3 scoped proposals, 6 subspace studies, 3 held; zero formal credit.')

if __name__=='__main__': main()
