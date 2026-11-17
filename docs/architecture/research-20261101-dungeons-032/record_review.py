#!/usr/bin/env python3
"""Preserve complete ice-tower observations without material-only family credit."""
import copy
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
BASE = OUT.parent


def get(p):
    return json.loads(p.read_text())


def evidence(p):
    return dict(path=str(p), sha256=hashlib.sha256(p.read_bytes()).hexdigest())


def dump(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


OBS = {
 'T01': dict(
  layout='冰壳内低部上下小室接中央单梯井，上部变细，仅在y19有小木环台，主体是低室—长细轴—小高台的组织。整个作者塔含地脚一次研究，不按门、环台或5个实体点拆例。',
  proportion='16×27×17，实占y0–26，确有27格保存方块高；但房间主要在下部约y1–7，上部窄冰轴及尖部不称二十多格净高的封闭多层楼。',
  facade='下部冰壳较宽，外形向上急收为细柱，低侧留木门和层板外沿。它不是泥塔等宽连续墙筒，但冰外皮本身不能证明独立于其他细轴高台塔的设计族。',
  roof='上部冰尖没有完整高室屋盖，y19为小木环台，四角灯与y20角半砖不能读成完整四柱覆顶上房；低室盖和尖柱一并保留。',
  materials='blue_ice、packed_ice、spruce_planks、spruce_slab、spruce_stairs、lantern及原门梯构件。木环台在分类图上可能呈灰色，原状态证明不是一圈天然石砖；冰换材不是新增设计依据。',
  circulation='门[4,1,8]、[5,5,8]。普通梯[8,*,8]为y1–6和y8–21，中间y7不是梯；y19原stray socket[7,19,7]的final_state为spruce_planks。只记录环台与梯井的空间线索，未装配角色、未验证台阶/半砖碰撞或全程上行。',
  terrain='作者结构限定icy_snowy生境、直接start_pool选此整塔并配置stray；5个socket全是stray实体池。完整用途支持不能替代同族独立性证明，地表投影和beard_thin未运行。'),
 'T02': dict(
  layout='冰残围墙包低地脚，细中柱向上托一个小冰壳顶腔；不是已证完整地面营房或宽厅。旧003-F11的完整性/入口/路线待查继续保留。',
  proportion='18×29×20，实占y0–28。低围边多到y3左右，长窄竖轴占大部高度，顶腔很小；不能由29格总高推断完整多层驻守空间。',
  facade='断续冰墙和不规则竖柱，底层没有普通门；不凭残断程度称另一座完整城堡或给冰塔补想修复前布局。',
  roof='顶端膨大的冰壳、孔口及尖饰留档，未把小壳叫成完整大高阁；不按同材冰冠与T01归同族或分新族。',
  materials='依原blue_ice/packed_ice及底部雪地、构件识别，非空气并不自动是可站立整格平台。',
  circulation='无普通门；[7,*,11]梯仅y2、4–6、9、12–14、16–20、22–25，y3/7/8/10/11/15/21缺梯。旧记录漏梯间断不可抹去，不把稀疏竖向连接写成连续可走路线。',
  terrain='11个实体接口含流浪者和北极熊，不是11间房。作者直接选择本体及stray spawn证明其为作者场景，仍不能独自证明完整普通守望岗位、入口和房层关系。'),
 'C01': dict(
  layout='旧015-F01连续泥墙筒体托上部开台，下部围护较均匀；与T01宽低小室、细梯轴、遥隔小环台的收放不同。',
  proportion='15×25×15，实占y0–22；31批已记录存储/实占高度口径问题，本批保留旧计数，不自动重审或改旧回执。',
  facade='连续泥墙与低围边、单门分明，未因和冰壳外观不同就认定冰塔独立。',
  roof='顶上宽木盖和开台，主体连续承托；不是细冰轴上小裸环台。',
  materials='泥砖、夯实泥、云杉构件依原状态留档；分类图不替代材质观察。',
  circulation='普通门[3,5,7]，梯[9,*,5]y5–10和[5,*,9]y11–20；局部上行位置不同不是独立性充分证据。',
  terrain='原地脚与低围边属于整塔，terrain_small未展开；复看对照加0，旧scope计数保持。')}


def main():
    src = get(OUT / 'sources.json')
    rows = []
    for c in src['candidates']:
        images = [c['original_whole_image'], evidence(OUT / (c['id'] + '-details.png'))]
        if c['id'] == 'T01':
            images.append(evidence(OUT / 'T01-upper-ring.png'))
        rows.append(dict(id=c['id'], prior_identity=c['prior_identity'], source=c,
          decision='HOLD_MAST_AND_HIGH_PLATFORM_FAMILY' if c['id'] == 'T01' else
                   'EXISTING_COMPLETENESS_AND_ROUTE_HOLD_RETAINED' if c['id'] == 'T02' else 'PREVIOUS_CONTROL_NO_CREDIT',
          credit=0, credit_identity=None, scope_id=None, observations=OBS[c['id']],
          actual_images_viewed=images, native_acceptance=False, independent_human_review=False))
    dump('manual-review.json', dict(entries=rows,
      new_source_templates=0, previous_source_template_rereads=3,
      actual_new_section_images_viewed=4, actual_unique_previous_whole_images_viewed=3,
      independent_references_added=0, independent_human_review_claimed=False,
      family_question=dict(candidate='001-F11', comparison='028-F01',
        shared_spatial_organization='Low stationed space, long thin vertical connection, small remote high lookout platform.',
        observed_differences='Ice-enclosed small low rooms and bare upper ring versus wide low stilted covered area and covered high platform.',
        decision='Retain pending: ice shell, different cap and body width alone do not yet establish a distinct whole-design family; no automatic material/roof credit.'),
      prior_comparison_evidence=[evidence(BASE / f'research-20261101-dungeons-{n:03d}/manual-review.json') for n in (1, 3, 28, 31)],
      historical_comparison_limit='028-F01 observations reused from actual prior study, not counted as a newly reopened image. Seven actual PNGs in this batch, not seven buildings.',
      native_routes_verified=False, production_changes=0, checklist_deletions=0))
    parent = BASE / 'research-20261101-dungeons-031/scoped-reference-update.json'
    update = copy.deepcopy(get(parent))
    update['prior_additional_holds_retained'] = update.pop('current_batch_holds')
    update.update(prior_update=evidence(parent), added_ids=[], added_credit=0,
      old_candidate_first_scope_acceptance=[], new_source_discoveries=0,
      current_batch_holds=[dict(id='001-F11', credit=0, reason='Complete author ice tower; relationship to low-room/mast/high-platform family unresolved.'),
                           dict(id='003-F11', credit=0, reason='Original completeness/entrance/route hold retained; no full reconstruction inferred.')],
      limits='保持31批8/10/1，001-F05高度口径问题、全部旧族问题和58格超范围整塔继续保留。不能将冰材、屋帽、5/11实体点或7图作为新增完整参考。')
    dump('scoped-reference-update.json', update)
    dump('discovery-boundary.json', dict(indices_checked=[evidence(parent)], local_only=True,
      new_source_templates=0, source_templates_reread=3, actual_images_viewed=7,
      network_requests=0, java_run=False, game_run=False, scope_definitions_changed=False,
      production_changes=0, checklist_deletions=0, sound_brightness_window_save_changes=0))
    print('Ice tower and ice-fort holds recorded; 3 old source rereads, 7 actual PNGs; new references0; counts 8/10/1.')


if __name__ == '__main__':
    main()
