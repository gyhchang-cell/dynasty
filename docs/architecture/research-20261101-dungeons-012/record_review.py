#!/usr/bin/env python3
"""Four actually inspected whole designs, including a windmill purpose hold."""
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
  '高低两段断石塔墙前后错置，外伸长阶/残台沿较低一侧上升，四周木长柱支撑局部边缘；研究作者整座守望塔遗址，不把残台和高塔拆两例。',
  '18×38×25，占用y0..37，主体较狭长；高处平台约y23，侧小砖帽约y29..32，旗在更高处。断墙、细旗不当作完整居住楼层。',
  '圆石、苔圆石和铁栏组成破损墙面，外露木柱到地；不同于旧dark_keep厚墙完整方堡连侧门堡的密实体量。',
  '主要高台露天，偏侧小竖段保留一顶红砖坡帽，残檐随破墙断开；不能想象整个废塔原本都是砖覆顶。',
  'cobblestone568、mossy_cobblestone402、oak_fence126、oak_slab123、stone_bricks114、cobblestone_stairs107、iron_bars60、brick_stairs39；大量绿色为苔石，不是统一树叶。',
  '无普通门/梯方块，原始石木台阶全量另存；补看y11/y23与x8/z9，见低段长台和高平台不同层级，未认证残阶连续可走或每处破墙可达。',
  '草、碎石及外柱脚包含在模板内；11点为10grunt和1captain。提案DUN03狭长错层废塔及外阶，限定作者完整遗址体，不补造缺失屋顶。'],
 'F02':[
  '不规则收腰塔体逐层偏移，多个小室与外挑阳台沿竖向错落，底部展开较宽石质地脚；不是直接放一根实心蘑菇茎，也未见典型巨蘑菇菌盖。',
  '20×53×19，占用x1..19、y0..52、z0..18；室层/门在y1、10、18、24、29，小上室与尖顶更高，不能把53格盒高全当可用楼层。',
  '蘑菇柄方块外皮包木楼层，房体与外挑小台不规则收放；虽然分类图为灰色，不能写成全石塔，外形差异在楼层错移而非单换白材。',
  '上部窄木尖帽和细旗封顶，沿侧面有小阳台罩/局部挑边；整组塔室和阳台一次，不拆多层平台增数。',
  'mushroom_stem780、spruce_planks310、spruce_slab271、cobbled_deepslate130、smooth_basalt95、dark_oak_log72、shroomlight28；蘑菇柄主墙与深石地脚和木室板分开。',
  '底门(12,1,15)，门层还见y10/18/24/29；唯一梯x7,z12仅y26..29。补看y18/y29及x7/z12，门较多不证明每层到达，未认证全部错层的原生通路。',
  '不规则深色石脚在本体，没额外围院或缺房接口；12点为11grunt和1captain。提案DUN03不规则错层窄守望塔，材料不直接迁为目标美术方案。'],
 'F03':[
  '一端高方塔连长条厅，另一端较低门廊，长厅两侧连续竖扶壁；整体单向长轴，与011-F03横厅被两处不等高尖顶穿入的十字组织不同。',
  '29×40×17，占用y0..39；长厅屋脊约y20，高方塔顶台约y29，旗杆延到y39；顶台与旗段分开，不称40格高厅。',
  '石质厚墙、连续扶壁与较高玻璃窗控制长厅节奏，高塔平顶垛口突出；虽像教堂形体，源为前哨，未凭外观宣称内部有已验祭坛。',
  '长厅深石双坡顶接一端露天方塔垛口，没有旧W008的高塔木坡帽，也没有011-F03的双尖顶；不能仅以换顶判独立，须结合厅宽/扶壁/塔端布局。',
  'dark_oak_planks385、stone_slab365、andesite_slab356、gravel307、tuff284、spruce_planks130、andesite_wall130、andesite_stairs91；原始台阶含屋顶与墙饰，不能全部当走道。',
  '无普通门；x4,z6及x4,z10梯y1..11，x6,z8梯y11..29，远端x25,z6/z10仅y1..3。补看y11/y29与主梯剖，较长梯证据不认证长厅地面至顶台所有转接净空。',
  '占地较紧贴长厅与高塔， gravel/tuff等构成地脚墙体；8点为7grunt和1captain。提案DUN03端塔连扶壁长厅，范围限定整个29×40×17组合，非大型城塞或中式殿堂。'],
 'F04':[
  '近多边围栏/石裙圈内是中央收分塔屋，正面带四叶斜置风车状轮面，底层和中层小室叠置；整体完整，但不能只因源目录outpost就当普通守望塔。',
  '27×35×27，占用y0..34，门层y2/y19，上部尖帽和旗继续升高；轮面横向扫幅占边界，不是房间净宽。',
  '石基、木框与外置叶片构成主立面，围栏院面较低；与旧old_home小住宅的双层塌顶和外梯没有同样的轮面/塔院组织。',
  '中央小尖坡帽，下部环缘和围栏院保持开放；轮叶的白羊毛与木条不是第二座建筑屋顶。',
  'stone_bricks299、spruce_planks249、cobblestone246、grass_block107、spruce_fence104、white_wool100、spruce_stairs95；白帆为羊毛，未验机械驱动或研磨设备功能。',
  '底门(13,2,16)，高门(11,19,13)/(15,19,13)；梯x12,z15仅y10..12，x13,z14为y14..19，中间y13转接未原生验。补看y9/y19及两梯侧剖，不称完整通顶。',
  '低围栏与草泥地裙完整包含，7点为6grunt和1captain。仅保留风车状塔屋与院的空间研究；未证实任务所需机械功能/用途，当前DUN03守望塔及DUN02工坊信用均不提案。']}
TARGET={'F01':'DUN03狭长错层守望塔遗址及外阶，18×38×25。','F02':'DUN03不规则错层窄守望塔，20×53×19。',
 'F03':'DUN03端塔连扶壁长厅，29×40×17；近长厅/钟塔家族需按主体差异复核。','F04':'风车状塔屋及低围栏院研究；用途/机械功能不符或缺证，不提案当前塔堡/工坊范围。'}
COMPARE=[('research-20261101-dungeons-002','F02-whole.png'),('continuation-20261022/references/whole-candidates-002','B004.png'),
 ('research-20261101-dungeons-002','F08-whole.png'),('research-20261101-dungeons-004','F03-whole.png'),
 ('continuation-20261022/references/whole-candidates','W008.png'),('research-20261101-dungeons-011','F03-whole.png')]
def ev(p):return dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def dump(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def main():
 s=json.loads((OUT/'sources.json').read_text());a=json.loads((OUT/'interface-audit.json').read_text());entries=[];states=[];actors={}
 for c in s['candidates']:
  i=c['id'];entries.append(dict(id=i,member=c['member'],nbt_sha256=c['nbt_sha256'],observations=dict(zip(FIELDS,NOTES[i])),
   proposed_target=TARGET[i],independent_design_basis=NOTES[i][0]+' '+NOTES[i][1],
   status='WINDMILL_PURPOSE_AND_FUNCTION_HOLD' if i=='F04' else 'SCOPED_WHOLE_TOWER_PROPOSAL_PENDING_FAMILY_REVIEW',
   images_actually_viewed=[ev(OUT/n) for n in c['images']+[i+'-details.png']],credit_proposal=int(i!='F04'),formal_credit_added=0,native_acceptance=False))
  with ZipFile(c['source_archive']) as z:
   d=read(z.read(c['member']));p=d.get('palette') or d['palettes'][0]
   states.append(dict(id=i,nbt_sha256=c['nbt_sha256'],stairs_doors_ladders=[dict(position=b['pos'],state=p[b['state']]) for b in d['blocks'] if p[b['state']]['Name'].endswith(('_stairs','_door')) or p[b['state']]['Name']=='minecraft:ladder']))
   for pool in next(x for x in a['entries'] if x['id']==i)['outgoing_pools']:
    for comp in pool['component_identities_only']:
     raw=z.read(comp['member']);cd=read(raw);cp=cd.get('palette') or cd['palettes'][0]
     actors[comp['member']]=dict(member=comp['member'],sha256=hashlib.sha256(raw).hexdigest(),size=cd['size'],entity_ids=[e['nbt']['id'] for e in cd['entities']],
      materials=dict(Counter(cp[b['state']]['Name'] for b in cd['blocks'])),images_viewed=False,building_credit=0,assembled=False)
 dump('manual-review.json',dict(entries=entries,counts=dict(templates_studied=4,new_images_actually_viewed=16,historical_images_reviewed_again=6,proposals=3,scope_held=1,formal_credit_added=0),
  historical_comparison_views=[ev(OUT.parent/f/n) for f,n in COMPARE],semantic_deduplication=[
   'F01最近dark_keep厚实体方堡连侧门堡；新为前后错层断墙台、外长阶和外露木长柱的废塔，没有旧主副厚块堡，不能以覆苔换材判断。',
   'F02最近B004腐朽地下寺为低方形集中残殿和矮顶室；新为53高的收腰错层窄塔/侧阳台，灰色分类不意味同材同用途。',
   'F03最近wither_keep为宽大近方城馆、双高角竖段和中央宽殿；新为窄长扶壁厅的一端单高平顶塔，空间组织不同。',
   '另看W008和011-F03：旧W008窄短厅连木帽高塔，011-F03横厅两处偏置尖顶；新长厅更长宽且扶壁/侧窗连续、端塔平垛。此作为整栋主体差异交复核，不把换屋顶当充分证据。',
   'F04最近old_home为低双层塌顶住宅外阶，新为中央塔屋+外置四叶风轮+低围栏院；独立形态不等于当前任务用途已经相近，故不提案。'],
  principles=['研究完整遗址的当前断墙与路径线索，不补想原来完整楼层或屋盖。',
   '结构材料的名字不直接等于建筑形态，蘑菇柄墙塔仍需看房层、入口和阳台。',
   '端塔长厅、十字厅带两尖顶和近方城馆需比较主体布局，不能只比较塔帽。',
   '风轮、旗杆及尖顶占用边界和房间净空分开，不以保存尺寸直接推楼层。',
   '原始长梯/短梯分段记录，遇转接空层保留不确定性，不凭图认证碰撞。',
   '完整但用途不合仍可保留研究，不挪入工坊或前哨数目凑门槛。']))
 dump('vertical-original-states.json',dict(entries=states,formal_credit_added=0,limits='Original identities and positions only; no game path certification.'))
 dump('actor-component-boundary.json',dict(entries=list(actors.values()),formal_credit_added=0,unresolved_pools=[],limits='Three 1×3×1 actor templates, no building credit or assembly.'))
 print('Four complete authored designs studied, three provisional tower proposals, one windmill-purpose hold; formal zero.')
if __name__=='__main__':main()
