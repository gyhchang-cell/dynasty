package com.dynasty.client;

import com.dynasty.*;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.entity.player.ItemTooltipEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;

import java.util.List;

/** One owner per tooltip: vanilla stats, then concise blue Dynasty bonuses. */
@Mod.EventBusSubscriber(modid = Dynasty.MODID, value = Dist.CLIENT)
public class DynastyTooltips {
    @SubscribeEvent
    public static void onItemTooltip(ItemTooltipEvent event) {
        ItemStack stack = event.getItemStack();
        if (!DynastyItemInfo.isDynasty(stack)) return;
        ResourceLocation id = ForgeRegistries.ITEMS.getKey(stack.getItem());
        if (id == null) return;
        append(stack, id.getPath(), event.getToolTip(), DynastyItemInfo.chinese(), DynastyTooltipGate.shiftDown());
    }

    static void append(ItemStack stack, String path, List<Component> tip, boolean zh, boolean shift) {
        if (stack.getItem() instanceof ArmorItem) {
            double[] bonus = DynastyBalance.setNameBonus(path);
            if (bonus != null) {
                int at = afterAttribute(tip, "attribute.name.generic.armor_toughness");
                if (at < 0) at = afterAttribute(tip, "attribute.name.generic.armor");
                if (at < 0) at = tip.size();
                tip.add(at++, Component.literal("+" + number(bonus[0] * 100) + "% "
                        + (zh ? "伤害减免" : "Damage Reduction")).withStyle(ChatFormatting.BLUE));
                tip.add(at, Component.literal("+" + number(bonus[1]) + " "
                        + (zh ? "生命上限" : "Max Health")).withStyle(ChatFormatting.BLUE));
            }
            return; // Armour stats already describe the item; set details live in the book.
        }
        if (stack.getItem() instanceof DynastyTrinketTips.Charm) return;
        if (DynastyWeaponProgression.eligible(stack)) {
            String passive = "tooltip.dynasty.branch." + path;
            if (net.minecraft.client.resources.language.I18n.exists(passive))
                tip.add(Component.translatable(passive).withStyle(ChatFormatting.BLUE));
            double extra = DynastyBalance.weaponBonus(path);
            if (extra > 0) {
                int at = afterAttribute(tip, "attribute.name.generic.attack_damage");
                tip.add(at < 0 ? tip.size() : at, Component.literal("+" + number(extra) + " "
                        + (zh ? "附加伤害" : "Bonus Damage")).withStyle(ChatFormatting.BLUE));
            }
            int level = DynastyWeaponProgression.level(stack);
            tip.add(Component.literal((zh ? "兵器等级 " : "Weapon level ") + level + " · +"
                    + number((DynastyWeaponProgression.multiplier(level) - 1) * 100) + "% "
                    + (zh ? "伤害" : "damage")).withStyle(ChatFormatting.BLUE));
            if (shift) {
                tip.add(Component.literal((zh ? "杀敌历练 " : "Kill experience ")
                        + DynastyWeaponProgression.progress(stack) + "/"
                        + DynastyWeaponProgression.required(level)).withStyle(ChatFormatting.GRAY));
                String key = "tooltip.dynasty.school." + path;
                if (net.minecraft.client.resources.language.I18n.exists(key))
                    tip.add(Component.translatable(key).withStyle(ChatFormatting.GRAY));
                else for (String line : DynastyItemInfo.lines(stack, false))
                    tip.add(Component.literal(line.replace("常驻", "")));
            } else tip.add(DynastyTooltipText.holdShift(zh));
            return;
        }
        List<String> info = DynastyItemInfo.lines(stack);
        if (!info.isEmpty()) tip.add(Component.literal(info.get(0).replace("常驻", "")));
        if (shift) for (int i = 1; i < info.size(); i++) tip.add(Component.literal(info.get(i).replace("常驻", "")));
        else if (info.size() > 1) tip.add(DynastyTooltipText.holdShift(zh));
    }

    private static int afterAttribute(List<Component> tip, String key) {
        String name = Component.translatable(key).getString();
        for (int i = 0; i < tip.size(); i++)
            if (tip.get(i).getString().contains(name)) return i + 1;
        return -1;
    }

    private static String number(double value) {
        return value == Math.rint(value) ? Long.toString((long) value)
                : String.format(java.util.Locale.ROOT, "%.1f", value);
    }
}
