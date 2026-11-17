"""Record actual views and preserve the prior scope ledger without new credit."""
import hashlib
import json
from pathlib import Path

OUT=Path(__file__).resolve().parent
BASE=OUT.parent

def get(p):
    return json.loads(p.read_text())

def dump(n,v):
    (OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')

def evidence(p):
    return dict(path=str(p.resolve()),sha256=hashlib.sha256(p.read_bytes()).hexdigest())

def main():
    src=get(OUT/'sources.json')
    src.update(new_source_templates=4,previous_source_template_rereads=0)
    dump('sources.json',src)
    layouts=[
      '两侧厚闭墙围住局部楼层，另两侧楼板与室内陈设在文件边界截断；高处小房位于其中一角，非独立塔完整平面。',
      '两侧厚闭墙与两侧开放截面，低处L形环绕栏线延伸到边缘；分层地牢空间而非完整驻守塔。',
      '角部闭墙与连续高低楼板，其余两侧暴露室内断面；低处L形栏线和上层开口均在模板边缘结束。',
      '两侧厚闭墙、两侧断面；顶部另有灰色局部构件与小洞，局部差异不能说明它是独立完整建筑。']
    entries=[]
    bounds=get(OUT/'raw-source-audit.json')['entries']
    details=get(OUT/'detail-evidence.json')['entries']
    for c,a,de,layout in zip(src['candidates'],bounds,details,layouts):
        obs=dict(layout=layout,
          proportion=f"保存盒{c['size']}，实占y{a['occupied_bounds'][1][0]}–{a['occupied_bounds'][1][1]}；这是单文件外盒，不当作完整建筑尺寸或制作门槛参考。",
          facade='闭墙有重复竖向壁柱、横带及厚重下座；另两侧是截断室内，不能当成面向庭院的完整开敞立面。',
          roof='上部为厚平顶盖及少量边带，未见可独立确认的塔顶守望平台；不可把开放断面重命名为塔楼外廊。',
          materials='侵蚀深板岩砖、深板岩砖/瓦、裂纹深板岩砖、发光地衣及楼梯为主；分类色不能显示真实贴图与碰撞。',
          circulation=f"普通下半门{len(c['doors'])}处；原梯段{de['ladder_runs']}。局部楼板、洞口和阶梯不证明独立入口或全程竖向可达。",
          terrain='作者结构type为eeeabsmobs:guling、step为underground_decoration，生物群系标签指forge:is_underground；不纳入当前地面堡营/独立塔/连厅。')
        entries.append(dict(id='034-'+c['id'],source=c,observations=obs,
          decision='EXCLUDED_CURRENT_GROUND_GUARD_SCOPES_UNDERGROUND_OPEN_BOUNDARY_TEMPLATE',
          reason='原作者地下配置与实际开放截面不支持完整地面守备建筑；四模板名同现生成类，仅作静态边界线索，不声称四座独立设计或已验证完整拼接。',
          credit=0,credit_identity=None,complete_building_identity_confirmed=False,
          native_acceptance=False,independent_human_review=False,
          actual_images_viewed=[evidence(OUT/f"{c['id']}-{s}.png") for s in ('whole','details')]))
    dump('manual-review.json',dict(batch=34,date='2026-11-02',new_source_templates=4,
      independent_references_added=0,previous_source_template_rereads=0,
      actual_unique_images_viewed=8,actual_whole_images_viewed=4,actual_section_images_viewed=4,
      generated_but_not_claimed_viewed='Four separate plan and four vertical PNGs were generated but not reopened; not counted as viewed.',
      independent_human_review_claimed=False,entries=entries,
      family_and_completeness='No four-building claim. Open cut faces and shared generation-class strings support a component concern. Class constants do not establish offsets, complete composition or native placement.',
      production_changes=0,checklist_deletions=0,native_routes_verified=False))
    prior_path=BASE/'research-20261102-dungeons-033/scoped-reference-update.json'
    prior=get(prior_path);scope=dict(prior)
    scope.update(prior_update=evidence(prior_path),added_ids=[],added_credit=0,
      new_source_discoveries=4,old_candidate_first_scope_acceptance=0,
      prior_review_exclusions_retained=prior['current_batch_exclusions'],
      current_batch_exclusions=[dict(id=e['id'],decision=e['decision'],reason=e['reason'],credit=0) for e in entries],
      limits='保持33批8/10/1及全部旧待查/排除；古陵4模板与8图均不增加完整相关建筑。未验证拼接偏移、完整边界、原生通行或制作验收。')
    dump('scoped-reference-update.json',scope)
    boundary=get(OUT/'discovery-boundary.json')
    boundary.update(new_source_templates=4,actual_images_viewed=8,
      historical_distinct_archive_member_pairs=221,new_distinct_archive_member_pairs=4,
      scoped_valid_references_added=0,scope_definitions_changed=False,production_changes=0,
      checklist_deletions=0,sound_brightness_window_save_changes=0,
      sampling_limit='Four local size hits only, not an exhausted queue or four complete related buildings. Python read static bytes; no Java process or class execution.')
    dump('discovery-boundary.json',boundary)

if __name__=='__main__':
    main()
