"""Record explicit visual observations after viewing the pinned PNGs, not file-count credit."""
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone

D = Path(__file__).resolve().parent
R = D.parents[3]

# One distinct design-family unit, never one unit per atlas region/frame/color.
# All observations below are limited to the actual displayed PNG; no runtime claims.
NOTES = {
1: ('ornate-four-cardinal-open-center', 'symbol_composition', '四个凹尖围出空心中心，外圈小圆与十字分层；中心留白优于整面发亮。只借主次与负空间，不照抄花边。'),
2: ('four-lobed-element-medallions', 'symbol_composition', '四个相交大瓣各容一个小符号，中心交界留黑；元素身份靠不同内符而非只靠颜色。四瓣关系不作四个参考。'),
3: ('quadrant-linked-square-crosses', 'symbol_composition', '四个方结组成内方阵，外框四角内凹；适合研究方印的中轴和角点。外部碎点须减量，不能复制成敕字。'),
4: ('interlocked-square-guard', 'symbol_composition', '正方形与菱形叠置，中央完全留空，外圈断续小点；护体边界与中心内容分离。该符不证明尚方剑已有接入。'),
5: ('four-inward-triangles-with-discs', 'symbol_composition', '四个三角内指、四圆占四向，斜角小三角作次级节奏；可学方向感，不用密线冒充雷符。'),
6: ('concave-square-crossed-arcs', 'symbol_composition', '凹边四角和两条交叉弧线围成中心菱形，外缘仅八处小点；比整圈均布纹样有疏密。'),
7: ('eight-node-alternating-rim', 'symbol_composition', '四向尖角与斜向方框交替，双细环内侧留白；身份来自节点节奏。与pactum/repel保守合为一族，不能按配色拆计。'),
8: ('eight-circular-node-rim', 'symbol_composition', '八个同心小圆落在双圈外缘，中心无图；节点圆和外轮廓圆重复较强，只用于边界排布研究，不作独特流派最终稿。'),
9: ('small-square-chain-rim', 'symbol_composition', '128×256上下两帧是同一小方环链；帧色不同不拆计。与pure同属小方链边框，保守合并。'),
10: ('four-crescent-cardinal-rim', 'symbol_composition', '四个较大的内向月牙决定轮廓，斜向圆较小；主符号有尺度差。只借星月类主次，不把月牙直接当逐星专属。'),
11: ('eight-node-alternating-rim', 'symbol_composition', '四向大三角、斜向叠方和小菱点；比absolute复杂，但相同八节点交替组织，本批不重复记一族。'),
12: ('small-square-chain-rim', 'symbol_composition', '一圈方孔与小菱点相间、双线限宽；与corrupt环链属于同族，不靠白色换色新增参考。'),
13: ('eight-node-alternating-rim', 'symbol_composition', '八向三角尖围双环，中心空；与absolute/pactum同为尖节点双环边框，本批合并，不按红紫金拆计。'),
14: ('four-eye-scroll-rim', 'symbol_composition', '四向椭圆主结、斜向小方结配内卷钩，空白中心占绝大部分；借大结/小结层次，拒绝照搬眼形与旋纹。'),
15: ('EXCLUDE-soft-center-glow', 'excluded', '白色碎符外圈内是宽幅模糊光团。违反用户硬边材质方向，作为反例保留，不计有效设计参考。'),
16: ('botania-jointed-metal-panels', 'equipment_material', '粉色板片以深色接缝划分，亮点集中于凸缘，留大块实底；与蓝色manasteel共用板片组织，本批合一族。64×128不是原版64×32，未推断具体身体面。'),
17: ('botania-jointed-metal-panels', 'equipment_material', '蓝钢面用短硬高光、暗接缝而非周身白描边；与elementium同族，仅比较材质明度，不加一条。'),
18: ('botania-ribbed-manaweave', 'equipment_material', '青色细竖褶与横边分工、下方大片深布压住亮上部；布料节奏不同于金属接缝。不直接套成竹节或龙鳞。'),
19: ('botania-green-plate-brown-binding', 'equipment_material', '亮绿板片间穿插棕绑带、少数暗槽；材质在连接处换色，避免全套一色。没有按每条绑带计数。'),
20: ('archevoker-charcoal-gold-hem', 'equipment_material', '大面积炭黑布仅用短低对比折线，金边落在开襟与下缘、腰扣集中；不是全表面铺金纹。图集96×96，需原模型才能认定正背UV。'),
21: ('PENDING-crown-strip-binding', 'pending_binding', '骨色冠齿、深红小面与细长条同图；PNG里可见材质但不能确认细条对应骨冠哪一面。待匹配模型后再判独立性，不计数。'),
22: ('speed-boots-leather-lacing', 'equipment_material', '三条棕皮展开面、交叉白绑带、金色鞋口线；同一双靴的多面不是三件参考。交叉绑带需配合几何确认朝向。'),
23: ('cryomancer-ice-over-dark-cloth', 'equipment_material', '浅冰白不规则硬边岛压在深青底衣上，白点与深槽不等密；上浅下深保持读图。未称其已在本项目穿戴。'),
24: ('cultist-maroon-bone-hem', 'equipment_material', '暗红布、黑裙和骨色齿状边形成材质层；金扣为孤立强调，避免骨色和布色平均铺满。'),
25: ('electromancer-slate-copper-edges', 'equipment_material', '蓝灰大布面、淡铜边线、方形中心块；暗色水平断续折线较克制。只借蓝灰/铜色面积关系。'),
26: ('PENDING-crown-strip-binding', 'pending_binding', '金冠仅一条细横面，无法仅从PNG确认金齿轮廓和受光方向；与另两条冠材质暂不拆成独立设计。'),
27: ('infernal-charcoal-gold-harness', 'equipment_material', '黑色块状表面与金色开窗带交替，棕色交接块说明边带层次；金色集中在局部结构，不能推成全金甲。'),
28: ('pale-mottled-fabric-family', 'equipment_material', '深紫板面与淡紫大片硬边纹理分区，细线面单独排；浅色斑纹与wizard织物方向相近，本批保守合并，避免把UV重排算新设计。'),
29: ('paladin-gold-plates-chain', 'equipment_material', '金白甲片与棋盘链甲区域明确分离，最亮色只在大斜面和角部；链甲不应平铺整个胸甲。64×64图集，不能按其他96图强行映射。'),
30: ('plagued-dark-fabric-bone-mask', 'equipment_material', '墨绿布和暗紫围带衬出骨黄小区域，孤立青色扣点；材质重心集中。骨区只靠PNG不能断定正脸对应。'),
31: ('priest-ivory-purple-gold-trim', 'equipment_material', '乳白大面加低对比浅灰折痕，紫金只占横带和局部；亮衣不靠整面纯白填充，适合研究神圣感而非照搬宗教符号。'),
32: ('pyromancer-black-crimson-closure', 'equipment_material', '黑色布为主体，暗红跨面、金色扣口是小亮点，袖/下缘窄灰色磨损；火系不需要把全身画成火焰。'),
33: ('shadowwalker-dark-wrap-silver-links', 'equipment_material', '大块暗灰斜条与稀疏银链/扣分开，紫色占较少肩/布区域；细亮链可以局部用，不把全套描成白框。'),
34: ('PENDING-crown-strip-binding', 'pending_binding', '淡灰紫冠条与gold_crown类似展开，仅颜色不足以算独立造型；待模型绑定，不计数。'),
35: ('wandering-blue-cloth-leather-pouch', 'equipment_material', '蓝布的大折痕、金色衣边和棕色袋带分工，绿色下摆只作局部；功能材质在连接处出现，避免所有布面同密度花纹。'),
36: ('pale-mottled-fabric-family', 'equipment_material', '淡紫/乳白的块状织纹、棕色细带、下方两个大圆岛；圆岛的模型作用不猜测。与netherite同类浅斑纹组织保守合并。'),
37: ('coarse-eight-spoke-inner-knot', 'symbol_composition', '32px粗线八向结与中心小星仍有可读性；外围半透明光晕不采用，只研究主线/孔洞关系。不能把柔光样式原封移植。'),
38: ('coarse-flame-in-framed-disc', 'symbol_composition', '中央单火苗、矩形角与外圈相接，红橙深浅分层；中央图标和外框各有职责，边缘柔光不借鉴。'),
39: ('wizardry-interlaced-element-ring', 'symbol_composition', '粗环由斜向交错菱结组成，中心透明；与frost/lightning的结点安排相同，仅色与亮度差别，三张合一族。'),
40: ('wizardry-interlaced-element-ring', 'symbol_composition', '青白同心编结环，与fire_sigil同形，换色不新增设计参考；不因法术名不同拆计。'),
41: ('wizardry-interlaced-element-ring', 'symbol_composition', '同样的青白编结环，火/霜/雷不能用三种名称当三种独立纹样；本批与39合并。'),
42: ('EXCLUDE-smooth-shield-gradient', 'excluded', '256px大幅平滑径向色带和柔光，完全不符合本轮硬边MC纹样标准；只作为明确反例，不计数。'),
43: ('goety-orthogonal-square-lattice', 'symbol_composition', '橙红直角格线中留四大孔与若干小方孔，32px硬边可读；纹样由连通关系决定，不需要曲线或光晕。'),
44: ('goety-branched-cross-central-square', 'symbol_composition', '16px四向叉枝围中心方孔，端点向角分叉，整体较粗；研究留孔和主干宽度，不复制该召唤符。'),
45: ('PENDING-bear-rune-face-mapping', 'pending_binding', '128×64大透明图集上仅少量金色短符列，尚未定位对应兽体面。缺少面向证据前不计独立护体纹样。'),
46: ('goety-nested-square-hanging-seal', 'symbol_composition', '紫色方形套框、中心小方孔、下方独立挂结，方向性明确；相较对称圆环可研究符首/符尾的主次。'),
47: ('EXCLUDE-generic-concentric-ring', 'excluded', '青色八边同心环，当前只见通用圈层，未发现超出现有环类的目标专属用途；不为凑数新增一族。'),
}

if __name__ == '__main__':
    candidates = json.loads((D/'candidates.json').read_text())['rows']
    seen = {}
    rows = []
    for c in candidates:
        i = int(c['reference_id'].split('-')[-1])
        family, scope, note = NOTES[i]
        assert c.get('git_blob_verified') and c.get('decoded')
        good = scope not in ['excluded', 'pending_binding']
        first = family not in seen
        row = {**c, 'status': 'VISUALLY_REVIEWED_LOCAL_NOT_COORDINATOR_ACCEPTED',
               'semantic_family': family, 'scope': scope, 'observation_zh': note,
               'distinct_family_proposed_credit': int(good and first),
               'counts_as_runtime_or_new_production': False,
               'limitation': 'PNG composition/material inspection only; no face assignment, game, animation, emissive shader or runtime claimed.'}
        if good:
            row['family_representative'] = seen.setdefault(family, c['reference_id'])
        if 1 <= i <= 6: row['inspected_detail_view'] = 'build/art-reference-20261101/inner-symbols-full.png'
        elif i <= 15: row['inspected_detail_view'] = 'build/art-reference-20261101/outer-symbols-full.png'
        elif i <= 19: row['inspected_detail_view'] = 'build/art-reference-20261101/botania-full.png'
        elif i <= 37: row['inspected_detail_view'] = f'build/art-reference-20261101/armor-full-{20+4*((i-20)//4)}.png'
        else: row['inspected_detail_view'] = 'build/art-reference-20261101/page-04.png'
        rows.append(row)
    count = sum(r['distinct_family_proposed_credit'] for r in rows)
    result = {'recorded_at': datetime.now(timezone.utc).isoformat(),
              'scope': 'Actual PNG visual design families; separate from historical Java-method ledger227',
              'viewed_pngs': len(rows), 'proposed_distinct_design_families': count,
              'coordinator_accepted_new_visual_credit': 0,
              'production_gate_required': 1000, 'production_gate_met': False,
              'policy': 'One atlas/set/frame sequence/recolor family is at most one unit. Cross-task prior semantic dedup still pending. No automatic global ledger credit.',
              'rows': rows}
    (D/'review-batch-01.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    baseline=json.loads((D/'production-baseline.json').read_text())['rows']
    changed=[r['path'] for r in baseline if hashlib.sha256((R/r['path']).read_bytes()).hexdigest()!=r['sha256']]
    print(json.dumps({'viewed_pngs':len(rows), 'proposed_families':count,
        'symbol_families':sum(r['distinct_family_proposed_credit'] for r in rows if r['scope']=='symbol_composition'),
        'equipment_families':sum(r['distinct_family_proposed_credit'] for r in rows if r['scope']=='equipment_material'),
        'protected_assets':len(baseline), 'changed_since_baseline':changed},ensure_ascii=False))
