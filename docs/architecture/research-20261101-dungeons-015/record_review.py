#!/usr/bin/env python3
"""Three source studies, one bounded mud watchtower proposal and two family holds."""
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
  '泥砖方筒围连续叠层内室，约y4低板、y10中板、y20大上台，顶部无坡帽而是敞天木围沿；实体围筒与开放顶台作为一座守望塔，不拆成房、平台或地基。',
  '保存15×25×15，实际非空y0..22，末端两层留空不当建筑高度。顶台约y20、墙筒到其下；较宽连续围筒不同于仅细柱托宽顶小室的比例。',
  '泥砖/压实泥墙夹窄长白玻璃与木支撑，上缘木托臂外挑平台，下沿木石草地脚；不是给旧中心柱石木塔换成泥色就直接加例，而是看围筒/楼板/无帽露台组织。',
  '无四坡或双坡帽，约y20木板为开放顶台、外圈短围沿；台面零碎物件不认作新小房，细装饰不当额外楼层。',
  'spruce_planks298、stripped_spruce_wood284、packed_mud231、mud_bricks228、spruce_trapdoor151、mud_brick_wall118、mossy_cobblestone82；不能把红分类全叫红砖，原表另含10TNT。',
  '唯一普通门(3,5,7)，并非y0入口；两段梯(9,5)y5..10、(5,9)y11..20。补看y11/y20及x9/z9，内板与换侧梯可辨，未认证两段间转接及全程原生可走。',
  '底部(7,0,7)向下terrain_small接口；原外接25×24×25仅石土草地形和一个同名接口，未渲染/拼装/验证终止或生成落位。建筑本体布局可提DUN03泥墙方筒敞天守望塔，完整生成地形不算验收。'],
 'F02':[
  '极细中央竖杆周边换面短梯串接，长杆顶约y23托一间宽切角方形高室，顶盖近水平；杆中段不是一串可拆的房楼，是整座单高室守望塔。',
  '15×30×15，占用y0..29；中段多数层仅约10..21个非空格，上室板约y23、顶盖约y28。保存宽度主要由高室出挑控制，不代表下部也有15格方屋。',
  '去皮云杉窄杆与错面小支块向上延续，高室角柱、半砖边和低栏框更宽；未把每根外挑短块都视作门廊或可站平台。',
  '高室顶为近水平薄盖，外缘木石半砖切角，顶部仅少量短构件；和旧011-F01的宽檐上室差别需排除屋盖/尺度变量，不能仅换平盖算独立。',
  'stripped_spruce_wood254、spruce_trapdoor102、cracked_stone_bricks97、spruce_slab81、spruce_stairs44、spruce_planks41、ladder23；主杆为木，不把灰阶分类当石质实心塔身。',
  '无普通门；梯绕四面分段：(8,7)y1..6及21..23、(7,6)y7..11、(6,7)y12..16、(7,8)y17..20。同一xz梯有y7..20缺段，不能汇总min/max后谎称连续；补看x8/z6未做原生换面转接验收。',
  '少量草土石小脚，顶室一个zombie_villager接口。原组件1×3×1仅单僵尸村民与empty终止，不是另一个房屋；与旧宽上室窄颈塔的家族独立性暂缓，无新增提案。'],
 'F03':[
  '小底石室、中段较窄柱室与上部小帽室绕中央柱叠置，约y6宽板和y11上板，外圈低矮石边；小整塔完整，但不因更小而自动成为独立设计。',
  '10×30×9，占用y0..29，主要房室约y1..15，主砖帽约y16..20，其上细长杆到y29；29高绝不等于29层可用房间。',
  '石角柱与小木窗段、上部方解石浅墙和玻璃，底部草地窄边，横向石板带分出几段；窗色与材质变化不是去重依据。',
  '窄小砖四坡帽带极长中杆和偏置烟管，和旧011-F04的砖帽木石中心柱塔相近；帽顶尺寸、烟管与尖杆不够证明新设计。',
  'stone_bricks123、spruce_stairs71、stone59、brick_slab58、stripped_spruce_log49、calcite42、spruce_fence33；浅分类中还含diorite30，不能一概当白陶。',
  '无普通门；梯(5,5)y1..9、(4,4)y7..15交叠但位置不同。补看y7/y11及x4/z5，记录小室与上板，未认证梯间移动、净空和所有房室可达。',
  '小草土地脚且无拼图接口，只有完整本体形态研究，不代表原生成地形/入口已通过。与旧中心柱塔主体家族待辨，当前零提案；不因无外接接口自动过独立性检查。']}
COMPARE=[('research-20261101-dungeons-011','F01-whole.png'),('research-20261101-dungeons-011','F04-whole.png'),
 ('research-20261101-dungeons-001','F12-whole.png'),('continuation-20261022/references/whole-candidates-003','C024.png')]
def ev(p):return dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def dump(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def main():
 s=json.loads((OUT/'sources.json').read_text());a=json.loads((OUT/'interface-audit.json').read_text());entries=[];states=[];components=[]
 for c in s['candidates']:
  i=c['id'];entries.append(dict(id=i,member=c['member'],nbt_sha256=c['nbt_sha256'],observations=dict(zip(FIELDS,NOTES[i])),
   proposed_target='DUN03泥墙方筒敞天守望塔，15×25×15保存尺寸，实际本体最高y22；仅建筑布局。' if i=='F01' else '细杆宽上室/小型中心柱塔家族研究，独立性暂缓，不增加任何范围信用。',
   independence_question=NOTES[i][0]+' '+NOTES[i][1],status='SCOPED_WHOLE_TOWER_PROPOSAL' if i=='F01' else 'FAMILY_DISTINCTNESS_UNRESOLVED_NO_PROPOSAL',
   images_actually_viewed=[ev(OUT/n) for n in c['images']+[i+'-details.png']],credit_proposal=int(i=='F01'),formal_credit_added=0,native_acceptance=False))
  with ZipFile(c['source_archive']) as z:
   d=read(z.read(c['member']));p=d['palette'];states.append(dict(id=i,nbt_sha256=c['nbt_sha256'],stairs_doors_ladders=[dict(position=b['pos'],state=p[b['state']]) for b in d['blocks'] if p[b['state']]['Name'].endswith(('_stairs','_door')) or p[b['state']]['Name']=='minecraft:ladder']))
   for pool in next(x for x in a['entries'] if x['id']==i)['outgoing_pools']:
    for comp in pool.get('component_identities_only',[]):
     raw=z.read(comp['member']);cd=read(raw);cp=cd['palette'];components.append(dict(candidate=i,member=comp['member'],sha256=hashlib.sha256(raw).hexdigest(),size=cd['size'],
      entity_ids=[e['nbt']['id'] for e in cd['entities']],materials=dict(Counter(cp[b['state']]['Name'] for b in cd['blocks'])),
      sockets=[dict(position=b['pos'],state=cp[b['state']],data=b.get('nbt',{})) for b in cd['blocks'] if cp[b['state']]['Name']=='minecraft:jigsaw'],
      kind='STONE_SOIL_TERRAIN_NOT_BUILDING' if i=='F01' else 'ONE_ZOMBIE_VILLAGER_NOT_BUILDING',images_viewed=False,assembled=False,building_credit=0))
 dump('manual-review.json',dict(entries=entries,counts=dict(templates_studied=3,new_images_actually_viewed=12,historical_images_reviewed_again=4,proposals=1,family_holds=2,formal_credit_added=0),
  historical_comparison_views=[ev(OUT.parent/f/n) for f,n in COMPARE],semantic_deduplication=[
   '185历史archive/member对无原始或四旋转分类几何精确匹配，批内也无精确重复；不是185个有效相近建筑。',
   'F01最近几何旧011-F04是中央柱围较窄上室及大砖帽；新为连续泥墙围筒、两层内室和整块敞天上台，不靠泥色区别，按整塔限定提案，生成地形接口另保留未验。',
   'F02最近001-F12旧witch_tower为塌损尖帽复合室塔，不同于长细杆托宽高室；但与旧011-F01宽上室窄颈塔仍有家族疑问，当前不认定独立或相同。',
   'F03最近C024为10×13×7低层祭祀屋加偏置后高室/水顶，与新窄高中心柱塔不同；然而旧011-F04同有中心柱石木叠室和砖帽，缩小、旗杆与配色不足以直接增加新实例。'],
  principles=['塔身是否连续封闭、上台是否敞天、可用房室与细杆的关系，比换泥色、帽顶和旗杆更有助判断独立设计。',
   '原本体的布局研究与外接地基的生成验收分开；地形模板不是完整建筑参考。',
   '同一xz处的多段梯保留每个y，不能把有缺口的min/max写成连续梯段。',
   '保存尺寸包括留空和旗杆，按实际占用与楼板/房室范围分别解释比例。',
   '不同作者或包也可能共享设计家族，换源不代替语义去重。']))
 dump('vertical-original-states.json',dict(entries=states,formal_credit_added=0,limits='Original states only; no native route certification.'))
 dump('secondary-component-boundary.json',dict(entries=components,formal_credit_added=0,limits='Raw terrain and single-actor identities, not rendered or assembled; terrain matching, processors and termination not verified.'))
 print('Three whole tower studies: one bounded layout proposal, two family holds, zero formal credit.')
if __name__=='__main__':main()
