"""Actual vanilla-mask reading, explicitly separate from other-mod or target gate credit."""
from pathlib import Path
from datetime import datetime, timezone
import json

D=Path(__file__).resolve().parent
rows=json.loads((D/'batch-09-candidates.json').read_text())['rows']
N={
281:('EXCLUDE-blank-base',281,0,'整片白布只带纵向浅折层，无身份内纹。','底坯不算专属设计。'),
282:('vanilla-banner-plain-frame',282,1,'粗度一致的矩形边框围大暗心，图集并排两份同形。','可借外框与中央留白比例，不将两份图案计成两个。'),
283:('vanilla-banner-brick-bond',283,1,'短矩块隔行错位，横缝不断、竖缝交错，图案主次稳定。','仅学块片错缝；这是平面纹样，不是建筑案例，也不用于给甲胄满铺密砖。'),
284:('EXCLUDE-generic-filled-disc',284,0,'两个同样的实心圆点，外缘以阶梯逼近。','仅校准粗像素边；通用圆点不充当逐星完整身份。'),
285:('EXCLUDE-unrelated-creeper-face',285,0,'两方眼和下方缺口嘴，空白负形清楚。','可看负空间读形，不复刻原版苦力怕脸作为原创王朝纹章。'),
286:('goety-branched-cross-central-square',44,0,'两组斜直带交叉成 X，中部留下窄菱空，边沿台阶连续。','与交叉构图保守合并；不因白色/旋转另算。'),
287:('vanilla-banner-indented-frame',287,1,'边框向内作几处大台阶凹口，中央开口仍大，转角不过密。','可借大凹口打断长边，不能画成平滑蕾丝或把每个缺口算新图。'),
288:('vanilla-banner-diagonal-field',288,1,'白填区沿长对角断开，中央形成尖三角暗口。','只学斜向面积关系；四个方向/反相文件保守合并，不算四例。'),
289:('vanilla-banner-diagonal-field',288,0,'与上一张相反方向的斜分区，白三角朝下。','同族翻转，不能增加独立设计。'),
290:('vanilla-banner-diagonal-field',288,0,'一侧由直角三角白面填入，尖端指向中下。','同斜分区移位/反相版本；不另计。'),
291:('vanilla-banner-diagonal-field',288,0,'相反侧的白三角沿同样坡度抬起。','同族镜像，不自动复制到不对称符字上。'),
292:('vanilla-banner-block-rosette',292,1,'方形空心中央外接粗短放射齿，主纹很小但中心和外齿能分。','可借中心留孔与四周短齿层级，不搬原版花标像素。'),
293:('EXCLUDE-unrelated-world-emblem',293,0,'小地球样轮廓内有不规则白块，外框断续。','与现有方令/云折/星翎主题无直接联系，不按复杂程度加数。'),
294:('EXCLUDE-gradient-mask',294,0,'上白下透明逐行连续衰减，底部没有硬分区。','即使来自原版，也不符合用户当前拒绝模糊渐变的贴图要求。'),
295:('EXCLUDE-gradient-mask',294,0,'上一渐变上下反转，白亮集中下方。','同一渐变反向，既不另计也不沿用到原稿。'),
296:('EXCLUDE-primitive-half-field',296,0,'上半填白下半空，只有一条硬横分界。','通用半面/移位作为基线，不充当独特学院设计。'),
297:('EXCLUDE-primitive-half-field',296,0,'下半填白，顶部另有窄白条。','反相/移位不新增；窄条属于图集内容，未核 UV 前不报多余白线 bug。'),
298:('EXCLUDE-primitive-half-field',296,0,'左半白面并排重复两份，右半留空。','横竖方向变化与重复不新增案例。'),
299:('EXCLUDE-primitive-half-field',296,0,'右侧白块与薄边形成两侧不等宽带。','同分区族；不能据平面位置直接认定实际左右身体。'),
300:('EXCLUDE-brand-symbol',300,0,'两个重复的带圆缺口品牌形。','品牌轮廓不作为原创纹章参考计数。'),
301:('EXCLUDE-unrelated-piglin-face',301,0,'小横框中两根直白柱，轮廓像鼻部符号。','不把非当前主题的原版脸谱移作帝王符字。'),
302:('malum-closed-lozenge',59,0,'两枚细长实心菱形，最大宽度居中，上下尖端台阶递减。','沿已读菱形组织合并；填实/并排不增加新学院符。'),
303:('EXCLUDE-unrelated-skull',303,0,'方颅与交错骨，颅骨内留出眼口小孔，图集重复两份。','读形方法可学，当前不需骷髅徽记，排除当前身份门槛。'),
304:('vanilla-banner-repeated-narrow-pales',304,1,'等宽细白竖条均匀间隔，顶部连续到底部，暗间距与白条接近。','只学均匀条带和留缝；本项目小 UV 面不可照搬全部条数造成密纹。'),
305:('EXCLUDE-shifted-square-primitive',305,0,'下角小矩形块并排重复，顶部有细短线。','四角移位是同一矩形原语，不分别计设计。'),
306:('EXCLUDE-shifted-square-primitive',305,0,'另一侧下角矩形移位，填面与细线关系相同。','同原语移位，不另计。'),
307:('EXCLUDE-shifted-square-primitive',305,0,'顶部一侧两块竖矩形，其余留空。','矩块换角不新增语义。'),
308:('EXCLUDE-shifted-square-primitive',305,0,'顶部矩块换到相反侧。','同族镜像；不作为不同肩章设计。'),
309:('goety-branched-cross-central-square',44,0,'粗竖条与横条正交，中心填白，图集两份同形。','交叉原语只校准线宽；和既有交叉族合并，不作新符。'),
310:('EXCLUDE-shifted-bar-primitive',310,0,'底部宽白横带，顶部还有一条窄边。','边带位置不自动决定腰带实际 UV；未绑定不下结论。'),
311:('EXCLUDE-shifted-bar-primitive',310,0,'两根同样的中间竖带，旁侧透明。','横竖方向变化不增加完整设计。'),
312:('EXCLUDE-shifted-bar-primitive',310,0,'两条宽斜带相向展开，像顶端合拢的折线。','仅校准台阶坡度；原图内重复与转向不另计。'),
313:('EXCLUDE-shifted-bar-primitive',310,0,'上一斜带方向反转，底部合拢。','同斜带翻转，不另计。'),
314:('EXCLUDE-shifted-bar-primitive',310,0,'左侧竖白带与右侧重复块间距大。','同直条移位，不能按不同槽位扩成新参考。'),
315:('EXCLUDE-shifted-bar-primitive',310,0,'一条水平细白带跨过两份纹样区域。','通用横条不算独特甲带或符字。'),
316:('EXCLUDE-shifted-bar-primitive',310,0,'右侧竖带，左端另有短横边。','移位/反相仍同原语，未核面向不报错。'),
317:('EXCLUDE-shifted-bar-primitive',310,0,'顶部宽横白带，中间有浅竖折。','同直带换顶，不增加设计。'),
318:('down-wedge-stem',162,0,'底部实心三角向上突起，边沿按等节奏台阶收窄。','与已有三角方向头保守合并；朝向颠倒不算另一个学院。'),
319:('down-wedge-stem',162,0,'两枚顶部向下的实心三角，留空端朝下。','与上一三角翻转且重复，不另计。'),
320:('vanilla-banner-stepped-teeth-hem',320,1,'底边一排等节奏短尖齿，尖端和谷底宽度克制。','可借羽片/鳞边的粗重复节奏；一个图案的多齿不拆计，也不复制原图。'),
321:('vanilla-banner-stepped-teeth-hem',320,0,'上一排齿翻到上边，齿尖向下。','同齿边翻转，不能再算一套。'),
}
for r in rows:
    n=int(r['reference_id'].split('-')[1]);fam,rep,credit,note,limit=N[n]
    r.update(status='VISUALLY_REVIEWED_VANILLA_BASELINE_NOT_OTHER_MOD_GATE',semantic_family=fam,
        family_representative=f'VIS-{rep:03}',distinct_family_proposed_credit=credit,
        scope='vanilla_pixel_pattern_baseline',observation_zh=note,limitation=limit,
        inspected_detail_view=r['review_sheet'],applicable_targets_proposal=[],
        other_mod_case_credit=0,coordinator_accepted_new_visual_credit=0)
out=dict(recorded_at=datetime.now(timezone.utc).isoformat(),viewed_pngs=41,
    proposed_distinct_design_families=7,coordinator_accepted_new_visual_credit=0,production_gate_met=False,
    policy='Actually opened41 source masks, only7 coarse baseline composition groups proposed. Rotations/positions/paired atlas copies are not cases. Vanilla is not1000 other-mod armor; no current target credit or production.',rows=rows)
(D/'review-batch-09.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(opened=41,coarse_baseline_families=7,other_mod_case_credit=0,accepted_credit=0)))
