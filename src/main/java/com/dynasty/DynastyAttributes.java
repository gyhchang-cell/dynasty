package com.dynasty;

import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeMap;

/**
 * 属性安全访问：**取不到就返回 null / fallback，绝不抛异常**。
 *
 * 为什么必须走这里（踩了很久的坑）：
 *   原版 {@code AttributeSupplier#getValue/getBaseValue} 在「这个实体的属性表里没有该属性」时
 *   会抛 {@code IllegalArgumentException: Can't find attribute minecraft:generic.attack_damage}。
 *   玩家、大部分怪都没问题，但有些实体天生没有攻击力 —— 最典型的是**盔甲架**
 *   （`EntityType.ARMOR_STAND` 用的是 `LivingEntity.createLivingAttributes()`，
 *   只有生命 / 抗击退 / 移速，没有攻击力）。
 *   我们在 EntityJoinLevelEvent 里给「进入世界的怪」按维度加难度时会读攻击力，
 *   只要那个区块里有一个盔甲架（创造模式摆装备很常见），服务端主线程就当场崩，
 *   报错只有一行 IllegalArgumentException —— 表现就是「一进别的维度就崩」。
 *
 * 结论：凡是「对不特定实体读属性」的地方，一律用本类，不用原版 getAttribute* 。
 *
 * Safe attribute access — vanilla throws when the attribute is missing (armour stands have
 * no ATTACK_DAMAGE), which used to crash the server thread while a chunk with an armour
 * stand was being promoted, i.e. "crash when entering another dimension".
 */
public final class DynastyAttributes {

    private DynastyAttributes() {
    }

    /** 安全取属性实例：实体没有这个属性就返回 null / null when absent */
    public static AttributeInstance instance(LivingEntity entity, Attribute attribute) {
        if (entity == null || attribute == null) {
            return null;
        }
        try {
            AttributeMap map = entity.getAttributes();
            if (map == null || !map.hasAttribute(attribute)) {
                return null;                 // 属性表里没有 → 直接放弃，绝不调用 getValue
            }
            return map.getInstance(attribute);
        } catch (Throwable ignored) {
            return null;                     // 别的模组的怪属性表再怪，也不能崩我们的线程
        }
    }

    /** 有没有这个属性 / whether the entity actually has the attribute */
    public static boolean has(LivingEntity entity, Attribute attribute) {
        return instance(entity, attribute) != null;
    }

    /** 基础值（没有就返回 fallback）/ base value with fallback */
    public static double base(LivingEntity entity, Attribute attribute, double fallback) {
        AttributeInstance instance = instance(entity, attribute);
        return instance == null ? fallback : instance.getBaseValue();
    }

    /** 当前值（没有就返回 fallback）/ current value with fallback */
    public static double value(LivingEntity entity, Attribute attribute, double fallback) {
        AttributeInstance instance = instance(entity, attribute);
        return instance == null ? fallback : instance.getValue();
    }

    /** 最大生命（没有就返回 fallback）/ max health with fallback */
    public static double maxHealth(LivingEntity entity, double fallback) {
        return value(entity, net.minecraft.world.entity.ai.attributes.Attributes.MAX_HEALTH, fallback);
    }
}
