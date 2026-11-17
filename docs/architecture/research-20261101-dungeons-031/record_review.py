#!/usr/bin/env python3
"""Preserve a height-basis question without changing existing scope totals."""
import copy
import hashlib
import json
from pathlib import Path
import sys
from zipfile import ZipFile

OUT = Path(__file__).resolve().parent
BASE = OUT.parent
sys.path.insert(0, str(OUT.parents[2] / 'tools/architecture'))
from nbt_read import read


def get(p):
    return json.loads(p.read_text())


def evidence(p):
    return dict(path=str(p), sha256=hashlib.sha256(p.read_bytes()).hexdigest())


def dump(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


OBS = {
 'T01': dict(
  layout='一座方形石塔以四角较厚中空区围中央叠层主室，四个角区延续至上部，不是四座独立建筑。y15平面见四处分散角梯，中央仍为同一主室层。',
  proportion='存储19×25×19，但实占x0–18、y0–22、z0–18：保存方块总高23格，y23/24为空。不能单凭25格盒高认定达到25格实际保存高度。',
  facade='四角竖向厚柱与中央墙面贯穿楼层，顶部木带和小开孔成水平分界；比default大上台托宽屋盖更连续，和dark_keep中层挑廊、低附院也不同。',
  roof='四角短垛包中央台阶收分小屋盖，顶层四角梯与屋面相邻；短垛和屋顶不拆成新塔，也不把各角都当可独立使用的角楼。',
  materials='polished_andesite、cracked_stone_bricks、stone_bricks配spruce_planks、dark_oak_slab等。独立性不能靠石灰色、红砖色或木色决定，原状态与分类色分开。',
  circulation='双门[11,5,2]/[12,5,2]。四角普通梯分别在[1,*,15]、[3,*,1]、[15,*,17]、[17,*,3]，均y15–19；中央选剖不切中这些角梯，因此另以原状态核对。只证明上角梯段，不宣称底部至顶全程已验。',
  terrain='一个向下terrain_small接口，作者结构直接选择illager_tower；原实体含多层掠夺者、卫道士和唤术师，支持驻守用途。源模板本体完整，但高度门槛和同族独立性仍须按一致口径处理。'),
 'T02': dict(
  layout='旧016-F01为紧凑叠室柱塔，最高驻守层成为较宽开放有盖平台。它与001-F05四角厚竖区围中央室不同，但这不自动解决它与其他紧凑叠室塔的原型问题。',
  proportion='15×25×15，实占y0–23；保持旧待查0，不因本轮重看就纳入。保存盒和实占方块高同时记录。',
  facade='下部木石窄墙、逐层木带与高开台形成上宽下窄轮廓；上平台外柱不是独立屋子。',
  roof='大浅阶坡顶覆盖上开台，屋盖明显比下段主壳宽；区别于001-F05四角短垛包小收分顶，不以顶色认族。',
  materials='依原NBT木材、石材、栏杆、阶块状态区分墙体与屋盖；分类色不足以认定所有灰块为可行走楼板。',
  circulation='无普通门，三段梯分别[7,*,4]y2–6、[4,*,10]y7–10、[5,*,10]y11–14；不像001-F05四处分散角梯，局部位置变化仍不等于整个设计族独立。',
  terrain='旧完整模板及底脚保留，actor socket不计作独立建筑；原型问题继续0，未运行生成。'),
 'T03': dict(
  layout='旧011-F04紧凑塔室围中部竖柱叠置，y6主要切中一层木板，y20位于大屋盖下，上层活动空间与中心柱相邻。',
  proportion='15×39×15，实占y0–38，尖顶和旗杆决定很大一段保存高度；不能凭总高39就视为更多同规模房间。',
  facade='窄塔身、木带和屋盖下小开口，上部较宽；与default相似的叠室/上部帽顶关系仍需在原有同族候选之间继续证明。',
  roof='陡尖砖盖和旗，不是额外独立塔楼；本轮没有因为盖坡比default陡就单独给数。',
  materials='木石主体和砖屋盖依原始状态区分，换材与旗饰不能替代平面、室层、承托和交通组织的独立性证据。',
  circulation='无普通门，普通梯[6,*,7]y14–20，中心柱与梯相邻；本批剖面仍不能把不同帽顶视为不同完整室层原型。',
  terrain='原完整地脚与实体接口保留，旧tudor和其他候选族问题继续待查；无地形、碰撞或全程路径验收。'),
 'C01': dict(
  layout='旧002-F02单个矩形主堡叠室，低附院、中层外挑廊与上部大室分工。本批y12平面同时见侧廊和主室，y20收成主壳单室。',
  proportion='20×35×22，非空气y0–34；顶尖不作新房层。它在29批已入账，本轮复看加0。',
  facade='深石竖角柱、窄窗和中层挑廊，比001-F05连续四角厚区多了明确低院及外廊分工。',
  roof='集中陡坡主屋盖带短角饰；不把其四处角饰与001-F05中空角梯区混为同一种房间组织。',
  materials='深板岩、玄武岩与木层等原始材料留档；深浅色不单独作为原型划分依据。',
  circulation='门在y2、12、20，主楼内阶块及y11/y19木板分层；原无普通梯，并不表示没有内阶或另有未存楼梯。',
  terrain='唯一terrain_small向下接口和低附院仍属于一个完整主堡；未拆围院或屋顶加数。')}


def main():
    src = get(OUT / 'sources.json')
    rows = []
    for c in src['candidates']:
        decision = ('HOLD_HEIGHT_BASIS_AND_FAMILY' if c['id'] == 'T01' else
                    'EXISTING_FAMILY_HOLD_RETAINED' if c['id'] in ('T02', 'T03') else 'PREVIOUS_CONTROL_NO_CREDIT')
        rows.append(dict(id=c['id'], prior_identity=c['prior_identity'], source=c,
          decision=decision, credit=0, credit_identity=None, scope_id=None,
          observations=OBS[c['id']], actual_images_viewed=[c['original_whole_image'], evidence(OUT / (c['id'] + '-details.png'))],
          new_source_template_credit=0, native_acceptance=False, independent_human_review=False))
    c = src['candidates'][0]
    with ZipFile(c['source_archive']) as z:
        d = read(z.read(c['member']))
    dump('authored-use-evidence.json', dict(
      id='T01', prior_identity='001-F05', nbt_sha256=c['nbt_sha256'],
      entities=[dict(position=e.get('pos'), id=e.get('nbt', {}).get('id')) for e in d.get('entities', [])],
      ordinary_guard_role_evidence_present=True, native_entities_spawned=False, building_credit=0,
      limits='Guard entities support intended use, not height eligibility, family novelty or tested passability.'))
    dump('manual-review.json', dict(entries=rows,
      actual_new_section_images_viewed=4, actual_unique_previous_whole_images_viewed=4,
      previous_source_template_rereads=4, new_source_templates=0, independent_references_added=0,
      prior_comparison_evidence=[evidence(BASE / f'research-20261101-dungeons-{n:03d}/manual-review.json') for n in (1, 16, 29)],
      comparison_result='Four thick hollow corner zones and four upper corner ladders deserve further family comparison. They do not resolve the 25 stored versus 23 occupied height question. Do not promote this old tower merely because it is complete and has guard entities.',
      height_consistency_issue=dict(candidate='001-F05', stored_height=25, occupied_y=[0,22], occupied_height=23, top_stored_empty_layers=[23,24],
        prior_comparable='015-F01', prior_stored_height=25, prior_occupied_y=[0,22],
        action='Flag stored-size versus occupied-height basis for consistent scope review; preserve existing accepted totals pending that review, do not silently redefine scope or retrospectively change another receipt.'),
      historical_exact_self_matches='All four sources are old exact self identities; no new-source credit.',
      independent_human_review_claimed=False, native_routes_verified=False, production_changes=0, checklist_deletions=0))
    parent = BASE / 'research-20261101-dungeons-030/scoped-reference-update.json'
    update = copy.deepcopy(get(parent))
    update.update(prior_update=evidence(parent), added_ids=[], added_credit=0,
      old_candidate_first_scope_acceptance=[], new_source_discoveries=0,
      current_batch_holds=[dict(id='001-F05', credit=0, reason='Stored height25 but actual occupied height23; height basis and broader family independence unresolved.')],
      limits='保持30批8/10/1及所有旧待查。001-F05不借顶部空层凑25格，不自动重算历史已入账泥塔，也不把3张塔图或4角梯区当作多个新参考。')
    dump('scoped-reference-update.json', update)
    dump('discovery-boundary.json', dict(indices_checked=[evidence(parent)], local_only=True,
      new_source_templates=0, source_templates_reread=4, actual_images_viewed=8,
      network_requests=0, java_run=False, game_run=False, scope_definitions_changed=False,
      production_changes=0, checklist_deletions=0, sound_brightness_window_save_changes=0))
    print('Four old bodies reviewed; 001-F05 held on occupied-height/family basis; old family holds retained; counts unchanged 8/10/1.')


if __name__ == '__main__':
    main()
