"""Actual atlas observations; material families are not full equipment/UV cases."""
from pathlib import Path
from datetime import datetime, timezone
import json
D=Path(__file__).resolve().parent
rows=json.loads((D/'batch-11-candidates.json').read_text())['rows']
notes={}
def put(ids,family,rep,note,limit='只作材质/纹饰阅读，尚未核原模型全套 UV 与穿戴槽；不认定完整装备案例。'):
    for n in ids:
        notes[n]=(family,rep,int(n==rep and not family.startswith('EXCLUDE')),note,limit)

colors={363:'暗紫',365:'炭黑',367:'冰蓝',369:'深铜褐',371:'红铜褐',387:'电蓝',389:'灰黑',391:'绿',393:'红',395:'宝石蓝',397:'银灰',422:'乳白灰'}
for n,c in colors.items():
    put([n,n+1],'iceandfire-stepped-scale-plate-family',363,
        f'{c}底材上以阶梯 V 形暗槽分大片甲片，亮边没有铺满整岛；附加窄长区域留出条状间隔。',
        '十二种色型与上下层合成一族。学习甲片边/实底比例，不把不同颜色当新案例；未确定每个孤岛的身体朝向。')
put([373,374,399,400],'iceandfire-polished-metal-insets',373,
    '铜金属图集以宽铜棕板和嵌框分区，并有蓝色窄连结岛；银金属图集用白灰宽板、棕连接带及紫金小附块。',
    '铜/银两材质的部分排布不完全相同，本批仍保守合为宽金属嵌板组织；不按金属颜色和层拆计。')
for n,c in [(375,'暗红'),(377,'白灰'),(379,'骨黄')]:
    put([n,n+1],'iceandfire-segmented-shell-ribs',375,
        f'{c}壳层用多道横向明暗带表现节段，灰色罩形区域与彩色下方壳带分开，边缘以大弧阶梯而非毛边收口。',
        '同一蠕虫壳甲三色/两层只算一材质族；不把壳节段逐条数为案例。')
put([381,382,383,384,385,386],'iceandfire-dragonsteel-plate-chain-family',381,
    '火/雷版为紫灰甲板、宽暗框与小面积链网；冰版换成冰白板、棕色连接条与灰蓝槽，腿图包含独立短带和链网岛。',
    '冰版排布并非只换 RGB，但三龙钢版本本批按同一板甲/链网系统保守合并；不冒充已验几何差异。')
tide={401:'蓝',403:'铜褐',405:'深蓝',407:'绿',409:'铜橙并横条纹',410:'紫',412:'红',414:'青'}
for n,c in tide.items():
    ids=[n] if n==409 else [n,n+1]
    put(ids,'iceandfire-tide-scale-fins',401,
        f'{c}甲面以深槽划分大鳞，浅青白的棋格/亮带与弯边附片保持分区；部分孤岛是窄齿状边，非整图均匀鳞噪。',
        '潮汐甲所有颜色、guardian 纹带和腿层保守合一；未核鳍片模型与身体面，不把亮条直接认定胸前图案。')
for n,c in [(416,'苔绿'),(418,'冷灰蓝'),(420,'深灰')]:
    put([n,n+1],'iceandfire-hide-bone-tooth-hem',416,
        f'{c}低对比底材上搭配稀疏骨色小块和下缘短齿，整条暗带留出大面积实底。',
        '三环境变体、上下层同族；骨齿的数量不代表参考数，也不能直接当人类骨甲正背验收。')
put([424],'EXCLUDE-plain-blindfold-strip',424,'一根骨灰横带与末端小结，其他区域透明。','通用窄带原语，没有当前专属甲纹语义，不占制作门槛。')
put([425],'EXCLUDE-earplug-tiny-placeholder-like-islands',425,'只有两个很小的棕色方块岛，几乎无表面纹样。','耳塞配件和当前整套装备 UV 不同，不因为有 PNG 就新增案例。')
put([426,427,428,429],'iceandfire-chitin-chevron-shell',426,
    '沙色和青绿甲壳以宽折线、V 形节段和亮中面分区；条状区域也重复节段，中心没有高密度散点。',
    '沙漠/丛林与两层合一；只借粗壳节奏，不用虫甲源像素覆盖本项目。')
put([430,431],'iceandfire-wool-leather-disguise',430,
    '白灰羊毛面用少量块状暗簇，棕色皮带在连接处穿过，黑边仅局部出现，白底没有满面描金。')
put([432,433],'caves-dark-cloak-red-nodes',432,
    '大部分岛接近黑色，破口式下缘用粗齿与透明缺口表达；红色只在数个小节点。glow 只复现这些红点，其他全部透明。',
    '完整4倍原图已核看；底图/红色发光覆层同族。不能靠把黑衣提亮来捏造原图颜色或当另一装备。')
put([434,435],'caves-copper-pressure-suit',434,
    '铜橙宽壳板、暗棕皮质带及局部方形亮铆点分区；腿岛由长暗棕条与铜色外块组成。',
    '与 Create 潜水甲同属铜潜水题材但不直接认定同设计；需后续与历史图标语义配对，暂不获新计数。')
put([436,437],'EXCLUDE-gingerbread-costume',436,
    '橙褐饼干底上有白色糖霜锯齿、粉色十字糖饰和局部红点，腿层同样糖霜封边。',
    '糖果戏服与当前帝王/护卫及八武器语义不相关；虽可读硬色簇，不拿来凑本任务相关设计。')
put([438,439],'EXCLUDE-modern-hazmat-suit',438,
    '黄绿色大布面配黑灰横条、深色接缝和少数浅色边，左右岛留出大片纯底。',
    '完整4倍图核看；现代防化服与当前目标不符，不把黄颜色算神圣甲案例。')
put([440,441],'caves-bone-hide-bindings',440,
    '骨白叉形块和骨盘与橙棕毛皮/肤色带分开，细棕连接线留在单独窄岛，腿层为少量浅棕纹理。')
put([442],'EXCLUDE-rubber-boot-bands',442,
    '黄色短条上有数个白色硬亮点和薄灰横带，许多图集面积完全透明。',
    '现代胶靴式短带无法充作当前完整盔甲或专属纹章，零计数。')
put([443,444],'caves-polarity-angular-open-trim',443,
    '白色稀疏线在上层围成两个斜角结与开口横框，腿层仅短折带；中间留大暗区，线端有明确开口。',
    '一套纹饰的上下层合一，只借留孔和线条粗细；没有原版之外全套装备 UV 接入证据。')
put([445],'alexsmobs-centipede-segment-bands',445,
    '红橙段甲紧贴近黑下带，暗槽把节段分成数块，亮点集中在上方小块而非整面噪点。')
put([446],'alexsmobs-crocodile-scute-field',446,
    '橄榄绿表面以深浅交错的短矩块组成鳞甲，小鳞在宽板区域重复，窄延伸区逐渐收束。')
put([447,454],'alexsmobs-coarse-feather-bindings',447,
    'Emu 腿岛以浅棕纵羽簇与暗细缝分开；Roadrunner 靴岛是深棕基带与下缘一排骨色粗羽齿。',
    '两种鸟装在排布上有别，本批只作为粗羽/绑带组织合一，不拿物种数新增参考。')
put([448],'EXCLUDE-modern-fedora',448,'棕红帽檐由深浅横块分层，另有细长带和方形开口岛。','现代礼帽与当前甲套/学院纹样不相近，不作有效范围案例。')
put([449],'alexsmobs-flying-fish-pale-blue-panels',449,
    '浅蓝大板与少量灰蓝槽分区，下方透明区域另有细小蓝色翅片岛。',
    '图集只有局部鞋与附片材料，不等于已核专用靴模型、全部六面或翼动作。')
put([450],'alexsmobs-frontier-fur-tail',450,
    '灰褐毛皮长带用疏密不同的细块，另有短尾样的横向明暗节段，最亮像素不沿整边铺满。')
put([451],'alexsmobs-frost-pale-jagged-helm',451,
    '浅蓝白罩形岛的下沿有不等长冰齿，窄暗缝压住白块，另有少量紫色附岛。',
    '只读冰壳配色和齿边组织；未核原头盔几何，不凭图集猜正脸、角的位置。')
put([452],'EXCLUDE-antler-trophy-headgear',452,'褐色鹿角样长岛在末端粗分叉，黑带岛分离。','猎获角冠与当前帝纹关系不足，不能把分叉数充作多个图案。')
put([453],'EXCLUDE-novelty-drink-hat',453,'蓝帽上有白红小盒、细绿弯管及粉色小附岛。','明确玩笑/现代造型，不作为用户要求的神圣盔甲参考。')
put([455],'alexsmobs-rocky-bone-like-relief',455,
    '骨灰大面以少量棕暗分缝形成重叠石片，亮色在块顶，附加窄岛以粗短横节串联。')
put([456],'EXCLUDE-shield-not-wearable-uv',456,
    '双青绿色矩板内有菱形凹框，另有珊瑚橙岛和白色锯齿长条。',
    '这是盾贴图的独立展开，不把它按护甲槽位计入装备 UV；无符字/方令特定关系。')
put([457],'EXCLUDE-sombrero-themed-hat',457,
    '浅棕帽面中央有大圆孔，外缘用红绿细条，面中阴影是多档棕环。',
    '完整4倍源图已看；与当前盔甲题材不符，不借现代/地域帽型改成帝冠。')
put([458],'alexsmobs-turtle-dark-shell-rims',458,
    '深棕宽壳片以方折暗缝区分，长横边只有稀疏小凸块亮点；不是整片高密度鳞纹。')
put([459],'EXCLUDE-wing-only-membrane',459,
    '单侧橙色翅膜岛由深橙隔脉切成几格，周边其他区域透明。',
    '翼膜不是当前人类甲套所需 UV，也不跨做妖兽翅膀模型；排除门槛。')
put([460],'alexsmobs-maroon-fabric-embossing',460,
    '暗红大布块用低对比卷折纹和几条宽边分区，附加长岛保留一片平稳实底，亮点克制。',
    '可研究锦布低对比纹理密度；未核骨骼方向，不按孤岛位置断言背面。')
put([461],'cataclysm-stone-moss-petal-materials',461,
    '灰黑石片和绿色苔枝交替，紫白花瓣只在几处边角；紫色不平均铺满石面。',
    '完整4倍图核看，只借石/苔/花分工；分离纹理岛和花瓣不拆成多个案例。')
put([462],'cataclysm-bone-gold-dark-bindings',462,
    '骨白板片用棕暗凹槽勾出厚边，局部金黄连接边与近黑底并置，多块暗区仍然留白。')
put([463,464],'cataclysm-cursium-purple-gold-cyan',463,
    '暗紫板面配局部金色硬边，青色短条单独分区；腿层仅少量紫灰带与金青小扣。',
    '完整4倍源图已看，上下层一族；这种稀疏三材质布局不能直接套给所有高级甲。')
put([465,466,467],'cataclysm-ignitium-hot-rim-dark-plate',465,
    '近紫黑板片以橙黄亮边分区，亮色集中在节点、边带和少数火状岛；腿层是同色短带，鞘翅胸同套材质并有橙膜岛。',
    '普通甲/腿层/鞘翅胸作为同一套装备系统，不因配件展开或橙色强度另计。')
put([468],'cataclysm-charcoal-helm-orange-nodes',468,
    '灰黑罩形岛用宽横阶分层，暗红顶点和两侧橙金小片作亮点，近黑面大幅保留。')
assert set(notes)==set(range(363,469))
for r in rows:
    n=int(r['reference_id'].split('-')[1]);family,rep,credit,note,limit=notes[n]
    r.update(status='VISUALLY_REVIEWED_LOCAL_WEARABLE_MATERIAL_ATLAS',semantic_family=family,
        family_representative=f'VIS-{rep:03}',distinct_family_proposed_credit=credit,
        scope='equipment_material',observation_zh=note,
        atlas_part_observation_zh='原图文件：'+Path(r['path']).name+'；'+('腿层/第二层与同套主层共同阅读，不独立加数。' if Path(r['path']).stem.endswith(('_legs','_leggings','layer_2')) or ('/alexscaves/' in r['path'] and Path(r['path']).stem.endswith('_1')) else '按所见完整平面图集记录；不臆测孤岛对应身体朝向。'),
        limitation=limit,inspected_detail_view=r.get('supplemental_detail_view',r['review_sheet']),
        applicable_targets_proposal=[],historical_equipment_semantic_comparison_pending=True,
        coordinator_accepted_new_visual_credit=0)
out={'recorded_at':datetime.now(timezone.utc).isoformat(),'viewed_pngs':len(rows),
    'proposed_distinct_design_families':sum(r['distinct_family_proposed_credit'] for r in rows),
    'coordinator_accepted_new_visual_credit':0,'production_gate_met':False,
    'policy':'106 actual archive PNGs read including recolors/layers/excluded unrelated hats. 15 large atlases additionally read at exact integer4x. Material grouping is not full UV proof or accepted new equipment credit. Historical icon semantic pairing pending.', 'rows':rows}
(D/'review-batch-11.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='rows'},ensure_ascii=False))
