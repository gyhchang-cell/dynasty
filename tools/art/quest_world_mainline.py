"""Additive world-story integration; never renumber existing tasks or rewards."""
from quest_routes import node, code, jump


def add_world_mainline(chapters):
    def quest(i, title, target, how, icon):
        q = node(0xA0000+i, title, 'advancement', 'dynasty:'+target,
                 '亲自探索王朝世界，把遗迹、敌人与四象终章联系起来。',
                 how+' 服务器保存探索/击杀进度；提前完成也会记录，任务解锁后自动检测。',
                 xp=25, role='main')
        q.update(subtitle='主线 · 实地探索与战斗', icon='{ id: "'+icon+'" }', world_story=True)
        return q

    manor = quest(0, '云栖访古 · 进入庄园', 'story_visit_yunqi_manor',
        '青铜装备准备好后，在主世界用探险者指南针寻找云栖庄园（dynasty:yunqi_manor），进入建筑范围。探索院落、屋顶与内饰，准备接下来的远征；不是提交方块，也不会强制改造你的院子。自然建筑请在新生成区块寻找；本版本 place 生成完成的庄园也会登记。旧版本未登记的手工复制建筑不会凭空判定。', 'minecraft:dark_oak_door')
    beast = quest(1, '山林试锋 · 山精山魈', 'story_slay_shanjing_shanxiao',
        '在主世界森林或山地（高度 50～240）寻找山精山魈，亲自击败一只。夜间更容易遇到；注意攀爬与扑击，先准备盾牌、照明和撤退路线。和平难度或关闭生物生成时不会自然出现。', 'dynasty:mu_mao')
    swords = quest(2, '破阵先锋 · 卒伍刀手', 'story_slay_zuwu_daoshou',
        '前往主世界长城关隘或天工城（great_wall_gate / tiangong_citadel），进入建筑寻找巡防敌人。先处理一名卒伍刀手，观察攻击前摇再反击；敌群受生成上限与冷却保护，不会无限增援。', 'dynasty:tong_dao')
    shield = quest(3, '侧击破盾 · 橹盾甲士', 'story_slay_ludun_jiashi',
        '同一类军事遗迹里寻找橹盾甲士；不要一直正面硬打，绕侧面并留意盾击。击败一名后再推进符法敌人的调查。', 'minecraft:shield')
    priest = quest(4, '断符寻源 · 符法祭酒', 'story_slay_fufa_jijiu',
        '用探险者指南针寻找主世界观星祭坛或草庐（star_altar / herbal_retreat），进入建筑寻找符法祭酒。躲开符弹并打断施法，击败一名，再按旧主线挑战叛将。怪物需要非和平难度并开启生物生成。', 'dynasty:talisman_pouch')
    dragon = quest(5, '龙阙寻源 · 深入巨龙遗迹', 'story_visit_longque_sanctuary',
        '击败龙帝后回到主世界，用探险者指南针寻找龙阙（dynasty:longque_sanctuary），进入巨型龙头建筑范围。找到龙嘴内供台，接下来打开第 09 章四象镇渊；朱雀羽、玄武壳等仍按现有供台真实归位，不是交任务扣物品。自然生成和本版本完成的 place 均可检测。', 'dynasty:zhenyuan_node')
    # Insert only after side branches have bound their stable anchors.
    second, third, eighth = [next(c for c in chapters if c['file']==f'dynasty_story_{i:02}') for i in (2,3,8)]
    def insert_before_branches(c, rows):
        n = next((i for i,q in enumerate(c['quests']) if q['role']!='main'),len(c['quests']))
        c['quests'][n:n] = rows
    insert_before_branches(second,[manor,beast])
    n = next(i for i,q in enumerate(third['quests']) if q['kind']=='kill' and q['target']=='dynasty:rebel_general')
    third['quests'][n:n] = [swords,shield,priest]
    insert_before_branches(eighth,[dragon])
    eighth['goal']='击败龙帝后深入龙阙，继续第 09 章四象镇渊；毕业配装仍可自由选择。'
    previous=None
    spine=[q for c in chapters if c['main'] for q in c['quests'] if q['role']=='main']
    for i,q in enumerate(spine):
        q['deps']=[] if previous is None else [previous['id']]
        previous=q
        marker='&a&l完成后去哪&r'
        if marker in q['description']:
            q['description']=q['description'][:q['description'].index(marker)]
        q['description'] += ['',marker,'下一步：'+(spine[i+1]['title'] if i+1<len(spine) else '第 09 章 · 四象镇渊，完成四象归位和最终献祭')+'。']
        if q['title']=='你来决定毕业流派':
            q['description'][1]='龙帝战后自由选择毕业配装；主线继续前往龙阙，完成四象终章。'
    for c in chapters:
        if c in (second,third,eighth):
            rows=[q for q in c['quests'] if q['role']=='main']
            for i,q in enumerate(rows):
                q.update(x=(i-(len(rows)-1)/2)*1.5,y=0.0)
    ascent=next(c for c in chapters if c['file']=='dynasty_boss_ascent')
    ascent.update(title='09 · 四象镇渊 · 主线终章',goal='承接龙帝与龙阙探索；四象真实归位 → 中央献祭 → 镇渊战场 → 归来奖励箱。')
    # Preserve old boss tasks/rewards as optional records. The main spine already
    # proves those kills: requiring their second counter would force repeat fights.
    byid={q['id']:q for q in ascent['quests']}
    for q in ascent['quests']:
        if q['id'] in {code(1,0x90000+i) for i in (10,20,30,40)}:
            q['deps']=[dragon['id']]
            q['world_story_gate']=dragon['id']
    for base in (10,20,40):
        byid[code(1,0x90000+base+2)]['deps']=[code(1,0x90000+base)]
    for i in (0,1,2,3,11,21,41):
        q=byid[code(1,0x90000+i)]
        q['subtitle']='保留旧记录 · 不要求为终章再战'
        q['description'].insert(0,'此节点保留旧进度与奖励；当前主线已验证相关讨伐，不必再次完成本节点来解锁贡品路线。')
    dragon['description'].append(jump('→ 第 09 章 · 从青龙贡品路线开始',code(1,0x9000A)))
