"""Save one whole-layout observation, with explicit scope and height limits."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

OUT=Path(__file__).resolve().parent
BASE=OUT.parent

def get(p):return json.loads(p.read_text())
def dump(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def evidence(p):return dict(path=str(p.resolve()),sha256=hashlib.sha256(p.read_bytes()).hexdigest())

def main():
    src=get(OUT/'sources.json');src.update(new_source_templates=1,previous_source_template_rereads=0);dump('sources.json',src)
    c=src['candidates'][0]
    comparisons=[evidence(BASE/'research-20261101-dungeons-019/F01-whole.png'),evidence(BASE/'research-20261101-dungeons-009/F04-whole.png')]
    obs=dict(
      layout='同一模板中四边墙身、四处角塔、南门段、内院及偏西/北的成组厅房闭合成整座小堡。成组厅房占据部分院内而非仅贴墙低棚；门段与厅房之间留有院内通道。只计整个堡院一例。',
      proportion='保存盒27×40×31，真实占用x0–26/y0–30/z0–30，含旗总高31；y23–26仅西北角收尖木顶，y27/28为单栅栏、y29单铁栏、y30单旗，均不当作房层。约30格平面的中型地面堡院组织与原范围相近；未隐去31格总高，也未将40格空保存盒当高楼。',
      facade='连续石墙/墙垛围院，南门楼段较低、角部竖向构件高低有别；西侧厅房层叠开口和短横向衔接段与墙边带共同形成内外层次，不是单塔轴线叠室。',
      roof='院内厅房多组小坡顶相交并有高低衔接，西北角单独收尖，另外角塔上部开敞；区别于019-F01开放大院配沿边浅棚和墙中高塔，也区别于009-F04三角塔配一条低长侧厅。',
      materials='原状态主材stone_bricks1469、dirt461、cobblestone391、stone_brick_stairs284、stone_brick_wall205、cracked_stone_bricks202及spruce_stairs175；分类色合并细部，不把绿化和屋顶换色当独立设计。',
      circulation='9处下半门：南门两列x12/14、两排z25/27均y1，厅门y4两处、y7/8/9各一处；角塔梯(22,4)y8–14。以门段—院—厅房—墙/角塔的相邻关系学习，不声称全程原生可走或所有楼层通达。',
      terrain='一体低地脚含院、墙与土底；4个向外道路接口和4个村民接口不增加建筑数量。作者地表beard_thin配置及村庄外路不等于地形验收；本地JAR缺原版村民池，保持未装配。')
    dedup=dict(exact_source_baseline=225,exact_matches=0,
      compared_whole_designs=['019-F01','009-F04'],
      observed_distinctions='新例是偏置成组厅房侵入院内、由门段/院带接合角塔与墙路；019为大空院和墙中单高塔，009-F04为三角塔与一条低侧长厅。比较的是厅房—院—门—塔的组织，不是石材、顶帽数量或旋转。',
      other_existing_family_context='010-F01破碎围院、010-F02中央叠台、010-F03高围栏中央低长房、010-F05窄高长厅加横低翼、020-F01宽长屋单端回接院、009-F01斜对高台均沿用既有记录比较，未冒称重新打开这些旧图。',
      heuristic_limit='Four-rotation occupancy Jaccard is only a shortlist aid, not proof of semantic novelty.')
    height=dict(stored_height=40,occupied_height_including_banner=31,occupied_y=[0,30],
      highest_non_singleton_level=25,singleton_levels=[26,27,28,29,30],
      scope_definition_unchanged=True,
      decision='原堡营范围写约17–30格保存高度，按整座约30格量级的房/院/塔关系接纳这一例布局观察；明确保留含旗31格原边界，不裁旗改写外盒，不据旗杆添加房层。此处不是修改单塔25–53格范围，也未解决015-F01/001-F05旧口径问题。')
    entry=dict(id='036-F01',source=c,scope_id='DUN03-MEDIUM-GROUND-GARRISON',
      decision='ACCEPTED_ONE_COMPLETE_SCOPED_LAYOUT_OBSERVATION',credit=1,credit_identity='036-F01',
      observations=obs,semantic_dedup=dedup,height_basis=height,
      actual_images_viewed=[evidence(OUT/n) for n in ('F01-whole.png','F01-details.png','F01-hall-tower.png')],
      actual_comparison_images_viewed=comparisons,whole_castle_envelope_observed=True,
      native_acceptance=False,independent_human_review=False,
      production_scope_limit='仅为古战场附属中型驻防堡院布局学习，不验收整个战场、国风造型、瓮城、机关、任务或指南针。')
    dump('manual-review.json',dict(batch=36,date='2026-11-03',new_source_templates=1,
      actual_new_images_viewed=3,actual_prior_comparison_images_viewed=2,actual_total_images_viewed=5,
      independent_references_added=1,credited_ids=['036-F01'],entries=[entry],
      generated_not_claimed_viewed=['F01-plan.png','F01-vertical.png'],
      independent_human_review_claimed=False,production_changes=0,checklist_deletions=0))
    prior_path=BASE/'research-20261102-dungeons-035/scoped-reference-update.json'
    prior=get(prior_path);scope=deepcopy(prior)
    scope.update(prior_update=evidence(prior_path),added_ids=['036-F01'],added_credit=1,
      new_source_discoveries=1,old_candidate_first_scope_acceptance=0,
      current_batch_holds=[],current_batch_exclusions=[],
      current_scope_observations=[dict(id='036-F01',scope_id=entry['scope_id'],credit=1,
        manual_review=evidence(OUT/'manual-review.json'),native_acceptance=False,independent_human_review=False)],
      limits='新增一座完整堡院布局观察，计数9/10/1；含旗31格和保存盒40格口径显式保留。1000门槛未到，旧高度/族/冰塔问题及全部旧排除不变，其他用途不转移信用。')
    scope['scopes'][0]['accepted_ids'].append('036-F01')
    scope['scopes'][0].update(accepted_references=9,remaining=991,construction_allowed=False)
    dump('scoped-reference-update.json',scope)
    boundary=get(OUT/'discovery-boundary.json')
    boundary.update(new_source_templates=1,actual_new_images_viewed=3,actual_prior_comparison_images_viewed=2,
      historical_distinct_archive_member_pairs=225,scoped_layout_observations_added=1,
      scope_definitions_changed=False,production_changes=0,checklist_deletions=0,
      sound_brightness_window_save_changes=0,prior_033_035_images_reopened=0,
      sampling_limit='Only one formerly unviewed source. Three views plus two historical comparison views are not five buildings; no fixed-local-corpus exhaustion claim.')
    dump('discovery-boundary.json',boundary)
    dump('session.json',dict(owner='做建筑的',date='2026-11-03',batch=36,
      status='ONE_NEW_COMPLETE_LAYOUT_OBSERVATION_RECORDED_PENDING_INTEGRITY_VERIFICATION',
      previous_receipt=evidence(BASE/'research-20261102-dungeons-035/RECEIPT.json'),
      current_scope=evidence(OUT/'scoped-reference-update.json'),active_checkpoint_path=str(OUT/'active-checkpoint.json'),
      counts=[9,10,1],remaining=[991,990,999],production_allowed=False,
      coordinator_only_main_checklist=True,shared_coordinator_session_not_overwritten=True,
      next='核对本批源字节、选层、边界、去重与旧收据；再从尚未实看的本地相关完整来源继续。',
      java_run=False,game_run=False,network_requests=0,no_automation=True,duration_hours_claimed=0))

if __name__=='__main__':main()
