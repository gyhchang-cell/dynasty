package com.dynasty.blueprint.elite;

import com.dynasty.blueprint.BlueprintEntities;
import com.dynasty.blueprint.combat.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.syncher.*;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.Level;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.*;
import software.bernie.geckolib.util.GeckoLibUtil;
import java.util.UUID;

/** One entity changes from a breakable egg to a short-lived spider, never a second spawning cascade. */
public final class SpiderBrood extends Monster implements GeoEntity,Combatant {
    public static final String ID="tianzhu_brood";
    private static final EntityDataAccessor<Boolean> HATCHED=SynchedEntityData.defineId(SpiderBrood.class,EntityDataSerializers.BOOLEAN);
    private final AnimatableInstanceCache cache=GeckoLibUtil.createInstanceCache(this);
    private UUID owner,victim;
    private long born=-1,lastTick=-1,nextBite;
    public SpiderBrood(EntityType<? extends SpiderBrood> type,Level level){super(type,level);xpReward=0;}
    @Override protected void defineSynchedData(){super.defineSynchedData();entityData.define(HATCHED,false);}
    @Override protected void registerGoals(){}
    @Override public Faction faction(){return Faction.SPIRITS;}
    @Override public MobRole role(){return MobRole.MELEE;}
    public boolean hatched(){return entityData.get(HATCHED);}
    public boolean ownedBy(SpiderWoman caster){return caster.getUUID().equals(owner);}
    public void launch(SpiderWoman caster,LivingEntity target){owner=caster.getUUID();victim=target==null?null:target.getUUID();born=level().getGameTime();lastTick=born;setHealth(4);setPersistenceRequired();}
    @Override public void tick(){
        super.tick();if(level().isClientSide)return;
        if(!(level() instanceof ServerLevel world)||owner==null||born<0||world.getGameTime()<born||world.getGameTime()-born>=260
            ||!(world.getEntity(owner) instanceof SpiderWoman caster)||!caster.isAlive()||caster.distanceToSqr(this)>32*32){discard();return;}
        long now=world.getGameTime(),age=now-born;
        // Delayed unloaded eggs do not hatch on an arbitrary later frame.
        if(!hatched()&&now-lastTick>10){discard();return;}lastTick=now;
        if(!hatched()){getNavigation().stop();setDeltaMovement(0,getDeltaMovement().y,0);if(age>=60){entityData.set(HATCHED,true);setHealth(6);}else return;}
        var found=victim==null?null:world.getEntity(victim);var target=found instanceof LivingEntity living&&caster.enemy(living)?living:caster.getTarget();
        if(!caster.enemy(target))return;getNavigation().moveTo(target,1.15);
        if(distanceToSqr(target)<1.44&&hasLineOfSight(target)&&now>=nextBite){nextBite=now+20;if(target.hurt(damageSources().mobAttack(this),2))target.addEffect(new MobEffectInstance(BlueprintEntities.LANTERN_GLARE.get(),40,1),caster);}
    }
    @Override public void die(DamageSource source){super.die(source);discard();}
    @Override protected void dropAllDeathLoot(DamageSource source){}
    @Override public void addAdditionalSaveData(CompoundTag t){super.addAdditionalSaveData(t);if(owner!=null)t.putUUID("Owner",owner);if(victim!=null)t.putUUID("Victim",victim);t.putLong("Born",born);t.putLong("LastTick",lastTick);t.putBoolean("Hatched",hatched());t.putLong("NextBite",nextBite);}
    @Override public void readAdditionalSaveData(CompoundTag t){super.readAdditionalSaveData(t);owner=t.hasUUID("Owner")?t.getUUID("Owner"):null;victim=t.hasUUID("Victim")?t.getUUID("Victim"):null;born=t.contains("Born")?t.getLong("Born"):-1;lastTick=t.contains("LastTick")?t.getLong("LastTick"):-1;nextBite=Math.max(level().getGameTime()+1,t.getLong("NextBite"));entityData.set(HATCHED,t.getBoolean("Hatched"));}
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar c){c.add(new AnimationController<>(this,"body",0,state->{state.getController().setAnimation(RawAnimation.begin().thenLoop("animation."+ID+"."+(hatched()?"walk":"egg")));return software.bernie.geckolib.core.object.PlayState.CONTINUE;}));}
    @Override public AnimatableInstanceCache getAnimatableInstanceCache(){return cache;}
}
