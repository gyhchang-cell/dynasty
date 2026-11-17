#!/usr/bin/env python3
"""Record examined narrow towers while withholding unproven family instances."""
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
  '13格方形底盘内中央柱与窄室板竖向叠置，约y11为环边板、y18上板托较开敞上室，单顶出檐；不是把每一室板、柱架或帽顶拆成建筑。',
  '13×34×13，占用y0..33；顶大檐约y24，旗杆继续到y33，主体下室比屋檐窄。上板与低板间空段不能折算成额外房层。',
  '竖向浅色去皮云杉柱夹深板岩低墙，板缘短柱与小悬灯点缀；上室较开敞、下室深色围护，非整座封闭石塔。',
  '单顶近四坡逐级收分深板岩帽，宽檐在约y24，上带旗；与其他窄塔的尖帽、双坡、重檐差别本身不足以证明独立。',
  'spruce_planks286、stripped_spruce_log277、spruce_stairs110、spruce_slab108、spruce_fence98、polished_deepslate_slab79；灰深屋顶含板岩，不能按分类颜色一律叫普通石。',
  '无普通门；(6,3)梯y2..7、(6,8)y6..12、(6,5)y13..19，三段位置改变。补看y11/y18及x6/z8，确认梯与板相邻，未认证各转接和地面至屋顶完整原生通路。',
  '模板几乎是柱架地脚而非整块自然地形，9个接口为8grunt和1captain。不能从flower_forest文件名推定花林环境已验证；中心柱窄塔家族独立性暂缓，当前零提案。'],
 'F02':[
  '低部窄石室前有短外阶，中段约y13扩大十字边室板并盖一圈低坡帽，上方约y22又托收窄小室和更高帽，仍以中央柱串联的整座窄塔研究。',
  '13×37×13，占用y0..36；中板约y13，顶部小室底约y22、顶帽约y26..30，细旗至y36。前阶、板缘及屋顶的边界不是全高实用室面积。',
  '底部苔石围窄室，上部木柱夹白陶小墙与玻璃，较低一圈坡檐和较高帽形成收分；新窗型和覆苔不自动增加建筑实例。',
  '下圈坡帽约y17..20与高小帽约y26..30分开，中间有更窄上室；需按室板和连接关系比较，不能只用双帽外形判独立。',
  'oak_planks306、cobblestone170、stone_brick_stairs156、oak_slab146、oak_stairs120、mossy_cobblestone84、white_terracotta64；石坡檐与木楼板分别辨认。',
  '普通门(9,4,5)、(6,6,3)、(6,6,9)均不在y1。梯(8,8)y1..4、(8,9)和(9,8)各y14..17；补看y13/y22与x8/z9，不把三段短梯说成贯通全塔。',
  '地脚仅少量草土石与前阶，不证明meadow坡地落位；9点为8grunt和1captain。与旧011-F04、013-F02/F03均需中心柱/分层上室语义复核，本批暂不提交新增信用。'],
 'F03':[
  '近方底部工作室上方叠多层绕中央柱的板与外缘栏框，约y13宽板、y19上室底板及约y24高盖下的室段，外周水平层带较明显；依然是单塔而非多栋亭楼。',
  '13×34×13，占用y0..33；普通门仅y20，最上旗y30..33，最高点与居住/守望空间高度分开记。底盘宽与同批其他13格塔相同不构成独立或相同证明。',
  '金合欢竖柱、水平石板外带及上室柱围较规则，底部有石脚包角与木构小侧段；较少苔化和不同木色不能作为设计去重依据。',
  '上盖分层收分并带高角柱/中杆，石板带与木坡片交织；它与F01深色四坡、F04双坡的区别不直接转换为参考数量。',
  'acacia_log245、stone_slab210、oak_planks166、acacia_stairs128、andesite_slab122、acacia_slab120、stripped_acacia_log95；层带含多种石半砖，不是数个完整实心石楼层。',
  '普通门(3,20,3)、(7,20,3)在高层；短梯(3,6)、(6,3)仅y2..4。补看y13/y20及x3/z6，中心升高构件记录原楼梯状态；最低普通门y20不能当作真实地面入口。',
  '底部是小石脚和柱基，不把savanna名字当作已验证的干草原地形；10点为9grunt和1captain。与F04及既有中央柱单塔的主体家族区分不足，保留研究不提案。'],
 'F04':[
  '较厚石木底室上有约y12宽板，中央连续升高构件通过较高空段通向约y24上室板，上室顶是横向双坡盖；底板、上室和屋顶作为整座设计一起看。',
  '13×35×13，占用y0..34；约y12至y24间较高柱架/楼梯段，主屋顶约y28..34，顶部无其他实例可拆。与同高窄塔的室板间距应比较而不是按文件尺寸直接去重。',
  '深橡木竖柱、云杉板及石窗边形成窄高分层墙面，底部较实，柱架中段较空，上室围护更紧；厚脚与栏格变化还不能独立通过家族验收。',
  '双坡山墙沿一个方向展开，两侧长檐与端部木横带清楚；双坡对四坡的改变属于需剥离检查的屋顶变量，不能因此单独加一例。',
  'spruce_planks335、dark_oak_log254、dark_oak_stairs130、spruce_trapdoor122、cobblestone112、hay_block108、spruce_stairs104；hay_block在原料清单中，不能把所有黄色格认作灯或室外草垛。',
  '底部普通门(2,1,6)；梯(6,3)和(9,6)仅y1..3。补看y12/y24及x6/z3，中央构件向上延续，但没有运行游戏验证转角、头部净空或所有室段可达。',
  '仅少量草径地脚，文件snowy_taiga不证明模板已有完整雪坡；8点为7grunt和1captain。与F03及旧中心柱塔的室板/层架家族待审，当前零提案。']}
COMPARE=[('research-20261101-dungeons-011','F04-whole.png'),('research-20261101-dungeons-013','F02-whole.png'),
 ('research-20261101-dungeons-013','F03-whole.png'),('continuation-20261022/references/whole-candidates-004','D008.png')]
def ev(p):return dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def dump(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def main():
 s=json.loads((OUT/'sources.json').read_text());a=json.loads((OUT/'interface-audit.json').read_text());entries=[];states=[];actors={}
 for c in s['candidates']:
  i=c['id'];entries.append(dict(id=i,member=c['member'],nbt_sha256=c['nbt_sha256'],observations=dict(zip(FIELDS,NOTES[i])),
   proposed_target='DUN03窄型中心柱叠层守望塔研究；独立设计尚未通过，不增加任何范围信用。',
   independence_question=NOTES[i][0]+' '+NOTES[i][1],status='FAMILY_DISTINCTNESS_UNRESOLVED_NO_PROPOSAL',
   images_actually_viewed=[ev(OUT/n) for n in c['images']+[i+'-details.png']],credit_proposal=0,formal_credit_added=0,native_acceptance=False))
  with ZipFile(c['source_archive']) as z:
   d=read(z.read(c['member']));p=d['palette'];states.append(dict(id=i,nbt_sha256=c['nbt_sha256'],stairs_doors_ladders=[dict(position=b['pos'],state=p[b['state']]) for b in d['blocks'] if p[b['state']]['Name'].endswith(('_stairs','_door')) or p[b['state']]['Name']=='minecraft:ladder']))
   for pool in next(x for x in a['entries'] if x['id']==i)['outgoing_pools']:
    for comp in pool.get('component_identities_only',[]):
     raw=z.read(comp['member']);cd=read(raw);cp=cd['palette'];actors[comp['member']]=dict(member=comp['member'],sha256=hashlib.sha256(raw).hexdigest(),size=cd['size'],
      entity_ids=[e['nbt']['id'] for e in cd['entities']],materials=dict(Counter(cp[b['state']]['Name'] for b in cd['blocks'])),images_viewed=False,assembled=False,building_credit=0)
 dump('manual-review.json',dict(entries=entries,counts=dict(templates_studied=4,new_images_actually_viewed=16,historical_images_reviewed_again=4,proposals=0,family_holds=4,formal_credit_added=0),
  historical_comparison_views=[ev(OUT.parent/f/n) for f,n in COMPARE],semantic_deduplication=[
   '四份源模板原始/四旋转分类几何哈希与181个历史archive/member对无精确匹配；181包含非建筑组件，不等于181个有效相近实例。',
   '最近几何相似D008海庙是12×14×15低方石水室、低层环檐，和本批约34..37高中心柱塔用途与室板关系不同；Jaccard相似不是语义同一，也不能因此证明本批塔彼此独立。',
   '实际重看旧011-F04、013-F02/F03：中央竖柱、外围楼层和上室/帽顶组成有家族重叠。旧013两塔仍未证独立，本批不借它们建立新信用。',
   'F01约y11/18室板和单大帽、F02约y13宽中板+约y22小上室、F03约y13/19分层室板、F04约y12/24高跨段双坡上室可辨区别；未证明这些区别超出同族楼层/帽顶变体，四项均暂缓。',
   '不武断断言四座完全相同，也不因木种、覆苔、窗、短梯、旗或不同体积/哈希而把它们计为独立建筑。'],
  principles=['同一中心柱塔族先对照室板、上室位置和内部连接，屋顶/材质差异不自动增加实例。',
   '完整塔形和相近用途不等于独立设计已经确认，待证时保留观察且不增账。',
   '最高旗杆、宽檐与短梯的保存尺寸不能当作可用楼层数或全程通路。',
   '分类图中的灰格/黄色格会合并不同材料，回查原始方块后再命名。',
   '文件中的生物群系名称不代替地脚、雪坡和生成地形的验证。']))
 dump('vertical-original-states.json',dict(entries=states,formal_credit_added=0,limits='Original stair/door/ladder states only; no native route certification.'))
 dump('actor-component-boundary.json',dict(entries=list(actors.values()),formal_credit_added=0,limits='Three single-actor templates, no rooms or complete buildings.'))
 print('Four examined whole narrow tower templates, four family holds, zero proposals or formal credit.')
if __name__=='__main__':main()
