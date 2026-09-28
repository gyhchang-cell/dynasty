"""Additional smithing paths using fully implemented Dynasty weapons.

Keys are published recipe identities. Never reorder them into numeric IDs.
Vanilla smithing copies the entire base NBT, including growth and refinement.
"""
PATHS = {
    'guard': [
        ('pojun', 'juque_sword', 'pojun_axe', 'rebel_head', '破阵重斧'),
        ('juling', 'pojun_axe', 'juling_axe', 'emperor_bone', '巨灵重击'),
        ('leiting', 'juling_axe', 'leiting_hammer', 'sky_token', '雷霆重锤'),
    ],
    'sword': [
        ('seven_star', 'sword_dragon_crystal', 'seven_star_saber', 'jade', '七星刀锋'),
        ('dragon_slayer', 'seven_star_saber', 'dragon_slayer', 'sea_token', '屠龙刀锋'),
        ('supreme', 'dragon_slayer', 'supreme_sword', 'dragon_emperor_seal', '尚方御剑'),
    ],
    'archer': [
        ('luoyan', 'shenbi_bow', 'luoyan_bow', 'jade', '落雁强弓'),
        ('tianlang', 'luoyan_bow', 'tianlang_bow', 'dragon_crystal', '天狼穿透'),
        ('zhuque', 'tianlang_bow', 'zhuque_bow', 'phoenix_feather', '朱雀神弓'),
    ],
    'talisman': [
        ('zhuque_fan', 'taiyi_whisk', 'zhuque_fan', 'phoenix_feather', '朱雀羽扇'),
        ('hunyuan_fan', 'zhuque_fan', 'hunyuan_staff', 'dragon_emperor_seal', '混元归一'),
    ],
}

# Stable task offsets are keyed by recipe identity, not by list position.
QUEST_OFFSETS = {
    'pojun': 0xb0, 'juling': 0xb1, 'leiting': 0xb2,
    'seven_star': 0xb0, 'dragon_slayer': 0xb1, 'supreme': 0xb2,
    'luoyan': 0xb0, 'tianlang': 0xb1, 'zhuque': 0xb2,
    'zhuque_fan': 0xb0, 'hunyuan_fan': 0xb1,
}

def recipe_id(school, key):
    return f'evolution_path_{school}_{key}'

def generate_resources():
    from gen_school_branches import RES, smithing, write
    for school, paths in PATHS.items():
        for key, base, result, material, _ in paths:
            write(RES/f'data/dynasty/recipes/{recipe_id(school, key)}.json',
                  smithing(base, material, result))

if __name__ == '__main__':
    generate_resources()
