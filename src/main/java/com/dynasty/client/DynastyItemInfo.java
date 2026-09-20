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
        List<String> out = new ArrayList<>();
        ResourceLocation id = net.minecraftforge.registries.ForgeRegistries.ITEMS.getKey(stack.getItem());
        if (id == null || !id.getNamespace().equals(com.dynasty.Dynasty.MODID)) {
            return out;
        }
        boolean zh = chinese();
        String path = id.getPath();
        String[] special = DynastyItemUsage.special(path);
        String[] chosen = special != null ? special : codex(path);
        if (chosen == null) {
            chosen = category(path, stack);
        }
        if (chosen != null) {
            out.add(zh ? chosen[0] : chosen[1]);
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
            return new String[]{"王朝方块：" + path + "（放置装饰用）。",
                    "Dynasty block: " + path + "."};
        }
        if (path.endsWith("_spawn_egg")) {
            return new String[]{"刷怪蛋：右键地面放出该生物。",
                    "Spawn egg: right-click the ground to spawn."};
        }
        if (path.endsWith("_coin")) {
            return new String[]{"货币：用于科举、节庆与交易。",
                    "Currency: used for exams, festivals and trade."};
        }
        if (path.startsWith("dynasty_potion") || path.startsWith("dynasty_splash_potion")
                || path.startsWith("dynasty_lingering_potion")) {
            return new String[]{"药水：饮用或投掷获得对应的王朝增益。",
                    "Potion: drink or throw for a dynasty buff."};
        }
        if (path.endsWith("_helmet") || path.endsWith("_chestplate")
                || path.endsWith("_leggings") || path.endsWith("_boots")) {
            return new String[]{"护甲：穿戴提升防御，并计入王朝套装减伤。",
                    "Armor: raises defense and counts towards the dynasty set bonus."};
        }
        if (path.startsWith("sword_") || path.equals("halberd_fangtian")) {
            return new String[]{"武器：左键攻击造成大量伤害。",
                    "Weapon: left-click to deal heavy damage."};
        }
        if (path.startsWith("pickaxe_")) {
            return new String[]{"工具：挖掘方块，兼顾强力攻击。",
                    "Tool: mines blocks and hits hard."};
        }
        return new String[]{"王朝物品：可用于合成、交易或收藏（详见王朝图鉴）。",
                "Dynasty item: used for crafting, trade or collection (see the Codex)."};
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
        boolean zh = chinese();
        String path = id.getPath();
        String[] special = DynastyItemUsage.special(path);
        String[] chosen = special != null ? special : codex(path);
        if (chosen == null) {
            chosen = category(path, stack);
        }
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
