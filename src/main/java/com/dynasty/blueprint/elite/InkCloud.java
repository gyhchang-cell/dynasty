package com.dynasty.blueprint.elite;

import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.effect.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.level.*;
import net.minecraft.world.phys.*;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.*;
import software.bernie.geckolib.util.GeckoLibUtil;

/** Twenty harmless ticks as an ink pellet, then an absolute-lived cloud with vanilla finite blindness. */
public final class InkCloud extends AreaEffectCloud implements GeoEntity {
    public static final String ID="assassin_finite_ink_cloud";
    private final AnimatableInstanceCache cache=GeckoLibUtil.createInstanceCache(this);
    private long born=-1,expires=-1,nextPulse;
    public InkCloud(EntityType<? extends InkCloud> t,Level level){super(t,level);}
    public boolean ownedBy(InkAssassin caster){return getOwner()!=null&&getOwner().getUUID().equals(caster.getUUID());}
    public void launch(InkAssassin caster){setOwner(caster);born=level().getGameTime();expires=born+100;nextPulse=born+20;setWaitTime(20);setDuration(100);setRadius(1.5F);setRadiusOnUse(0);setDurationOnUse(0);setRadiusPerTick(0);setFixedColor(0x1F2428);setWaiting(true);setParticle(ParticleTypes.SMOKE);}
    @Override public void tick(){
        if(level().isClientSide){super.tick();return;}
        long now=level().getGameTime();if(born<0||expires<0||now<born||now>=expires||!(getOwner() instanceof InkAssassin caster)||!caster.isAlive()||distanceToSqr(caster)>32*32){discard();return;}
        baseTick();setWaiting(now-born<20);if(isWaiting()||now<nextPulse)return;nextPulse=now+20;
        for(var target:level().getEntitiesOfClass(LivingEntity.class,getBoundingBox().inflate(0,1.1,0),caster::enemy).stream().limit(12).toList()){
            if(target.getBoundingBox().getCenter().distanceToSqr(position().add(0,.6,0))>4||level().clip(new ClipContext(position().add(0,.5,0),target.getEyePosition(),ClipContext.Block.COLLIDER,ClipContext.Fluid.NONE,this)).getType()!=HitResult.Type.MISS)continue;
            target.addEffect(new MobEffectInstance(MobEffects.BLINDNESS,100),caster);
        }
    }
    @Override protected void addAdditionalSaveData(CompoundTag t){super.addAdditionalSaveData(t);t.putLong("InkBorn",born);t.putLong("InkExpires",expires);t.putLong("InkPulse",nextPulse);}
    @Override protected void readAdditionalSaveData(CompoundTag t){super.readAdditionalSaveData(t);long now=level().getGameTime();born=t.contains("InkBorn")?t.getLong("InkBorn"):-1;expires=t.contains("InkExpires")?Math.min(now+100,t.getLong("InkExpires")):-1;nextPulse=Math.min(now+20,Math.max(now+1,t.getLong("InkPulse")));setRadius(1.5F);setWaiting(now-born<20);setParticle(ParticleTypes.SMOKE);}
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar c){c.add(new AnimationController<>(this,"pellet",0,state->{state.getController().setAnimation(RawAnimation.begin().thenLoop("animation."+ID+".idle"));return software.bernie.geckolib.core.object.PlayState.CONTINUE;}));}
    @Override public AnimatableInstanceCache getAnimatableInstanceCache(){return cache;}
}
