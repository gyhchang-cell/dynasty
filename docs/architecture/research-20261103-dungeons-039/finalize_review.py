"""Finish the residential mansion review without guard-reference credit."""
import hashlib
import importlib.util
import json
from pathlib import Path
from zipfile import ZipFile

OUT=Path(__file__).resolve().parent
BASE=OUT.parent
def get(p):return json.loads(p.read_text())
def dump(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def sha(b):return hashlib.sha256(b).hexdigest()
def evidence(p):return dict(path=str(p.resolve()),sha256=sha(p.read_bytes()))
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def main():
    f=module('fields038',BASE/'research-20261103-dungeons-038/finalize_review.py')
    src=get(OUT/'sources.json');c=src['candidates'][0]
    target='simply_houses:plains_mansion/plains_mansion'
    relations=[];direct=[];resources=[]
    with ZipFile(c['source_archive']) as z:
        for r in c['pool_references']:
            raw=z.read(r['member']);hits=list(f.fields(r['data'],target))
            selects=any(p.endswith('.location') for p in hits)
            relations.append(dict(member=r['member'],sha256=sha(raw),matching_fields=hits,directly_selects_template=selects))
            if selects:direct.append(r)
        for n in ['data/simply_houses/worldgen/structure/plains_mansion.json',
                  'data/simply_houses/tags/worldgen/biome/has_structure/plains_mansion_biomes.json']:
            raw=z.read(n);resources.append(dict(member=n,sha256=sha(raw),data=json.loads(raw)))
        manifest=z.read('META-INF/mods.toml')
    c['pool_references']=direct
    c['pool_reference_semantics']='Exact location selection, not any identifier mention.'
    src.update(new_source_templates=1,previous_source_template_rereads=0);dump('sources.json',src)
    dump('selection-role-audit.json',dict(target=target,relations=relations,
        direct_location_selection_pools=len(direct),author_resources=resources,
        manifest_sha256=sha(manifest),manifest_text=manifest.decode(),
        assembly_performed=False,native_terrain_verified=False))
    observations=dict(
        layout='石质低层承托连续多室住宅，上层木框多房间及转折通道共同占据主体；屋面之间的内凹开口未证明为防护院落。没有发现院带、驻所与独立高低守望空间的组织，不能用大宅名称替代用途证据。',
        proportion='保存33×30×32，实占x0–32/y0–28/z0–31，实际高29格；与堡营外盒接近，却不因此成为堡营。也不符合窄占地单塔或24–29×15–17的偏置守望长厅。',
        facade='低层厚石墙，上层木柱与连续窗、栏杆、阳台带；立面层次围绕住宅房间展开，没有独立门楼塔和院墙。借鉴时应让楼层和门窗对齐，不能把多段山墙当作多座建筑。',
        roof='数段陡双坡屋顶交接并错开屋脊高度，覆盖住宅多室组合；高屋脊不是驻守楼层，内凹屋面空隙也不是已证实开放堡院。可研究不同跨度屋面交接的收口，不能复制原建筑。',
        materials='stone1378、stripped_birch_log821、stone_bricks774、pink_terracotta772、stripped_oak_log664、spruce_planks515等原状态；石基与木框按楼层分层。分类色图仅便于读结构，不能证明原生材质外观或碰撞。',
        circulation='22处下半门分布于y2/10/16/17；短梯仅在(28,9)y8–10。y10切面呈多个房间与通道，竖剖显示低层、主层及屋顶下层关系；未实测逐门、楼梯连续可走。8盔甲架、8画、5展示框是装饰实体，不能当驻军或21个建筑。',
        terrain='作者单一start_pool直接location选择大宅本体，原模板无jigsaw；WORLD_SURFACE_WG与beard_thin是放置配置，非当前任务实机承托验收。底层石基及临边入口可作坡地衔接观察，未证明随机地形下可通行。')
    entry=dict(id='039-F01',source_evidence=evidence(OUT/'sources.json'),source_candidate_id='F01',
        observations=observations,credit=0,credit_identity=None,
        decision='EXCLUDED_RESIDENTIAL_LAYOUT_FROM_CURRENT_GUARD_SCOPES',
        reason='完整住宅主体不等于相关守备设计；缺少围合驻防院带及独立守望组织。另不符合既定40–50格公共客栈的规模与公共功能，原DUN05计数不变。',
        template_body_confirmed=True,complete_native_placement_confirmed=False,
        native_acceptance=False,independent_human_review=False,
        actual_images_viewed=[evidence(OUT/'F01-whole.png'),evidence(OUT/'F01-details.png')])
    dump('manual-review.json',dict(batch=39,date='2026-11-03',new_source_templates=1,
        actual_images_viewed=2,independent_references_added=0,entries=[entry],
        generated_not_claimed_viewed=['F01-plan.png','F01-vertical.png'],
        independent_human_review_claimed=False,native_routes_verified=False,
        production_changes=0,checklist_deletions=0))
    prior_path=BASE/'research-20261103-dungeons-038/scoped-reference-update.json'
    scope=get(prior_path)
    scope.update(prior_update=evidence(prior_path),added_ids=[],added_credit=0,new_source_discoveries=1,
        prior_038_exclusions_retained=scope['current_batch_exclusions'],
        current_batch_exclusions=[dict(id=entry['id'],decision=entry['decision'],reason=entry['reason'],credit=0)],
        limits='39批实看完整草原大宅1份，住宅布局不适用当前三守备范围，新增信用0；保留全部旧观察、排除与待查，本地9/10/1待协调核收。')
    dump('scoped-reference-update.json',scope)
    boundary=get(OUT/'discovery-boundary.json')
    boundary.update(new_source_templates=1,actual_images_viewed=2,new_valid_scoped_references=0,
        historical_distinct_archive_member_pairs=227,scope_definitions_changed=False,
        production_changes=0,checklist_deletions=0,sound_brightness_window_save_changes=0)
    dump('discovery-boundary.json',boundary)
    dump('session.json',dict(date='2026-11-03',owner='做建筑的',batch=39,
        status='RESIDENTIAL_SCOPE_REVIEW_PENDING_INTEGRITY_VERIFICATION',
        previous_receipt=evidence(BASE/'research-20261103-dungeons-038/RECEIPT.json'),
        counts=[9,10,1],remaining=[991,990,999],production_allowed=False,
        shared_coordinator_session_not_overwritten=True,coordinator_only_main_checklist=True,
        next='换另一现有本地来源，先确认完整建筑、守备用途和边界；同设计组件与住宅不补当前三守备范围。',
        java_run=False,game_run=False,network_requests=0,no_automation=True,duration_hours_claimed=0))

if __name__=='__main__':main()
