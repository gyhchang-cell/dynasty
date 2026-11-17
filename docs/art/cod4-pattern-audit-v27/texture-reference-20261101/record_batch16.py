"""Thirty-one wearable PNG observations, not thirty-one full UV cases."""
from pathlib import Path
from datetime import datetime,timezone
import json
D=Path(__file__).resolve().parent
rows=json.loads((D/'batch-16-candidates.json').read_text())['rows']
N={
555:('relics-vented-hardware-boot',555,1,'绿白硬件、灰边大暗孔和窄扣带分别成岛，脚部亮绿块集中，连接处保持灰暗。','只借大材/扣带分工；与两种 walker 硬件靴保守并同材料族，不推断实际左右脚或模型槽。'),
556:('relics-vented-hardware-boot',555,0,'青蓝面、紫边大方孔及细青长带，亮色大块仍集中于少数壳片。','颜色和附片布局变化不在本批拆新硬件靴族；未核实际模型，不能断言是纯换色。'),
557:('relics-quiver-leather-feather-parts',557,1,'橙褐宽皮面通过深棕粗边与浅褐大折面分厚度，细长独立岛有白羽与褐杆交替。','借皮革块面与箭羽分材；箭羽数量/皮面六面都不是独立设计，不复制图标或筒体。'),
558:('relics-framed-belt-buckle-parts',558,1,'灰蓝宽框围出深蓝长方内孔，横带沿下缘延伸；独立紫白小片与主带分开。','只参考框扣/宽带留孔；与同形猎带、皮带保守合并，框扣不是完整盔甲UV。'),
559:('relics-wire-loop-pendant-parts',559,1,'蓝紫细链围空心长环，金黄与红色窄岛在别处，链本身不铺满发光色。','小链/吊坠是同对象不同部件；与蓝紫链系保守合并，不能把独立岛当新增饰品。'),
560:('relics-framed-belt-buckle-parts',558,0,'深绿框带保留大暗孔，独立骨白片与细长棕白串分离，亮绿仅在边角。','沿用同类宽框带组织；骨/绿变化保留材料观察，不另外算完整穿戴案例。'),
561:('relics-wire-loop-pendant-parts',559,0,'深青细链围大空孔，浅青白小片和细短串另置，主亮点数量少。','与同类细链挂件合并；jellyfish 名称不证明图中每块属于水母结构。'),
562:('relics-framed-belt-buckle-parts',558,0,'棕褐带的深内孔仍大，独立金黄扣件用约三阶亮暗表现，亮点集中。','与宽框带合并；这是扣件面积控制参考，不照搬金扣像素。'),
563:('relics-vented-hardware-boot',555,0,'暗棕主板上几条橙黄亮段，外围黑边；亮块只占少量壳片，另有小黄岛。','与硬件靴材料族合并，不凭名称证明熔岩粒子或发光运行效果。'),
564:('relics-midnight-cloth-sparse-moon-hem',564,1,'近黑蓝大片上稀疏白紫短星簇与弯月，亮蓝边沿窄下摆分段，中心大面仍暗。','可借夜色布面与局部纹样层级；白紫点若均匀铺满会失主次，不复制其月星纹。'),
565:('relics-pale-wrap-ember-cuff',565,1,'浅皮褐宽片与红橙腕部块分开，黄白亮段集中在上缘，手部岛留大素面。','只借缠带/腕部强调分工，不按火色认定手套实际燃烧，也不是本项目新护腕。'),
566:('relics-wire-loop-pendant-parts',559,0,'深紫细链顶部与侧面少量蓝亮点，青色大吊片与紫短片另置。','同类线环挂件合并；未核完整绑定，不把各岛当独立戒指/项链。'),
567:('artifacts-wire-loop-pendant-family',567,1,'淡金细环围大空孔，下方棕金小十字/吊端，右上独立浅金短岛。','只借线链与小吊端面积；宗教标识不移作王朝身份。与银链多色小坠保守合并。'),
568:('artifacts-coarse-banded-claw-glove',568,1,'深蓝斜楔与亮蓝横条用很少色阶分区，两组同形指/掌岛按大块排布。','与绿色同形爪具合并；简洁色面适合作硬像素参考，但没有证明手指三维弯曲。'),
569:('artifacts-coarse-banded-claw-glove',568,0,'相同爪/掌布局换深浅绿，主横条位置不变，小亮块数量有限。','同形换色不增加设计族；不把六个重复岛拆为六个饰品。'),
570:('artifacts-sawtooth-cuff-flame-overlay',570,1,'灰褐两条粗带：一条带有规则短齿，另一条平直，仅两三阶灰褐；没有火焰。','底材与571覆层是同手套不同层，宽窄臂也合并；灰带不可单独算新装备。'),
571:('artifacts-sawtooth-cuff-flame-overlay',570,0,'橙黄大火舌附在中条和下条，较亮黄集中于宽火段，其他处完全留空。','记录火形覆层与底材分离，不据文件名断言实际shader发光或播放状态。'),
572:('artifacts-sawtooth-cuff-flame-overlay',570,0,'宽臂版同灰褐带与短齿，条带长度略展，暗上缘保持一整块。','与570同手套宽度版本，源UV不同仍需分别绑定，不改成共用图后宣称通过。'),
573:('artifacts-sawtooth-cuff-flame-overlay',570,0,'宽版火舌沿横带扩宽，仍黄芯橙边，透明空场大。','同覆层/宽度变体合并，实际温度、伤害或特效不在本研究范围。'),
574:('artifacts-wire-loop-pendant-family',567,0,'银白细环下挂小红空心方坠，右上独立金橙短片。','沿用同链挂件族；仅靠金/红小片不同不能追加完整案例。'),
575:('artifacts-fringed-cloth-scarf',575,1,'黄绿大布面内有细小折纹，下缘短齿流苏不等长，独立窄片与宽布分开。','只借布面/下缘面积；绿/蓝版本合并，碎色较多不作为未来必须照搬的标准。'),
576:('artifacts-wire-loop-pendant-family',567,0,'银链下端是红色小心形空环，右上红灰小片分开。','与同链吊坠合并；心形区别保留观察，不移作学院令符或拆成独立UV案例。'),
577:('artifacts-gold-block-glove-dark-cuff',577,1,'金色宽带以少数大折面分亮暗，底部灰黑窄腕带独立，少量金色方岛在上部。','可借黄金不靠全边描白；宽窄臂同设计，不复制其原像素。'),
578:('artifacts-gold-block-glove-dark-cuff',577,0,'宽版金带延长，灰黑腕带仍窄，金色方岛尺寸随宽度改变。','与577同版式族，不因为条带宽度加一套。'),
579:('artifacts-root-leather-brown-green-straps',579,1,'棕色大带用明暗块表现，亮绿只在少数折点和竖向连接处，主带留大透明缺口。','可借根/皮主材与绿色接点分工；不凭平面透明缺口报穿模或缺面。'),
580:('artifacts-fringed-cloth-scarf',575,0,'蓝色大布面有碎深浅蓝折纹，下缘短流苏和同类布局，独立窄片同结构。','与绿围巾材料族合并，换色不新增设计；所谓隐身效果未验。'),
581:('artifacts-wire-loop-pendant-family',567,0,'同银链下挂蓝色小方坠，右上一个青蓝短片，链空孔大小保持。','与574/583同链坠结构合并，颜色不作为新身份。'),
582:('artifacts-leather-spike-hardware',582,1,'深棕粗带与灰白尖齿分区，铁齿以整根亮竖和暗端表示，下方另有棕白短细带。','只借皮带/铁齿分材；尖齿图集中各面不是多种装备，不推断运行时落点。'),
583:('artifacts-wire-loop-pendant-family',567,0,'同银链下方小坠换绿，右上绿短片替代青片，外环轮廓不变。','沿用同挂件家族，不为 thorn 名称创造不存在的叶/刺模型证据。'),
584:('artifacts-leather-glove-palm-cuff',584,1,'深棕宽掌带中有少数浅褐竖块，下方细腕带和两段窄长条同为棕色硬分区。','可借皮掌/腕带/露指的材质节奏；不按吸血名字借鲜血粒子或改变玩法。'),
585:('artifacts-leather-glove-palm-cuff',584,0,'宽版棕掌带加长，浅褐竖块保持集中，窄腕带不增加花纹密度。','与584同一宽度变体，不另计一件饰品或完整UV。'),
}
for r in rows:
 n=int(r['reference_id'].split('-')[1]);family,rep,credit,note,limit=N[n]
 r.update(status='VISUALLY_REVIEWED_SOURCE_MATERIAL_ONLY',semantic_family=family,family_representative=f'VIS-{rep:03}',
  distinct_family_proposed_credit=credit,scope='equipment_material',observation_zh=note,limitation=limit,
  inspected_detail_view=r['supplemental_detail_view'],applicable_targets_proposal=[],coordinator_accepted_new_visual_credit=0)
out=dict(recorded_at=datetime.now(timezone.utc).isoformat(),viewed_pngs=len(rows),
 proposed_distinct_design_families=sum(r['distinct_family_proposed_credit'] for r in rows),coordinator_accepted_new_visual_credit=0,
 production_gate_met=False,policy='31 sources/8 enlarged detail sheets opened. Same carriers, arm widths, overlays and recolors merge. Family labels remain material proposals pending historical semantic pairing; no complete wearable UV/runtime acceptance.',rows=rows)
(D/'review-batch-16.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='rows'},ensure_ascii=False))
