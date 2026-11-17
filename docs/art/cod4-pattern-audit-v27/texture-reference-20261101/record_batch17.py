"""Twenty-five actual sources reviewed; zero new semantic design proposals."""
from pathlib import Path
from datetime import datetime,timezone
import json
D=Path(__file__).resolve().parent
rows=json.loads((D/'batch-17-candidates.json').read_text())['rows']
notes={
586:'同类斜置卷轴，金褐卷边围深灰纸面，中央只是几笔金黄折线；卷边高光大块而非均匀描白。',
587:'同类卷边换橙白、紫红，内纸面零散多彩短点；色相变化多于稳定身份纹样，不能充学院构图。',
588:'红卷边、灰紫底纸中是模糊可辨的方折暗线；不凭 cursed 名字臆造符文含义。',
589:'近黑卷边和灰黑纸面之间只有少量灰块区分，轮廓可读但内符弱，不作为当前身份纹样范本。',
590:'青白卷边围灰纸面，中心白短线/蓝点像小星簇；同卷轴载体不另计套装或护卫纹样。',
591:'16x96有六块源帧，逐帧看是粉紫卷边与白粉小符变色；mcmeta只列0、1、2、1，不推断下三块实际播放。',
592:'紫蓝纸面内为浅蓝宽短笔与点，棕红卷边沿相同轮廓；只保留大色块组织观察，不作独立学院符。',
593:'四角金爪围中央绿方宝石，左右浅金块很宽；这是通用宝石框，不能自动认作帝王纹章。',
594:'棕黄卷轴几乎不画内符，靠浅褐大折面与暗右缘分厚度；是留白材料参考，不是纹样案例。',
595:'同斜卷轴的亮绿卷边、青灰小符，中央笔画与多张同形纸符近似；不因 xp 名称拆新体系。',
596:'与595同卷轴载体，外边绿、内符青，形态差别有限；同系列状态不当独立符面设计。',
597:'青长竖居中，红金四角与下端绿宝石分区，深灰底架；只作色块主次反例/材料观察，不照搬徽章。',
598:'两块源帧都是绿卷边、白灰纸与蓝色中央点，仅局部亮点移位；mcmeta开启17tick插值，静态硬像素不代表播放过程硬切。',
599:'绿色卷边围棕纸，中央红橙菱斑；单一元素亮斑与载体换色不增加独立纹样。',
600:'紫卷边、蓝纸面、绿缺口环，形状是通用开环；不因 night 名称把它解释成学院星图。',
601:'两块源帧都是褐卷边与橙黄亮芯，亮芯稍变化；mcmeta23tick插值，未渲染中间帧或判断游戏发光。',
602:'灰紫卷边、棕纸内浅青白斜线与短点，颜色组织比专属符形明显；不把源图当雷符成稿。',
603:'unused路径是灰黑框、红四角、中央灰竖件，和当前597不同；未证注册引用，排除运行时案例。',
604:'四块源帧为灰卷边内紫色空心长环，上端灰小块逐帧变化；0帧55tick后1/2/3/2/1短动，不能当四个符面。',
605:'灰石坯上粉色顶拱、横线与下垂三脚，已与旧VIS159/060/067实际放大比较；但旧1000物品索引已经含同源arcane_stone，PNG哈希也一致，零新增。',
606:'同灰石坯内橙色粗火形、少量黄色亮芯，通用元素象形，不具有当前学院身份；不扩成完整目标案例。',
607:'同石坯内白青八向/格状雪形，几条粗线和少量灰缺口；仅元素符号，不复制原版式充新纹样。',
608:'同石坯中绿色十字横竖在中心叠亮绿块，负空间大；基础十字不充独立完整设计。',
609:'同石坯里黄色折闪，中心亮黄块宽于下方折尾；已知闪电折符的通用构图，不加族。',
610:'同石坯里青白火/魂状轮廓，深灰小眼点与白顶角；生物/元素象形不适用现有指定身份。',
}
for r in rows:
 n=int(r['reference_id'].split('-')[1])
 family='EXCLUDE_COMMON_SCROLL_CARRIERS_AND_COLOR_STATES' if n<=604 else 'EXCLUDE_GENERIC_ELEMENT_STONES'
 if n==603:family='EXCLUDE_UNUSED_UNBOUND_INSIGNIA'
 if n==605:family='EXCLUDE_HISTORICALLY_REVIEWED_ARCANE_STONE'
 r.update(status='VISUALLY_REVIEWED_SOURCE_CONTEXT_ONLY',semantic_family=family,
  distinct_family_proposed_credit=0,scope='pattern_context',observation_zh=notes[n],
  limitation='只观察源PNG；共享载体、状态帧、旧来源和通用元素不新增完整设计。未验注册/运行时、目标身份或三维UV。',
  applicable_targets_proposal=[],coordinator_accepted_new_visual_credit=0)
 if n in [591,598,601,604]:r['inspected_detail_view']='build/art-reference-20261101/batch17-animation/tiles.png'
 if n==605:r['historical_source_reuse']=dict(index='docs/art/accessories-mc-v11/references/sources.json',id='runes:arcane_stone',sha256=r['sha256'],comparison_sheet='build/art-reference-20261101/batch17-rune-prior-compare.png')
out=dict(recorded_at=datetime.now(timezone.utc).isoformat(),viewed_pngs=len(rows),proposed_distinct_design_families=0,
 coordinator_accepted_new_visual_credit=0,production_gate_met=False,
 policy='All three sheets plus fourteen source animation tiles opened. Six source tiles of fabulous_scroll do not imply six scheduled frames; only0/1/2/1 are listed. All25 sources excluded from new proposals.',rows=rows)
(D/'review-batch-17.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
review=dict(recorded_at=out['recorded_at'],actually_opened=True,inspection_sheet='build/art-reference-20261101/batch17-animation/tiles.png',
 source_pngs=4,source_tiles_opened=14,new_design_credit=0,runtime_acceptance=False,
 observations_zh=[notes[n] for n in [591,598,601,604]],
 limitation='仅按原图完整切片，未模拟插值/着色器或调用游戏；下三块未列帧不等同其他代码绝不使用。')
(D/'batch17-animation-manual-review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='rows'},ensure_ascii=False))
