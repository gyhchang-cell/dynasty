"""Propose one first admission of held W028, without rewriting any formal ledger."""
import hashlib
import json
from pathlib import Path
OUT=Path(__file__).resolve().parent
BASE=OUT.parent
def get(p):return json.loads(p.read_text())
def dump(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def evidence(p):return dict(path=str(p.resolve()),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def main():
    src=get(OUT/'sources.json');src.update(new_source_templates=2,previous_source_template_rereads=1)
    for c in src['candidates']:
        target='goetyawaken:'+c['member'].split('/structures/')[1][:-4]
        c['pool_references']=[r for r in c['pool_references'] if any(e['element'].get('location')==target for e in r['data']['elements'])]
        c['pool_reference_semantics']='Exact element.location selection only; actual structure root and old unnumbered pool bound separately.'
    src['source_archives'][0]['provenance_url_role']='issueTrackerURL in archive manifest, not publisher homepage'
    dump('sources.json',src)
    common=dict(
        layout='单模板完整地下陵墓体，内部有多层室、通道、中央和边部空间。上部y33/35四个厚墙角部体之间形成十字形内向通道，中部大空间与低部侧室有不同划分。原start_pool直接选择1或2之一，两个候选均0jigsaw，不需把两份拼成上下半部。',
        proportion='保存37×48×37，原非空气实占x0–36/y0–46/z0–36；保存48、实高47分别保留，不压低成村祠或守望塔。整个墓体仅一实例，房间、地下层或37格边长都不另外计数。',
        facade='四角厚竖向支撑与重复横带包围墓室，闭合厚外壳内的通道/房间可从切面分辨；外立面是地下构筑壳，不把包埋状态冒充可见地上宫殿。',
        roof='多级收分厚顶覆盖全部地下主体，中央顶部原状态为柱台、(18,45,18)木桶及y46半砖。没有把木桶改称墓石或把厚顶高度当成可驻守楼层；原书墓石叙述与实测顶轴分别记录。',
        materials='crypt_bricks19881、crypt_plinth2670、crypt_pillar2101、shade_bricks_wall2068等；black_wool3934原样保留，未隐藏、替换或当作空气。分类色仅辅助读布局，不能证实原材质或碰撞；三模板30022个选定骨架状态完全相同。',
        circulation='原普通门0。上层十字通道、中下部大室与侧室的邻接可读；原作者书页描述封闭墓石下向深处掘进，但没有认证墓石坐标、外部入口、连续挖掘路线、逐层通行或玩家可达。入口未知继续保留，完整作者模板边界不冒充原生通路验收。',
        terrain='原jigsaw结构根选择the_mausoleum/start_pool，underground_structures、start_height[-40,0]与bury；无外接结构socket，处理器配置仅水浸自定义及箱/桶战利品规则。学习葬室、封闭外壳和通道的分级关系；地上义庄的道路/坡地接入不能照搬埋置墓体。')
    first=dict(id='042-F01',source_candidate_id='F01',source_evidence=evidence(OUT/'sources.json'),observations=common,
        decision='PROPOSE_FIRST_SCOPE_ADMISSION_OF_PREVIOUSLY_HELD_W028',
        proposal_identity='COD4-R001-W028',previous_candidate_id='W028',newly_discovered_design=False,
        proposed_credit=1,formal_credit_added=0,coordinator_acceptance_pending=True,
        relevance='作者中英书页明确陵墓、墓主、陪葬物与向下甬道，与墓地配套葬室空间相关；只比较完整墓体的室、甬道、封闭边界和上下关系，不声称它是义庄、中式建筑或生存入口已验。',
        resolved_part_of_old_hold='实际根池二选一而非两份拼接；两新模板均无外接socket；三份同名体在原坐标共享30022骨架状态，属于一个完整墓体家族。',
        retained_part_of_old_hold='作者书页未替代真实入口和连续掘进/通行证明；此部分未知随提案提交，不删除旧暂缓记录。',
        complete_author_template_body_confirmed=True,native_entry_or_routes_verified=False,independent_human_review=False,
        actual_images_viewed=[evidence(OUT/n) for n in ['F01-whole.png','F01-details.png','F01-upper-levels.png']])
    second_obs=dict(common)
    second_obs.update(layout='与F01和旧W028同一墓体家族：上下层、十字通道、侧室、外壳和屋盖骨架一致。内部内容和空气编码有差异，不当成第二个完整设计。',
        materials='30022处选定原骨架状态与F01/旧W028一致；F01→F02总1809处状态差异中1721处为未存→显式air，另有蛛网、祭坛、床/告示牌等变化。原黑羊毛仍3934，不说所有差异均换色或均空气。',
        circulation='布局骨架不变不代表玩法相同；两版祭坛、告示牌、床、笼及方块实体分布不同。F02实际入口、挖掘路线与连续通行同样未验，不因同族排重隐藏这些差别。')
    second=dict(id='042-F02',source_candidate_id='F02',source_evidence=evidence(OUT/'sources.json'),observations=second_obs,
        decision='SAME_W028_BUILDING_FAMILY_NO_SECOND_PROPOSAL',proposal_identity='COD4-R001-W028',proposed_credit=0,formal_credit_added=0,
        complete_author_template_body_confirmed=True,native_entry_or_routes_verified=False,independent_human_review=False,
        actual_images_viewed=[evidence(OUT/n) for n in ['F02-whole.png','F02-details.png']])
    old=BASE/'continuation-20261022/references/whole-candidates/W028.png'
    dump('manual-review.json',dict(batch=42,date='2026-11-03',new_source_templates=2,previous_source_template_rereads=1,
        actual_new_images_viewed=5,actual_old_comparison_images_viewed=1,actual_images_viewed=6,
        old_comparison_images=[evidence(old)],entries=[first,second],
        proposed_first_scope_admissions=1,newly_discovered_designs=0,formal_credit_added=0,
        generated_not_claimed_viewed=['F01-plan.png','F01-vertical.png','F02-plan.png','F02-vertical.png'],
        production_changes=0,checklist_deletions=0))
    pp=BASE/'research-20261103-funerary-041/scope-status.json';scope=get(pp)
    scope['prior_scope_status']=evidence(pp)
    scope['funerary'].update(batch_proposed_credit=1,proposal_identity='COD4-R001-W028',formal_credit_added=0,
        coordinator_acceptance_pending=True,formal_baseline=148,remaining_formal=852,owner_proposed_total_if_accepted=149,owner_proposed_remaining_if_accepted=851,
        proposal_is_old_hold_first_admission_not_new_discovery=True)
    dump('scope-status.json',scope)
    dump('session.json',dict(date='2026-11-03',owner='做建筑的',batch=42,status='W028_FAMILY_BOUNDARY_PROPOSAL_PENDING_INTEGRITY',
        previous_receipt=evidence(BASE/'research-20261103-funerary-041/RECEIPT.json'),
        formal_funerary_baseline=148,new_first_scope_proposals=1,coordinator_acceptance_pending=True,production_allowed=False,
        next='交协调核收旧W028完整边界补证与入口未知；继续未读完整相关墓园/义庄范围，不把同族模板、房间或视图累计为新实例。',
        shared_coordinator_session_not_overwritten=True,coordinator_only_main_checklist=True,
        java_run=False,game_run=False,network_requests=0,no_automation=True,duration_hours_claimed=0))
    print('One proposed first admission under old W028 identity; formal148 unchanged, entry/native routes explicitly unknown.')
if __name__=='__main__':main()
