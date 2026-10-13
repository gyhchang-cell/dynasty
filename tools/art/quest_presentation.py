"""Native FTB presentation only: never change completion/reward identities.

2001.4.22 MissingItem.readItem calls setCount(tag.getInt("Count")); an icon
compound without Count becomes empty, triggering the generic task fallback.
"""
import json
import re
from quest_snbt import list_compounds


def icon_stack(text):
    if text.lstrip().startswith('{') and re.search(r'\bid\s*:', text):
        if re.search(r'\bCount\s*:', text):
            return re.sub(r'\bCount\s*:\s*\d+b?', 'Count: 1b', text)
        return text.rstrip()[:-1].rstrip() + ', Count: 1b }'
    return text


def task_presentation(quest):
    text = quest['tasks']
    for block in list_compounds('\ttasks: ' + text, 'tasks'):
        # Backend-only advancements have neither a display icon nor readable name.
        if 'type: "advancement"' not in block:
            continue
        fields = ', icon: ' + icon_stack(quest['icon'])
        title = quest.get('objective_title', quest.get('display_title', quest['title']))
        fields += ', title: ' + json.dumps(title, ensure_ascii=False)
        text = text.replace(block, block[:-1].rstrip() + fields + ' }', 1)
    return text


def reward_presentation(quest):
    # Only display icons: item reward stack counts and completion IDs stay intact.
    return re.sub(r'\bicon:\s*(\{[^{}]*\})',
                  lambda match: 'icon: ' + icon_stack(match[1]), quest['rewards'])


# Chapter covers are deliberately independent of the first (often explanatory) quest.
CHAPTER_ICONS = {
    'dynasty_home':'minecraft:filled_map',
    'dynasty_story_01':'minecraft:campfire',
    'dynasty_story_02':'minecraft:smithing_table',
    'dynasty_story_03':'dynasty:exam_paper',
    'dynasty_story_04':'dynasty:jade_portal',
    'dynasty_story_05':'dynasty:underworld_portal',
    'dynasty_story_06':'dynasty:cloud_portal',
    'dynasty_story_07':'dynasty:dragon_gate',
    'dynasty_story_08':'dynasty:dragon_emperor_seal',
    'dynasty_boss_ascent':'dynasty:ritual_altar',
    'dynasty_c1':'dynasty:refined_steel',
    'dynasty_c2':'minecraft:bricks',
    'dynasty_c3':'dynasty:tang_dao',
    'dynasty_c4':'dynasty:bronze_chestplate',
    'dynasty_c5':'dynasty:official_seal',
    'dynasty_c6':'dynasty:tiger_tally',
    'dynasty_c7':'dynasty:dragon_crystal',
    'dynasty_c8':'dynasty:emperor_bone',
    'dynasty_c9':'dynasty:immortal_peach',
    'dynasty_c10':'dynasty:phoenix_hairpin',
    'dynasty_c12':'dynasty:sky_token',
    'dynasty_c13':'dynasty:sea_trident',
    'dynasty_legacy':'minecraft:clock',
    'dynasty_boss_guides':'minecraft:ender_eye',
    'dynasty_build_guard':'dynasty:zhenyue_blade',
    'dynasty_build_sword':'dynasty:liuyun_sword',
    'dynasty_build_archer':'dynasty:zhuxing_bow',
    'dynasty_build_talisman':'dynasty:chiling_brush',
    'dynasty_accessory_necklace':'dynasty:jade_pendant',
    'dynasty_accessory_ring':'dynasty:phoenix_ring',
    'dynasty_accessory_bracelet':'dynasty:zen_bead_string',
    'dynasty_accessory_hands':'dynasty:quickdraw_glove',
    'dynasty_accessory_body':'dynasty:moonlit_mirror',
    'dynasty_accessory_back':'dynasty:phoenix_wing_charm',
    'dynasty_accessory_belt':'dynasty:cavalry_sash',
    'dynasty_accessory_charm':'dynasty:bronze_mirror',
    'dynasty_cod4_workshop':'dynasty:qimen_gear',
    'dynasty_cod4_wilds':'dynasty:fox_pelt',
    'dynasty_cod4_supplies':'dynasty:army_ration',
    'dynasty_cod4_encounters':'minecraft:compass',
}
GENERIC_ICONS = {'dynasty:dynasty_manual','dynasty:dynasty_guide',
                 'minecraft:book','minecraft:knowledge_book','minecraft:iron_sword'}
ENEMY_ICONS = {
    'rebel_general':'dynasty:rebel_head', 'eunuch_mastermind':'dynasty:eunuch_token',
    'undead_first_emperor':'dynasty:emperor_bone', 'nine_heaven_general':'dynasty:sky_token',
    'dragon_king':'dynasty:sea_token', 'dragon_emperor':'dynasty:dragon_emperor_seal',
    'archer':'minecraft:bow', 'assassin':'dynasty:assassin_spawn_egg',
    'rebel_soldier':'dynasty:tong_dao', 'terracotta_warrior':'minecraft:terracotta',
    'soul_soldier':'minecraft:soul_lantern', 'thunder_envoy':'minecraft:lightning_rod',
    'merfolk':'minecraft:prismarine_shard', 'phoenix':'dynasty:phoenix_feather',
    'nine_tailed_fox':'dynasty:fox_tail_charm', 'nian_beast':'minecraft:firework_rocket',
    'qilin':'dynasty:qilin_horn_charm', 'royal_guard':'dynasty:tiger_tally',
    'imperial_soldier':'dynasty:bronze_chestplate','jade_guard':'dynasty:jade_chestplate',
    'zombie':'minecraft:rotten_flesh','skeleton':'minecraft:bone',
}
ADVANCEMENT_ICONS = {
    'exam_passed':'dynasty:exam_paper','keju':'dynasty:ink_stick',
    'army_led':'dynasty:tiger_tally','grand_marshal':'dynasty:tiger_tally',
    'entered_celestial':'dynasty:jade_portal','celestial_dynasty':'dynasty:jade_portal',
    'entered_underworld':'dynasty:underworld_portal','underworld':'dynasty:underworld_portal',
    'entered_jiuxiao':'dynasty:cloud_portal','entered_dragon_palace':'dynasty:dragon_gate',
    'slay_emperor':'dynasty:emperor_bone','slay_sky_general':'dynasty:sky_token',
    'slay_dragon_king':'dynasty:sea_token','slay_dragon_emperor':'dynasty:dragon_emperor_seal',
    'jade_sword':'dynasty:sword_jade','full_jade_armor':'dynasty:jade_chestplate',
    'dragon_crystal':'dynasty:dragon_crystal','met_minister':'dynasty:official_seal',
    'dynasty_root':'minecraft:campfire','rebellion_calmed':'minecraft:emerald',
    'qilin_friend':'dynasty:immortal_peach','beast_friend':'minecraft:saddle',
    'rank_official':'dynasty:official_seal','rank_scholar':'dynasty:exam_paper',
    'rank_hanlin':'dynasty:ink_stick','rank_minister':'dynasty:merit_badge',
    'rank_grand_secretary':'dynasty:mandarin_rank_badge','rank_chancellor':'dynasty:jade_ruyi',
    'rank_prince_regent':'dynasty:tiger_tally','rank_son_of_heaven':'dynasty:jade_crown',
    'story_slay_juma_changqiangbing':'dynasty:iron_spearhead',
    'cod4_old_weapon_rack':'dynasty:tie_jian',
}
TUTORIAL_ICONS = {
    '1000000000010000':'minecraft:campfire',
    '1000000000010006':'dynasty:bronze_chestplate',
    '1000000000010007':'dynasty:sea_pearl',
    '1000000000010008':'dynasty:dragon_emperor_seal',
    '1000000000010009':'minecraft:nether_star',
}


def themed_icon(quest, chapter):
    current = re.search(r'\bid:\s*"([^"]+)"', quest['icon'])[1]
    if current not in GENERIC_ICONS or quest['kind']=='item':
        return quest['icon']  # A real book/iron-sword collection goal still depicts that item.
    target=quest['target'].split(':')[-1]
    if quest['id'] in TUTORIAL_ICONS:
        item=TUTORIAL_ICONS[quest['id']]
    elif target in ENEMY_ICONS:
        item=ENEMY_ICONS[target]
    elif target in ADVANCEMENT_ICONS:
        item=ADVANCEMENT_ICONS[target]
    elif target.startswith(('build_', 'slot_')) or target=='home':
        item=CHAPTER_ICONS[chapter['file']]
    else:
        raise AssertionError('Choose a meaningful quest icon for '+quest['target'])
    return '{ id: "'+item+'" }'


def compact_description(quest):
    """Keep this objective's conditions, recipes and tips; remove repeated itinerary prose."""
    result=[]
    skip_paragraph=False
    for line in quest['description']:
        if line.startswith('{"'):
            label=json.loads(line).get('text','')
            if label.startswith(('← 山河总览','返回本槽位','行旅导航','接着做','准备 ·')):
                continue
            if quest.get('route')=='cod4' and label.startswith('← 返回主线'):
                continue
            # Keep the few chapter entrances and boss-specific help links.
            result.append(line)
            continue
        plain=re.sub(r'&[0-9a-fk-or]', '', line)
        if plain in {'为什么做','完成后去哪','下一步','战后回到路线'}:
            skip_paragraph=True
            continue
        if skip_paragraph:
            if not plain:
                continue
            if not line.startswith('&'):
                skip_paragraph=False
                continue
            skip_paragraph=False
        if plain.startswith(('下一步：','回到『主线旅程』','材料任务可查：',
            '材料、用途与获取方式见下方。','这是主线途中的可选支线；',
            '先看物品提示中的效果，再按生存、输出或探索需求搭配',
            '从凡间动乱追索四象之力，最后进入龙口镇渊仪式。')):
            continue
        if plain.startswith(('点击本页任务栏里的物品图标','如列出多条配方，任选一种；基础配方')):
            line='&8配方任选一种；悬停物品按 R 查看摆放。'
        elif plain.startswith('仅检测物品，不会收走；升级会消耗旧装备'):
            line='&8持有即可，不消耗物品。'
        elif plain.startswith('完成现场行动会自动记录；'):
            line='完成现场交互后自动记录。'
        elif plain.startswith('取得成品后自动记录；'):
            line='取得成品后自动记录，不消耗物品。'
        line=line.replace('&e&l现在怎么做&r','&e&l做法&r').replace('&6&l这一步要做什么&r','&6&l目标&r')
        # Remove an appended next-objective sentence, never the conditions of this one.
        line=re.sub(r'下一步[^。]*。','',line)
        if line and line in result:
            continue
        if line or (result and result[-1]):
            result.append(line)
    while result and not result[-1]:result.pop()
    return result


def apply_presentation(chapters):
    assert {c['file'] for c in chapters} == set(CHAPTER_ICONS), 'New chapter needs a deliberate cover'
    for chapter in chapters:
        chapter['icon']='{ id: "'+CHAPTER_ICONS[chapter['file']]+'" }'
        for quest in chapter['quests']:
            quest['icon']=themed_icon(quest,chapter)
            quest['description']=compact_description(quest)
