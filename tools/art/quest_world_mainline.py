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
        '前往主世界观星祭坛或林间药庐（star_altar / herbal_retreat），寻找护卫符法祭酒的两名卒伍刀手。先处理一名刀手，观察攻击前摇再反击；敌群受生成上限与冷却保护，不会无限增援。', 'dynasty:tong_dao')
    shield = quest(3, '侧击破盾 · 橹盾甲士', 'story_slay_ludun_jiashi',
        '前往主世界长城关隘或天工城（great_wall_gate / tiangong_citadel），寻找橹盾甲士；不要一直正面硬打，绕侧面并留意盾击。击败一名后再推进符法敌人的调查。', 'minecraft:shield')
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
    # Existing mainline IDs, rewards and gates stay intact. These are additional combat branches.
    encounters = [
        (6, '焦土寻旗 · 古战场', 'visit_ruined_battlefield', 'minecraft:black_banner',
         '用探险者指南针寻找主世界焦土古战场（dynasty:ruined_battlefield）。只在新生成区块出现；进入残营即可记录。夜间低光时生成一名掌旗官、一名祭酒、两名斥候和三名死士；最后一员被清理后，整组至少等待十分钟再生。', shield['id']),
        (7, '破枪阵 · 拒马长枪兵', 'story_slay_juma_changqiangbing', 'minecraft:iron_sword',
         '在长城关隘或天工城寻找盾甲士身后的拒马长枪兵。不要正面疾跑撞入枪阵，观察突刺后绕侧反击，亲自击败一名。', shield['id']),
        (8, '断箭雨 · 连弩阵卒', 'story_slay_liannu_zhenzu', 'minecraft:crossbow',
         '同一军事遗迹中有两名连弩阵卒。借掩体避开三连弩，注意翻滚留下的铁蒺藜，亲自击败一名。', shield['id']),
        (9, '避飞爪 · 铁索斥候', 'story_slay_tiesuo_chihou', 'minecraft:tripwire_hook',
         '夜间在主世界森林、山地（高度60～220）或焦土古战场寻找铁索斥候。躲开飞爪，别在其贴近时停留；亲自击败一名。', swords['id']),
        (10, '断引信 · 溃军死士', 'story_slay_kuijun_sishi', 'minecraft:gunpowder',
         '夜间进入焦土古战场。死士连续贴近三秒会自爆；拉开三格距离或利用遮挡打断引信，再亲自击败一名。远程击杀后仍须离开尸体，防备延迟的小范围爆炸。', code(1,0xA0006)),
        (11, '拔残旗 · 阵亡掌旗官', 'story_slay_zhenwang_zhangqiguan', 'minecraft:black_banner',
         '夜间古战场每组只有一名掌旗官。先识别军旗光环和横扫前摇，亲自击败掌旗官，削弱附近军兵。此支线不代替叛将或镇渊帝君的主线挑战。', code(1,0xA0006)),
    ]
    for column,(i,title,target,icon,how,dependency) in enumerate(encounters):
        q=node(0xA0000+i,title,'advancement','dynasty:'+target,'学习已有军兵的不同攻击与撤退窗口。',
               how+' 服务器保存探访或亲自击杀记录；提前完成也会记录。',xp=25,role='exploration_branch')
        q.update(subtitle='支线 · 军阵实战',icon='{ id: "'+icon+'" }',deps=[dependency],x=-4+column*2,y=-6.0)
        third['quests'].append(q)
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
