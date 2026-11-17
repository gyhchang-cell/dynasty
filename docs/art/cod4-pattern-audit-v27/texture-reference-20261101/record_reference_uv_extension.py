"""Manual observations from all eighteen source-face sheets actually opened."""
from pathlib import Path
from datetime import datetime,timezone
import json
D=Path(__file__).resolve().parent
x=json.loads((D/'reference-uv-extension.json').read_text())
notes={
'archevoker-01.png':('armorHead六面透明；另三块帽体才含黑底、深灰宽折块、棕带和正面方金扣。帽檐up/down的负U被保留，不能把透明头层报成整顶帽子缺图。','先分清透明底层与独立帽层；金色只集中于扣件。'),
'archevoker-02.png':('胸外层north是两根金边开襟，背侧金线明显更短；另一层正面也是长金边，而旋转后摆只在下端有黑金小段。内衣north为灰褐衣襟、三个金扣，背面是大块横褶。','内衣、开襟与后摆分层；金边随职责变化，不能每面刷相同金框。'),
'archevoker-03.png':('裤腰正面仅下端方金扣，背侧主要黑棕带。左右袖主体是长黑面与下端一小条金边；右腕额外块为少数灰阶大折面，上下均为灰面。','大片暗衣保留低对比空间，浅金袖口和灰腕块分工。'),
'archevoker-04.png':('左腕灰块与右腕同大块组织。左腿黑长条底部才有金橙边；额外腿层只在顶部有棕布角，靴层只在低段留黑鞋块。','裤层与靴层的透明区承担覆盖，不能合并后推断整腿只有一个岛。'),
'archevoker-05.png':('右腿金橙下边与左侧相应，但north用负U。额外右腿部分面未定义，已有三面只在上部有棕布角；右靴与左靴同低段黑鞋和深底。','逐面记录左右镜像和未定义面；不把局部采样当三维接缝通过。'),
'pyromancer-01.png':('头层四侧只在下段有暗红带。两个零高帽檐块仅定义up，按各自旋转记录；采到的是黑灰破边大块，不能为未定义侧面补纹理。','平面装饰与有厚度体块分开处理；暗帽不必密铺亮线。'),
'pyromancer-02.png':('帽尖分段均用少量黑灰宽块。胸外层正面只有暗红领片与一点橙黄扣；内衣才是大面积红袍、棕腰带和大方金扣，背面无同样亮扣。','亮点有明确层和位置，不能按图集整体红黄主色把每个胸面刷满。'),
'pyromancer-03.png':('裤腰仅底部红带；右袖外片用暗红阶梯角形，内袖从暗红肩过渡到大块黑护臂。左袖对应外片使用负U，不能盲目复制同一朝向。','用少数边界清楚的大块区分红布与黑护件，不借模糊渐变。'),
'pyromancer-04.png':('左内袖和左腿主层均是黑底少数深灰折块；额外腿层只留下上段红布。左靴前面才有黄橙短斜扣，背侧基本全黑灰。','亮色集中于小连接物，靴背无需复用正面符号。'),
'pyromancer-05.png':('右腿/右靴沿用上述黑底、红上段与前黄扣的层次，north腿面为负U。右靴底用两块黑灰大面，未画细密装饰。','左右配对可共享节奏，但必须保留原UV符号与每面差异。'),
'netherite-01.png':('头盔是灰紫硬块、阶梯脸口和深暗边。普通hat0采样全透明，帽檐只有一像素窄框；hat2则只有下段宽块，上下未定义。','空图层与实际甲层分开；脸口透明有形状职责。'),
'netherite-02.png':('dyeHat四块采到白、粉、灰紫大块，大小层段不同，帽檐up/down为宽块环。这里只是未着色源像素，bone名含dye不能证明默认游戏是粉白色或已染色。','可染覆盖层必须另核运行时着色；不能依据原图直接更换主甲颜色。'),
'netherite-03.png':('裤腰是大灰紫下层。胸甲主面用几组较亮灰紫中央折块建立板片节奏；两侧倾斜短框只采到窄边和透明孔，左右未定义的内侧面不同。','暗金属也用宽明暗板片，不是整面噪点；框内空场不要填死。'),
'netherite-04.png':('普通胸外层north只两根细暗紫边，south为上下框；dyeArmorBody短侧片为粉白局部，而长外层为两条白粉襟边与背面宽纹，顶部仍留中心孔。','主甲、框边和可染覆层的像素职责不同，不把白粉大图集区域当金属高光。'),
'netherite-05.png':('左肩主块用灰紫十字大折面，附加短袖只在小片和角点有暗块；dye袖为少量宽白粉区。右肩沿对应大块组织但east/west明暗分布互换。','左右肩成对检查；不从平面同色认定镜像后接缝必然正确。'),
'netherite-06.png':('右短袖与可染袖延续局部块面。左腿普通主层只留上缘及低位短横，额外腿层只有上角和外侧短片；源cube高10却部分uv高11，记录差异，不擅自判原作者拉伸错误。','体块尺寸与UV尺寸分别记录；按真实像素面积安排细节密度。'),
'netherite-07.png':('左腿染色层是白粉宽色块，顶部留透明；左靴是低段灰紫壳与暗底。右腿普通层和附片与左侧相应，部分面方向和明暗有区别。','同一腿的普通壳、附片和染色层是一个装备的多个层，不拆成多个参考。'),
'netherite-08.png':('右染色腿层的白粉纹与左侧按面排列；右靴低段灰紫亮块与黑底保持，up透明而down为深色底面。','靴筒上透明不等同缺靴；最终还需核遮挡和运动中的穿插。'),
}
review=[]
for sheet in x['sheets']:
 observation,principle=notes[Path(sheet).name]
 keys=[f"{r['bone']}[{r['cube_index']}]" for r in x['rows'] if r['inspection_sheet']==sheet]
 review.append(dict(sheet=sheet,actually_opened=True,cube_keys=keys,observation_zh=observation,applicable_principle_zh=principle,new_design_credit=0,runtime_acceptance=False))
out=dict(recorded_at=datetime.now(timezone.utc).isoformat(),reviewer='same agent manual visual pass, not independent acceptance',
 models=3,cubes=len(x['rows']),defined_faces=sum(len(r['faces']) for r in x['rows']),
 signed_integer_crops=sum(f['status']=='SIGNED_INTEGER_CROP' for r in x['rows'] for f in r['faces']),
 undefined_cube_face_directions=sum(6-len(r['faces']) for r in x['rows']),
 fully_transparent_defined_face_samples=sum(f.get('alpha_nonzero_pixels')==0 for r in x['rows'] for f in r['faces']),
 source_pngs_reopened=3,source_pngs_exact_equal_previously_reviewed=True,new_design_credit=0,production_changes=0,
 limitations=['仅固定本地JAR资源的带符号面裁剪；没有Java槽位/染色分支、三维姿态、游戏或全目标验收。',
  '同归档/尺寸和同名只构成资源候选对应，不冒充运行时renderer到texture绑定。',
  '38处该cube未定义的方向、77个全透明已定义采样均不能独立报成作者bug；其他层可能承担外观。',
  '三张PNG与先前已看原图字节一致，仅补UV证据，不计新增美术案例。'],rows=review)
(D/'reference-uv-extension-manual-review.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='rows'},ensure_ascii=False))
