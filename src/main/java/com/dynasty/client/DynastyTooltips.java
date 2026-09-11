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
        List<String> info = DynastyItemInfo.lines(stack);
        boolean zh = DynastyItemInfo.chinese();
        boolean shift = shiftDown();

        if (info.isEmpty() && !hasStats(stack)) {
            return;
        }
        if (!shift) {
            tip.add(Component.literal(zh ? "§8【按住 §eShift §8查看用法与数值】"
                    : "§8[Hold §eShift §8for usage & stats]"));
            return;
        }
        for (String line : info) {
            tip.add(Component.literal(line));
        }
        appendStats(stack, tip, zh);
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
