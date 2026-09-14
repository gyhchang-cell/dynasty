package com.dynasty;

import java.util.List;

/** 图鉴·饰品 / codex: accessories. */
final class DynastyCodexItems {

    private DynastyCodexItems() {
    }

    static void add(List<DynastyCodex.Entry> l) {
        l.add(new DynastyCodex.Entry("jade_pendant", "合成：玉×2 + 丝绸", "Craft: 2 jade + silk",
                "饰品：额外 8% 减伤，可与盔甲套装减伤叠加；放进 Curios 的饰品槽即生效。",
                "Trinket: extra 8% damage reduction, stacks with the armor set bonus.",
                "dynasty:jade", "dynasty:silk"));
        l.add(new DynastyCodex.Entry("jade_bi_disc", "合成：玉×3 + 金锭", "Craft: 3 jade + gold ingot",
                "最大生命 +150。", "+150 max health.",
                "dynasty:jade", "minecraft:gold_ingot"));
        l.add(new DynastyCodex.Entry("gold_seal_charm", "合成：铜钱×4 + 官印 + 丝绸",
                "Craft: 4 coins + official seal + silk",
                "功名获取 +25%，并每秒恢复忠诚 —— 升官更快。",
                "+25% merit gain and passive loyalty.",
                "dynasty:gold_coin", "dynasty:official_seal", "dynasty:silk"));
        l.add(new DynastyCodex.Entry("dragon_scale_charm", "合成：龙鳞×2 + 丝绸", "Craft: 2 dragon scales + silk",
                "护甲 +12、抗击退 +0.4。", "+12 armor and +0.4 knockback resistance.",
                "dynasty:dragon_scale", "dynasty:silk"));
        l.add(new DynastyCodex.Entry("phoenix_feather_charm", "合成：凤凰羽 + 丝绸 + 铜钱",
                "Craft: phoenix feather + silk + coin",
                "移动速度 +10% 且持续缓降，跳崖不摔伤。",
                "+10% speed and permanent slow falling.",
                "dynasty:phoenix_feather", "dynasty:silk"));
        l.add(new DynastyCodex.Entry("qilin_horn_charm", "合成：麒麟角 + 丝绸 + 玉",
                "Craft: qilin horn + silk + jade",
                "幸运 +3 且持续生命恢复，麒麟等祥瑞更亲近你。",
                "+3 luck and regeneration.",
                "dynasty:qilin_horn", "dynasty:silk", "dynasty:jade"));
        l.add(new DynastyCodex.Entry("fox_tail_charm", "合成：狐尾 + 丝绸 + 玉", "Craft: fox tail + silk + jade",
                "跳跃提升 II、移速 +5%，翻墙越脊如狐。",
                "Jump Boost II and +5% speed.",
                "dynasty:fox_tail", "dynasty:silk", "dynasty:jade"));
        l.add(new DynastyCodex.Entry("silk_pouch", "合成：丝绸×3 + 线", "Craft: 3 silk + string",
                "水下呼吸 + 夜视，探地府与矿井最实用。",
                "Water breathing and night vision.",
                "dynasty:silk", "minecraft:string"));
        l.add(new DynastyCodex.Entry("south_pointing_compass", "合成：铜镜 + 青铜锭×2 + 红石",
                "Craft: bronze mirror + 2 bronze ingots + redstone",
                "抗性提升，并在屏幕左上角显示当前坐标。",
                "Resistance I and shows your coordinates on the HUD.",
                "dynasty:bronze_mirror", "dynasty:bronze_ingot", "minecraft:redstone"));
        l.add(new DynastyCodex.Entry("bronze_mirror", "合成：青铜锭×3 + 玻璃", "Craft: 3 bronze ingots + glass",
                "饰品：每 30 秒自动净化一个负面效果。",
                "Accessory: cleanses one debuff every 30 seconds.",
                "dynasty:bronze_ingot", "minecraft:glass"));
    }
}
