package com.dynasty.dungeon;

import net.minecraft.core.BlockPos;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.block.BaseEntityBlock;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityTicker;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.level.block.state.properties.DirectionProperty;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.world.level.material.PushReaction;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;

public final class DungeonMechanismBlock extends BaseEntityBlock {
    public enum Kind {CORE,SEAL,TARGET,DOOR,FLOOR,TRAP}
    public static final BooleanProperty ACTIVE=BooleanProperty.create("active"),OPEN=BlockStateProperties.OPEN;
    public static final DirectionProperty FACING=BlockStateProperties.HORIZONTAL_FACING;
    public static final IntegerProperty STAGE=IntegerProperty.create("stage",0,3);
    private final Kind kind;
    public DungeonMechanismBlock(Kind kind,Properties properties){
        super(properties);this.kind=kind;
        registerDefaultState(stateDefinition.any().setValue(ACTIVE,false).setValue(OPEN,false)
            .setValue(FACING,net.minecraft.core.Direction.SOUTH).setValue(STAGE,0));
    }
    public Kind kind(){return kind;}
    @Override protected void createBlockStateDefinition(StateDefinition.Builder<net.minecraft.world.level.block.Block,BlockState> builder){builder.add(ACTIVE,OPEN,FACING,STAGE);}
    @Override public RenderShape getRenderShape(BlockState state){return kind==Kind.CORE?RenderShape.INVISIBLE:RenderShape.MODEL;}
    @Override public VoxelShape getCollisionShape(BlockState state,BlockGetter level,BlockPos pos,CollisionContext ctx){
        return kind==Kind.CORE||((kind==Kind.DOOR||kind==Kind.FLOOR)&&state.getValue(OPEN))?Shapes.empty():Shapes.block();
    }
    @Override public PushReaction getPistonPushReaction(BlockState state){return PushReaction.BLOCK;}
    @Override public BlockEntity newBlockEntity(BlockPos pos,BlockState state){return new DungeonMechanismBlockEntity(pos,state);}
    @Override public <T extends BlockEntity> BlockEntityTicker<T> getTicker(Level level,BlockState state,BlockEntityType<T> type){
        return level.isClientSide?null:createTickerHelper(type,DungeonContent.MECHANISM.get(),DungeonMechanismBlockEntity::tick);
    }
    @Override public InteractionResult use(BlockState state,Level level,BlockPos pos,Player player,InteractionHand hand,BlockHitResult hit){
        if(!level.isClientSide&&hand==InteractionHand.MAIN_HAND&&level.getBlockEntity(pos) instanceof DungeonMechanismBlockEntity be){be.interact(player);}
        return InteractionResult.sidedSuccess(level.isClientSide);
    }
    @Override public void onProjectileHit(Level level,BlockState state,BlockHitResult hit,Projectile projectile){
        if(!level.isClientSide&&kind==Kind.TARGET&&projectile.getOwner() instanceof Player player
                &&level.getBlockEntity(hit.getBlockPos()) instanceof DungeonMechanismBlockEntity be)be.hitTarget(player);
    }
    @Override public void entityInside(BlockState state,Level level,BlockPos pos,Entity entity){
        if(!level.isClientSide&&(kind==Kind.FLOOR||kind==Kind.TRAP)&&entity instanceof Player player&&!player.isSpectator()
                &&level.getBlockEntity(pos) instanceof DungeonMechanismBlockEntity be)be.trigger();
    }
    @Override public void stepOn(Level level,BlockPos pos,BlockState state,Entity entity){
        entityInside(state,level,pos,entity);super.stepOn(level,pos,state,entity);
    }
}
