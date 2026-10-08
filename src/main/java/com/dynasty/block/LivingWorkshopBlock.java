package com.dynasty.block;

import com.dynasty.workshop.WorkshopBlockEntity;
import net.minecraft.core.*;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.*;
import net.minecraft.world.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.*;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.*;

/** Existing eight IDs/shapes retained; all share one persisted one-item transaction. */
public final class LivingWorkshopBlock extends Block implements EntityBlock {
    public enum Kind { MARROW, ESSENCE, REPAIR, VITALITY, HIDE, HERBAL, LAPIDARY, EMBER }
    private final Kind kind;
    public Kind kind(){return kind;}
    public LivingWorkshopBlock(Properties properties,Kind kind){
        super(properties);this.kind=kind;
        registerDefaultState(stateDefinition.any().setValue(BlockStateProperties.LIT,false).setValue(BlockStateProperties.HORIZONTAL_FACING,Direction.NORTH));
    }
    @Override public BlockEntity newBlockEntity(BlockPos p,BlockState s){return new WorkshopBlockEntity(p,s);}
    @Override protected void createBlockStateDefinition(StateDefinition.Builder<Block,BlockState>b){b.add(BlockStateProperties.LIT,BlockStateProperties.HORIZONTAL_FACING);}
    @Override public VoxelShape getShape(BlockState s,BlockGetter l,BlockPos p,CollisionContext c){return WorkshopShapes.get(kind,s.getValue(BlockStateProperties.HORIZONTAL_FACING));}
    @Override public VoxelShape getCollisionShape(BlockState s,BlockGetter l,BlockPos p,CollisionContext c){return getShape(s,l,p,c);}
    @Override public BlockState getStateForPlacement(net.minecraft.world.item.context.BlockPlaceContext c){return defaultBlockState().setValue(BlockStateProperties.HORIZONTAL_FACING,c.getHorizontalDirection().getOpposite());}
    @Override public BlockState rotate(BlockState s,Rotation r){return s.setValue(BlockStateProperties.HORIZONTAL_FACING,r.rotate(s.getValue(BlockStateProperties.HORIZONTAL_FACING)));}
    @Override public BlockState mirror(BlockState s,Mirror m){return s.rotate(m.getRotation(s.getValue(BlockStateProperties.HORIZONTAL_FACING)));}
    @Override public InteractionResult use(BlockState s,Level level,BlockPos pos,Player p,InteractionHand hand,BlockHitResult hit){
        if(hand!=InteractionHand.MAIN_HAND)return InteractionResult.PASS;
        if(level.isClientSide)return InteractionResult.SUCCESS;
        if(!(level.getBlockEntity(pos) instanceof WorkshopBlockEntity vat))return InteractionResult.PASS;
        var held=p.getItemInHand(hand);
        // A deliberate cleanse gesture leaves the existing workshop recipe/deposits untouched.
        if(kind==Kind.REPAIR && p.isShiftKeyDown() && held.is(com.dynasty.expansion.ExpansionContent.MATERIALS.get("sprite_jade").get())
                && p.hasEffect(com.dynasty.expansion.ExpansionEffects.BREAK.get())) {
            p.removeEffect(com.dynasty.expansion.ExpansionEffects.BREAK.get());
            if(!p.getAbilities().instabuild)held.shrink(1);
            p.getInventory().setChanged();
            com.dynasty.expansion.CombatFeedback.send(p,com.dynasty.expansion.CombatFeedback.HEAL);
            p.displayClientMessage(Component.translatable("message.dynasty.cod4.armor_cleansed"),true);
            return InteractionResult.CONSUME;
        }
        if((held.isEmpty()&&!vat.ready()) || p.isShiftKeyDown()) {
            if(p instanceof net.minecraft.server.level.ServerPlayer server)
                net.minecraftforge.network.NetworkHooks.openScreen(server,vat,pos);
            return InteractionResult.CONSUME;
        }
        if(vat.ready()){
            if(!held.isEmpty())return InteractionResult.CONSUME;
            var result=vat.collect();if(!p.getInventory().add(result))p.drop(result,false);
        } else if(!vat.accept(held)) {
            var next=vat.recipe().next(vat.deposited());
            if(next!=null)p.displayClientMessage(Component.translatable("workshop.dynasty.next",next.stack().getHoverName(),vat.deposited(),vat.recipe().total()),true);
            return InteractionResult.CONSUME;
        }
        p.getInventory().setChanged();
        level.playSound(null,pos,vat.ready()?SoundEvents.AMETHYST_BLOCK_CHIME:SoundEvents.COMPOSTER_FILL,SoundSource.BLOCKS,.6f,1f);
        ((ServerLevel)level).sendParticles(vat.ready()?ParticleTypes.ENCHANT:ParticleTypes.HAPPY_VILLAGER,pos.getX()+.5,pos.getY()+.8,pos.getZ()+.5,4,.2,.1,.2,.01);
        return InteractionResult.CONSUME;
    }
    @Override public void onRemove(BlockState s,Level level,BlockPos pos,BlockState next,boolean moving){
        if(!s.is(next.getBlock())&&level.getBlockEntity(pos) instanceof WorkshopBlockEntity vat)vat.refund();
        super.onRemove(s,level,pos,next,moving);
    }
}
