package com.dynasty;

import java.util.List;

/** 图鉴·随身物品 / codex: hand items (手册、科举、调兵、符箓、节日). */
final class DynastyCodexTools {

    private DynastyCodexTools() {
    }

    static void add(List<DynastyCodex.Entry> l) {
        l.add(new DynastyCodex.Entry("dynasty_manual", "开局自动赠送；合成：书 + 徽墨 + 竹简×2",
                "Given on first join; craft: book + ink stick + 2 bamboo slips",
                "右键阅读内置手册：开局流程、武器进化、饰品、图鉴导航。",
                "Right-click to read the handbook.",
                "minecraft:book", "dynasty:ink_stick", "dynasty:bamboo_slip"));
        l.add(new DynastyCodex.Entry("exam_paper", "合成：纸×3 + 徽墨 + 毛笔", "Craft: 3 paper + ink stick + brush",
                "右键答题，答对得功名；每 100 功名晋升一阶。",
                "Right-click to sit the exam; every 100 merit promotes you.",
                "minecraft:paper", "dynasty:ink_stick", "dynasty:ink_brush"));
        l.add(new DynastyCodex.Entry("tiger_tally", "合成：青铜锭×3 + 朱砂 + 铜钱",
                "Craft: 3 bronze ingots + cinnabar + coin",
                "右键调兵（阵型+人数）；潜行右键威慑周围生物。",
                "Right-click to summon troops; sneak-use to intimidate.",
                "dynasty:bronze_ingot", "dynasty:cinnabar", "dynasty:copper_coin"));
        l.add(new DynastyCodex.Entry("jade_seal", "合成：玉×2 + 金锭", "Craft: 2 jade + gold ingot",
                "右键查看王朝档案（官阶/功名/忠诚/叛乱）。",
                "Right-click for your dynasty records.",
                "dynasty:jade", "minecraft:gold_ingot"));
        l.add(new DynastyCodex.Entry("talisman_paper", "合成：纸 + 朱砂", "Craft: paper + cinnabar",
                "符箓基材：符箓都是一次性的，但每张都够猛（火符/雷符/摄魂符能秒一片）。",
                "Talisman base: every charm is single-use but very strong.",
                "minecraft:paper", "dynasty:cinnabar"));
        l.add(new DynastyCodex.Entry("fire_talisman", "合成：符纸 + 火药×2 + 朱砂",
                "Craft: paper + 2 gunpowder + cinnabar",
                "★ 爆炎：准星落点 4.5 格内造成 §c600 + 攻击×3§r 火焰伤害并点燃 8 秒。",
                "★ Blazing detonation: 600 + 3x attack fire damage in a 4.5 block radius, ignites 8s.",
                "dynasty:talisman_paper", "minecraft:gunpowder", "dynasty:cinnabar"));
        l.add(new DynastyCodex.Entry("thunder_talisman", "合成：符纸 + 火药×2 + 金锭 + 朱砂",
                "Craft: paper + 2 gunpowder + gold ingot + cinnabar",
                "★★ 天雷：三道落雷，5 格内 §b800 + 攻击×4§r 伤害，并给缓慢 II + 虚弱 II。",
                "★★ Triple lightning: 800 + 4x attack in 5 blocks, plus Slowness II and Weakness II.",
                "dynasty:talisman_paper", "minecraft:gunpowder", "minecraft:gold_ingot"));
        l.add(new DynastyCodex.Entry("wind_talisman", "合成：符纸 + 羽毛×2 + 丝绸",
                "Craft: paper + 2 feathers + silk",
                "★ 罡风：8 格内敌人 §f200 + 攻击×2§r 伤害并全部击飞；自己获得疾风 III + 缓降 45 秒。",
                "★ Gale: 200 + 2x attack and a knock-up for everything within 8 blocks; you get Speed III + slow falling.",
                "dynasty:talisman_paper", "minecraft:feather", "dynasty:silk"));
        l.add(new DynastyCodex.Entry("stealth_talisman", "合成：符纸 + 徽墨 + 煤炭 + 丝绸",
                "Craft: paper + ink stick + coal + silk",
                "★ 隐身：60 秒隐身 + 速度 II + 夜视，并清除 16 格内怪物对你的仇恨。",
                "★ Vanish: 60s invisibility with Speed II and night vision, and drops all aggro within 16 blocks.",
                "dynasty:talisman_paper", "dynasty:ink_stick", "dynasty:silk"));
        l.add(new DynastyCodex.Entry("vajra_talisman", "合成：符纸 + 金锭×2 + 朱砂",
                "Craft: paper + 2 gold ingots + cinnabar",
                "★ 金刚护体：抗性提升 III + 力量 II（15 秒）+ 抗火 60 秒（不回血，纯硬吃）。",
                "★ Adamant: Resistance III + Strength II for 15s and fire resistance for 60s.",
                "dynasty:talisman_paper", "minecraft:gold_ingot", "dynasty:cinnabar"));
        l.add(new DynastyCodex.Entry("soul_talisman", "合成：符纸 + 朱砂×2 + 徽墨",
                "Craft: paper + 2 cinnabar + ink stick",
                "★★ 摄魂：6 格内 §5 500 + 攻击×3§r 伤害，并施加失明 + 虚弱 II 8 秒。",
                "★★ Soul reave: 500 + 3x attack in 6 blocks with Blindness and Weakness II.",
                "dynasty:talisman_paper", "dynasty:cinnabar", "dynasty:ink_stick"));
        l.add(new DynastyCodex.Entry("return_talisman", "合成：符纸 + 末影珍珠",
                "Craft: paper + ender pearl",
                "右键：传送回世界出生点，并净化所有负面效果。",
                "Right-click: teleport to world spawn and cleanse all debuffs.",
                "dynasty:talisman_paper", "minecraft:ender_pearl"));
        l.add(new DynastyCodex.Entry("festival_lantern", "合成：纸×4 + 铜钱 + 火把",
                "Craft: 4 paper + coin + torch",
                "右键开启当令节日（春节/端午/中秋/重阳/除夕）。",
                "Right-click to start today's festival.",
                "minecraft:paper", "dynasty:gold_coin", "minecraft:torch"));
    }
}
