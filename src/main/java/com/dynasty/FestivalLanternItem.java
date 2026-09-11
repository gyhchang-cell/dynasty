package com.dynasty;

import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;

/**
 * 节令灯：无需指令即可开启当令节日（不在节令期则提示最近节令）。
 * Festival Lantern: starts today's festival without any command.
 */
@SuppressWarnings("null")
public class FestivalLanternItem extends Item {

    public FestivalLanternItem(Properties properties) {
        super(properties);
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (level.isClientSide() || !(player instanceof ServerPlayer serverPlayer)) {
            return InteractionResultHolder.success(stack);
        }
        String today = DynastyFestivals.today();
        ServerLevel serverLevel = serverPlayer.serverLevel();
        if (today == null) {
            serverPlayer.sendSystemMessage(Component.literal(
                    "§e[节令] 今日非节令之日。春节 2/1-2/20 · 端午 6/1-6/10 · 中秋 9/15-9/25 · 重阳 10/1-10/10 · 除夕 12/31-1/2"));
            serverPlayer.getCooldowns().addCooldown(this, 40);
            return InteractionResultHolder.consume(stack);
        }
        DynastyFestivals.trigger(serverLevel, today, serverPlayer);
        serverLevel.playSound(null, serverPlayer.blockPosition(), SoundEvents.FIREWORK_ROCKET_LAUNCH,
                SoundSource.PLAYERS, 2.0F, 1.0F);
        serverPlayer.getCooldowns().addCooldown(this, 200);
        return InteractionResultHolder.consume(stack);
    }
}
