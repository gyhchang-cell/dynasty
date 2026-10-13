"""Short source and operation help, derived from the repository's actual data.

These tutorials are optional and rewardless. Reading them never stands in for
an item detector or an advancement, and never adds a gate to the main journey.
"""
import json
import re
from functools import lru_cache

NAMES = {'naturescompass:naturescompass':'自然指南针',
         'explorerscompass:explorerscompass':'探险者指南针',
         'minecraft:compass':'指南针',
         'minecraft:glass':'玻璃','minecraft:scute':'鳞甲',
         'minecraft:brewing_stand':'酿造台','minecraft:nether_wart':'下界疣',
         'minecraft:hay_block':'干草块','minecraft:zombie':'僵尸','minecraft:skeleton':'骷髅',
         'minecraft:ladder':'梯子','minecraft:bucket':'桶','minecraft:smoker':'烟熏炉',
         'minecraft:grindstone':'砂轮','minecraft:raw_iron':'粗铁','minecraft:map':'空地图',
         'minecraft:barrel':'木桶','minecraft:scaffolding':'脚手架',
         'minecraft:magma_block':'岩浆块','minecraft:sea_lantern':'海晶灯',
         'minecraft:writable_book':'书与笔',
         'minecraft:charcoal':'木炭','minecraft:poppy':'虞美人',
         'minecraft:glistering_melon_slice':'闪烁的西瓜片',
         'dynasty:celestial_dynasty':'天朝','dynasty:underworld':'幽冥',
         '#minecraft:logs':'原木'}
VANILLA_SOURCES = {
 'iron_ingot':'用石镐或更好的镐采铁矿，把粗铁放熔炉烧炼。',
 'copper_ingot':'用石镐或更好的镐采铜矿，把粗铜放熔炉烧炼。',
 'gold_ingot':'用铁镐或更好的镐采金矿，把粗金放熔炉烧炼。',
 'coal':'用镐采煤矿；木炭可作燃料，但不能替代配方中的煤炭。',
 'oak_planks':'砍橡树取得橡木原木，在合成栏分解为橡木木板。',
 'stick':'把两块木板竖排合成木棍。',
 'paper':'把三根甘蔗横排合成纸。',
 'ink_sac':'在河流或海中找鱿鱼，击败后拾取墨囊。',
 'bamboo':'在丛林寻找竹子，留一根种回营地。',
 'string':'击败蜘蛛取得线；在安全位置交战。',
 'sugar':'把甘蔗放入合成栏制成糖。',
 'wheat':'播种小麦种子，等作物成熟后收获。',
 'glass':'把沙子放入熔炉烧炼。',
 'glass_bottle':'三块玻璃在工作台摆成V形，制成玻璃瓶。',
 'leather':'牛、马等动物可掉皮革；狐皮也有转成皮革的配方。',
 'cobblestone':'用镐开采普通石头；不要使用精准采集。',
 'compass':'四块铁锭放上下左右，中央放红石粉，合成指南针。',
 'apple':'橡树或深色橡树的树叶有概率掉苹果。',
 'cooked_porkchop':'把生猪排放熔炉或烟熏炉烧熟。',
 'bone':'击败骷髅可取得骨头。',
 'feather':'鸡会掉普通羽毛；合成御风符用两根，不必寻找玄鸟神羽。',
 'scute':'幼龟长成成年龟时掉鳞甲；喂海龟海草繁殖，保护海龟蛋。',
 'ender_pearl':'击败末影人有概率掉落；先备好防具和安全退路。',
 'gunpowder':'击败苦力怕可取得火药，别让它爆炸。',
 'amethyst_shard':'寻找紫水晶洞，用镐采完全长成的紫水晶簇。',
 'glowstone_dust':'进入下界后采荧石；出发前备好回程。',
 'nautilus_shell':'钓鱼或击败持有鹦鹉螺壳的溺尸取得。',
 'book':'三张纸和一块皮革合成一本书。',
 'golden_apple':'八块金锭围住一个苹果，合成金苹果。',
}
MATERIAL_SOURCES = {
 'jade':'用铁镐开采主世界地下玉矿，取得玉。',
 'dragon_crystal':'用铁镐在主世界Y=-60至-5开采龙晶矿，取得龙晶。',
 'cinnabar':'主世界神庙、法阵遗迹或帝陵宝箱有概率出朱砂；没有朱砂矿。',
 'bronze_ingot':'铜锭×3＋铁锭×1，无序合成青铜锭×4。',
 'refined_steel':'铁锭×3＋朱砂×1，无序合成精钢×2；也可用蟹甲×1配铁锭×1取得精钢×1。',
 'emperor_bone':'亲自讨伐不死始皇或龙帝取得帝骸骨，普通骷髅不掉。',
 'phoenix_feather':'讨伐凤凰有概率取得凤凰羽。',
 'dragon_scale':'讨伐东海龙王取得龙鳞；先保障水下呼吸。',
 'sky_token':'讨伐九霄天将取得天将令。',
 'sea_token':'讨伐东海龙王取得此信物。',
 'dragon_emperor_seal':'讨伐龙帝取得龙帝印，先留一枚作复战信物。',
 'ancient_stele_rubbing':'带纸到官道驿站，按破损界碑的倒计时交互取得拓片。',
 'marble_block':'在主世界平原、草甸或热带草原找书院，带石镐采白色地面或石栏；直接掉汉白玉，无须精准采集。',
 'crimson_pillar':'书院围墙和廊下的红色立柱可采成朱红柱；用镐较快，无须精准采集。',
 'xuanniao_shenyu':'主世界白天，离出生点至少512格且累计击败100只敌对怪后，有机会遇到玄鸟止戈。进入天象64格内参与，天象开始约20秒后结算；15%取得神羽，非必出。',
}

# These are the existing Cod4 obtain/craft pages, not new checkmark objectives.
# Follow the current biome tags, loot, recipes and item-use implementations.
WILD_HELP = {
 'fox_pelt':('森林或山地的赤狐', '狐皮×1可换皮革×2；配丝绸和玉可做狐尾坠。'),
 'wolf_fang':('森林、山地或雪地的灰狼', '狼牙用于破甲矢、壮行酒和灰狼牙饰。普通狼不掉狼牙。'),
 'python_gall':('森林、山地、沼泽或丛林的巨蟒', '蟒蛇胆用于避毒丹、状元酒和御寒酒。'),
 'crab_shell':('河流、海洋或沼泽的蟹兵', '蟹甲配铁锭可制精钢，也用于重钢弩矢和蟹将甲饰。'),
 'kappa_scale':('河流、海洋或沼泽的河童', '河童鳞配末影珍珠、玉制避水珠；配面包、海带可制军粮。'),
 'sprite_jade':('森林、山地或洞穴的石精', '石精玉粒用于回春丹和聚气丹。'),
 'lantern_oil':('森林、山地、平原或沙漠夜间的灯笼鬼', '灯油用于安魂香和引路香。寻找敌对灯笼鬼，无须攻击打更人。'),
 'locust_dust':('沙漠、恶地或热带草原的蝗群', '蝗粉用于淬毒矢、毒烟弹，也有避毒丹配方。'),
}
COD4_OPERATIONS = {
 'qimen_gear':['机括用于连弩、鸳鸯钺和流星锤。'],
 'qimen_cable':['钢索用于绳镖、飞爪和流星锤；修复残破水车也要一条。'],
 'repeating_crossbow':[
    '背包带箭。按住右键蓄满后松手装填，再按住右键依次发射，最多装3发。',
    '普通箭也能装；专用弹药用连发弩矢，不能装重钢弩矢。'],
 'siege_crossbow':[
    '按住右键蓄满后松手装填，再按住右键发射，一次1发。普通箭或重钢弩矢均可，不能装连发弩矢。',
    '射击会后退，避开悬崖；升级配方会消耗连弩。'],
 'rope_dart':[
    '对准12格内的普通敌人右键，将敌人拉近并踉跄2秒；不能穿墙，Boss免疫牵引。'],
 'flying_claw':[
    '对准12格内方块右键，把自己拉向落点；对准普通敌人则把敌人拉近。',
    '不会穿墙；Boss免疫牵引。先在平地练习落点。'],
 'meteor_hammer':[
    '按住右键至少1秒后松开，横扫周围4格范围内可见敌人；普通敌人会被击退。'],
 'mandarin_duck_axe':[
    '副手放鸳鸯钺，主手持另一把钺或空手；按住右键面对来袭方向，减轻可被格挡的正面伤害。',
    '格挡后3秒内的一次近战命中获得反击加成；只持主手一把钺不能触发此格挡。'],
 'repeating_bolt':['连弩专用弹药；背包带上后给连弩蓄满装填，最多3发。不能装入重弩。'],
 'heavy_bolt':['重弩专用弹药，不能装入连弩。命中附带破甲；普通敌人4秒，Boss2秒。'],
 'poison_arrow':['用普通弓或王朝弓发射，命中可中毒的敌人后施加5秒中毒。'],
 'pierce_arrow':['用弓发射即可，无须先做弩。命中附带破甲；普通敌人4秒，Boss2秒。'],
 'thunder_arrow':['用弓发射，命中施加3秒阳雷；连续叠到第3层触发雷击。'],
 'army_ration':['恢复10点饥饿值，并获得10秒饱和。'],
 'regen_pill':['立即恢复最大生命的12%，并获得5秒生命恢复II。'],
 'qi_pill':['增加2点怒气，上限5点；聚气持续10秒，另施加5秒阳气。'],
 'antidote_pill':['解除中毒，并在30秒内持续清除中毒；不解除凋零。'],
 'zhuangyuan_wine':['饮用后60秒内开考，每题答题时间增加6秒；仍需自己选择答案。'],
 'marching_wine':['施加5秒阳气，同时反胃4秒；在安全位置饮用。'],
 'soul_incense':[
    '清除自身阴气、魂灼，让周围6格范围内亡灵丢失当前目标并后退。',
    '神龛祈福或鬼市小舟请船夫时，手持它右键现场互动点，不要先用掉。'],
 'guide_incense':['搜寻附近法阵遗迹，方向和距离提示持续60秒；换维度后失效，未找到时会提示。'],
 'silk_pouch':['取得后解锁锦囊槽；打开物品栏的Curios面板，把锦囊拖进锦囊槽。'],
 'jade_crown':['取得玉冠并达到官阶三阶才解锁玉冠槽；达到三阶也会授予一顶。'],
}
COD4_CONSUMABLES = {
 'army_ration','regen_pill','qi_pill','antidote_pill','zhuangyuan_wine',
 'marching_wine','soul_incense','guide_incense',
}

def cod4_help(q):
    """Keep actual item/craft detection distinct from optional practice/use."""
    item=q.get('cod4_item')
    if item not in WILD_HELP and item not in COD4_OPERATIONS:return
    label=display_name('dynasty:'+item)
    references=[s for s in q['description'] if s.startswith('{')]
    if item in WILD_HELP:
        source,use=WILD_HELP[item]
        q['description']=[f'&e取得{label}×1，放入背包；不收走物品。',
            f'主世界寻找{source}；击败后有概率掉落。自然指南针只定位群系。',use,*references]
        return
    recipes=[s.replace(' + ','＋') for s in q['description'] if '→' in s and '×' in s]
    crafted=item in COD4_CONSUMABLES
    q['description']=[f'&e亲手合成{label}×1；拾取或购买不计。' if crafted else f'&e取得{label}×1，背包持有即可。',
        *(['合成就记录，无须试用；按住右键直到用完会消耗一份并生效。'] if crafted else []),
        *COD4_OPERATIONS[item],*recipes[:1],*references]

def display_name(target):
    from quest_story import name
    return NAMES.get(target,name(target))

@lru_cache(maxsize=None)
def source_hint(target):
    from quest_story import recipe_index,loot_index
    from quest_cod4 import WILDS
    namespace,short=target.split(':',1)
    if namespace=='minecraft' and short in VANILLA_SOURCES:
        return VANILLA_SOURCES[short]
    if namespace=='dynasty' and short in MATERIAL_SOURCES:
        return MATERIAL_SOURCES[short]
    if namespace=='dynasty' and short in WILDS:
        return '主世界寻找'+WILDS[short][0]+'，掉落有概率。'
    # Prefer normal recipes to recoveries or alternate end-game conversions.
    recipes=recipe_index().get(target,[])
    if recipes:
        r=min(recipes,key=lambda r:(r['id'].startswith(('recover_','cod4/','branch_')),r['id']))
        parts=['或'.join(display_name(v) for v in k.split(' / '))+'×'+str(n)
               for k,n in r['ingredients'].items()]
        method='锻造台' if r['type']=='minecraft:smithing_transform' else '烧炼' if r['type'] in {'minecraft:smelting','minecraft:blasting'} else '合成'
        return method+'：'+'＋'.join(parts)+' → '+display_name(target)+'×'+str(r['output'])+'。'
    chests=[name for kind,name in loot_index().get(target,[]) if kind=='chests' and re.search('[\u4e00-\u9fff]',name)]
    if chests:return '探索'+ '、'.join(chests[:2])+'宝箱，有概率取得。'
    enemies=[name for kind,name in loot_index().get(target,[]) if kind=='entities']
    if enemies:return '来源：'+ '、'.join(dict.fromkeys(enemies))+'的掉落。'
    # Use the already-audited item's own event guide rather than invent a recipe.
    return '在物品用途页查看来源；没有核实配方的收藏不作为主线门槛。'

def item_requirements(tasks):
    """Read every inventory detector, including secondary items and quantities."""
    from quest_snbt import list_compounds
    amounts=[]
    for task in list_compounds('\ttasks: '+tasks,'tasks'):
        if not re.search(r'\btype:\s*"item"',task):continue
        item=re.search(r'\bitem:\s*\{[^}]*\bid:\s*"([^"]+)"',task)
        count=re.search(r'\bcount:\s*(\d+)L',task)
        if item and count:amounts.append((item[1],int(count[1])))
    return amounts

def simplify(q):
    from quest_journey import ASSET,clean
    lines=q['description'];target=q['target']
    # One short loot line avoids a wall of repetitive chest/entity names.
    sources=[s for s in lines if s.startswith(('探索宝箱：','可能掉落：'))]
    if sources:
        chests=[];enemies=[]
        for s in sources:
            label=s.split('：',1)[1].split('（',1)[0]
            if not re.search('[\u4e00-\u9fff]',label):continue
            (chests if s.startswith('探索') else enemies).append(label)
        hint=[]
        if chests:hint.append('宝箱：'+'、'.join(list(dict.fromkeys(chests))[:3]))
        # Optional sources need not invite attacks on friendly NPCs.
        enemies=[x for x in enemies if x not in {'麒麟','大臣','帝国士兵','锦衣卫'}]
        if enemies:hint.append('掉落：'+'、'.join(list(dict.fromkeys(enemies))[:2]))
        first=next(i for i,s in enumerate(lines) if s in sources)
        q['description']=[s for s in lines if s not in sources]
        if hint:q['description'].insert(first,'；'.join(hint)+'（概率取得）。')
    if target.startswith('guide:slot_'):
        slot=clean(q['title']).split(' · ')[0]
        refs=[s for s in q['description'] if s.startswith('{"')]
        q['description']=[f'打开物品栏的Curios面板，把饰品拖进{slot}槽或万能槽。',
            '佩戴才生效；先看悬浮说明的代价、昼夜、水下或残血条件。',
            '收藏节点只检测持有。这一页读完可勾选，无须收齐本区。',*refs,
            f'{{image:{ASSET}curios.png width:220 height:110 align:center fit:true}}']
    if re.fullmatch(r'dynasty:refine_[a-z]+_\d+',target):
        stage=target.rsplit('_',1)[1]
        important=[s for s in q['description'] if s.startswith('本段 ') or '额外伤害：' in s]
        q['description']=[f'&e持有或佩戴本流派淬炼达到+{stage}的饰品。',
            '铁砧左槽放一件饰品，右槽放当前材料；逐级取出结果。',
            *important,'经验按每次操作扣等级；材料不足时先做较低阶段。']
    if target in NAMES:
        for field in ('title','display_title'):
            q[field]=q.get(field,q['title']).replace(target,NAMES[target])
        q['description']=[s.replace(target,NAMES[target]).replace('#minecraft:logs','原木') for s in q['description']]
    if q.get('for_quest'):
        q['description']=[q['description'][0],source_hint(target)]
        q['source_hint']=True
        q['subtitle']='备料 · 持有一份即可'
    elif target in {'dynasty:marble_block','dynasty:crimson_pillar'}:
        q['description'].append(source_hint(target))
        q['description'].append(f'{{image:{ASSET}academy_materials.png width:220 height:110 align:center fit:true}}')
    if target=='dynasty:xuanniao_shenyu' and q.get('for_quest'):
        q.update(title='可选 · 玄鸟神羽',display_title='可选 · 玄鸟神羽',subtitle='吉兆事件 · 概率收藏')
        q['description'][0]='持有玄鸟神羽×1，可配符纸制成两张御风符。主线可用普通羽毛配方。'
    if target=='dynasty:wind_talisman':
        q['description']=[q['description'][0],
            '无序合成：符纸×1＋普通羽毛×2＋丝绸×1 → 御风符×1。',
            '右键使用：45秒缓降、速度III、跳跃提升II，并推开周围敌人；到期前回到安全平台。',
            f'{{image:{ASSET}wind_recipe.png width:220 height:110 align:center fit:true}}']
    if target=='dynasty:altar':
        from boss_quest_guides import jump
        q.update(title='祭坛 · 建筑装饰',display_title='祭坛 · 建筑装饰')
        q['description'].extend(['这是装饰祭坛；召唤Boss使用另一种“法阵·祭坛”。',
            jump('法阵祭坛 · 摆放与信物','1000000000020006')])
    # Cod6 changes the serialized detector to army_clear, while keeping the old
    # kind/target/save identity. Prose must follow that actual detector.
    army=re.search(r'advancement: "dynasty:army_clear_([a-z_]+)"',q['tasks'])
    if army:
        from boss_quest_guides import jump
        from quest_journey import ident
        boss=display_name('dynasty:'+army[1]);milestone=q['id']=='100000000000014b'
        q.update(title='军阵 · '+boss,display_title='军阵 · '+boss)
        q['description']=['&e完成'+boss+'军阵关卡。',
            '科举中第后，在募兵台用银币购兵。手持虎符选关卡，入场后编队、出阵，再点开战。',
            '开战至少部署1名士兵。关卡结算胜利才记录；野外击杀不算本节点，战损会保留。',
            jump('首领招式应对',ident('boss:'+army[1]+':应对')),
            f'{{image:{ASSET}army_stage.png width:220 height:110 align:center fit:true}}']
        if milestone:q['description'].insert(3,'首次领取本节点奖励：永久增加1个万能饰品槽。')
    # Keep stage effects and one actual smithing recipe; remove duplicate prose.
    if q.get('route') and q.get('subtitle')=='进阶饰品':
        from boss_quest_guides import jump
        from quest_journey import ident
        recipe=next((s for s in q['description'] if '→' in s),None)
        q['description']=[q['description'][0],q['purpose']+'。',
            '锻造台升级；佩戴才生效，保留淬炼、附魔和名称。',
            *([recipe] if recipe else []),
            jump('饰品淬炼操作',ident('refining:'+q['route']))]
    visits={
        'dynasty:story_visit_yunqi_manor':('进入主世界云栖庄园。',
            '用探险者指南针搜索云栖庄园，在新生成区块寻找。进入建筑范围自动记录，无须提交建筑材料。'),
        'dynasty:visit_ruined_battlefield':('进入主世界焦土古战场。',
            '用探险者指南针搜索焦土古战场，在新生成区块寻找。进入残营即可记录；夜间会有军兵，先留退路。'),
        'dynasty:story_visit_longque_sanctuary':('进入主世界龙阙。',
            '击败龙帝后，用探险者指南针搜索龙阙。进入巨龙头建筑范围自动记录；供台位于龙嘴内。'),
    }
    if target in visits:
        goal,details=visits[target]
        refs=[s for s in q['description'] if s.startswith('{"')]
        if target=='dynasty:story_visit_longque_sanctuary':
            for i,s in enumerate(refs):
                link=json.loads(s)
                if '青龙' in link.get('text',''):
                    link['text']='《四象试炼与讨伐》 · 青龙供台'
                    refs[i]=json.dumps(link,ensure_ascii=False)
        q['description']=['&e'+goal,details,*refs,
            f'{{image:{ASSET}compasses.png width:220 height:110 align:center fit:true}}']
    if target=='dynasty:dynasty_potion':
        q.update(title='王朝药水 · 旧藏记录',display_title='王朝药水 · 旧藏记录',subtitle='历史收藏 · 可跳过')
        q['description']=['旧版本药水的收藏记录。生存酿造请看“酿造入门”，此项不要求完成。']
    # Older optional advancements still have specific conditions; the detector
    # stays unchanged while the page explains the actual action instead of a
    # generic "look at the progress menu" placeholder.
    from boss_quest_guides import jump
    legacy={
        'dynasty:jade_sword':[
            '&e取得玉剑×1，放入背包。',
            '持有触发旧成就；不要求挥剑，也不收走玉剑。',
            jump('玉剑 · 材料与制作','1000000000000046')],
        'dynasty:full_jade_armor':[
            '&e同时持有玉盔、玉胸甲、玉护腿、玉靴各1件。',
            '四件放在背包一起检测；逐件做完可先留在箱中，集齐后一起取出。',
            *[jump(label,qid) for label,qid in [('玉盔','1000000000000098'),('玉胸甲','100000000000009e'),
                ('玉护腿','10000000000000a4'),('玉靴','10000000000000aa')]]],
        'dynasty:dragon_crystal':[
            '&e取得龙晶×1，放入背包。',source_hint('dynasty:dragon_crystal')],
        'dynasty:keju':[
            '&e取得原版书与笔×1，放入背包。',
            '书×1＋墨囊×1＋羽毛×1，无序合成书与笔。此项是旧科举收藏记录。',
            '正式科举另用科举试卷右键答题，答对一次才算中第。',
            jump('正式科举 · 答题中第','100000000000012a')],
        'dynasty:dynasty_root':[
            '&e取得铜钱×1，放入背包。',
            '这是旧版入门成就，不要求建营地；铜钱来源和换钱见货币节点。',
            jump('铜钱 · 来源与兑换','1000000000000012')],
        'dynasty:beast_friend':[
            '&e手持蟠桃右键麒麟。',
            '带一枚蟠桃寻找麒麟，喂食会消耗蟠桃；普通马匹与鞍不能替代。',
            jump('蟠桃 · 获取方式','100000000000016d')],
        'dynasty:grand_marshal':[
            '旧版军职记录，保留已有进度；此节点可跳过。',
            jump('调兵 · 当前可完成的操作','1000000000000147')],
        'dynasty:first_infusion':[
            '&e获得玉后，在炼入台成功确认一次炼入。',
            '入门示例：左槽放单件兵器，右槽放青铜锭×2；选空炼入位，点“炼入”。',
            '消耗两份材料和3级经验，示例占1容量；成品留在左槽，操作后取回。',
            f'{{image:{ASSET}infusion.png width:220 height:110 align:center fit:true}}'],
    }
    if target in legacy and re.search(r'\badvancement:\s*"'+re.escape(target)+'"',q['tasks']):
        q['description']=legacy[target]
    if target=='dynasty:grand_marshal':
        q.update(title='军职旧录 · 兵马大元帅',display_title='军职旧录 · 兵马大元帅',subtitle='历史记录 · 可跳过')
        q['unverified_trigger']=True
    if target=='dynasty:keju':
        q.update(title='旧科举记录 · 书与笔',display_title='旧科举记录 · 书与笔',subtitle='持有检测 · 正式科举另做')
    if target in {'dynasty:beast_friend','dynasty:dynasty_root'}:
        q['icon']='{ id: "'+('dynasty:immortal_peach' if target.endswith('beast_friend') else 'dynasty:copper_coin')+'" }'
    if target=='dynasty:army_led':
        q['description']=[s for s in q['description'] if not s.startswith('上：官道驿站；')]
    cod4_help(q)
    amounts=item_requirements(q['tasks'])
    if len(amounts)>1:
        # Every required item must be visible even when no quantity changed.
        # Keep recipes/use instructions, but replace the misleading single-item
        # headline and duplicate material list with short groups of three.
        details=[s for s in q['description'] if not s.startswith(('&e取得','同时准备：'))]
        labels=[display_name(item)+'×'+str(count) for item,count in amounts]
        q['description']=['&e同时备齐：']+['、'.join(labels[i:i+3])+'。' for i in range(0,len(labels),3)]+[
            '全部放在背包等待检测；不收走物品。',*details]
        q['journey_item_requirements']=amounts
        if q['title'].startswith('进化备料 '):
            title='进化备料 · '+'与'.join(display_name(item) for item,_ in amounts)
            q.update(title=title,display_title=title)
    # Known ingredient display names should not leak resource IDs into instructions.
    # Chinese letters also count as Unicode word characters: a word-boundary
    # before "取得minecraft:..." wrongly skipped those visible resource IDs.
    q['description']=[s if s.startswith('{') else re.sub(r'(?:dynasty|minecraft|naturescompass|explorerscompass):[a-z0-9_/]+',
        lambda m:display_name(m[0]),s) for s in q['description']]
    # Empty editorial headings and travel-next-step boilerplate are not objectives.
    q['description']=[s for s in q['description'] if clean(s) not in {'顺路可做','选择 Boss 查看地点与打法'}
                      and not s.startswith(('林地、河岸、矿洞与夜行四路','备军粮和锦囊；'))]
    q['description']=[s.replace('第 09 章四象镇渊','《四象试炼与讨伐》')
        .replace('第 09 章 · 从青龙贡品路线开始','四象试炼与讨伐 · 青龙路线') for s in q['description']]
    # Use the real serialized kill detector, not the editorial kind (army_clear
    # advancements also have kind=kill). Keep any remaining tactical prose.
    detector=re.search(r'type:\s*"kill"[^}]*entity:\s*"([^"]+)"[^}]*value:\s*(\d+)L',q['tasks'])
    friendly={'dynasty:royal_guard','dynasty:imperial_soldier','dynasty:jade_guard'}
    if detector and detector[1]==target and target not in friendly:
        count=int(detector[2]);enemy=display_name(target)
        for field in ('title','display_title'):
            q[field]=re.sub(r'[一二两三四五六七八九十\d]+(?=名|只)',str(count),q.get(field,q['title']))
        goal='击败'+enemy+'×'+str(count)+'。';out=[]
        for s in q['description']:
            if s.startswith('{'):
                out.append(s);continue
            s=re.sub(r'(击败'+re.escape(enemy)+r'×)\d+',lambda m:m[1]+str(count),s)
            if clean(s).strip()==goal:continue
            out.append(s)
        q['description']=['&e'+goal,*out]
    if q['id']=='1000000000030208':
        q.update(title='靶场准备 · 标靶×1',display_title='靶场准备 · 标靶×1',subtitle='持有检测 · 搭建可自由练习')

def add_operation_steps(chapters):
    from quest_journey import node,ASSET
    from boss_quest_guides import jump
    byfile={c['file']:c for c in chapters}
    c=byfile['dynasty_story_02']
    original=next(q for q in c['quests'] if q['id']=='100000000001000b')
    helpers=[]
    for key,target,title,description in [
      ('nature','naturescompass:naturescompass','自然指南针 · 找群系',[
        '工作台中央放指南针，上下左右各放一块原木，四角留空。',
        '合成后右键，选择群系并开始搜索；先进入目标维度。']),
      ('explorer','explorerscompass:explorerscompass','探险者指南针 · 找建筑',[
        '工作台中央放指南针，上下左右各放一块圆石，四角留空。',
        '合成后右键，选择建筑并开始搜索；找建筑不保证怪物立刻刷新。'])]:
        q=node('navigation:'+key,title,target,deps=list(original['deps']),description=[
            '&e取得并持有'+display_name(target)+'×1。',*description,
            f'{{image:{ASSET}compass_recipe.png width:220 height:110 align:center fit:true}}'])
        q['section']=c['file'];helpers.append(q)
    c['quests'].extend(helpers)
    original.update(title='两种罗盘 · 备齐导航',display_title='两种罗盘 · 备齐导航')
    original['description']=['&e同时持有自然指南针×1、探险者指南针×1。',
        '领取上一节点的两个指南针，按两种配方分别制作；不收走物品。',
        *[jump(q['title'],q['id']) for q in helpers],
        f'{{image:{ASSET}compasses.png width:220 height:110 align:center fit:true}}']
    workshop=byfile['dynasty_cod4_workshop']
    infusion=next(q for q in workshop['quests'] if q['target']=='dynasty:first_infusion')
    table=node('infusion:table','炼入入门 · 做一座炼入台','dynasty:infusion_table',
        deps=list(infusion['deps']),description=[
            '&e取得炼入台×1，背包持有即可。',
            '工作台上排：银锭、玉、银锭；中排：青铜锭、工作台、青铜锭；下排青铜锭×3。',
            '需要银锭×2、玉×1、青铜锭×5、工作台×1。放在营地，右键打开。',
            jump('银锭 · 来源与制作','100000000000013b'),
            jump('青铜锭 · 基础合金','1000000000000005'),
            f'{{image:{ASSET}infusion_table.png width:220 height:110 align:center fit:true}}'])
    table['section']=workshop['file'];table['journey_operation']='infusion_station'
    table['subtitle']='制作工位 · 持有检测';workshop['quests'].append(table)
    infusion['description'].append(jump('炼入台 · 制作与摆放',table['id']))
    table['description'].append(jump('首次炼入 · 兵器与青铜示例',infusion['id']))
    # A small writing lane supports the old writable-book inventory achievement.
    # It neither replaces the real exam nor adds a gate to any saved objective.
    school=byfile['dynasty_c5'];previous=None;writing=[]
    for key,target,title,details in [
        ('book','minecraft:book','书写备料 · 一本书',[
            '纸×3＋皮革×1，无序合成书×1。甘蔗制纸，牛等动物掉皮革。']),
        ('ink','minecraft:ink_sac','书写备料 · 墨囊',[
            source_hint('minecraft:ink_sac'),'普通墨囊用于书与笔；荧光墨囊不能替代。']),
        ('quill','minecraft:writable_book','书写入门 · 书与笔',[
            '书×1＋墨囊×1＋羽毛×1，无序合成书与笔。羽毛来自鸡。',
            '右键写字；签名后变成成书。先让持有任务记录，再决定是否签名。'])]:
        q=node('writing:'+key,title,target,deps=[previous] if previous else [],
            description=['&e取得'+display_name(target)+'×1，背包持有即可。',*details])
        q['section']=school['file'];q['journey_operation']='writing';q['subtitle']='书写支线 · 持有检测'
        writing.append(q);previous=q['id']
    writing[-1]['description'].append(f'{{image:{ASSET}writing_recipe.png width:220 height:110 align:center fit:true}}')
    school['quests'].extend(writing)
    keju=next(q for q in school['quests'] if q['target']=='dynasty:keju')
    keju['description'].extend([jump('书写备料 · 纸、皮革与墨囊',writing[0]['id']),
        f'{{image:{ASSET}writing_recipe.png width:220 height:110 align:center fit:true}}'])
    # A normal-material lane is easier than waiting for the rare celestial event.
    # Keep the existing main detector and the saved rare-feather detector intact.
    c=byfile['dynasty_story_06']
    wind=next(q for q in c['quests'] if q['id']=='1000000000010026')
    previous=None;materials=[]
    for key,target,title,details in [
        ('feather','minecraft:feather','御风备料 · 普通羽毛',[
            source_hint('minecraft:feather')]),
        ('silk','dynasty:silk','御风备料 · 丝绸',[
            '线×3合成生丝×1，生丝×3合成丝绸×1；从头制作需要线×9。']),
        ('paper','dynasty:talisman_paper','御风备料 · 符纸',[
            source_hint('dynasty:talisman_paper'),source_hint('dynasty:cinnabar')])]:
        q=node('wind-material:'+key,title,target,
            deps=[previous] if previous else list(wind['deps']),
            description=['&e取得'+display_name(target)+'×1，背包持有即可。',*details])
        q['section']=c['file'];q['subtitle']='普通配方 · 备料';q['journey_operation']='wind_material'
        materials.append(q);previous=q['id']
    c['quests'].extend(materials)
    wind['description'].extend([jump('普通材料 · 羽毛、丝绸、符纸',materials[0]['id']),
        jump('可选事件配方 · 玄鸟神羽','10d388e6188a3f8e')])
    # Teach the working vanilla base process with real item/NBT objectives.
    # Do not substitute a vanilla bottle for the saved legacy dynasty_potion ID.
    c=byfile['dynasty_c2'];previous=None;brewing=[]
    for key,target,title,details,potion in [
        ('stand','minecraft:brewing_stand','酿造入门 · 酿造台',[
            '工作台下排圆石×3，中间一根烈焰棒，合成酿造台。烈焰棒来自下界要塞的烈焰人。'],None),
        ('fuel','minecraft:blaze_powder','酿造入门 · 燃料',[
            '烈焰棒×1可分解成烈焰粉×2。把一份烈焰粉放酿造台左侧燃料槽。'],None),
        ('wart','minecraft:nether_wart','酿造入门 · 下界疣',[
            '在下界要塞的灵魂沙上收集下界疣。它是上方酿造材料，不是燃料。'],None),
        ('water','minecraft:potion','酿造入门 · 水瓶',[
            '用玻璃瓶右键水源装水。下方三个瓶槽放1瓶也能酿造，不必放满。'],'minecraft:water'),
        ('awkward','minecraft:potion','酿造入门 · 粗制药水',[
            '下方放水瓶，上方放下界疣，左侧有烈焰粉；等酿造完成，取出一瓶粗制的药水。',
            '本步检测粗制的药水，普通水瓶或其他药水不算。'],'minecraft:awkward'),
        ('melon','minecraft:glistering_melon_slice','救人备料 · 闪烁的西瓜片',[
            '工作台中央放西瓜片，周围放金粒×8；金锭×1可分解成金粒×9。',
            '在丛林找西瓜，或种西瓜收获西瓜片；这份材料放酿造台上格。'],None),
        ('healing','minecraft:potion','救人准备 · 普通治疗药水',[
            '酿造台下格放粗制的药水，上格放闪烁的西瓜片，左侧有烈焰粉；酿好后取出。',
            '义庄救人使用普通治疗药水；不要加荧石粉升级，强效治疗药水不符合该现场条件。',
            jump('义庄 · 带药水救流民','1000000000c40029')],'minecraft:healing')]:
        label={'water':'水瓶','awkward':'粗制的药水','healing':'普通治疗药水'}.get(key,display_name(target))
        q=node('brewing:'+key,title,target,deps=[previous] if previous else [],
            description=['&e取得'+label+'×1，背包持有即可。',*details])
        q['subtitle']='酿造支线 · 持有检测';q['section']=c['file'];q['journey_operation']='brewing'
        if potion:
            stack='{ id: "minecraft:potion", Count: 1b, tag: { Potion: "'+potion+'" } }'
            q['icon']=stack;q['journey_potion']=potion
            q['tasks']='[{ id: "2'+q['id'][1:]+'", type: "item", item: '+stack+', count: 1L, consume_items: false, match_nbt: true, weak_nbt_match: true }]'
        if key=='awkward':q['description'].append(f'{{image:{ASSET}brewing.png width:220 height:110 align:center fit:true}}')
        brewing.append(q);previous=q['id']
    c['quests'].extend(brewing)
    encounters=byfile['dynasty_cod4_encounters']
    rescue=next(q for q in encounters['quests'] if q.get('cod4_item')=='mortuary_room')
    rescue['description'].append(jump('治疗药水 · 实际酿造方法',brewing[-1]['id']))
    # Small inventory steps support actual site payments without adding a new
    # prerequisite to any deployed interaction or changing its advancement.
    for item,target,title,details in [
        ('broken_stele','minecraft:paper','拓印备料 · 一张纸',[
            '甘蔗×3横排合成纸×3；带一张到官道驿站界碑，主手拿纸再交互。']),
        ('nameless_tomb','minecraft:poppy','祭扫备料 · 一朵花',[
            '在平原等地采一朵虞美人，带到林间药庐的无名墓。现场也接受其他鲜花。']),
        ('old_bellows','minecraft:charcoal','风箱备料 · 木炭',[
            '熔炉上格放可烧的原木，下格放燃料，烧出木炭。现场要求木炭，煤炭不能替代。'])]:
        site=next(q for q in encounters['quests'] if q.get('cod4_item')==item)
        q=node('site-prep:'+item,title,target,deps=list(site['deps']),description=[
            '&e取得'+display_name(target)+'×1，背包持有即可；不收走物品。',
            *details,jump('现场 · '+site['title'],site['id'])])
        q['section']=encounters['file'];q['journey_operation']='site_preparation'
        q['subtitle']='现场备料 · 持有检测';q['journey_site']=item
        q['journey_site_parent']=site['id']
        encounters['quests'].append(q)
        site['description'].append(jump('备料 · '+display_name(target),q['id']))
    # Optional supporting lanes; saved water/target quests do not acquire new
    # gates. Every addition detects an actual inventory item and is rewardless.
    bottles=[];previous=None
    for key,target,title,details in [
        ('glass','minecraft:glass','制瓶备料 · 烧出玻璃',[
            '把沙子放熔炉上格，木炭等燃料放下格，等烧出玻璃。制作玻璃瓶总共需要玻璃×3。']),
        ('bottle','minecraft:glass_bottle','制瓶入门 · 空瓶',[
            '工作台上一行左右各放一块玻璃，下一行中央放一块，合成玻璃瓶×3。留一瓶装水即可。'])]:
        q=node('bottle-material:'+key,title,target,deps=[previous] if previous else [],
            description=['&e取得'+display_name(target)+'×1，背包持有即可。',*details])
        q['section']=c['file'];q['journey_operation']='bottle_material';q['subtitle']='酿造备料 · 持有检测'
        bottles.append(q);previous=q['id']
    bottles[-1]['description'].append(f'{{image:{ASSET}glass_bottle.png width:220 height:110 align:center fit:true}}')
    c['quests'].extend(bottles)
    water=next(q for q in brewing if q.get('journey_potion')=='minecraft:water')
    water['description'].extend([jump('玻璃瓶 · 熔炉与合成摆法',bottles[0]['id']),
        f'{{image:{ASSET}glass_bottle.png width:220 height:110 align:center fit:true}}'])
    archer=byfile['dynasty_build_archer'];previous=None;target_materials=[]
    for key,target,title,details in [
        ('wheat','minecraft:wheat','靶场备料 · 收第一束小麦',[
            '锄耕水边泥土，播小麦种子，成熟后收获。干草块需要小麦×9。']),
        ('hay','minecraft:hay_block','靶场备料 · 干草块',[
            '小麦×9无序合成干草块×1。村庄中现成的干草块也可以采集。']),
        ('redstone','minecraft:redstone','靶场备料 · 红石粉',[
            '用铁镐或更好的镐采地下红石矿。制作一个标靶需要红石粉×4，不必先造红石机器。'])]:
        q=node('target-material:'+key,title,target,deps=[previous] if previous else [],
            description=['&e取得'+display_name(target)+'×1，背包持有即可。',*details])
        q['section']=archer['file'];q['journey_operation']='target_material';q['subtitle']='靶场支线 · 采料练习'
        target_materials.append(q);previous=q['id']
    target_materials[1]['description'].append(f'{{image:{ASSET}target_recipe.png width:220 height:110 align:center fit:true}}')
    archer['quests'].extend(target_materials)
    target=next(q for q in archer['quests'] if q['id']=='1000000000030208')
    target['description']=['&e取得标靶×1，背包持有即可；不检测搭建或命中。',
        '工作台中央放干草块，上下左右各放红石粉，合成标靶×1。',
        '放在营地的安全位置练射，留出后方挡箭墙。此节点不要求击杀怪物。',
        jump('靶场采料 · 小麦、干草与红石',target_materials[0]['id']),
        f'{{image:{ASSET}target_recipe.png width:220 height:110 align:center fit:true}}']
    legacy=next(q for q in c['quests'] if q['target']=='dynasty:dynasty_potion')
    legacy['description'].append(jump('酿造入门 · 实际制作路线',brewing[0]['id']))
    for route in ('guard','sword','archer','talisman'):
        c=byfile['dynasty_build_'+route]
        q=node('refining:'+route,'饰品淬炼 · 铁砧操作','guide:refining:'+route,kind='checkmark',description=[
            '左槽放单件饰品，右槽放材料。每次取出结果升一级。',
            '当前0–9级用玉；10–24用龙晶；25–49用玄天玉；50级起用天将令。',
            '每次材料：1＋当前等级÷4向下取整，上限64；经验：2＋当前等级，上限39级。',
            '本页是阅读教程；各淬炼目标检测本流派饰品。佩戴才生效，锻造进化保留淬炼。',
            f'{{image:{ASSET}refining.png width:220 height:110 align:center fit:true}}'])
        q['icon']='{ id: "minecraft:anvil" }';q['section']=c['file']
        c['quests'].append(q)
        for old in c['quests']:
            if old['target'].startswith('dynasty:refine_'+route+'_'):
                old['description'].append(jump('铁砧操作与逐级材料',q['id']))

def quiet_long_connections(chapters):
    """Hover-reveal distant/obscured prerequisites with exact clickable links.

    FTB 1.20.1 QuestPanel.drawConnections preserves the real dependency graph
    while hide_dependency_lines limits default drawing. Main spine stays visible.
    """
    from quest_journey import clean
    from boss_quest_guides import jump
    from quest_layout_geometry import penetrates, visible_edges, crossings
    import math
    for c in chapters:
        local={q['id']:q for q in c['quests']}
        def reveal_on_hover(q, prerequisites, reason):
            q['hide_dependency_lines']=True
            existing={json.loads(s).get('clickEvent',{}).get('value')
                      for s in q['description'] if s.startswith('{"')}
            q['description'].extend(jump('前置 · '+clean(local[d]['title']),d)
                                    for d in q['deps'] if d in local and d not in existing)
            q['journey_distant_dependencies']=sorted(set(
                q.get('journey_distant_dependencies',[])+prerequisites))
            if reason:q[reason]=prerequisites
        for q in c['quests']:
            if q['role']=='main':continue
            distant=[d for d in q['deps'] if d in local and (
                local[d].get('section')!=q.get('section') or
                math.dist((local[d]['x'],local[d]['y']),(q['x'],q['y']))>12)]
            obscured=[d for d in q['deps'] if d in local and any(
                p['id'] not in (d,q['id']) and penetrates(local[d],q,p)
                for p in c['quests'])]
            if not distant and not obscured:continue
            reveal_on_hover(q,sorted(set(distant+obscured)),None)
            if obscured:q['journey_obscured_dependencies']=obscured
        # Keep short material lanes visible. Only the longer crossing connector
        # becomes contextual; all actual conditions and clickable targets survive.
        while crossed:=crossings(visible_edges(c)):
            a,b,d,e=crossed[0]
            candidates=[(local[x],local[y]) for x,y in ((a,b),(d,e))
                        if local[y]['role']!='main']
            if not candidates:break
            parent,child=max(candidates,key=lambda pair:math.dist(
                (pair[0]['x'],pair[0]['y']),(pair[1]['x'],pair[1]['y'])))
            reveal_on_hover(child,[parent['id']],'journey_crossed_dependencies')
