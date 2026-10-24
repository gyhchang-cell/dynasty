#!/usr/bin/env python3
"""Read the current quest graph and make bounded, survival-compatible native route segments."""
import hashlib
import json
from pathlib import Path
import re
import sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0,str(ROOT/'tools/art'))
from quest_snbt import list_compounds, object_id


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v): p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')


def main():
    nodes={}; hashes={}
    for p in sorted((ROOT/'modpack/config/ftbquests/quests/chapters').glob('*.snbt')):
        raw=p.read_text();hashes[str(p.relative_to(ROOT))]=sha(p)
        for block in list_compounds(raw,'quests'):
            inner='\n'.join(x[2:] if x.startswith('\t\t') else x for x in block.splitlines())
            qid=object_id(block).lower();dep=re.search(r'^\tdependencies:\s*\[([^\]]*)\]',inner,re.M)
            title=re.search(r'^\ttitle:\s*"([^"]*)"',inner,re.M)
            tasks=[]
            for task in list_compounds(inner,'tasks'):
                kind=re.search(r'\btype:\s*"([^"]+)"',task)
                if not kind:continue
                row={'id':object_id(task).lower(),'type':kind[1],'definition':task}
                if kind[1]=='item':
                    item=re.search(r'\bitem:\s*\{\s*id:\s*"([^"]+)"',task);count=re.search(r'\bcount:\s*(\d+)L',task)
                    if item:row.update(item=item[1],count=int(count[1]) if count else 1)
                if kind[1]=='advancement':row['advancement']=re.search(r'\badvancement:\s*"([^"]+)"',task)[1]
                tasks.append(row)
            nodes[qid]={'id':qid,'title':title[1] if title else '', 'chapter':p.stem,
                'path':str(p.relative_to(ROOT)), 'line':raw.count('\n',0,raw.index(block))+1,
                'dependencies':[i.lower() for i in re.findall(r'"([0-9a-fA-F]{16})"',dep[1])] if dep else [],'tasks':tasks}
    assert len(nodes)==1259
    def ancestors(qid):
        seen=set();todo=list(nodes[qid]['dependencies'])
        while todo:
            v=todo.pop()
            if v not in seen:seen.add(v);todo.extend(nodes[v]['dependencies'])
        return seen
    old=json.loads((HERE/'old-equipment-utility.json').read_text())
    equipment={i['item'] for i in old['items']}
    recipe_root=ROOT/'src/main/resources/data/dynasty/recipes';recipes={}
    for p in sorted(recipe_root.rglob('*.json')):
        rid='dynasty:'+str(p.relative_to(recipe_root).with_suffix(''));data=json.loads(p.read_text());recipes[rid]=data
        hashes[str(p.relative_to(ROOT))]=sha(p)
    index=json.loads((ROOT/'docs/cod4/quest-nodes.json').read_text());entries=[]
    for row in index:
        q=nodes[row['id']];prior=ancestors(q['id']);item='dynasty:'+row['item']
        produced=[rid for rid,r in recipes.items() if (r.get('result',{}).get('item') if isinstance(r.get('result'),dict) else r.get('result'))==item]
        sources=[]
        for p in (ROOT/'src/main/resources/data/dynasty/loot_tables').rglob('*.json'):
            if '"'+item+'"' in p.read_text():sources.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p),'status':'READ_ONLY_SOURCE_ASSOCIATION_NOT_NATURAL_ENCOUNTER'})
        entries.append({**row,'chapter':q['chapter'],'task_source':q,'ancestor_count':len(prior),'ancestor_ids':sorted(prior),
            'required_prior_equipment_objectives':sorted({t['item'] for a in prior for t in nodes[a]['tasks'] if t.get('item') in equipment}),
            'recipes':produced,'loot_associations':sources,
            'entry_gap':'原31取得/合成节点单点原生提交已过；本轮查来源产物→成本支付→当前前置链的连续衔接。' if not row['interaction'] else '原互动定时/场景另有专用验收；本轮关注其收益进入后续配方/Build与FTB前置链。'})
    phase_defs=[
        ('opening','开局','原第一章根任务→工作台/储物/火把/熔炉/铁镐/水桶→木矛/石戈/铜刀/铁剑→盾；布衣→竹甲',
         '原生合成+顺序FTB提交；无任务进度预置。矿物、木材等QA供料逐次记账，水桶为明确入口夹具。'),
        ('early','早期','完整开局链→两种罗盘→青铜/朱砂/竹简/墨/图纸/精钢→奇门机括/钢索/连弩',
         '原生库存连续扣料、目标提交；指南针和罗盘等若由QA供给必须逐项声明，不能记为自然取得。'),
        ('middle','中期','原青铜剑→银剑→玉剑；布衣→竹甲→青铜甲→玉甲；原军粮→丝绸袋任务分支',
         '任务前置单列预置；原装备前驱递归实付，银锭/玉/丝绸等明确QA提供。科举赠冠和真实饰品槽成长另验。'),
        ('rack_build+armory_build','中后期','旧兵器架600tick→残损铁剑→流云剑+流派配饰；废弃军械3600tick→机括→钢索/连弩→重弩与弹药',
         '导航/军令/科举/Boss等段首任务夹具逐项列出；两条真实互动收益进入后续原配方，流派备料任务先验后付款。'),
        ('late','后期','原镇岳刀→巨阙→青龙→玄武锻造进化链',
         '仅原生连续付款与现有任务检测；关卡材料提供清单明确，不把QA材料当自然Boss掉落。'),
        ('terminal','终盘','原胸甲分支连续制作→玄天/鸿蒙终点与原FTB物品目标',
         '原配方按真实前驱逐步消耗；终盘原料均标QA，既有前驱不得直接补发绕过链。真实终盘战斗/替换体验另验。'),
    ]
    ref=ROOT/'docs/cod4/audit-20261022/quest-reference-1000.json';reference=json.loads(ref.read_text());files={s['file']:s['file_sha256'] for s in reference['sites']}
    assert len({s['semantic_sha256'] for s in reference['sites']})==len(reference['sites'])==1000
    assert all(sha(Path(p))==h for p,h in files.items())
    boundary={'qa_materials':'每次补料均记录物品/数量/用途；连续产出的前驱装备不允许自动补发。',
        'qa_progress':'跨科举、Boss、地图发现的段首前置仅作有清单的夹具；本段测试的目标禁止setCompleted。',
        'time':'只记录服务器真实tick差及脚本动作序列。GameTest加速运行，不能声称2–3小时真人时长或合适淘汰节奏。',
        'natural_spawn':'生态NATURAL刷怪由Rawls负责，本轮只关联当前源文件，不重复刷怪率/生态测试。',
        'legacy':'旧档兼容由主协调处理，本轮新建私有世界。',
        'build':'所有结构均调用既有放置实现/资产，只验收益入口，不新建或改建筑设计。'}
    report={'status':'PLAN_READY_NATIVE_RESULTS_SEPARATE','quest_count':len(nodes),'cod4_entry_count':46,
        'obtain_craft_nodes':31,'interaction_nodes':15,'entries':entries,
        'ancestor_union_count':len(set().union(*(set(e['ancestor_ids']) for e in entries))),
        'six_stages':[{'case':c,'stage':s,'route':r,'proof_boundary':b} for c,s,r,b in phase_defs],
        'stage_spec_source':'docs/cod4/request.txt:385-390；保留原六阶段语义，实际任务章节用当前1259节点解析。测试开局前置链跨及早期铁制装备，不能把脚本边界当作自然游玩阶段或时长。',
        'scope_boundaries':boundary,'research':{'reused':str(ref.relative_to(ROOT)),'records':1000,'verified_source_files':len(files),'scope':'同一任务来源、前驱和成本用途；不声称1000实机。'},
        'findings':[{'entry':'old_weapon_rack','observation':'当前旧兵器架任务的完成前置经导航链要求先取得铁剑；这不等于首次可见时间。旧剑已有流派前驱用途，不据此判无用或擅改任务。'},
            {'entry':'abandoned_armory','observation':'当前任务依赖虎符调兵，收益机括有更早制作入口；是否实际出现过晚须看自然发现和Build选择，静态前置不能证明玩家到访时间。'}],
        'can_remove_survival_or_pacing_todo':False,'input_sha256':hashes}
    dump(HERE/'routes/plan.json',report);dump(HERE/'routes/quest-graph.json',nodes);dump(HERE/'routes/recipes.json',recipes)
    print(json.dumps({k:report[k] for k in ('status','quest_count','cod4_entry_count','ancestor_union_count')},ensure_ascii=False))


if __name__=='__main__':main()
