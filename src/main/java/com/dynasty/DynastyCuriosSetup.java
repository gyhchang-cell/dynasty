package com.dynasty;

import net.minecraft.world.entity.LivingEntity;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.fml.ModList;

import java.lang.reflect.Method;
import java.util.Set;

/**
 * Curios 接入开关（不直接引用 Curios 类，避免没有 Curios 时类校验失败）。
 * 若 Curios 存在，则通过反射调用 {@link DynastyCuriosBridge}。
 *
 * Curios entry point that references no Curios type directly, so the class always loads.
 */
public final class DynastyCuriosSetup {

    private DynastyCuriosSetup() {
    }

    private static final String BRIDGE = "com.dynasty.DynastyCuriosBridge";
    private static Method attachMethod;
    private static Method collectMethod;
    private static Method growMethod;
    private static boolean available;

    static {
        try {
            available = ModList.get() != null && ModList.get().isLoaded("curios");
        } catch (Throwable ignored) {
            available = false;
        }
        if (available) {
            try {
                Class<?> bridge = Class.forName(BRIDGE);
                attachMethod = bridge.getMethod("attach", IEventBus.class);
                collectMethod = bridge.getMethod("collectEquipped", LivingEntity.class, Set.class);
                growMethod = bridge.getMethod("syncQuestSlots", LivingEntity.class, int.class);
                Dynasty.LOGGER.info("[Dynasty] Curios detected - trinket slots enabled");
            } catch (Throwable throwable) {
                available = false;
                Dynasty.LOGGER.warn("[Dynasty] Curios bridge unavailable: {}", throwable.toString());
            }
        } else {
            Dynasty.LOGGER.info("[Dynasty] Curios not present - trinkets use inventory fallback");
        }
    }

    public static boolean isLoaded() {
        return ModList.get().isLoaded("curios");
    }

    /** 标准槽的基础格数由数据包定义，这里只同步任务奖励。 */
    public static void syncQuestSlots(LivingEntity entity, int bonus) {
        if (!available || growMethod == null) {
            return;
        }
        try {
            growMethod.invoke(null, entity, bonus);
        } catch (Throwable ignored) {
            // Curios 侧异常不影响本体 / never let Curios break the base mod
        }
    }

    public static void register(IEventBus modEventBus) {
        if (!available || attachMethod == null) {
            return;
        }
        try {
            attachMethod.invoke(null, modEventBus);
        } catch (Throwable throwable) {
            Dynasty.LOGGER.warn("[Dynasty] could not attach Curios listener: {}", throwable.toString());
        }
    }

    /** 把 Curios 槽位里的饰品加入集合 / adds trinkets worn in Curios slots to the set */
    public static void collectEquipped(LivingEntity entity, Set<String> out) {
        if (!available || collectMethod == null) {
            return;
        }
        try {
            collectMethod.invoke(null, entity, out);
        } catch (Throwable ignored) {
            // Curios 侧异常不影响本体 / never let Curios break the base mod
        }
    }
}
