package com.dynasty.blueprint.elite;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.entity.*;
import net.minecraft.world.effect.*;
import net.minecraft.world.level.*;
import net.minecraft.world.phys.*;

/** Native visual cloud and twelve bounded hostile contacts, once per second. */
public final class AlchemistZone extends AreaEffectCloud {
    private long expires=-1,nextPulse;private boolean fire;
    public AlchemistZone(EntityType<? extends AlchemistZone> t,Level level){super(t,level);}
    public boolean ownedBy(Alchemist parent){return getOwner()!=null&&getOwner().getUUID().equals(parent.getUUID());}
    public void launch(Alchemist caster,boolean fire){setOwner(caster);this.fire=fire;expires=level().getGameTime()+(fire?160:120);nextPulse=level().getGameTime()+20;setRadius(fire?5:2.5F);setWaitTime(0);setDuration(fire?160:120);setRadiusOnUse(0);setDurationOnUse(0);setRadiusPerTick(0);setFixedColor(fire?0xB66D35:0xD9B457);setParticle(fire?net.minecraft.core.particles.ParticleTypes.FLAME:net.minecraft.core.particles.ParticleTypes.ENTITY_EFFECT);}
    @Override public void tick(){
        if(level().isClientSide){super.tick();return;}
        if(expires<0||level().getGameTime()>=expires||!(getOwner() instanceof Alchemist caster)||!caster.isAlive()||distanceToSqr(caster)>32*32){discard();return;}
        baseTick();if(level().getGameTime()<nextPulse)return;nextPulse=level().getGameTime()+20;
        for(var target:level().getEntitiesOfClass(LivingEntity.class,getBoundingBox().inflate(0,.6,0),caster::enemy).stream().limit(12).toList()){
            if(target.position().subtract(position()).horizontalDistanceSqr()>getRadius()*getRadius()||Math.abs(target.getY()-getY())>1||level().clip(new ClipContext(position().add(0,.4,0),target.getEyePosition(),ClipContext.Block.COLLIDER,ClipContext.Fluid.NONE,this)).getType()!=HitResult.Type.MISS)continue;
            if(fire){if(target.hurt(damageSources().indirectMagic(this,caster),3))target.setSecondsOnFire(2);}
            else target.addEffect(new MobEffectInstance(MobEffects.POISON,40,1),caster);
        }
    }
    @Override protected void addAdditionalSaveData(CompoundTag t){super.addAdditionalSaveData(t);t.putLong("Expires",expires);t.putLong("NextPulse",nextPulse);t.putBoolean("Fire",fire);}
    @Override protected void readAdditionalSaveData(CompoundTag t){super.readAdditionalSaveData(t);fire=t.getBoolean("Fire");long now=level().getGameTime();expires=t.contains("Expires")?Math.min(now+(fire?160:120),t.getLong("Expires")):-1;nextPulse=Math.min(now+20,Math.max(now+1,t.getLong("NextPulse")));setRadius(fire?5:2.5F);}
}
