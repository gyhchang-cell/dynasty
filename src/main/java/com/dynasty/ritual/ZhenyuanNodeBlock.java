package com.dynasty.ritual;

import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.BaseEntityBlock;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;

/** A carved low offering plinth. The globe is a renderer, never a giant glass collision cube. */
public final class ZhenyuanNodeBlock extends BaseEntityBlock {
    public static final IntegerProperty SLOT = IntegerProperty.create("slot", 0, 4);
    public static final BooleanProperty ACTIVE = BooleanProperty.create("active");
    private static final VoxelShape SIDE = Shapes.or(Block.box(1, 0, 1, 15, 2, 15),
            Block.box(3, 2, 3, 13, 5, 13), Block.box(2, 5, 2, 14, 8, 14));
    private static final VoxelShape CORE = Shapes.or(Block.box(0, 0, 0, 16, 3, 16),
            Block.box(2, 3, 2, 14, 8, 14), Block.box(1, 8, 1, 15, 12, 15));

    public ZhenyuanNodeBlock(Properties properties) {
        super(properties);
        registerDefaultState(stateDefinition.any().setValue(SLOT, 4).setValue(ACTIVE, false));
    }
    @Override protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) { builder.add(SLOT, ACTIVE); }
    @Override public RenderShape getRenderShape(BlockState state) { return RenderShape.MODEL; }
    @Override public VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return state.getValue(SLOT) == 4 ? CORE : SIDE;
    }
    @Override public BlockEntity newBlockEntity(BlockPos pos, BlockState state) { return new ZhenyuanNodeBlockEntity(pos, state); }
    @Override public <T extends BlockEntity> net.minecraft.world.level.block.entity.BlockEntityTicker<T> getTicker(Level level,BlockState state,net.minecraft.world.level.block.entity.BlockEntityType<T> type) {
        if(!level.isClientSide||type!=ZhenyuanRitualContent.NODE_ENTITY.get())return null;
        return (l,p,s,be)-> { if(be instanceof ZhenyuanNodeBlockEntity node&&node.getSlot()==4&&node.timeline().getBoolean("Enabled"))
            net.minecraftforge.fml.DistExecutor.unsafeRunWhenOn(net.minecraftforge.api.distmarker.Dist.CLIENT,
                    ()->()->com.dynasty.client.RitualPhaseOneEffects.observe(node)); };
    }
    @Override public InteractionResult use(BlockState state, Level level, BlockPos pos, Player player,
                                           InteractionHand hand, BlockHitResult hit) {
        // Do not process the offhand a second time after the main-hand offering was consumed.
        if (hand != InteractionHand.MAIN_HAND) return InteractionResult.CONSUME;
        if (level.isClientSide) return InteractionResult.SUCCESS;
        if (player instanceof ServerPlayer server && level.getBlockEntity(pos) instanceof ZhenyuanNodeBlockEntity node) {
            com.dynasty.structure.megabuild.NaturalSculptures.bindIfNatural(server.serverLevel(),node);
            return ZhenyuanRitualService.interact(server, node);
        }
        return InteractionResult.PASS;
    }
}
