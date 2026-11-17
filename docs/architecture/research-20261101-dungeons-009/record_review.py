#!/usr/bin/env python3
"""Four actual fort studies, including semantic scope and route limitations."""
import hashlib
import json
import sys
from pathlib import Path
from zipfile import ZipFile
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
sys.path.insert(0,str(ROOT/'tools/architecture'))
from nbt_read import read
FIELDS=['layout','proportion','facade','roof','materials','circulation','terrain']
NOTES={
 'F01':[
  '砂岩残墙围出开放小院，侧边低房与对角两处较高棚台组合；不是一座大实心堡。完整围院一次，不把两棚、平台和房间各计一例。',
  '35×18×30，占用y0..17，普通门y1、上平台门y6；较高棚台与低墙院分主次，远低于旧48盒、实际39格的双高塔。',
  '砂岩墙垛、突出木构件和不规则残缺外沿，敞棚与低房门洞尺度分开；石块零散裙边不是密封外城墙已验。',
  '两处较高方形低坡棚盖加零散低屋面；灰色屋盖含浅灰/灰羊毛与地毯，不应把分类灰投影都称石瓦或石楼板。',
  'sand641、oak_planks556、cut_sandstone426、smooth_sandstone350、oak_slab201、sandstone_stairs156；light_gray_carpet65、light_gray_wool45、gray_wool32参与轻屋盖/内装。',
  '底门三处y1、上门三处y6；x10,z11梯y6..10连续，补剖见约y5/y10木层板与两棚分离。仅证明局部上行，不认证院地—所有棚顶可通行。',
  '模板自带砂地与残石外裙，14个接口全为实体池，不缺14间房；来源base_plate名称不否定本体全院。提案DUN03低双棚守备围院，不能计入旧双高塔、单角塔L厅或四低棚范围。'],
 'F02':[
  '高低两座方塔由窄桥连接，低塔外伸门廊，整体沿一条狭长轴展开；不是对称两塔加宽院的旧双高塔布局。',
  '26×23×10，占用y0..22，桥与两塔门在y7；窄厚10格，最高塔与较低塔有明显主次，不当48格宽的厚堡或大城门。',
  '红砂岩厚塔墙、少量窄缝与屋缘石饰，低塔门廊以柱支起小檐；黄色分类墙实际上主要是红砂岩。',
  '两塔砖坡帽、较高塔腰部一圈外挑檐，低塔前有小门廊顶；与旧双高塔垛口平顶和多重横带完全不同。',
  'smooth_red_sandstone302、red_sandstone293、brick_slab189、oak_planks156、oak_stairs73、brick_stairs64；小屋盖与腰檐是砖构件，不是普通红木贴图。',
  '底门(1,1,5)，桥两门(8,7,5)/(17,7,5)；高塔x20,z4梯y7..18连续，补剖见约y6/y13/y19层板。木阶与平台存在，不替代完整原生碰撞和通顶验收。',
  '入口台阶及柱脚在模板内，无额外房间拼图池，7接口全为实体。提案DUN03狭长高低双塔连桥哨站；用途相近但尺度/桥式布局需独立验收，不直接给既有双高塔范围加数。'],
 'F03':[
  '方形金字塔外壳内底层十字通道分四区，上有中央木平台和较小顶室；是单体营房式金字塔，不是有角塔的露天守备院。',
  '23×13×23，占用y0..12，四底门y1、上平台约y5；屋盖大幅收进占主高度，不把每级退台当楼层。',
  '红砖斜向阶层包四面入口，墙外照明与浅饰条对称；外观看似整块金字塔，底部实际有分区和贯穿通道。',
  '整体四面收进砖质阶梯盖，中心较高，十字轴端局部开口；不是低四棚、双塔帽或单角高塔屋盖。',
  'bricks1013、oak_planks367、brick_slab116、brick_stairs109、oak_wall_sign21、gray_carpet19；黄色点有wall_torch，不按颜色当金属构件。',
  '四门在x/z两端，中梯x11,z10仅y1、3、5三格，中间y2、4缺梯。补剖保留此实际状态；不能称连续五格梯，也不能据图直接断言游戏绝对不可攀登。',
  '模板含平底，无待接房间，6接口均为实体池；只留金字塔式营房分区研究。与当前三类前哨目的/布局不同，不给已有范围加数，未提出本批完整前哨范围提案。'],
 'F04':[
  '三处方形角塔与一条低侧楼由围墙/廊段围开院，一塔高出其余并带竖旗杆；不同于单角高塔加L厅或四处等低棚。',
  '29×21×28，占用y0..20；主要屋面多在约y10/11，较高塔帽约y15，上段细杆到y20不是又一层可用塔室。',
  '红砖墙、木带和较窄门窗，被草叶/蛛网局部覆裹；覆绿主要影响外沿，不当作新的承重结构或换色新建筑证明。',
  '三方塔低坡帽配灰边，低侧楼较长双坡顶，连接墙廊更低；屋盖含云杉板/半砖、地毯与活板，不将灰边全称天然石瓦。',
  'bricks1223、spruce_slab378、spruce_planks283、dirt201、spruce_trapdoor189、dark_oak_planks188、grass_block167、mangrove_leaves158；叶层不能遮过门口/柱脚检查。',
  '底门(18,1,8)、上门(8,5,6)/(17,5,5)；主梯x24,z14,y1..10连续，另梯x20,z17仅y5/6。补剖见顶帽与低楼高差，未认证全院绕行或所有塔可达。',
  '草土地裙和局部残砖在本体，8接口全为实体池，两个队长点仍不是两座堡。提案DUN03三角塔连低侧楼守备围院，只学该规模布局，不把覆绿当旧单角L厅的计数依据。'],
}
TARGET={
 'F01':'DUN03低双棚守备围院；35×18×30，无双高塔或四低棚范围自动信用。',
 'F02':'DUN03狭长高低双塔连桥哨站；26×23×10，与既有双高塔用途相近但尺度/桥式布局需单独验收。',
 'F03':'单体金字塔营房分区与非连续梯研究；不提案当前三类前哨参考。',
 'F04':'DUN03三角塔连低侧楼围院；29×21×28，不自动并入单角高塔L厅或低四棚范围。',
}
COMPARE=[('research-20261101-dungeons-003','F01-whole.png'),('research-20261101-dungeons-003','F05-whole.png'),
 ('research-20261101-dungeons-003','F09-whole.png'),('research-20261101-dungeons-002','F14-whole.png'),
 ('continuation-20261022/references/whole-candidates','W008.png')]
def ev(p):return dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def dump(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def main():
 s=json.loads((OUT/'sources.json').read_text());entries=[];states=[]
 for c in s['candidates']:
  ident=c['id'];assert len(NOTES[ident])==7
  entries.append(dict(id=ident,member=c['member'],nbt_sha256=c['nbt_sha256'],
   observations=dict(zip(FIELDS,NOTES[ident])),proposed_target=TARGET[ident],
   independent_design_basis=NOTES[ident][0]+' '+NOTES[ident][3],
   status='SCOPED_WHOLE_FORT_PROPOSAL' if ident!='F03' else 'PYRAMID_BARRACK_SCOPE_MISMATCH',
   images_actually_viewed=[ev(OUT/n) for n in c['images']+[ident+'-details.png']],
   credit_proposal=int(ident!='F03'),formal_credit_added=0,native_acceptance=False))
  with ZipFile(c['source_archive']) as z:
   d=read(z.read(c['member']));pal=d.get('palette') or d['palettes'][0]
   selected=[dict(position=b['pos'],state=pal[b['state']]) for b in d['blocks'] if pal[b['state']]['Name'].endswith(('_stairs','_door')) or pal[b['state']]['Name']=='minecraft:ladder']
  states.append(dict(id=ident,nbt_sha256=c['nbt_sha256'],stairs_doors_ladders=selected))
 dump('manual-review.json',dict(entries=entries,counts=dict(templates_studied=4,new_images_actually_viewed=16,
  historical_images_reviewed_again=5,proposals=3,scope_held=1,formal_credit_added=0),
  historical_comparison_views=[ev(OUT.parent/f/n) for f,n in COMPARE],
  semantic_deduplication=['F01/F04与最近旧maya均不同：旧maya为大分层四面退台和内部双小祭室，新例为低双棚残院、三方塔连长低侧楼开院，不是旋转换材。',
   'F02与最近旧W008不同：旧为单高钟塔连短低厅，新为高低双方塔连窄桥且双砖坡帽。',
   '与003三份正式例实际对照：旧双高平顶塔/单高角塔连L厅/四低棚，均不与本批低双棚、狭长双塔桥、三塔低楼院完全同家族。用途接近也不自动迁入信用。',
   'F01与F04虽都是小围院，但前者两较高轻棚配多层砂岩残墙，后者三个砖角塔加独立低长楼；差异在空间组织、层高和屋盖，不是覆绿或颜色。'],
  principles=['先检查完整base_plate的实际房间和外接池，名字不证明只是地板碎片，也不证明已完成。',
   '将主塔、辅助塔、廊桥、低侧楼和院落的分工区别观察；整个组合算一个参考。',
   '墙裙、羊毛/地毯棚盖、砖坡帽和绿叶层分别核对材质；分类灰色不能全部读作石。',
   '高处旗杆、屋脊和空盒都不增加可用楼层；尺寸记录与有效空间分别说明。',
   '连续梯与隔格梯按原始状态记录，局部梯不等于完成全塔/全院路径验收。',
   '实体池中的队长、掠夺者和卫道士不是缺房或额外建筑，不按接口/生成权重拆数。']))
 dump('vertical-original-states.json',dict(entries=states,formal_credit_added=0,
  limits='Original stair/door/ladder identities and positions only, not terrain/collision/path certification.'))
 print('Four actual fort studies, three scope-specific proposals, one purpose/layout hold; zero formal credit.')
if __name__=='__main__':main()
