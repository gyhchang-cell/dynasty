"""Seven-aspect observations, scope holds and coordinator transition evidence."""
import json
import hashlib
from pathlib import Path
OUT=Path(__file__).resolve().parent
BASE=OUT.parent
ROOT=BASE.parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def get(p):return json.loads(p.read_text())
def evidence(p):return dict(path=str(p.resolve()),sha256=sha(p.read_bytes()))
def dump(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
    common=dict(formal_credit_added=0,proposed_credit=0,independent_human_review=False,
        native_generation_or_collision_verified=False,actual_native_entry_or_continuous_routes_verified=False,
        source_evidence=evidence(OUT/'sources.json'),author_evidence=evidence(OUT/'author-context.json'))
    entries=[dict(common,id='045-F01',decision='HOLD_ZERO_RITUAL_OR_FUNERARY_RELEVANCE_UNPROVEN',
        complete_authored_site_template=True,
        completeness='独立structure根→唯一stonehedge池→本模板、0jigsaw，作者散布立石和地面构件均保留，不拿单根柱或一片地面当完整实例。',
        relevance_limit='有围绕中央空地的立石/过梁与六格骨块，但所读根池/标签只证明平原选址，未明示墓园/丧葬/祠堂或村落礼仪用途。不能把Stonehenge联想或骨材自动当功能证明，当前0。',
        observations=dict(
            layout='27×8×26保存盒内，数处石柱和横向过梁围出中央疏空区域，部分立石仅低残段。少量地表苔块和砂土沿外缘散置；六格骨块在偏侧，不是中央祭坛或已确认墓位。按整个作者场地观察，不分柱计数。',
            proportion='原非空气实占x3–26/y0–7/z2–24；保存27×8×26与实际24×8×23分别记录。立石最高8格，多处低段形成不齐轮廓，没有把整幅保存盒填成平台。',
            facade='无连续围墙或有顶室内，立石/横梁与不同高度断段在各方向露出空隙。两方向整体可读其疏密不对称，不虚构正式山门、墙洞或唯一主立面。',
            roof='无整场屋顶；仅局部柱间过梁和18格smooth_stone_slab收顶。过梁不是待接房屋屋脊，现存低断段不复原成古代完整宫室。',
            materials='石头107、磨制安山岩37、安山岩26、安山岩墙28、苔块28、砂土20、平滑石半砖18、骨块6。六骨块位于(12/14,1/2,18)及(12/14,3,17)，只是原材；无方块实体、无生物实体、无明示墓碑铭文。',
            circulation='立石之间有宽窄不等的空隙，中央相对开敞；270格已存、5346格省略、显式air0。省略格可能保留原地形，不能据空白图证明一圈连续平路或可直达中央。',
            terrain='根WORLD_SURFACE_WG、beard_thin；唯一池投影terrain_matching、empty处理器，适用plains/is_plains_no_snow及可选兼容草原。图为原坐标，未执行贴地投影或地形，不把浮空近似显示解释成实际悬石。'),
        actual_images_viewed=[evidence(OUT/n) for n in ['F01-whole.png','F01-plan.png']]),
        dict(common,id='045-F02',decision='HOLD_ZERO_FUNCTION_AND_WHOLE_BUILDING_RELEVANCE_UNPROVEN',
            complete_authored_site_template=True,
            completeness='独立smoldering_altar根、唯一池与0jigsaw可确认作者选取整份低构筑物；现存破碎围缘和中心火堆原样研究，不是补造完整祭祀屋宇。',
            relevance_limit='9处campfire和coal/hay/苔石构成火堆式中心，但所读资源未确证丧葬、献祭流程或村落礼仪用途；altar名称不足，火堆不能自动作火葬台。无证据则0。',
            observations=dict(
                layout='13×5×13保存盒中，中心紧凑堆叠体外有疏断低石/墙点位。中央营火跨y0–3叠置，外围不构成有顶厅房；不把9个营火、每根残柱或每个切面分别算建筑。',
                proportion='原非空气x0–12/y0–3/z0–12，保存高度5而实高4，顶一层空存储盒不算屋顶。中心高低差与外围残段分开记录，不增高成供奉大厅。',
                facade='外围开敞且不规则，各向没有可证的正式门或连续围墙。整格近似让营火和栏墙显厚，不能按灰/绿立方体断言有实体墙围住中央。',
                roof='无覆盖中央火堆的屋盖，中心堆顶营火不是建筑屋顶；没有复原假想坍塌前的殿阁或把残圈称完整义庄。',
                materials='苔圆石19、石砖12、煤块6、干草5、苔石砖台阶8、石砖墙3等，共68个已存非空气格。9个营火仅2个lit=true，其余7个lit=false；5个signal_fire=true不等于点燃。原状态保留，不把9处都描写成燃烧。',
                circulation='中心堆叠体周围有留白，但777格省略、显式air0；没有已验入口/台阶上下转接或安全的环行路线。营火状态与危险性、烟雾、碰撞和玩家可通行均未原生验收。',
                terrain='原根#trek:is_dry、WORLD_SURFACE_WG、terrain_adaptation=none，池为terrain_matching。原crackify_50_mossify_50含有序随机换材规则，stone_bricks为0.375开裂规则和后续0.6苔化规则，不能按文件名一概说各50%；未执行投影/处理器或声称原生地脚。'),
            actual_images_viewed=[evidence(OUT/n) for n in ['F02-whole.png','F02-plan.png']])]
    dump('manual-review.json',dict(batch=45,date='2026-11-03',entries=entries,actual_new_images_viewed=4,
        actual_old_comparison_images_viewed=1,actual_images_viewed=5,
        old_comparison_images=[evidence(BASE/'research-20261103-funerary-044/F01-whole.png')],
        semantic_comparison='已复看044中心晶簇/水环/八组点燃烛台的低仪式场。F01为偏空的高低立石与局部过梁，没有晶簇/水环/烛台；F02为中心营火堆与断圈，没有明确礼仪场组织证据。差异只作观察，不以此替代相关性或新增设计信用。',
        dedup_limit='237历史archive/member对无精确匹配是预筛，不是237完整相关设计实看；原候选缺用途时，不凭名字、哈希或低相似度加数。',
        proposed_first_scope_admissions=0,formal_credit_added=0,production_changes=0,checklist_deletions=0,
        generated_not_claimed_viewed=['F01-vertical.png','F02-vertical.png']))
    prior=BASE/'research-20261103-funerary-044/scope-status.json';scope=get(prior)
    formal=BASE/'continuation-20261022/references/full-buildings.json';f=get(formal)
    acceptance=ROOT/'docs/cod4/audit-20261022/coordinator-building-044-boundary-review-20261103.json';a=get(acceptance)
    assert len(f['entries'])==150 and a['formal_count_before']==149 and a['formal_count_after']==150
    assert sha(acceptance.read_bytes())=='d46caeef4e56fd246fb2f2623b7a6c483932c94c30fcb3855ab7eead3958d602'
    scope.update(batch=45,prior_scope_status=evidence(prior),current_batch_proposed_credit=0,
        pending_proposal_identities=[],previously_accepted_proposal_identities=['COD4-R001-W028','COD4-R044-F01'])
    scope['funerary']=dict(baseline=evidence(formal),formal_baseline=150,remaining_formal=850,
        current_batch_proposed_credit=0,formal_credit_added=0,formal_register_written=False,production_allowed=False,
        previous_044_proposal_accepted_by_coordinator=True,coordinator_acceptance=evidence(acceptance),
        coordinator_acceptance_pending=False)
    scope['discovery_formal_index_transition']=dict(old_record=get(OUT/'discovery-boundary.json')['indices_checked'][0],
        old_count=get(OUT/'dedup-evidence.json')['formal_identity_records_checked'],current_count=150,
        old_record_is_historical_not_rewritten=True,coordinator_acceptance=evidence(acceptance))
    dump('scope-status.json',scope)
    dump('session.json',dict(date='2026-11-03',owner='做建筑的',batch=45,status='REVIEWED_TWO_AUTHORED_SITES_HOLD0',
        previous_receipt=evidence(BASE/'research-20261103-funerary-044/RECEIPT.json'),formal_funerary_baseline=150,
        new_first_scope_proposals=0,coordinator_acceptance_pending=False,production_allowed=False,
        next='不重复本批仅有名称/材料的用途猜测；继续固定本地完整相关设计或原始用途补证，缺证仍0。',
        shared_coordinator_session_not_overwritten=True,coordinator_only_main_checklist=True,
        java_run=False,game_run=False,network_requests=0,no_automation=True,duration_hours_claimed=0))
    (OUT/'HANDOFF.md').write_text('''# 第45批：两处独立场地原稿，均hold0

固定Trek B0.6.1归档，SHA-256 `fea95f69d7d023a8d990c043ee63bc07ea0a85cde1a558b369ef4884d3ac5012`。首次实际研究stonehedge（27×8×26）与smoldering_altar（13×5×13）两份模板及各自原根、唯一池、处理器/生物群系上下文。已逐一查看4张新整体/切层图，复看1张044仪式场比较图。两张竖切仅生成，未计实看。

F01有疏散立石、局部过梁及六格骨材，但无明示丧葬/村落礼仪用途。F02为中心营火堆和断圈；9处营火只有2处点燃，不因altar名称或煤/干草推断火葬台。二者独立作者选择边界可证，相关性仍不足，提案0、正式新增0；不分柱/火堆计数、不复原假想屋宇。七项观察与原状态、固定哈希均已记录。

两模板无显式air，分别270存/5346省略、68存/777省略；省略不是清空。二者池均terrain_matching，离线图保留原坐标，未执行贴地投影、随机处理器或碰撞。石砖开裂/苔化规则按原概率0.375及后续0.6记录，不按文件名偷换为全部50%。237历史archive/member对无精确匹配只是预筛，不是完整建筑信用。

本批生成初期正式表仍149，协调随后验收044并更新至150/1000、缺850（收据SHA-256 `d46caeef4e56fd246fb2f2623b7a6c483932c94c30fcb3855ab7eead3958d602`）。新checkpoint绑定新正式表及验收；发现日志的旧149输入哈希保留，并明确接受的转换，不倒改历史042–044或原登记。D010入口缺口、036高度hold0保留。

本批只写研究包；不制作、不删清单、不改共享session/Jar/专业资产，不启动Java或游戏、不联网、不操作屏幕声音亮度、不声称10小时。
''')
    print('Saved two hold0 reviews; coordinator transition149→150 bound without old-input rewrite.')
if __name__=='__main__':main()
