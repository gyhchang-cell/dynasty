"""Readable kill-growth quests. IDs of all previous quests remain unchanged."""
from gen_growth_book import EVOLUTIONS
from gen_school_branches import BRANCHES

def refining_costs(rank, name):
    """Same cost contract as DynastyAccessoryRefining; no ambiguous cumulative XP."""
    from collections import Counter
    totals=Counter()
    steps=[]
    start={1:0,5:1,15:5,30:15}.get(rank,0)
    for current in range(start,rank):
        material='jade' if current<10 else 'dragon_crystal' if current<25 else 'xuantian_jade' if current<50 else 'sky_token'
        amount=1+min(63,current//4)
        totals[material]+=amount
        steps.append(f'+{current} → +{current+1}：{name("dynasty:"+material)}×{amount}，经验 {2+min(37,current)} 级。')
    total='、'.join(f'{name("dynasty:"+k)}×{v}' for k,v in totals.items())
    return [f'本段 +{start} → +{rank}，材料合计：'+total+'。',
            '铁砧左槽放饰品，右槽放本次材料；逐级取出结果。经验按每次操作时的等级扣除，不是一次扣累计经验值。',
            '&b逐级消耗&r',*steps,
            f'淬炼 +{rank} 的额外伤害：{4*rank**.5:.2f}%。必须佩戴生效；伤害类型跟随所属流派。',
            '锻造进化保留淬炼。'+('30级之后仍可继续：25–49用玄天玉、50起用天将令；每次材料为1+当前等级÷4向下取整（最多64），经验为2+当前等级（最多39级）。' if rank==30 else '')]

PASSIVES={
 'guard':'镇关镜把每点护甲韧性转成1.6%增伤（最多200%）；虎贲护腕再增加12%伤害。',
 'sword':'连城穗增加16%伤害，踏云佩增加12%伤害。无需移动或连段。',
 'archer':'观星佩增加10%伤害，对发光目标提高至25%；鸣弦戒增加12%伤害。',
 'talisman':'司天印增加25%伤害，定风绢增加15%伤害。无需站定蓄势。'}

def refine_route(rows,key,spec,recipes,name):
    from quest_routes import node,add_recipe,jump
    base=spec['base']
    generic='使用本流派王朝兵器击杀敌对生物，或给其他王朝兵器搭配本流派饰品。普通怪给1点历练，强敌最多8点；同一敌人只结算一次。'
    for i,q in enumerate(rows):
        if i==0:
            title='入门 · '+spec['title']
            body='先制作兵器，再杀怪成长。左到右查看熟练度里程碑；下排查看兵器进化。'+PASSIVES[key]
        elif i==1:
            title=q['title']; body=q['how']
        elif i==2:
            title=q['title']; body='带上这把武器开始杀怪；流派熟练度和武器历练同时增加。按Shift查看武器等级与历练进度。'
        elif i in (3,4):
            title=q['title']; body='在Curios对应槽位佩戴才生效。'+PASSIVES[key]
            q['deps']=[]
        elif i==5:
            title='初战 · 击杀一个敌人'; body=generic+' 不要求格挡、走位、连击或满蓄。'
        elif i>=12:
            title=q['title']; body=generic+' 流派阶数属于玩家，切换装备、死亡不清零。每阶提高伤害，升级所需历练递增；10阶以后仍可继续成长。'
        else:
            title=q['title']
            body=(f"击败{name(q['target'])}×{q['count']}。" if q['kind']=='kill' else
                  f"进入{name(q['target'])}。带好回程门和恢复品。" if q['kind']=='dimension' else
                  '准备：'+'、'.join(f'{name(k)}×{v}' for k,v in (q.get('items') or [(q['target'],q['count'])]))+'。')
            title=title.replace('练步装束','轻装备料').replace('三击成势','杀敌成长')
            if q['target']=='minecraft:target': body+='持有即可，不检测搭建。'
        # Preserve native boss-guide links while replacing stale instructions completely.
        links=[line for line in q['description'] if line.startswith('{') and 'change_page' in line]
        q.update(title=title,display_title=title,purpose=body,how=body,subtitle='杀怪成长' if i>=12 or i==5 else '')
        q['description']=[body]+links
        add_recipe(q,recipes,name)
    previous=rows[2]['id']
    for stage,(old,new,material) in enumerate(EVOLUTIONS[key],1):
        rid=f'evolve_{key}_{stage}'
        mats=[('dynasty:blueprint',1),('dynasty:'+material,1)]
        prep=node(base+0x60+stage*2,'进化备料 '+str(stage),'item','dynasty:'+material,
                  '准备本次锻造材料。','图纸放锻造台左槽，原兵器放中槽，强化材料放右槽。',items=mats,xp=15)
        prep['deps']=[previous]
        result=node(base+0x61+stage*2,'进化 '+str(stage)+' · '+name('dynasty:'+new),'item','dynasty:'+new,
                    '旧兵器进化，练过的等级不丢。',
                    f'锻造台：兵器图纸 + {name("dynasty:"+old)} + {name("dynasty:"+material)} → {name("dynasty:"+new)}。保留原武器等级、历练、附魔与名称。普通合成不继承历练。',xp=40)
        result['deps']=[prep['id']]
        for q in (prep,result):
            q.update(route=key,subtitle='锻造进化',shape='square')
            add_recipe(q,recipes,name)
        rows.extend((prep,result))
        previous=result['id']
    branch=BRANCHES[key]
    prep=node(base+0x80,'分支备料','item','dynasty:'+branch['base'],
              '保留已有等级，锻造成另一种被动兵器。','在锻造台使用图纸、原兵器和材料。',
              items=[('dynasty:'+branch['base'],1),('dynasty:blueprint',1),('dynasty:'+branch['material'],1)])
    result=node(base+0x81,'兵器分支 · '+branch['zh'],'item','dynasty:'+branch['id'],
                branch['effect'],f'锻造台：兵器图纸 + {name("dynasty:"+branch["base"])} + {name("dynasty:"+branch["material"])}。'
                +branch['effect']+'之后仍可进化成'+name('dynasty:'+branch['next'])+'；配方见山河录本流派页。',xp=30)
    result['deps']=[prep['id']]
    for q in (prep,result):
        q.update(route=key,subtitle='被动兵器分支',shape='square')
        add_recipe(q,recipes,name)
    rows.extend((prep,result))
    # Only real accessory evolution links connect; no gates on weapons or mastery.
    from gen_trinkets7 import ITEMS, TRINKETS
    from gen_codex_all import use_line
    group=[v for v in ITEMS.values() if v['school']==key]
    from quest_routes import code
    ids={v['id']:code(1,base+0x90+i) for i,v in enumerate(group)}
    for i,item in enumerate(group):
        stats=use_line(TRINKETS[item['id']], (0,0,0), 0, True)
        if item['zh_effect']: stats.insert(0,item['zh_effect'])
        advanced=item['recipe'][0].split(':')[-1] in ITEMS
        how='；'.join(stats)+'。放进对应 Curios 槽位即可生效。'
        if advanced: how+='锻造台：兵器图纸 + '+name(item['recipe'][0])+' + '+name(item['recipe'][1])+'。保留淬炼、附魔和自定义名称。'
        how+='铁砧可反复淬炼；本页淬炼节点列出每一级的材料和经验。'
        q=node(base+0x90+i,('进阶配装 · ' if advanced else '基础配装 · ')+item['zh'],
               'item','dynasty:'+item['id'],'；'.join(stats),how,xp=20 if advanced else 10)
        q.update(route=key,subtitle='进阶饰品' if advanced else '基础饰品',shape='diamond',
                 deps=[ids[item['recipe'][0].split(':')[-1]]] if advanced else [])
        add_recipe(q,recipes,name)
        rows.append(q)
    prep=node(base+0xa0,'淬炼工位 · 铁砧','item','minecraft:anvil',
              '同一件流派饰品可以一直培养。','铁砧左槽放本页任一饰品，右槽放材料。点击下方 +1、+5、+15、+30 节点查看逐级消耗；取出结果才扣材料和经验。')
    prep.update(route=key,subtitle='饰品淬炼',shape='square')
    rows.append(prep)
    previous=prep['id']
    for i,rank in enumerate((1,5,15,30)):
        q=node(base+0xa1+i,'淬炼 +'+str(rank),'advancement',f'dynasty:refine_{key}_{rank}',
               '持有或佩戴本流派淬炼等级达到目标的饰品。',
               '\n'.join(refining_costs(rank,name)),xp=20)
        q['description']=['持有或佩戴本流派淬炼等级达到目标的饰品。',*refining_costs(rank,name)]
        q.update(route=key,subtitle='饰品淬炼',deps=[previous],icon='{ id: "dynasty:'+group[0]['id']+'" }')
        rows.append(q);previous=q['id']
    # Published offsets 0x00..0xa4 above remain unchanged. New paths use 0xb0 onward.
    from weapon_evolution_paths import PATHS, QUEST_OFFSETS, recipe_id
    sources={q['target']:q['id'] for q in rows if q['kind']=='item' and not q.get('items')}
    for i,(path_id,old,new,material,label) in enumerate(PATHS[key]):
        q=node(base+QUEST_OFFSETS[path_id],label+' · '+name('dynasty:'+new),'item','dynasty:'+new,
               '把已有兵器锻造成另一把更强的兵器。',
               f'锻造台：兵器图纸 + {name("dynasty:"+old)} + {name("dynasty:"+material)} → {name("dynasty:"+new)}。各1件。保留等级、历练、淬炼、附魔与名称。',xp=40)
        q.update(route=key,subtitle='兵器进化',shape='square',deps=[sources['dynasty:'+old]],
                 evolution_recipe='dynasty:'+recipe_id(key,path_id))
        add_recipe(q,recipes,name)
        rows.append(q)
        sources['dynasty:'+new]=q['id']

def clean_navigation(chapters):
    """Remove redundant progression disclaimers, not quest edges or rewards."""
    replacements={
      '可选流派，不阻塞主线':'流派成长','点击选择，自由切换，不阻塞主线':'点击查看成长路线',
      '阅读无奖励，不阻塞主线。':'', '不阻塞主线':'',
      '不更改主线、不选永久职业、不要求集齐。':'',
      '，不作为主线要求':'',
      '不影响主线':'',
      '主线无关':'',
      '不是新的主线通关条件。':'', '旧主线导航':'行旅导航',
      '，主线无需等待本页':'', '常驻':'',
      '可选 · ':'', '可选会战 · ':'会战 · ',
      '可选补充；不要求完成本页来解锁主线。':'材料、用途与获取方式见下方。',
    }
    def walk(value):
        if isinstance(value,str):
            for a,b in replacements.items(): value=value.replace(a,b)
            return value
        if isinstance(value,list): return [walk(v) for v in value]
        if isinstance(value,dict): return {k:walk(v) for k,v in value.items()}
        return value
    for i,chapter in enumerate(chapters): chapters[i]=walk(chapter)
