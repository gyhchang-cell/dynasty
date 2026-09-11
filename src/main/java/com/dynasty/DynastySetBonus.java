package com.dynasty;

import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.living.LivingEquipmentChangeEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

/**
 * 套装生命加成：穿上王朝盔甲即获得最大生命加成（玉甲 +600 / 将军铠 +800 / 龙鳞甲 +1000）。
 * 每秒校验一次，登录、换装、穿越维度都会自动刷新，不会叠加。
 *
 * Set bonus health: wearing dynasty armor raises max health. Refreshed every second so
 * login / equipment / dimension changes are always covered and the modifier never stacks.
 */
@Mod.EventBusSubscriber(modid = Dynasty.MODID)
public class DynastySetBonus {

    private static final UUID HEALTH_UUID = UUID.fromString("3f2a7c10-5d44-4a6e-9c1d-0b7e6a51d001");
    private static final String HEALTH_NAME = "dynasty_set_health";
    private static int counter;

    @SubscribeEvent
    public static void onEquipmentChange(LivingEquipmentChangeEvent event) {
        if (event.getEntity() instanceof ServerPlayer player) {
            refresh(player);
        }
    }

    @SubscribeEvent
    public static void onPlayerTick(TickEvent.PlayerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || !(event.player instanceof ServerPlayer player)) {
            return;
        }
        if (++counter % 20 == 0) {
            refresh(player);
        }
    }

    /** 重新计算套装生命加成 / recomputes the set health bonus */
    public static void refresh(ServerPlayer player) {
        List<String> worn = wornArmorIds(player);
        double bonus = DynastyBalance.setHealthBonus(worn);
        AttributeInstance instance = player.getAttribute(Attributes.MAX_HEALTH);
        if (instance == null) {
            return;
        }
        instance.removeModifier(HEALTH_UUID);
        if (bonus > 0.0D) {
            instance.addPermanentModifier(new AttributeModifier(HEALTH_UUID, HEALTH_NAME, bonus,
                    AttributeModifier.Operation.ADDITION));
        }
        // 脱甲后生命不得超过新的上限 / never leave health above the new maximum
        if (player.getHealth() > player.getMaxHealth()) {
            player.setHealth(player.getMaxHealth());
        }
    }

    /** 当前穿戴的王朝装备 id / ids of the dynasty armor currently worn */
    public static List<String> wornArmorIds(Player player) {
        List<String> out = new ArrayList<>();
        for (EquipmentSlot slot : new EquipmentSlot[]{
                EquipmentSlot.HEAD, EquipmentSlot.CHEST, EquipmentSlot.LEGS, EquipmentSlot.FEET}) {
            ItemStack stack = player.getItemBySlot(slot);
            if (stack.isEmpty()) {
                continue;
            }
            ResourceLocation id = ForgeRegistries.ITEMS.getKey(stack.getItem());
            if (id != null && id.getNamespace().equals(Dynasty.MODID)) {
                out.add(id.getPath());
            }
        }
        return out;
    }
}
