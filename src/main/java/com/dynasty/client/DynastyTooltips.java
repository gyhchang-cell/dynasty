package com.dynasty.client;

import com.dynasty.DynastyBalance;
import com.google.common.collect.Multimap;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.SwordItem;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.entity.player.ItemTooltipEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;
import org.lwjgl.glfw.GLFW;
import net.minecraft.client.Minecraft;

import java.util.List;

/**
 * 悬停提示：默认只显示一行「按住 Shift 查看用法」，按住 Shift 后展开用法与数值（攻击力/护甲/耐久/套装加成）。
 * Tooltips: by default only a "hold Shift" hint is shown; holding Shift reveals usage and stats.
 */
@Mod.EventBusSubscriber(modid = com.dynasty.Dynasty.MODID, value = Dist.CLIENT)
public class DynastyTooltips {

    @SubscribeEvent
    public static void onItemTooltip(ItemTooltipEvent event) {
        ItemStack stack = event.getItemStack();
        List<Component> tip = event.getToolTip();
        if (!DynastyItemInfo.isDynasty(stack)) {
            return;
        }
        List<String> info = DynastyItemInfo.lines(stack);
        boolean zh = DynastyItemInfo.chinese();
        boolean shift = shiftDown();

        // 1) 名字下面的一行简介（始终显示）/ one-line summary right under the name
        String brief = briefLine(stack, zh);
        if (!brief.isEmpty()) {
            tip.add(Math.min(1, tip.size()), Component.literal(brief));
        }

        // 2) 盔甲：全部直接显示、格式统一，不需要按 Shift
        //    armour shows everything at once in a uniform block, no Shift needed
        if (stack.getItem() instanceof ArmorItem) {
            for (String line : info) {
                tip.add(Component.literal(line));
            }
            appendArmorStats(stack, tip, zh);
            return;
        }

        if (info.isEmpty() && !hasStats(stack)) {
            return;
        }
        // 3) 其它物品：不按 Shift 只给提示 / other items: Shift reveals the details
        if (!shift) {
            tip.add(Component.literal(zh ? "§8【按住 §eShift §8查看用法与详细数值】"
                    : "§8[Hold §eShift §8for usage & full stats]"));
            return;
        }
        for (String line : info) {
            tip.add(Component.literal(line));
        }
        appendStats(stack, tip, zh);
    }

    /** 盔甲名称（按套）/ armour set name */
    private static String setName(String path, boolean zh) {
        if (path.startsWith("cloth")) return zh ? "布衣" : "Cloth";
        if (path.startsWith("general")) return zh ? "将军铠" : "General";
        if (path.startsWith("jade")) return zh ? "玉甲" : "Jade";
        if (path.startsWith("dragon_scale")) return zh ? "龙鳞甲" : "Dragon Scale";
        if (path.startsWith("sea_silk")) return zh ? "鲛绡甲" : "Sea Silk";
        if (path.startsWith("dark_iron")) return zh ? "玄铁重铠" : "Dark Iron";
        if (path.startsWith("xuantian")) return zh ? "玄天真龙甲" : "Xuantian True Dragon";
        // 第二十轮扩充的 10 套（注意：bronze 要在 brocade 之后判断也无所谓，前缀不重叠）
        if (path.startsWith("bamboo")) return zh ? "竹甲" : "Bamboo";
        if (path.startsWith("leather")) return zh ? "皮甲" : "Leather";
        if (path.startsWith("brocade")) return zh ? "织锦袍" : "Brocade";
        if (path.startsWith("bronze")) return zh ? "青铜甲" : "Bronze";
        if (path.startsWith("silver")) return zh ? "白银铠" : "Silver";
        if (path.startsWith("cinnabar")) return zh ? "朱砂符甲" : "Cinnabar";
        if (path.startsWith("phoenix")) return zh ? "凤凰羽衣" : "Phoenix";
        if (path.startsWith("qilin")) return zh ? "麒麟鳞甲" : "Qilin";
        if (path.startsWith("sky")) return zh ? "天将云铠" : "Sky General";
        if (path.startsWith("draco_king")) return zh ? "龙王鳞铠" : "Dragon King";
        // 第三十一轮：10 套终盘甲（四象 / 星斗 / 道门）
        if (path.startsWith("xuanwu")) return zh ? "玄武甲" : "Xuanwu";
        if (path.startsWith("zhuque")) return zh ? "朱雀羽" : "Zhuque";
        if (path.startsWith("qinglong")) return zh ? "青龙鳞" : "Qinglong";
        if (path.startsWith("baihu")) return zh ? "白虎铠" : "Baihu";
        if (path.startsWith("beidou")) return zh ? "北斗甲" : "Beidou";
        if (path.startsWith("tiangang")) return zh ? "天罡甲" : "Tiangang";
        if (path.startsWith("disha")) return zh ? "地煞甲" : "Disha";
        if (path.startsWith("taiyi")) return zh ? "太乙甲" : "Taiyi";
        if (path.startsWith("ziwei")) return zh ? "紫微甲" : "Ziwei";
        if (path.startsWith("hunyuan")) return zh ? "混元甲" : "Hunyuan";
        // 第三十二轮：毕业甲（两条流派线终点合体）
        if (path.startsWith("hongmeng")) return zh ? "鸿蒙帝铠" : "Hongmeng Imperial Armor";
        return zh ? "护甲" : "Armour";
    }

    private static String pieceName(ArmorItem.Type type, boolean zh) {
        return switch (type) {
            case HELMET -> zh ? "头盔" : "Helmet";
            case CHESTPLATE -> zh ? "胸甲" : "Chestplate";
            case LEGGINGS -> zh ? "护腿" : "Leggings";
            case BOOTS -> zh ? "靴子" : "Boots";
        };
    }

    /**
     * 盔甲统一信息块（直接显示，不需要按 Shift）：
     *   §6套装名 · 部位 → §f特殊效果： → §f套装效果： → 耐久
     * 格式与「愚者 / Goety」那种两段式提示一致：段落标题 + "- " 开头的条目。
     * Uniform armour block, always visible: section headers with dash bullets.
     */
    private static void appendArmorStats(ItemStack stack, List<Component> tip, boolean zh) {
        if (!(stack.getItem() instanceof ArmorItem armorItem)) {
            return;
        }
        EquipmentSlot slot = armorItem.getEquipmentSlot();
        Multimap<Attribute, AttributeModifier> mods = stack.getAttributeModifiers(slot);
        double armor = 0.0D;
        double toughness = 0.0D;
        double kb = 0.0D;
        for (AttributeModifier m : mods.get(Attributes.ARMOR)) {
            armor += m.getAmount();
        }
        for (AttributeModifier m : mods.get(Attributes.ARMOR_TOUGHNESS)) {
            toughness += m.getAmount();
        }
        for (AttributeModifier m : mods.get(Attributes.KNOCKBACK_RESISTANCE)) {
            kb += m.getAmount();
        }
        ResourceLocation id = ForgeRegistries.ITEMS.getKey(stack.getItem());
        String path = id == null ? "" : id.getPath();
        double[] bonus = DynastyBalance.setNameBonus(path);

        tip.add(Component.literal("§6" + setName(path, zh) + " · " + pieceName(armorItem.getType(), zh)));

        // ---- 特殊效果：这一件自带的属性 ----
        tip.add(Component.literal("§f" + (zh ? "特殊效果：" : "Special effects:")));
        tip.add(Component.literal("§d- §7" + (zh ? "护甲 " : "Armour ") + "§f" + (long) armor
                + "§7   " + (zh ? "韧性 " : "Toughness ") + "§f" + (long) toughness
                + (kb > 0.0D ? "§7   " + (zh ? "抗击退 " : "KB resist ") + "§f" + percent(kb) : "")));
        if (bonus != null) {
            tip.add(Component.literal("§d- §7" + (zh ? "受击减伤 " : "Damage taken ") + "§f-"
                    + percent(bonus[0]) + "§7，" + (zh ? "生命上限 " : "max health ") + "§f+"
                    + (long) bonus[1]));
        }

        // ---- 套装效果：四件同套才吃满，并标出当前已穿几件 ----
        if (bonus != null) {
            tip.add(Component.literal("§f" + (zh ? "套装效果：" : "Set effects:")));
            tip.add(Component.literal("§d- §7" + (zh ? "四件同套：总减伤 " : "All four: total reduction ")
                    + "§f" + percent(Math.min(0.92D, bonus[0] * 4.0D)) + "§7，"
                    + (zh ? "总生命 " : "health ") + "§f+" + (long) (bonus[1] * 4.0D)));
            tip.add(Component.literal("§d- §7" + (zh ? "当前已穿 " : "Currently worn ") + "§f"
                    + wornPieces(path, zh) + "/4§7（"
                    + (zh ? "每秒自动刷新，换装 / 过维度都不会丢"
                          : "refreshed every second, never lost") + "）"));
        }
        if (stack.isDamageableItem()) {
            tip.add(Component.literal("§7" + (zh ? "耐久 " : "Durability ") + "§f" + stack.getMaxDamage()));
        }
    }

    /** 身上同套的件数（0-4）/ how many pieces of this set are currently worn */
    private static int wornPieces(String path, boolean zh) {
        var player = Minecraft.getInstance().player;
        if (player == null) {
            return 0;
        }
        String set = setName(path, zh);
        int worn = 0;
        for (ItemStack piece : player.getArmorSlots()) {
            ResourceLocation id = ForgeRegistries.ITEMS.getKey(piece.getItem());
            if (id != null && DynastyBalance.setNameBonus(id.getPath()) != null
                    && setName(id.getPath(), zh).equals(set)) {
                worn++;
            }
        }
        return worn;
    }

    /** 0.16 → "16%"、0.05 → "5%"（整数就不带小数点）/ percent without trailing zeros */
    private static String percent(double ratio) {
        long tenths = Math.round(ratio * 1000.0D);
        if (tenths % 10L == 0L) {
            return (tenths / 10L) + "%";
        }
        return (tenths / 10L) + "." + Math.abs(tenths % 10L) + "%";
    }

    /** 一句话简介：武器给攻击力，护甲给护甲与套装减伤 / one-line summary */
    private static String briefLine(ItemStack stack, boolean zh) {
        EquipmentSlot slot = slotOf(stack);
        if (slot == null) {
            return DynastyItemInfo.shortText(stack);
        }
        Multimap<Attribute, AttributeModifier> mods = stack.getAttributeModifiers(slot);
        double damage = 0.0D;
        double armor = 0.0D;
        for (AttributeModifier m : mods.get(Attributes.ATTACK_DAMAGE)) {
            if (m.getOperation() == AttributeModifier.Operation.ADDITION) {
                damage += m.getAmount();
            }
        }
        for (AttributeModifier m : mods.get(Attributes.ARMOR)) {
            armor += m.getAmount();
        }
        if (damage > 0.0D) {
            ResourceLocation id = ForgeRegistries.ITEMS.getKey(stack.getItem());
            double bonus = id == null ? 0.0D : DynastyBalance.weaponBonus(id.getPath());
            String extra = bonus > 0.0D
                    ? (zh ? " §7· 特攻 §c+" + (long) bonus : " §7· extra §c+" + (long) bonus)
                    : "";
            return (zh ? "§7兵器 · 攻击力 §c" : "§7Weapon · damage §c") + (long) (damage + 1.0D)
                    + extra
                    + (zh ? " §8（Shift 看机制）" : " §8(Shift for gimmick)");
        }
        if (armor > 0.0D) {
            ResourceLocation id = ForgeRegistries.ITEMS.getKey(stack.getItem());
            double[] bonus = id == null ? null : DynastyBalance.setNameBonus(id.getPath());
            String extra = bonus == null ? "" : (zh
                    ? " §7· 套装减伤 §6" + (long) (bonus[0] * 100.0D) + "%/件"
                    : " §7· set reduction §6" + (long) (bonus[0] * 100.0D) + "%/piece");
            return (zh ? "§7护甲 §b" : "§7Armour §b") + (long) armor + extra;
        }
        return DynastyItemInfo.shortText(stack);
    }

    private static boolean shiftDown() {
        try {
            long handle = Minecraft.getInstance().getWindow().getWindow();
            return GLFW.glfwGetKey(handle, GLFW.GLFW_KEY_LEFT_SHIFT) == GLFW.GLFW_PRESS
                    || GLFW.glfwGetKey(handle, GLFW.GLFW_KEY_RIGHT_SHIFT) == GLFW.GLFW_PRESS;
        } catch (Exception ignored) {
            return false;
        }
    }

    private static EquipmentSlot slotOf(ItemStack stack) {
        if (stack.getItem() instanceof ArmorItem armorItem) {
            return armorItem.getEquipmentSlot();
        }
        if (stack.getItem() instanceof SwordItem) {
            return EquipmentSlot.MAINHAND;
        }
        if (stack.getItem() instanceof net.minecraft.world.item.DiggerItem) {
            return EquipmentSlot.MAINHAND;
        }
        return null;
    }

    private static boolean hasStats(ItemStack stack) {
        return slotOf(stack) != null;
    }

    private static void appendStats(ItemStack stack, List<Component> tip, boolean zh) {
        EquipmentSlot slot = slotOf(stack);
        if (slot == null) {
            return;
        }
        Multimap<Attribute, AttributeModifier> mods = stack.getAttributeModifiers(slot);
        double damage = 0.0D;
        double armor = 0.0D;
        double toughness = 0.0D;
        for (AttributeModifier m : mods.get(Attributes.ATTACK_DAMAGE)) {
            if (m.getOperation() == AttributeModifier.Operation.ADDITION) {
                damage += m.getAmount();
            }
        }
        for (AttributeModifier m : mods.get(Attributes.ARMOR)) {
            armor += m.getAmount();
        }
        for (AttributeModifier m : mods.get(Attributes.ARMOR_TOUGHNESS)) {
            toughness += m.getAmount();
        }
        if (damage > 0.0D) {
            tip.add(Component.literal((zh ? "§c攻击力：§f" : "§cAttack damage: §f")
                    + (long) (damage + 1.0D)));
        }
        if (armor > 0.0D) {
            tip.add(Component.literal((zh ? "§b护甲：§f" : "§bArmor: §f") + (long) armor
                    + (zh ? " §7韧性：§f" : " §7Toughness: §f") + (long) toughness));
        }
        if (stack.isDamageableItem()) {
            tip.add(Component.literal((zh ? "§7耐久：§f" : "§7Durability: §f") + stack.getMaxDamage()));
        }
        ResourceLocation id = ForgeRegistries.ITEMS.getKey(stack.getItem());
        if (id != null) {
            double[] bonus = DynastyBalance.setNameBonus(id.getPath());
            if (bonus != null) {
                tip.add(Component.literal((zh ? "§6套装加成：§f减伤 +" : "§6Set bonus: §f-")
                        + (long) (bonus[0] * 100.0D) + (zh ? "% §f生命 +" : "% §fhealth +")
                        + (long) bonus[1]));
            }
        }
    }
}
