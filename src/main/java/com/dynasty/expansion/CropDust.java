package com.dynasty.expansion;

import net.minecraft.world.*;
import net.minecraft.world.item.*;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.block.*;
import net.minecraft.world.phys.*;
import net.minecraft.world.level.ClipContext;
import net.minecraft.network.chat.Component;

/** Original material ID, native use-on-block and original finite flee goal; no crop/world manager. */
final class CropDust extends Item {
    CropDust(){super(new Properties());}
    @Override public InteractionResult useOn(UseOnContext c){
        var level=c.getLevel();var p=c.getPlayer();var pos=c.getClickedPos();var held=c.getItemInHand();
        if(c.getHand()!=InteractionHand.MAIN_HAND||p==null||!p.isAlive()||p.isSpectator()||held.isEmpty()||p.level()!=level
            ||p.distanceToSqr(Vec3.atCenterOf(pos))>36||!level.hasChunkAt(pos)||p.getCooldowns().isOnCooldown(this)
            ||!p.mayUseItemAt(pos,c.getClickedFace(),held)||!level.mayInteract(p,pos))return InteractionResult.PASS;
        var state=level.getBlockState(pos);if(!(state.getBlock() instanceof CropBlock)&&!state.is(Blocks.FARMLAND))return InteractionResult.PASS;
        if(level.isClientSide)return InteractionResult.SUCCESS;
        var pests=level.getEntitiesOfClass(SecondaryMob.class,new AABB(pos).inflate(8),m->m.isAlive()&&!m.isNoAi()&&m.cropPest()&&!m.isAlliedTo(p)&&m.distanceToSqr(Vec3.atCenterOf(pos))<=64
            &&level.clip(new ClipContext(Vec3.atCenterOf(pos).add(0,.5,0),m.getEyePosition(),ClipContext.Block.COLLIDER,ClipContext.Fluid.NONE,p)).getType()==HitResult.Type.MISS)
            .stream().sorted(java.util.Comparator.comparingDouble(m->m.distanceToSqr(Vec3.atCenterOf(pos)))).limit(12).toList();
        int changed=0;for(var mob:pests)if(mob.repelFromCrop(pos))changed++;
        if(changed==0)return InteractionResult.PASS;
        if(!p.getAbilities().instabuild)held.shrink(1);p.getCooldowns().addCooldown(this,SecondaryMob.CROP_FLEE_TICKS);
        p.displayClientMessage(Component.translatable("message.dynasty.cod4.crop_repel",changed),true);
        if(level instanceof net.minecraft.server.level.ServerLevel server)server.sendParticles(net.minecraft.core.particles.ParticleTypes.ASH,pos.getX()+.5,pos.getY()+.8,pos.getZ()+.5,6,.5,.1,.5,.01);
        return InteractionResult.CONSUME;
    }
}
