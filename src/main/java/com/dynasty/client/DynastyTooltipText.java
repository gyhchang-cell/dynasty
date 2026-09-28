package com.dynasty.client;

import net.minecraft.client.resources.language.I18n;
import net.minecraft.network.chat.Component;

/**
 * 悬停说明的「纯文案 + 纯算术」层（不碰 GUI、不碰注册表，方便单测）。
 *
 * 设计目标（本轮需求）：
 * <ul>
 *   <li>默认只给 1～3 条**简短被动效果**，详细内容按住 Shift 才展开；</li>
 *   <li>不重复原版已经显示的东西（物品名、攻击力、护甲、韧性、耐久、附魔）；</li>
 *   <li>数值一律来自真实配置 / 真实属性修饰符，并按原版运算类型折叠
 *       （ADDITION 相加 → MULTIPLY_BASE 相加 → MULTIPLY_TOTAL 连乘），不是「把所有数字加起来」；</li>
 *   <li>文案走翻译键：键存在就用键（可被语言包覆盖），键缺失时回退到内置中英文，
 *       **绝不**把原始键名显示给玩家。</li>
 * </ul>
 *
 * Pure text + arithmetic helpers for the hover tooltip. Translation keys win;
 * a built-in zh/en fallback is used only when a key is missing.
 */
public final class DynastyTooltipText {

    private DynastyTooltipText() {
    }

    /** 原版属性运算类型（与 {@code AttributeModifier.Operation} 序号一致）。*/
    public static final int OP_ADDITION = 0;
    public static final int OP_MULTIPLY_BASE = 1;
    public static final int OP_MULTIPLY_TOTAL = 2;

    /** 套装减伤的真实上限（与玩法结算一致，见 DynastyBalance.setDamageReduction）。*/
    public static final double SET_REDUCTION_CAP = 0.90D;

    /** 默认（不按 Shift）最多显示几行自定义说明：与饰品共用同一个预算 / shared budget */
    public static final int BRIEF_LIMIT = com.dynasty.DynastyTooltipBudget.BRIEF_LIMIT;

    /** 一条属性修饰符的纯数据形式 / plain attribute modifier */
    public record Mod(int operation, double amount) {
    }

    /** 装备分类 / item kind */
    public enum Kind {
        ARMOR, WEAPON, OTHER
    }

    /** 翻译键 + 内置中英回退（键缺失时用）。(key, zh, en) */
    public record Text(String key, String zh, String en) {
    }

    public static final Text HOLD_SHIFT = new Text("tooltip.dynasty.hold_shift",
            "§8【按住 §eShift §8查看详情】", "§8[Hold §eShift §8for details]");
    public static final Text SET_CODEX = new Text("tooltip.dynasty.armor.set_in_codex",
            "§8套装详情见图鉴", "§8Set bonus: see the Codex");
    public static final Text ARMOR_SET = new Text("tooltip.dynasty.armor.set",
            "§6%s §7套装 · 每件减伤 §6+%s §7· 生命上限 §6+%s",
            "§6%s §7set · §6+%s §7damage reduction · §6+%s §7max health");
    public static final Text ARMOR_TOTAL = new Text("tooltip.dynasty.armor.set_total",
            "§7穿满四件：总减伤 §6+%s§7（上限 %s）· 总生命 §6+%s",
            "§7All four pieces: §6+%s §7damage reduction (cap %s) · §6+%s §7health");
    public static final Text ARMOR_WORN = new Text("tooltip.dynasty.armor.worn",
            "§7当前已穿 §f%s/4 §7件：实际减伤 §6+%s §7· 生命 §6+%s",
            "§7Currently worn §f%s/4§7: §6+%s §7damage reduction · §6+%s §7health");
    public static final Text ARMOR_TOTALS = new Text("tooltip.dynasty.armor.piece_totals",
            "§7四件合计：护甲 §f+%s §7· 韧性 §f+%s",
            "§7Whole-set totals: §f+%s §7armour · §f+%s §7toughness");
    public static final Text WEAPON_EXTRA = new Text("tooltip.dynasty.weapon.extra_damage",
            "§7特攻 §c+%s", "§7Bonus damage §c+%s");

    /** 翻译键优先的文案 / key first, built-in fallback second */
    public static Component line(Text text, boolean zh, Object... args) {
        if (I18n.exists(text.key())) {
            return Component.translatable(text.key(), args);
        }
        return Component.literal(String.format(java.util.Locale.ROOT, zh ? text.zh() : text.en(), args));
    }

    /** 「按住 Shift 查看详情」/ the always-visible hint */
    public static Component holdShift(boolean zh) {
        return line(HOLD_SHIFT, zh);
    }

    /** 「套装详情见图鉴」（套装不展开长文）/ short pointer to the Codex */
    public static Component setCodexHint(boolean zh) {
        return line(SET_CODEX, zh);
    }

    /** 按原版规则折叠属性修饰符：先加法、再基础乘、最后总乘。/ vanilla-style attribute folding. */
    public static double fold(double base, Iterable<Mod> mods) {
        double addition = 0.0D;
        double multiplyBase = 0.0D;
        double multiplyTotal = 1.0D;
        for (Mod mod : mods) {
            switch (mod.operation()) {
                case OP_ADDITION -> addition += mod.amount();
                case OP_MULTIPLY_BASE -> multiplyBase += mod.amount();
                case OP_MULTIPLY_TOTAL -> multiplyTotal *= 1.0D + mod.amount();
                // 未知运算类型：保守按加法处理，绝不把数值悄悄丢掉
                default -> addition += mod.amount();
            }
        }
        return (base + addition) * (1.0D + multiplyBase) * multiplyTotal;
    }

    /** 0.16 → "16%"、0.055 → "5.5%"（整数不带小数点）/ percent without trailing zeros */
    public static String percent(double ratio) {
        long tenths = Math.round(ratio * 1000.0D);
        if (tenths % 10L == 0L) {
            return (tenths / 10L) + "%";
        }
        return (tenths / 10L) + "." + Math.abs(tenths % 10L) + "%";
    }

    /** 紧凑数字（16 / 16.5，不带多余小数）/ compact number */
    public static String number(double value) {
        if (Math.abs(value - Math.rint(value)) < 1.0E-6D) {
            return String.valueOf((long) Math.rint(value));
        }
        return String.format(java.util.Locale.ROOT, "%.1f", value);
    }

    /** 穿满四件的理论总减伤（按真实上限截断）。/ theoretical full-set reduction */
    public static double fullSetReduction(double perPiece) {
        return Math.min(SET_REDUCTION_CAP, perPiece * 4.0D);
    }

    /** 当前实穿件数的总减伤（按真实上限截断）。/ reduction of the pieces actually worn */
    public static double wornReduction(double perPiece, int worn) {
        return Math.min(SET_REDUCTION_CAP, perPiece * Math.max(0, Math.min(4, worn)));
    }

    /** 护甲：默认那两行（套装一行 + 图鉴指引）。/ armour brief lines. */
    public static java.util.List<Component> armorBrief(boolean zh, String setKey,
                                                      double perPieceReduction, double perPieceHealth) {
        java.util.List<Component> out = new java.util.ArrayList<>(2);
        out.add(line(ARMOR_SET, zh, setKey, percent(perPieceReduction), number(perPieceHealth)));
        out.add(setCodexHint(zh));
        return out;
    }

    /** 护甲：Shift 展开的准确数值（不重复默认那两行）。/ armour detail lines. */
    public static java.util.List<Component> armorDetails(boolean zh, double perPieceReduction,
                                                        double perPieceHealth, int worn,
                                                        double wornArmor, double wornToughness) {
        java.util.List<Component> out = new java.util.ArrayList<>(3);
        int clamped = Math.max(0, Math.min(4, worn));
        out.add(line(ARMOR_TOTAL, zh, percent(fullSetReduction(perPieceReduction)),
                percent(SET_REDUCTION_CAP), number(perPieceHealth * 4.0D)));
        out.add(line(ARMOR_WORN, zh, clamped, percent(wornReduction(perPieceReduction, clamped)),
                number(perPieceHealth * clamped)));
        if (wornArmor > 0.0D || wornToughness > 0.0D) {
            out.add(line(ARMOR_TOTALS, zh, number(wornArmor), number(wornToughness)));
        }
        return out;
    }

    /** 兵器：只有真实存在的「特攻」才多一行（攻击力 / 耐久原版已显示，不重复）。*/
    public static java.util.List<Component> weaponBrief(boolean zh, double extraDamage) {
        java.util.List<Component> out = new java.util.ArrayList<>(1);
        if (extraDamage > 0.0D) {
            out.add(line(WEAPON_EXTRA, zh, number(extraDamage)));
        }
        return out;
    }
}
