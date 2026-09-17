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
                growMethod = bridge.getMethod("growSlots", LivingEntity.class, String.class, int.class);
                Dynasty.LOGGER.info("[Dynasty] Curios detected - trinket slots enabled");
            } catch (Throwable throwable) {
                available = false;
                Dynasty.LOGGER.warn("[Dynasty] Curios bridge unavailable: {}", throwable.toString());
            }
        } else {
            Dynasty.LOGGER.info("[Dynasty] Curios not present - trinkets use the built-in pouch");
        }
    }

    /** 所有 Curios 标准槽：开局就要有，否则玩家只有 back 一个槽。 */
    private static final String[] STANDARD_SLOTS = {
            "back", "belt", "body", "bracelet", "charm", "curio", "hands", "head", "necklace", "ring"
    };

    /** 每个标准槽的初始格数（戒指 2 格，其余 1 格）。 */
    private static final int STANDARD_SIZE = 1;
    private static final int RING_SIZE = 2;

    /**
     * 开格子：王朝饰品槽按官阶成长，所有 Curios 标准槽至少各开 STANDARD_SIZE 格（只增不减，幂等）。
     * Grows the dynasty trinket slot by rank and guarantees every standard Curios slot exists.
     */
    public static void growTrinketSlots(LivingEntity entity, int wantExtra) {
        if (!available || growMethod == null) {
            return;
        }
        try {
            growMethod.invoke(null, entity, DynastyRankPerks.SLOT, DynastyRankPerks.BASE_SLOTS + wantExtra);
            for (String slot : STANDARD_SLOTS) {
                growMethod.invoke(null, entity, slot, "ring".equals(slot) ? RING_SIZE : STANDARD_SIZE);
            }
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
