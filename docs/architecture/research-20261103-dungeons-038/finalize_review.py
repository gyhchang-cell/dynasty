"""Separate actual template selection from shared processor identifiers."""
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

OUT=Path(__file__).resolve().parent
BASE=OUT.parent
def get(p):return json.loads(p.read_text())
def dump(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def sha(b):return hashlib.sha256(b).hexdigest()
def evidence(p):return dict(path=str(p.resolve()),sha256=sha(p.read_bytes()))
def fields(value,target,path='$'):
    if isinstance(value,dict):
        for k,v in value.items():yield from fields(v,target,path+'.'+k)
    elif isinstance(value,list):
        for i,v in enumerate(value):yield from fields(v,target,path+f'[{i}]')
    elif value==target:yield path

def main():
    src=get(OUT/'sources.json');c=src['candidates'][0];target='friendsandfoes:citadel/citadel'
    relations=[];direct=[];resources=[]
    with ZipFile(c['source_archive']) as z:
        for r in c['pool_references']:
            raw=z.read(r['member']);hits=list(fields(r['data'],target))
            selects=any(p.endswith('.location') for p in hits)
            relations.append(dict(member=r['member'],sha256=sha(raw),matching_fields=hits,
                directly_selects_template=selects,shared_processor_only=not selects))
            if selects:direct.append(r)
        for n in ['data/friendsandfoes/worldgen/structure/citadel.json',
            'data/friendsandfoes/worldgen/processor_list/citadel/citadel.json',
            'data/friendsandfoes/tags/worldgen/biome/has_structure/citadel.json']:
            raw=z.read(n);resources.append(dict(member=n,sha256=sha(raw),data=json.loads(raw)))
        manifest=z.read('META-INF/mods.toml')
    c['pool_references']=direct
    c['pool_reference_semantics']='Only exact location fields select this template; all other exact-value mentions remain in raw-source-audit.json and selection-role-audit.json.'
    src.update(new_source_templates=1,previous_source_template_rereads=0);dump('sources.json',src)
    dump('selection-role-audit.json',dict(target=target,relations=relations,
        exact_value_mentions=len(relations),direct_location_selection_pools=len(direct),
        processor_only_mentions=sum(r['shared_processor_only'] for r in relations),
        author_resources=resources,manifest_sha256=sha(manifest),manifest_text=manifest.decode(),
        prior_research_packages_rewritten=False,building_credit_added=0,
        custom_bottom_processor_executed=False,
        custom_processor_limit='Configuration names yellow_concrete target and nether_bricks output, but custom processor source/conditions not executed or certified; raw template is not native terrain acceptance.'))
    observations=dict(
      layout='31格方形包围盒中近圆形厚壁主体，多层大室、中央空间及四向桥接口；未见当前堡营的独立院带、厅房与高低守望组合。只看一份中心主体，不把外桥/平台/链条计作建筑。',
      proportion='保存31×33×31，实占y0–32。此例全宽31而非原单塔15–27格小占地；不能因名称citadel就忽略体量或改用堡营计数。',
      facade='下部连续厚墙和竖肋，上部环绕重复水平出挑带与开口；四面高度相近，以中央腔室为主，区别于偏置高塔接厅或四角院堡。',
      roof='上部层层环带收拢成宽盖，中央上层原有熔岩层；不是开放院心配屋厅和守望段。',
      materials='nether_bricks4178、nether_brick_slab1506、red_nether_brick_slab1302、nether_brick_stairs1027及yellow_concrete825等。黄混凝土是原模板状态且参与自定义底部处理器，不能当成最终黄色饰面；分类色图不是原生材质验收。',
      circulation='普通门0、普通梯0。4个桥接口在边界y10，中央wildfire实体接口y8、8个凋灵骷髅接口y1；原熔岩柱/层需保留。桥、角色和链条均未装配，不能认证桥到室内或全程楼层路线。',
      terrain='作者自定义citadel_structure、Nether标签、start_height34–54且terrain_adaptation none；尚未证明在当前地面驻防目标中的承托和通达。12个链条接口不是12条已生成链，更不是12座建筑。')
    entry=dict(id='038-F01',source=c,observations=observations,credit=0,credit_identity=None,
        decision='EXCLUDED_CURRENT_THREE_GROUND_GUARD_SCOPES_AUTHOR_COMPLEX_BOUNDARY_UNVERIFIED',
        reason='宽圆叠室、四向外桥和中心实体岗位不符合现有房院塔堡营、窄占地单塔或长厅偏置守望定义。完整作者桥/平台/链的边界亦未装配验收，保留原接口角色，不靠改名或多接口凑数。',
        complete_author_complex_boundary_confirmed=False,native_acceptance=False,independent_human_review=False,
        actual_images_viewed=[evidence(OUT/'F01-whole.png'),evidence(OUT/'F01-details.png')])
    dump('manual-review.json',dict(batch=38,date='2026-11-03',new_source_templates=1,
        actual_images_viewed=2,independent_references_added=0,entries=[entry],
        generated_not_claimed_viewed=['F01-plan.png','F01-vertical.png'],
        exact_pool_field_role_correction=True,independent_human_review_claimed=False,
        native_routes_verified=False,production_changes=0,checklist_deletions=0))
    prior_path=BASE/'research-20261103-dungeons-037/scoped-reference-update.json'
    scope=get(prior_path)
    scope.update(prior_update=evidence(prior_path),added_ids=[],added_credit=0,new_source_discoveries=1,
        current_batch_exclusions=[dict(id=entry['id'],decision=entry['decision'],reason=entry['reason'],credit=0)],
        prior_keep_boundary_holds_retained=scope.pop('current_batch_boundary_holds'),
        current_batch_boundary_holds=[],
        limits='38批新增实看中心城塞模板1份但当前三范围均0信用；本地计数保持9/10/1。保留36批观察、37批井桥侧部塔梯边界和所有旧待查，不将处理器引用冒充直接选本体。')
    dump('scoped-reference-update.json',scope)
    boundary=get(OUT/'discovery-boundary.json')
    boundary.update(new_source_templates=1,actual_images_viewed=2,new_valid_scoped_references=0,
        historical_distinct_archive_member_pairs=226,scope_definitions_changed=False,
        production_changes=0,checklist_deletions=0,sound_brightness_window_save_changes=0,
        reference_unit_limit='One centre template, two images,25 interfaces,11 exact-value mentions and one direct selection pool are not complete-building credit.')
    dump('discovery-boundary.json',boundary)
    dump('session.json',dict(date='2026-11-03',owner='做建筑的',batch=38,
        status='CITADEL_SCOPE_AND_POOL_ROLE_REVIEW_PENDING_INTEGRITY_VERIFICATION',
        previous_receipt=evidence(BASE/'research-20261103-dungeons-037/RECEIPT.json'),
        counts=[9,10,1],remaining=[991,990,999],production_allowed=False,
        shared_coordinator_session_not_overwritten=True,coordinator_only_main_checklist=True,
        next='从实际落盘断点继续完整相关本地建筑；优先完整边界和真实用途，避免重复本批圆形中心室或把共享处理器误当本体选择。',
        java_run=False,game_run=False,network_requests=0,no_automation=True,duration_hours_claimed=0))

if __name__=='__main__':main()
