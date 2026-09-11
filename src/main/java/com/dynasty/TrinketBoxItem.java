package com.dynasty;

import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.SimpleMenuProvider;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraftforge.network.NetworkHooks;

/**
 * 百宝妆匣：右键打开 6 个饰品槽（相当于自带一套 Curios 槽位）。
 * Trinket Box: right-click to open the six built-in accessory slots.
 */
@SuppressWarnings("null")
public class TrinketBoxItem extends Item {

    public TrinketBoxItem(Properties properties) {
        super(properties);
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (player instanceof ServerPlayer serverPlayer) {
            NetworkHooks.openScreen(serverPlayer,
                    new SimpleMenuProvider((id, inventory, p) -> new TrinketMenu(id, inventory),
                            Component.literal("百宝妆匣 · 饰品")),
                    buf -> DynastyMenus.write(buf, DynastyTrinkets.load(serverPlayer)));
        }
        return InteractionResultHolder.sidedSuccess(stack, level.isClientSide());
    }
}
