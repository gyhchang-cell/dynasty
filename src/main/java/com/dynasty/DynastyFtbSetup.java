package com.dynasty;

import net.minecraftforge.fml.ModList;

import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.function.BooleanSupplier;
import java.util.function.Consumer;

/**
 * FTB 侧边栏按钮处理（纯反射，不依赖 FTB 的编译期类）。
 *
 * 目前做一件事：把 FTB Teams 的「My Team」侧边栏按钮**隐藏**掉
 * （单人玩不需要队伍，而且它挡在背包/任务界面旁边）。
 *
 * Hides the FTB Teams "My Team" sidebar button via reflection, so the mod still
 * compiles and runs with or without FTB Library installed.
 */
public final class DynastyFtbSetup {

    private DynastyFtbSetup() {
    }

    private static final String EVENT_CLASS = "dev.ftb.mods.ftblibrary.sidebar.SidebarButtonCreatedEvent";
    private static final String BUTTON_CLASS = "dev.ftb.mods.ftblibrary.sidebar.SidebarButton";
    /** 要隐藏的按钮 id（FTB Teams 的队伍按钮）/ sidebar button ids to hide */
    private static final String[] HIDDEN = {"my_team", "team"};

    public static void register() {
        if (ModList.get() == null || !ModList.get().isLoaded("ftblibrary")) {
            Dynasty.LOGGER.info("[Dynasty] FTB Library not present - sidebar tweaks skipped");
            return;
        }
        try {
            Class<?> eventClass = Class.forName(EVENT_CLASS);
            Field eventField = eventClass.getField("EVENT");
            Object archEvent = eventField.get(null);
            Method register = findRegister(archEvent.getClass());
            if (register == null) {
                Dynasty.LOGGER.warn("[Dynasty] FTB sidebar tweak: no register() found - skipped");
                return;
            }
            register.invoke(archEvent, (Consumer<Object>) DynastyFtbSetup::hide);
            Dynasty.LOGGER.info("[Dynasty] FTB sidebar tweak attached (hide team button)");
        } catch (Throwable throwable) {
            Dynasty.LOGGER.warn("[Dynasty] could not attach FTB sidebar tweak: {}", throwable.toString());
        }
    }

    /**
     * Architectury 的 Event#register 参数被泛型擦除，可能是 Consumer 也可能是 Object，
     * 这里找一个「只有一个参数、且能接收 Consumer」的 register 方法。
     */
    private static Method findRegister(Class<?> type) {
        for (Method method : type.getMethods()) {
            if (!method.getName().equals("register") || method.getParameterCount() != 1) {
                continue;
            }
            Class<?> param = method.getParameterTypes()[0];
            if (param.isAssignableFrom(Consumer.class)) {
                return method;
            }
        }
        return null;
    }

    private static void hide(Object event) {
        try {
            Object button = event.getClass().getMethod("getButton").invoke(event);
            if (button == null) {
                return;
            }
            Object id = Class.forName(BUTTON_CLASS).getMethod("getId").invoke(button);
            String text = String.valueOf(id).toLowerCase();
            for (String hidden : HIDDEN) {
                if (text.endsWith(hidden) || text.contains(hidden)) {
                    Method addCondition = Class.forName(BUTTON_CLASS)
                            .getMethod("addVisibilityCondition", BooleanSupplier.class);
                    addCondition.invoke(button, (BooleanSupplier) () -> false);
                    Dynasty.LOGGER.info("[Dynasty] hidden FTB sidebar button: {}", text);
                    return;
                }
            }
        } catch (Throwable ignored) {
            // FTB 侧异常不影响本体 / never let FTB break the base mod
        }
    }
}
