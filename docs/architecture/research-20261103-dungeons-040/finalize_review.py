"""Record the actual four visual readings and keep custom-complex boundary open."""
import hashlib
import json
from pathlib import Path

OUT=Path(__file__).resolve().parent
BASE=OUT.parent
def get(p):return json.loads(p.read_text())
def dump(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def evidence(p):return dict(path=str(p.resolve()),sha256=hashlib.sha256(p.read_bytes()).hexdigest())

def main():
    src=get(OUT/'sources.json');src.update(new_source_templates=2,previous_source_template_rereads=0)
    for c in src['candidates']:
        assert not c['pool_references']
        c['pool_reference_semantics']='No exact JSON selector in this archive; custom structure class strings are separate evidence, not placement proof.'
    dump('sources.json',src)
    tower=dict(
        layout='近圆形厚壁竖向主体，原始图内侧大量gel占位；诊断图仅隐藏蓝/黄gel及structure标记后，可观察圆室外壳与沿边台阶，未证明原生空室、逐层路线或驻军房间。没有偏置长厅或独立围合院带。',
        proportion='保存及原状态占据范围29×32×29，y0–31。宽径29超过既定小占地单塔15–27；不能只截掉外围装饰或把地脚排除后宣称满足当前范围。尚未核实作者完整组合外盒。',
        facade='竖肋、壁柱及分层横向出挑带组织圆形厚壁；四面主宽相近，未见低厅接高塔。相邻肋与上部女墙有节奏差别，不能把旋转视图计成不同实例。',
        roof='顶部宽圆平台与环边围护；隐藏gel图露出上层平台，不是尖屋顶或庭院环屋。boss元数据位于(14,30,14)，只是标记，不代表已生成Boss或已验收战斗平台。',
        materials='原模板blue_gel8724、yellow_gel1282，共10006格；locked_gale_stone3528、gale_stairs388、gale_slab368、gale_wall348、gale_pillar242等。gel语义未执行；不能把原始灰块图当最终实心石塔，亦不能把诊断隐藏图当原生结果。',
        circulation='普通门/梯0；隐藏gel后可见贴壁上升台阶段和圆形内室。3个loot_chest、1个platinum_chest与1个boss元数据待作者自定义处理，不能以标记替代原生生成或通路证明；没有认证连续可走。',
        terrain='作者platinum_dungeon为自定义surface_structures；同包另有47×23×47 ground模板，类字符串含tower/ground与StoneFillPiece。字符串仅支持相关模板存在，不证明旋转、相对偏移、石基填充或完整建筑边界。')
    ground=dict(
        layout='独立地脚模板，中心近圆平地，外圈不规则分级草坡；它是塔周地形候选，不含可独立计数的厅、院墙或守望空间。未与塔拼接。',
        proportion='47×23×47，明显大于塔29×32×29；高差来自下部厚石和外围分级地形，不是23格高建筑。不能将两文件分别算两例或凭尺寸猜测偏移。',
        facade='地脚侧边为不规则石壁和草土台阶，不能解释成建筑立面或防护院墙。',
        roof='无屋顶；中心地表与外圈坡地是地面关系，不把地形顶面当楼顶或独立建筑。',
        materials='holystone21546、aether_dirt3120、aether_grass_block1282、aether_dirt_path38与data_handler68。顶部散点中包含生成处理标记，不全部是成品景观石。',
        circulation='可观察一侧浅色路径接中心地表，但未运行地形/碰撞或塔门衔接。68个data_handler为配置特征处理接口，不是68个门、树或建筑。',
        terrain='分级土草覆在厚石上，以不规则外缘过渡；68个configured_feature处理器指向aether:crystal_tree（原概率保留），未生成树也未认证其对路径的遮挡。借鉴原则是先核实承托与入口相对高程，不能只放一块方形地基。')
    entries=[]
    for identity,obs,images in [('F01',tower,['F01-whole.png','F01-details.png','F01-gel-mask.png']),('F02',ground,['F02-whole.png'])]:
        entries.append(dict(id='040-'+identity,source_evidence=evidence(OUT/'sources.json'),source_candidate_id=identity,
            observations=obs,credit=0,credit_identity=None,
            decision='HOLD_CUSTOM_TOWER_GROUND_COMPOSITION_AND_CURRENT_SCOPE',
            reason='两份相关模板不是两座完整守备建筑；自定义组合、gel处理与完整边界尚未证明，塔本体也不符合现有三类布局。',
            complete_author_complex_boundary_confirmed=False,native_acceptance=False,independent_human_review=False,
            actual_images_viewed=[evidence(OUT/n) for n in images]))
    dump('manual-review.json',dict(batch=40,date='2026-11-03',new_source_templates=2,
        actual_images_viewed=4,independent_references_added=0,entries=entries,
        generated_not_claimed_viewed=['F01-plan.png','F01-vertical.png','F02-plan.png','F02-vertical.png','F02-details.png'],
        diagnostic_mask_is_not_native_output=True,java_run=False,production_changes=0,checklist_deletions=0))
    pp=BASE/'research-20261103-dungeons-039/scoped-reference-update.json';scope=get(pp)
    scope.update(prior_update=evidence(pp),added_ids=[],added_credit=0,new_source_discoveries=2,
        prior_039_exclusions_retained=scope['current_batch_exclusions'],current_batch_exclusions=[],
        current_batch_boundary_holds=[dict(id=e['id'],decision=e['decision'],reason=e['reason'],credit=0) for e in entries],
        limits='40批实看塔与地脚两模板、4张图，原生组合和gel处理未证，不计完整建筑；本地9/10/1待协调核收，未达1000不制作。')
    dump('scoped-reference-update.json',scope)
    boundary=get(OUT/'discovery-boundary.json')
    boundary.update(new_source_templates=2,actual_images_viewed=4,new_valid_scoped_references=0,
        historical_distinct_archive_member_pairs=228,scope_definitions_changed=False,
        production_changes=0,checklist_deletions=0,sound_brightness_window_save_changes=0,
        full_author_complex_assembled=False,gel_processing_verified=False)
    dump('discovery-boundary.json',boundary)
    dump('session.json',dict(date='2026-11-03',owner='做建筑的',batch=40,
        status='CUSTOM_TOWER_GROUND_REVIEW_PENDING_INTEGRITY_VERIFICATION',
        previous_receipt=evidence(BASE/'research-20261103-dungeons-039/RECEIPT.json'),
        counts=[9,10,1],remaining=[991,990,999],production_allowed=False,
        shared_coordinator_session_not_overwritten=True,coordinator_only_main_checklist=True,
        next='继续现有本地完整相关建筑；无准确组合证据不拼塔与地脚，不把gel占位或处理器当成房间、通路或多座建筑。',
        java_run=False,game_run=False,network_requests=0,no_automation=True,duration_hours_claimed=0))

if __name__=='__main__':main()
