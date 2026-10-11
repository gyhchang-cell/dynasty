package com.dynasty.blueprint.elite;

import com.dynasty.blueprint.combat.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.syncher.*;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.*;
import software.bernie.geckolib.util.GeckoLibUtil;
import java.util.UUID;

/** Four lightweight summons at most; shooting one converts its burst to the player's counterattack. */
public final class ClockworkSpider extends Monster implements GeoEntity,Combatant {
    public static final String ID="yanshi_clockwork_spider";
    private static final EntityDataAccessor<Long> FUSE=SynchedEntityData.defineId(ClockworkSpider.class,EntityDataSerializers.LONG);
    private final AnimatableInstanceCache cache=GeckoLibUtil.createInstanceCache(this);
    private UUID owner,victim;
    private long born=-1;
    private boolean exploded;
    public ClockworkSpider(EntityType<? extends ClockworkSpider> type,Level level){super(type,level);xpReward=0;}
    @Override public Faction faction(){return Faction.CONSTRUCT;}
    @Override public MobRole role(){return MobRole.MELEE;}
    @Override protected void registerGoals(){}
    @Override protected void defineSynchedData(){super.defineSynchedData();entityData.define(FUSE,-1L);}
    public long fuseStart(){return entityData.get(FUSE);}
    public boolean ownedBy(Mechanist caster){return caster.getUUID().equals(owner);}
    public void launch(Mechanist caster,UUID target,int n){owner=caster.getUUID();victim=target;born=level().getGameTime();setPos(caster.position().add(0,1.4,0));
        double angle=n*Math.PI/2+Math.toRadians(caster.getYRot());setDeltaMovement(Math.sin(angle)*.3,.45,Math.cos(angle)*.3);setPersistenceRequired();}
    @Override public void tick(){
        super.tick();if(level().isClientSide)return;
        if(!(level() instanceof ServerLevel world)||owner==null||born<0||world.getGameTime()<born||world.getGameTime()-born>=120
                ||!(world.getEntity(owner) instanceof Mechanist caster)||!caster.isAlive()||caster.distanceToSqr(this)>32*32){discard();return;}
        var found=victim==null?null:world.getEntity(victim);var target=found instanceof LivingEntity living&&caster.enemy(living)?living:caster.getTarget();
        long now=world.getGameTime();
        if(caster.enemy(target)&&distanceToSqr(target)<=16*16){
            if(onGround())getNavigation().moveTo(target,1.15);
            if(fuseStart()<0&&distanceToSqr(target)<2.25&&hasLineOfSight(target)){entityData.set(FUSE,now);playSound(SoundEvents.CREEPER_PRIMED,.55F,1.6F);}
        }
        if(fuseStart()>=0){getNavigation().stop();if(now-fuseStart()>=10){burst(caster,null);discard();}}
    }
    private void burst(Mechanist caster,LivingEntity counter){
        if(exploded||!(level() instanceof ServerLevel world))return;exploded=true;
        for(var hit:CombatGeometry.query(world,position(),Vec3.ZERO,CombatGeometry.Shape.CIRCLE,1.5,0,360,1.5,e->e!=this&&e.isAlive()&&!e.isSpectator()&&hasLineOfSight(e)
                &&(counter==null?caster.enemy(e):e!=counter&&!Combatant.allied(counter,e)&&!(e instanceof Player))))
            hit.hurt(damageSources().explosion(this,counter==null?caster:counter),6);
        world.sendParticles(net.minecraft.core.particles.ParticleTypes.EXPLOSION,getX(),getY()+.2,getZ(),4,.3,.2,.3,.01);playSound(SoundEvents.GENERIC_EXPLODE,.6F,1.5F);
    }
    @Override public void die(DamageSource source){
        if(!exploded&&level() instanceof ServerLevel world&&owner!=null&&world.getEntity(owner) instanceof Mechanist caster&&caster.isAlive()
                &&source.getEntity() instanceof LivingEntity killer)burst(caster,killer);
        super.die(source);discard();
    }
    @Override protected void dropAllDeathLoot(DamageSource source){}
    @Override public void addAdditionalSaveData(CompoundTag t){super.addAdditionalSaveData(t);if(owner!=null)t.putUUID("Owner",owner);if(victim!=null)t.putUUID("Victim",victim);t.putLong("Born",born);t.putLong("Fuse",fuseStart());t.putBoolean("Exploded",exploded);}
    @Override public void readAdditionalSaveData(CompoundTag t){super.readAdditionalSaveData(t);owner=t.hasUUID("Owner")?t.getUUID("Owner"):null;victim=t.hasUUID("Victim")?t.getUUID("Victim"):null;born=t.contains("Born")?t.getLong("Born"):-1;exploded=t.getBoolean("Exploded");
        // A loaded, already-lit micro-fuse is spent safely rather than detonating on a delayed frame.
        entityData.set(FUSE,-1L);if(t.getLong("Fuse")>=0||exploded)born=-1;}
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar c){c.add(new AnimationController<>(this,"body",0,state->{state.getController().setAnimation(RawAnimation.begin().thenLoop("animation."+ID+"."+(fuseStart()>=0?"fuse":"walk")));return software.bernie.geckolib.core.object.PlayState.CONTINUE;}));}
    @Override public AnimatableInstanceCache getAnimatableInstanceCache(){return cache;}
}
