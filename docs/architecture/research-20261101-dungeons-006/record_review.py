#!/usr/bin/env python3
"""Four actual studies with explicit rejection from the three accepted scopes."""
import hashlib
import json
from pathlib import Path
OUT=Path(__file__).resolve().parent
FIELDS=['layout','proportion','facade','roof','materials','circulation','terrain']
NOTES={
 'F01':[
  '中央单塔带低平台，左右另有低砂屋与白棚，整片营地为一个设计；与003-F01双主塔相连不同，不按营地附属物拆例。',
  '40×20×22保存及占用边界，高塔至y19，低附屋约y5；不是双高塔、多角高楼或16×8×16低四棚院。',
  '塔身细窄、两层外挑平台和少量窄口，营地外围离散细杆多为仙人掌；不能全写成石防柱。',
  '主塔平帽分阶收进，附屋为低平顶，另一侧白羊毛小棚；不是四角等量哨棚屋盖。',
  'sand699、smooth_sandstone278、cut_sandstone173、sandstone_wall127、smooth_sandstone_stairs100、cactus47及white_wool25；仙人掌并非石材。',
  '无door或ladder状态，y4/y15平面及x20/z11剖面显示下上平台与中部塔心；台阶状态未做碰撞通路验收，不能认定全部可达或完全无路。',
  '沙地内围小水池且保存五条热带鱼实体；十二个jigsaw全是悦灵/卫道士/掠夺者实体池，不是缺十二间房。可学单塔营地层次，但不进入已有三个限定范围。'],
 'F02':[
  '木围篱内分布短棚、树木、水池和营地空地；整片营地一个研究单位，四棵高树不是四角建筑哨棚。',
  '31×28×26，保存高度主要来自高树冠，棚屋和围篱多在y0..5；不能称二十八格高的城堡或多层寨楼。',
  '木围篱、低柱棚与藤蔓形成边界，石灰色短顶下为小棚；植物遮挡不能据此推断墙体完整。',
  '低棚短脊与开口围院并存，上方大片绿色为树冠；不能将叶冠当四座有房间的塔帽。',
  'jungle_leaves958、vine566、grass_block491、jungle_log484、stripped_jungle_log127、bamboo82为主，需将树木和人工棚柱区分。',
  '无door/ladder，y4平面和x10/z11补剖定位短棚与地面院路；y8主要只余树干，不能算第二层棚房或攀爬路线。',
  '完整草泥营地有小水池；八个接口为掠夺者、熊猫和鹦鹉实体池，无房间待拼。可学营地遮挡控制，不计近地四哨棚、双高塔或角塔连L厅。'],
 'F03':[
  '高一些的主屋与低侧厅、外廊连成偏L形小组，旁有围边草台；不是一座高角塔控低厅，也不是两高塔。',
  '25×16×27保存边界，实际最高y14；主屋为约三段层次、外廊低，不能因outpost名称升级为高塔堡。',
  '浅砂岩木框、下部窄窗与高层侧门，外廊开敞；外放储箱及散块不等于新的独立储屋。',
  '主屋有较高短坡顶，低翼覆平顶/草台，外廊不封大院；与四角等量棚或双垛口塔不同。',
  'sand512、cut_sandstone222、spruce_slab186、sandstone177、stripped_spruce_log134、spruce_trapdoor118等；分类灰顶中含木半砖。',
  '门在(10,1,13)、(6,5,14)、(14,5,14)；x12,z18梯y6..8连续，补剖见约y4/8层板及屋盖下腔，未验证地面到每层的原生路径。',
  '沙地基裙无jigsaw，主屋及低厅不需外接房池；可留小驻守屋与外廊比例原则，不为既有高角塔范围借用计数。'],
 'F04':[
  '长方上层主厅覆盖低层多室，侧边附低外廊和小屋顶；是整体民居/村民站屋组织，不是军事双塔或四棚院。',
  '21×15×25，实际高15格，上部宽高厅与底部较低间分层；不按上层高度宣称四角哨塔或大型府衙。',
  '下层多门口、上层窄窗和立柱，深浅石墙配木柱；环地路径与棚口构成多面进入的民居界面。',
  '上层单长坡顶远高于侧廊低顶，宽檐遮主体；灰色屋面含spruce_slab而非全石板。',
  'spruce_slab286、grass_block197、cobblestone142、oak_slab138、stone120、oak_planks104、dirt_path100为主。',
  '四处底门均y1，x11/z12补剖见约y5层板与上厅空腔；原始实体含十个村民，部分保存在较高y，不据实体位置假定楼梯净空和全部可达。',
  '土草路径基裙无jigsaw，未缺房间；可作DUN05小街屋上下厅、外廊的局部原则，不因outpost文件名就计DUN03军哨范围。'],
}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 s=json.loads((OUT/'sources.json').read_text());entries=[]
 for c in s['candidates']:
  ident=c['id']
  entries.append(dict(id=ident,member=c['member'],nbt_sha256=c['nbt_sha256'],observations=dict(zip(FIELDS,NOTES[ident])),
   images_actually_viewed=[dict(path=str(OUT/f),sha256=sha(OUT/f)) for f in c['images']+[ident+'-details.png']],
   independent_design_basis=NOTES[ident][0]+' '+NOTES[ident][3],
   status='COMPLETE_SOURCE_DIFFERENT_PURPOSE_SCALE' if ident!='F02' else 'LANDSCAPED_CAMP_NOT_FOUR_BUILT_CANOPIES',
   scope_rejection=NOTES[ident][6],credit_proposal=0,formal_credit_added=0,native_acceptance=False))
 d=dict(date='2026-11-01',entries=entries,counts=dict(templates_studied=4,new_images_actually_viewed=16,seven_aspect_reviews=4,proposals=0,formal_credit_added=0),
  method='Actual study of 16 whole/plan/vertical/detail images and original source states, not name-based selection credit.',
  scope_boundary='No source matches the accepted twin-tall-tower, corner-tower-L-hall, or low-four-built-canopy scope sufficiently for credit; all three stay 1/1000.',
  principles=['树冠、仙人掌、实体接口与人工哨棚/石柱/房间分别识别，不能拿植物制造建筑数量。',
   '同叫outpost，单塔营地、树下篱院、低屋廊组和村民站屋用途与尺度不同。',
   '低主屋带侧棚不能借高角塔连厅的门槛，单塔也不能借双高塔门槛；保留不适用记录。',
   '研究资料可以有用但不计入当前范围，不能为了数字把相似词汇和完整模板直接当有效参考。'])
 (OUT/'manual-review.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
 print('Four original sources and sixteen actual views recorded; no scoped credit or proposals.')
if __name__=='__main__':main()
