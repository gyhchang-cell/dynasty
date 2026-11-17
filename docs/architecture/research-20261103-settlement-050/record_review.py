"""Record actual visual reading and exact original scope; never write registers."""
import hashlib,json
from pathlib import Path
from datetime import datetime,timezone
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):
    p=Path(p).resolve();return dict(path=str(p),sha256=sha(p))
def dump(name,data):(OUT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def main():
    source=json.loads((OUT/'sources.json').read_text())['candidates'][0]
    context=json.loads((OUT/'author-context.json').read_text())
    formal=ROOT/'docs/architecture/continuation-20261022/references/full-buildings.json'
    lodging=ROOT/'docs/architecture/research-20261101-scoped-urban-lodging-ledger/urban-lodging-scope-register.json'
    lodging_data=json.loads(lodging.read_text())
    prompt=Path('/Users/a15356015027/Desktop/code x提示词/cod2.txt')
    lines=prompt.read_text().splitlines()
    dump('task-use-boundary.json',dict(original_prompt=ref(prompt),
      excerpts=[dict(line=i,text=lines[i-1]) for i in [84,85,87,88,89,100]],
      requested_scope='COD2-5 阴司枉死城：密集商铺/民居、相连屋顶与巷道的立体组织；整体仍要求中式地底死城。',
      current_reading_scope='一个整体海岛聚落的密集生活层、错层门口、岩基及高处地标，只读学习。',
      lodging_scope_id=lodging_data['scope_id'],lodging_scope_definition=lodging_data['scope_definition'],
      original_lodging_scope=ref(lodging),
      boundary='53×54平面、49全实高的岩岛聚落，不是既有约40–50平面/30–36实高的公共地面层+客房旅店组；不削地基或链条改计高度。没有义庄/墓园/小祭场用途证据。',
      chinese_style_or_underground_city_proven=False,inn_use_proven=False,funerary_use_proven=False,
      new_scope_definition=False,new_ledger_created=False,formal_credit_added=0))
    dump('functional-evidence.json',dict(
      original_complete_design=dict(identity=source['member'],size=source['size'],
        actual_nonair_bounds=context['nonair_bounds'],nonair=source['nonair'],
        identity_unit='Whole original authored island settlement, including rock base, low timber structure, dense upper cluster and towers; no subdivision.',
        root='data/trek/worldgen/structure/overworld/rare/villager_island.json',
        root_start_pool='trek:overworld/rare/villager_island',root_size=2,
        pool_single_location='trek:overworld/rare/villager_island',projection='rigid',processors='minecraft:empty',
        architectural_outgoing_pools=0,mob_only_parent_sockets=13,mob_support_alternatives=3),
      author_use_evidence='Original root/pool identifier is villager_island; all13 sockets select original plains villager support templates. Eight bed states form four complete beds, workstations and storage provide further settlement-use evidence. Original signs are blank, no invented inn/shop name.',
      lower_door_layers=context['lower_door_layers'],lower_door_count=18,
      complete_beds=4,bed_levels=[24,25],
      bed_clearance='Two pairs of x/z bed footprints repeat on directly adjacent y24/y25; occupancy/clearance and sleeping were not tested, so this is not an accepted bunk-bed construction pattern.',
      original_ladder_run=dict(x=41,z=8,ys=list(range(23,34)),facing='east',
        near_upper_doors=[[41,34,6],[41,34,10]],native_route_verified=False),
      stairs_stored=614,ladders_stored=55,
      feature_examples=[dict(position=[43,24,31],name='minecraft:blast_furnace'),
        dict(position=[40,24,30],name='minecraft:lectern',has_book=False),
        dict(position=[44,29,30],name='minecraft:brewing_stand'),
        dict(position=[37,25,35],name='minecraft:bell'),
        dict(position=[41,40,10],name='minecraft:campfire')],
      boats_or_boarding_route_accepted=False,continuous_rooftop_route_accepted=False,
      vanilla_loot_member_boundary='minecraft:chests/village/village_taiga_house is referenced but not shipped in this mod Jar. The minecraft namespace can be supplied by the base game; absence here is not a missing-table bug finding. Base-game resolution was not checked in this batch.',
      native_loot_or_resident_generation_verified=False,quest_or_compass_acceptance=False))
    new_images=['F01-whole.png','F01-plan.png','F01-vertical.png','F01-y19.png','F01-y24.png','F01-y34.png','F01-life-level-cutaway.png']
    old_images=[OUT.parent/'research-20261101-dungeons-002/F15-whole.png',OUT.parent/'research-20261101-dungeons-003/F06-whole.png']
    observations={
      'layout_observation':'整体生活建筑集中在岛体一侧上部，较低木构伸向另一侧；y19/20与y24/25层的墙体/平台轮廓不同，聚落不是一块平地上的单排房屋。y24有密集门口及生活设施，北端较独立高塔形成端部地标。可借鉴先组织公共通达层与局部抬升体量，再布置小间的顺序；未认定任何空白格为已清空通道。',
      'proportion_observation':'原53×49×54和实x0..52/y0..48/z0..53完整保留；y0..10大面积岩体与y19..34生活/高处层分开读，不能把岛高当普通房间层高，也不能裁地基或顶端链条来迁就旅店范围。最高y48五根链条属原整体，仍保留。',
      'facade_observation':'生活层石质墙面、木向横线、门窗开口、挑出平台及爬梯形成深浅交替，外轮廓有多处退进；原门包括云杉、丛林木、红树，不把分类图灰色当相同真实材质。可借鉴同一基底上改变开间与门口朝向，未证明徽派立面。',
      'roof_observation':'整图/低切显示多个不同标高的台沿和上覆屋面，高塔明显越过密集体量；原台阶上下半、转角、半砖、栅栏/链条参与轮廓。614台阶含檐口、家具等，不能全部视为可走楼梯。可借鉴屋面高低与塔的主次，不宣称已存在连续屋顶路线或飞檐样式。',
      'material_observation':'10758石、2026沙、1209砂岩、1197安山岩等构成岩岛主体；上部有方解石392、裂石砖438、木构、彩色羊毛/陶瓦及储物工作站。原料分布和旧新块可供地形—建筑过渡研究，不复制作者调色/资产，也不把酒架/蜂箱等分类色解释成自创店铺。',
      'circulation_observation':'18处原门下半跨y13/19/20/23/24/29/34七个标高，y24集10处，说明门口组织随层变化；(41,y23..33,8)连续11格东向爬梯靠近y34双侧门，是明确的局部竖向构件。没有验证梯脚/梯顶、净空、落脚、岸边入口、全村或屋面互通；学习应保留这些待查条件。',
      'terrain_connection_observation':'石/沙混合岩基已有阶梯状外缘，低处木构与上部密集体量共同塑造岛岸轮廓。原根WORLD_SURFACE_WG、start_height绝对-11、terrain_adaptation none、cold_default海洋群系标签是作者放置上下文，不能从离线空白背景断言水位、船岸登陆或实际地形融合已通过。'}
    review=dict(id='COD2-R050-F01',member=source['member'],source_archive=source['source_archive'],
      source_archive_sha256=source['source_archive_sha256'],nbt_sha256=source['nbt_sha256'],
      evidence_actually_viewed=[dict(**ref(OUT/n),actual_visual_reading=True) for n in new_images],
      old_comparison_images_actually_viewed=[dict(**ref(p),actual_visual_reading=True) for p in old_images],
      actual_original_complete_designs_visually_studied=1,actual_new_images_viewed=7,actual_old_images_viewed=2,
      complete_instance_boundary='Single authored NBT contains all fixed architectural solids;13 jigsaws target only1×3×1 villager support alternatives and their final empty pools. No generated assembly or mob population claimed.',
      deduplication_basis='No exact raw/role/occupancy/member match in250 historical archive/member pairs. Compared original whole image to closest occupancy-only steam_house (0.30959), which has a broad unified courtyard/roof arrangement, and old sunken_city, whose broad lower grid and isolated tower differ from this terraced dense island. Heuristic and two comparisons do not establish global family novelty or reference eligibility.',
      relevance_to_current_task='COD2-5 dense street/roof spatial study only; island above-ground use and non-Chinese appearance do not fulfil Chinese underground ghost city, cemetery or large inn scope.',
      **observations,
      limitations=['Full-cell classification views, not original native textures/meshes/collision.',
        '115214 omitted positions are not explicit air or guaranteed cleared spaces.',
        'Original7 signs contain empty text; no invented shop/inn inscription.',
        'Four complete bed pairs include adjacent stacked levels; native sleep/clearance unverified.',
        'Actual generated island, resident population, loot, approach and quests/compass unverified.'],
      actual_design_credit_proposed=0,formal_credit_added=0,
      decision='COMPLETE_SETTLEMENT_READ_ONLY_SPATIAL_STUDY; OUTSIDE_EXISTING_FUNERARY_AND_LARGE_LODGING_SCOPES',
      same_agent_semantic_reading=True,independent_review=False,human_acceptance=False)
    dump('manual-review.json',dict(entries=[review],new_first_scope_proposals=0,formal_credit_added=0))
    status=dict(batch=50,funerary=dict(baseline=ref(formal),formal_baseline=151,remaining_formal=849,
      current_batch_added=0,scope_definition_unchanged=True,
      coordinator_048_authority=ref(ROOT/'docs/cod4/audit-20261022/coordinator-building-048-boundary-review-20261103.json')),
      lodging=dict(baseline=ref(lodging),formal_baseline=2,remaining_formal=998,current_batch_added=0,
        scope_definition=lodging_data['scope_definition'],scope_definition_unchanged=True),
      guard=dict(prior_hold_authority=ref(ROOT/'docs/cod4/audit-20261022/coordinator-building-036-boundary-review-20261103.json'),
        new_credit=0,original_size_definition_unchanged=True,reference_036_F01_still_hold=True),
      prior_scope_status=ref(OUT.parent/'research-20261103-lodging-049/scope-status.json'),
      prior_receipt=ref(OUT.parent/'research-20261103-lodging-049/RECEIPT.json'),
      new_scope_definitions=False,new_ledgers_created=False,cod6_credit_added=0,current_batch_formal_credit_added=0,
      production_allowed=False,source_exhaustion_claimed=False,pending_proposal_identities=[])
    dump('scope-status.json',status)
    dump('session.json',dict(date='2026-11-03',owner='做建筑的',batch=50,
      recorded_utc=datetime.now(timezone.utc).isoformat(),
      actual_work='Read original task, selected one unstudied whole settlement; inspected7 images +2 old comparisons; traced13 original sockets through3 mob-only alternatives; recorded seven architectural observations and exact scope exclusion.',
      source_root_and_six_context_resources_read=True,original_nbts_read=4,original_complete_designs_read=1,
      counted_nbts_as_buildings=False,formal_credit_added=0,new_proposals=0,
      next_breakpoint='Seek another exact-use/scale whole courtyard/large inn/settlement from readable fixed local sources; reuse existing evidence. This case retains its original identity and no credit; do not resubmit a rotation/recolour or silently broaden a scope.',
      source_exhaustion_claimed=False,only_current_research_directory_written=True,
      java_run=False,game_run=False,network_requests=0,production_changes=0,checklist_deletions=0,
      audio_or_brightness_changed=False,wake_unlock_focus_or_process_queries=False,
      shared_coordinator_session_written=False,duration_hours_claimed=0,no_automation=True))
    (OUT/'HANDOFF.md').write_text('''# 第50批：完整岩岛聚落空间研究，既有范围不变

依据原cod2第87–88行的密集街巷、相连屋顶与立体探索，读取固定Trek B0.6.1原包 `overworld/rare/villager_island.nbt`。一处原53×49×54整体含25024非空气格，实高49，岩基、低处木构、上部密集生活建筑和高塔共同构成完整作者实例。原来源manifest署名hotsuop、Hugger、ALDgamer，MIT；来源页仅使用本地manifest给出的URL，没有联网访问。

实看7张本批原结构整图/低切/平面/竖切，并看旧002-F15沉城与003-F06 steam_house两张原整体对比。七项布局、比例、立面、屋顶、材质、动线、地形观察逐项保存在manual-review.json。250个历史源文件对的去重无精确匹配，最接近的占位启发式是steam_house 0.30959，不能把此扫描当参考信用或全球家族去重证明。

13个原jigsaw都指向同一村民池；池中三个1×3×1原NBT只是空格/连接器和村民实体，各自再指向empty，不缺待拼接楼房，不拆成13栋或3例。没有执行拼装或宣称村民生成成功。原8个床状态构成4张床，分布y24/25，部分上下紧邻，净空/睡眠未验，不能直接借作可用双层床。18处门跨七个标高，y24占10处；(41,y23..33,8)是连续原爬梯，梯顶接门和全村通行仍待原生验收。

学习重点是岩基→低处木构→密集生活层→高塔的层级关系、随地形变化的门口标高及屋面主次。它不是中式地底死城或完整鬼市验收；没有义庄、墓园、小祭场或公共旅店的用途依据。它也不符既有大型公共旅店约40–50平面/30–36实高范围；不裁地基、链条，不换定义或新建信用表。因此本批提案0、正式新增0：义庄等原登记151/1000缺849，大型旅店仍2/1000缺998，COD6新增0。

115214省略位置不是显式air，整格分类图不是原生贴图/家具/碰撞/地形。原根WORLD_SURFACE_WG、起点偏移-11、无terrain adaptation和cold_default海洋标签已保留，实际水线、船岸入口及屋顶连续路线未验。7块原招牌为空，不编造店铺文字。Jar不含原引用的minecraft村庄战利品表并不构成缺表bug结论，基础游戏解析未查；三张trek表原文可读，没有发奖或拾取验收。

仅写本050研究目录。上一049收据逐文件保持，048已核收1例不重复计算；045–047未重查，不宣称穷尽本地来源。不制作、不改艺术/生产/主清单/共享session/Jar，不Java/游戏/联网，不动声音、亮度、屏幕或焦点，任务删除0，主动工时声称0。
''')
if __name__=='__main__':main()
