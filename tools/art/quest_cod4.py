"""Authored optional journeys for the 46 existing Cod4 quest identities.

Move presentation, not player data. Main quests never depend on these branches.
Dependencies express actual preparation; related pages link back to main travel.
"""
import json
from pathlib import Path
from boss_quest_guides import jump
ROOT = Path(__file__).resolve().parents[2]

# item: (chapter, x, y, prerequisites); @ references a main-story target.
PLAN = {
 'qimen_gear': ('workshop',-6,-4,['@refined_steel']),
 'qimen_cable': ('workshop',-3,-4,['qimen_gear']),
 'repeating_crossbow': ('workshop',0,-4,['qimen_cable']),
 'repeating_bolt': ('workshop',3,-4,['repeating_crossbow']),
 'siege_crossbow': ('workshop',0,-1,['repeating_crossbow','@dragon_crystal']),
 'heavy_bolt': ('workshop',3,-1,['siege_crossbow','crab_shell']),
 'flying_claw': ('workshop',-3,-1,['qimen_cable']),
 'rope_dart': ('workshop',-6,-1,['qimen_cable']),
 'meteor_hammer': ('workshop',-6,2,['rope_dart','@dragon_crystal']),
 'mandarin_duck_axe': ('workshop',-9,-1,['qimen_gear']),
 'pierce_arrow': ('workshop',-6,5,['wolf_fang','@refined_steel']),
 'poison_arrow': ('workshop',-3,5,['locust_dust']),
 'thunder_arrow': ('workshop',0,5,['@refined_steel']),
 'fox_pelt': ('wilds',-4,-3,['@naturescompass:naturescompass']),
 'wolf_fang': ('wilds',0,-3,['fox_pelt']),
 'python_gall': ('wilds',4,-3,['wolf_fang']),
 'crab_shell': ('wilds',-4,0,['@minecraft:water_bucket']),
 'kappa_scale': ('wilds',0,0,['crab_shell']),
 'sprite_jade': ('wilds',4,0,['@jade']),
 'lantern_oil': ('wilds',-2,3,['@naturescompass:naturescompass']),
 'locust_dust': ('wilds',2,3,['@naturescompass:naturescompass']),
 'army_ration': ('supplies',-6,-3,['@minecraft:furnace']),
 'silk_pouch': ('supplies',-2,-3,['army_ration']),
 'antidote_pill': ('supplies',2,-3,['python_gall']),
 'regen_pill': ('supplies',-6,0,['sprite_jade']),
 'qi_pill': ('supplies',-2,0,['regen_pill']),
 'marching_wine': ('supplies',2,0,['wolf_fang']),
 'zhuangyuan_wine': ('supplies',-6,3,['python_gall','@exam_paper']),
 'jade_crown': ('supplies',-2,3,['@exam_passed']),
 'soul_incense': ('supplies',2,3,['lantern_oil']),
 'guide_incense': ('supplies',6,3,['soul_incense']),
 'old_weapon_rack': ('encounters',-6,-4,['@naturescompass:naturescompass']),
 'broken_stele': ('encounters',-3,-4,['old_weapon_rack']),
 'puzzle_box': ('encounters',0,-4,['broken_stele']),
 'wayside_tea_stall': ('encounters',3,-4,['puzzle_box']),
 'wayside_shrine': ('encounters',6,-4,['wayside_tea_stall','soul_incense']),
 'herb_spot': ('encounters',-6,0,['@healing_salve']),
 'broken_waterwheel': ('encounters',-3,0,['herb_spot','qimen_cable']),
 'nameless_tomb': ('encounters',0,0,['broken_waterwheel']),
 'mortuary_room': ('encounters',3,0,['nameless_tomb']),
 'sword_scar_wall': ('encounters',6,0,['mortuary_room']),
 'abandoned_armory': ('encounters',-6,4,['@army_led']),
 'old_bellows': ('encounters',-3,4,['abandoned_armory']),
 'ancient_well': ('encounters',0,4,['old_bellows']),
 'ghost_market_boat': ('encounters',3,4,['ancient_well','soul_incense']),
 'battlefield_remnant': ('encounters',6,4,['ghost_market_boat']),
}
CHAPTERS = {
 'workshop': ('机巧工坊 · 备料到成器','精钢→机括与钢索→机巧兵器；按所选武器补弹药。', 'refined_steel'),
 'wilds': ('山野采获 · 循迹取材','林地、河岸、矿洞与夜行四路；收获用于下页丹药和弹药。','naturescompass:naturescompass'),
 'supplies': ('行旅补给 · 带上再出发','备军粮和锦囊；把采获制成药、酒与香，再返回主线出行。','naturescompass:naturescompass'),
 'encounters': ('途中见闻 · 三地行记','上：官道驿站；中：林间药庐；下：沙海商旅院。每行从左到右。','army_led'),
}
USE = {
 'qimen_gear':'精钢有了，先做传动件。机括用于连弩、鸳鸯钺和流星锤；再备钢索组装。',
 'qimen_cable':'钢索把机括接到兵器上；也能修复林间药庐的残破水车。留一条出行备用。',
 'repeating_crossbow':'松手装填最多三发，再按住依次发射。接着制作连发弩矢，或等取得龙晶后升级重弩。射艺六阶会解锁配方书页面。',
 'siege_crossbow':'升级会消耗连弩；先让连弩任务记录完成。重弩单发穿甲，有后坐力，避开悬崖边缘；再做重钢弩矢。射艺十阶解锁配方书页面。',
 'rope_dart':'钢索配精钢做成绳镖，适合先尝试有回收过程的投掷兵器。要重型选择再看流星锤。',
 'flying_claw':'带在出行栏试用飞爪的牵引功能；目标与距离以物品提示为准，先在平地熟悉。',
 'meteor_hammer':'钢索、机括与龙晶组成重型兵器。先在平地试用，再带入讨伐；无需为主线制作所有机巧武器。',
 'mandarin_duck_axe':'需要近身兵器时选择鸳鸯钺。官阶三阶或守势三阶后也可向大臣潜行交互购买机巧装备；这不限制提前合成。',
 'poison_arrow':'把旱地采得的蝗粉用于箭矢；带普通弓或王朝弓试射，留意目标的中毒效果。',
 'pierce_arrow':'把林地狼牙与精钢制成破甲矢，给远行弓手备弹；不需要先制作弩。',
 'thunder_arrow':'紫水晶碎片与红石用于引雷矢，留作远程交战的另一种弹药选择。',
 'heavy_bolt':'蟹甲和精钢做成重弩弹药；先有重弩，再按需补充。',
 'repeating_bolt':'机括配普通箭和羽毛制成连弩弹药；先试装填与发射，再决定储备数量。',
 'army_ration':'出远门前准备耐用口粮，使用后恢复饥饿并提供短时饱和。下一步做锦囊整理行装。',
 'silk_pouch':'取得锦囊会解锁自己的锦囊饰品槽；在 Curios 对应槽位佩戴。任务不会再次赠送槽位。',
 'regen_pill':'补给主力：使用后恢复最大生命的12%，并获得5秒生命恢复II。把它放到容易切换的快捷栏。',
 'qi_pill':'有回春丹保命后，再按需做聚气丹；使用时增加怒气并短时提振阳气，适合战前准备。',
 'antidote_pill':'蟒蛇胆用于解毒。使用后移除中毒，并获得30秒避毒效果；去沼泽或调查可疑茶摊前带上。',
 'zhuangyuan_wine':'准备科举时使用，考场增益持续60秒。答题前饮用，随后使用试卷；酒本身不会自动答题或升官。',
 'marching_wine':'使用后短时提振阳气，同时会有4秒反胃；选择安全位置饮用，再进入交战。',
 'soul_incense':'使用可清除阴气、魂灼，并驱散附近亡灵；也用于小神龛祈福和鬼市小舟请船夫。出行留一支。',
 'guide_incense':'右键后尝试寻找附近法阵遗迹，方向和距离提示持续60秒；它不负责寻找所有建筑。三地行记用探险者指南针。',
 'jade_crown':'玉冠可按配方制作；达到官阶三阶也会授予一顶。取得玉冠并达到三阶才解锁玉冠槽；用 /dynasty stats 查看官阶。',
}
WILDS = {
 'fox_pelt':('林地与山地的赤狐','狐皮用于后续装备，先留作野外采获；下一站留意同一带的灰狼。'),
 'wolf_fang':('林地、山地与雪地的灰狼','狼牙用于破甲矢和壮行酒；继续前往湿润林地寻找蟒蛇。'),
 'python_gall':('森林、山地、沼泽或丛林的巨蟒','蟒蛇胆用于避毒丹与状元酒，回营后再制药。'),
 'crab_shell':('河流、海岸与沼泽的蟹兵；尸甲虫也可能掉落','蟹甲用于重钢弩矢。沿河继续寻找河童，注意留好上岸位置。'),
 'kappa_scale':('河流、海岸与沼泽的河童','河童鳞用于水行装备；悬停按 U 查看当前可制作的用途。'),
 'sprite_jade':('林地、山地或洞穴的石精','石精玉粒用于回春丹和聚气丹，拿到后回营补充丹药。'),
 'lantern_oil':('林地、山地、平原或沙漠夜间的灯笼鬼','灯油用于安魂香和引路香。优先对付敌对灯笼鬼，不必攻击打更人。'),
 'locust_dust':('沙漠、恶地或热带草原的蝗群','蝗粉用于淬毒矢；备好恢复品再去旱地采获。'),
}
# Use recognizable existing vanilla/object icons for landmarks, never anonymous cubes.
SITES = {
 'old_weapon_rack':('post_house','minecraft:iron_sword','检视兵器架并拔取旧铁剑，剩余约四分之一耐久；每人只领一次。','沿院边查看破损界碑。'),
 'broken_stele':('post_house','minecraft:paper','带一张纸，右键开始观察，按现场倒计时提示再次交互完成拓印。','接着研究同院的小机关盒。'),
 'puzzle_box':('post_house','minecraft:tripwire_hook','右键机关盒按提示解锁：朝北站立→朝东潜行→朝南站立→朝西潜行。前三段各等40秒，总计至少2分钟；最后一销至少等半秒。方向错会复位。','获得图纸后，去查看古道茶摊。'),
 'wayside_tea_stall':('post_house','minecraft:honey_bottle','右键茶摊并察看茶面七彩油膜、无招牌摊位与摊主神情。首次观察满2分钟后，在对话中选掀翻茶桌，揭穿后取得丝绸。直接喝茶会中毒20秒，喝茶不算完成调查。','临行可带安魂香到小神龛祈福。'),
 'wayside_shrine':('post_house','minecraft:lantern','带一支安魂香右键神龛，按现场等待提示再次交互完成祈福。','驿站行程结束，可返回主线或前往林间药庐。'),
 'herb_spot':('herbal_retreat','dynasty:tea','右键采集点，按现场倒计时再次交互取得茶叶药材。药材可放进药浴盆，配朱砂制疗伤膏。','沿院边找到残破水车，备一条奇门钢索。'),
 'broken_waterwheel':('herbal_retreat','dynasty:qimen_cable','带一条奇门钢索，右键水车开始修复；满1分钟后再次交互，消耗钢索修好水车并打开机关通路。','继续查看无名墓，备一朵鲜花。'),
 'nameless_tomb':('herbal_retreat','minecraft:poppy','带鲜花右键无名墓，按现场倒计时再次交互完成祭扫。','接着察看义庄停尸台附近的流民。'),
 'mortuary_room':('herbal_retreat','minecraft:potion','先察看停尸台旁流民的微弱呼吸；观察满2分钟后，手持治疗药水救助生者。消耗一瓶并返还空瓶，可获一次传家龙渊剑；牛奶净化自身不等于救人。','带一把剑，等晴朗夜晚研究剑痕石壁。'),
 'sword_scar_wall':('herbal_retreat','dynasty:longyuan_sword','晴朗夜晚在露天持主手剑观察石壁：朝北向东移半步并挥剑→朝北向西移半步并挥剑→向北移半步、转朝东挥剑。每式间隔至少40秒，总计至少2分钟；原地右键不算。不要换剑、远离石壁或站到屋顶下。','三式完成可得玉；药庐行程结束，返回主线继续讨伐。'),
 'abandoned_armory':('desert_caravan','minecraft:anvil','右键开始拆解废弃军械，等待3分钟后再次交互，取得奇门机括。','接着利用院内旧风箱辅助烧炼。'),
 'old_bellows':('desert_caravan','minecraft:charcoal','带一块木炭，在风箱三格内准备熔炉、烟熏炉或高炉，放入能烧炼的材料并留空输出位。右键后等30秒再次交互，消耗木炭推动实际烧炼并取得铁粒。','备好水桶，继续调查古井。'),
 'ancient_well':('desert_caravan','minecraft:water_bucket','手持真正装满水的水桶，按井边提示分七次供水，每次返还空桶，可重新装水。七次总计至少3分钟，完成后得一枚玉；空桶不计。','再带安魂香和朱砂到鬼市小舟。'),
 'ghost_market_boat':('desert_caravan','minecraft:oak_boat','手持安魂香右键小舟请出船夫，在对话中询问渡口；点香满2分钟后，手持朱砂再交互交付，取得旧竹简。请给船边留出站立空间。','最后调查古战场残迹；需要走访三处不同位置。'),
 'battlefield_remnant':('desert_caravan','minecraft:iron_helmet','右键调查三处不同位置的古战场残迹，每处按现场等待提示完成。重复点击同一处不增加地点数，需要继续寻找其他商旅院的残迹。','三地行记收尾：返回主线继续平叛或准备跨维度远行。'),
}
LOCATIONS = {'post_house':'官道驿站','herbal_retreat':'林间药庐','desert_caravan':'沙海商旅院'}


def add_cod4(chapters):
    from quest_story import recipe_index, name
    nodes = json.loads((ROOT/'docs/cod4/quest-nodes.json').read_text())
    assert set(PLAN)=={n['item'] for n in nodes}, 'New Cod4 content needs an authored journey'
    recipes=recipe_index(); original={n['item']:n for n in nodes}
    main={q['target']:q for c in chapters if c['main'] for q in c['quests'] if q['role']=='main'}
    def anchor(target):
        return main[target if ':' in target else 'dynasty:'+target]
    def identity(key):
        return anchor(key[1:])['id'] if key.startswith('@') else original[key]['id']
    made={}
    for i,(key,(title,goal,origin)) in enumerate(CHAPTERS.items()):
        c=dict(file='dynasty_cod4_'+key,id=f'40000000000006{i:02x}',group=2,order=i-4,
               title=title,goal=goal,main=False,quests=[],images=[],quest_links=[])
        chapters.append(c); made[key]=c
    for item,(chapter,x,y,requirements) in PLAN.items():
        node=original[item]; crafted=node.get('objective')=='CRAFT'; interaction=node['interaction']
        mode='亲手合成' if crafted else '现场完成' if interaction else '取得物品'
        origin=anchor(CHAPTERS[chapter][2]); icon='dynasty:'+item
        description=[jump('← 返回主线 · '+origin['title'],origin['id']),
                     '&6&l这一步要做什么&r',f'{mode}：{node["title"]}。']
        if item in SITES:
            location,icon,action,after=SITES[item]
            description += ['&b&l去哪里&r', f'主世界的{LOCATIONS[location]}，查看院落边缘的互动点。使用探险者指南针，在建筑列表中搜索「{LOCATIONS[location]}」并开始搜索；已探索旧地没有这些互动点时寻找新的建筑。',
                            '&e&l如何完成&r',action,'完成现场行动会自动记录；不需要挖下或收集这个方块。现场给出的物品就是本次收获，任务页不重复发放。','&a&l下一步&r',after]
        elif item in WILDS:
            source,use=WILDS[item]
            description += ['&b&l去哪里&r',f'在主世界寻找{source}。自然指南针可查对应生物群系，敌人出现和材料掉落有概率，不保证到达即有。',
                            '&e&l如何完成&r',f'取得一份{node["title"]}并放入背包，等待自动记录；任务不收走物品。','&a&l采回来做什么&r',use]
        else:
            description += ['&e&l用途与操作&r',USE[item],'&b&l材料与制作&r']
            for r in sorted(recipes.get('dynasty:'+item,[]), key=lambda r: (not r['id'].startswith('cod4/'), r['id'])):
                parts=[f"{' 或 '.join(name(v) for v in k.split(' / '))}×{amount}" for k,amount in r['ingredients'].items()]
                description.append(' + '.join(parts)+f' → {node["title"]}×{r["output"]}。')
            description += ['如列出多条配方，任选一种；基础配方无需工匠图纸。背包中悬停成品按 R 查看配方摆放，按 U 查看用途。',
                '必须亲手合成一次，拾取或购买不计本项；合成后自动记录，不扣留成品。' if crafted else '取得成品后自动记录；任务不收走物品，也不要求消耗试用。']
        description += ['','&7这是主线途中的可选支线；完成后带着收获继续主线，无需清空全部支线。']
        for req in requirements:
            target=anchor(req[1:]) if req.startswith('@') else original[req]
            description.append(jump('准备 · '+target['title'],identity(req)))
        q=dict(id=node['id'],title=node['title'],display_title=node['title'],icon='{ id: "'+icon+'" }',
               kind='advancement',target='dynasty:'+node['advancement'],count=1,
               tasks='[{ id: "'+node['task']+'", type: "advancement", advancement: "dynasty:'+node['advancement']+'" }]',
               rewards='[]',purpose=USE.get(item,node['title']),how=description[2],deps=[identity(r) for r in requirements],
               role='cod4_branch',route='cod4',x=x,y=y,shape='circle' if interaction else 'square',
               subtitle=mode+' · '+CHAPTERS[chapter][0].split(' · ')[0],description=description,
               objective_title=mode+' · '+node['title'],cod4_item=item)
        made[chapter]['quests'].append(q)
    allnew={q['id']:q for c in made.values() for q in c['quests']}
    for q in allnew.values():
        children=[child for child in allnew.values() if q['id'] in child['deps']]
        for child in children:
            q['description'].append(jump('接着做 · '+child['title'],child['id']))
    # Restore the cover to navigation only; retain the existing optional craft identity.
    home=next(c for c in chapters if c['file']=='dynasty_home')
    infusion=next(q for q in home['quests'] if q['id']=='10000000000F1001')
    home['quests'].remove(infusion)
    infusion.update(x=3,y=2,role='cod4_branch',deps=[anchor('jade')['id']],objective_title='在炼入台完成一次炼入')
    infusion['description'].insert(0,jump('← 返回主线 · 玉',anchor('jade')['id']))
    made['workshop']['quests'].append(infusion)
    for key,c in made.items():
        origin=anchor(CHAPTERS[key][2])
        origin['description'].extend(['', '&a&l顺路可做&r',jump('支线 · '+c['title'],c['id']),c['goal']])
        home['quests'][0]['description'].append(jump(c['title'],c['id']))
    # Give players practical exits from their existing combat/equipment pages as well.
    for file,key in [('dynasty_build_guard','workshop'),('dynasty_build_archer','workshop'),('dynasty_story_03','supplies')]:
        c=next(c for c in chapters if c['file']==file)
        c['quests'][0]['description'].append(jump('出行准备 · '+made[key]['title'],made[key]['id']))
