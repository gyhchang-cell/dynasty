"""Record actual visual study; neither damage variants nor mood establish credit."""
import hashlib
import json
from pathlib import Path
OUT=Path(__file__).resolve().parent
BASE=OUT.parent
def sha(b):return hashlib.sha256(b).hexdigest()
def get(p):return json.loads(p.read_text())
def evidence(p):return dict(path=str(p.resolve()),sha256=sha(p.read_bytes()))
def dump(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
    tasks=Path('/Users/a15356015027/Desktop/code x提示词')
    excerpts=[]
    for name,numbers in [('cod4.txt',[21]),('cod2.txt',[231,368,369,712])]:
        p=tasks/name;lines=p.read_text().splitlines()
        excerpts.append(dict(source=evidence(p),lines=[dict(line=i,text=lines[i-1]) for i in numbers]))
    dump('task-use-boundary.json',dict(excerpts=excerpts,
        selected_reason='荒村/义庄/墓地场景所需完整残存空间与小型祭祀组织；本地haunted_ruin只有可能线索，实际研究后不能凭名称录取。',
        original_scope='COD4-1/11/13: 义庄、墓地配套场景；村落小型祭祀空间与墓园的空间组织参考',
        broader_abandoned_scene_not_silently_added_to_formal_scope=True,ecology_or_morgue_acceptance_not_implied=True))
    common=dict(formal_credit_added=0,proposed_credit=0,independent_human_review=False,
        native_generation_or_collision_verified=False,source_evidence=evidence(OUT/'sources.json'),
        author_evidence=evidence(OUT/'author-context.json'),family='047-HAUNTED-RUIN-ALTERNATIVES-NOVELTY-UNRESOLVED',
        decision='HOLD_ZERO_RELEVANT_FUNERARY_OR_RITUAL_USE_AND_DISTINCT_DESIGN_UNPROVEN')
    observations=[dict(
        layout='15×15底盘上为多段矩形残墙、局部直立墙柱与中心/侧边开口；北侧较完整小围合和南侧断墙形成疏密差，箱在(4,2,4)，头颅/发射器另在(7–8,1–2,8–9)。没有独立停棺间、墓列或明确祭坛的用途证据。',
        proportion='保存15×10×15，原非空气界x0–14/y0–7/z0–14，实占8高；上部y8–9为空气，不能把保存10高称可用楼层。断墙强弱与留白可学，但残损和尺寸差不能单独成为新建筑。',
        facade='整体两方向可见多段开敞门形/洞形残墙及孤柱，没有普通门、栅栏门或jigsaw道路端。残墙之间空白只说明原坐标有air，不是已验入口/可通行的屋门。',
        roof='上方有石楼梯、半砖与墙块形成的残梁/断顶轮廓，没有连续完整屋盖；不将楼梯轮廓说成通往二层，不复原未保存的屋顶或中式飞檐。',
        materials='草218、灵魂沙41、缠根土38、石按钮36、虫蚀石砖21等；7块TNT在y0，陷阱箱1、向上发射器1、红石线2、player_head与骷髅头各1。发射器存金粒/剑/红石/盾的物品，头颅无作者皮肤信息；不把头颅和灵魂沙当墓葬证明。',
        circulation='y1地表补丁、y2残墙与整体低切显示多个侧向间隙；无原模板jigsaw、梯、门。陷阱箱南向，TNT埋在其附近下方；仅保留状态，不推定电路已触发、行走安全或外围连续可达。',
        terrain='完整单模板由haunted_ruin根池直接选取，rigid，WORLD_SURFACE_WG与beard_thin尚未执行；生物群系标签有平原/森林及可选fortified_village标签，后者是群系适用范围，不证明属于实际村落。monster空列表与已存illusioner实体并存，不混为没有敌人。'),
        dict(
        layout='同15×15残墙场地，残墙较低，中心(6,2,6)陷阱箱周围8个点布红蜡烛，四向与斜向对称成环。专门看原坐标y0/1/2图确认了环形组织；中心原物是宝箱而非棺材/祭坛，不将灯环或illusioner直接认作祭祀。',
        proportion='保存15×11×15，原非空气界x0–14/y0–5/z0–14，实占6高；比另两份少高残墙、上方多空气。不能把保存高度11当建筑更高，也不靠更严重残损多算一个设计。',
        facade='两侧残墙和低石圈围合中心，周界多断口，屋体立面仅剩局部柱/短墙。箱面向西，蜡烛环不能等同独立建筑围墙或独立墓园入口。',
        roof='没有完整屋盖，少量残存水平石构与阶梯状短墙表明废墟状态；露天中心与残墙属于同模板。没有把断顶中的每组构件分别算祭台、殿堂和墓室。',
        materials='草222、灵魂沙55、缠根土44、砂砾色花岗岩半砖25、石按钮20；8个red_candle均lit=true/candles=1、水浸false，箱为simple_dungeon战利品。y0在(5,0,6)/(6,0,6)/(7,0,6)有3块TNT，不把原蜡烛环改说为七星灯或殡葬用品。',
        circulation='蜡烛占(4,2,6)/(5,2,5)/(5,2,7)/(6,2,4)/(6,2,8)/(7,2,5)/(7,2,7)/(8,2,6)，中心箱(6,2,6)。分类整格图与原状态分层共同证明相对组织，未证明蜡烛/箱/半砖碰撞下连续可走；TNT机关无运行验收。',
        terrain='与F01/F03共享同一根/池/群系/处理器选择链，三元素均weight2且各为single_pool_element；选一种完整模板，不是三个拼成一座。minecraft:mossify_20_percent本Jar未包含对应JSON，不能称ID失效或苔化已实测。'),
        dict(
        layout='15×15场地内较长的线性残墙与端部小围合相接，中部孤柱/门形断梁围出局部狭长间隙，箱在(5,2,8)。虽与F01残墙分布不同，尚不能排除同底稿的损坏/摆放变体，也没有明确棺室/墓列/祭坛用途。',
        proportion='保存15×10×15，原非空气界x0–14/y0–7/z0–14，实占8高；较完整长墙与低断墙形成高低对比。与F01等大、与F02实高不同都只是观察，未给出独立完整相关设计信用。',
        facade='长向墙片、较高端墙和孤柱从两方向可辨，低层空白与残墙缺口连接，但无普通门或拼图入口。未将遗迹的视觉开口认作原生进出路线通过。',
        roof='高处石楼梯/半砖拼成断裂水平顶边及梁状残段，主体敞顶；不是完整檐口或可站屋面。未按残顶段数另计建筑。',
        materials='草220、缠根土55、灵魂沙51、粗泥30、石按钮26、花岗岩半砖25，陷阱箱1。5块TNT在y0围(5,0,8)呈十字，箱同x/z位于y2；与F01/F02机关摆放差异不证明建筑类型不同。',
        circulation='北向陷阱箱邻接低层空白和柱墙，整体低切显示狭长通道可能性；无梯、门或jigsaw，只有原楼梯状态的残墙不能证明上下楼路线。原illusioner在(4.5,1.875,7.5)，实体未绘入整格图，未验证战斗/掉落/过门碰撞。',
        terrain='单模板边界和无jigsaw出口与共享根池相符，可只读研究完整遗迹场景；不据size7推定还会拼出村落或墓园。原草/土/灵魂沙补丁与WORLD_SURFACE_WG/beard_thin地形融合未实机验收。')]
    entries=[]
    for i,obs in enumerate(observations,1):
        ident=f'F{i:02}'
        images=[evidence(OUT/(ident+s)) for s in ('-whole.png','-plan.png')]
        if ident=='F02':images.append(evidence(OUT/'F02-original-layers.png'))
        entries.append(dict(common,id='047-'+ident,observations=obs,actual_images_viewed=images,
            relevance_limit='完整原残存场景可研究；原任务所需墓地配套/义庄/小型祭祀用途缺证，三份残损变体的独立设计资格也未确认，全部0。'))
    old=BASE/'research-20261101-dungeons-001'
    dump('manual-review.json',dict(batch=47,date='2026-11-03',entries=entries,
        actual_templates_visually_studied=3,actual_new_images_viewed=7,
        actual_old_comparison_images_viewed=[evidence(old/'F06-whole.png')],old_comparison_source=evidence(old/'sources.json'),
        semantic_families_newly_confirmed=0,alternative_set_groups_observed=1,semantic_family_identity_resolved=False,
        semantic_dedup='无历史精确匹配且有426/589/453处原状态或缺失差异，不自动代表三个新设计；实看同为15格底盘残墙废墟，谨慎保留为一组替代模板，未确认独立建筑家族。旧stray_ruins已看整体对比，仅积雪/残损或机关差不能再计。242历史archive/member对不是242个参考。',
        proposed_first_scope_admissions=0,formal_credit_added=0,production_changes=0,checklist_deletions=0,
        generated_not_claimed_viewed=['F01-vertical.png','F02-vertical.png','F03-vertical.png'],
        applicable_lessons=['残墙高度递减与地面材料补丁可提示破败程度，但用途应由空间功能和内容共同支持。',
            '中心—环形布置应记录原坐标与中心物用途；对称灯环不能自动改写成殡葬或七星灯设计。',
            '陷阱箱、地底TNT和存档实体须与场景一起审读，研究图不能替代动线、碰撞与机关验收。']))
    prior=BASE/'research-20261103-funerary-046/scope-status.json';scope=get(prior)
    scope.update(batch=47,prior_scope_status=evidence(prior),current_batch_proposed_credit=0,
        current_batch_old_case_retained='D010 remains hold0 in sealed043',pending_proposal_identities=[])
    dump('scope-status.json',scope)
    dump('session.json',dict(date='2026-11-03',owner='做建筑的',batch=47,status='REVIEWED_THREE_HAUNTED_RUINS_HOLD0',
        previous_receipt=evidence(BASE/'research-20261103-funerary-046/RECEIPT.json'),formal_funerary_baseline=150,
        new_first_scope_proposals=0,production_allowed=False,
        next='haunted_ruin三替代模板用途和独立设计资格不足，保留原记录0；继续固定本地可核查、用途边界明确的同范围完整来源。不要把残损、灯环或扫描凑数；源内缺入口/用途原证则保持0。',
        shared_coordinator_session_not_overwritten=True,coordinator_only_main_checklist=True,
        java_run=False,game_run=False,network_requests=0,no_automation=True,duration_hours_claimed=0))
    (OUT/'HANDOFF.md').write_text('''# 第47批：ATi三份闹鬼废墟原稿核查，全部暂不计入

对固定本地ATi原包实际读取3份完整遗迹模板、根结构/模板池/群系标签、存档实体、方块状态与机关，逐一查看6张新整体/切层图，另看1张原坐标重点图和1张既有stray_ruins对比图。新增图实看7张；三张竖切仅生成、不冒充实看。

- 三份保存尺寸为15×10×15、15×11×15、15×10×15，非空气实高为8、6、8。多个残墙、孤柱和断梁组织可读，但没有明确义庄停棺、墓列或墓园配套用途。三份为同池等权替代模板，无jigsaw，不拼成一座村落。
- F02确有8个点燃红蜡烛对称环绕(6,2,6)陷阱箱；中心是simple_dungeon战利品箱，下方y0有3块TNT。保留灯环的实际布局观察，不改说成七星续命灯或已证实祭坛。F01/F03另有7/5块TNT；机关、碰撞及存档illusioner均未运行验证。
- 三份原状态差异不自动构成三个不同设计；与旧雪地stray_ruins也作整体比较，不拿残损、积雪、换材或机关变化凑数。242历史archive/member对只是机器辅助范围。三候选当前新增正式参考0、提案0，独立家族资格也不宣称已证实。
- 根结构WORLD_SURFACE_WG、beard_thin和rigid均保留未执行边界。minecraft:mossify_20_percent处理器原ID保留，本Jar缺其定义不是断言全运行环境缺失。包名写1.4.2、内manifest写1.4.0且Forge显示名/URL不一致，均保留原文，不据此伪造版本或作者来源。

七项观察、原任务用途摘录、原始上下文、去重与验证均在本包。正式义庄/墓地/小型祭祀参考仍为150/1000，缺850；未达到门槛，不开始建筑制作。036原高度范围hold0、D010入口/地形缺证均保留。

只写本047研究包，不重写046或更早收据，不改正式登记、主清单、共享session/Jar或游戏资产，不运行Java/游戏，不联网，不动声音/亮度/焦点；没有任务达到完成验收条件，清单删除0，不声称10小时。
''')
    print('Saved three original haunted ruins, seven new images plus one old comparison; hold0.')
if __name__=='__main__':main()
