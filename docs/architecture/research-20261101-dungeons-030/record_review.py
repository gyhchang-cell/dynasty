#!/usr/bin/env python3
"""Manual semantic decisions from reopened whole buildings and fresh sections."""
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


OBSERVATIONS = {
 'T01': dict(
  layout='砂岩残墙围院，侧边低房与对角两处棚台占地不同，y2平面已有分室和开放院地，y6侧边层板及门联系两棚；按作者现存整院一例，不复原想象中的完好城。',
  proportion='35×18×30，非空气y0–17，属于现有约29–36格长轴、17–30格保存高度的驻防组。院墙、低房和高棚分级，不能把18格总高全当净空。',
  facade='不连续砂岩墙垛、较密低房墙身及开放木柱棚台并存。立面破损不等于待接房间；相比旧grove，不只是把残墙换成砂岩，现存棚台、侧房及其层板组织不同。',
  roof='对角两处较高四柱低坡棚盖，另有较低侧屋屋面；原灰色盖含羊毛和地毯，不能按渲染灰色称石瓦。高棚分离而中院开放，不是一个中央大屋盖。',
  materials='sand、oak_planks、cut_sandstone、smooth_sandstone、oak_slab、sandstone_stairs为主，light_gray_carpet、light_gray_wool、gray_wool用于轻盖和内装。只借围院与棚房组织，材质差别不是独立性依据。',
  circulation='下半门三处y1、三处y6；[10,*,11]梯y6–10连续，剖面可见y5和y10层板。只确认局部梯段，未证明院地到全部棚顶的原生碰撞路线；actor接口不误读为门。',
  terrain='自带砂地、残石裙与围院，14个外接点为13grunt和1captain实体池；作者pillager_outpost_desert直接以完整本体为start_pool，monster spawn为pillager。未拼actor、未执行beard_thin或地表投影。'),
 'T02': dict(
  layout='三处方角塔与一条低侧楼通过墙廊围出开院；y2仍有塔底和围边，y5可见侧楼与两角塔之间的联系。不是四角同高塔院，也不是对角双棚院换材。',
  proportion='29×21×28，非空气y0–20。低楼约y10/11屋面，较高塔帽约y15，细杆继续到y20；计为现存整院保存高度，细杆不增加可用房层或参考例数。',
  facade='红砖墙体、较窄门窗、木水平带与局部叶层形成实墙塔及低楼。现存三处角部室圈、长侧楼和院地关系，与grove残墙组织不同，不以是否覆绿或损坏程度作为新例依据。',
  roof='三座方塔小坡帽与较长的低楼双坡盖构成三点加一边的围院，墙廊更低；区别于砂岩双棚、旧Terralith四角塔加东侧高塔。屋盖含木板、半砖、活板和地毯。',
  materials='bricks、spruce_slab、spruce_planks、dirt、spruce_trapdoor、dark_oak_planks、grass_block、mangrove_leaves；灰边不笼统称天然石瓦，覆绿不能掩盖开口核查。',
  circulation='门[18,1,8]、[8,5,6]、[17,5,5]；主梯[24,*,14]y1–10，另一[20,*,17]仅y5/6。剖面见低楼和高角塔的层板差，不声称全院绕行或所有塔顶已通。',
  terrain='原草土地裙、局部残砖和8个实体socket同存于一个完整院；6grunt及2captain不拆成额外建筑。作者pillager_outpost_iberian直接选择该本体、monster spawn为pillager；未执行地形适配。'),
 'C01': dict(
  layout='旧010-F01为石残墙围院，院内一棵小云杉，角部残段与少量木层板并置。现存没有T01两处带盖棚台及侧房组合，也没有T02长侧楼和三完整角室的围院。',
  proportion='29×17×22，非空气y0–16，现存高角残墙和低院边有层级；本批继续沿旧编号，只作对照。',
  facade='石砖圆石、断墙垛和轻木栅组合，不能推测原完整未损坏形态再拿去与新例比数量。',
  roof='大部分露天，仅零星木构和残余上沿；院树不是屋顶。以现存作者遗址比较，不把不存在的屋盖补成与另一堡相同或不同。',
  materials='原stone_bricks、stone、cobblestone、dirt、grass_block和少量spruce构件留档；新例不靠材质差异获得信用。',
  circulation='[3,*,3]梯y2–7、[16,*,2]y2–4，高处普通门y8；本批剖面仍不能证明残墙全程绕行。',
  terrain='自带草土碎石和院树，7grunt及1captain接口为实体，非外接8座房屋；既有完整遗址编号本批加0。'),
 'C02': dict(
  layout='旧019-F01是四边完整方院，四角低塔另加东侧中部高塔，内院大片留空，两侧低棚带；不是T01对角双棚或T02三角室连一条低侧楼。',
  proportion='31×30×31，非空气y0–29，四边墙与四角低塔以东侧高塔为重心；相近尺度不等于相同设计。',
  facade='连续水平带和女墙围出规整四边外壳，五个竖段有明确主次；与本批残墙低围边及非对称棚楼分工不同。',
  roof='四角独立小帽与东侧高塔帽分立，低棚在院边；不按五个塔帽拆成五例。',
  materials='cut_sandstone、sandstone、smooth_sandstone与少量木构；和T01都含砂岩不能据此判同族，也不能因砂岩色不同就分族。',
  circulation='西侧四个底门，东塔梯[28,*,15]y10–22；本批y1/y12和主梯剖面只核对原存开口，未认证从底门到高塔全程通行。',
  terrain='单个本体完整存有四墙与院地，道路/村民/傀儡接口为村落连接背景，不并入本堡计数；对照加0，原地形适配未运行。')}

COMPARISONS = [
 ('010-F01', '现存grove为断墙角残段及院树。009-F01的对角有盖高棚和侧房层板、009-F04的三角室连低长楼均有不同现存平面；没有推定grove修复形态后再按破损状态分族。'),
 ('010-F02', 'jungle粗柱围中央竖向叠台和中央高大屋盖，院心被叠层主体占用。本批两例均将守备体沿边分置、保留开院，不是中央叠台换材。'),
 ('010-F03', 'old_growth_taiga近圆高木栅包中央低长营厅。本批两例外围墙与边侧棚楼分工，中院开放，没有同样的中央长厅与外围环院带。'),
 ('010-F05', 'rustic低围栏内高窄长厅加横向低翼；本批两例核心为空院、守望与驻所沿边组织，不是同样高长厅或低翼换屋顶。'),
 ('019-F01', '本批重看Terralith四边方院、四角低塔加东侧中部高塔。009-F01为对角双棚与侧低房，009-F04为三角室与一边低长楼，塔/棚数量、位置和院边功能关系均不同，不只由破损或材质造成。'),
 ('020-F01', 'forest_fort宽长屋配单端回接围院，主屋高低长盖同向并行；本批两例围绕中院沿边分散棚楼，没有宽长屋压住一个端头的共同主壳。')]


def main():
    src = get(OUT / 'sources.json')
    entries = []
    for c in src['candidates']:
        admitted = c['id'] in ('T01', 'T02')
        entries.append(dict(id=c['id'], prior_identity=c['prior_identity'], source=c,
          decision='PREVIOUS_CANDIDATE_FIRST_SCOPED_ACCEPTANCE' if admitted else 'PREVIOUS_CONTROL_NO_CREDIT',
          credit=int(admitted), credit_identity=c['prior_identity'] if admitted else None,
          scope_id='DUN03-MEDIUM-GROUND-GARRISON' if admitted else None,
          observations=OBSERVATIONS[c['id']],
          actual_images_viewed=[c['original_whole_image'], evidence(OUT / (c['id'] + '-details.png'))],
          new_source_template_credit=0, native_acceptance=False, independent_human_review=False))
    dump('manual-review.json', dict(entries=entries,
      semantic_comparisons=[dict(prior_identity=i, observation=o, additional_credit=0) for i, o in COMPARISONS],
      within_batch_semantic_comparison='009-F01对角双棚与侧低房；009-F04三角室和一条低长楼。两者保存的驻所/院/守望位置关系不同，不靠砂岩与红砖、覆绿、旋转或破损状态分开。',
      prior_comparison_evidence=[evidence(BASE / f'research-20261101-dungeons-{n:03d}/manual-review.json') for n in (9, 10, 19, 20)],
      historical_comparison_limit='Four old whole images reopened, four fresh section sheets actually viewed. Other historical observations reused from hashed prior studies, not new image or building discoveries.',
      historical_exact_self_matches='All four re-read archive/member pairs exactly match old identities. The two old candidates receive first credit in this narrow scope only, not new-source credit.',
      new_source_templates=0, previous_source_template_rereads=4,
      actual_new_section_images_viewed=4, actual_unique_previous_whole_images_viewed=4,
      independent_references_added=2, independent_human_review_claimed=False,
      credit_identity_rule='Original 009-F01 and 009-F04 only, once each; 030 row labels are not separate designs.',
      reviewer='Same Codex agent actual visual/original-state review, not independent human approval',
      native_routes_verified=False, production_changes=0, checklist_deletions=0))
    parent = BASE / 'research-20261101-dungeons-029/scoped-reference-update.json'
    update = copy.deepcopy(get(parent))
    update.update(prior_update=evidence(parent), added_ids=['009-F01', '009-F04'], added_credit=2,
      new_source_discoveries=0, old_candidate_first_scope_acceptance=['009-F01', '009-F04'],
      limits='各用途单独1000；旧完整双棚院及三角塔低楼院首次纳入现有中型驻防组。沿用旧编号，不是新增来源，亦不挪作旧双高塔、角塔L厅、低四棚或整座中式战场完成。')
    update['prior_other_exclusions_retained'] = update.pop('current_exclusions')
    for s in update['scopes']:
        if s['scope_id'] == 'DUN03-MEDIUM-GROUND-GARRISON':
            assert not set(update['added_ids']) & set(s['accepted_ids'])
            s['accepted_ids'] += update['added_ids']
            s['accepted_references'] = len(s['accepted_ids'])
            s['remaining'] = s['target'] - s['accepted_references']
    dump('scoped-reference-update.json', update)
    dump('discovery-boundary.json', dict(local_only=True,
      indices_checked=[evidence(parent), evidence(BASE / 'research-20261101-dungeons-009/manual-review.json')],
      new_source_templates=0, source_templates_reread=4, actual_new_section_images_viewed=4,
      actual_previous_whole_images_reopened=4,
      metadata_screen_is_not_visual_study=True, local_catalog_semantically_exhausted=False,
      historical_pairs_compared=get(OUT / 'dedup-evidence.json')['historical_unique_local_archive_member_pairs'],
      network_requests=0, java_run=False, game_run=False, scope_definitions_changed=False,
      production_changes=0, checklist_deletions=0, sound_brightness_window_save_changes=0))
    print('First narrow-scope acceptance of old whole identities: 009-F01, 009-F04; counts 8/10/1; new sources 0.')


if __name__ == '__main__':
    main()
