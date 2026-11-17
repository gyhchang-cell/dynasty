#!/usr/bin/env python3
"""Publish bounded route evidence, including failed attempts; never modify task lists."""
import argparse
import collections
import datetime
import hashlib
import json
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WORK = HERE / '.work/routes'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p): return str(p.relative_to(ROOT))
def read(p): return json.loads(p.read_text())
def dump(p,v): p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--run',required=True);args=parser.parse_args()
    run=WORK/args.run; native=read(run/'native-results.json'); receipt=read(run/'run-receipt.json')
    assert 'exit_code' in receipt, 'Publish completed native attempts only'
    assert sha(run/'JourneyRouteGameTests.java')==receipt['qa_sha256']
    assert sha(run/'routes.init.gradle')==receipt['init_sha256']
    assert sha(WORK/(args.run+'.log'))==receipt['log_sha256']
    assert sha(run/'source-hashes.json')==receipt['source_manifest_sha256']
    for name,digest in receipt['qa_inputs'].items(): assert sha(run/'qa-inputs'/name)==digest
    if all(r.get('pass') for r in native):
        assert receipt['exit_code']==0 and 'BUILD SUCCESSFUL' in (WORK/(args.run+'.log')).read_text()
    evidence=HERE/'evidence/routes'/args.run;evidence.mkdir(parents=True,exist_ok=True)
    for p in run.iterdir():
        if p.is_file() and p.suffix in ('.json','.java','.gradle'): shutil.copy2(p,evidence/p.name)
    shutil.copy2(WORK/(args.run+'.log'),evidence/'native.log')
    if not (evidence/'qa-inputs').exists():shutil.copytree(run/'qa-inputs',evidence/'qa-inputs')
    graph=read(run/'qa-inputs/route-quest-graph.json'); plan=read(HERE/'routes/plan.json')
    cases=[]; submitted=set(); recipes=set();qa_totals=collections.Counter()
    for row in native:
        steps=row['steps']; counts=collections.Counter(s['kind'] for s in steps)
        actual=[s for s in steps if s['kind']=='native_ftb_submit']
        paid=[s for s in steps if s['kind'] in ('native_craft','native_smith')]
        supplied=collections.Counter()
        for s in steps:
            if s['kind']=='qa_material':supplied[s['item']]+=s['count']
        submitted.update(s['quest'] for s in actual);recipes.update(s['recipe'] for s in paid);qa_totals.update(supplied)
        cases.append({'case':row['case'],'pass':row.get('pass',False),'failure':row.get('failure'),
            'food_scope':row.get('food_scope'),'food_measurements':row.get('food_measurements'),
            'counts':dict(counts),'elapsed_server_ticks':row.get('elapsed_server_ticks'),
            'native_quest_ids':[s['quest'] for s in actual], 'native_recipe_ids':[s['recipe'] for s in paid],
            'qa_materials':dict(sorted(supplied.items())),
            'qa_boundary_progress':[s for s in steps if s['kind']=='qa_boundary_progress'],
            'site_yields':[s for s in steps if s['kind']=='native_site_yield'],
            'final_inventory':row.get('final_inventory'),
            'evidence':rel(evidence/'native-results.json')+'#case='+row['case']})
    entries=[]
    for e in plan['entries']:
        entries.append({'quest':e['id'],'item':e['item'],'interaction':e['interaction'],
            'current_ancestors':e['ancestor_ids'],'native_ancestor_submissions':sorted(set(e['ancestor_ids'])&submitted),
            'remaining_ancestor_submissions':sorted(set(e['ancestor_ids'])-submitted),
            'connected_segment_submitted':e['id'] in submitted,
            'connected_cases':[r['case'] for r in cases if e['id'] in r['native_quest_ids']],
            'natural_acquisition_in_this_run':False})
    frozen=WORK/'frozen';source_links=[];recipe_index=read(HERE/'evidence/20261023/recipe-index.json')
    definitions=read(run/'qa-inputs/route-recipes.json')
    for item,total in sorted(qa_totals.items()):
        sources=[]
        for p in (frozen/'src/main/resources/data/dynasty/loot_tables').rglob('*.json'):
            if '"'+item+'"' in p.read_text():sources.append({'path':str(p.relative_to(frozen)),'sha256':sha(p),'kind':'STATIC_LOOT_ASSOCIATION'})
        producing=[]
        for rid,r in definitions.items():
            out=r.get('result');out=out.get('item') if isinstance(out,dict) else out
            if out==item:
                old=recipe_index[rid];p=frozen/old['path']
                producing.append({'recipe':rid,'native595_record':old['native_pass'],
                    'same_recipe_as_prior_native595':sha(p)==old['sha256'],
                    'acquisition_in_this_run':'QA supplied; this recipe was NOT necessarily used for this ingredient'})
        source_links.append({'item':item,'qa_units_across_independent_cases':total,'loot_sources':sources,
            'original_production_recipes':producing,'natural_acquisition':'NOT_EXECUTED',
            'scope':'仅现有来源关联；没有来源记录不等于游戏中无法获取，QA供应不能算已获得自然材料。'})
    manifest=read(run/'source-hashes.json')
    drift=[p for p,d in manifest.items() if not (ROOT/p).is_file() or sha(ROOT/p)!=d]
    quest_drift=[]
    for p,d in read(run/'quest-hashes.json').items():
        current=ROOT/'modpack'/p
        if not current.exists() or sha(current)!=d:quest_drift.append(str(current.relative_to(ROOT)))
    food=[r for r in cases if r['case'].startswith('food_')];routes=[r for r in cases if not r['case'].startswith('food_')]
    attempts=[]
    failure_notes={
        'routes-01':'QA init局部变量resources遮蔽sourceSet.resources，配置失败，未执行游戏；改为mainResources。',
        'routes-02':'3/6；测试函数把COD4任务ID前缀拼错，找不到节点。开局/终盘/守御已过。仅改QA引用。',
        'routes-03':'6/7；中期末尾测试误用dynasty:cod4/silk_pouch，原配方实际为dynasty:silk_pouch。前面银玉/胸甲/军粮记录已执行；仅改QA配方路径。',
        'routes-04':'14/15；QA把200tick气到期与每20玩家tick清理怒气视作同一时刻。拆成202tick气失效及222tick周期清理，未改正式周期。',
    }
    for directory in sorted(WORK.glob('routes-*')):
        if not directory.is_dir() or not (directory/'run-receipt.json').exists():continue
        rr=read(directory/'run-receipt.json')
        if 'exit_code' not in rr:continue
        dest=HERE/'evidence/routes'/directory.name;dest.mkdir(parents=True,exist_ok=True)
        for p in directory.iterdir():
            if p.is_file() and p.suffix in ('.json','.java','.gradle'):shutil.copy2(p,dest/p.name)
        shutil.copy2(WORK/(directory.name+'.log'),dest/'native.log')
        if (directory/'qa-inputs').exists() and not (dest/'qa-inputs').exists():shutil.copytree(directory/'qa-inputs',dest/'qa-inputs')
        attempts.append({'run':directory.name,'exit_code':rr['exit_code'],'evidence':rel(dest),
            'classification':failure_notes.get(directory.name,'See native results and actual runner exit code')})
    report={'status':'ALL_SELECTED_NATIVE_SEGMENTS_PASSED' if all(r.get('pass') for r in native) else 'PARTIAL_NATIVE_SEGMENTS_WITH_RECORDED_FAILURES',
        'updated_at':datetime.datetime.now().astimezone().isoformat(),'run':args.run,
        'cases_passed':sum(bool(r.get('pass')) for r in native),'cases_total':len(native),'cases':cases,
        'route_segments':{'passed':sum(r['pass'] for r in routes),'total':len(routes)},
        'food_segments':{'passed':sum(r['pass'] for r in food),'total':len(food)},'attempt_history':attempts,
        'requirement_sources':['docs/cod4/request.txt:385-390','docs/cod4/audit-20261022/cod4-before.txt:173-178'],
        'six_stage_plan':plan['six_stages'],'graph_denominator':len(graph),'cod4_entries_denominator':46,
        'cod4_connected_nodes_submitted':sum(e['connected_segment_submitted'] for e in entries),
        'cod4_connected_coverage':{
            'obtain_craft':{'submitted':sum(e['connected_segment_submitted'] for e in entries if not e['interaction']),'total':31},
            'interaction':{'submitted':sum(e['connected_segment_submitted'] for e in entries if e['interaction']),'total':15},
            'ancestor_union':{'submitted':len(set().union(*(set(e['native_ancestor_submissions']) for e in entries))),
                'total':len(set().union(*(set(e['current_ancestors']) for e in entries)))},
            'unconnected_entries':[e['item'] for e in entries if not e['connected_segment_submitted']]},
        'native_unique_quests_submitted':len(submitted),'native_unique_recipes_paid':len(recipes),
        'entries':entries,'qa_material_source_associations':source_links,
        'real_natural_acquisition_count':0,'production_changes':[],
        'input_evidence':rel(evidence),'source_drift_since_freeze':drift,'quest_drift_since_run':quest_drift,
        'findings':plan['findings']+[
            {'entry':'opening_weapon_prefix','observation':'原木矛任务的完成前置已要求铁镐/水桶；本轮native_ftb_submit背包确有铁镐/水桶。脚本即刻付料能依次换石戈/铜刀/铁剑，但不据此断言真人过快淘汰或擅改门槛。',
             'evidence_quest':'1000000000000000','native_case':'opening'},
            {'entry':'build_cost_observation','observation':'旧兵器架残损铁剑在原流云备料任务完成后被工作台实际消耗；军械所得单个机括进入连弩，再由原连弩进入重弩。只证明后续用途和付款顺序，不证明自然发现时机合适。'}],
        'stage_execution_boundaries':{
            'opening_early':'顺序FTB提交，无setCompleted进度预置；仍由QA供原料及水桶。开局脚本跨到了原规格的早期铁制工具，不能把这个边界视为玩家阶段长度。',
            'middle_midlate_late':'各自独立新玩家，段首外部前置ID完整列入qa_boundary_progress；本段目标走实际检测。装备前驱递归合成或来自真实定时互动，没有装备直接补发。',
            'terminal':'两个当前胸甲目标无任务前置；装备前驱逐件实际付款，Boss信物/稀有材料由QA补充，未证明Boss/镇渊生存流程。',
            'food':'8种各自独立角色，前置任务预置；本次实际原配方产物提交并消费。使用动作只验服务端32tick与EAT/DRINK枚举，未验中文视听/真人手感。'},
        'survival_followup_plan':[
            {'stage':'开局','native_segment':'opening','next_natural_inputs':'自然获得木/石/铜/铁/煤、竹、线与丝绸；按qa_materials同量替换供料，水桶由原水源装取。',
             'checkpoints':'保留根任务起每次完成时的背包、游戏/现实时间；重点记录铁镐/水桶已在手时才完成木矛目标，以及布衣→竹甲实际使用区间。'},
            {'stage':'早期','native_segment':'early','next_natural_inputs':'自然制作罗盘所需材料、青铜合金、朱砂、竹简、墨、图纸、精钢；以source_associations中的原配方/掉落为入口，再接奇门与军粮。',
             'checkpoints':'比较原任务完成时铁剑/盾/青铜甲与连弩的成本、选择理由；当前路线从原合成表选到的具体tag材料只是可行实例，非唯一采集方案。'},
            {'stage':'中期','native_segment':'middle','next_natural_inputs':'银锭、玉、丝绸等从原掉落/交易/矿物链获得；科举与赠冠入口仍须自然完成，原生交易旁证见evidence/20261023。',
             'checkpoints':'保留银剑使用时长→玉剑和青铜甲→玉甲的实际替换记录；完成军粮/丝袋分支后检查真实流派需要与饰品槽。'},
            {'stage':'中后期','native_segment':'rack_build+armory_build','next_natural_inputs':'自然找到原旧兵器架/军械点，而不是本轮QA调用TravelSitePiece放置；用真实故事/导航/军令/Boss进度替换完整边界ID清单。',
             'checkpoints':'到访时已有装备及机括库存；按实测600/3600服务器tick完成，实际残损剑→流云、军械机括→连弩→重弩，记录是否有替换需求。'},
            {'stage':'后期','native_segment':'late','next_natural_inputs':'龙晶、帝骸骨、玉玺从既有Boss/战利品链自然取得；读取DynastyBossDrops现有行为，不新增掉落。',
             'checkpoints':'原镇岳→巨阙→青龙→玄武的三个锻造前成本任务与实际库存，Boss战前后原武器仍用多久；不要求普通合成继承全部NBT。'},
            {'stage':'终盘','native_segment':'terminal','next_natural_inputs':'收集原龙鳞/令牌/羽角/玄天玉/帝兵信物，并真实进入终盘相关探索/镇渊流程；本轮33次胸甲递归付款只给成本清单。',
             'checkpoints':'玄天/鸿蒙目标虽无当前FTB依赖，不能据此绕过自然资源难度；记录整套Build收益和最终替换理由。'},
            {'stage':'食品贯穿各段','native_segment':'food_*','next_natural_inputs':'用自然取得原料复用8条实付合成与使用链；生态掉落接Rawls结果，不重复他的刷怪验收。',
             'checkpoints':'真人客户端核对使用动画、中文反馈、持续观感；回气丹另接实际流派攻击/连招，引路香的定位结果需走到遗迹。暖酒及其他材料转化不被本次基础8种食品覆盖。'}],
        'historical_mapping_note':'task-location-audit.json是修复前历史快照，主协调已校准主表。此报告解析独立快照中的1259真实节点，不以旧主表hash证明当前表匹配。',
        'research_reuse':plan['research'],
        'independently_closable_todos':[], 'can_remove_survival_or_pacing_todo':False,
        'exact_todos_not_closed':[
            '用生存流程核对六个阶段：开局、早期、中期、中后期、后期、终盘。',
            '检查任务出现时玩家已有装备、制作成本、Build 需求与替代时机，避免刚完成任务就立即淘汰。',
            '验证开局过渡约 2–3 小时等原文节奏目标；代码和静态任务图不能证明实际游玩时长。',
            '实机验收药品/酒/香/军粮的使用动作、持续时长与对应 Build 收益；已完成的物品注册和普通配方不重复制作。'],
        'pending':[
            '六阶段自然采集、寻路、科举、Boss战与完整材料成本；本轮所有补料均为QA提供。',
            '31取得/制作与15互动中未连接入口见entries；各段跨阶段故事/发现前置是明示夹具，并非真人跑通。',
            '原Build需求和实际替代时机需携带这些装备进入真实战斗/探索；配方使用价值不代表体验节奏合适。',
            '开局2–3小时要求未测；服务器真实tick与加速GameTest、脚本即刻操作均不等于真人时长。',
            '原生ServerPlayer/Menu/FTB证明服务端路径；菜单由QA打开、材料由QA供给，未证明工作站自然找到或界面/声音/动作观感。',
            '生态自然刷怪Rawls负责，旧档主协调负责，本轮不重复或代为认定。'],
        'prior_evidence_boundary':'595配方与18utility只作独立旁证，不计作六阶段自然生存完成。'}
    dump(HERE/'routes/acceptance.json',report)
    doc=ROOT/'docs/cod4/audit-20261022/journey-acceptance.json';full=read(doc);full['route_acceptance']=report;dump(doc,full)
    print(json.dumps({k:report[k] for k in ('status','cases_passed','cases_total','native_unique_quests_submitted','native_unique_recipes_paid','cod4_connected_nodes_submitted')},ensure_ascii=False))

if __name__=='__main__':main()
