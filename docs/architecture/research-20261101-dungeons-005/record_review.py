#!/usr/bin/env python3
"""Record actual eight-source visual study, explicitly excluding cottage variants."""
import hashlib
import json
from pathlib import Path

OUT=Path(__file__).resolve().parent
FIELDS=['layout','proportion','facade','roof','materials','circulation','terrain']
NOTES={
 'F01':[
  '花园内偏中部为多室、错层的L/T形住宅，周围水池、路径与植被属于同一宅地；全院一项设计，不按房间或花园拆数。',
  '36×26×44保存边界，实际最高y24；房体只占宅地一部分，屋脊、烟囱和花园范围不能等同可用居室面积。',
  '木框浅墙、分层小窗与侧向门口区分不同房间，附廊较低；密集植被不构成新增建筑翼。',
  '主屋交叉高坡顶连较低侧屋顶，砖烟囱穿脊；不同屋盖对应房间转折，不是F02单长脊小屋的换色。',
  'dirt1139、grass_block829、stripped_spruce_log416、smooth_sandstone189、dark_oak_stairs181等；灰色分类屋盖含木台阶，不能写成全石顶。',
  '底门y2，中层门y7，上门y12；x14,z13梯y2..5及x20,z16梯y7..10连续，补剖可定位两段与层板，但未原生认证梯口净空和全屋通路。',
  '完整花园地块含水池和小径；五个外接点均为平原村民实体池，不是五个待拼房间。只提案街区带院民居，不替代整城或官衙。'],
 'F02':[
  '紧凑矩形单主室加屋顶下阁层，一侧有烟囱；与F03旋转、覆雪版本归一个设计家族，本例为代表，家族最多一例。',
  '12×12×10，主室低、阁层窄，上部坡屋面与烟囱占高；不能称十二格净高或多层大型住宅。',
  '木墙、原木框与侧窗围单室，单入口和短攀梯分侧；藤叶是外景，不当厚墙或第二层外廊。',
  '长双坡屋盖带四臂式烟囱帽，与F03方向改变后相同的屋面和烟囱组织相对应；不按旋转增加实例。',
  'dark_oak_stairs106、spruce_log56、spruce_planks135、dark_oak_planks31；和F03数量相近只作辅助，布局与剖面对照才是家族判断主体。',
  '门(3,2,4)，x9,z4梯y2..5连续；补剖见约y6阁层板及其上窄腔，入口至阁层组织明确，未运行碰撞验证。',
  '小型地面基裙，唯一外接点是针叶林村民实体池；只作单室带阁层小宅参考，不计为军堡、寺庙或大院。'],
 'F03':[
  '与F02相同的单主室、短梯阁层及侧烟囱，旋转后改雪地、门窗与入口局部；不提出第二独立设计。',
  '10×12×12与F02的12×12×10互换水平边长；相同屋层和烟囱高度，覆雪与门廊不构成独立用途或规模。',
  '木窗框、同样的长侧墙及小入口雨篷；窗和门位置的局部变化不足以另算一座独立建筑参考。',
  '同长双坡顶、同阁层与四臂烟囱，雪层覆盖改变外观而不改变主要屋盖空间组织。',
  'dark_oak_stairs106、spruce_log56与F02相同，spruce_planks136、dark_oak_planks30及snow46不同；原文哈希不同不代表独立设计。',
  '门(5,2,8)，x5,z2梯y2..5连续，y6阁层板与F02对应；旋转位置不同不增加路径或楼层数。',
  '雪地底裙及雪地村民实体池，缺少房间拼接池；仅研究积雪与门廊变化，独立参考提案数和正式信用均为零。'],
 'F04':[
  '细长宅地一端为小屋，另一端为池塘、石框和花园，沿园路联系；全宅地一个候选，池塘和屋子不能拆两例。',
  '18×15×28保存边界，房体仅占一端；高烟囱与花园框架抬高边界，不能称高塔住宅或大礼厅。',
  '小型木框低墙、短窗与园侧入口；池边石竖框是花园构件，不误认完整第二座石屋。',
  '单座小双坡屋盖被高烟囱穿过，花园没有与房体同量级的屋盖；不能按烟囱高度增层。',
  'dirt413、grass_block232、spruce_stairs65、water60、coarse_dirt58、oak_leaves50与polished_diorite44；池水与白石框分别记录。',
  '底门(5,2,10)，x8,z11梯y2..4连续；x8剖面区分短屋身和高烟囱，短梯不等于通到烟囱顶。未认证池边与阁层净空。',
  '土草完整宅地内有池塘和园路，仅一个平原村民实体接口；提案小型水院民居的宅地组织，不当忘川河、水泵或地下水关。'],
 'F05':[
  '石脚抬起的两段小厅连接偏置细高塔，底部留空；整组一座房屋，塔室和小厅不拆参考。',
  '19×38×24，高主要来自细塔和尖顶，主屋楼板抬离地面；不是三十八格高的大面积多层宅院。',
  '石脚、深木框与玻璃围高低房间，塔窗显著高于主厅；空中零散灰块未作为可站平台或新房间。',
  '低厅多条短坡脊，高塔尖帽分段收进；烟囱旁离散块不当额外可通建筑。',
  'stone_bricks470、dark_oak_planks397、dark_oak_stairs171、dark_oak_log168、spruce_stairs157等，石脚和木屋分别承担不同视觉比例。',
  '门(13,5,8)，x3,z20梯y7..24连续；补剖见约y6、16、24层次，但地面到抬高主入口、主厅到塔脚的连续路线未锁定，保留待核。',
  '本体有高脚而非完整悬崖地形，单个针叶林村民池不补入口道路；不能直接算DUN06吊脚寨或DUN03军堡。'],
 'F06':[
  '错位双翼近L形连接，中段转折处设置入口和短门廊，较宽主室与较深侧翼相连；一座双翼住宅，不按两个山墙拆数。',
  '30×22×28，主要居室低，较高山墙和顶饰占上部；不是二十二格净高大厅，也未证明多层大庄园。',
  '浅方解石墙、深色柱框和底层窗门形成清楚的房间边界，屋脊尖饰与门廊小柱不能混作高楼。',
  '主脊与侧翼坡脊错开，高烟囱和檐角饰竖起；y10平面已切屋盖，不按灰色屋面带增加楼层。',
  'calcite591、cobbled_deepslate234、stripped_spruce_wood208、deepslate_tiles175、spruce_stairs147、blackstone139等；深顶不全是同一种黑石。',
  '六个门位均y3；y5平面见相连居室，x17与z15剖面区分房间和屋顶空腔。无梯子状态，本例以同层组织为主，不宣称原生全路通行。',
  '土草底面随双翼展开，三个平原村民池为实体生成；可作街区双翼住宅入口和分区参考，不直接证明中式建筑风格。'],
 'F07':[
  '低矮L形主空间由大室和短臂连成，较短入口侧留转角；屋盖下窄腔和地面房间区别记录，整座一项设计。',
  '15×9×15，小主室、宽低檐与短脊组成紧凑轮廓；不因sorcerer名称推断大型法殿或附加地牢。',
  '云杉木柱、深石墙段、小窗及蛛网，角部高低洞口有差；蛛网不等于实体承重墙。',
  '两段相交低坡屋盖沿L形展开，短臂屋盖较低；较高门处在屋盖线附近，不把它自动解释成完整上层走廊。',
  'deepslate_bricks162、deepslate_brick_stairs162、deepslate_tiles148、deepslate_brick_slab83、spruce_log75、cobweb45为主。',
  '底门(10,1,1)，另门(10,5,7)在上方窄屋腔；x10与z7补剖见低室和上腔，未找到梯子，不宣称上门可达或存在秘密通道。',
  '薄土草底面；两个bat_3及一个zombie_villager接口不是三间秘密房。仅提案低层L形街宅，不借文件名添加巫术玩法。'],
 'F08':[
  '长主厅连接前后较低附厅及侧廊，多层沿中轴叠合；整体长宅一项设计，不按楼层、侧翼或十二个接口拆数。',
  '29×46×48，实际z只到46，高尖饰到y45；主厅跨度和多层层板与窄高尖塔的尺度不同，不能按总高估算统一房间层数。',
  '深木竖柱、浅横带、长侧廊与多层窗分层；中央上部紫红块包含实体接口，不全是门或通道。',
  '长高山墙主顶连较低圆端/多边端附顶，单侧尖塔抬起轮廓；整体不属于单层小街宅或四棚前哨。',
  'oak_log846、spruce_stairs820、spruce_trapdoor626、mangrove_log582、spruce_slab514、stripped_spruce_log353、netherrack349等，非统一橡木材质。',
  '实际门位在y1、y8；x14/z21补剖可见约y6/13/19/28层次和高屋腔，无ladder不表示无楼梯，但尚未验完整竖向路径。y14一排jigsaw不是一排门。',
  '完整草泥基裙，十二个针叶林村民接口均为实体池，不缺十二间房；仅借厅、侧廊与附翼原则，不能当完整判官殿或已验收地下内衙。'],
}
PROPOSE={'F01','F02','F04','F06','F07'}
TARGET={
 'F01':'DUN05街区带院错层民居；36×26×44保存宅地，不覆盖整城、客栈或官衙。',
 'F02':'DUN05单主室带小阁层住宅；12×12×10，作为F02/F03家族唯一代表。',
 'F03':'仅F02旋转/覆雪/局部改动的变体研究；无独立设计提案。',
 'F04':'DUN05小型水院民居宅地；18×15×28，不覆盖忘川河或水关。',
 'F05':'高脚小厅与细塔的局部；地面入口连接待核，不计完整相关建筑。',
 'F06':'DUN05同层双翼住宅；30×22×28，不覆盖全街区或大型厅堂。',
 'F07':'DUN05低层L形小街宅；15×9×15，不含上腔路径或巫术机关验收。',
 'F08':'DUN05厅廊附翼局部原则；29×46×48地上长宅，非完整判官内衙。',
}

def evidence(p):return dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def dump(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')

def main():
 s=json.loads((OUT/'sources.json').read_text());entries=[]
 for c in s['candidates']:
  ident=c['id'];assert len(NOTES[ident])==7
  status='SCOPED_WHOLE_BUILDING_PROPOSAL' if ident in PROPOSE else 'SAME_DESIGN_FAMILY_VARIANT' if ident=='F03' else 'HELD_COMPLETENESS_OR_ROUTE' if ident=='F05' else 'SUBSPACE_PRINCIPLES_ONLY'
  entries.append(dict(id=ident,member=c['member'],nbt_sha256=c['nbt_sha256'],observations=dict(zip(FIELDS,NOTES[ident])),
   independent_design_basis=NOTES[ident][0]+' '+NOTES[ident][3],images_actually_viewed=[evidence(OUT/f) for f in c['images']+[ident+'-details.png']],
   proposed_target=TARGET[ident],status=status,credit_proposal=int(ident in PROPOSE),formal_credit_added=0,native_acceptance=False))
 dump('manual-review.json',dict(date='2026-11-01',entries=entries,method='Actually studied 32 new NBT whole/plan/vertical/detail images and source states. No additional historical images claimed in this batch.',
  counts=dict(templates_studied=8,new_images_actually_viewed=32,historical_images_reviewed_again=0,scope_specific_proposals=5,variant_exclusions=1,held=1,subspace_only=1,formal_credit_added=0),
  scope_boundary='Five different purpose/scale proposals are not five accepted credits or one common scope. F03 never contributes a second cottage design.',
  principles=['先区分宅地、房体、屋盖和烟囱的占用，保存盒不当居室面积或净高。',
   '单室阁层、错层带院宅、双翼住宅和水院住宅须各保留用途与规模，不能统一写作大型内衙。',
   '原始哈希和角色几何均不同仍可能是同一设计家族，F02/F03按布局、阁层与烟囱对应只留一例。',
   '实体拼接点不等于缺少房间；屋盖内门和高实体点不当可用上层入口。',
   '短连续梯只证明该梯段存在，高脚屋仍需单独确认地面入口，不能因此宣称全楼可达。',
   '学习空间与比例，不直接复制外来建筑，也不把欧式屋盖研究当中式风格验收。']))
 a,b=s['candidates'][1:3]
 dump('variant-family-audit.json',dict(date='2026-11-01',family_id='trek-small-gabled-attic-cottage',representative='F02',excluded_independent_designs=['F03'],
  sources=[dict(id=c['id'],member=c['member'],nbt_sha256=c['nbt_sha256'],size=c['size'],materials=c['materials']) for c in [a,b]],
  actual_visual_evidence=[evidence(OUT/f) for c in [a,b] for f in c['images']+[c['id']+'-details.png']],
  semantic_matches=['水平尺寸12×10和10×12对应旋转；同单主室、y6阁层、y2..5短梯及长双坡屋盖。',
   '同侧烟囱与四臂帽；dark_oak_stairs均106、spruce_log均56，木板数量仅局部差异。'],
  changes_not_new_design=['覆雪、底裙、门窗和入口雨篷的局部改变。','旋转后门与梯坐标改变，实体池改为雪地村民。'],
  exact_hash_match=False,method='Manual family decision from eight actual views and raw states; not inferred from filename or hash novelty.',
  max_independent_family_references=1,proposals=1,formal_credit_added=0))
 print('Eight sources / 32 actual image views / five narrowly scoped proposals; one cottage variant excluded; zero formal credits.')

if __name__=='__main__':main()
