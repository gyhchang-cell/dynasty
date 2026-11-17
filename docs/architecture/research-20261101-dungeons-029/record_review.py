#!/usr/bin/env python3
"""Record actual visual review; no new discovery or production credit."""
from collections import Counter
import copy
import hashlib
import json
from pathlib import Path
import sys
from zipfile import ZipFile

OUT = Path(__file__).resolve().parent
BASE = OUT.parent
ROOT = OUT.parents[2]
sys.path.insert(0, str(ROOT / 'tools/architecture'))
from nbt_read import read


def sha(data):
    return hashlib.sha256(data).hexdigest()


def evidence(path):
    return dict(path=str(path), sha256=sha(path.read_bytes()))


def get(path):
    return json.loads(path.read_text())


def dump(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


OBSERVATIONS = {
    'T01': dict(
        layout='单一矩形主堡沿同一竖轴叠置驻守房间，侧接较低入口围院；y20的单上室位于主堡壳内，不是低厅端头另起的细塔。低院、主楼、挑廊连同地脚按一个完整设计研究。',
        proportion='存储20×35×22，非空气y0–34。主堡占主导，侧院只形成低入口过渡；35格是保存总高，屋坡和角部尖饰不当成可用层数。',
        facade='深石竖角柱围住紧凑矩形上室，中层有外挑木廊和窄窗；顶层大体维持主室的墙圈，区别于宽平台上退进小房，也区别于多根并置细竖室。',
        roof='集中陡坡主屋盖带角部短尖饰，覆盖封闭主室；不是一片宽平屋盖架在长空杆上。x7/z7剖面见上室与y19楼板，但不能由该剖面把其余尖饰各认作房间。',
        materials='原始cobbled_deepslate、deepslate_bricks、deepslate、smooth_basalt和deepslate_tiles构成深石围护，木挑廊、楼板、窗另成轻构件；PNG仅用分类色，未作真实材质效果评价。',
        circulation='六个底层下半门在y2，中层门[7,12,7]及上层门[8,20,15]，剖面可见y11/y19楼板和主楼内台阶。原NBT的16个守卫实体分布在底层、y12和y20，支持多层驻守用途；没有普通梯子不能推断无内阶，也不声称已验证真实台阶碰撞或逐层通关。',
        terrain='唯一向下接口位于[10,0,11]，terrain_small、final_state=dirt，只指向地形模板；作者start_pool直接选整个dark_keep。低围院不需另接房间才能形成图示主体，未验证原生坡地接缝。'),
    'T02': dict(
        layout='窄偏塔与两块相连的低厅形成横向驻所，y3、y12平面及x11剖面共同显示低厅向塔侧接入，不能裁掉低厅只数塔。',
        proportion='存储17×38×23，非空气x0–16、y0–37、z0–21。长轴存储23格、实占22格；同时缺少当前连厅范围的连续横向门廊对应证据，不能仅因尺寸接近就扩范围。塔尖延长保存高度，不证明主要驻守空间沿单塔叠置。',
        facade='泥砖塔壳与木横带、低厅窗面有明确高低分工；这不是T01高宽主堡配低围院的同一外壳换材。',
        roof='一端高陡尖顶与低厅长坡顶相接，尖饰很长；屋顶收尖段的空隙不计作完整驻守层。',
        materials='mud_bricks、spruce_trapdoor、spruce_stairs、oak_wood、spruce_planks组成红褐墙壳和木构，不能把分类色笼统叫成红砖。',
        circulation='下半门在y1、7、12；[11,*,10]普通梯子仅y1–3。y7低厅和y12偏塔是不同房间联系，原husk实体不是普通驻守用途的充分证据；未将装饰台阶当作已验证路线。',
        terrain='向下terrain_small接口的final_state为spruce_planks，和T01的dirt不同。整座旧小堡仍保留完整研究记录，当前三个窄范围均不计；未改作者文件或拼接地基。'),
    'C01': dict(
        layout='旧015-F01是连续泥墙塔筒承托上部开台；y6围护和y21开台不同于T01有中层外挑廊、闭合上室的多层堡楼。',
        proportion='15×25×15、非空气y0–22，主要围护是一根较均匀塔筒，平面紧凑；已有有效编号保持原计数。',
        facade='泥墙实面和低脚围边为主体，中段没有T01那样沿主室外缘的突出通廊。',
        roof='上部为木构开放屋盖及开台，没有T01闭合上室的陡坡集中主屋盖。',
        materials='泥砖、夯实泥和云杉木等原始状态保留；比较的是连续围护关系，不以换材增加例数。',
        circulation='门[3,5,7]，两段普通梯为[9,*,5]y5–10及[5,*,9]y11–20；与T01室内台阶组织不同，连接及真实碰撞未作游戏验收。',
        terrain='低脚围边和塔身已有同一完整身份；底接口不另算基座建筑，作为对照本批加0。'),
    'C02': dict(
        layout='旧013-F01为不对称并置的小竖室和高低台；y12平面有两段相接围护，y20两处分离的小壳，和T01主堡宽上室并非同一空间组织。',
        proportion='23×38×23，旗及屋帽计入保存总高，不能把塔顶旗杆当成人可站立房层。',
        facade='石面、独立凸出竖段、台口与底层入口小盖形成多重体块；T01是相对集中的矩形主壳和同层挑廊。',
        roof='不等高平台与一个偏置尖帽相邻，不是T01对主室统一覆盖的集中陡坡盖。',
        materials='按原NBT石材、木材、门及原梯状态识别；分类色不证明真实纹理观感，也不按材质拆新例。',
        circulation='下半门在y2、10、18；梯[12,*,16]y18–22与高位小竖室对应。多处actor接口不算新建筑，未作原生碰撞或通关测试。',
        terrain='完整base_plate及自带地脚沿用原身份；不把底部地景和竖室拆成多例。本批复看加0。'),
}


def main():
    src = get(OUT / 'sources.json')
    authors = []
    for c in src['candidates'][:2]:
        with ZipFile(c['source_archive']) as z:
            raw = z.read(c['member'])
            d = read(raw)
            metadata = z.read('META-INF/mods.toml')
        authors.append(dict(
            id=c['id'], prior_identity=c['prior_identity'], nbt_sha256=sha(raw),
            metadata=dict(member='META-INF/mods.toml', sha256=sha(metadata), text=metadata.decode()),
            declared_metadata_limit='Local manifest declares version 1.4.0, displayName Structory, authors ATi; filename says V1.4.2. Preserve these literally; no network verification.',
            entities=[dict(position=e.get('pos'), id=e.get('nbt', {}).get('id')) for e in d.get('entities', [])],
            actor_building_credit=0, native_entities_spawned=False))
    dump('authored-use-evidence.json', dict(entries=authors, network_requests=0, java_run=False, game_run=False))

    observations = []
    for c in src['candidates']:
        admitted = c['id'] == 'T01'
        control = c['id'].startswith('C')
        observations.append(dict(
            id=c['id'], prior_identity=c['prior_identity'], source=c,
            decision='PREVIOUS_CANDIDATE_FIRST_SCOPED_ACCEPTANCE' if admitted else
                     'PREVIOUS_CONTROL_NO_CREDIT' if control else 'WHOLE_DESIGN_OUTSIDE_UNCHANGED_SCOPES',
            credit=1 if admitted else 0, credit_identity=c['prior_identity'] if admitted else None,
            scope_id='DUN03-SINGLE-WATCHPOST' if admitted else None,
            observations=OBSERVATIONS[c['id']],
            actual_images_viewed=[c['original_whole_image'], evidence(OUT / (c['id'] + '-details.png'))],
            new_source_template_credit=0, native_acceptance=False, independent_human_review=False))

    comparisons = [
        ('011-F01', 'birch以细颈托宽上房；002-F02由连续主堡房层配同层外挑廊，不是下细杆加一块突然外扩的大上房。'),
        ('011-F02', 'oriental是同心层台逐级收尖；002-F02是一个矩形驻守主壳和集中坡盖，层台组织不同。'),
        ('012-F01', 'forest为偏置破损台和长外阶；002-F02驻守室层收在完整主堡内，不是同样破损或外攀骨架的修补态。'),
        ('012-F02', 'mushroom_fields是束腰、偏移房层交错；002-F02主室墙圈相对连续，上下房层以外廊和低院分工。'),
        ('013-F01', '本批重看：snowy_plains不对称并置小竖室和高低台；002-F02上层是主堡内一个较宽房间，非并列小竖段。'),
        ('015-F01', '本批重看：mud为连续泥墙筒托开放顶台；002-F02具有多层封闭房间、中层外廊和坡盖上室，差异不是换材。'),
        ('016-F02', 'dark_forest宽底斜撑向上收为两个开放平台；002-F02上下为主楼封闭驻守室，围护与承托组织不同。'),
        ('013-F03', 'taiga下部开放框架承宽台，台上是退进小房和环边外台；002-F02是主壳叠层、侧附低院、中层挑廊，不是台上同一小房改材。'),
        ('028-F01', '上批offshore以宽低棚台、长细桅和远隔的小有盖瞭望台组成岗位；002-F02上下驻守室在连续堡壳内，没有长空桅分隔低棚和高台。'),
    ]
    prior_evidence = [evidence(BASE / f'research-20261101-dungeons-{n:03d}/manual-review.json') for n in (2, 21, 28)]
    dump('manual-review.json', dict(
        entries=observations,
        semantic_comparisons=[dict(prior_identity=i, observation=v, additional_credit=0) for i, v in comparisons],
        prior_comparison_evidence=prior_evidence,
        historical_comparison_limit='Only four old whole images actually reopened this batch. Other prior whole-image observations reused from hashed evidence; do not claim new visual readings of nine historical controls.',
        historical_exact_self_matches='All four rereads match their original archive/member and geometry. Expected old identities, never newly found sources; 002-F02 is admitted only once to the narrow scope.',
        scope_fit='002-F02: complete 20×35×22 single vertical guard keep with low attached entry enclosure. Main stationed spaces are in its stacked main rooms; raw author entities and doors support that reading. No enlargement of the three definitions.',
        new_source_templates=0, previous_source_template_rereads=4,
        actual_new_section_images_viewed=4, actual_unique_previous_whole_images_viewed=4,
        independent_references_added=1, credit_identity_rule='Retain original 002-F02 exactly once; 029-T01 is a review row only, not another design.',
        reviewer='Same Codex agent visual and original-state review, not independent human approval',
        independent_human_review_claimed=False, native_routes_verified=False,
        production_changes=0, checklist_deletions=0))

    parent_path = BASE / 'research-20261101-dungeons-028/scoped-reference-update.json'
    update = copy.deepcopy(get(parent_path))
    update['prior_update'] = evidence(parent_path)
    update['added_ids'] = ['002-F02']
    update['added_credit'] = 1
    update['new_source_discoveries'] = 0
    update['old_candidate_first_scope_acceptance'] = ['002-F02']
    update['current_exclusions'] = [dict(id='002-F06', credit=0, reason='Whole low halls plus narrow side tower; insufficient correspondence to unchanged narrow single-watchpost or hall-with-transverse-porch scopes.')]
    update['prior_58_block_assembly_exclusion_retained'] = dict(id='028-A01', complete_size=[18, 58, 18], credit=0, scope_height_max=53)
    update['limits'] = '三个用途分别1000；002-F02仅以旧完整主堡身份首次纳入单塔范围，不代表新来源或正式建筑制作。002-F06不靠裁掉低厅凑单塔，58格作者整塔继续超范围计0。'
    for scope in update['scopes']:
        if scope['scope_id'] == 'DUN03-SINGLE-WATCHPOST':
            assert '002-F02' not in scope['accepted_ids']
            scope['accepted_ids'].append('002-F02')
            scope['accepted_references'] = len(scope['accepted_ids'])
            scope['remaining'] = scope['target'] - scope['accepted_references']
    dump('scoped-reference-update.json', update)

    checked = [BASE / 'research-20261101-dungeons-026/remaining-size-review-queue.json', parent_path,
               BASE / 'research-20261101-dungeons-002/manual-review.json',
               BASE / 'research-20261101-dungeons-028/assembly-evidence.json']
    dump('discovery-boundary.json', dict(
        indices_checked=[evidence(p) for p in checked], local_only=True,
        reason='Reconcile previous complete uncredited candidates from the fixed local size-screen with current narrow semantic scopes.',
        source_templates_reread=4, new_source_templates=0, new_section_images_actually_viewed=4,
        previous_whole_images_actually_reopened=4, metadata_screen_is_not_visual_study=True,
        historical_pairs_compared=get(OUT / 'dedup-evidence.json')['historical_unique_local_archive_member_pairs'],
        local_catalog_semantically_exhausted=False, network_requests=0, java_run=False, game_run=False,
        automatic_reference_credit=0, scope_definitions_changed=False,
        production_changes=0, checklist_deletions=0, sound_brightness_window_save_changes=0))
    dump('source-needs.json', dict(
        scopes=[dict(scope_id=s['scope_id'], accepted=s['accepted_references'], target=s['target'], remaining=s['remaining']) for s in update['scopes']],
        construction_allowed=False,
        next_review_rule='Continue semantically relevant complete local designs or verifiable author assemblies; reconcile previous identity and scope first. Queue rows are not accepted references; unrelated dwellings, actor sockets, components, recolours, rotations and damaged states cannot fill the target.',
        preserve_holds_and_exclusions=True, all_scopes_separate=True))
    print('Old candidates reviewed: 2; accepted controls reread: 2; new sources: 0; first narrow-scope acceptance: 002-F02; counts: 6/10/1.')


if __name__ == '__main__':
    main()
