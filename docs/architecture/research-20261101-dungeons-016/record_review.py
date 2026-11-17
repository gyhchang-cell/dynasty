#!/usr/bin/env python3
"""Five actual source studies, one whole-layout acceptance and explicit family exclusions."""
from collections import Counter
import hashlib
import json
import sys
from pathlib import Path
from zipfile import ZipFile
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
BASE=OUT.parent
sys.path.insert(0,str(ROOT/'tools/architecture'))
from nbt_read import read
FIELDS=['layout','proportion','facade','roof','materials','circulation','terrain']
PRIOR=BASE/'research-20261101-proposal-semantic-acceptance-010-015/scoped-reference-register.json'
SCOPE='DUN03-SINGLE-WATCHPOST'
NOTES={
 'F01':[
  '紧凑方塔底部围室、中部叠板和上部宽缘瞭望台贯为一体，中央竖构与侧换位梯共同组织上下；主体完整，不拆中间楼板计例。',
  '保存15×25×15，非空最高y23，y24留空；主要地板约y1/6/10/14，屋盖约y20..23。上部大空间与屋盖内腔不能折算成每格一层。',
  '木角柱、石质下沿和连续水平边带包围方形体量，上部更开敞；底侧紫点是外围组件接口，不是普通门。',
  '上台罩低坡切角宽屋盖；分类灰色中含大量深橡木半砖，不能统称石瓦。屋顶差异本身不证明与011-F04中心柱叠室塔独立。',
  'birch_planks325、dark_oak_slab255、stone_bricks177、dark_oak_log121、dark_oak_planks118、oak_slab84；层板与屋盖分别按原材辨识，不照分类色取材。',
  '无普通门；梯(7,4)y2..6、(4,10)y7..10、(5,10)y11..14，位置换移并非一根贯通梯。补看y6/y14及x4/z10，未认证转接、净空或所有房室可达。',
  '外围4个feature_plates接口加11个实体接口；地块模板是路径和进一步外接点，不是缺少塔身楼层。仅核本体，未装配营地，与011-F04家族独立性继续HOLD。'],
 'F02':[
  '中心竖柱与四周斜收木石支架构成开敞守望塔，下部较宽守备平台约y8，上部较小露台约y16；左右对称向上收分，主体没有偏置完整房楼或围院。',
  '保存17×27×17，实际最高y25，y26留空；主要驻守台到y16，以上是柱端和细旗。广基窄顶的开敞支架比例不同于012-F01狭长错位高低石残台及长外阶。',
  '木柱沿对角支撑展开，低石边／栏杆围局部平台，上段柱间敞开；按作者现存完整开敞塔体研究，不将缺大墙面解释为漏载房间。',
  '无集中封闭坡帽，y16木台以上为短柱／栏缘和细旗；不想象复原全覆顶。独立设计判断依据对称收分骨架和两级开台，而不单依据无屋顶。',
  'dark_oak_log342、spruce_planks156、cobblestone118、cobblestone_wall73、spruce_fence58、dark_oak_slab56；石木骨架与干草等储物分开，绿色变体不多计。',
  '无普通门；唯一梯(8,7)y2..16连续原状态，穿近轴线连接两台。补看y8/y16及x8/z7；连续梯证据不认证台边全可走或登旗杆。',
  '本体四边有4个外围路径地块接口，另9个实体接口；所有建筑主体在当前NBT内。路径地块未拼接且零建筑信用。作为同族F02/F03/F04唯一代表，接纳DUN03小占地独立守望塔布局1例。'],
 'F03':[
  '与F02同为宽下台、窄上台和中央梯的收分开敞支架塔；红树林材质和藤蔓遮盖骨架，不形成新的侧翼或独立房组。',
  '保存17×27×17，实际y0..25；两主要平台仍约y8/y16，梯位及逐y区间与F02相同，不因植被使非空方块增多便判新体量。',
  '红树林木、泥砖壁与藤蔓换掉深木石边；柱轴有细部状态差别，需保留而非宣称全部原状态完全一样。',
  '上台和短栏柱无大覆顶，顶端细旗沿用同一轮廓；屋缘小差异没有改变开敞塔的主要空间组织。',
  'mangrove_log342、vine296、mangrove_planks147、mud_bricks118、mud_brick_wall72、mangrove_fence58、mangrove_slab56；藤蔓不得当封闭墙体或新房间。',
  '无普通门；梯(8,7)y2..16，所有梯原状态与F02一致。补剖y8/y16与x8/z7；不以藤蔓攀爬想象额外已验路线。',
  '外围4路径地块、9实体接口，未拼装。选定结构类别870位置中与F02共865位置，保留轴向等状态差异；结合整体和平剖归同一设计族，不增加第二例。'],
 'F04':[
  '沼泽配色开敞支架塔沿用F02宽基／中台／窄顶台与中心梯布局；藤蔓密度改变可见外观，没有新增完整侧房或院落。',
  '保存17×26×17，实际y0..25，与F02/F03实际高度相同；保存盒少一层留空不是新建筑比例，主要台面仍在y8/y16。',
  '苔石、深木与藤蔓盖在同一套柱撑和栏边上，层间开空；不同绿量不当作新增实墙、额外竖井或新的体量。',
  '无大坡顶，短柱围上台后接细旗；不能以苔化栏边或细旗微调增加独立参考。',
  'dark_oak_log342、vine326、spruce_planks156、mossy_cobblestone118、mossy_cobblestone_wall70、spruce_fence58、dark_oak_slab56；苔石变化不改变骨架用途。',
  '无普通门；梯(8,7)y2..16，原梯状态同F02。补剖同层位，台面与中轴关系一致；未认证原生碰撞或藤蔓形成的可能捷径。',
  '4路径地块加9实体接口，同样未拼装。与F02所选结构共868位置，868处形态与属性均相同，差异位置另存；归同族，不增加第三例。'],
 'F05':[
  '较细长下塔身托宽大上台，中央较小上室再覆低帽，外围多横带和地脚斜撑；整塔完整，但与旧013-F03 taiga构图非常接近。',
  '保存19×34×19，实际y0..33；大上台约y17，上室和盖约y20..26，其后细旗到y33。细旗不是额外房层，顶台宽度不代表整个下塔身同宽。',
  '深木竖柱、灰石横带和台缘开栏与旧taiga的主要立面组织相近，地脚与物件差别尚不足以证明独立主体设计。',
  '宽檐低帽罩较小中央上室，细旗更高；上盖和檐环不拆计。不能因源在TREK而自动排除与KAISYN现有设计族重复。',
  'dark_oak_log328、dark_oak_slab254、spruce_stairs180、dark_oak_planks135、dark_oak_trapdoor113、grass_block100；分类灰帽仍含木半砖，不冒称全石构。',
  '无普通门；梯(9,6)仅y19..22，下段保存大量台阶但未做原生连通证明。补看y17/y23及x9/z6，旧013-F03梯状态不全相等，不宣称字节相同。',
  '4路径地块接口加9实体接口；未装配外围。相对013-F03所选构件占位相似约83.9%，同坐标同形态属性1125处，仍有实质细节差异；整体空间近同族，独立计数暂缓。']}
COMPARE=[('research-20261101-dungeons-008','F04-whole.png'),('research-20261101-dungeons-013','F03-whole.png'),
 ('research-20261101-dungeons-012','F01-whole.png'),('research-20261101-dungeons-011','F01-whole.png'),
 ('research-20261101-dungeons-011','F04-whole.png'),('research-20261101-dungeons-012','F03-whole.png'),
 ('continuation-20261022/references/whole-candidates','W008.png'),('research-20261101-dungeons-011','F02-whole.png'),
 ('research-20261101-dungeons-012','F02-whole.png'),('research-20261101-dungeons-013','F01-whole.png'),
 ('research-20261101-dungeons-015','F01-whole.png'),('research-20261101-dungeons-013','F02-whole.png'),
 ('research-20261101-dungeons-015','F03-whole.png'),('research-20261101-dungeons-014','F02-whole.png')]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ev(p):return dict(path=str(p),sha256=sha(p))
def get(p):return json.loads(p.read_text())
def dump(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def main():
 src=get(OUT/'sources.json');entries=[];states=[]
 for c in src['candidates']:
  i=c['id'];status=('ACCEPTED_SCOPED_WHOLE_LAYOUT_REFERENCE' if i=='F02' else 'FAMILY_VARIANT_NO_ADDITIONAL_CREDIT' if i in ['F03','F04'] else 'FAMILY_INDEPENDENCE_HOLD')
  entries.append(dict(id=i,source=c,observations=dict(zip(FIELDS,NOTES[i])),status=status,credit=int(i=='F02'),
   scope_id=SCOPE if i=='F02' else None,actual_images_viewed=[ev(OUT/n) for n in c['images']+[i+'-details.png']],
   counted_family_representative='016-F02' if i in ['F02','F03','F04'] else None,native_acceptance=False))
  with ZipFile(c['source_archive']) as z:
   d=read(z.read(c['member']));p=d['palette']
   states.append(dict(id=i,nbt_sha256=c['nbt_sha256'],stairs_doors_ladders=[dict(position=b['pos'],state=p[b['state']]) for b in d['blocks'] if p[b['state']]['Name'].endswith(('_stairs','_door')) or p[b['state']]['Name']=='minecraft:ladder']))
 dump('manual-review.json',dict(entries=entries,new_templates_studied=5,new_images_actually_viewed=20,historical_images_reviewed_again=14,
  supplementary_old_identity_section_images=6,accepted_independent_layouts=1,variants_not_additional=2,family_holds=2,
  historical_comparison_views=[ev(BASE/f/n) for f,n in COMPARE],
  independence_for_016_F02='已验6例中：011-F01细颈托宽室，011-F02多级同轴收分室塔，012-F01偏心长阶错台废塔，012-F02偏移收腰多室塔，013-F01偏心多小室石塔，015-F01连续方筒内室露台。本例为宽基斜撑、对称收分中台与小上台的开敞架塔，连接同轴长梯；不是给上述已验主体单换材、改屋顶或旋转。',
  other_nearest_comparison='008-F04 piglin_mine_2为低矮封壳屋和侧凹工位，不是双级开台架塔；几何近邻不代替实际语义。016-F05与013-F03近同族，换包和实体点不证明新设计。',
  limits='所有图为离线分类色与全方格近似。188历史身份的几何筛查不是188个有效建筑或本次全部目视复核。'))
 dump('vertical-original-states.json',dict(entries=states,formal_credit_added=0,native_acceptance=False))
 interface=get(OUT/'interface-audit.json');comp=[];seen=set()
 for e in interface['entries']:
  c=next(c for c in src['candidates'] if c['id']==e['id'])
  with ZipFile(c['source_archive']) as z:
   for pool in e['outgoing_pools']:
    for r in pool.get('component_identities_only',[]):
     if r['member'] in seen:continue
     seen.add(r['member']);raw=z.read(r['member']);d=read(raw);p=d['palette']
     comp.append(dict(member=r['member'],sha256=hashlib.sha256(raw).hexdigest(),size=d['size'],
      entity_ids=[e['nbt'].get('id') for e in d['entities']],materials=dict(Counter(p[b['state']]['Name'] for b in d['blocks'])),
      sockets=[dict(position=b['pos'],state=p[b['state']],data=b.get('nbt',{})) for b in d['blocks'] if p[b['state']]['Name']=='minecraft:jigsaw'],
      kind='PATH_PLATE_WITH_FURTHER_FEATURE_SOCKETS' if 'feature_plate' in r['member'] else 'SINGLE_ACTOR',
      images_viewed=False,assembled=False,building_credit=0))
 dump('secondary-component-boundary.json',dict(entries=comp,formal_credit_added=0,limits='Three path plates and three one-actor templates are not whole building references. Further feature pools not assembled or certified.'))
 oldsrc=get(OUT/'hold-sections/sources.json')['candidates']
 dump('hold-review.json',dict(entries=[
  dict(id='011-F04',decision='HOLD_FAMILY',credit=0,new_sources=0,
   observations='H01新增y7/y14室层平剖及x7/z8纵剖：下层近方形围护包中心木柱，上层扩宽外缘并围中心梯柱留空，未见把室层分成多个独立房间的连续隔墙。T01/swamp的y6较宽下室、y18较小上室；T02的y2/y12均为紧凑单室围中心柱，纵剖保留两处交叠梯；T03改取y2/y23，确实比较下室和上室，低段旁附构件、上层方形围护与中间细颈可区分。楼层高度、围护尺寸、柱梯关系有差异，但仍不足以排除同一中心竖构叠室原型的尺度及屋盖变体，继续保留。',
   next_evidence='已有六幅补剖中的匹配室层对照；仍需逐层标出入口、隔墙开口与平台的完整邻接关系，并验证差异超出尺度和屋盖调整。分类色整方块剖面不认证原生碰撞或完整通路，不能以没有相同哈希代替设计族判断。',
   section_ids=['H01','T01','T02','T03']),
  dict(id='012-F03',decision='HOLD_FAMILY',credit=0,new_sources=0,
   observations='H02新增y6/y12平剖、x16厅横剖及z5纵剖：长厅两侧重复柱窗，较低平层为连贯厅腔，较高平层两侧屋坡侵入，单端高塔沿长轴接厅。T04/W008的y3/y9及x10/z4剖面同样为端塔顺接单一长厅，较高平层从全厅缩到塔及坡顶残段。H02上台y29、长厅脊约y20，W008体量较小且塔覆坡帽；厅高、围护节奏及塔帽不同，未见足以证明独立布局的新增厅翼或另一路分区，继续保留。',
   next_evidence='已补厅内平层与塔厅转接剖面；仍需穷举转接处各层的开口和入口至塔的邻接关系，对照归一化厅塔比例后确认是否超出教堂原型尺度／屋盖变体，现不接纳。',section_ids=['H02','T04'])],
  images_actually_viewed=[ev(OUT/'hold-sections'/f"{e['id']}-details.png") for e in oldsrc],
  source_identities=[{k:e[k] for k in ['id','prior_identity','source_archive','source_archive_sha256','member','nbt_sha256','size','original_index']} for e in oldsrc],
  new_buildings_added=0,independent_reviewer_claimed=False))
 prior=get(PRIOR);tower=next(s for s in prior['scopes'] if s['scope_id']==SCOPE)
 assert tower['accepted_references']==6 and tower['remaining']==994 and not tower['construction_allowed']
 accepted=entries[1]
 dump('scoped-reference-update.json',dict(scope_id=SCOPE,scope_definition=tower['scope_definition'],
  prior_register=ev(PRIOR),previous_accepted=6,previous_accepted_ids=tower['accepted_ids'],
  added=[dict(id='016-F02',source=accepted['source'],observations=accepted['observations'],credit=1,
              family='SYMMETRIC_TAPERED_OPEN_FRAME_TWO_GUARD_PLATFORMS',actual_views=accepted['actual_images_viewed'],
              source_review=ev(OUT/'manual-review.json'),family_comparison=ev(OUT/'family-structural-evidence.json'),native_acceptance=False)],
  accepted_references=7,remaining=993,target=1000,construction_allowed=False,
  not_additional_ids=['016-F01','016-F03','016-F04','016-F05'],prior_two_holds_still_held=['011-F04','012-F03'],
  unchanged_scope_counts={'DUN03-MEDIUM-GROUND-GARRISON':4,'DUN03-HALL-WITH-LOOKOUT':1},
  old_credit_transferred=0,production_tasks_completed=0,checklist_deletions=0,
  count_unit='F02、F03、F04同族整体仅F02一次；不按截图、旋转、材质、藤蔓、平台或外围路径片段增加例数。',
  application='仅古战场附属小占地守望岗位的现存开敞塔布局，不是中心瓮城、全战场、国风资产、原生通路／地形、任务或指南针验收。'))
 print('Five templates studied: one whole watchpost family accepted once; two variants, two new family holds; two prior holds retained.')
if __name__=='__main__':main()
