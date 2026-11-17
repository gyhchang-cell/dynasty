"""Second editorial pass: smaller goals, fewer chapters, original save identities.

The 40-chapter source book remains independently validated. This pass is the
user-authorized migration, so its contract explicitly allows smaller quantities
and new preparation dependencies, while preserving targets, IDs and rewards.
"""
import copy
import hashlib
import json
import math
import re
from pathlib import Path
from boss_quest_guides import jump

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / 'docs/quests-journey-v3'
ASSET = 'dynasty:textures/gui/quests/journey/'

# Retain a representative chapter identity, redirect all removed chapter links.
MERGES = {
 'dynasty_c1': ['dynasty_c2','dynasty_cod4_workshop'],
 'dynasty_c3': ['dynasty_c4','dynasty_c7','dynasty_c8'],
 'dynasty_c5': ['dynasty_c6','dynasty_legacy'],
 'dynasty_c9': ['dynasty_c13','dynasty_cod4_wilds','dynasty_cod4_supplies','dynasty_cod4_encounters'],
 'dynasty_c10': ['dynasty_accessory_'+s for s in ('necklace','ring','bracelet','hands','body','back','belt','charm')],
 'dynasty_boss_ascent': ['dynasty_boss_guides'],
}
TITLES = {
 'dynasty_c1': '百工与机巧', 'dynasty_c3': '兵甲与锻造',
 'dynasty_c5': '科举与军旅', 'dynasty_c9': '山野与行旅',
 'dynasty_c10': '饰品与配装', 'dynasty_c12': '九霄见闻',
 'dynasty_boss_ascent': '四象试炼与讨伐',
}
GROUPS = [(6,'&6&l山河行纪'),(1,'&6&l主线旅程'),(7,'&c&l四门修习'),(2,'&2&l支线生活')]
KEEP = {'minecraft:torch':8,'minecraft:arrow':8,'minecraft:cobblestone':4,
        'minecraft:oak_planks':4,'minecraft:scaffolding':4,'dynasty:palace_brick':4}
PICTURES = {
 'dynasty:ritual_altar':'altar', 'guide:ritual_altar':'altar',
 'dynasty:jade_portal':'portals','dynasty:underworld_portal':'portals',
 'dynasty:cloud_portal':'portals','dynasty:dragon_gate':'portals',
 'dynasty:qimen_gear':'qimen','dynasty:bronze_ingot':'bronze',
 'dynasty:first_infusion':'infusion','dynasty:exam_paper':'exam',
 'dynasty:tiger_tally':'army','dynasty:army_led':'army',
 'naturescompass:naturescompass':'compasses',
 'explorerscompass:explorerscompass':'compasses',
}
MECHANICS = {
 'old_weapon_rack':'右键兵器架，等30秒再交互，领取一次残损铁剑。',
 'broken_stele':'主手拿纸右键界碑，等30秒再交互拓印；消耗纸×1。',
 'puzzle_box':'北站立→东潜行→南站立→西潜行。前三段各等40秒，末段等半秒；错向重来。',
 'wayside_tea_stall':'在官道驿站观察茶摊满2分钟，选择掀翻茶桌。喝茶不算调查。',
 'wayside_shrine':'主手拿安魂香右键神龛，等30秒再交互祈福；消耗香×1。',
 'herb_spot':'右键采集点，等1分钟再交互取药材。',
 'broken_waterwheel':'带奇门钢索右键水车；等1分钟再交互，消耗钢索修复。',
 'nameless_tomb':'主手拿鲜花右键无名墓，等1分钟再交互祭扫；消耗花×1。',
 'mortuary_room':'观察停尸台满2分钟，主手拿普通治疗药水右键停尸台救流民；消耗一瓶，返还空瓶。',
 'sword_scar_wall':'晴朗夜晚露天持剑：北向东移挥剑→北向西移挥剑→北移转东挥剑。每式隔40秒，总计2分钟。',
 'abandoned_armory':'右键军械开始拆解；等3分钟后再次交互取得机括。',
 'old_bellows':'在风箱3格内备可烧炼的熔炉与材料；带木炭右键，等30秒再交互。输出格留空。',
 'ancient_well':'用装满水的水桶供水7次，总计至少3分钟。每次返空桶，可装水重用。',
 'ghost_market_boat':'手持安魂香请船夫，询问渡口；点香满2分钟后交付朱砂。',
 'battlefield_remnant':'调查3处不同的战场残迹，按每处等待提示完成；重复同址不计数。',
}
SITE_PICTURES = {'puzzle_box':'locks','sword_scar_wall':'sword_moves',
                 'ancient_well':'well','ghost_market_boat':'boat',
                 'mortuary_room':'rescue','old_bellows':'bellows'}
SITE_VISITS = {'post_house':'1000000000072000','herbal_retreat':'1000000000072010',
               'desert_caravan':'1000000000072020'}

def clean(text): return re.sub(r'&[0-9a-fk-or]','',text)
def ident(key):
    return '1'+format(0xd3000000000000 | int(hashlib.sha256(key.encode()).hexdigest()[:12],16),'015x')

def node(key,title,target,kind='item',deps=None,description=None):
    qid=ident(key); tid='2'+qid[1:]
    if kind=='item':
        tasks=f'[{{ id: "{tid}", type: "item", item: {{ id: "{target}", Count: 1b }}, count: 1L, consume_items: false }}]'
        icon='{ id: "'+target+'" }'
    elif kind=='advancement':
        tasks=f'[{{ id: "{tid}", type: "advancement", advancement: "{target}" }}]'
        icon='{ id: "minecraft:compass" }'
    else:
        tasks=f'[{{ id: "{tid}", type: "checkmark" }}]';icon='{ id: "minecraft:map" }'
    return {'id':qid,'title':title,'display_title':title,'subtitle':'备料' if kind=='item' else '操作教程 · 阅读后勾选',
            'icon':icon,'kind':kind,'target':target,'count':1,'tasks':tasks,'rewards':'[]',
            'description':description or [f'取得{title.split(" · ")[-1]}×1，放在背包等待检测。'],
            'deps':deps or [],'role':'tutorial','x':0.,'y':0.,'shape':'circle' if kind=='item' else 'square',
            'section':'','journey_new':True}

def quantity(q):
    if q['kind'] not in {'item','kill'}:return
    if q['kind']=='item':
        # Multi-item preparation goals have their own quantities, independent of
        # the primary item's count (e.g. water bucket plus a stack of road stone).
        original=q['tasks']
        q['tasks']=re.sub(r'\bcount:\s*(\d+)L',lambda m:'count: '+str(min(int(m[1]),KEEP.get(q['target'],4)))+'L',q['tasks'])
        if original!=q['tasks']:q['journey_task_quantity_changed']=True
    old=q['count'];limit=3 if q['kind']=='kill' else KEEP.get(q['target'],1)
    q['count']=min(old,limit)
    if q['count']==old:return
    field='value' if q['kind']=='kill' else 'count'
    q['tasks']=re.sub(r'\b'+field+r':\s*(\d+)L',lambda m:f'{field}: {min(int(m[1]),limit)}L',q['tasks'])
    for key in ('title','display_title'):
        q[key]=re.sub(r'×\s*'+str(old)+r'\b','×'+str(q['count']),q.get(key,q['title']))
        for word in ('六十四','三十二','十六','十二','两份','两枚','两支'):
            if word in q[key]:q[key]=q[key].replace(word,str(q['count']))
    q['journey_previous_count']=old

def concise(q):
    from quest_story import name
    out=[]; links=[]
    for s in q['description']:
        if s.startswith('{"'):
            label=json.loads(s).get('text','')
            if label.startswith(('出行准备','←','返回','接着做')):continue
            links.append(s);continue
        if s.startswith('{image:'):continue
        plain=clean(s)
        if not plain or plain in {'做法','目标','用途与操作','材料与制作','掉落与探索'}:continue
        if plain.startswith(('获得','取得物品：','亲手合成：','配方任选一种','持有即可',
          '取得成品后自动记录','完成现场交互后自动记录','合成后自动记录','本页采用配方')):continue
        if 'music_tier' in s or '符号 +' in s:continue
        if q.get('journey_task_quantity_changed') and plain.startswith('准备：'):continue
        if '必须亲手合成一次' in s:s='必须亲手合成；拾取或购买不计，不扣留成品。'
        if plain.startswith('方块掉落表：'):continue
        if q.get('journey_previous_count') and re.search(r'(背包|检测|收集|持有|准备).*(×|支|块|份)',s):continue
        out.append(s)
    if q['kind']=='item':goal=f'&e取得{name(q["target"])}×{q["count"]}，背包持有即可。'
    elif q['kind']=='kill':goal=f'&e击败{name(q["target"])}×{q["count"]}。'
    elif q['kind']=='advancement':goal='&e'+clean(q.get('objective_title',q.get('display_title',q['title'])))
    else:goal=None
    # Use one basic recipe here; alternative recipes remain accessible through JEI.
    recipes=[s for s in out if '→' in s and ('×' in s or '合成：' in s)]
    if recipes:out=[s for s in out if s not in recipes]+[recipes[0]]
    q['description']=([goal] if goal else [])+out+links[:2]
    if q.get('journey_task_quantity_changed'):
        from quest_snbt import list_compounds
        amounts=[]
        for task in list_compounds('\ttasks: '+q['tasks'],'tasks'):
            target=re.search(r'\bitem:\s*\{[^}]*id:\s*"([^"]+)"',task)
            count=re.search(r'\bcount:\s*(\d+)L',task)
            if target and count:amounts.append(name(target[1])+'×'+count[1])
        if len(amounts)>1:q['description'].insert(1,'同时准备：'+'、'.join(amounts)+'。')
    item=q.get('cod4_item')
    if item in MECHANICS:
        from quest_cod4 import SITES,LOCATIONS
        site=SITES[item][0];location=LOCATIONS[site]
        q['subtitle']='现场交互 · '+location
        q['description']=['&e'+MECHANICS[item],
            '地点：主世界'+location+'院边互动点；旧建筑无互动点时找新建筑。',
            jump('找建筑 · '+location,SITE_VISITS[site])]
    # Cod4 obtain tasks target advancements; their item identity is stored
    # separately. Using only the advancement target silently dropped qimen.
    picture=SITE_PICTURES.get(item) or PICTURES.get('dynasty:'+item if item else q['target']) or PICTURES.get(q['target'])
    if q.get('evolution_recipe'):picture='smithing'
    if q['target'].startswith('guide:slot_'):picture='curios'
    if picture:q['description'].append(f'{{image:{ASSET}{picture}.png width:220 height:110 align:center fit:true}}')

def preparations(source):
    from quest_story import recipe_index,name
    recipes=recipe_index();added=[]
    locked=json.loads(Path(__file__).with_name('quest_journey_preparations.json').read_text())['parents']
    # Reserve the deployed lanes before considering new recipes. A newly-added
    # recipe must not take a lane away from a saved quest later in the section.
    used=sum(q['id'] in locked for q in source['quests'])
    # Short, actual recipe preparation chains. Existing main milestones stay in order.
    for q in list(source['quests']):
        if q['kind']!='item' or q['target'] not in recipes:continue
        choices=[r for r in recipes[q['target']] if len(r['ingredients'])>=2]
        if not choices:continue
        candidates=[(t,n) for t,n in min(choices,key=lambda r:sum(r['ingredients'].values()))['ingredients'].items()
                    if ':' in t and not t.startswith('#') and ' / ' not in t and t!=q['target']]
        deployed=locked.get(q['id'],[])
        if deployed:
            assert any({('#minecraft:planks' if p['target']=='minecraft:oak_planks' and '#minecraft:planks' in r['ingredients'] else p['target']) for p in deployed}<=set(r['ingredients']) for r in recipes[q['target']]),'Deployed prep recipe removed; inspect before changing save identity: '+q['id']
            candidates=[(p['target'],1) for p in deployed]
        if not candidates:continue
        # Curated density: two steps for eight recipes per source section, three on main pages.
        if used>=(3 if source['main'] else 8) and not deployed:continue
        if not deployed:used+=1
        deps=list(q['deps']);previous=None
        for index,(target,count) in enumerate(candidates[:2]):
            p=node('prep:'+q['id']+':'+str(index),'备料 · '+name(target),target,
                   deps=[previous] if previous else deps,
                   description=[f'取得{name(target)}×1，留作{name(q["target"])}的材料。',
                                '此步只记一次备料，成品配方所需数量见制作节点。'])
            if deployed:assert p['id']==deployed[index]['id'],'Deployed preparation order changed'
            p['section']=source['file'];p['for_quest']=q['id'];added.append(p);previous=p['id']
        if q['role']!='main' and previous:
            q['deps']=[previous]
            q['journey_preparation']=True
    return added

def redirect(chapters,mapping):
    for c in chapters:
        for q in c['quests']:
            rewritten=[]
            for s in q['description']:
                if s.startswith('{"'):
                    obj=json.loads(s);event=obj.get('clickEvent',{})
                    if event.get('value') in mapping:event['value']=mapping[event['value']]
                    s=json.dumps(obj,ensure_ascii=False)
                rewritten.append(s)
            q['description']=rewritten
        for image in c.get('images',[]):
            click=image.get('click','')
            if click.startswith('#') and click[1:] in mapping:image['click']='#'+mapping[click[1:]]

def arrange(chapter,sections):
    """Separate labeled blocks; local lanes, no long diagonals across the page."""
    from quest_journey_layout import prerequisite_rows
    chapter['images']=[];chapter['quest_links']=[]
    allq=[];columns=3 if len(sections)>4 else 2 if len(sections)>1 else 1
    row_top=0.;row_height=0.
    for index,section in enumerate(sections):
        if index and index%columns==0:row_top+=row_height+3.;row_height=0.
        center=(index%columns-(columns-1)/2)*18.
        rows=prerequisite_rows(section['quests'],columns=6)
        title=clean(section['title']) if section['file'].startswith('dynasty_accessory_') else clean(section['title']).split(' · ')[0]
        if section['file']=='dynasty_c10':title='饰品 · 头部'
        section_goal=section['goal'].replace('沿连线查看下一步材料和成品。','')
        header=node('section:'+section['file'],title,'guide:section',kind='checkmark',
                    description=[section_goal,'本区从上到下阅读，带连线的节点按连线完成。'])
        header['icon']=section['icon'];header['section']=section['file'];header['section_header']=True
        header['x']=center;header['y']=row_top-1.8;header['size']=1.25
        header['subtitle']='分区 · 点击查看';allq.append(header)
        chapter['images'].append({'image':ASSET+'labels/'+section['file']+'.png',
            'x':center,'y':row_top-3.2,'width':15.,'height':1.,'rotation':0.,'alpha':255,
            'order':-1,'click':'#'+header['id'],'hover':[title]})
        if section['file']=='dynasty_accessory_charm':
            from quest_journey_charms import arrange as arrange_charms
            row_height=max(row_height,arrange_charms(section,center,row_top,header,allq,chapter['images']))
            continue
        for row,nodes in enumerate(rows):
            for col,q in enumerate(nodes):
                q['x']=center+(col-(len(nodes)-1)/2)*1.65;q['y']=row_top+row*1.8
                q['section']=section['file'];allq.append(q)
        row_height=max(row_height,len(rows)*1.8)
    chapter['quests']=allq
    xs=[q['x'] for q in allq];ys=[q['y'] for q in allq]
    dx=(max(xs)+min(xs))/2;dy=(max(ys)+min(ys))/2
    for q in allq:q['x']-=dx;q['y']-=dy
    for image in chapter['images']:image['x']-=dx;image['y']-=dy
    chapter['autofocus_id']=allq[0]['id']
    headers=[q for q in allq if q.get('section_header')]
    if len(headers)>1:
        headers[0]['description'].extend(jump('分区 · '+q['title'],q['id']) for q in headers[1:])

def separate_main_routes(chapters):
    """Keep the story pages free of optional spurs without changing save progress."""
    from gen_curios import classifications
    SLOTS=classifications()
    sources={c['file']:c for c in chapters}
    byid={q['id']:q for c in chapters for q in c['quests']}
    origins={q['id']:c['file'] for c in chapters if c['main'] for q in c['quests']}
    moved={}
    def destination(q):
        if q.get('for_quest') in origins:return destination(byid[q['for_quest']])
        if q['role']=='exploration_branch':return 'dynasty_c9'
        item=q['target'].split(':',1)[-1]
        if item in SLOTS:
            slot=SLOTS[item]
            return 'dynasty_c10' if slot=='head' else 'dynasty_accessory_'+slot
        if item in {'official_seal','jade_seal','arrow'}:return 'dynasty_c5'
        if item in {'zhuxing_bow','pickaxe_jade','sword_dragon_crystal','tianzi_sword','tianlang_bow','houyi_bow'}:return 'dynasty_c3'
        if item in {'white_bed','bread','bucket','magma_block','sea_lantern','sea_pearl','sea_conch','emperor_bone'}:return 'dynasty_c9'
        if item in {'scaffolding','spyglass','sky_token'}:return 'dynasty_c12'
        origin=origins[q['id']]
        return {'dynasty_story_03':'dynasty_c5','dynasty_story_06':'dynasty_c12',
                'dynasty_story_07':'dynasty_c9','dynasty_story_08':'dynasty_c3'}.get(origin,'dynasty_c1')
    for c in chapters:
        if not c['main']:continue
        optional=[q for q in c['quests'] if q['role']!='main']
        for q in optional:
            target=destination(q)
            q['journey_main_origin']=c['file']
            q['section']=target
            if target=='dynasty_accessory_charm' and not q.get('journey_effect_notes'):
                from quest_journey_charms import describe
                describe(q)
            sources[target]['quests'].append(q)
            moved[q['id']]=target
        c['quests']=[q for q in c['quests'] if q['role']=='main']
        # Five columns keep the same button size and the existing 1.5-unit spacing.
        rows=math.ceil(len(c['quests'])/5)
        for i,q in enumerate(c['quests']):
            row,col=divmod(i,5)
            q['x']=(col if row%2==0 else 4-col)*1.5-3.
            q['y']=(row-(rows-1)/2)*1.8
        c['autofocus_id']=min(c['quests'],key=lambda q:abs(q['x'])+abs(q['y']))['id']
        if optional:
            c['quests'][0]['description'].append(jump('本章备料与支线',optional[0]['id']))
    # A cross-chapter prerequisite has no drawable line. Give it an exact link.
    for c in chapters:
        for q in c['quests']:
            if q['id'] not in moved:continue
            existing={json.loads(s).get('clickEvent',{}).get('value') for s in q['description'] if s.startswith('{"')}
            for dep in q['deps']:
                if dep not in moved and dep in origins and dep not in existing:
                    q['description'].append(jump('前置 · '+clean(byid[dep]['title']),dep))

def split_boss_guides(chapters):
    from boss_quest_guides import GUIDES
    c=next(c for c in chapters if c['file']=='dynasty_boss_guides')
    for boss,(number,title,token,adv,location,prepare,tactics) in GUIDES.items():
        q=next(q for q in c['quests'] if q['id']==f'1{number:015x}')
        steps=[]
        for topic,text in [('寻找',location),('准备',prepare),('应对',tactics)]:
            step=node('boss:'+boss+':'+topic,title+' · '+topic,'guide:'+boss+':'+topic,kind='checkmark',
                      description=[text],deps=[steps[-1]['id']] if steps else [])
            step['icon']=q['icon'];step['section']=c['file'];steps.append(step)
        q['description']=['先找到所在维度的栖息地，再备好退路和恢复品。',
            *[jump(s['title'],s['id']) for s in steps],
            jump('祭坛复战 · 摆放与信物','1000000000020006')]
        c['quests'].extend(steps)

def combat_ladders(chapters):
    for c in chapters:
        groups={}
        for q in c['quests']:
            if q['kind']=='kill':groups.setdefault(q['target'],[]).append(q)
        for target,qs in groups.items():
            if target in {'dynasty:royal_guard','dynasty:imperial_soldier','dynasty:jade_guard'}:
                for q in qs:
                    q['subtitle']='旧档兼容记录'
                    q['description']=['保留旧档记录。此实体属于友军，无需主动攻击；选择其他支线继续。']
                continue
            if len(qs)<2:continue
            for stage,q in enumerate(sorted(qs,key=lambda q:q.get('journey_previous_count',q['count']))):
                original=q.get('journey_previous_count',q['count']);n=min(original,stage+1,3)
                if n!=q['count']:
                    q['tasks']=re.sub(r'\bvalue:\s*\d+L','value: '+str(n)+'L',q['tasks'])
                    q['title']=re.sub(r'×\s*\d+','×'+str(n),q['title'])
                    q['display_title']=re.sub(r'×\s*\d+','×'+str(n),q.get('display_title',q['title']))
                    q['count']=n;concise(q)

def apply(base):
    from quest_journey_help import simplify,add_operation_steps,quiet_long_connections
    from quest_journey_charms import describe as describe_charm
    chapters=copy.deepcopy(base); sources={c['file']:c for c in chapters}
    for c in chapters:
        for q in c['quests']:quantity(q);concise(q);q['section']=c['file']
        c['quests'].extend(preparations(c))
    split_boss_guides(chapters)
    combat_ladders(chapters)
    for c in chapters:
        for q in c['quests']:
            simplify(q)
            describe_charm(q)
    add_operation_steps(chapters)
    from quest_bugfix_oct17 import apply as fix_oct17
    fix_oct17(chapters)
    from quest_bugfix_oct18 import apply as fix_oct18
    fix_oct18(chapters)
    from quest_cod2 import add_chensha,add_wangsi
    add_chensha(chapters)
    add_wangsi(chapters)
    separate_main_routes(chapters)
    removed={n for v in MERGES.values() for n in v};mapping={}
    for target,aliases in MERGES.items():
        destination=sources[target]
        for filename in aliases:
            old=sources[filename]
            mapping[old['id']]=old['quests'][0]['id']
        destination['title']=TITLES[target]
        destination['goal']='按分区选一条小支线；每次只完成眼前的一步。'
        destination['group']=2
        arrange(destination,[sources[n] for n in [target]+aliases])
    for c in chapters:
        if c['file'] in removed:continue
        if c['file'] not in MERGES:
            if c['main']:
                pass  # Only the story spine remains; optional tasks live in themed pages.
            elif c['file']!='dynasty_home':arrange(c,[c])
        if c['file'] in TITLES:c['title']=TITLES[c['file']]
        if c['group'] not in {1,6,7}:c['group']=2
    chapters=[c for c in chapters if c['file'] not in removed]
    redirect(chapters,mapping)
    # A single concise home directory links to live chapters only.
    home=sources['dynasty_home'];home['images']=[]
    q=home['quests'][0];q['description']=['选一条旅程开始；支线随时做，不要求清空所有物品。']
    q['x']=0.;q['y']=0.;q['subtitle']='上方主线；向下查看支线与四门修习'
    home['autofocus_id']=q['id']
    for c in chapters:
        if c is not home:q['description'].append(jump(clean(c['title']),c['id']))
    for i,c in enumerate([c for c in chapters if c is not home]):
        row=i//2
        home['images'].append({'image':ASSET+'cards/'+c['file']+'.png','x':(-2.55 if i%2==0 else 2.55),
            'y':-2.325+row*1.55+(1.2 if i>=8 else 0.),'width':4.,'height':1.,'rotation':0.,'alpha':255,
            'order':0,'click':'#'+c['id'],'hover':[clean(c['title'])]})
    for order,c in enumerate(chapters):c['order']=order
    quiet_long_connections(chapters)
    validate(chapters,base)
    previous=DOC/'last-deployed-book.json'
    if previous.is_file():validate_forward(chapters,json.loads(previous.read_text()))
    from quest_readability_oct20 import apply as readability
    readability(chapters)
    return chapters

def validate_forward(chapters,previous):
    """Nightly additions have save identities too, not just the original 808."""
    new={q['id']:q for c in chapters for q in c['quests']}
    assert {c['id'] for c in previous}<={c['id'] for c in chapters},'Previously deployed chapter lost'
    from quest_bugfix_oct17 import REMOVED_BLUEPRINT_PREPS
    for q in (q for c in previous for q in c['quests']):
        from quest_bugfix_oct18 import REMOVED
        if q['id'] in REMOVED_BLUEPRINT_PREPS | REMOVED:continue
        assert q['id'] in new,'Previously deployed quest lost: '+q['id']
        n=new[q['id']]
        assert (n['target'],n['kind'],n['rewards'])==(q['target'],q['kind'],q['rewards']),'Deployed identity repurposed: '+q['id']
        assert n['count']<=q['count'],'Deployed quantity increased: '+q['id']
        normalize=lambda text:re.sub(r'\b(count|value):\s*\d+L',r'\1: Q',text)
        # Explicit material migration for the previously conflicting Wind Plume smithing recipe.
        old_tasks=q['tasks']
        if q['id']=='1000000000030280':old_tasks=old_tasks.replace('dynasty:refined_steel','dynasty:sky_feather')
        assert normalize(n['tasks'])==normalize(old_tasks),'Deployed task detector changed: '+q['id']
        if q['role']=='main':assert n['deps']==q['deps'],'Deployed main spine changed'

def validate(chapters,base):
    from boss_quest_guides import validate_links
    old={q['id']:q for c in base for q in c['quests']};new={q['id']:q for c in chapters for q in c['quests']}
    assert len(new)==sum(len(c['quests']) for c in chapters),'Duplicate quest IDs'
    assert set(old)<=set(new) and len(new)>len(old),'Every existing quest must survive'
    assert len(chapters)==20,'Consolidation must retain exactly 20 live chapters'
    for key,q in old.items():
        n=new[key]
        assert n['rewards']==q['rewards'] and n['target']==q['target'] and n['kind']==q['kind'],'Existing save target/reward altered: '+key
        assert n['count']<=q['count'],'Quantity increased: '+key
        a=re.sub(r'\b(count|value):\s*\d+L',r'\1: Q',q['tasks'])
        b=re.sub(r'\b(count|value):\s*\d+L',r'\1: Q',n['tasks'])
        assert a==b,'Task behavior other than quantity altered: '+key
        if q['role']=='main':assert n['deps']==q['deps'],'Main journey sequence changed'
    graph={k:q['deps'] for k,q in new.items()};seen=set();active=set()
    def visit(k):
        assert k in graph,'Dangling dependency: '+k
        assert k not in active,'Dependency cycle: '+k
        if k in seen:return
        active.add(k)
        for d in graph[k]:visit(d)
        active.remove(k);seen.add(k)
    for k in graph:visit(k)
    validate_links(chapters)
    live=set(new)|{c['id'] for c in chapters}
    for c in chapters:
        for image in c.get('images',[]):
            path=ROOT/'src/main/resources/assets'/image['image'].replace(':','/',1)
            assert path.is_file(),'Missing map card/header: '+image['image']
            click=image.get('click','')
            assert not click or click.startswith('#') and click[1:] in live,'Broken map-card jump'
        positions=set()
        for q in c['quests']:
            p=(round(q['x'],3),round(q['y'],3));assert p not in positions,'Overlapping nodes: '+c['file'];positions.add(p)
            for s in q['description']:
                if s.startswith('{image:'):
                    assert (ROOT/'src/main/resources/assets'/s.split('image:',1)[1].split(' ',1)[0].replace(':','/',1)).is_file(),'Missing inline illustration'
            if q.get('journey_distant_dependencies'):
                links={json.loads(s)['clickEvent']['value'] for s in q['description'] if s.startswith('{"')}
                assert set(q['journey_distant_dependencies'])<=links,'Hidden prerequisite has no visible jump'
    ids=[c['id'] for c in chapters]+list(new)
    ids += [i.lower() for q in new.values() for i in re.findall(r'\bid:\s*"([0-9a-fA-F]{16})"',q['tasks']+q['rewards'])]
    assert len(ids)==len(set(i.lower() for i in ids)),'Duplicate FTB identity'
    assert all(0<int(i,16)<2**63 for i in ids),'Unsigned FTB identity'

def known_removed():return {n+'.snbt' for names in MERGES.values() for n in names}
