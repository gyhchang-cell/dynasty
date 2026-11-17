"""Observations written after four icon, thirteen native atlas pages and all animation frames."""
from pathlib import Path
from datetime import datetime,timezone
import json
D=Path(__file__).resolve().parent;rows=[]
def row(group,cases,observation,new=False):
 x={'semantic_group':group,'cases':cases,'observation':observation,'credit':'NEW_CONSERVATIVE_LEARNING_GROUP' if new else 'APPEND_TO_PRIOR_GROUP_ZERO_NEW_DESIGNS'}
 if not new:x['prior_group']=group
 rows.append(x)
row('hazmat_yellow_dark_suit',['radiation_zone_reborn:protective'], '暗绿黑防护面罩以两格浅绿视窗和黑呼吸口识别，胸前是厚衣两竖束带、腰两侧垂袋，裤腿暗面，靴筒斜分。保守追加已有防护服族，不因颜色和防毒功能相同又计一套。四张64×64独立候选含面罩、衣、裤和靴，不能按普通64×32套切。暗纹反差偏低，后续布皮材质应至少让领口/袖端和包袋在缩小后可辨。')
row('gray_stone_suit_conservative',['radiation_zone_reborn:giantrock_armor'], '暗石外壳配少量苔绿额/胸口/腰带，头盔和短V胸保留基本甲形，裤窄直；两只靴以斜片组织，追加石甲族。models/armor两层和另一个protective_mask候选并存，不能推断面罩候选实际选中。苔绿细线不足以拯救全黑大面，避免密石点噪纹。')
row('vanilla_outline_elemental_palette',['radiation_zone_reborn:sedisilver_armor','pasterdream:copper_armor','pasterdream:dyedream_armor','pasterdream:titanium_armor','gobber2:gobber2','inventorypets:solstice','deeperdarker:resonarium','evilhunter:silver_armor'], '八名称共享倒U盔、短V胸、直裤与分靴基本模板，按既有原版轮廓材料族合并，不把铜橙、粉梦、淡紫钛、蓝Gobber、浅白Solstice、亮蓝Resonarium和灰银改色算独立设计。Sedisilver靴更斜且有防护面罩候选，仍不据局部换形追加信用。Paster三金属层的分区近似而亮度高；Solstice只有近白浅青几块且头/胸宽，作缺乏层次和比例反例。以原版比例为基础的材料微调应保留深轮廓和明显面孔，不能用白色填满整件。')
row('creature_hide_shell_vests',['radiation_zone_reborn:tyrant_skin_armor'], '苔绿兽皮配米白牙骨边，头顶短突起、胸口V形白牙和肩白片、腰左右白骨及靴口白带对应，追加已有兽皮壳甲族。128×64候选有多块独立皮骨岛，不能当两张64×32普通甲拼接来复用；只学软皮承托硬骨的材料顺序，白牙不铺成全身栅栏。')
row('complete_wastefur_torn_hem_coat',['radiation_zone_reborn:wastefur_armor'], '黑绿短罩帽略遮两颊，胸用左右两块斜肩毛皮接短腰、下沿碎角，裤子较宽且毛皮条向下收，靴长筒两脚分明。新增保守破边毛皮衣组，区别平直金属边和白毛领。四张64×64候选分别包含帽、披肩/衣、裤和靴，多处锯齿/毛束，而整体接缝仍依实际骨架未核。暗面过多和碎毛过密作为限制，Dynasty毛皮只借粗块边、衣口和局部亮毛，不照抄破边形状。',True)
row('mixed_maid_clothing_apron',['pasterdream:qym_armor'], '耳夹是两只粉耳而非普通头盔，衣为浅白紫蝴蝶结短上衣，蓝白短裙和粉色圆头鞋；追加既有女仆/衣裙组作普通甲比例的反例，不把部件稀奇计为独立完整普通盔甲。两张qym64×32候选全透明且哈希相同，不能当穿戴UV学习，更不能据此判游戏隐形；可能自定义渲染仍未核。只学衣料、饰结与裙边分色，排除圆鞋和插画式比例。')
row('bossloot_bone_sculk_rib_armor',['pasterdream:sculk_armor'], '深蓝绿窄盔带横向短角，胸的青色V形层叠片和暗腰，裤靴只保留少量蓝绿边，追加既有幽匿肋甲族。两张候选有稀少青肋及大片暗区；发光感用离散青块表达，不用柔光，也不要靠加长角把普通甲改成怪物头。')
row('gem_plate_metal_variants',['outer_end:cobalt_crystal','outer_end:mint_crystal','outer_end:rose_crystal'], '三套共享矿晶甲轮廓和高亮切面，蓝钴胸多竖块，薄荷胸三段横片，玫瑰胸一层斜V；头部主要换横额与面口亮区，裤靴仍基本模板。保守合并既有宝石板甲族，不将矿物名、细部面线和配色计三套独立设计。两层原生图均为普通比例候选，小而连续的亮边偏多，只借正侧面层次，不用全图雕碎。')
row('complete_soul_steel_wrap_visor_green_core',['sons_of_sins:remnant'], '头图以低顶平横条和三层暗灰面罩收束，胸为短甲身内一点绿黄竖芯，腰腿灰板和深红边、靴细长且两脚分开。新增保守缠绕面罩/绿芯灵钢组，借识别点小而集中、其余大块暗灰的层次。胸原图16×48是3个16×16动画帧，16tick/帧并插值，帧之间主要绿芯强弱变化；三帧只算同一件，不借动态当额外设计。层1的灰条和绿芯、层2的灰腿片仅候选，不宣称实际UV连接。',True)
row('complete_mechanized_dark_frame',['torchesbecomesunlight:patrol_captain','torchesbecomesunlight:preparation_op'], '两套现代作战服保守追加既有机械/防护框架族：巡逻长方闭面罩、黑胸横束带和两红肩扣，直裤和短鞋；预备干员灰横目镜、下方棋盘口罩、斜襟与青肩/鞋底。只学护具开口、暗布与硬甲片的层次，不把现代服整套搬成Dynasty古代甲。未把同名NPC皮肤当甲图集，本批这两套只读四部件图标，实际穿戴图层/骨架仍未核。')
row('souls_black_knight_dark_silhouette',['cardinal_sins:darksteelarmor'], '黑色双角罩盔、深胸两侧小护片、黑裤和高直靴，追加既有黑骑士族。两张名带placeholder的64×32候选均全透明，与另一套robed的两层同哈希，零UV信用；不要凭文件名和空层认定运行显示失败。图标太黑、面口与边缘混在一起，只作反差不足反例。')
row('immersive_robe_open_front',['cardinal_sins:robed_armor'], '深蓝低罩帽、敞襟衣里白领和棕黄扣列、棕直裤与灰靴，追加开襟袍族。两张placeholder全透明，另有256×256黑袍实体候选带羽状/破边岛和少量白领节点；不能跳过实际模型绑定直接认为该实体图就是玩家穿戴。可借衣襟与领口连接，但密集羽毛纹不适合全部甲面。')
row('vanilla_outline_elemental_palette',['echovoids:gravity'], '青黑头盔几处亮绿凸点、胸深青V片与下缘两根浅绿垂带，腿腰上两条亮带、靴口一圈亮绿，保守追加原版材料轮廓族。chainmail_layer命名候选含相同青绿和条带但绑定未读；名字不相同不等于缺图。只学少量发光识别点，避免把长悬带当普通腰连接。')
row('molten_plate_dark_shell',['netherman:azazel'], '橙金弧形头物、红黑胸面金边、金色短腰片与两个金环靴图，追加熔融/祭仪暗壳族作非普通甲轮廓的限制例。believer_armor128×128候选有红披片、金链和零散小环，未证对应azazel装备完整渲染链，不能用来切普通玩家甲UV。只学红布与金属件主次，巨环和断裂悬空轮廓不用于微调已认可神圣甲。')
keys={a['case_key'] for a in json.loads((D/'provenance.json').read_text())['cases']};flat=[k for r in rows for k in r['cases']];assert len(flat)==len(set(flat))==24 and set(flat)==keys
out={'reviewed_at':datetime.now(timezone.utc).isoformat(),'pages_opened':[f'icons-{i:02}.png' for i in range(1,5)]+[f'worn-{i:02}.png' for i in range(1,14)]+['animation-frames.png'],'observations':rows,'excluded_cases':[],'complete_name_families_viewed':24,'native_icon_entries_viewed':96,'item_model_declarations_read':96,'native_layer_candidate_entries_viewed':49,'animation_metadata_present':1,'animation_frame_slots_viewed':3,'new_conservative_learning_groups':2,'append_observations':12,'limits':'24个四件图标齐全名称不等于24独立完整设计；其中普通材料模板、局部、反例及未绑定图集不能冒充有效整套信用。两个保守新组仍非已核定完整独立总数。','new_artwork':0,'production_changes':0,'game_starts':0,'gate_met':False}
assert len(rows)==14
(D/'semantic-review.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print('24 new names / 96 icons / 49 native candidates / 2 conservative new groups / 12 appended observations')
