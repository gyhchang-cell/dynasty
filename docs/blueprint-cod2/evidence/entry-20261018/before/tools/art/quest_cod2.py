"""Optional Chensha exploration and authored elite kills; no unfinished boss gate."""


def garrison_advancements():
    return {
        f'defeat_chensha_{role}': {
            'criteria': {'kill': {
                'trigger': 'minecraft:player_killed_entity',
                'conditions': {'entity': {
                    'type': 'dynasty:'+entity,
                    'nbt': '{ForgeData:{ChenshaGarrison:{Hammer:'+flag+'}}}',
                }},
            }},
        }
        for role,entity,flag in [('jinwu','pilin_zhijinwu','0b'),('hammer','juchui_jinjia_lishi','1b')]
    }


def add_chensha(chapters):
    from boss_quest_guides import jump
    from quest_journey import node

    chapter = next(c for c in chapters if c['file'] == 'dynasty_c9')
    compass_id = '100000000001000b'
    visit = node('cod2:chensha:visit', '沉沙玄宫 · 遗址勘察',
                 'dynasty:visit_chensha_xuangong', kind='advancement',
                 deps=[compass_id], description=[
        '&e进入主世界的沉沙玄宫遗址范围，自动记录到访。',
        '主世界手持探险者指南针，搜索“沉沙玄宫”；也可输入 /dynasty_find chensha_xuangong。',
        '在远离世界出生点的荒漠、恶地寻找；遗址稀少，旧区块不会补建。一次搜索未找到时，先向未探索的荒漠前进再试。',
        '出发前带好镐、弓箭、食物和照明，在入口留好返程标记。先完成入口三处破封，再沿墓道下行。',
        '本任务只记录勘察。昭明帝挑战和帝王内棺奖励尚未开放，不计入主线通关条件。',
        jump('两种罗盘 · 备齐导航', compass_id),
    ])
    visit.update(role='exploration_branch', section=chapter['file'],
                 subtitle='到访记录 · 主世界', icon='{ id: "minecraft:chiseled_deepslate" }')
    guide = node('cod2:chensha:route', '玄宫探路 · 留好退路',
                 'guide:chensha:route', kind='checkmark', deps=[visit['id']], description=[
        '这是探路说明，阅读后可勾选；不发放通关奖励。',
        '上层留意地板预警和墙面弩孔。翻板坑东侧有返回上层的梯道；跌落后先找梯道。',
        '殉马井西壁另有维修梯，只返回神道。中层沿青铜吊桥中央通行，两侧链索接在锚座上；两处水渠北端有三级出水台阶。',
        '中层水银闸闭锁后，须在60秒内射中三枚兽眼。准备好弓箭再进入，重复命中同一枚不会增加进度。',
        '在中层瀑布后寻找裂纹青砖，用镐破开可进入工匠室。补给箱是共享的，高阶机关图纸用后会消耗。',
        '图纸×1、铁锭×4、铜锭×2、红石×1，可在工作台无序合成机关齿轮×8。',
        '到达底层后，用镐敲碎四角任意一座无字碑，永久开启返程吊篮；右键吊篮回到入口。它是单向回程。',
        jump('沉沙玄宫 · 遗址勘察', visit['id']),
    ])
    guide.update(role='exploration_branch', section=chapter['file'],
                 subtitle='可选阅读 · 机关与返程', icon='{ id: "minecraft:map" }')
    visit['description'].append(jump('玄宫探路 · 留好退路', guide['id']))
    jinwu=node('cod2:chensha:jinwu', '铜桥守卫 · 披鳞执金吾',
        'dynasty:dungeons/defeat_chensha_jinwu',kind='advancement',deps=[guide['id']],description=[
            '可选讨伐：击败沉沙玄宫中层北部、铜桥连接玄室内的披鳞执金吾。',
            '先完成入口三处破封。守卫体型宽大，在玄室内留足闪避空间，别把狭桥当作交战平台。',
            '本陵此守卫清除后不再补刷。只记录遗迹实际生成的守卫；其他地点同名精英不计入这条任务。',
            '此任务不发放帝王内棺奖励，不作为主线前置。',jump('玄宫探路 · 留好退路',guide['id']),
        ])
    hammer=node('cod2:chensha:hammer', '棺前镇卫 · 巨锤金甲力士',
        'dynasty:dungeons/defeat_chensha_hammer',kind='advancement',deps=[guide['id']],description=[
            '可选讨伐：击败沉沙玄宫主地宫龙台西侧的巨锤金甲力士。',
            '先完成入口破封和水银兽眼机关。进入底层后，留意龙台西侧的干燥前殿，避开外围水银渠。',
            '本陵此守卫清除后不再补刷。只记录遗迹实际生成的守卫；其他地点同名精英不计入这条任务。',
            '此任务不发放帝王内棺奖励，不作为主线前置。',jump('玄宫探路 · 留好退路',guide['id']),
        ])
    for quest,entity in [(jinwu,'pilin_zhijinwu'),(hammer,'juchui_jinjia_lishi')]:
        quest.update(role='exploration_branch',section=chapter['file'],subtitle='可选讨伐 · 本陵守卫',
                     icon='{ id: "dynasty:'+entity+'_spawn_egg" }')
        guide['description'].append(jump(quest['title'],quest['id']))
    chapter['quests'].extend([visit, guide, jinwu, hammer])
