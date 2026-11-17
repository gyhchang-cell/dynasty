"""Four equipment source families;43component/layer PNGs never43cases."""
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import json
D=Path(__file__).resolve().parent;rows=json.loads((D/'batch-21-candidates.json').read_text())['rows']
notes={
789:'下部灰白棋格网片与一条阶梯细边，非整块高亮铠板。',790:'金褐覆层分为方框头区、短肩带、下沿起伏板和几处方钉，中心大留空。',791:'只有一小绿色点岛与金橙短梯形岛，不凭小岛猜实际宝石/腰扣位置。',792:'只有两处白色短岛，主体透明，不报整套缺图。',793:'金黄V叉与两条上弯短尖，是覆图局部，不是独立甲。',794:'披风一明一暗两块分别用几阶大斜色片，没有密集布噪点。',795:'橙金披风边为两条宽窄不同倒U框，中心透明；不算第二条披风。',796:'腿下层白灰板与宽短条，大面只少量灰方阴影。',797:'金色覆层是断续斜短块和稀疏横片，中心透明多。',798:'组合基础层包含金橙小岛、绿色点、白灰网格与白短岛，和部件同族。',799:'组合金覆层收齐同方框头/肩短条/下沿，不另算第二套神圣甲。',800:'第二层同白腿面源，多文件不扩装数。',801:'第二层金覆层同断续短块，不增加套数。',
802:'银板以两三档灰、较宽边与少量亮铆钉，大片黑棋格和深棕束材独立。',803:'头/上身区域银灰折面与黑色中槽，底部粗带扣/白铆钉分明。',804:'白灰短带与黑白块只占小岛，不能把整个透明区判作手臂漏贴。',805:'下腿为低对比深棕宽片与几处孔块，不当银金属。',806:'腿上片深灰棋格、三角折口和一块宽暗片，边界硬。',807:'单条灰斜短杆源图只有局部像素；不因独立文件叫新装备。',808:'组合层保留银板、黑格内衬、棕带，亮点只在部分板角。',809:'第二层棕大面与灰黑格为下部同材，不另算裤装套。',
810:'袍基础面有大白灰布面和少数宽褶影，色差低，没有花纹满铺。',811:'alpha全零的袍下部overlay，占位不增新案例，也不能凭此断言错误。',812:'长白短岛与齿边白条，灰线疏，不从此单图猜完整袍长。',813:'金环/红褐直边和两处L折端，覆图中央大留空。',814:'白灰长面以竖折块表示布褶，边为短横岛。',815:'alpha全零腿下overlay，排除新增数。',816:'alpha全零腿中基础图，排除新增数。',817:'只有金黄和红褐L形细边，和基础腿面分材。',818:'组合袍白灰布面与原body_lower同组织，非第二套白甲。',819:'组合覆层只有同金环/红褐边/长横边，不能脱离底衣当完整袍。',820:'组合腿白灰面为同袍腿片，不另算。',821:'组合腿覆图为同L折边，不另算。',
822:'战士底材为棕灰棋格网片、暗棕短带，和银板层分开。',823:'银灰大板用少量棱角高光，灰暗中槽与很少白点，轮廓依赖板片留孔。',824:'褐色宽V束带与右侧银小片分开，斜线以单阶梯线读出。',825:'棕披风用一明一暗宽斜折，布面留大底，不用现代徽记大贴纸。',826:'白灰U形横部件弯端只有几块，细节服从大弯。',827:'腿下部低对比深棕片与孔带，未据名字认定实际靴区。',828:'银腿板用两三灰方块/白端头，少量高光保留大平面。',829:'一组灰网条与一条褐带，分离小片属于同裤层。',830:'组合战士基础层把银板、棕V带和灰棕网格并存，材质边界清晰。',831:'腿组合层同银板、棕带、灰网片，不增加装备数。'}
for r in rows:
 n=int(r['reference_id'].split('-')[1]);im=Image.open(r['local_path']).convert('RGBA');alpha=im.getchannel('A')
 if n<=801:family,rep='immersive-divine-panel-gold-trim',789
 elif n<=809:family,rep='immersive-heavy-silver-dark-binding',802
 elif n<=821:family,rep='immersive-robe-sparse-colored-borders',810
 else:family,rep='immersive-warrior-silver-net-v-strap',822
 blank=alpha.getbbox() is None
 r.update(status='VISUALLY_REVIEWED_SOURCE_CONTEXT_ONLY',semantic_family='EXCLUDE_TRANSPARENT_COMPONENT_PLACEHOLDER' if blank else family,scope='equipment_material',distinct_family_proposed_credit=int(n==rep),observation_zh=notes[n],
   source_alpha_bbox=alpha.getbbox(),source_partial_alpha_pixels=sum(0<v<255 for v in alpha.get_flattened_data()),applicable_targets_proposal=[],coordinator_accepted_new_visual_credit=0,
   limitation='部件/组合层/覆图同装备合并，图存minecraft命名空间仍来自本模组JAR，不冒充原版。只看源PNG，不推断染色、模型绑定或游戏效果；完整帝王/护卫/装备UV门槛不据此满足。')
 if not blank:r['family_representative']=f'VIS-{rep:03}'
out=dict(recorded_at=datetime.now(timezone.utc).isoformat(),viewed_pngs=43,proposed_distinct_design_families=4,coordinator_accepted_new_visual_credit=0,production_gate_met=False,
 policy='All4overview and11integer-detail pages opened. Three transparent component placeholders excluded. Four equipment groups, not43unique designs; history pending.',rows=rows)
(D/'review-batch-21.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print('Recorded43raw/4material groups/3transparent excluded/0accepted.')
