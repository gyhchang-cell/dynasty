"""Save actual three-template study, purpose holds and one-family correction."""
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
    tent=dict(
        layout='7×8×30狭长骨构帐篷/拟生骨架式住处，两个端部构件经长条骨木构连接，中间夹家具与工作点。酿造台、箱桶、陷阱箱和营火均为同一整体内容；不把骨架头、端部、每格工作台当独立建筑。',
        proportion='保存及实占均x0–6/y0–7/z0–29；长轴30、窄轴7、最高8，属于横向低构筑物。不能按30长轴称高守望塔，也不强行缩成16格四角哨棚或放大为29–36平面/17–30高驻防堡。',
        facade='长边敞开，骨块、栅栏、柱脚与不同端部轮廓穿插；无普通门。侧面east_up的jigsaw在(6,0,15)为入口对接、pool=minecraft:empty，不能称缺另一半建筑或已接上道路。',
        roof='上部以骨构、毛料/木半砖及石英构件形成疏密不齐的覆盖，非连续大殿屋盖。骨材颜色和skull拼写不证明骸骨墓、祠堂或礼仪用途；没有复原假想缺失屋顶。',
        materials='原F01骨块167、红羊毛37、云杉半砖27、橡木栅栏24、石英半砖15等；酿造台1、TNT1、普通箱/陷阱箱/桶各1。F02只在(3,5,23)由air改为axis=z骨块，骨块168；分类图把半砖/栅栏整格化，非穿模或材质验收。',
        circulation='两张低切层及两方向整体显示狭长构件与局部空隙；梯4格不自动证明连续室内动线。入口拼图对接尚无原生道路/生成验收，显式air保存与可走空间、家具碰撞不能等同。',
        terrain='作者house池直接选择拼写skull的F02，旧skul F01无直接location选择记录；两者都只有empty出口。没有从骨材、酿造台推断宗教或军事用途，也不把未追到结构根的村落选址编成已验。')
    common=dict(formal_credit_added=0,proposed_credit=0,independent_human_review=False,
        native_generation_or_collision_verified=False,source_evidence=evidence(OUT/'sources.json'),
        author_evidence=evidence(OUT/'author-context.json'))
    entries=[]
    for ident in ('F01','F02'):
        entries.append(dict(common,id='046-'+ident,family='046-PIGLIN-SKULL-TENT-ONE-FAMILY',
            decision='HOLD_ZERO_UNPROVEN_RITUAL_OR_GUARD_USE_SAME_TENT_FAMILY',
            observations=dict(tent),relevance_limit='固定村落houses上下文与单个酿造台未给出祭祀、墓地配套或守卫职能。骨材不是用途证明；两近名模板最多同一完整家族，当前全0。',
            actual_images_viewed=[evidence(OUT/(ident+s)) for s in ('-whole.png','-plan.png')]))
    entries.append(dict(common,id='046-F03',family='046-MUSHROOM-BREWING-HOUSE',
        decision='HOLD_ZERO_WORKSTATION_IS_NOT_RITUAL_OR_WATCHPOST_PURPOSE',
        relevance_limit='独立酿造/居住主体可以观察，但村落house池、酿造台及高塔外形不足证明祠堂、祭祀场或守望岗位；不能借17×31×17恰好接近单塔尺寸转入原守卫范围。',
        observations=dict(
            layout='17×31×17方形底盘上是多层集中的竖向主体，中下部有房间、外缘环带及上部收分。酿造台、黑床、书架、疣田/装饰与物品展示框是原房内容；没有将每层或每件头颅饰物各算一实例。',
            proportion='保存及原非空气实占x0–16/y0–30/z0–16，31高包含顶部收束。中间突出环缘和上段收分使轮廓近塔，但用途没有因此成为守望塔，顶部装饰不当驻守楼层。',
            facade='下部浅色框架及多面窗/柱间分隔，中部外挑环缘，上部深色高构件收束；普通门下半在(12,2,8)。图中颜色仅按方块名分类，未证明材料原生外观。',
            roof='顶部尖拱/交叉收分式深色构件与多层檐带处于同一完整模板，中央房体和外挑层次可读。未把它称中式祠堂屋顶、塔楼射击平台或已验可站屋面。',
            materials='菌丝289、平滑石英254、紫陶208、橡木原木110、黑曜石44、黑石台阶72等，含酿造台1、双格黑床、书架7与四块空白告示牌。13个item_frame实体保留在原内容中，分类图不绘制实体；工作台不能单独证明cleric或priest。',
            circulation='已看门层y2/y3与整体y≤12切面；可读门、下部房体和中部环缘的邻接。5格梯及局部楼梯状态不证明地面至31高全程；原生碰撞、顶部到达和周边路接未验。',
            terrain='根为蘑菇村落、WORLD_SURFACE_WG、beard_thin、size6，从town_centers池起始。house主体有一处empty道路端和一处minecraft:village/mushroom/villagers接口；同Jar缺data/minecraft/...对应池，虽有trek:同路径villagers池，不能改命名空间替它解析或假定原生已补全。'),
        actual_images_viewed=[evidence(OUT/n) for n in ('F03-whole.png','F03-plan.png')]))
    dump('manual-review.json',dict(batch=46,date='2026-11-03',entries=entries,
        screened_templates=1131,screening_is_not_whole_building_or_credit=True,screening_signal_templates=3,
        actual_templates_visually_studied=3,architectural_families_observed=2,actual_new_images_viewed=6,
        proposed_first_scope_admissions=0,formal_credit_added=0,production_changes=0,checklist_deletions=0,
        semantic_dedup='两猪灵模板1680原坐标中仅一格air→bone_block不同，主体、家具和入口布局相同，合并一族；全量占用/role哈希不同也不能另计。F03多层集中体与横向骨棚不同，但功能不符仍0。239历史archive/member预筛不是真实相关完整建筑信用。',
        generated_not_claimed_viewed=['F01-vertical.png','F02-vertical.png','F03-vertical.png']))
    prior=BASE/'research-20261103-funerary-045/scope-status.json';scope=get(prior)
    scope.update(batch=46,prior_scope_status=evidence(prior),current_batch_proposed_credit=0,
        current_batch_old_case_retained='D010 remains hold0 in sealed043',pending_proposal_identities=[])
    # A historical discovery transition belongs to045; retain by link, not as046 event.
    scope.pop('discovery_formal_index_transition',None)
    dump('scope-status.json',scope)
    dump('session.json',dict(date='2026-11-03',owner='做建筑的',batch=46,status='REVIEWED_THREE_ROLE_CANDIDATES_TWO_FAMILIES_HOLD0',
        previous_receipt=evidence(BASE/'research-20261103-funerary-045/RECEIPT.json'),formal_funerary_baseline=150,
        new_first_scope_proposals=0,production_allowed=False,next='酿造台/名称预筛已收束为三候选两家族0；继续真实用途与完整边界有依据的固定本地参考，不把1131扫描、工作站或尺寸凑信用。',
        shared_coordinator_session_not_overwritten=True,coordinator_only_main_checklist=True,
        java_run=False,game_run=False,network_requests=0,no_automation=True,duration_hours_claimed=0))
    (OUT/'HANDOFF.md').write_text('''# 第46批：村落功能线索补查，三模板两家族hold0

为避免只按temple/church命名找参考，对固定本地来源尚未实际研究的小型houses作功能预筛：1131份中只3份有酿造台/cleric/priest线索。1131是机器扫描数，0完整参考信用；没有把扫描、文件或工作台当作实际建筑研究。

随后仅对3个阳性模板做实际整体研究并逐一查看6张新整体/切层图，保留原方块、实体、根池与精确出接口上下文，七项观察均落盘：

- Towns and Towers的piglin_skul_tent_1、piglin_skull_tent_1都是7×8×30；原1680位置仅(3,5,23)一处air→axis=z骨块不同。相同长骨棚及家具/入口布局合一族，不按哈希差或拼写差另计。house池只直接选skull版本，旧skul无直接选择记录。酿造台与骨材不能证实墓园/祭祀/守卫用途，两份均0。
- Trek蘑菇村落brewing_stand为17×31×17多层房体；酿造台、床、书架、展示框不自动代表祠堂或守望岗位。村民接口精确指向minecraft:village/mushroom/villagers，本Jar缺该命名空间的池；trek:同路径池不是可擅自替用的同ID。实际生成/连续路线未验，当前0。

239历史archive/member对只是辅助，不是新增239个语义案例。三张竖切仅生成，未计实看。没有因候选落空扩大既有用途/尺寸范围。

正式范围保持150/1000、缺850，引用协调044验收；本批新增0、提案0。D010入口缺证和036存储高度40与17–30范围不符的hold0不变。只写本研究包，不回写045或更早文件，不制作、不改清单/正式登记/共享session/Jar/专业资产，不运行Java/游戏，不联网、无屏幕声音亮度操作，不声称10小时。
''')
    print('Saved three actual templates / two families hold0;1131 prefilter not credit.')
if __name__=='__main__':main()
