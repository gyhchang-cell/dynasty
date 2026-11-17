from pathlib import Path
import json,hashlib,runpy
from PIL import Image
r=Path.cwd();H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();finish=runpy.run_path('/tmp/armor-finish-common-v3.py')['finish']
obs={
'abyssal':[
'轮廓：黑紫护甲用短阶晶角、上扬肩端和分叉靴形成识别；头冠是同套开放头部变体，不能单独计套数。原图实际查看，不从名称臆测形状。',
'比例：胸8×13×4、头8×9×8保留方块人基础体积；两臂4×12×4附10×10零厚肩片，靴4×12×4附4×10零厚饰片，凸出来自专用几何而不是放大图标。',
'材质：深紫黑大块承底、洋红和近白晶亮簇点亮边缘；PNG仅0/255透明度，近白是晶体主体，不能当白底清除。亮色不证明自发光。',
'像素：亮簇集中于面罩下角、肩端和腿靴局部，主体有暗面余量；阶梯硬边，不把每个轮廓像素变成独立细线。',
'留白：头冠留空中央和两侧，盔和冠各自独立64×64原图；腿靴原图横排片区不是头脸。通用裁片页仅位置上下文，具体解剖标签不适用于这些专用图集。',
'槽位与UV：四槽及同套头冠原生工厂→EquipmentSlot→initializeClient→IClientItemExtensions模型字段→直接纹理路径已逐项保存；ABYSSAL_ARMOR层指向ModelAbyssalArmor.createBodyLayer。各件独立64×64，不能套layer1/layer2。',
'适用与去重：可学基础方块体积内以肩片和晶角建立强甲身份；专用零厚平面需双面和姿态实测，不能照抄像素。既有家族沿用，尚未完成整套语义独立验收，新增信用0。'],
'terrible':[
'轮廓：暗青壳搭青白尖簇，盔冠两侧宽尖、胸肩上扬、靴外侧晶片分工明确；不是在普通甲上单纯换蓝色。',
'比例：头基体8×8×8、胸8×12×4、肢体4×12×4；头饰16×11零厚片，肩8×10零厚片，保持主件体量，饰片不等于厚实实体角。',
'材质：深青大块与青色亮簇形成壳和尖刺的边界，近白只占局部亮块；所有图标/穿戴原图alpha仅0或255，无原生PNG半透明证据。',
'像素：晶亮沿头和臂外缘逐阶展开，胸有明确深色中线与亮块分区，背面不靠密纹填满；可借鉴局部明暗而非全身柔光。',
'留白：面口黑区与透明裁口区别保留；原始图集未用部分透明。通用原版裁片标签在本套不成立，只作为原始矩形背景，不能据此判断缺面。',
'槽位与UV：裤装包装器实际仅选left_shoe2/right_shoe2，不选构造器出现的body2；鞋选left_shoe/right_shoe。四槽各有独立64×64原图，TERRIBLE_ARMOR层直接指向专用createBodyLayer。',
'适用与去重：应学原版比例主体加少量阶梯轮廓，但这些额外平面需姿态/有符号面/接缝核查。整套家族既有记录不清零，不因四槽补全新增设计数，信用0。'],
 'three-bolt':[
'轮廓：铜棕封闭潜水盔、灰白套服、暗靴形成工艺装备身份；图标仍是四件护甲而非小人物插画。',
'比例：头8×8×8加独立顶盖和通气小块，胸8×12×4、臂腿4×12×4；背部两只4×10×4箱体提供设备厚度。窗口相关盒体是分组局部坐标，不能未计算姿态就宣称最终朝向。',
'材质：铜棕边框、灰白衣料与近黑面窗三种主体分工清楚；灰白大块是套服而非背景。全部原图alpha仅0或255，不能称玻璃半透明。',
'像素：铜边阶梯和衣料横向明暗带保留较大色簇，头部面窗大片深色，低频结构比细金线更接近MC。',
'留白：双腿、双靴分开，透明槽隙不补底；头盔原始图集的面窗在图标和模型中不同区域，不用通用layer裁片当确切UV验收。',
'槽位与UV：注册胸件three_bolt_suit的实际穿戴路径是three_bolt_chestplate.png；四包装器按head/body+双臂/leggings_body+双腿/双靴选原生字段。模型层THREE_BOLT_ARMOR指向ModelThreeBoltArmor.createBodyLayer，64×64独立图集。',
'适用与去重：可借鉴设备用途决定外形和低频明暗，不能只复制原版铁甲换铜色；窗口姿态和背箱穿戴遮挡仍待验，独立语义去重未完成，新增信用0。']}
prior='armor-neptune-whole-20261114';state='D118_NEPTUNE_NATIVE_WHOLE_REFERENCE_SAVED'
for key,num in [('abyssal',119),('terrible',120),('three-bolt',121)]:
 b=r/'docs/art'/f'armor-aquamirae-{key}-whole-20261114';assert not list(b.glob('bounded-receipt*'));put=lambda n,x:(b/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n');p=json.load(open(b/'provenance.json'));a=[]
 for e in p['entries']:
  if e['entry'].endswith('.png'):
   im=Image.open(b/e['local']).convert('RGBA');h=im.getchannel('A').histogram();a.append({'source':e['local'],'sha256':e['sha256'],'size':im.size,'alpha_histogram':{str(i):n for i,n in enumerate(h) if n}})
 put('alpha-inventory.json',a)
 dims=dict(zip(['silhouette','proportion','material_identity','pixel_clusters','negative_space','slot_uv_consumers','applicability_dedup'],obs[key]));put('seven-dimension-mc-review.json',{'dimensions':dims,'dimension_count':7,'case':p['case'],'new_validated_credit':0,'scope':'native originals and direct custom model static contract; not runtime'})
 models=[]
 for e in p['entries']:
  if '/models/item/' in e['entry']:
   q=json.load(open(b/e['local']));models.append({'source':e['local'],'data':q})
   for v in q.get('textures',{}).values():
    ns,path=v.split(':');assert (b/'source/assets'/ns/'textures'/(path+'.png')).exists()
 put('native-icon-model-binding.json',models)
 put('native-acquisition-data.json',[{'source':e['local'],'data':json.load(open(b/e['local'])),'scope':'native recipe/loot declarations only; no obtaining executed'} for e in p['entries'] if '/recipes/' in e['entry'] or '/loot_tables/' in e['entry']])
 bindings={'static_chains':'native-slot-texture-model-chains.json','layer_factory':'native-layer-definition-chain.json','custom_geometry':'native-geometry-literal-study.json; literal extraction only, not VM or final transforms','uv_warning':'raw-uv-scope-correction.json; generic anatomical crop labels NOT valid custom UV face claims','color':'native-alpha-inventory has only0/255; actual render type, fullbright, global tint and overrides remain unvalidated','source_version':'native mods.toml MC1.19.2 Forge43.2.0+ obscure_api15+; not claimed compatible with Dynasty1.20.1','source_closure':'direct native factories, slots, PNG texture selection and custom model fields read; runtime/dependency/global consumers incomplete => HOLD0 for full acceptance','seven_dimensions':'seven-dimension-mc-review.json','new_validated_credit':0}
 pending=['完整整套语义去重与1000适用设计总数核定','专用模型层事件实际激活、ObscureAPI和全局渲染影响未完整闭合，HOLD0','自定义模型最终旋转/有符号面/双面/接缝和五视图未实机验收','28现有Dynasty甲件无新增未重画且简陋目标证据，不准据此覆盖','泛用裁片不是专用穿戴UV验收']
 status=f'D{num}_AQUAMIRAE_{key.upper().replace("-","_")}_NATIVE_WHOLE_REFERENCE_SAVED';finish(b.name,prior,f'D{num}',state,status,'latest_aquamirae_'+key.replace('-','_')+'_whole',obs[key],bindings,pending);prior=b.name;state=status
