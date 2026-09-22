package com.dynasty.bounty;

import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;

/**
 * 悬赏告示板：右键打开委托界面（服务端建立会话后把界面数据发给客户端）。
 *
 * 方块本身不含任何业务逻辑，判定全在 {@link BountyService}（服务端权威）。
 */
public class BountyBoardBlock extends Block {

    public BountyBoardBlock(Properties props) {
        super(props);
    }

    @SuppressWarnings("null")
    @Override
    public InteractionResult use(BlockState state, Level level, BlockPos pos, Player player,
                                 InteractionHand hand, BlockHitResult hit) {
        if (level.isClientSide() || !(player instanceof ServerPlayer serverPlayer)) {
            return InteractionResult.sidedSuccess(level.isClientSide());
        }
        BountyService.openSession(serverPlayer, pos);
        return InteractionResult.CONSUME;
    }

    @SuppressWarnings("null")
    @Override
    public void onRemove(BlockState state, Level level, BlockPos pos, BlockState newState, boolean moved) {
        super.onRemove(state, level, pos, newState, moved);
        if (!state.is(newState.getBlock()) && !level.isClientSide()) {
            // 方块被拆：让所有还开着这块板会话的玩家收到提示（界面上会显示失效）
            for (ServerPlayer player : level.getEntitiesOfClass(ServerPlayer.class,
                    new net.minecraft.world.phys.AABB(pos).inflate(BountyService.REACH))) {
                BountyService.closeSession(player);
                player.sendSystemMessage(Component.translatable("dynasty.bounty.msg.board_removed"));
            }
        }
    }
}
