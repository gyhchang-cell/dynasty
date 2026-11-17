"""Manual atlas study, with set/overlay/recolor grouping stricter than file uniqueness."""
from pathlib import Path
import json
from PIL import Image

D=Path(__file__).resolve().parent
GROUPS=[
([72,73],'enigmatic-purple-edge-gold','紫黑板面以短块高光围边，金色仅在连接/底边出现；上层和裤层作为同套，不能计两件。'),
([74],'enigmatic-grey-relief-chain','128图集的灰色硬边浮雕/关节面与局部网纹分开，红色只在少量岛；有组织的暗部优于随机噪点。未把图岛位置猜成身体部位。'),
([77,78],'PENDING-sample-etherium','sample文件是青色样例板片，名称和存在不证明实际发布绑定；不把样例两层算新装甲参考。'),
([80,81],'ie-grid-fabric-copper-seams','深灰小网格、窄铜边和腰部接缝有明确分工；电工服材质与金属板不同，只借材质密度，不能复制工业身份。'),
([82,83],'ie-steel-banded-plates','灰钢用内暗外亮的宽方板，局部横条分节，棕色只占带扣接合；板片不靠细点镀满，裤层同套。'),
([84,85],'create-cardboard-folds','浅褐纸板以平行折痕和暗色接边说明材质，洞口保留；下层几条竖线不是独立参考或可直接套用的甲纹。'),
([86],'create-copper-diving','铜橙板面与青色小窗/核心对比，暗边稳定厚度，亮边集中；只借木铜设施/铜甲的材质分区，不照搬潜水装备。'),
([87,88,89],'create-netherite-diving','暗紫灰分节面、黑色接缝和少量铜橙亮点，臂部单独图与上下层仍为一套；同套多文件只一族。'),
([90,91,92,93,94,95,98,99],'ars-native-element-robes','四种元素原生袍共享衣缘组织；气系灰紫/黄边、土系褐绿、火系焦褐/橙边、水系青蓝竖褶有材质差别，但本批保守归一族，不按元素名拆四套。'),
([96,97],'ars-sourcesteel-geometry-trim','紫色大面由亮金直线、V形折角和窄横带组织，前期不可照搬过多描边；上下层合一套，借线宽与留白，不复制纹样。'),
([100,101,102,104,105,106,107,108,109,110,111,112],'ars-gold-jointed-plate-family','128图集多种轻/中/重和元素名共用大量金色构件/灰或彩色板面组织；只记一族。金色集中在窄连结件和边缘，不等于全身泛黄；具体权重差异需模型，不用名称猜新设计。'),
([103],'ars-red-cloth-gold-branch','64图集大块暗红布与少量金色阶梯支枝、橙色小核心分层，布面浅红细边克制；只借材质关系，不把展开金枝当本项目几何参考。'),
([113,114,115,116,117,118,124,125,126,127,128,129,130,131,137,138],'aether-colored-plate-family','紫/蓝/黑等基础甲沿同一板片组织换材质，classic_base为同套另一版本；共16张只记一族，不按材质、上下层或资源包副本拆计。暗色版靠低对比硬高光保持层次。'),
([119,120,132,133],'aether-phoenix-ribbed-fire','橙黄甲面以明显竖向亮带和暗槽构造节奏，classic版更碎；作为同一套的两个版本合并。借竖带方向，不把亮面覆盖整个早期甲。'),
([121,134],'PENDING-aether-sentry-regions','图上只有少量灰色岛和短带，未配原模型确认是何身体面；classic副本也不能另计，暂不列为独立完整材质设计。'),
([122,123,135,136],'aether-valkyrie-white-gold','乳白/淡青大板面加金色小结与窄底边，亮色之间有灰蓝暗缝；上下层与classic版四张仍只一套。可学神圣盔甲的面积配比，不复制徽章。'),
([139,140,141,142,143,144,145,146],'goety-dark-plate-chain-family','黑铁/诅咒骑士/诅咒圣骑/暗甲不同图集中都有暗板、低对比硬反光、局部网链与极少强调点；本批按共同材质组织保守合一族。上覆破布/链甲必须随原UV定位，不能把黑色填充当真实空腔。'),
([147,148],'goety-frost-pale-plate','冰蓝甲的浅色块沿边缘分节，胸侧亮纹向下收束，深色下层与上层区分；白色不铺满全套，两图算同套。'),
([149],'goety-malefic-bone-helm','骨黄/灰褐用少量硬边层次，黑色大孔保持通透；只借骨材明度与空白，不把原骷髅符号复制到帝兵。'),
([150,153],'archers-leather-garment','棕皮衣用大块斜向折线、深蓝下部与浅布小岛分工；generic为同款的灰度局部纹饰，不算第二套。没有把附图猜作已绑定本项目。'),
([151,152,154],'archers-ranger-cloth-metal','绿布和青黑高阶版共用大块V形布褶，棕带与小扣点集中；generic灰线仅是同家族纹饰。三张归一族，不因netherite名字当不同造型。'),
]
rows=json.loads((D/'batch-04-candidates.json').read_text())['rows']
seen={};out=[];proposed=0
lookup={i:(fam,note) for ids,fam,note in GROUPS for i in ids}
detail_ids=[74,100,103,105,109,139,140,141,142,143,144,145,146,149,150,151,152,153,154]
for r in rows:
    i=int(r['reference_id'].split('-')[1]);im=Image.open(r['local_path']).convert('RGBA')
    if not im.getchannel('A').getbbox():
        family='EXCLUDE-fully-transparent';note='实际RGBA全透明，没有可见美术，不计有效参考。';credit=0
    else:
        family,note=lookup[i]
        credit=int(family not in seen and not family.startswith('PENDING-'))
        seen.setdefault(family,r['reference_id'])
    proposed+=credit
    detail=(f'build/art-reference-20261101/batch04-detail-{detail_ids.index(i)//4+1}.png' if i in detail_ids else r['review_sheet'])
    out.append({**r,'status':'VISUALLY_REVIEWED_LOCAL_NOT_COORDINATOR_ACCEPTED','scope':'equipment_material',
        'semantic_family':family,'distinct_family_proposed_credit':credit,
        'family_representative':seen.get(family),'observation_zh':note,'inspected_detail_view':detail,
        'limitation':'Actual source PNG/atlas only; no complete model pose, face assignment, load binding or runtime claimed. Shared palette/weight variants/overlays/layers are not separate credit.'})
(D/'review-batch-04.json').write_text(json.dumps({'viewed_pngs':len(rows),'proposed_distinct_design_families':proposed,
    'coordinator_accepted_new_visual_credit':0,'production_gate_met':False,
    'policy':'Set layers, overlays, classic variants and related recolor/weight families grouped by visual organization; blank and unbound sparse/sample assets get zero credit. Prior-study semantic overlap remains for coordinator review.',
    'rows':out},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'viewed':len(rows),'proposed_families':proposed,'transparent_excluded':sum(r['semantic_family'].startswith('EXCLUDE') for r in out),'pending_files':sum(r['semantic_family'].startswith('PENDING') for r in out)}))
