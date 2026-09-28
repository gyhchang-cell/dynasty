package com.dynasty.client;

import net.minecraft.client.Minecraft;

/**
 * 客户端打开王朝图鉴。
 * Client helper to open the Dynasty Codex screen.
 */
public final class ClientGuide {

    private ClientGuide() {
    }

    public static void open() {
        if (net.minecraftforge.fml.ModList.get().isLoaded("patchouli")) {
            try {
                Class<?> api = Class.forName("vazkii.patchouli.api.PatchouliAPI");
                Object instance = api.getMethod("get").invoke(null);
                Class.forName("vazkii.patchouli.api.PatchouliAPI$IPatchouliAPI")
                        .getMethod("openBookGUI", net.minecraft.resources.ResourceLocation.class)
                        .invoke(instance, new net.minecraft.resources.ResourceLocation("dynasty", "imperial_codex"));
                return;
            } catch (ReflectiveOperationException failure) {
                com.mojang.logging.LogUtils.getLogger().error("Cannot open Dynasty Patchouli book", failure);
            }
        }
        Minecraft.getInstance().setScreen(new GuideScreen());
    }
}
