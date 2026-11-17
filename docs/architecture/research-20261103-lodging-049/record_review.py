"""Save a complete original inn study while preserving existing scope gates."""
from collections import Counter
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
    # An unverified external publication URL must not masquerade as provenance.
    src=get(OUT/'sources.json')
    for r in src['source_archives']:
        r.update(publisher_url=None,url_access='No external publication URL verified; fixed local manifest attribution only.',
            publisher_provenance='META-INF/mods.toml: Aurelj, DiamondTown & Zephyrusj')
    for c in src['candidates']:c.update(publisher_url=None,publisher_provenance='Fixed local META-INF/mods.toml; no external page accessed.')
    dump('sources.json',src)
    task=Path('/Users/a15356015027/Desktop/code x提示词/cod2.txt');lines=task.read_text().splitlines()
    urban=BASE/'research-20261101-scoped-urban-lodging-ledger/urban-lodging-scope-register.json';u=get(urban)
    dump('task-use-boundary.json',dict(task_source=evidence(task),lines=[dict(line=i,text=lines[i-1]) for i in [85,88,100]],
        original_task='DUN05鬼市中的客栈/废弃民居及公共饮食到住宿的空间组织',
        existing_lodging_scope=evidence(urban),existing_definition=u['scope_definition'],existing_accepted=u['accepted_references'],
        candidate_stored_size=[22,25,25],candidate_occupied_height=22,
        decision='READ_ONLY_ORIGINAL_TASK_STUDY_OUTSIDE_EXISTING_LARGE_LODGING_SCOPE',
        reason='客栈用途有原招牌、原根池及床/家具直接证据，但22×25平面与22实高不符合既有约40–50平面/30–36实高的大型公共旅店范围。保留学习，不新建/放宽范围、不借它增加原义庄150/151登记或大型旅店2例。',
        new_scope_definition=False,scoped_credit_added=0,construction_allowed=False))
    ctx=get(OUT/'author-context.json');signs=[]
    for b in ctx['block_entities']:
        if b['nbt'].get('id')!='minecraft:sign':continue
        texts={k:v for k,v in b['nbt'].items() if k.startswith('Text')}
        if any('Inn' in str(v) or 'Lothrick' in str(v) for v in texts.values()):signs.append(dict(position=b['pos'],texts=texts))
    beds=[e for e in ctx['bed_states'] if e['state']['Properties']['part']=='head']
    counts=Counter(b['nbt']['LootTable'] for b in ctx['block_entities'] if b['nbt'].get('LootTable'))
    dump('functional-evidence.json',dict(inn_signs=signs,bed_heads=beds,complete_beds_observed=3,bed_block_states=6,
        door_lower_counts_by_y=dict(Counter(e['position'][1] for e in ctx['doors'] if e['state']['Properties']['half']=='lower')),
        original_loot_reference_counts=dict(counts),missing_exact_loot_id='luna_structures:chests/taiga_inn/taiga_inn_barrels',missing_exact_loot_reference_blocks=4,
        missing_in_this_fixed_jar_not_asserted_absent_everywhere=True,available_simply_houses_id_not_silently_substituted=True,
        native_room_count_not_inferred_from_door_or_bed_count=True))
    obs=dict(
        layout='同一模板包含厚石基/底部储藏空间、主层分区及上层三张床所在分室；两段主屋与一侧较低屋面相接，入口前有木石踏步与小平台。主层y4切面和y≤6整体显示家具小组、隔间与相连通道；原sign在(16,7,15)写Inn/Lothrick，不因单床或单工作台推断旅店。',
        proportion='保存22×25×25，原非空气实占x0–21/y0–21/z0–24，实高22。三根烟囱和坡顶都在总高内，不能称25格实高或按屋脊数算楼层。相较既有48×48及44×43大型旅店明显更紧凑，不削小原范围给它信用。',
        facade='木柱/横梁框架分隔浅色墙面与多面窗，外有挑梁、檐下支撑、栏件和小平台，入口前开口与台阶区别于封闭客房门。原招牌确定客栈身份；不把木框架风格当成已满足徽派黑瓦白墙，更不抄作中式成品。',
        roof='主屋高山墙坡顶与相接低屋面形成高低体量，屋脊和烟囱各自突出；原材料含light_gray_wool351、绿色/黄绿色陶土以及木楼梯/台阶，分类图未渲染真实贴图。原屋顶不是已制作的中国式飞檐，屋内上部空腔也不自动算阁楼客房。',
        materials='原非空气3889格：stone614、stripped_spruce_wood405、light_gray_wool351、stone_bricks301等。26桶、6格绿色床构成3张床，5炉/2烟熏炉、3营火等原内容均保留；另有item_frame与armor_stand各1不绘入整格图。5699保存位置中1810显式air、8051省略，不能把省略格都当清空或把三张床说成六间房。',
        circulation='普通门下半共12：y0一处、y4六处、y10五处；上层三处dark_oak门在x7、z11/15/19，与x8–10床位相邻。外三格宽西向踏步从x19/y0经18/y1、17/y2到16/y3；内有(14,5,2)→(13,6,2)及(12,7,3)/(12,8,4)/(12,9,5)的转向梯段。只记录原坐标/方向和分室—走廊关系，未证明转角落脚、头顶净空、连续通行或所有屋面相连。',
        terrain='根为taiga群系、WORLD_SURFACE_WG/beard_thin，单元素rigid、minecraft:empty处理器，直接选择整屋；0jigsaw，不依赖另一个屋翼组件来补齐。石基和低门层与实际地表高度关系未运行，不能宣称地上/地下落位正确。4个桶引用luna_structures旧表，本固定Jar缺该精确ID；同路径simply_houses表存在也不替换，未验证任何原生出货/付费/奖励。')
    images=[evidence(OUT/n) for n in ['F01-whole.png','F01-plan.png','F01-vertical.png','F01-y4.png','F01-y10.png','F01-hall-cutaway.png']]
    old=[BASE/'research-20261101-dungeons-004/F01-whole.png',BASE/'research-20261101-dungeons-004/F02-whole.png']
    dump('manual-review.json',dict(batch=49,date='2026-11-03',entries=[dict(id='049-F01',
        source_evidence=evidence(OUT/'sources.json'),author_evidence=evidence(OUT/'author-context.json'),function_evidence=evidence(OUT/'functional-evidence.json'),
        decision='COMPLETE_ORIGINAL_INN_READ_ONLY_STUDY_ZERO_EXISTING_SCOPED_CREDIT',
        complete_authored_designs_observed=1,proposed_credit=0,formal_credit_added=0,
        original_task_relevance='DUN05原文客栈/民居；公共主层与上层私密房间、桌椅叙事和沿街入口的空间分工可研究。',
        scope_limit='用途与完整性可核，既有大型公共旅店尺寸范围不符；不转入义庄/墓园/小祭场，不扩大既有范围或另开信用表。',
        observations=obs,actual_images_viewed=images,independent_human_review=False,native_generation_or_collision_verified=False,
        semantic_dedup='249历史archive/member对是辅助，不是完整参考数。实际对比旧004两旅店：主楼加分离低附屋、U形多翼围院都不同于本紧凑双坡屋与上层分室，但不同不等于符合原大型尺寸，且不以缩小体量单独认定独立家族获得信用。无精确同NBT/role/occupancy命中，语义观察只供本研究。')],
        actual_original_templates_visually_studied=1,actual_new_images_viewed=6,
        actual_old_comparison_images_viewed=[evidence(p) for p in old],generated_not_claimed_viewed=[],
        proposed_first_scope_admissions=0,formal_credit_added=0,production_changes=0,checklist_deletions=0,
        applied_research_principles=['先区分公共接待/饮食和上层住宿，再用走廊与门的关系处理私密性；不能只复制床与招牌。',
            '用主屋与低附体的高差建立入口辨识；不把烟囱、屋脊或每间房拆成建筑实例。',
            '地面来源、旧命名空间战利品与真实付款/发奖分开核；完整参考不等于生存获取闭环已验。']))
    prior=BASE/'research-20261103-funerary-048';scope=get(prior/'scope-status.json')
    formal=BASE/'continuation-20261022/references/full-buildings.json'
    receipt=BASE.parent/'cod4/audit-20261022/coordinator-building-048-boundary-review-20261103.json'
    assert sha(receipt.read_bytes())=='69c0235fd5aff89ecb8f91ebfa3feff38be60153426250ff40cf8ce9c4be329f'
    assert sha(formal.read_bytes())=='0852fc0944b3e083a42cae4c00d07f343d0ca67e93595bbab1ab93cf2d2042aa' and len(get(formal)['entries'])==151
    old_baseline=scope['funerary']['baseline']
    scope['funerary'].update(baseline=evidence(formal),formal_baseline=151,remaining_formal=849,
        coordinator_acceptance=evidence(receipt),coordinator_acceptance_pending=False)
    scope.update(batch=49,prior_scope_status=evidence(prior/'scope-status.json'),
        current_batch_proposed_credit=0,current_batch_formal_credit_added=0,current_batch_admission_pending=False,
        pending_proposal_identities=[],current_batch_boundary='Complete smaller inn outside existing large urban-lodging size scope; no scope expansion or funerary admission.',
        lodging=dict(baseline=evidence(urban),formal_baseline=2,remaining_formal=998,current_batch_added=0,original_scope_unchanged=True,production_allowed=False),
        discovery_formal_index_transition=dict(discovery_formal_index_before_acceptance=old_baseline,current_formal_index=evidence(formal),
            authority=evidence(receipt),accepted_identity='COD4-R048-F01',accepted_previous_batch_credit=1,
            current_batch_credit=0,old_discovery_and_048_records_not_rewritten=True))
    if 'COD4-R048-F01' not in scope['previously_accepted_proposal_identities']:scope['previously_accepted_proposal_identities'].append('COD4-R048-F01')
    dump('scope-status.json',scope)
    dump('session.json',dict(date='2026-11-03',owner='做建筑的',batch=49,status='COMPLETE_SMALLER_INN_RESEARCH_ZERO_EXISTING_SCOPE_CREDIT',
        previous_receipt=evidence(prior/'RECEIPT.json'),formal_funerary_baseline=151,remaining_formal=849,
        previous_048_accepted_by_coordinator=True,coordinator_receipt=evidence(receipt),
        new_first_scope_proposals=0,formal_credit_added=0,production_allowed=False,
        next='本完整小旅店已研究，原大型范围不符保持0，不重复再读；继续其他固定本地用途明确且边界完整的原任务建筑。48已正式核收1，不重跑旧验收、不改48历史待核状态，不把任意机器纳入建筑。',
        shared_coordinator_session_not_overwritten=True,coordinator_only_main_checklist=True,
        java_run=False,game_run=False,network_requests=0,no_automation=True,duration_hours_claimed=0))
    (OUT/'HANDOFF.md').write_text('''# 第49批：原任务客栈完整研究，保留既有范围边界

从原cod2第100行明确的鬼市客栈继续研究，读取固定Simply Houses原包的完整taiga_inn、作者manifest、根/单元素模板池/群系、家具/招牌/床/门及战利品表。实看6张新整体、主层低切、平面与竖切图，另看旧004两张大型旅店整体作对比。不重查45–47，也未再扫无关酿造设施。

原招牌(16,7,15)写“Inn / Lothrick”，与作者住宿用途、上层3张完整床及分室相互支持。整体22×25×25，原非空气实高22，包含石基、公共/服务主层、走廊客房、相接高低坡顶和外部台阶，0jigsaw，单池直接选择整屋；床/房/屋翼均不拆计。

本设计用途真实、边界完整，但**不符原大型公共旅店约40–50平面、30–36实高范围**。保存只读学习，不扩大范围或新建信用表；大型旅店仍2/1000、缺998。本批提案0、正式新增0，不加进义庄/墓园登记，也不宣称满足徽派样式、全地下城、屋顶连续路线或任务/指南针验收。

原5699保存位置含1810显式air、8051省略；省略格不是清空。6个床状态为3张床，12处门下半分布在y0/y4/y10。保留原梯段、门向、楼板、家具和地基观察，未以整格图代替连续碰撞路测。4个桶引用旧luna_structures:chests/taiga_inn/taiga_inn_barrels，本Jar缺该精确表；simply_houses同路径存在但不能替它解析。没有修改作者资产、触发战利品或验证付款发奖。

研究中收到主协调48验收：原作者多方块祭坛整体1已纳入既有小祭场范围，**150→151/1000、缺849**。本049断点绑定原正式表与协调收据SHA69c0235f…，旧48待核日志/收据及本49初期150输入均原样保留，不回写历史、不复跑已通过的协调核收。COD6仍0，其他分组不合并。

用途摘录、七项观察、原上下文、精确战利品ID缺口、旧图对比、去重及断点均在本包。只写049研究目录；不制作、不改生产/主清单/共享session/Jar/专业资产，不运行Java/游戏、不联网、不动声音/亮度/焦点，任务删除0，不声称10小时。
''')
    print('Recorded one complete original inn; existing lodging scope unchanged; coordinator048 baseline151 bound.')
if __name__=='__main__':main()
