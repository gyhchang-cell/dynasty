"""Observed all seven analysis pages; template color/material variants get no new groups."""
from pathlib import Path
from datetime import datetime,timezone
import json
D=Path(__file__).resolve().parent
def row(group,cases,observation):return {'semantic_group':group,'prior_group':group,'cases':['macabre:'+c for c in cases],'observation':observation,'credit':'APPEND_TO_PRIOR_GROUP_ZERO_NEW_DESIGNS'}
rows=[
row('organic_flesh_rib_armor_family',['baal_armor','blood_clot_armor','gargamaw_armor','gomoria_armor','morphegor_armor','valamon_armor'], '六套头盔同为分叉眉骨/暗面孔、V领双肩开口胸、窄腰腿和L靴模板，主要改变米骨、暗红、粉肉、灰青、半白半暗、棕骨配色。保守合并已有有机肉肋族，六套不新增独立设计。原生图集中Baal/Valamon的骨米色、Gargamaw粉红与黄色附属岛、Gomoria灰青与粉紫岛、Morphegor浅粉与深红片、BloodClot普通64×32暗红筋理分别可读；图集附属岛不是独立设计，不因更高复杂度就照搬。只学骨肉主面与凹陷暗线的区别，避免每块像素都描边和白肉高光铺满。五个GeoModel返回具体纹理/模型/动画路径已保存，但尚未证运行时物品注册到该渲染器的全链，不把静态返回当实机。'),
row('organic_flesh_rib_armor_family',['abhorrent_armor'], '绿皮主面配米黄色大斑，短盔一块黄额、胸两肩和中间斑点连向腰、腿靴外侧浅块，追加有机材料同族。静态分槽getArmorTexture明确选dun__layer_1/2，名称不同但不是缺纹理。原生层主面密黄块接缝可见；借鉴有限配色，但腐肉斑点应有大区而非满屏撒噪点，不直接用于普通布甲。'),
row('organic_flesh_rib_armor_family',['skinsuit','symbiotic_armor'], 'Skinsuit是浅粉骨白敞襟，帽大暗口、胸前一条暗红竖缝、窄裤腰、两只浅鞋；Symbiotic暗粉胸的斜肋/腹结，头两根浅角与靴竖筋。与已有有机甲族保守合并，不因开襟和角另加信用。Skinsuit层1大敞口接浅肉面、层2只有少量腿片；Symbiotic分槽分别返回vikinghelmet/chestplate/trousers/boots，胸图含鲜艳调试色方块而不是同名标准layer。只记录原图现象，未看实际模型全链不能说游戏一定显示调试色。专用32×32/64×64分件不能按64×32普通甲切；普通甲不要做成裸露人台或肌肉插画。'),
row('material_layout_skull_vent_metal_family',['ferrum_armor'], '铁灰全罩圆额加两个黑眼孔，胸短灰U/V板与深色锁边，裤胫窄直、靴小脚面，追加已读颅面通气金属族。四分槽返回bloodiron__layer_1/2，不能按ferrum文件名搜索失败就称缺图。原生灰小板有连续深缝，适合学边口和粗分面；整头圆额和满身小粒点不作为Dynasty轮廓标准。'),
row('molten_plate_dark_shell',['plasma_armor'], '黑紫头盔斜橙裂口、胸一侧橙亮片和另一侧紫肩、腰腿少量细橙条，追加熔融暗壳族。分槽静态返回plasma__layer_1/2，原生层橙白高亮比图标明显更多，是材质一致性和过亮限制例。只借暗底上一到两块有方向的发热裂口；不要给每个UV岛描满黄边，不把亮点当纹理品质。')]
keys={c['case_key'] for c in json.loads((D/'provenance.json').read_text())['cases']};flat=[c for r in rows for c in r['cases']];assert len(flat)==len(set(flat))==11 and set(flat)==keys
out={'reviewed_at':datetime.now(timezone.utc).isoformat(),'pages_opened':['icons-01.png','icons-02.png']+[f'worn-{i:02}.png' for i in range(1,6)],'observations':rows,'excluded_cases':[],'complete_name_families_viewed':11,'native_icon_entries_viewed':44,'item_model_declarations_read':44,'native_layer_candidate_entries_viewed':19,'animation_metadata_present':0,'new_conservative_learning_groups':0,'append_observations':5,'limits':'六个头胸相同模板材料版本及其余有机/金属/熔融变体全部合并旧组，十一名称不增加独立设计信用。29静态返回只证声明，未证运行注册/渲染/UV/实机全链。','new_artwork':0,'production_changes':0,'game_starts':0,'gate_met':False}
(D/'semantic-review.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print('11 names / 44 original icons / 19 declared native layers / ZERO new groups / 5 append observations')
