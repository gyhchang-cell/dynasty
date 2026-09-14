package com.dynasty;

import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.attributes.RangedAttribute;

import java.lang.reflect.Field;

/**
 * 解开原版属性硬上限：攻击力 2048 / 生命 1024 / 护甲 30 / 护甲韧性 20。
 *
 * 原版 {@code RangedAttribute#sanitizeValue} 会把结果夹到 [min, max]，
 * 所以不管怎么叠属性、武器都超不过 2048 —— 这是玩家反馈「毕业数值太低」的根。
 * 这里在模组初始化时把这几个上限直接改掉：**反射写 {@code maxValue} 字段**。
 *
 * ⚠ 线上（SRG 名）字段叫 {@code f_22313_}，开发环境（官方映射）叫 {@code maxValue}，
 *   以前只试了 "maxValue" 和猜错的 "f_22312_"，于是生产环境 100% 失败，
 *   日志里刷「无法解除属性上限」，玩家看到的还是 2048 顶。
 *   现在改成：先按名字试 → 失败就**扫描所有 double 字段**（混淆后名字会变、类型不会），
 *   每写一个字段都用 {@code getMaxValue()} + {@code sanitizeValue()} **验证生效**，
 *   验证不过就把字段原值还原，绝不留下「min > max」这种坏状态。
 *
 * Raises the hard caps of the vanilla attributes so endgame numbers can keep growing.
 * Field lookup is mapping-agnostic and functionally verified.
 */
public final class DynastyAttributeCaps {

    private DynastyAttributeCaps() {
    }

    /** 新上限：够用又不至于让 HUD 数字失控 */
    public static final double NEW_MAX_DAMAGE = 100_000.0D;
    public static final double NEW_MAX_HEALTH = 100_000.0D;
    public static final double NEW_MAX_ARMOR = 10_000.0D;
    public static final double NEW_MAX_TOUGHNESS = 1_000.0D;

    /** 已知字段名：官方映射 / SRG / 更早的猜想，挨个试 */
    private static final String[] FIELD_NAMES = {"maxValue", "f_22313_", "f_22312_"};

    private static boolean unlocked;

    public static boolean unlocked() {
        return unlocked;
    }

    /** 模组初始化时调用一次 / called once during mod init */
    public static void unlock() {
        int ok = 0;
        ok += raise("attack_damage", Attributes.ATTACK_DAMAGE, NEW_MAX_DAMAGE) ? 1 : 0;
        ok += raise("max_health", Attributes.MAX_HEALTH, NEW_MAX_HEALTH) ? 1 : 0;
        ok += raise("armor", Attributes.ARMOR, NEW_MAX_ARMOR) ? 1 : 0;
        ok += raise("armor_toughness", Attributes.ARMOR_TOUGHNESS, NEW_MAX_TOUGHNESS) ? 1 : 0;
        ok += raise("attack_speed", Attributes.ATTACK_SPEED, 100.0D) ? 1 : 0;
        unlocked = ok >= 4;
        if (unlocked) {
            Dynasty.LOGGER.info("[Dynasty] 属性上限已解除（攻击力/生命 {} 起）", (long) NEW_MAX_DAMAGE);
        } else {
            Dynasty.LOGGER.warn("[Dynasty] 属性上限只改成功 {} 项 —— 超上限的部分仍由「特攻」补足", ok);
        }
    }

    private static boolean raise(String label, Attribute attribute, double newMax) {
        if (!(attribute instanceof RangedAttribute ranged)) {
            Dynasty.LOGGER.warn("[Dynasty] {} 不是 RangedAttribute，跳过", label);
            return false;
        }
        if (ranged.getMaxValue() >= newMax) {
            return true;                     // 已经是够大的上限（例如 AttributeFix 已经改过）
        }
        // ① 按字段名找（官方映射 maxValue / SRG f_22313_）
        for (String name : FIELD_NAMES) {
            try {
                Field field = RangedAttribute.class.getDeclaredField(name);
                if (write(field, ranged, newMax)) {
                    Dynasty.LOGGER.info("[Dynasty] 属性上限 {} -> {}（字段 {}）", label, (long) newMax, name);
                    return true;
                }
            } catch (Throwable ignored) {
                // 换下一个名字 / try the next field name
            }
        }
        // ② 兜底：扫描所有 double 字段（混淆后名字会变，类型不会）
        for (Field field : RangedAttribute.class.getDeclaredFields()) {
            if (field.getType() != double.class) {
                continue;
            }
            if (write(field, ranged, newMax)) {
                Dynasty.LOGGER.info("[Dynasty] 属性上限 {} -> {}（扫描字段 {}）",
                        label, (long) newMax, field.getName());
                return true;
            }
        }
        Dynasty.LOGGER.warn("[Dynasty] 无法解除属性上限 {}：RangedAttribute 里找不到 maxValue 字段", label);
        return false;
    }

    /**
     * 写字段并**验证真的生效**：写完 maxValue 之后，
     * {@code sanitizeValue(极大值)} 必须不再被夹回原上限；否则还原字段原值。
     *
     * Writes the field, verifies the clamp is really gone, and restores the old value
     * when the write did not work (so a wrong guess can never corrupt min/max).
     */
    private static boolean write(Field field, RangedAttribute ranged, double newMax) {
        double before;
        try {
            field.setAccessible(true);
            before = field.getDouble(ranged);
            if (before >= newMax) {
                return ranged.getMaxValue() >= newMax;
            }
            field.setDouble(ranged, newMax);
            boolean ok = ranged.getMaxValue() >= newMax
                    && ranged.sanitizeValue(newMax * 2.0D) >= newMax;
            if (!ok) {
                field.setDouble(ranged, before);          // 猜错了（比如写到了 minValue）就还原
            }
            return ok;
        } catch (Throwable ignored) {
            return false;
        }
    }
}
