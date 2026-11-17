"""Record one authored installation proposal, not four rotated references."""
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
    prior=BASE/'research-20261103-funerary-047'
    dependencies=[BASE/'research-20261031-principles/local-evidence-inventory.json',
        BASE/'research-20261101-local-discovery/discovery.json',
        BASE/'research-20261101-dungeons-024/fixed-source-screen.json',
        BASE/'research-20261101-dungeons-026/all-structure-metadata.json',
        BASE/'research-20261101-dungeons-027/source-needs.json',
        BASE/'research-20261102-dungeons-035/HANDOFF.md',
        BASE/'research-20261103-funerary-046/manual-review.json',prior/'manual-review.json']
    src=get(OUT/'sources.json')
    dump('source-boundary.json',dict(date='2026-11-03',previous_gap_analysis=[evidence(p) for p in dependencies],
        fixed_inventory_archives=292,existing_metadata_templates=7139,
        metadata_counts_are_not_complete_semantic_reference_counts=True,
        prior_unresolved_or_rejected_not_reopened=['046酿造屋/骨棚用途不符','047闹鬼废墟用途不足','043 D010外部入口与地形未验','036 F01保存高度不符原范围'],
        source_exhaustion_claimed=False,all_local_suitable_sources_proven_insufficient=False,
        reason='旧026记录明确只有元数据覆盖，旧035保留未完成语义核查队列；不能把292包或7139NBT扫描说成全部相关完整建筑已研究。当前从同一固定清单的另一个既有作者包找到用途原证，尚不能宣称适用源耗尽。',
        current_purpose_supported_candidate=dict(source_archive=src['source_archives'][0],
            members=[c['member'] for c in src['candidates']],
            original_book_and_image_read=True,original_code_registration_read=True,
            independent_scope_admission_pending=True,max_distinct_designs=1,formal_credit_added=0),
        skipped_without_new_visual_batch=['YUNG墓碑3×2×3开闭/装备变体是旧发现的墓碑子件，不能计成完整墓园。',
            'Trek短残墙与道路/药工作点没有新增用途原证，不再批量渲染。',
            '大boss神庙、城堡碎片与辐射工业设施不转成村落小祭场。',
            '已知本地投影合集目录只有7项，两个亭已研究，其余人物/大树/普通小家名称不提供本范围用途原证；目录读取不算参考。'],
        followup='优先其他既有固定本地、作者用途明确且完整边界可核的同范围设计；仍缺证者保持0。若后续已核范围确实没有可读完整来源，记录具体范围，不重试429、不把局部阴性扩成全磁盘耗尽。',
        java_run=False,game_run=False,network_requests=0,building_credit_added=0))
    images=[evidence(OUT/n) for n in ['author-altar.png','F01-whole.png','F01-plan.png','F02-whole.png','F03-whole.png','F04-whole.png']]
    old=[BASE/'research-20261103-funerary-044/F01-whole.png',BASE/'continuation-20261022/references/whole-candidates-003/C004.png']
    obs=dict(
        layout='8×8平面中，一侧红羊毛门架/鸟居和其余三侧六根橡木柱共同围出空心活动区；F01柱位xz为(2,0)/(5,0)/(0,2)/(7,2)/(0,5)/(7,5)，鸟居位于z7。不是单个供桌道具，也不是六座建筑；原书实际图显示同一布局的装饰成品和中心发光合成效果，但不把图中效果补写进原NBT。',
        proportion='四模板均8×6×8，原非空气界均x0–7/y0–5/z0–7；鸟居6格高、六柱各3格高，门架约为柱高两倍，中心留白明显。整体为低尺度露天装置，不是完整屋宇、祠堂或墓园；原作者图有自定义模型，不能用整格图冒充激活后真实比例/碰撞。',
        facade='鸟居双竖脚在x2/x5、z7，下部三格竖向，y3/y5各有x1–6水平梁，y4保留双脚；无普通门和jigsaw。左右以及柱间开敞，强调一侧竖向门架与三侧供物柱，不虚构强制穿鸟居的唯一入口。',
        roof='露天供物区没有屋顶。原书图的鸟居有深色上沿/檐状模型，而原识别NBT仍20块红羊毛；鸟居上梁不是覆盖六柱的屋盖，不拿成品模型的外观推定另有完整厅堂。',
        materials='原模板18块oak_log均axis=y，20块red_wool，总38块；0显式air，346位置省略。作者tags允许柱材用logs、门架用红羊毛/红混凝土及可选红杉木板；这些替材仍同一个装置，不另计。作者原图未改动另存并标明固定Jar内来源，未制作/接入任何贴图。',
        circulation='中央省略区及柱间距可读，原书说明对六个柱顶放物、空手潜行右击移除、足Power才触发合成，并以御币从第四层门架正面启用。可研究围绕供物柱操作和朝向关系；没有运行激活或玩家行走，346省略位置不是清空指令，不能证明生成地面、碰撞净宽或与外路连续。',
        terrain='本例是玩家搭建的多方块祭坛，原类getTemplate按朝向选altar_north/east/south/west，不是自然世界jigsaw建筑根；原作者图在平草地展示，无地基/道路/坡地模板。只有空心仪式操作区和门架—柱列的空间组织可借鉴，不证明属于村落/墓园，更不替代荒村自然生态验收。')
    reading=dict(source=evidence(OUT/'class-evidence.json'),text=evidence(OUT/'class-reading.txt'),
        classes_decoded=3,methods_decoded=16,
        actual_manual_scope=['MultiBlockAltar.isCoreBlock/isMatch/build/getCenterPos/getTemplate/getAltarTemplate/<clinit>',
            'MultiBlockManager.init','MultiblockRegistry.init/<clinit>'],
        findings=['getTemplate与<clinit>按朝向绑定四份NBT，JSON中没有模板池选择不是死资产证据。',
            'isMatch遍历保存块；pillar/torii材料标签与原识别材料相连。build处理保存的38位置并把pillar顶位收集至同一装置，原成品与识别模板应分开记录。',
            'Patchouli同一altar ID注册O/R材质tag，空格为anyMatcher；不能把图书模板空格说成必须air。'],
        limits='Python解析原class字节及指令，只读；未加载/执行Java，没有游戏、合成、付款、发奖或多方块激活验收。部分SRG字段保持原名，不据映射猜地形成功。')
    dump('manual-review.json',dict(batch=48,date='2026-11-03',entries=[dict(
        id='048-F01',proposal_identity='COD4-R048-F01',complete_building_identity='touhou_little_maid:altar-one-authored-installation',
        member_ids=['F01','F02','F03','F04'],source_evidence=evidence(OUT/'sources.json'),author_evidence=evidence(OUT/'author-context.json'),
        decision='PROPOSE_AT_MOST_ONE_SMALL_OPEN_AIR_ALTAR_INSTALLATION_PENDING_SCOPE_ADMISSION',
        proposed_credit=1,formal_credit_added=0,coordinator_acceptance_pending=True,
        independent_human_review=False,native_generation_or_collision_verified=False,
        relevance='既有范围含小型祭祀空间；原作者明确多方块祭坛、御币启用和六柱献物/Power合成，原书有完整成品图。不是由房内一酿造台/箱子推断宗教用途。仅提议露天门架—六柱操作空间整体一例；是否满足完整相关建筑范围需协调独立核收，不静默将所有魔法工作台纳入。',
        admission_boundary='原NBT为38块识别/激活前结构，原书图为装饰成品；不宣称独立有顶建筑、义庄、完整村庄/墓园。若仅获装置学习而非完整相关空间认可，正式仍0。',
        observations=obs,actual_images_viewed=images,
        semantic_dedup='四份经原坐标最小角对齐及0/90/180/270度旋转后，全部原方块名与axis状态精确一致，合一例。245历史archive/member与150正式身份未见同一祭坛；已实看044水环仪式场和C004小祠对比：前者为八组石构/水环向心组织，后者为门架前庭加有顶封闭主室，本例六柱空心操作区无主屋/水环，差异是空间组织而非换材。哈希及占用相似度仅辅助。')],
        actual_original_templates_visually_studied=4,distinct_authored_designs_observed=1,
        actual_new_images_viewed=6,actual_old_comparison_images_viewed=[evidence(p) for p in old],
        generated_not_claimed_viewed=['F01-vertical.png','F02-plan.png','F02-vertical.png','F03-plan.png','F03-vertical.png','F04-plan.png','F04-vertical.png'],
        original_bytecode_reading=reading,source_exhaustion_claimed=False,
        proposed_first_scope_admissions=1,formal_credit_added=0,production_changes=0,checklist_deletions=0))
    scope=get(prior/'scope-status.json');scope.update(batch=48,prior_scope_status=evidence(prior/'scope-status.json'),
        current_batch_proposed_credit=1,pending_proposal_identities=['COD4-R048-F01'],
        current_batch_admission_pending=True,current_batch_formal_credit_added=0,
        current_batch_boundary='At most one complete small open-air altar installation, not four orientation files; admissibility within original small-ritual-space scope pending coordinator.')
    dump('scope-status.json',scope)
    dump('session.json',dict(date='2026-11-03',owner='做建筑的',batch=48,status='ONE_AUTHOR_SUPPORTED_ALTAR_PROPOSAL_PENDING',
        previous_receipt=evidence(prior/'RECEIPT.json'),formal_funerary_baseline=150,
        new_first_scope_proposals=1,formal_credit_added=0,remaining_formal=850,production_allowed=False,
        next='待协调独立核收COD4-R048-F01用途/完整空间边界；四朝向固定合一，不复数计入。继续其他已有固定本地、用途原证可核的完整相关设计，源不足如实保留边界，不复扫无关模板。',
        shared_coordinator_session_not_overwritten=True,coordinator_only_main_checklist=True,
        java_run=False,game_run=False,network_requests=0,no_automation=True,duration_hours_claimed=0))
    (OUT/'HANDOFF.md').write_text('''# 第48批：用途原证明确的小型祭坛，四朝向合一项待核收

先复用既有缺口分析，未重复扫描046骨棚/酿造屋、047废墟或墓碑子件。292固定包与7139条NBT只曾完成元数据覆盖，不足以证明全部相关建筑已耗尽。本轮转该固定清单内另一既有作者包，找到车万女仆完整祭坛原证；没有网络重试。

实际研究4份8×6×8原NBT、3份原class的登记/识别指令、原作者图书与中文用途说明。实看4张朝向整体图、1张F01平面、1张作者未改动成品原图，共6张新图；另看044水环仪式场与旧C004小祠两张对比图。其它7张生成图未计实看。

鸟居与六根三格高橡木柱围成露天操作区，完整识别模板共38块（18橡木、20红羊毛），0显式air、346省略格。作者书明确御币启用、六柱放置/取下物品及Power合成；原登记类按方向选择四NBT，旋转对齐后原名称/axis状态完全一致，所以最多只有**一项**。不把六柱、四朝向、替材或原作者成品图分别计建筑。

提出`COD4-R048-F01`，仅供既有“小型祭祀空间”范围独立核收：它是完整多方块仪式操作装置，是否达到完整相关建筑/场所边界待协调判断，不能把所有魔法工作台自动纳入。原NBT是激活前识别结构，作者图是自定义模型成品，两者明确区分。它没有屋宇/地基/道路，不是义庄、完整墓园或自然村落证明，省略格不是清空，激活/碰撞/连续路线/地形均未运行。

正式仍**150/1000、缺850**；提案1，正式新增0，待核收不提前改151。036高度hold0及D010入口/地形缺证保留。来源尚未获全范围语义穷尽证明，详见source-boundary.json；后续只继续用途和完整边界确可查的来源。

仅写本048包，原始书图明确固定Jar成员和哈希作为研究引用，未冒充原创资产。未改047及更早收据、生产/主清单/共享session/Jar/专业资产；未运行Java/游戏，未联网、未动声音亮度焦点，删除任务0，无定时，无10小时达成声称。
''')
    print('Saved one original altar design proposal pending scope admission; formal150 unchanged.')
if __name__=='__main__':main()
