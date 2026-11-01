"""Actual 30 native symbol icons compared to earlier glyph families; conservative reuse."""
from pathlib import Path
from datetime import datetime, timezone
import json

D=Path(__file__).resolve().parent
rows=json.loads((D/'batch-08-candidates.json').read_text())['rows']
N={
251:('EXCLUDE-blank-carrier',251,0,'只有圆石坯和左上单侧硬高光，内部空白。',[]),
252:('malum-fork-hook',49,0,'青色竖干向右上、右下伸短叉，左上两块亮色说明局部厚度。',['chiling_brush','leifu_staff']),
253:('opposed-short-arrowheads',253,1,'上下两条短横的端头反向回折，中间保留暗隙，黄笔亮面只占左上。',['zhenyue_blade','beichen_spear']),
254:('malum-tree-fork',60,0,'紫色粗叉顶连下垂主干，右端略越过石坯内框，仍是叉头主柱组织。',['chiling_brush']),
255:('malum-closed-lozenge',59,0,'青色闭合菱眼中央留孔，上下轴有两个短点，亮段落在左侧。',['chiling_brush','supreme_sword']),
256:('malum-fork-hook',49,0,'紫色折笔横过石坯再往下回收，中央有短支与暗缝。',['chiling_brush','leifu_staff']),
257:('EXCLUDE-empty-overlay-rim',257,0,'只有不完整灰边框，中央透明；是载体覆层，非独立内符。',[]),
258:('goety-branched-cross-central-square',44,0,'蓝色斜叉分数个短端，白亮笔压在左上转折，中心没有全填亮。',['leifu_staff']),
259:('malum-fork-hook',49,0,'红色竖折主干向左右出短横，右下端再折向下；明暗沿同一笔画组织。',['chiling_brush','leifu_staff']),
260:('malum-fork-hook',49,0,'与激活版同红色分叉折笔，仅亮度降低。',['chiling_brush','leifu_staff']),
261:('malum-fork-hook',49,0,'黄绿上叉头连下方回钩，主干中间有两次转折，周围石坯保持一致。',['chiling_brush']),
262:('malum-fork-hook',49,0,'同上一张的绿叉头/回钩，去掉亮黄点后的状态，不是第二套。',['chiling_brush']),
263:('malum-bent-flow',48,0,'黄色折干由上方亮端向下折，再以两条短横向右收，顶部还有侧向小亮段。',['chiling_brush','leifu_staff']),
264:('malum-bent-flow',48,0,'和上一张相同路径的低亮状态；右下短横仍在。',['chiling_brush','leifu_staff']),
265:('malum-fork-hook',49,0,'浅青 Y 状分叉加中部横笔，亮区只在顶端，底端回弯。',['chiling_brush','leifu_staff']),
266:('malum-fork-hook',49,0,'同浅青叉笔低亮变体，主体路径未改变。',['chiling_brush','leifu_staff']),
267:('malum-bent-flow',48,0,'绿顶横折下去形成几段右向台阶，底部短竖笔下垂。',['chiling_brush','leifu_staff']),
268:('malum-bent-flow',48,0,'与上一张相同的阶梯转折，亮绿变暗绿；不重复计状态。',['chiling_brush','leifu_staff']),
269:('open-comb-rune',159,0,'紫色上横与中间短横连斜下短腿，开口向右，仍属开口多横笔。',['chiling_brush','leifu_staff']),
270:('open-comb-rune',159,0,'同符位置不变，紫亮笔降为暗紫；颜色状态不构成新案例。',['chiling_brush','leifu_staff']),
271:('malum-fork-hook',49,0,'青色顶部左右叉与下方短钩，与 air 的主干组织接近。',['chiling_brush','leifu_staff']),
272:('malum-fork-hook',49,0,'同青色叉钩低亮状态，与 air/wind 保守归一族。',['chiling_brush','leifu_staff']),
273:('malum-fire-s',50,0,'红色长折线沿对角下行，中腰有短叉，亮部集中上段。',['chiling_brush']),
274:('malum-fire-s',50,0,'同红色对角折线与短叉，激活/关闭只改变明度。',['chiling_brush']),
275:('paired-post-gap',164,0,'红色两侧粗柱顶部向内收，中央保留灰石间隙，下端一侧折角伸出。',['chiling_brush','supreme_sword']),
276:('paired-post-gap',164,0,'同双柱暗红状态，与已有双柱留缝族保守合并，不新增状态。',['chiling_brush','supreme_sword']),
277:('open-comb-rune',159,0,'蓝色上横/下横由右侧短柱相连，中间留暗口；与开口梳形同类。',['chiling_brush']),
278:('open-comb-rune',159,0,'同蓝色开口笔的低亮版，保留同一暗口。',['chiling_brush']),
279:('linked-top-dual-foot',279,1,'深蓝顶横连接两根有间距的直竖柱，柱脚分别横折，双脚结构不同于单柱叉形。',['chiling_brush','leifu_staff','supreme_sword']),
280:('linked-top-dual-foot',279,0,'同顶横、双柱和折脚，颜色压暗；同一案例的另一状态。',['chiling_brush','leifu_staff','supreme_sword']),
}
for r in rows:
    n=int(r['reference_id'].split('-')[1]);family,rep,credit,note,targets=N[n]
    r.update(status='VISUALLY_REVIEWED_LOCAL_NOT_COORDINATOR_ACCEPTED',semantic_family=family,
        family_representative=f'VIS-{rep:03}',distinct_family_proposed_credit=credit,
        observation_zh=note,applicable_targets_proposal=targets,scope='targeted_symbol_composition',
        inspected_detail_view=r['review_sheet'],coordinator_accepted_new_visual_credit=0,
        limitation='Native icon and coarse glyph composition only. Eleven active/inactive pairs share design; no item-state registration, skill behavior, weapon texture binding or game acceptance inferred. Three older index searches do not establish global semantic novelty.')
out=dict(recorded_at=datetime.now(timezone.utc).isoformat(),viewed_pngs=30,proposed_distinct_design_families=2,
    coordinator_accepted_new_visual_credit=0,production_gate_met=False,
    policy='Thirty actual PNGs opened; blank/overlay excluded; eleven state pairs consolidated; existing cross-source glyph families reused; only two additional structural family proposals, pending historic/global semantic review.',rows=rows)
(D/'review-batch-08.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(opened=30,new_family_proposals=2,accepted_credit=0)))
