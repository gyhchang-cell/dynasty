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
                || com.dynasty.infusion.InfusionTraits.material(stack) != null) return out;
        boolean zh = chinese();
        String path = id.getPath();
        String[] special = DynastyItemUsage.special(path);
        String[] chosen = special != null ? special : codex(path);
        if (chosen == null && stack.getItem() instanceof BlockItem) {
            chosen = DynastyBlockInfo.use(path);
        }
        if (chosen == null && includeGeneric) {
            chosen = category(path, stack);
        }
        if (chosen != null) {
            String text = zh ? chosen[0] : chosen[1];
            String bare = text.replaceAll("§.", "");
            String name = stack.getHoverName().getString();
            if (bare.startsWith(name + "：") || bare.startsWith(name + ":")) text = bare.substring(name.length() + 1).trim();
            out.add(text);
        }
        // 追加「翻译键」写的补充说明（料理用途 / 信物用途 / 传送门目的地与回程提醒）；
        // 没有对应键的物品不受影响，重复行由 DynastyInfoKeys 自己过滤。
        out.addAll(DynastyInfoKeys.lines(path, out.isEmpty() ? null : out.get(0)));
        return out;
    }

    /** 图鉴里的「妙用」文案 / usage text taken from the codex */
    private static String[] codex(String path) {
        DynastyCodex.Entry entry = DynastyCodex.find(path);
        if (entry == null) {
            return null;
        }
        return new String[]{entry.zhUse(), entry.enUse()};
    }

    private static String[] category(String path, ItemStack stack) {
        if (stack.getItem() instanceof BlockItem) {
            String[] own = DynastyBlockInfo.use(path);
            if (own != null) {
                return own;
            }
            return null;
        }
        if (path.endsWith("_coin")) {
            return new String[]{"货币：用于科举、节庆与交易。",
                    "Currency: used for exams, festivals and trade."};
        }
        return null;
    }

    /** 是否为本模组物品 / whether the stack belongs to this mod */
    public static boolean isDynasty(ItemStack stack) {
        ResourceLocation id = net.minecraftforge.registries.ForgeRegistries.ITEMS.getKey(stack.getItem());
        return id != null && id.getNamespace().equals(com.dynasty.Dynasty.MODID);
    }

    /**
     * 物品名下面那一行「一句话介绍」（不按 Shift 也能看到）。
     * The single-line description shown right under the item name (always visible).
     */
    public static String shortText(ItemStack stack) {
        ResourceLocation id = net.minecraftforge.registries.ForgeRegistries.ITEMS.getKey(stack.getItem());
        if (id == null || !id.getNamespace().equals(com.dynasty.Dynasty.MODID)) {
            return "";
        }
        if (stack.getItem() instanceof net.minecraft.world.item.SpawnEggItem) return "";
        boolean zh = chinese();
        String path = id.getPath();
        String[] special = DynastyItemUsage.special(path);
        String[] chosen = special != null ? special : codex(path);
        if (chosen == null) {
            chosen = category(path, stack);
        }
        if (chosen == null || stack.getItem() instanceof net.minecraft.world.item.PotionItem) return "";
        String line = strip(zh ? chosen[0] : chosen[1]);
        if (line.length() > 34) {
            line = line.substring(0, 34) + "…";
        }
        return line;
    }

    /** 去掉颜色代码与「前导标题」，只留一句短介绍 / strip colour codes and the leading label */
    private static String strip(String text) {
        String out = text.replaceAll("§.", "");
        int split = out.indexOf('：');
        if (split < 0) {
            split = out.indexOf(':');
        }
        if (split > 0) {
            out = out.substring(split + 1);
        }
        return out.trim();
    }
}
