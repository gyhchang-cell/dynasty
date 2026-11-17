"""Record the actual image review separately from automatic source inspection."""
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
BASE = OUT.parent

def get(p):
    return json.loads(p.read_text())

def dump(n, value):
    (OUT / n).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')

def evidence(p):
    return dict(path=str(p.resolve()), sha256=hashlib.sha256(p.read_bytes()).hexdigest())

OBSERVATIONS = [
 dict(layout='一座紧凑小屋与不规则岩土绿化地脚；低处门与上部小室集中在单一主干，没有围合守备院带。',
      proportion='保存盒25×37×21，实占y0–35；尖长弯曲屋帽贡献显著高度，不能把屋帽长度解释为驻守楼层。',
      facade='底层岩石及木构入口、上层紧凑开口、侧向细烟囱／外挑构件；未见宽守望环台。',
      roof='不对称陡斜高帽逐段收尖，适合学习轮廓控制，但帽尖不等于上室。',
      materials='原状态含红树木板、深色橡木板/半砖、滴水石、红树叶与泥根等；分类色全景不证明真实材质观感。',
      circulation='下半门均在y2；梯(14,8)y7–10、(14,9)y11/12/14–16，y13缺梯。未认证原生碰撞或完整路线。',
      terrain='自带不规则低岩土及植物衔接；作者beard_thin地表配置不等于实测地形适配。'),
 dict(layout='低岩土围合小空间与紧凑竖向小屋共置，上室偏移，未形成守备院带、驻所及瞭望组合。',
      proportion='保存盒24×41×23，实占y0–39；很高的收尖帽顶与小房体比例不能转译成多层驻防塔。',
      facade='岩木混合低座、植物与上部小开口；屋帽外挑明显，和F01同为紧凑高帽小屋主题。',
      roof='单侧长坡与尖帽逐级转折；没有因此确认一个独立新守望族。',
      materials='草方块、石、橡树叶、红树木、深橡木、圆石及安山岩等；颜色归类图合并了实际方块差异。',
      circulation='下半门y1四处、y11一处；数段短梯换轴且有空缺，门多不等于守备单元多。',
      terrain='低岩土外圈含植物，原来源与F01在同一选择池；不把选择权重或不同地脚算作两座有效相近守备建筑。'),
 dict(layout='高树主干上附小平台、上部小屋与低树冠地脚；4个实体接口全指丛林村民池。',
      proportion='保存盒26×48×19，实占y0–44；树冠与长树干贡献大部分高度，不能当成封闭驻守塔楼层。',
      facade='细树干配外悬泥砖平台和栅栏，低处另有树冠；没有地面守备厅与偏置瞭望段的连续厅房。',
      roof='叶冠覆在高处小屋上，不是独立塔的层层守望覆顶。',
      materials='丛林树叶、藤蔓、草方块、丛林原木、泥砖半砖等为主；需要按真实承托和平台关系学习，不能仅依绿色分类色。',
      circulation='普通门0、梯0，存在藤蔓与分层悬台；4个村民点在y1/14/21/30，不是4座建筑，未认证可攀通行。',
      terrain='地表低植物环带、两处主要树冠；作者丛林标签与地表投放仅为来源配置，未原生生成验收。'),
 dict(layout='近方形整座大屋，多条纵向分隔与侧向突出处组成室内，缺少当前堡营要求的守备主体—院带—高低守望关系。',
      proportion='保存盒33×25×33，实占y0–24；平面虽接近堡营尺寸，空间仍是宽大的覆顶屋体，不凭外盒尺寸纳入。',
      facade='木柱框格、石基、连续低檐与山墙；作者参考图只显示入口局部，不冒称整屋实机验收。',
      roof='大面积陡坡并交接横向坡面，覆住主要屋体；不是边界墙头或独立高守望塔。',
      materials='青色陶瓦、去皮深色橡木、木楼梯/活板门、深板岩瓦、石砖及松叶等；已提取作者原始入口参考图，未制作贴图。',
      circulation='下半门4处均y8，梯(7,16)y1–6；重复室内分隔及多层空间需与守备动线区别，敌对实体存在不能替代空间用途判断。',
      terrain='近方形草地底座与建筑边缘植物，自带地脚未构成防御院落；未运行地形或游戏测试。')
]

def main():
    src = get(OUT / 'sources.json')
    src.update(new_source_templates=4, previous_source_template_rereads=0)
    dump('sources.json', src)
    decisions = [
      'EXCLUDED_CURRENT_SCOPES_HIGH_HAT_COMPACT_HUT',
      'EXCLUDED_CURRENT_SCOPES_HIGH_HAT_COMPACT_HUT_FAMILY_NOT_SEPARATELY_CREDITED',
      'EXCLUDED_CURRENT_SCOPES_VILLAGER_TREEHOUSE',
      'EXCLUDED_CURRENT_SCOPES_RABBIT_KEEPER_DWELLING_NOT_GARRISON_LAYOUT']
    reasons = [
      '高帽紧凑小屋，无当前地面堡营／单塔守望／连厅布局证明；34个原僵尸实体部分自名the gnome，不能据敌对类型推断为守军。',
      '45个原僵尸实体及同池权重不证明守望用途；与F01的同族独立性未成立，不给两项设计信用。',
      '作者4接口全为村民池，树干悬台居住组织不符合当前守备定义。',
      '作者中英文说明为养兔灾厄村民居所；虽含僵尸卫道士等敌对实体，屋体和房间组织仍不满足当前堡营范围。']
    entries = []
    for c, obs, decision, reason in zip(src['candidates'], OBSERVATIONS, decisions, reasons):
        imgs = [evidence(OUT / f"{c['id']}-{suffix}.png") for suffix in ('whole','details')]
        if c['id'] == 'F04':
            imgs.append(evidence(OUT / 'F04-author-reference.png'))
        entries.append(dict(id=f"033-{c['id']}", source=c, decision=decision,
            observations=obs, reason=reason, credit=0, credit_identity=None,
            actual_images_viewed=imgs, native_acceptance=False, independent_human_review=False))
    review = dict(batch=33, date='2026-11-02', new_source_templates=4,
        previous_source_template_rereads=0, independent_references_added=0,
        actual_unique_images_viewed=9, actual_whole_images_viewed=4,
        actual_section_images_viewed=4, actual_author_detail_images_viewed=1,
        generated_but_not_claimed_viewed='Four plan PNGs and four vertical PNGs are generated aids, not additional viewed images or buildings.',
        independent_human_review_claimed=False, entries=entries,
        same_pool_family_question=dict(ids=['033-F01','033-F02'],
            decision='Both excluded by spatial use; not claimed two distinct relevant designs. Shared selector is not itself proof of identical geometry or independent family.'),
        source_manifest_discrepancies='ATI filename1.4.2 but manifest version1.4.0/displayName Structory/authors ATi; Goety filename1.3.8internal but manifest1.3.7/Team k1sak1. Retain literal identities.',
        native_routes_verified=False, production_changes=0, checklist_deletions=0)
    dump('manual-review.json', review)
    prior_path = BASE / 'research-20261101-dungeons-032/scoped-reference-update.json'
    prior = get(prior_path)
    scope = dict(prior)
    scope.update(prior_update=evidence(prior_path), added_ids=[], added_credit=0,
        new_source_discoveries=4, old_candidate_first_scope_acceptance=0,
        prior_ice_holds_retained=prior['current_batch_holds'], current_batch_holds=[],
        current_batch_exclusions=[dict(id=e['id'], decision=e['decision'], reason=e['reason'], credit=0) for e in entries],
        height_basis_question_retained=evidence(BASE / 'research-20261101-dungeons-031/manual-review.json'),
        limits='保持32批8/10/1；四个新模板不等于四个有效相关建筑，9图不等于9设计。001-F05/015-F01保存盒与实占高口径、全部旧族与冰塔待查和58格整塔超范围排除保持。')
    dump('scoped-reference-update.json', scope)
    boundary = get(OUT / 'discovery-boundary.json')
    boundary.update(new_source_templates=4, actual_images_viewed=9,
        historical_distinct_archive_member_pairs=217, new_distinct_archive_member_pairs=4,
        scoped_valid_references_added=0, scope_definitions_changed=False,
        production_changes=0, checklist_deletions=0, sound_brightness_window_save_changes=0,
        sampling_limit='Four exact-unmatched size-selected templates only; no claim the remaining local queue is exhausted or that these are related whole-building references.')
    dump('discovery-boundary.json', boundary)

if __name__ == '__main__':
    main()
