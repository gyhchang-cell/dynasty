package com.dynasty.client;

import com.dynasty.DynastyCodex;
import net.minecraft.client.Minecraft;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.ItemStack;

import java.util.ArrayList;
import java.util.List;

/**
 * 物品用法/数值文案（中英双语，按客户端语言自动选择）。
 * Per-item usage text (zh/en picked from the client language).
 */
public final class DynastyItemInfo {

    private DynastyItemInfo() {
    }

    /** 是否中文客户端 / whether the client language is Chinese */
    public static boolean chinese() {
        try {
            String code = Minecraft.getInstance().getLanguageManager().getSelected();
            return code == null || code.toLowerCase().startsWith("zh");
        } catch (Exception ignored) {
            return true;
        }
    }

    /** 该物品的说明行（可为空）/ usage lines for the item */
    public static List<String> lines(ItemStack stack) {
        return lines(stack, true);
    }

    /**
     * 该物品的说明行。
     *
     * @param includeGeneric 是否带上「通用兜底一句话」（护甲 / 武器 / 货币…）。
     *                       盔甲的套装行已经在悬停里单独给出，通用护甲句属于重复，故传 false。
     */
    public static List<String> lines(ItemStack stack, boolean includeGeneric) {
        List<String> out = new ArrayList<>();
        ResourceLocation id = net.minecraftforge.registries.ForgeRegistries.ITEMS.getKey(stack.getItem());
        if (id == null || !id.getNamespace().equals(com.dynasty.Dynasty.MODID)) {
            return out;
        }
        if (stack.getItem() instanceof net.minecraft.world.item.SpawnEggItem
                || stack.getItem() instanceof BlockItem || stack.getItem() instanceof net.minecraft.world.item.PotionItem
