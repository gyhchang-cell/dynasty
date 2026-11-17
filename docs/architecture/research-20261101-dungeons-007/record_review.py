#!/usr/bin/env python3
"""Seven-aspect observations from 32 actual new views and four comparator views."""
import hashlib
import json
from pathlib import Path
OUT=Path(__file__).resolve().parent
FIELDS=['layout','proportion','facade','roof','materials','circulation','terrain']
NOTES={
 'F01':[
  '长方主室沿两端和一侧布书架，另有小门廊、侧门与两处讲台；完整书屋一次，不按门数或讲台拆分。',
  '13×15×16，宽坡顶占上部较多高度，书架主要y1..3；不是十五格净高的多层藏经塔。',
  '原木浅墙分格，长侧窗和四处不同木门界面；外部细高竖件含竹，不全是石柱。',
  '单条长主脊配宽出檐及低门廊檐，屋盖高空腔不等于可用阁层；与旧海底寺同心四边退台组织不同。',
  'deepslate_brick_stairs117、stripped_cherry_log98、oak_planks82、deepslate_bricks76、calcite40；普通书架22、雕纹书架5、讲台2。',
  '四门均y1，书架集中z4、z9附近和x8侧，讲台(6,1,6)/(7,1,12)；y3/y7补平面区分底层书架与上方空腔，无梯子，不宣称阁层可达。',
  '草地小台基，唯一minecraft:empty标识处于建筑入口，当前归档无其JSON；本体无待接房间，可提案小型藏经用房空间，不能当整寺或中式风格已合格。'],
 'F02':[
  '方形低层书屋偏一角上叠小高室，低屋环绕上室，和F03低长屋不同；不是同名沼泽书屋简单换材。',
  '13×22×13，入口y4、下层书架y4..6，上室书架y11/12，尖顶到y21；高尖顶不能全作可用层数。',
  '木框、藤蔓与较低侧檐围合底层，窄高室少窗；藤蔓不作已验攀爬梯。',
  '低层平缓檐上起窄高坡帽，上下屋盖主次明显；不是四角同高塔或大圆殿屋盖。',
  'oak_log158、spruce_trapdoor107、spruce_planks86、spruce_slab86、vine85；普通书架15、雕纹书架3、讲台3。',
  '门(5,4,3)，x9,z8梯y4..10连续，补剖见上室约y10层板及书架；仅证明模板内梯段，不认证从地面上门或柱基承托。',
  '十一处朝下接口指向trek:feature/block_column/oak_log，当前归档没有同路径池或对应配置；另两处入口空标识、两处村民池。柱基缺证，整例保留待核，不按完整落地书楼计数。'],
 'F03':[
  '低长形主室配偏侧短入口台，书架集中室内两端和一侧；与F02方底窄高室是不同布置，但不能据此忽略柱基依赖。',
  '8×8×11，入口y3、地板约y2，屋顶到y7；只有低主室，没有F02式高层小室。',
  '深木墙、栅栏与短门台，底部紫红点为原始接口，不是实际完成的桩脚。',
  '低木坡屋盖包长室，局部横脊外挑；没有独立高塔帽或大型平台屋面。',
  'dark_oak_log76、dark_oak_planks69、dark_oak_fence25、stripped_dark_oak_log18；书架11、讲台1。',
  '门(1,3,5)，书架与讲台位于y3/4；补剖显示单室内部与下方未支撑边界，无梯子，也未组装进入平台的外部路线。',
  '九处底接口指向dark_oak_fence特征池，另有一个入口空标识；池内嵌向下高度63的柱特征及更新器，不是九栋建筑。未组装柱基，不提出完整落地建筑参考。'],
 'F04':[
  '9×9方基四外柱包一个内方室，与旧W018寺庙同外轮廓、同门(2,2,4)；改成书架内装不另算独立建筑设计。',
  '9×10×9，相较旧9×13×9主要减一层屋盖；不能以较矮尺寸把同家族算成新设计。',
  '浅墙、原木框和低基座保持旧寺庙布局，东墙两列书架夹讲台；方室其余侧留进入空间。',
  '同分层收进四坡檐，旧三层变两层，角端灯饰相近；屋盖层数变化不足以另添一个独立参考。',
  'deepslate_brick_slab67、deepslate_tile_slab44、stripped_spruce_log35、calcite34；书架6、讲台1，和旧酿造台/箱内装不同。',
  '门(2,2,4)，书架在x5,z3/5的y2..4，讲台(5,2,4)；补剖证实低方室，未把屋顶叠层称多层可用楼阁。',
  '朝街道接口及村民实体池分别记录，村民池未在当前归档内，不据此判运行失败。因历史设计家族重复排除独立信用，不给另一个地牢再复制一份。'],
 'F05':[
  '紧凑单室两端各排三列三层书架，中段留通路和讲台，侧门进入；整座小书房一个候选。',
  '7×7×9，墙顶竖件和女墙高于低平屋面；不称多层高塔或大藏经阁。',
  '红砂岩围墙、小侧窗与木门，长侧简洁，书架作室内两端墙；灰色架子不是石堵墙。',
  '低平屋盖配高一点的端部墙和边角装饰；与旧rustic_temple的高砖尖帽、塔饰和坡顶不同，不是换色高寺。',
  'smooth_red_sandstone64、cut_red_sandstone28、red_sandstone23、dark_oak_planks20；书架18、讲台1，分类黄块不表示普通黄色砂岩。',
  '门(1,1,4)，书架在z1/z7、x2..4、y1..3，两端夹中段操作区；补剖见低净空单室，无梯，不推断屋顶可上。',
  '小屋底部接入口空标识及针叶林村民池，没有待接侧房；提案DUN07小型典籍书室的架—路比例，不代表三岛仙观或中式屋面。'],
 'F06':[
  '长条双功能主室，左侧藏书、右侧制图，中央上起窄藏书阁室；整个长屋与上阁一个设计，不按功能拆两例。',
  '17×13×9，主入口y4，中央书架上阁在y8..10，两端低屋与中央较高短脊相区别。',
  '深木骨架、白墙和高石基，前后有入口台阶；窄中央高窗与两端房窗尺度不同。',
  '两端长低坡顶夹中央较高横脊，灰屋盖大量为白桦木台阶；不是中间实心高塔。',
  'cobbled_deepslate167、dark_oak_log136、birch_stairs108、white_concrete88；书架24、制图台1、讲台1。',
  '四门均y4，两内门分区；x8,z3梯y4..7连续，上阁x7/x9两列三层书架夹细通道。补剖见约y3/7楼板，未认证狭阁原生碰撞。',
  '模板含较高基座和短入口台阶，不依赖外接支柱；一处入口空标识及三处村民池接口不是四缺房。提案DUN07小藏书阁与附属工作室，不宣称已实现炼丹或隐藏机关。'],
 'F07':[
  '长条书舍中部向侧面伸短入口厅，形成T形，主空间两端设书架，中段有讲台；完整单座书屋一次。',
  '14×40×21保存盒，但实际最高y14，主体只有十五格占用高度；上方二十五格空白不是高塔或额外楼层。',
  '浅墙、木竖框与窄窗围长书室，短翼入口两侧有灯；庭边叶片与草地不当室内支柱。',
  '长主脊和短入口横脊相交，主顶较高，檐口低展；补剖中屋顶内腔与底层书房分开。',
  'spruce_stairs184、oak_planks114、cyan_terracotta98、stone_brick_stairs87与stripped_oak_log64；书架18、讲台2。',
  '门(11,2,10)，主要书架在x2/x6、z2/z18等处，讲台(2,2,8)/(2,2,11)；y4平面见T形主室与入口厅，无梯，未把屋盖空腔当可登阁层。',
  '草泥底裙、两个村民池接口及一个道路池接口，不缺书房翼；提案DUN04小型T形藏经用房组织，不当40格高藏经塔或完整悬崖寺院。'],
 'F08':[
  '数个低房与一侧长屋围中央开院，多房中分别安讲台、端墙书架和储物，整组藏书院一个候选，不按三块或四块屋顶拆数。',
  '19×12×23，低房多约y2..6，局部高屋顶/棚到y11；是小院组群，不是12层殿塔或完整地下城。',
  '浅砂岩厚墙配小侧窗、不同侧门和部分栏边，长屋比短房高；露天院和封闭书室界面有区别。',
  '多组低平顶围院，一角有较高木棚/小顶，平顶女墙局部抬起；不套作连续四坡中式殿顶。',
  'cut_sandstone904、cut_sandstone_slab174、spruce_fence102、gray_concrete_powder70等；书架26、讲台2，粉末块稳定性未验。',
  '门在y2与y3，右侧长房z21端墙书架跨y1..5，左端小室书架在x2/3,z2；补剖定位中央院与各室高差，无梯不等于全屋无阶，未原生验全院可达。',
  '沙地完整院组；两个道路池接口、两个原版村民点及三个幼年村民点，共七接口，不把实体点当缺房。只提案DUN04多室小藏书院，不代表崖壁、千佛崖或整寺。'],
}
PROPOSE={'F01','F05','F06','F07','F08'}
TARGET={
 'F01':'DUN04单层小型藏经用房；13×15×16，书架与讲台及多入口关系，不包含整寺/悬崖/中式风格验收。',
 'F02':'沼泽高脚小书楼上部研究；柱基池缺证，不提出完整建筑信用。',
 'F03':'低高脚书屋室内与柱特征研究；未组装支柱，不提出完整落地建筑信用。',
 'F04':'旧W018的改屋顶/内装同家族，排除独立设计计数。',
 'F05':'DUN07小型单室典籍房；7×7×9，不覆盖藏丹塔或三岛仙观。',
 'F06':'DUN07窄藏书阁加附属工作室；17×13×9，不覆盖炼丹/机关/整观。',
 'F07':'DUN04 T形小书舍；14×40×21保存、实际高15，不覆盖高塔或整寺。',
 'F08':'DUN04低层多室小藏书院；19×12×23，不覆盖悬崖大寺/千佛崖。',
}
COMPARISONS=['continuation-20261022/references/whole-candidates/W018.png',
 'continuation-20261022/references/whole-candidates/W018-plan.png',
 'continuation-20261022/references/whole-candidates/W015.png',
 'continuation-20261022/references/whole-candidates-004/D008.png']
def evidence(p):return dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def main():
 s=json.loads((OUT/'sources.json').read_text());entries=[]
 for c in s['candidates']:
  ident=c['id'];assert len(NOTES[ident])==7
  entries.append(dict(id=ident,member=c['member'],nbt_sha256=c['nbt_sha256'],observations=dict(zip(FIELDS,NOTES[ident])),
   independent_design_basis=NOTES[ident][0]+' '+NOTES[ident][3],
   images_actually_viewed=[evidence(OUT/f) for f in c['images']+[ident+'-details.png']],
   status='SCOPED_WHOLE_BUILDING_PROPOSAL' if ident in PROPOSE else 'HISTORICAL_DESIGN_FAMILY_VARIANT' if ident=='F04' else 'HELD_FOUNDATION_DEPENDENCY',
   proposed_target=TARGET[ident],credit_proposal=int(ident in PROPOSE),formal_credit_added=0,native_acceptance=False))
 review=dict(date='2026-11-01',entries=entries,
  method='Actual manual study of 32 new whole/plan/vertical/detail images and four historical comparator images; original fittings, door/ladder states and outgoing dependencies inspected.',
  historical_comparison_views=[evidence(OUT.parent/p) for p in COMPARISONS],
  counts=dict(templates_studied=8,new_images_actually_viewed=32,historical_images_reviewed_again=4,proposals=5,historical_family_exclusions=1,foundation_held=2,formal_credit_added=0),
  scope_boundary='Five purpose/scale-specific proposals. Do not sum into DUN04 or DUN07, apply to both, transfer old mortuary148, or count roof/room/fittings as separate designs.',
  principles=['先用原始书架、讲台坐标区别内装与墙体；书架数量不等于可读/可达书籍数量。',
   '单室、T形书舍、狭阁双功能长屋与围院组群各有不同进出和取书路线，不用一套屋顶替代用途观察。',
   '保存盒高40格而占用仅15格时保留两项尺度，不把空白当藏经塔。',
   '历史同家族改一层屋盖或更换内装仍须排除，原文与角色几何不同不是新设计证明。',
   '道路、实体、空入口标识和支柱特征区别记录；支柱池缺证或未组装不能装作已落地。',
   '村庄书屋只提供相应用房原则；不以日式或欧式参考研究冒充整座中式佛寺、道观制作完成。'])
 (OUT/'manual-review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
 print('Eight seven-aspect reviews / five separate proposals / one historical family excluded / two foundation holds / zero credit.')
if __name__=='__main__':main()
