package com.dynasty;

import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

/**
 * 王朝说明书：首次进入世界自动发放，右键打开内置手册（开局流程、武器进化、饰品、图鉴导航）。
 * Dynasty Manual: handed to every player on first join; right-click to read the built-in handbook.
 */
@SuppressWarnings("null")
public final class DynastyManual {

    private DynastyManual() {
    }

    public static final DeferredRegister<Item> ITEMS =
            DeferredRegister.create(ForgeRegistries.ITEMS, Dynasty.MODID);

    public static final RegistryObject<Item> MANUAL = ITEMS.register("dynasty_manual",
            () -> new ManualItem(new Item.Properties().stacksTo(1)));

    /** 打开说明书界面 / opens the handbook screen */
    public static class ManualItem extends Item {
        public ManualItem(Properties properties) {
            super(properties);
        }

        @Override
        public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
            ItemStack stack = player.getItemInHand(hand);
            if (level.isClientSide()) {
                com.dynasty.client.ClientGuide.open();
            }
            return InteractionResultHolder.sidedSuccess(stack, level.isClientSide());
        }
    }

    /** 首次进入时发放说明书与百宝妆匣 / hands out the manual and trinket box once */
    public static void giveOnce(ServerPlayer player) {
        if (player.getPersistentData().getBoolean("dynasty_manual_given")) {
            return;
        }
        player.getPersistentData().putBoolean("dynasty_manual_given", true);
        give(player, new ItemStack(MANUAL.get()));
        give(player, new ItemStack(DynastyTrinkets.TRINKET_BOX.get()));
        player.sendSystemMessage(Component.literal(
                "§6[王朝] §r欢迎来到王朝！已赠送 §e王朝说明书§r 与 §e百宝妆匣§r。"));
        player.sendSystemMessage(Component.literal(
                "§7按住 §eShift §7悬停物品可看用法与数值；打开背包点左上角「✦ 王朝任务」看任务与图鉴。"));
    }

    private static void give(ServerPlayer player, ItemStack stack) {
        if (!player.getInventory().add(stack)) {
            player.drop(stack, false);
        }
    }
}
