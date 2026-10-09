package com.dynasty.block;

import com.dynasty.expansion.*;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.world.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.effect.*;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.*;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.world.phys.*;

/** Original blocks, ordinary saved block states/scheduled ticks, no fuel BE or world manager. */
public final class OilFueledBlock extends Block {
    public enum Kind {LANTERN,INCENSE}
    public static final IntegerProperty FUEL=IntegerProperty.create("oil_fuel",0,3),BURN_STEP=IntegerProperty.create("oil_step",0,59);
    public static final int STEP_TICKS=20,STEPS_PER_UNIT=60;
    private final Kind kind;
    public OilFueledBlock(Properties properties,Kind kind){super(properties);this.kind=kind;registerDefaultState(stateDefinition.any().setValue(FUEL,0).setValue(BURN_STEP,0));}
    @Override protected void createBlockStateDefinition(StateDefinition.Builder<Block,BlockState> builder){builder.add(FUEL,BURN_STEP);}
    @Override public InteractionResult use(BlockState state,Level level,BlockPos pos,Player player,InteractionHand hand,BlockHitResult hit){
        var held=player.getItemInHand(hand);
        if(!held.is(ExpansionContent.item("lantern_oil")))return super.use(state,level,pos,player,hand,hit);
        if(hand!=InteractionHand.MAIN_HAND||!player.isAlive()||player.isSpectator()||player.level()!=level||player.distanceToSqr(Vec3.atCenterOf(pos))>36||state.getValue(FUEL)>=3)return InteractionResult.PASS;
        if(!level.isClientSide){
            int fuel=state.getValue(FUEL);var next=state.setValue(FUEL,fuel+1);if(fuel==0)next=next.setValue(BURN_STEP,0);
            level.setBlock(pos,next,3);if(!player.getAbilities().instabuild)held.shrink(1);
            if(fuel==0)level.scheduleTick(pos,this,STEP_TICKS);
            player.displayClientMessage(Component.translatable("message.dynasty.cod4.oil_added",fuel+1),true);
        }
        return InteractionResult.sidedSuccess(level.isClientSide);
    }
    @Override public void onPlace(BlockState state,Level level,BlockPos pos,BlockState old,boolean moving){
        super.onPlace(state,level,pos,old,moving);
        if(!level.isClientSide&&!old.is(this)&&state.getValue(FUEL)>0)level.scheduleTick(pos,this,STEP_TICKS);
    }
    @Override public void tick(BlockState state,ServerLevel level,BlockPos pos,RandomSource random){
        int fuel=state.getValue(FUEL);if(fuel==0)return;
        // The original palace lamp remains permanently bright; oil powers the extra night field.
        if(kind==Kind.LANTERN&&!level.isNight()){level.scheduleTick(pos,this,STEP_TICKS);return;}
        int step=state.getValue(BURN_STEP)+1;if(step>=STEPS_PER_UNIT){step=0;fuel--;}
        var next=state.setValue(FUEL,fuel).setValue(BURN_STEP,step);level.setBlock(pos,next,3);
        if(fuel==0)return;
        double radius=kind==Kind.LANTERN?6:4;
        var near=level.getEntitiesOfClass(ServerPlayer.class,new AABB(pos).inflate(radius),p->p.isAlive()&&!p.isSpectator()&&p.distanceToSqr(Vec3.atCenterOf(pos))<=radius*radius)
            .stream().sorted(java.util.Comparator.comparingDouble(p->p.distanceToSqr(Vec3.atCenterOf(pos)))).limit(16).toList();
        for(var p:near){
            if(kind==Kind.LANTERN)p.addEffect(new MobEffectInstance(MobEffects.NIGHT_VISION,240,0,true,false));
            else {p.removeEffect(ExpansionEffects.YIN.get());p.removeEffect(ExpansionEffects.SOUL.get());}
        }
        if(kind==Kind.INCENSE&&step%5==0)level.sendParticles(net.minecraft.core.particles.ParticleTypes.SMOKE,pos.getX()+.5,pos.getY()+1.05,pos.getZ()+.5,2,.1,.03,.1,.01);
        level.scheduleTick(pos,this,STEP_TICKS);
    }
    @Override public void onRemove(BlockState state,Level level,BlockPos pos,BlockState next,boolean moving){
        // Current burning unit is spent; unburned queued units are actual paid material, returned once.
        if(!level.isClientSide&&!moving&&!next.is(this)&&state.getValue(FUEL)>1)popResource(level,pos,new ItemStack(ExpansionContent.item("lantern_oil"),state.getValue(FUEL)-1));
        super.onRemove(state,level,pos,next,moving);
    }
}
