"""D25 actually viewed reference observations and conservative semantic dedup."""
from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 pages=[f'icons-{i:02}.png' for i in range(1,6)]+[f'worn-{i:02}.png' for i in range(1,4)]+[f'jinghui-{f}-assembly.png' for f in 'jrsy jrszj jrjyj jrtj jrtzj'.split()]
 review={'scope':'五套此前未读中式日常/军甲的整套原图与静态穿戴结构研究；不是贴图制作或游戏验收',
  'pages_actually_viewed':[{'path':p,'sha256':sha(D/p)} for p in pages],
  'observations':[
   {'semantic_group':'complete_straw_raincape_workwear','cases':['jinghui:jrsy'],'credit':'NEW_CONSERVATIVE_LEARNING_GROUP',
    'observation':'整套是宽阶梯斗笠、交叉绑带蓑衣、粗短片层袖、前后裙片与侧面绿色小竹器，双脚只是浅褐块。正背黑剪影都能读出蓑衣的层叠和下缘缺口；图标头为宽扁斗笠，胸是整段短外套，腿图包含长裙和侧挂，说明四件图标不是四张普通甲轮廓。原图128×128和geo128×128相符，143个cube分布八护甲根。新增1保守蓑衣装束学习组，不把斗笠、外套、裙、挂件另计设计。',
    'application':'可用于竹/布/海丝等目标判断材料编织方向和系带的大分区，长袖/短袖须按目标原生UV决定。参考衣片细密、图标高分辨率渲染且靴主体像矩形，均不作为Dynasty成稿规格；不复制斗笠、挂件或像素。'},
   {'semantic_group':'samurai_plate_variants_conservative','prior_group':'samurai_plate_variants_conservative','cases':['jinghui:jrszj','jinghui:jrjyj'],'credit':'APPEND_TO_PRIOR_GROUP_ZERO_NEW_DESIGNS',
    'observation':'士卒甲紫色双折帽、绿胸与浅黄短肩、棕甲裙白边、黄裤黑鞋，侧背仍以粗绿块区别甲片；头图甚至混入橙绑带，故不能照着图标当标准helmet轮廓。寒铁甲为低黑圆檐帽配小红顶、银灰胸板、黑短肩与长护臂、三片下摆黑筒靴；灰格与黑边在图标和穿戴图一致，不将灰格误称当前游戏缺图。二者几何123/115cube而非逐像素同图，但已有片甲族涵盖该类肩/裙/绑带组织，只追加学习，不因材料名称加独立信用。',
    'application':'对照绿色布底/棕甲裙及黑灰铁甲，学习主材与衬底区别、腰裙到裤子的连续；不把密小格直接照搬成MC像素噪点。jrszj纹理256×256、geo128×128是2倍纹素密度，不是自动UV错误；jrjyj128×128对应128网格。'},
   {'semantic_group':'samurai_plate_variants_conservative','prior_group':'samurai_plate_variants_conservative','cases':['jinghui:jrtj','jinghui:jrtzj'],'credit':'APPEND_TO_PRIOR_GROUP_ZERO_NEW_DESIGNS',
    'observation':'烫金灵铜甲红顶羽、金面甲与深褐围面、金甲红中央带和两长侧护裙，背面是大金板；玄黑灵铁甲用黑灰包颈盔、金额带、灰直胸、金腰结和黑侧摆。软件正/45/侧/背/剪影可见两者共享甲裙与宽肩类别但细部体块不相同，154/145cube不是额外设计数量。两者加入原片甲族而非以金/铁再分两个新组。图集与geo均256×256，实际8个护甲根均有cube或后代。',
    'application':'用深衬、金边和红带的面积比解释金属身份，尤其侧面和背面要继续有材质分区；Dynasty将军/铜铁甲的长袍需求须单独保留，不能把L2全长衣摆统一删掉。参考肩冠和长裙过大、图标像成套人台部件，不能当原版比例模板，也不照搬冠与绶带。'}],
  'native_bindings':{'names':5,'item_models':20,'item_icons':20,'native_atlases':5,'geo_models':5,'animations':5,'native_classes':26,'additional_geckolib_classes':2,'four_slot_chains':20,'geometry_cubes_read':680,'software_assembly_sheets':5},
  'dedup_limits':['五套名称不是五个新独立设计；新增1组只是保守学习组','同设计四槽、八骨根、680体块、2倍图集密度和五个角度均不重复计数','当前211既有学习组含局部/变体/反例，继续保持已验独立完整设计总数未知','高分辨率渲染图标不适合直接作原版甲轮廓范本；实际参考是材料分区、甲裙/袖片逻辑和正背连续'],
  'runtime_limits':['软件组装不是实机穿戴，未验槽位显示、动画、行走、接缝','固定GeckoLib4.8.4用于解读，不声称外部整合包实际依赖相同','D2五套袖盖、五套旧L2和三套材质问题仍待制作，精致/认可稿保护'],
  'new_names':5,'new_learning_groups':1,'new_validated_independent_design_credit':0,'new_artwork':0,'production_changes':0,'game_starts':0,'checklist_deletions':0,'reference_gate_met':False}
 (D/'semantic-review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n');print('D25: five source designs reviewed; one conservative learning group, no validated independent gate credit.')
if __name__=='__main__':main()
