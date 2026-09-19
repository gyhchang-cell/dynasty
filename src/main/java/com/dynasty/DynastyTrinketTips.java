package com.dynasty;

import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;

import java.util.List;
import java.util.Map;

/**
 * 饰品悬浮说明的**唯一来源**（第三十四轮）。
 *
 * 分两类：
 * 1) 表驱动饰品（`DynastyTrinkets.EXTRA_TABLE` 里的 130 件）：说明由那一行的
 *    属性 / 效果 / 条件自动拼出来，编码怎么改就怎么显示 —— 见 {@link Charm#Charm(Object[])}；
 * 2) 早期手写的 39 件（38 件 {@code charm(...)} + 铜镜）：效果写在 `DynastyTrinkets.apply()`
 *    的 switch 里，没法自动推导，所以在这里手工维护一张 {@link #LEGACY} 表。
 *
 * 加新编码时记得同步 {@code attrText} / {@code effectName} 两个 switch；新增手写饰品时补 LEGACY，
 * 否则它会在背包里「什么都不显示」（`tools/art/verify_gear.py` 会查这两件事）。
 *
 * Single source of truth for accessory tooltips: table-driven accessories build their lines from
 * the table row, the 39 hand-written ones read the LEGACY map.
 */
public final class DynastyTrinketTips {

    /** 条件名 / condition names */
    private static final String[] CONDITION_TEXT = {
            "常驻", "白天", "夜晚", "水下", "残血", "骑乘", "满血", "雷雨"};

    private static final String[] ROMAN = {"I", "II", "III", "IV", "V"};

    /** 手写饰品的说明（措辞以代码里的实际效果为准，任务书里是另一套展示文案）*/
    private static final Map<String, String[]> LEGACY = Map.ofEntries(
            Map.entry("jade_pendant", new String[]{"§7减伤 §f8%"}),
            Map.entry("jade_bi_disc", new String[]{"§7生命 §f+150"}),
            Map.entry("gold_seal_charm", new String[]{"§7功名 §f+25%", "§7每 30 秒 §f+2 忠诚度"}),
            Map.entry("dragon_scale_charm", new String[]{"§7护甲 §f+12 §8· §f抗击退 +0.4"}),
            Map.entry("phoenix_feather_charm", new String[]{"§7移速 §f+10% §8· §f常驻缓降"}),
            Map.entry("qilin_horn_charm", new String[]{"§7攻击 §f+10% §8· §f护甲 +4 §8· §f常驻再生"}),
            Map.entry("fox_tail_charm", new String[]{"§7跳跃提升 II §8· §f移速 +5%"}),
            Map.entry("silk_pouch", new String[]{"§7常驻夜视 §8· §f水下呼吸"}),
            Map.entry("south_pointing_compass", new String[]{"§7常驻抗性提升"}),
            Map.entry("heart_mirror", new String[]{"§7护甲 §f+8 §8· §f额外减伤 4%"}),
            Map.entry("jade_crown", new String[]{"§7生命 §f+220"}),
            Map.entry("jade_cicada", new String[]{"§7残血（<30%）时 §f抗性 II + 迅捷"}),
            Map.entry("dragon_pearl", new String[]{"§7攻击 §f+25% §8· §f抗击退 +0.3"}),
            Map.entry("phoenix_ring", new String[]{"§7常驻抗火 §8· §f移速 +3%", "§7着火时 §f立刻灭火并加速"}),
            Map.entry("storm_charm", new String[]{"§7常驻抗性", "§7雷雨天 §f额外力量 II + 迅捷"}),
            Map.entry("moon_pendant", new String[]{"§7夜晚 §f夜视 §8· §f攻击 +10% §8· §f攻速 +10%"}),
            Map.entry("tiger_crest", new String[]{"§7每 40 秒 §f威压 8 格内敌人，让他们放弃锁定你"}),
            Map.entry("jade_tortoise", new String[]{"§7水下呼吸 §8· §f海豚的恩惠 §8· §f抗性"}),
            Map.entry("war_drum_charm", new String[]{"§7常驻力量 I", "§7每秒 §f给 12 格内友军力量"}),
            Map.entry("cinnabar_pouch", new String[]{"§7每 2 秒 §f驱散中毒 / 凋零 / 失明 / 饥饿"}),
            Map.entry("dragon_whisker", new String[]{"§7攻速 §f+15% §8· §f击退 +0.5"}),
            Map.entry("tiger_token", new String[]{"§7移速 §f+8% §8· §f跳跃提升"}),
            Map.entry("sun_feather", new String[]{"§7白天 §f攻击 +15% §8· §f击退 +0.3", "§7夜晚 §f抗性"}),
            Map.entry("war_horse_bell", new String[]{"§7骑乘时 §f坐骑迅捷 II + 抗性", "§7步行时 §f护甲 +5"}),
            Map.entry("iron_waist_token", new String[]{"§7生命 §f+150 §8· §f护甲 +6 §8· §f抗击退 +0.2"}),
            Map.entry("auspicious_bell", new String[]{"§7攻速 §f+10%", "§7每 20 秒 §f驱散虚弱与缓慢"}),
            Map.entry("sea_pearl", new String[]{"§7水下呼吸 §8· §f海豚的恩惠", "§7水下 §f攻击 +20% §8· §f护甲 +6"}),
            Map.entry("dragon_bone_ring", new String[]{"§7护甲 §f+10 §8· §f抗击退 +0.3 §8· §f攻击 +8%"}),
            Map.entry("bronze_mirror", new String[]{"§7每 30 秒 §f自动净化一个负面效果"}),
            Map.entry("cloud_brocade", new String[]{"§7生命 §f+160 §8· §f护甲 +8"}),
            Map.entry("star_compass", new String[]{"§7攻击 §f+12% §8· §f移速 +6%"}),
            Map.entry("dragon_king_scale", new String[]{"§7攻击 §f+20% §8· §f抗击退 +0.5 §8· §f护甲 +6"}),
            Map.entry("sky_feather", new String[]{"§7跳跃提升 II §8· §f移速 +8%"}),
            Map.entry("imperial_seal_charm", new String[]{"§7功名 §f+40%", "§7生命 §f+100 §8· §f护甲 +4"}),
            Map.entry("tomb_candle", new String[]{"§7常驻夜视", "§7每 2 秒 §f清除凋零"}),
            Map.entry("inkstone", new String[]{"§7攻速 §f+12% §8· §f攻击 +6%"}),
            Map.entry("bamboo_flute", new String[]{"§7每 5 秒 §f让 8 格内敌人缓慢"}),
            Map.entry("merit_badge", new String[]{"§7生命 §f+200 §8· §f抗击退 +0.3"}),
            Map.entry("sea_conch", new String[]{"§7水下呼吸", "§7水下 §f攻击 +30% §8· §f护甲 +10"}));

    private DynastyTrinketTips() {
    }

    /** 手写饰品的说明行（没有就返回空数组）/ tooltip lines of a hand-written accessory */
    public static String[] legacy(String id) {
        return LEGACY.getOrDefault(id, new String[0]);
    }

    public static java.util.Set<String> legacyIds() {
        return LEGACY.keySet();
    }

    /**
     * 带说明的饰品物品：表驱动饰品传那一行，手写饰品传自己的 id。
     * Accessory item that renders its tooltip: pass the table row, or the id for legacy ones.
     */
    public static final class Charm extends Item {
        private final Object[] row;
        private final String id;

        /** 表驱动（EXTRA_TABLE 的一行）/ table-driven */
        public Charm(Object[] row) {
            super(new Item.Properties().stacksTo(1));
            this.row = row;
            this.id = (String) row[0];
        }

        /** 手写饰品：只按 id 查 LEGACY / hand-written accessory */
        public Charm(String id) {
            super(new Item.Properties().stacksTo(1));
            this.row = null;
            this.id = id;
        }

        @Override
        public void appendHoverText(ItemStack stack, Level level, List<Component> lines, TooltipFlag flag) {
            super.appendHoverText(stack, level, lines, flag);
            if (row == null) {
                for (String line : legacy(id)) {
                    lines.add(Component.literal(line));
                }
                return;
            }
            String first = attributeLine((Integer) row[7], (Integer) row[1], (Double) row[2],
                    (Integer) row[3], (Double) row[4]);
            if (!first.isEmpty()) {
                lines.add(Component.literal(first));
            }
            if (row.length > 10) {
                String third = attributeLine((Integer) row[10], (Integer) row[8], (Double) row[9],
                        -1, 0D);
                if (!third.isEmpty()) {
                    lines.add(Component.literal(third));
                }
            }
            String effect = effectName((Integer) row[5], (Integer) row[6]);
            if (effect != null) {
                lines.add(Component.literal("§7效果：§d" + effect));
            }
            // 第 12~14 格：命中触发（吸血 / 斩杀 / 会心 / 突袭 / 连击 / 雷罚）
            if (row.length > 13) {
                String proc = onHitName((Integer) row[11], (Double) row[12], (Integer) row[13]);
                if (proc != null) {
                    lines.add(Component.literal("§7命中时：§c" + proc));
                }
            }
        }
    }

    /** 同一条件的一行属性：`§7[白天] §f攻击 +22% §8· §f移速 +10%` */
    private static String attributeLine(int condition, int code1, double value1, int code2, double value2) {
        List<String> parts = new java.util.ArrayList<>();
        String a = attrText(code1, value1);
        if (a != null) {
            parts.add(a);
        }
        String b = attrText(code2, value2);
        if (b != null) {
            parts.add(b);
        }
        if (parts.isEmpty()) {
            return "";
        }
        return "§7[" + conditionText(condition) + "] §f" + String.join(" §8· §f", parts);
    }

    private static String conditionText(int condition) {
        return condition >= 0 && condition < CONDITION_TEXT.length
                ? CONDITION_TEXT[condition] : CONDITION_TEXT[0];
    }

    /** 属性编码 → 文案（加新编码时这里也要加一行）/ attribute code to text */
    private static String attrText(int code, double value) {
        return switch (code) {
            case 0 -> "生命 " + number(value);
            case 1 -> "护甲 " + number(value);
            case 2 -> "抗击退 " + number(value);
            case 3 -> "移速 " + percent(value);
            case 4 -> "攻击 " + percent(value);
            case 5 -> "攻速 " + percent(value);
            case 6 -> "击退 " + number(value);
            case 7 -> "攻击距离 " + number(value);
            case 9 -> "生命上限 " + percent(value);
            case 11 -> "幸运 " + number(value);
            default -> null;                                   // -1 = 这一格没有属性
        };
    }

    private static String percent(double value) {
        return number(value * 100) + "%";
    }

    /** 带正号的紧凑数字（+240 / -160 / +22%），不带多余小数 */
    private static String number(double value) {
        String text = String.format(java.util.Locale.ROOT, "%.1f", value);
        if (text.endsWith(".0")) {
            text = text.substring(0, text.length() - 2);
        }
        return (value > 0 ? "+" : "") + text;
    }

    /**
     * 命中触发编码 → 文案（加新编码时同步这里，`verify_gear` 会核对覆盖面）。
     * 与 {@link DynastyTrinketOnHit} 的编码一一对应。
     */
    private static String onHitName(int code, double value, int chance) {
        String name = switch (code) {
            case 1 -> "吸血 " + percent(value) + "（按造成的伤害回血）";
            case 2 -> "斩杀 " + percent(value) + " 血线以下的目标（Boss / 神兽免斩）";
            case 3 -> "会心 " + percent(value) + " 额外伤害";
            case 4 -> "突袭 " + percent(value) + " 额外伤害（只在目标满血时生效）";
            case 5 -> "连击 每层 " + percent(value) + " 额外伤害（最多 6 层、3 秒内有效）";
            case 6 -> "雷罚 附加 " + number(value) + " 点伤害";
            default -> null;
        };
        if (name == null) {
            return null;
        }
        return chance >= 100 ? name : name + "，§7概率 " + chance + "%";
    }

    /** 效果编码 → 文案（21~27 是模组自有效果）/ effect code to text */
    private static String effectName(int code, int level) {
        String name = switch (code) {
            case 21 -> "龙威";
            case 22 -> "铁壁";
            case 23 -> "疾风";
            case 24 -> "威慑";
            case 25 -> "天命";
            case 26 -> "忠诚";
            case 27 -> "内伤";
            case 1 -> "夜视";
            case 2 -> "水下呼吸";
            case 3 -> "抗火";
            case 4 -> "抗性";
            case 5, 12 -> "再生";
            case 8 -> "缓降";
            case 11 -> "幸运";
            default -> null;
        };
        if (name == null) {
            return null;
        }
        int shown = code == 12 ? level + 2 : level + 1;         // 与 applySpecEffect 的换算一致
        return name + " " + ROMAN[Math.min(shown, ROMAN.length) - 1];
    }
}
