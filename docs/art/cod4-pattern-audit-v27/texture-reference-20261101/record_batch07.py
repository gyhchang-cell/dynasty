"""Manual material readings, layers consolidated; no whole-model visual acceptance."""
from pathlib import Path
from datetime import datetime, timezone
import json

D=Path(__file__).resolve().parent
rows=json.loads((D/'batch-07-candidates.json').read_text())['rows']
notes={
224:('twilight-arctic-fur-leather',224,1,'蓝白碎毛面与红褐宽皮带分区，毛面断边与皮带方扣不同材质；不得把这类短毛碎块铺成普通布料。'),
225:('twilight-arctic-fur-leather',224,0,'白色覆盖区保留毛面细节，底部皮件大多留空；是同套可着色区域图，不是另一套白甲。'),
226:('twilight-arctic-fur-leather',224,0,'褐色扣带及少量白边被单独保留；这是同套覆层，不重复算细带图。'),
227:('twilight-arctic-fur-leather',224,0,'腿区褐色纵向皮条与蓝白毛边分开，宽束带沿一侧延续；上下层仍同套。'),
228:('twilight-arctic-fur-leather',224,0,'仅几片白色毛沿保留，透明区域占多数；不作为独立设计或完整腿甲。'),
229:('twilight-arctic-fur-leather',224,0,'腿面褐色竖条与底边短扣条被分离；同套覆层，只支持分材质阅读。'),
230:('twilight-hot-edge-dark-plate',230,1,'深褐面被少量黄橙硬边包住，内面比边框暗得多；亮边有断点，没有全填黄。'),
231:('twilight-hot-edge-dark-plate',230,0,'腿区橙亮竖边与暗褐内片对应，上下层同族；不由平面图声称实际动态发光。'),
232:('twilight-muted-iron-green-nodes',232,1,'灰褐铁片的大面低饱和，几枚鲜绿小扣集中在明确节点，亮绿面积很少。'),
233:('twilight-muted-iron-green-nodes',232,0,'窄灰褐条与暗缝形成腿甲层次，未把每个关节全染绿；同套第二层。'),
234:('twilight-pale-green-plate',234,1,'浅灰绿甲面配更浅硬边与规则直纹，绿只略染底材；主材仍是金属，不是满身荧光绿。'),
235:('twilight-pale-green-plate',234,0,'腿面浅绿竖板、灰暗接缝，腰带上仅一枚金色扣；不能按腰扣单列新设计。'),
236:('twilight-scale-center-field',236,1,'上区亮绿平面和下区深绿鳞块分明，中央一列较亮鳞片，左右大暗面辅助。'),
237:('twilight-scale-center-field',236,0,'腿区窄长鳞列有统一朝向，层间暗缝留足，沿用同套纹理组织。'),
238:('twilight-dark-green-segment-plate',238,1,'近黑大面内只留稀疏暗绿甲片边和少数绿点，右侧少量斜片；低亮度不等于整体刷黑。'),
239:('twilight-leaf-overlap-armor',239,1,'叶形亮片在深绿底上沿不同方向交叠，主叶片明显大于小纹点；不是把全身填成棋盘格。'),
240:('twilight-leaf-overlap-armor',239,0,'腿面少数斜叶亮簇穿过竖向暗底，主体仍有大块留白；属于同套。'),
241:('twilight-white-blue-hard-seam',241,1,'大白灰毛/布区域由粗蓝接边和腰带分开，中央暗口、几条粗折明暗足以读层次。'),
242:('twilight-white-blue-hard-seam',241,0,'腿面白灰宽块与蓝色断续缝带对应，笔粗统一；同套腿层不另算。'),
243:('malum-black-violet-hunter',243,1,'深黑大片围住有限紫缝，长横线中间有几个折角，胸处两条窄紫片，亮点层次较弱。'),
244:('malum-purple-edge-steel',244,1,'紫色亮边包黑板，宽窄变化明显，少数方孔/方扣分断横带；与满紫填面不同。'),
245:('malum-pale-violet-stronghold',245,1,'白紫亮块聚在少数边和分岔，暗紫主面很稀疏；图集中另有色条，但绑定用途不能靠颜色猜。'),
246:('malum-pale-violet-stronghold',245,0,'仅上角一小块白紫稀疏覆层有像素，其他全透明；不能当一套白色盔甲。'),
247:('malum-purple-edge-steel',244,0,'新图集紫边更细、组件更多，但仍是黑板紫边组织；古版与重铸版先合并，不因分辨率变化加数。'),
248:('malum-black-violet-hunter',243,0,'重铸图紫色分布仍局限于黑衣边和少数斜线，岛更碎；与古猎装保守合并，完整模型差异尚待核。'),
249:('goety-crypt-short-segment-trim',249,1,'灰色短柱、断续横条与少量斜折拼接，大部分透明；节段比画连续亮框更克制。'),
250:('goety-crypt-short-segment-trim',249,0,'几根短粗灰竖条和下方稀疏断线，裤层与上层同一节奏；不重复计上下层。'),
}
for r in rows:
    n=int(r['reference_id'].split('-')[1]);family,rep,credit,note=notes[n]
    r.update(status='VISUALLY_REVIEWED_LOCAL_NOT_COORDINATOR_ACCEPTED',semantic_family=family,
        family_representative=f'VIS-{rep:03}',distinct_family_proposed_credit=credit,
        observation_zh=note,scope='equipment_material',
        inspected_detail_view='build/art-reference-20261101/batch07-malum-detail.png' if 243<=n<=248 else r['review_sheet'],
        limitation='Actual atlas/material reading, not verified face/geometry binding, item icon matching, 3D front/back/side, emissive behavior or game acceptance. Layers, dye masks, glow and old/reforged variants conservatively merged.',
        coordinator_accepted_new_visual_credit=0)
out=dict(recorded_at=datetime.now(timezone.utc).isoformat(),viewed_pngs=len(rows),proposed_distinct_design_families=12,
    coordinator_accepted_new_visual_credit=0,production_gate_met=False,
    policy='27 actually viewed PNGs, 12 provisional material families; historical same-equipment review separate, no automatic full-UV or per-set gate contribution.',rows=rows)
(D/'review-batch-07.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
prior=json.loads((D/'prior-batch07-pairs.json').read_text())
compare={
224:('HOLD_VARIANT_OR_VERSION_BINDING','旧图标纯褐皮形，完全没展示现图集蓝白毛面；同名不证明相同材质变体。','不能宣称此对已确认同图案；待来源版本/覆层绑定核清。'),
234:('ALREADY_STUDIED_EQUIPMENT_CASE','旧图标灰绿大板和阶梯白高光，现图集同浅绿金属板分区。','同 knightmetal/knightly 装备复查，文件名变化不自动新增案例。'),
232:('ALREADY_STUDIED_EQUIPMENT_CASE','旧图标灰褐板上有三处鲜绿扣点；现图集仍用少量绿节点配灰褐面。','节点主次作为同案例材质补读，不重复计图标和图集。'),
236:('ALREADY_STUDIED_EQUIPMENT_CASE','旧图标中央较亮绿鳞列、左右暗绿；现图集延续中央鳞列与暗侧。','同套设计，腿层/头/靴图标不另加一套。'),
239:('ALREADY_STUDIED_EQUIPMENT_CASE','旧图标斜向绿叶大块、浅绿边；现图集多面分布同类交叠叶片。','叶片方向可学习，但与旧 steeleaf 同案例。'),
241:('ALREADY_STUDIED_EQUIPMENT_CASE','旧图标白灰大面和蓝色粗缝/腰线；现图集颜色分区与接边一致。','同套材质补读，不把白块和蓝边拆为两种设计。'),
244:('ALREADY_STUDIED_EQUIPMENT_CASE','旧图标紫色分层板和黑色缝口，现古版图集同黑板紫边。','仅确认 ancient 同案例；重铸与古版保持合并，未声称模型完全相同。'),
245:('ALREADY_STUDIED_EQUIPMENT_CASE','旧图标浅紫上板与深紫下板，亮紫小点集中下段；现图集也是浅紫边与暗紫板，但分岛细得多。','同装备复查，不按像素密度增加案例；色条用途及发光行为未实测。'),
}
for r in prior['rows']:
    n=int(r['current_reference'].split('-')[1]);decision,note,limit=compare[n]
    r.update(status='VISUALLY_RECHECKED_SAME_AGENT_NOT_INDEPENDENT_ACCEPTANCE',novelty_decision=decision,
        slot_comparable=True,observation_zh=note,application_limit_zh=limit,accepted_credit=0)
prior.update(recorded_at=datetime.now(timezone.utc).isoformat(),prior_icons_actually_reopened=8,
    same_case_reuse=7,variant_binding_pending=1,new_credit=0,
    reviewer='same agent second pass, not coordinator acceptance')
(D/'prior-batch07-semantic-review.json').write_text(json.dumps(prior,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(opened=len(rows),material_family_proposals=12,old_icons_reopened=8,reused_cases=7,held_variant=1,accepted_credit=0)))
