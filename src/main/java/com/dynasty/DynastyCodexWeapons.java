package com.dynasty;

import java.util.List;

/** 图鉴·兵器与工具 / codex: weapons and tools（进化链）。 */
final class DynastyCodexWeapons {

    private DynastyCodexWeapons() {
    }

    static void add(List<DynastyCodex.Entry> l) {
        l.add(new DynastyCodex.Entry("sword_bronze", "合成：青铜锭 + 木棍", "Craft from bronze ingots + sticks",
                "攻击 1000。进化链起点，可一路升级上去。",
                "1000 damage. The first step of the evolution chain.",
                "dynasty:bronze_ingot", "minecraft:stick"));
        l.add(new DynastyCodex.Entry("tang_dao", "合成：青铜剑 + 青铜锭×2 + 丝绸",
                "Craft: bronze sword + 2 bronze ingots + silk",
                "攻击 1000，攻速 2.8 次/秒；命中后短时加速，连击流首选。",
                "1000 damage at 2.8 swings/s; hits grant a short speed boost.",
                "dynasty:sword_bronze", "dynasty:bronze_ingot", "dynasty:silk"));
        l.add(new DynastyCodex.Entry("huan_shou_dao", "合成：唐刀 + 青铜锭×3 + 铜钱×2",
                "Craft: Tang Dao + 3 bronze ingots + 2 coins",
                "攻击 1100。受击后获得力量 II —— 越被打越强。",
                "1100 damage. Taking a hit grants Strength II.",
                "dynasty:tang_dao", "dynasty:bronze_ingot", "dynasty:gold_coin"));
        l.add(new DynastyCodex.Entry("sword_silver", "合成：银锭 + 木棍", "Craft from silver ingots + sticks",
                "攻击 1200。官银铸剑，中庸可靠。",
                "1200 damage, reliable mid-tier blade.",
                "dynasty:silver_ingot", "minecraft:stick"));
        l.add(new DynastyCodex.Entry("chang_qiang", "合成：环首刀 + 银锭×3 + 竹简",
                "Craft: Huan Shou Dao + 3 silver ingots + bamboo slip",
                "攻击 1300，攻击距离 +3（可隔一格打到人），命中挑飞目标。",
                "1300 damage with +3 reach; hits launch the target upward.",
                "dynasty:huan_shou_dao", "dynasty:silver_ingot", "dynasty:bamboo_slip"));
        l.add(new DynastyCodex.Entry("yu_di", "合成：玉×3 + 竹简×2", "Craft: 3 jade + 2 bamboo slips",
                "攻击 1450。右键吹奏：8 格内敌人虚弱+缓慢，自身获得力量。",
                "1450 damage. Right-click: weakness + slowness in 8 blocks, strength for you.",
                "dynasty:jade", "dynasty:bamboo_slip"));
        l.add(new DynastyCodex.Entry("sword_jade", "合成：玉 + 木棍", "Craft from jade + sticks",
                "攻击 1500。附魔值 32，最适合叠附魔。",
                "1500 damage, enchantability 32.",
                "dynasty:jade", "minecraft:stick"));
        l.add(new DynastyCodex.Entry("juque_sword", "合成：玉剑 + 玉×3 + 青铜锭×2",
                "Craft: jade sword + 3 jade + 2 bronze ingots",
                "攻击 1700。重击：命中击退并施加缓慢 II。",
                "1700 damage. Heavy hits knock back and inflict Slowness II.",
                "dynasty:sword_jade", "dynasty:jade", "dynasty:bronze_ingot"));
        l.add(new DynastyCodex.Entry("pojun_axe", "合成：巨阙重剑 + 龙鳞×3 + 龙晶",
                "Craft: Juque + 3 dragon scales + dragon crystal",
                "攻击 1750。破甲：无视目标一半「士气减伤」，打 Boss 首选。",
                "1750 damage. Armour-piercing: ignores half of enemy toughness — the boss breaker.",
                "dynasty:juque_sword", "dynasty:dragon_scale", "dynasty:dragon_crystal"));
        l.add(new DynastyCodex.Entry("sword_dragon_crystal", "合成：龙晶 + 木棍", "Craft from dragon crystal + sticks",
                "攻击 1900。顶级附魔剑（附魔值 40）。",
                "1900 damage with enchantability 40.",
                "dynasty:dragon_crystal", "minecraft:stick"));
        l.add(new DynastyCodex.Entry("halberd_fangtian", "合成：龙晶 + 龙鳞 + 青铜锭",
                "Craft: dragon crystal + scales + bronze",
                "攻击 2048（原版上限）。横扫：命中时对 3 格内敌人造成 60% 伤害。",
                "2048 damage (the cap). Sweeps nearby enemies for 60% damage.",
                "dynasty:dragon_crystal", "dynasty:dragon_scale"));
        l.add(new DynastyCodex.Entry("dragon_bow", "合成：龙晶×2 + 丝绸×2 + 木棍×2",
                "Craft: 2 dragon crystal + 2 silk + 2 sticks",
                "远程：箭矢伤害约三倍（+50 基伤）、穿透 3、强击退，耐久 8000。",
                "Ranged: ~3x arrow damage (+50 base), pierce 3, heavy knockback.",
                "dynasty:dragon_crystal", "dynasty:silk", "minecraft:stick"));
        l.add(new DynastyCodex.Entry("pickaxe_jade", "合成：玉 + 木棍", "Craft from jade + sticks",
                "工具：挖掘速度 22、攻击 2000、耐久 45000。",
                "Tool: speed 22, 2000 damage, 45000 durability.",
                "dynasty:jade", "minecraft:stick"));
        l.add(new DynastyCodex.Entry("pickaxe_dragon_crystal", "合成：龙晶 + 木棍", "Craft from dragon crystal + sticks",
                "工具：挖掘速度 30、攻击 2048、耐久 120000。",
                "Tool: speed 30, 2048 damage, 120000 durability.",
                "dynasty:dragon_crystal", "minecraft:stick"));
    }
}
