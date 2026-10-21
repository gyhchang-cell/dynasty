package com.dynasty.dungeon;

import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.world.level.material.PushReaction;

/** Visual finishes share the existing protected block identity and saved default. */
public final class DungeonMasonryBlock extends Block {
    public static final IntegerProperty FINISH = IntegerProperty.create("finish", 0, 7);

    public DungeonMasonryBlock(Properties properties) {
        super(properties);
        registerDefaultState(stateDefinition.any().setValue(FINISH, 0));
    }

    @Override protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(FINISH);
    }

    @Override public PushReaction getPistonPushReaction(BlockState state) {
        return PushReaction.BLOCK;
    }

    public static BlockState finish(int finish) {
        return DungeonContent.MASONRY.get().defaultBlockState().setValue(FINISH, finish);
    }
}
