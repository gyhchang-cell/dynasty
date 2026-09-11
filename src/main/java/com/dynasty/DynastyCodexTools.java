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
        l.add(new DynastyCodex.Entry("quest_ledger", "合成：书 + 丝绸 + 竹简", "Craft: book + silk + bamboo slip",
                "右键打开任务界面（也可在背包左上角点「✦ 王朝任务」）。",
                "Right-click for quests (or the inventory button).",
                "minecraft:book", "dynasty:silk", "dynasty:bamboo_slip"));
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
                "符箓基材：与羽毛 / 煤炭 / 火药 / 末影珍珠等合成六种符。",
                "Talisman base for the six charms.",
                "minecraft:paper", "dynasty:cinnabar"));
        l.add(new DynastyCodex.Entry("wind_talisman", "合成：符纸 + 羽毛", "Craft: talisman paper + feather",
                "右键：速度 + 跳跃 + 缓降（40 秒）。", "Right-click: speed, jump, slow falling.",
                "dynasty:talisman_paper", "minecraft:feather"));
        l.add(new DynastyCodex.Entry("healing_talisman", "合成：符纸 + 朱砂 + 小麦",
                "Craft: paper + cinnabar + wheat",
                "右键：瞬间治疗 + 持续恢复。", "Right-click: instant heal + regeneration.",
                "dynasty:talisman_paper", "dynasty:cinnabar"));
        l.add(new DynastyCodex.Entry("thunder_talisman", "合成：符纸 + 火药", "Craft: paper + gunpowder",
                "右键：召来闪电（打 Boss 与群敌好用）。", "Right-click: calls lightning.",
                "dynasty:talisman_paper", "minecraft:gunpowder"));
        l.add(new DynastyCodex.Entry("fire_talisman", "合成：符纸 + 煤炭×2", "Craft: paper + 2 coal",
                "右键：掷出火球。", "Right-click: hurls a fireball.",
                "dynasty:talisman_paper", "minecraft:coal"));
        l.add(new DynastyCodex.Entry("return_talisman", "合成：符纸 + 末影珍珠", "Craft: paper + ender pearl",
                "右键：传送回世界出生点。", "Right-click: teleport to world spawn.",
                "dynasty:talisman_paper", "minecraft:ender_pearl"));
        l.add(new DynastyCodex.Entry("festival_lantern", "合成：纸×4 + 铜钱 + 火把",
                "Craft: 4 paper + coin + torch",
                "右键开启当令节日（春节/端午/中秋/重阳/除夕）。",
                "Right-click to start today's festival.",
                "minecraft:paper", "dynasty:gold_coin", "minecraft:torch"));
    }
}
