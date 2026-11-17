"""Read existing COD4 evidence; write only this task's dated JSON/HTML report.

No exporter main, Java, game, world, quest, prompt, budget-policy or asset writes.
Source-declared faces are checked against saved native counts, not called a new bake.
"""
from pathlib import Path
import hashlib
import html
import json
import re
import sys
import zipfile
from datetime import datetime
from zoneinfo import ZoneInfo

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'docs/art/bestiary-v43/cod4-budget-readonly-20261030'
LOAD = 'docs/cod4/audit-20261022/mob-load-acceptance/'
NET = 'docs/cod4/audit-20261022/mob-network-acceptance/'
ASSET = 'src/main/resources/assets/dynasty/'
sys.path.insert(0, str(ROOT / 'tools/art'))
from quest_snbt import list_compounds, object_id
from PIL import Image

inputs = {}


def read(path):
    data = (ROOT / path).read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if path in inputs:
        assert inputs[path] == digest, ('concurrent change', path)
    inputs[path] = digest
    return data


def document(path):
    return json.loads(read(path))


def covered_candidates(bones):
    """Conservative same-bone axis-aligned solid-contact candidates, NOT edits.

    Whole face must lie against/inside one other solid cuboid with volume on its
    outward side. Different bones, cube rotations and inflation are excluded.
    Requires opaque PNG; native visual/export validation still needed before use.
    """
    result = []
    faces = {'north': (2, -1), 'south': (2, 1), 'east': (0, 1),
             'west': (0, -1), 'up': (1, 1), 'down': (1, -1)}
    for bone in bones:
        cubes = bone.get('cubes', [])
        for i, cube in enumerate(cubes):
            if cube.get('rotation') or cube.get('inflate', 0):
                continue
            low = cube['origin']; high = [a+b for a,b in zip(low,cube['size'])]
            for face, (axis, sign) in faces.items():
                if isinstance(cube['uv'], dict) and face not in cube['uv']:
                    continue
                plane = high[axis] if sign > 0 else low[axis]
                for j, other in enumerate(cubes):
                    if i == j or other.get('rotation') or other.get('inflate', 0):
                        continue
                    lo = other['origin']; hi = [a+b for a,b in zip(lo,other['size'])]
                    inward = lo[axis] <= plane < hi[axis] if sign > 0 else lo[axis] < plane <= hi[axis]
                    if inward and all(lo[k] <= low[k] and high[k] <= hi[k] for k in range(3) if k != axis):
                        result.append({'bone': bone['name'], 'cube': i, 'face': face, 'occluder': j})
                        break
    return result


def quest_nodes():
    nodes = []
    for path in sorted((ROOT / 'modpack/config/ftbquests/quests/chapters').glob('*.snbt')):
        rel = str(path.relative_to(ROOT)); raw = read(rel).decode()
        for block in list_compounds(raw, 'quests'):
            inner = '\n'.join(line[2:] if line.startswith('\t\t') else line for line in block.splitlines())
            title = re.search(r'^\ttitle:\s*"([^"]*)"', inner, re.M)
            nodes.append({'id': object_id(block), 'title': title[1] if title else '',
                          'path': rel, 'line': raw.count('\n',0,raw.index(block))+1,
                          'tasks': list_compounds(inner, 'tasks'), 'raw': block})
    return nodes


def main():
    frozen = document(LOAD+'frozen-source-sha256.json')
    native = document(LOAD+'run-03/native-geometry.json')['secondary']
    core = document(LOAD+'run-03/native-cod1-geometry.json')
    policy = document(LOAD+'class-budget-policy.json')
    earlier = document(LOAD+'class-budget-review.json')
    net = document(NET+'report.json'); fullpack = document(NET+'fullpack-report.json')
    nodes = quest_nodes()
    binding = read('src/main/java/com/dynasty/expansion/ExpansionClient.java').decode()
    steve = read('src/main/java/com/dynasty/client/steve/SteveFighterBindings.java').decode()
    ids = re.findall(r'"([a-z_]+)"', re.search(r'IDS=\{(.*?)\}',steve,re.S)[1])
    candidates = policy['groups']['light_human_biped']['candidates']
    rows = []
    for name in candidates:
        old = core[name]; rel = 'src/main/resources/assets/dynasty/'+old['resource'].split(':',1)[1]
        parts = document(rel)['parts']
        assert len(parts) == old['cuboids'] and len(parts)*6 == old['quads']
        rows.append({'id': name, **old, 'current_matches_native_snapshot': inputs[rel] == frozen.get(rel)})

    models = []
    for name in ['swindler','herb_picker','famished_refugee','snail_maiden','locust_swarm']:
        paths = {'geo': ASSET+f'geo/secondary/{name}.geo.json',
                 'animation': ASSET+f'animations/secondary/{name}.animation.json',
                 'texture': ASSET+f'textures/entity/secondary/{name}.png'}
        geo = document(paths['geo'])['minecraft:geometry'][0]
        clips = document(paths['animation'])['animations']; read(paths['texture'])
        image = Image.open(ROOT/paths['texture'])
        bones = geo['bones']; cubes = [c for b in bones for c in b.get('cubes',[])]
        count = sum(len(c['uv']) if isinstance(c['uv'],dict) else 6 for c in cubes)
        assert len(cubes) == native[name]['cuboids'] and count == native[name]['quads']
        previous = next(x for x in earlier['eleven'] if x['id'] == name)
        item = {'id': name, 'paths': paths, 'source_bones': len(bones), 'source_cuboids': len(cubes),
                'source_declared_quads': count, 'saved_native': native[name],
                'current_matches_frozen': {k: inputs[v] == frozen.get(v) for k,v in paths.items()},
                'atlas': list(image.size), 'animation_clips': len(clips),
                'budget_result': previous['conditional_result'],
                'all_candidates': previous['candidates'],
                'satisfying_count': previous.get('satisfying_count',0),
                'bone_cuboid_counts': {b['name']:len(b.get('cubes',[])) for b in bones},
                'new_native_bake_run': False}
        if name in ('swindler','herb_picker'):
            assert name not in ids and name in binding
            tool = 'abacus' if name == 'swindler' else 'sickle'
            by = {b['name']:b for b in bones}
            identity_bones = ['robe','crown','left_cuff','right_cuff','abacus'] if name == 'swindler' else ['hat','basket','straps','sickle']
            accessory_count = sum(len(by[b].get('cubes',[])) for b in identity_bones)
            item['authoring_basis'] = {
                'requested_identity_source':'docs/cod4/request.txt:33' if name == 'swindler' else 'docs/cod4/request.txt:34',
                'identity':'长衫算盘；假装受伤骗钱、被识破逃跑' if name == 'swindler' else '背篓；中立、不主动攻击、交换药草',
                'authoritative_source':'tools/art/secondary-cuboid/build_humans.py + human_atlas.py',
                'current_render_pipeline':'ExpansionClient Geo renderer, not SteveFighterRenderer override',
                'current_anatomical_cuboids':len(cubes)-accessory_count,
                'current_identity_accessory_cuboids':accessory_count,
                'anatomical_quads':6*(len(cubes)-accessory_count),
                'identity_accessory_quads':6*accessory_count,
                'exact_neutral_trader_profession_baseline':None,
                'no_heavy_armor_or_flag_carrier_baseline_substitution':True}
            assert by[tool]['parent'] == 'right_hand'
            assert not any(tool in c['bones'] or 'right_hand' in c['bones'] for c in clips.values())
            item['prop'] = {'bone':tool,'parent':'right_hand','real_item_id':None,
                            'reason':'Embedded body cuboids; not an ItemStack or player hand item',
                            'independent_animation_channels':False}
            assert image.convert('RGBA').getextrema()[3] == (255,255)
            hidden = covered_candidates(bones)
            item['preserve_appearance_options'] = {
                'same_bone_solid_contact_candidates':hidden,
                'candidate_quads_remaining':count-len(hidden),
                'candidate_only_not_exported_or_visually_verified':True,
                'meets_156_even_if_all_candidates_work':count-len(hidden)<=156,
                'minimum_reduction_to_156':count-156,
                'minimum_reduction_to_all_six_108':count-108,
                'do_not_remove_identity_prop_or_basket_to_force_pass':True,
                'do_not_merge_independently_animated_elbows_knees_or_basket':True}
            item['loot'] = document(f'src/main/resources/data/dynasty/loot_tables/entities/{name}.json')
            species = next(s for s in net['species'] if s['id'] == name)
            item['historical_network'] = {'reported_status':species['status'], 'production_jar_sha256':net['artifact_sha256'],
                 'stages':[{'path':f, **{k:document(f).get(k) for k in ('name','pass','checks')}} for f in species['evidence']],
                 'raw_failed_stages_retained':True,'qa_adjudications':net['qa_superseded']}
            item['direct_entity_quest_nodes'] = [{k:v for k,v in q.items() if k!='raw'} for q in nodes
                   if any(f'dynasty:{name}' in t for t in q['tasks'])]
        models.append(item)

    # Read production inputs and identity requirements. No arbitrary new budget.
    for rel in ['docs/cod4/request.txt','src/main/java/com/dynasty/expansion/SecondaryMob.java',
                'src/main/java/com/dynasty/expansion/SecondaryMobs.java',
                'src/main/java/com/dynasty/DynastyItems.java','src/main/java/com/dynasty/workshop/WorkshopRecipes.java',
                'src/main/java/com/dynasty/expansion/Cod4ContinuationGameTests.java',
                'src/main/java/com/dynasty/expansion/ExpansionGameTests.java',
                'src/main/java/com/dynasty/client/OriginalItemGeometry.java',
                'tools/cod4/generate_assets.py','tools/art/secondary-cuboid/build_humans.py',
                'tools/art/secondary-cuboid/human_atlas.py','tools/art/secondary-cuboid/check_humans.py',
                'docs/art/secondary-humans-v3/validation.json',NET+'qa-adjudications.json']:
        read(rel)

    # Generate in memory only. Never call either generator's main or Rig.save.
    sys.path.insert(0,str(ROOT/'tools/art/secondary-cuboid'))
    from human_atlas import generated
    authored = generated()
    for m in models[:2]:
        g,png,_ = authored[m['id']]
        m['current_authoritative_export_matches'] = {
            'geo_semantic':g == document(m['paths']['geo']), 'png_byte_exact':png == read(m['paths']['texture'])}

    item_links = []
    for item_id, role in [('dynasty:copper_coin','shared payment / ordinary loot'),
                          ('minecraft:dead_bush','swindler false medicine with cod4Swindler entity UUID'),
                          ('minecraft:clay_ball','fake_jade loot alias; NOT false medicine'),
                          ('dynasty:tea','herb trade gives 2 ordinary tea; wild_herb loot alias uses same real ID')]:
        # An advancement's icon is not an item objective or an NPC-trade trigger.
        links = [{k:v for k,v in q.items() if k!='raw'} for q in nodes
                 if any(re.search(r'\btype:\s*"item"', t)
                        and re.search(r'\bitem:\s*\{\s*id:\s*"'+re.escape(item_id)+'"', t)
                        for t in q['tasks'])]
        model_path = ASSET+'models/item/'+item_id.split(':')[1]+'.json' if item_id.startswith('dynasty:') else None
        data = document(model_path) if model_path else None
        if data: read('src/main/resources/'+data['original_texture'].replace('dynasty:', 'assets/dynasty/'))
        item_links.append({'real_item_id':item_id,'role':role,'existing_item_task_nodes':links,
                           'custom_item_model':model_path,'display':data.get('display') if data else None,
                           'player_first_third_person_visual_validation':'Not established by transforms or NPC geometry alone'})
    related = [{k:v for k,v in q.items() if k!='raw'} for q in nodes if any('dynasty:cod4_herb_spot' in t for t in q['tasks'])]

    jarpath = 'modpack/mods/dynasty-1.4.0.jar'; read(jarpath)
    with zipfile.ZipFile(ROOT/jarpath) as jar:
        jar_assets = {p: jar.read(p.removeprefix('src/main/resources/')) == read(p)
                      for m in models[:2] for p in m['paths'].values()}
    protected = {}
    for name in ('marshal','taoyan'):
        for p,old_sha in document(f'docs/art/bestiary-v43/{name}/protected-before.json').items():
            read(p); protected[p] = {'current_sha256':inputs[p],'matches_before':inputs[p]==old_sha}
    # Also freeze the four approved body forms, which aren't the above shared-effect files.
    for form in ('gongsun_wuwang','gongsun_wuwang_foot','taoyan_zhishi','taoyan_zhishi_phase2'):
        for folder,suffix in [('geo/blueprint/boss','.geo.json'),('animations/blueprint/boss','.animation.json'),
                              ('textures/entity/blueprint/boss','_body.png')]:
            read(ASSET+folder+'/'+form+suffix)
    read('tools/art/bestiary-v43/audit_cod4_readonly.py')
    unchanged = {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==sha for p,sha in inputs.items()}
    assert all(unchanged.values()), 'Concurrent input changes; do not publish stale audit'
    report = {'status':'READ_ONLY_EVIDENCE_COMPLETE_BUDGET_CONFLICT_REMAINS',
        'timestamp':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),
        'runtime_assets_or_source_modified':False,'game_or_Java_started':False,'new_entities':0,
        'basis':'Frozen run-03 native bake plus current source count/hash equivalence; not a new native bake',
        'native_render_binding_unchanged':{p:inputs[p]==frozen.get(p) for p in inputs if p.endswith(('ExpansionClient.java','SteveFighterBindings.java'))},
        'light_human_candidates':rows,'models':models,'asset_item_quest_links':item_links,
        'herb_spot_nodes_related_item_not_npc_trade':related,
        'current_jar':{'path':jarpath,'sha256':inputs[jarpath],
            'matches_saved_fullpack_acceptance_jar':inputs[jarpath]==fullpack['artifact']['patched_sha256'],
            'target_asset_byte_equivalence':jar_assets},
        'source_network_scope':{'current_SecondaryMob_matches_fullpack_source':inputs['src/main/java/com/dynasty/expansion/SecondaryMob.java']==fullpack['artifact']['formal_guard_source_sha256']['src/main/java/com/dynasty/expansion/SecondaryMob.java'],
             'specific_swindler_and_herb_cases_use_older_jar':True,
             'older_case_evidence_is_not_erased_or_relabelled_uncovered':True,
             'fullpack_representatives_do_not_retest_all_swindler_herb_cases':True},
        'remaining_acceptance':['Budget disposition: preserve appearance; no forced high-budget substitution or automatic decimation.',
             'Native visual/full-animation review required before applying any hidden-face candidates.',
             'Player-held real item first/third-person framing not proven by embedded NPC props or transform JSON.',
             'Specific older-jar ownership passes retained; exact-current-JAR rerun of those cases not performed here.',
             'Herb-spot advancement is not proof of NPC trade; no new quest node or fabricated counterfeit registry.'],
        'protected_shared_assets':protected,'input_sha256':inputs,'all_inputs_unchanged_during_audit':all(unchanged.values()),
        'prompt_or_TODO_cleanup':False,'reproduce':'PYTHONDONTWRITEBYTECODE=1 python3 tools/art/bestiary-v43/audit_cod4_readonly.py'}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    esc = html.escape
    table = ''.join(f'<tr><td>{esc(m["id"])}</td><td>{m["source_cuboids"]}/{m["source_declared_quads"]}</td><td>{esc(m["budget_result"])}</td></tr>' for m in models)
    detail = ''.join(f'<h2>{esc(m["id"])}</h2><p>同骨骼封闭接触候选 {len(m["preserve_appearance_options"]["same_bone_solid_contact_candidates"])} 面；即使全部验证成立，仍余 {m["preserve_appearance_options"]["candidate_quads_remaining"]} 面。这里只读记录，未执行删面。</p>' for m in models[:2])
    page = '<!doctype html><html lang="zh"><meta charset="utf-8"><title>COD4 模型与关联复核</title><style>body{max-width:1000px;margin:42px auto;padding:0 24px;background:#152129;color:#e9e5d9;font:16px/1.7 system-ui}table{border-collapse:collapse;width:100%}td,th{padding:10px;border-bottom:1px solid #495a61;text-align:left}a{color:#9dded6}h1,h2{line-height:1.3}</style><h1>COD4 只读复核 · 2026-10-30</h1><p>没有改模型、贴图、技能、任务或提示词，没有启动 Java / 游戏。已认可的两 Boss 四形态保留。</p><table><tr><th>现有实体</th><th>Cuboid / quad</th><th>条件结论</th></tr>'+table+'</table><p>轻装候选完整范围108–156面；骗子与采药客均超出全部六项，饥民仅满足1/6。螺女、飞蝗群没有同型基准。以上不是新预算，也不是整项通过。</p>'+detail+'<h2>资产 → 物品 → 现有任务</h2><p>算盘 / 镰刀是本体几何，不是玩家物品。骗子交互假药 = 带实体UUID的枯萎灌木；赝玉掉落 = 黏土球。两者没有专用任务入口。铜钱只关联既有持有铜钱任务1000000000000012，不等同完成骗局。</p><p>采药客付一铜钱得二茶；药草掉落也是茶的命名别名。茶对应任务1000000000000020。药草点1000000000c40027是独立现场交互进度，不是采药客交易进度。</p><h2>已验证与待验证</h2><p>两只6份资源与冻结原生测量快照、当前整合包JAR逐字节一致；权威生成源在内存再导出也一致。面数和绑定来源可追溯，不假称本轮重新烘焙。</p><p>已有双客户端付费、证据归属、拒绝他人、冷却和返还记录保留，包含原始失败及纠正补测。当前JAR匹配整包验收包；但该整包代表样本并未重测这两只的全部交互。玩家物品一/三人称观感、任何删面后的原生画面仍须独立验证。</p><p><a href="report.json">完整结果、候选面、真实节点和SHA256</a> · <a href="../continuation-20261028.html">已完成两Boss四形态</a></p></html>'
    (OUT/'index.html').write_text(page)
    print(json.dumps({'status':report['status'],'report':str((OUT/'index.html').relative_to(ROOT)),
        'inputs':len(inputs),'protected_shared':len(protected),'protected_match':all(x['matches_before'] for x in protected.values()),
        'source_export_match':{m['id']:m['current_authoritative_export_matches'] for m in models[:2]},
        'hidden_face_candidates':{m['id']:len(m['preserve_appearance_options']['same_bone_solid_contact_candidates']) for m in models[:2]}},ensure_ascii=False))


if __name__ == '__main__':
    main()
