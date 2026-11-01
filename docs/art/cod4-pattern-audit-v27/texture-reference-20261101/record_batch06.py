"""All 24 full-resolution sources viewed; do not reward inapplicable circle variants."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
from PIL import Image

D=Path(__file__).resolve().parent
R=D.parents[3]
rows=json.loads((D/'batch-06-candidates.json').read_text())['rows']
notes={
200:'双圈里一大正三角配三个倒小三角，中心无专属节点；是通用几何底坯。',
201:'外环细字带和五边开口围中心；中间三个小圆符与中心环连成短图网络，外围五个缺口重复。',
202:'同类文字环内一枚很长的白闪电，周围五个圆符沿多边框排布；中心强、外围弱的层级清楚。',
203:'正三角里套数圈和小倒三角，下方两圆一大弯月，右侧还有跨外框小圈；局部关系很密。',
204:'两相反大三角围住一只横眼，瞳孔为整圆，字环仍沿外边；不是当前帝王方印语义。',
205:'大三角骨架中置中央小符，三枚外圆符用直线连回中心，余下象限有三角与弯钩。',
206:'三枚圆节点围底架，中心为三瓣回旋形，上方有两枚竖排小圆，沿用共同字环。',
207:'三根粗长尖从中心外放，腰侧凹缺，几条细线分割外圈；中心另有小圆符，箭向比文字更醒目。',
208:'空心大三角与大块白填面交替，中央圆内交叉线，底部留粗白弧；填面挤压了小符可读性。',
209:'上下梯形/三角框分区，左右两个相反朝向的三瓣圆符，中间短符独立，整体仍为圆环字框。',
210:'四分段外三角骨架，中心三瓣旋叶，上方大三瓣冠形节点，外围仅三个三角尖超出圆圈。',
211:'外侧方框和斜方框相叠、双文字环，中心月牙与三颗不同大小六角星；与后面三个部件视觉相合。',
212:'只有内侧文字圆环，中央和外围均空；是已见月阵中的局部，不是完整新设计。',
213:'方框、斜方框、外文字圈重合，中心全空；是同一月阵的外围组织，不单计一例。',
214:'只有月牙和三颗六角星，位置大小与完整月阵的中心相合；独立文件不是独立设计。',
215:'两三角与外字圈包住内字圈和小白圆心；后面两张分别保留内心和外骨架。',
216:'小内字圈围白实心点，外围全空；作为太阳阵的局部，不单计。',
217:'去掉字带后的双圈、交错三角和实心白点；同太阳阵的结构组件，不能再算一套。',
218:'六向三角骨架的左中与右上有两块白填面，四枚小圆符在中心形成 Y 形连接，外沿有三个缺圆。',
219:'粗凹腰交叉面居中，上下尖形，外层交错三角与字环；大片填白会压住局部结构。',
220:'与 teleportation 画面一致；实际解码 RGBA 逐像素完全相等，虽然 PNG 文件 SHA-256 不同。',
221:'上方三瓣冠节点接中央实心三角，三角内留一小三角孔；外围框与 movement 的组织相近。',
222:'横向菱形包中央分扇小圆，左右相似半圆节点，上下各一枚圆符，围绕横轴建立层级。',
223:'大正三角内有一倒三角，中心直立矩形的上下端各压小圆，中下小圆有白心；细字仍占大半边界。',
}
for r in rows:
    n=int(r['reference_id'].split('-')[1])
    im=Image.open(R/r['local_path']).convert('RGBA')
    r.update(status='VISUALLY_REVIEWED_EXCLUDED_FROM_CURRENT_TARGET_GATE',
        semantic_family='EXCLUDE-vector-circle-family-not-current-MC-target',
        family_representative='VIS-200', scope='negative_style_and_component_dedup',
        distinct_family_proposed_credit=0, observation_zh=notes[n],
        rgba_sha256=hashlib.sha256(im.tobytes()).hexdigest(),
        inspected_detail_view=r['review_sheet'], applicable_targets_proposal=[],
        limitation='Large vector-like western alchemy circles and fine glyph rims are context/negative examples, not original MC pixel material or fully relevant school/imperial UV cases. No decoding or name gives runtime/mechanic/animation proof.',
        coordinator_accepted_new_visual_credit=0)
    if n in [211,212,213,214]:r['dedup_group']='moon-composite-and-components-one-context-case'
    elif n in [215,216,217]:r['dedup_group']='sun-composite-and-components-one-context-case'
    elif n in [219,220]:r['dedup_group']='teleportation-decoded-pixel-identical'
    else:r['dedup_group']='shared-alchemy-circle-grammar-context-only'
out=dict(recorded_at=datetime.now(timezone.utc).isoformat(),viewed_pngs=len(rows),
    proposed_distinct_design_families=0,coordinator_accepted_new_visual_credit=0,production_gate_met=False,
    policy='24 actual PNG files opened full 512x512; all held as context/negative study, no target gate credit. Moon/sun components and variants are not cases. Different byte hashes may contain identical decoded pixels.',
    decoded_identical_pairs=[dict(a='VIS-219',b='VIS-220',png_bytes_identical=False,rgba_pixels_identical=True)],rows=rows)
(D/'review-batch-06.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(opened=len(rows),new_family_proposals=0,decoded_duplicate_pairs=1,accepted_credit=0)))
