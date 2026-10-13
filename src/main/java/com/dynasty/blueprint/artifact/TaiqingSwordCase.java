package com.dynasty.blueprint.artifact;

import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.state.*;
import net.minecraft.world.level.block.state.properties.*;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.*;

/** Two metres long, so the actual1.4m sword fits. No craftable or portable case item. */
public final class TaiqingSwordCase extends Block {
    public static final IntegerProperty STAGE=IntegerProperty.create("trial_state",0,2);
    private static final VoxelShape SHAPE=box(2,0,-4,14,10,28);
    private static final VoxelShape OPEN_SHAPE=Shapes.or(SHAPE,box(14,8,-4,26,10,28));
    public TaiqingSwordCase(Properties properties){super(properties);registerDefaultState(stateDefinition.any().setValue(STAGE,0));}
    @Override protected void createBlockStateDefinition(StateDefinition.Builder<Block,BlockState> builder){builder.add(STAGE);}
    @Override public VoxelShape getShape(BlockState state,BlockGetter world,BlockPos pos,CollisionContext context){return state.getValue(STAGE)>0?OPEN_SHAPE:SHAPE;}
    @Override public InteractionResult use(BlockState state,Level world,BlockPos pos,Player player,InteractionHand hand,BlockHitResult hit){
        if(hand!=InteractionHand.MAIN_HAND||!player.getMainHandItem().isEmpty())return InteractionResult.PASS;
        if(world.isClientSide)return InteractionResult.SUCCESS;
        if(!(player instanceof ServerPlayer p)||p.isCreative()||p.isSpectator())return InteractionResult.PASS;
        TaiqingTrials.discover(p);
        if(ZhanluTrialRewards.claimed(p)){p.displayClientMessage(Component.translatable("message.dynasty.taiqing_claimed"),false);return InteractionResult.CONSUME;}
        if(ZhanluTrialRewards.eligible(p,pos)){
            if(ZhanluTrialRewards.claim(p,pos,hand)){TaiqingTrials.cancel(p);world.setBlock(pos,state.setValue(STAGE,2),3);p.displayClientMessage(Component.translatable("message.dynasty.taiqing_sword"),false);}
            else p.displayClientMessage(Component.translatable("message.dynasty.taiqing_inventory"),false);
        }else if(TaiqingTrials.begin(p,pos)){world.setBlock(pos,state.setValue(STAGE,0),3);p.displayClientMessage(Component.translatable("message.dynasty.taiqing_begin"),false);}
        else p.displayClientMessage(Component.translatable("message.dynasty.taiqing_unregistered"),false);
        return InteractionResult.CONSUME;
    }
}
