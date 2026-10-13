package com.dynasty.blueprint.elite;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.syncher.*;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.phys.*;
import net.minecraftforge.network.NetworkHooks;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.*;
import software.bernie.geckolib.util.GeckoLibUtil;
import java.util.UUID;

/** One60tick visible flame tube or one of five finite ground cracks. No block-fire placement. */
public final class SuanniEffect extends Entity implements GeoEntity {
    public static final String FLAME_ID="suanni_fixed_flame_jet",CRACK_ID="suanni_ground_fire_crack";
    private static final EntityDataAccessor<Float> LENGTH=SynchedEntityData.defineId(SuanniEffect.class,EntityDataSerializers.FLOAT);
    private final AnimatableInstanceCache cache=GeckoLibUtil.createInstanceCache(this);
    private UUID owner;
    private long born=-1,epoch=-1,lastTick=-1,lastPulse=-1;
    public SuanniEffect(EntityType<? extends SuanniEffect> type,Level level){super(type,level);setNoGravity(true);}
    public boolean flame(){return getType()==EliteContent.SUANNI_FLAME.get();}
    public String modelId(){return flame()?FLAME_ID:CRACK_ID;}
    public float length(){return entityData.get(LENGTH);}
    public boolean ownedBy(BronzeSuanni e){return e.getUUID().equals(owner);}
    // Keep the eight-metre jet visible beyond the tiny server anchor's default6.4m cutoff.
    @Override public boolean shouldRenderAtSqrDistance(double distance){return Double.isFinite(distance)&&distance<64*64;}
    @Override protected void defineSynchedData(){entityData.define(LENGTH,0F);}
    public void launch(BronzeSuanni caster,Vec3 at,long action){owner=caster.getUUID();epoch=action;born=level().getGameTime();lastTick=born-1;setPos(at);if(flame())updateFlame(caster);}
    private void updateFlame(BronzeSuanni caster){long age=level().getGameTime()-epoch;var d=caster.headDirection(age);setPos(caster.fireMuzzle(age));setYRot((float)Math.toDegrees(Math.atan2(-d.x,d.z)));entityData.set(LENGTH,(float)caster.flameLength(age));}
    @Override public void tick(){super.tick();if(level() instanceof ServerLevel world){long now=world.getGameTime();var source=owner==null?null:world.getEntity(owner);
        if(!(source instanceof BronzeSuanni caster)||!caster.isAlive()||born<0||now<born||now-born>=60||lastTick>=0&&now-lastTick>1||now<lastTick||distanceToSqr(caster)>16*16||!caster.loaded(getBoundingBox().inflate(2))){discard();return;}lastTick=now;
        if(flame()){long age=now-epoch;if(caster.skillId()!=451||caster.attack().started()!=epoch||age<24||age>=84){discard();return;}updateFlame(caster);return;}
        if((now-born)%10!=0)return;
        pulse(caster);
    }}
    public void pulse(BronzeSuanni caster){if(!(level() instanceof ServerLevel world)||!caster.isAlive()||isRemoved()||lastPulse>=0&&level().getGameTime()-lastPulse<10)return;lastPulse=level().getGameTime();
        for(var victim:world.getEntitiesOfClass(LivingEntity.class,getBoundingBox().inflate(.35,.4,.35),caster::enemy).stream().limit(16).toList()){
            if(!caster.isAlive())return;if(world.clip(new ClipContext(position().add(0,.6,0),victim.getEyePosition(),ClipContext.Block.COLLIDER,ClipContext.Fluid.NONE,this)).getType()!=HitResult.Type.MISS)continue;
            if(victim.hurt(caster.damageSources().mobAttack(caster),(float)caster.getAttributeValue(Attributes.ATTACK_DAMAGE)*.6F))victim.setSecondsOnFire(3);
        }
    }
    @Override protected void readAdditionalSaveData(CompoundTag t){owner=t.hasUUID("SuanniOwner")?t.getUUID("SuanniOwner"):null;born=t.contains("SuanniBorn")?t.getLong("SuanniBorn"):-1;epoch=t.getLong("SuanniEpoch");lastTick=t.contains("SuanniLastTick")?t.getLong("SuanniLastTick"):-1;lastPulse=t.contains("SuanniLastPulse")?t.getLong("SuanniLastPulse"):-1;float length=t.getFloat("FlameLength");entityData.set(LENGTH,Float.isFinite(length)?Math.max(0,Math.min(8,length)):0);}
    @Override protected void addAdditionalSaveData(CompoundTag t){if(owner!=null)t.putUUID("SuanniOwner",owner);t.putLong("SuanniBorn",born);t.putLong("SuanniEpoch",epoch);t.putLong("SuanniLastTick",lastTick);t.putLong("SuanniLastPulse",lastPulse);t.putFloat("FlameLength",length());}
    @Override public Packet<ClientGamePacketListener> getAddEntityPacket(){return NetworkHooks.getEntitySpawningPacket(this);}
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar c){c.add(new AnimationController<SuanniEffect>(this,"effect",0,s->{s.setAnimation(RawAnimation.begin().thenLoop("animation."+modelId()+".idle"));return software.bernie.geckolib.core.object.PlayState.CONTINUE;}));}
    @Override public AnimatableInstanceCache getAnimatableInstanceCache(){return cache;}
}
