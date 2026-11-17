"""Document actual observations and conservative scope proposals only."""
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile
import sys
OUT=Path(__file__).resolve().parent
BASE=OUT.parent
ROOT=BASE.parents[1]
sys.path.insert(0,str(ROOT/'tools/architecture'))
from nbt_read import read
def sha(b):return hashlib.sha256(b).hexdigest()
def get(p):return json.loads(p.read_text())
def dump(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def evidence(p):return dict(path=str(p.resolve()),sha256=sha(p.read_bytes()))
def main():
    src=get(OUT/'sources.json');details=[]
    for c in src['candidates']:
        with ZipFile(c['source_archive']) as z:d=read(z.read(c['member']))
        pal=d['palette'];states={tuple(b['pos']):pal[b['state']] for b in d['blocks']};sx,sy,sz=c['size']
        details.append(dict(id=c['id'],stored_positions=len(states),omitted_positions=sx*sy*sz-len(states),
            explicit_air=sum(s['Name']=='minecraft:air' for s in states.values()),
            centre_axis=[dict(position=[sx//2,y,sz//2],state=states.get((sx//2,y,sz//2))) for y in range(sy)],
            candle_states=[dict(position=p,state=s) for p,s in states.items() if s['Name']=='minecraft:candle'],
            sandstone_positions=[p for p,s in states.items() if s['Name']=='minecraft:sandstone'],
            raw_states_not_replaced=True,native_processors_executed=False))
    dump('detail-evidence.json',dict(entries=details,building_credit_added=0))
    old_images=[evidence(BASE/'research-20261101-settlements'/n) for n in ['S01-whole.png','S03-whole.png']]
    common=dict(source_evidence=evidence(OUT/'sources.json'),author_evidence=evidence(OUT/'author-context.json'),
        formal_credit_added=0,independent_human_review=False,native_generation_or_collision_verified=False,
        actual_native_entry_or_continuous_routes_verified=False)
    entries=[dict(common,id='044-F01',proposal_identity='COD4-R044-F01',newly_discovered_local_template=True,
        proposed_credit=1,coordinator_acceptance_pending=True,
        decision='PROPOSE_ONE_COMPLETE_SMALL_OPEN_AIR_RITUAL_DESIGN_PENDING_SCOPE_REVIEW',
        relevance='当前范围含小型祭祀空间。本例15×4×15开敞仪式场，中央晶簇、水环、外围八组石构与八处点燃烛台形成完整向心布局；仅提议用于墓园/村落室外礼仪场所的空间组织参考。不是停灵房、义庄屋宇、完整墓园或已经证实属于村落的设施，露天场所能否纳入仍交协调独立核收，不改原范围定义。',
        complete_authored_boundary='原structure根直接选唯一ritual池，池直接选择本模板、minecraft:empty处理器，模板0jigsaw和0门；中央、外围、基底均同一模板，无需把未读组件拼成主体。',
        observations=dict(
            layout='15×15角部收分草地底上，外周八组不等高低石构环绕方形水环，中央小台与晶簇形成中心焦点。外围石构之间留间隔，没有有顶大厅、附房或墙内墓室；八组石构与水域是一套整体，绝不分成八实例。',
            proportion='保存15×4×15，原非空气实占x0–14/y0–3/z0–14；最高外围石构仅4格。低横向仪式场与旧S01/S03的高摊棚区别明显，不把整格近似图当栏杆、台阶和蜡烛真实厚度。',
            facade='各方向均有开敞间隔；正向与转向整体可见离散石构、外缘草地和内侧水环。不是封闭围栏，既没有普通门也没有专门门楼，不虚构唯一礼仪入口。',
            roof='全场无屋顶。中央晶簇上方和环形活动区敞开；外围石构顶部以台阶/墙体及蜡烛收束，不视为八个独立亭子，也不用该例代替义庄屋架设计参考。',
            materials='草块116、石头53、安山岩11、水24、石台阶20、安山岩台阶5、石半砖8、圆石墙17。中央(7,1,7)紫水晶母岩和(7,2,7)朝上晶簇；8个candle方块的lit均true、每格1–3支。分类图中晶簇、烛台和墙均灰，不是材质验收；仅265位置存储、635省略，不能把省略视为显式空气。',
            circulation='外围石构之间留空，水环把中央晶簇小台与外圈分隔；图中未见桥。草地和留白可供理解内外环组织，但省略格的天然地形、涉水/跳跃、碰撞与连续玩家路线均未验，不宣称中心可步行直达。',
            terrain='原根WORLD_SURFACE_WG、beard_thin、birch_oak生物群系标签；同一刚性模板。低草地边缘适合学习仪式场贴近地面的收分，不等于实际选址是村庄或墓园，不声称所有省略格已清空。'),
        semantic_dedup='235历史archive/member对无成员/原NBT/role/occupancy精确匹配，仅辅助。已实际复看最接近旧S01沙漠市场和S03热带草原市场：旧例为三处有顶摊棚围合通道与交易设施，本例无棚无交易口，以八组石构、水环和中央晶簇向心组织；不是换材或删除一棚的同族变体。未发现已纳入149例中的同一ritual身份。',
        actual_images_viewed=[evidence(OUT/n) for n in ['F01-whole.png','F01-plan.png']]),
        dict(common,id='044-F02',proposal_identity=None,newly_discovered_local_template=True,proposed_credit=0,
            coordinator_acceptance_pending=False,decision='HOLD_ZERO_RITUAL_OR_FUNERARY_RELEVANCE_UNPROVEN',
            relevance='13×8×13完整低石台体的独立根与0jigsaw可确认；但原实体为180血decayed_totem，原成就要求杀死它。神庙名称、图腾形象和小体量不能单独证明村落祭祀/墓园功能，因此当前范围不提案。',
            observations=dict(
                layout='层层收分的石台与周缘台阶包围中央区域，上部四处高石柱端头；原中心实体位置(6.5,4,6.5)。下层切面呈空心方形中央空间、周缘厚带和两个箱位，不把中心敌人当建筑本身。',
                proportion='保存13×8×13，非空气实占全部x0–12/y0–7/z0–12；柱头在y7，台面和基底保持原比例。虽比高大boss地牢小，仍需用途证据，不能仅凭尺寸纳入。',
                facade='四周台阶、厚石基、角部竖柱构成开敞台体；无普通门、栅栏门或外接jigsaw。原方块分类图未渲染实体，不能据中央空白否认图腾存在。',
                roof='未见覆盖中央区域的封闭屋盖；四个柱头顶部并非四间独立房，也未证明原设计缺屋顶组件。主体根直接选择一个模板，保留其开敞台体形态。',
                materials='腐衰石/砖、台阶/墙与21格decaying_waste_liquid，另有两种旧箱。原NBT砂岩110格仍原样显示，但原池block_ignore明确忽略sandstone、air、structure_block；黄色外围不是已确认原生生成地基，忽略不等于替换空气。',
                circulation='周缘台阶形成可读的标高带，中央实体占上层；没有用整格渲染证明台阶碰撞、入口、中央液体安全或连续玩家通行。战斗目标实体和箱子不证明礼仪动线。',
                terrain='原根为辐射平原/荒废沙漠、WORLD_SURFACE_WG、beard_thin。处理器跳过砂岩与air，保留原地形可能影响边缘；未执行任何处理器、地形和游戏，不把裸原稿当原生落地效果。'),
            semantic_dedup='与本批仪式水环为不同布局、无精确匹配；不同不等于相关，当前仍hold0。',
            actual_images_viewed=[evidence(OUT/n) for n in ['F02-whole.png','F02-plan.png']])]
    dump('manual-review.json',dict(batch=44,date='2026-11-03',entries=entries,
        actual_new_images_viewed=4,actual_old_comparison_images_viewed=2,actual_images_viewed=6,
        old_comparison_images=old_images,generated_not_claimed_viewed=['F01-vertical.png','F02-vertical.png'],
        proposed_first_scope_admissions=1,formal_credit_added=0,production_changes=0,checklist_deletions=0))
    prior=BASE/'research-20261103-funerary-043/scope-status.json';scope=get(prior)
    scope.update(batch=44,prior_scope_status=evidence(prior),current_batch_proposed_credit=1,
        pending_proposal_identities=['COD4-R044-F01'],current_batch_old_case_retained='COD4-R004-D010 remains hold0 in sealed043')
    scope['funerary'].update(current_batch_proposed_credit=1,coordinator_acceptance_pending=True,formal_credit_added=0,
        owner_proposed_total_if_accepted=150,owner_proposed_remaining_if_accepted=850)
    dump('scope-status.json',scope)
    dump('session.json',dict(date='2026-11-03',owner='做建筑的',batch=44,status='REVIEWED_ONE_OPEN_AIR_RITUAL_PROPOSAL_ONE_HOLD',
        previous_receipt=evidence(BASE/'research-20261103-funerary-043/RECEIPT.json'),formal_funerary_baseline=149,
        new_first_scope_proposals=1,coordinator_acceptance_pending=True,production_allowed=False,
        next='交协调独立判断露天小型ritual完整设计的范围相关性，保持F02与旧D010 hold0；未满1000不制作。',
        shared_coordinator_session_not_overwritten=True,coordinator_only_main_checklist=True,
        java_run=False,game_run=False,network_requests=0,no_automation=True,duration_hours_claimed=0))
    (OUT/'HANDOFF.md').write_text('''# 第44批：小型露天仪式场提案1，图腾神庙hold0

仅固定本地归档。新读 Trek `overworld/medium/ritual.nbt`（15×4×15）及 Radiation Zone `totem_temple.nbt`（13×8×13）两模板与原根池/配置、方块实体/实体、清单来源。实际逐一查看4张新整体/切层图及旧S01/S03两张比较图。另2张竖切图仅生成，未计实看。

F01原独立根、单一模板、empty处理器与0jigsaw，八组低石构/8个点燃candle方块围绕水环和中心晶簇，完整开敞向心仪式布局。拟以 `COD4-R044-F01` 提案1，仅用于既有“小型祭祀空间”的室外组织参考。不是有顶义庄或完整墓园，未证明属于村落；是否纳入由协调独立核收，专岗不改范围或正式计数。原265位置已存、635省略，省略不是清空；真实地形/入口/中心连续通路未验。

F02原中心实体decayed_totem、成就为击杀，虽有独立低石台根，村落祭祀或墓地用途仍无充分依据，hold0。原NBT砂岩110格由作者block_ignore忽略，图中原样保留；不把黄色外框当实际地基，未执行处理器。清单中的mcreator.net是工具通用主页，非编造的作者项目主页。

235个历史archive/member对无精确匹配只是辅助；人工复看最近市场图，三处有顶摊棚/交易通道与八石构/水环/晶簇组织不同。两新模板各有完整七项观察，不凭名字/哈希提信用。

正式仍149/1000，缺851；本批提案1待核，不写成150。第43批旧D010仍hold0（组装布局补证≠实际完整生成），第36批height hold0不变。前批文件不回写；本批只写研究包，不制作、不删清单、不修改共享session/Jar，不运行Java/游戏，不联网，不操作屏幕声音亮度，不声称10小时。
''')
    print('Saved six-image review: one pending ritual proposal, one hold0.')
if __name__=='__main__':main()
