package com.dynasty.client;

import com.dynasty.DynastyBalance;
import com.dynasty.DynastySetBonus;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.util.Mth;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.RenderGuiOverlayEvent;
import net.minecraftforge.client.gui.overlay.VanillaGuiOverlay;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import java.util.List;

/**
 * 大血量 HUD：当最大生命超过 80 时，隐藏原版上百颗心（渲染上千个图标会掉帧），
 * 改为一条紧凑血条 + 数值，并把王朝套装减伤/护甲一并显示。
 *
 * Big-health HUD: above 80 max health the vanilla heart rows (hundreds of icons = frame drops)
 * are replaced by one compact bar with numeric readout, plus armor / set-reduction info.
 */
@Mod.EventBusSubscriber(modid = com.dynasty.Dynasty.MODID, value = Dist.CLIENT)
public class DynastyHealthHud {

    private static final float COMPACT_ABOVE = 80.0F;

    @SubscribeEvent
    public static void onOverlayPre(RenderGuiOverlayEvent.Pre event) {
        if (!event.getOverlay().id().equals(VanillaGuiOverlay.PLAYER_HEALTH.id())) {
            return;
        }
        Minecraft mc = Minecraft.getInstance();
        LocalPlayer player = mc.player;
        if (player == null || player.getMaxHealth() <= COMPACT_ABOVE) {
            return;
        }
        event.setCanceled(true);

        GuiGraphics graphics = event.getGuiGraphics();
        int left = mc.getWindow().getGuiScaledWidth() / 2 - 91;
        int right = mc.getWindow().getGuiScaledWidth() / 2 + 91;
        // 血条画在原版护甲行的上方，避免与原版图标重叠 / bar sits above the vanilla armor row
        int top = mc.getWindow().getGuiScaledHeight() - 49;

        float health = player.getHealth();
        float max = player.getMaxHealth();
        float ratio = Mth.clamp(health / max, 0.0F, 1.0F);
        int barWidth = 100;


        graphics.fill(left, top, left + barWidth, top + 9, 0xB0000000);
        graphics.fill(left + 1, top + 1, left + barWidth - 1, top + 8, 0xFF3A0A0A);
        int fillWidth = (int) ((barWidth - 2) * ratio);
        graphics.fill(left + 1, top + 1, left + 1 + fillWidth, top + 8, 0xFFD22B2B);
        graphics.fill(left + 1, top + 1, left + 1 + fillWidth, top + 4, 0xFFF06060);

        String healthText = String.format("§c%s §f%d §7/ §f%d", DynastyItemInfo.chinese() ? "生命" : "HP",
                Math.round(health), Math.round(max));
        graphics.drawString(mc.font, healthText, left + barWidth + 6, top + 1, 0xFFFFFFFF, true);

        List<String> worn = DynastySetBonus.wornArmorIds(player);
        double armor = wornArmor(player);
        float reduction = DynastyBalance.setDamageReduction(worn);
        if (armor > 0.0D) {
            String armorText = String.format("§b%s %.0f  §6%s %.0f%%",
                    DynastyItemInfo.chinese() ? "护甲" : "ARM", armor,
                    DynastyItemInfo.chinese() ? "减伤" : "RED", reduction * 100.0F);
            graphics.drawString(mc.font, armorText, right - mc.font.width(armorText), top - 11,
                    0xFFFFFFFF, true);
        }
    }

    @SubscribeEvent
    public static void onOverlayPost(RenderGuiOverlayEvent.Post event) {
        if (!event.getOverlay().id().equals(VanillaGuiOverlay.HOTBAR.id())) {
            return;
        }
        Minecraft mc = Minecraft.getInstance();
        LocalPlayer player = mc.player;
        if (player == null || !ClientTrinkets.has("south_pointing_compass")) {
            return;
        }
        String coords = String.format("§7司南 §fX %d §7Y §f%d §7Z §f%d",
                (int) player.getX(), (int) player.getY(), (int) player.getZ());
        event.getGuiGraphics().drawString(mc.font, coords, 4, 4, 0xFFFFFFFF, true);
    }

    /** 实际护甲值（读取装备属性）/ real armor value taken from the worn items */
    private static double wornArmor(LocalPlayer player) {
        double armor = 0.0D;
        net.minecraft.world.entity.EquipmentSlot[] slots = {
                net.minecraft.world.entity.EquipmentSlot.HEAD,
                net.minecraft.world.entity.EquipmentSlot.CHEST,
                net.minecraft.world.entity.EquipmentSlot.LEGS,
                net.minecraft.world.entity.EquipmentSlot.FEET};
        for (net.minecraft.world.entity.EquipmentSlot slot : slots) {
            net.minecraft.world.item.ItemStack stack = player.getItemBySlot(slot);
            if (stack.isEmpty()) {
                continue;
            }
            for (net.minecraft.world.entity.ai.attributes.AttributeModifier modifier
                    : stack.getAttributeModifiers(slot).get(net.minecraft.world.entity.ai.attributes.Attributes.ARMOR)) {
                armor += modifier.getAmount();
            }
        }
        return armor;
    }
}
