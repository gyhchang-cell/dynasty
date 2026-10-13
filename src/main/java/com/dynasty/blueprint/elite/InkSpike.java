package com.dynasty.blueprint.elite;

import com.dynasty.blueprint.combat.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.Level;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.*;
import software.bernie.geckolib.util.GeckoLibUtil;
import java.util.UUID;

/** A living, zero-XP anchor so the native player's sweeping attack can actually break the field. */
public final class InkSpike extends Monster implements GeoEntity,Combatant {
    public static final String ID="assassin_ink_bamboo_anchor";
    private UUID owner;
    private long castStart=-1,expires=-1,lastTick=-1;
    private final AnimatableInstanceCache cache=GeckoLibUtil.createInstanceCache(this);
    public InkSpike(EntityType<? extends InkSpike> t,Level level){super(t,level);xpReward=0;setNoAi(true);setNoGravity(true);}
    @Override protected void registerGoals(){}
    @Override public Faction faction(){return Faction.CONSTRUCT;}
    @Override public MobRole role(){return MobRole.MELEE;}
    public boolean ownedBy(InkAssassin caster){return caster.getUUID().equals(owner);}
    public long castStart(){return castStart;}
    public void launch(InkAssassin caster){owner=caster.getUUID();castStart=caster.skillStart();expires=castStart+56;lastTick=level().getGameTime();setPersistenceRequired();}
    @Override public void tick(){super.tick();if(level().isClientSide)return;long now=level().getGameTime();if(owner==null||expires<0||now>=expires||lastTick>=0&&(now-lastTick>1||now<lastTick)||!(level() instanceof ServerLevel w)||!(w.getEntity(owner) instanceof InkAssassin caster)||!caster.isAlive()||caster.skillId()!=412||caster.skillStart()!=castStart||distanceToSqr(caster)>32*32){discard();return;}lastTick=now;}
    @Override public boolean hurt(DamageSource source,float amount){boolean hit=super.hurt(source,amount);if(hit&&!level().isClientSide&&level() instanceof ServerLevel w&&owner!=null&&w.getEntity(owner) instanceof InkAssassin caster)caster.breakField(this);return hit;}
    @Override public void die(DamageSource source){super.die(source);if(level() instanceof ServerLevel w&&owner!=null&&w.getEntity(owner) instanceof InkAssassin caster)caster.breakField(this);discard();}
    @Override protected void dropAllDeathLoot(DamageSource source){}
    @Override public void addAdditionalSaveData(CompoundTag t){super.addAdditionalSaveData(t);if(owner!=null)t.putUUID("InkOwner",owner);t.putLong("InkCast",castStart);t.putLong("InkExpires",expires);t.putLong("InkLastTick",lastTick);}
    @Override public void readAdditionalSaveData(CompoundTag t){super.readAdditionalSaveData(t);owner=t.hasUUID("InkOwner")?t.getUUID("InkOwner"):null;castStart=t.contains("InkCast")?t.getLong("InkCast"):-1;expires=t.contains("InkExpires")?Math.min(level().getGameTime()+56,t.getLong("InkExpires")):-1;lastTick=t.contains("InkLastTick")?t.getLong("InkLastTick"):-1;setNoAi(true);setNoGravity(true);}
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar c){c.add(new AnimationController<>(this,"body",0,state->{state.getController().setAnimation(RawAnimation.begin().thenLoop("animation."+ID+".idle"));return software.bernie.geckolib.core.object.PlayState.CONTINUE;}));}
    @Override public AnimatableInstanceCache getAnimatableInstanceCache(){return cache;}
}
