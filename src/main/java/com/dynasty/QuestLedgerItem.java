package com.dynasty;

import com.dynasty.network.QuestRequestPacket;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;

/**
 * 王朝手札（任务书）：右键打开任务界面，也可在背包左上角点击「王朝任务」按钮打开。
 * Quest Ledger: right-click to open the quest screen (also reachable from the inventory button).
 */
@SuppressWarnings("null")
public class QuestLedgerItem extends Item {

    public QuestLedgerItem(Properties properties) {
        super(properties);
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (player instanceof ServerPlayer serverPlayer) {
            QuestRequestPacket.sendTo(serverPlayer);
        }
        return InteractionResultHolder.sidedSuccess(stack, level.isClientSide());
    }
}
