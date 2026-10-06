package com.dynasty.blueprint;

import java.util.UUID;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.level.Level;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.*;

/** One destructible cage with six visual roots; no world blocks or per-bone entities. */
public final class RootSnare extends Entity implements GeoEntity {
    private static final EntityDataAccessor<Long> BORN=SynchedEntityData.defineId(RootSnare.class,EntityDataSerializers.LONG);
    private final AnimatableInstanceCache cache=software.bernie.geckolib.util.GeckoLibUtil.createInstanceCache(this);
    private UUID owner;private long expires=-1,nextPulse;private float health=12,partial;
    public RootSnare(EntityType<? extends RootSnare> type,Level level){super(type,level);}
    public void activate(TemplateMob caster){owner=caster.getUUID();entityData.set(BORN,level().getGameTime());expires=level().getGameTime()+60;nextPulse=level().getGameTime()+10;}
    @Override protected void defineSynchedData(){entityData.define(BORN,-1L);}
    public float age(float partialTick){return entityData.get(BORN)<0?0:Math.max(0,level().getGameTime()-entityData.get(BORN)+partialTick);}
    @Override public void tick(){
        baseTick();if(!(level() instanceof net.minecraft.server.level.ServerLevel server))return;
        if(health<=0||expires<0||server.getGameTime()>=expires){discard();return;}
        var caster=owner==null?null:server.getEntity(owner);
        if(caster!=null&&!caster.isAlive()){discard();return;}
        if(server.getGameTime()<nextPulse)return;nextPulse=server.getGameTime()+10;
        for(var enemy:server.getEntitiesOfClass(net.minecraft.world.entity.LivingEntity.class,getBoundingBox(),e->e.isAlive()&&!e.isSpectator())){
            if(enemy.position().subtract(position()).horizontalDistanceSqr()>1.21
                ||enemy instanceof net.minecraft.world.entity.player.Player p&&p.isCreative()
                ||enemy instanceof com.dynasty.blueprint.combat.Combatant c&&c.faction()==com.dynasty.blueprint.combat.Faction.WOODLAND)continue;
            enemy.addEffect(new net.minecraft.world.effect.MobEffectInstance(BlueprintEntities.ROOT_GRIP.get(),12),caster);
            if((int)age(0)%20<10)enemy.hurt(damageSources().inWall(),2);
        }
    }
    @Override public boolean isPickable(){return !isRemoved();}
    @Override public boolean canBeHitByProjectile(){return isPickable();}
    @Override public boolean hurt(net.minecraft.world.damagesource.DamageSource source,float damage){
        if(level().isClientSide||isRemoved()||damage<=0||source.getEntity() instanceof com.dynasty.blueprint.combat.Combatant c&&c.faction()==com.dynasty.blueprint.combat.Faction.WOODLAND)return false;
        health-=source.getEntity() instanceof net.minecraft.world.entity.player.Player p&&p.isCreative()?12:damage;
        playSound(net.minecraft.sounds.SoundEvents.WOOD_BREAK,.8F,.8F);
        if(health<=0){
            ((net.minecraft.server.level.ServerLevel)level()).sendParticles(new net.minecraft.core.particles.BlockParticleOption(net.minecraft.core.particles.ParticleTypes.BLOCK,net.minecraft.world.level.block.Blocks.DARK_OAK_LOG.defaultBlockState()),getX(),getY()+.8,getZ(),16,.8,.6,.8,.04);
            discard();
        }
        return true;
    }
    @Override protected void addAdditionalSaveData(CompoundTag t){if(owner!=null)t.putUUID("Owner",owner);t.putLong("Born",entityData.get(BORN));t.putLong("Expires",expires);t.putLong("NextPulse",nextPulse);t.putFloat("Health",health);}
    @Override protected void readAdditionalSaveData(CompoundTag t){owner=t.hasUUID("Owner")?t.getUUID("Owner"):null;entityData.set(BORN,t.getLong("Born"));expires=t.getLong("Expires");nextPulse=Math.max(level().getGameTime()+1,t.getLong("NextPulse"));health=Math.max(0,Math.min(12,t.getFloat("Health")));}
    @Override public net.minecraft.network.protocol.Packet<net.minecraft.network.protocol.game.ClientGamePacketListener> getAddEntityPacket(){return net.minecraftforge.network.NetworkHooks.getEntitySpawningPacket(this);}
    @Override public AnimatableInstanceCache getAnimatableInstanceCache(){return cache;}
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar registrar){
        registrar.add(new AnimationController<RootSnare>(this,"roots",0,state->{partial=state.getPartialTick();return state.setAndContinue(RawAnimation.begin().thenPlayAndHold("animation.root_snare.grow"));}){
            @Override protected double adjustTick(double tick){boolean resetting=shouldResetTick;double local=super.adjustTick(tick);
                return resetting||getAnimationState()!=AnimationController.State.RUNNING?local:age(partial);}
        });
    }
}
