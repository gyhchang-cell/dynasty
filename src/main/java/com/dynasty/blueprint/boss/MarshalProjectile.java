package com.dynasty.blueprint.boss;

import com.dynasty.blueprint.combat.CombatGeometry;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.syncher.*;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.item.*;
import net.minecraft.world.level.*;
import net.minecraft.world.phys.*;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.*;
import software.bernie.geckolib.util.GeckoLibUtil;
import java.util.*;

/** Native wall arrows, a clipped five-metre sand blade, or a finite pulsing blood crack. */
public final class MarshalProjectile extends AbstractArrow implements GeoEntity {
    public static final int SAND_BLADE=0,WALL_ARROW=1,BLOOD_FISSURE=2;
    private static final EntityDataAccessor<Integer> KIND=SynchedEntityData.defineId(MarshalProjectile.class,EntityDataSerializers.INT);
    private final AnimatableInstanceCache cache=GeckoLibUtil.createInstanceCache(this);
    private final Set<UUID> sandHits=new HashSet<>();
    private long born=-1,epoch=-1,lastTick=-1,lastPulse=-1;
    private Vec3 origin=Vec3.ZERO;
    public MarshalProjectile(EntityType<? extends MarshalProjectile> type,Level level){super(type,level);pickup=Pickup.DISALLOWED;}
    @Override protected void defineSynchedData(){super.defineSynchedData();entityData.define(KIND,0);}
    public int kind(){return entityData.get(KIND);}
    public String modelId(){return switch(kind()){case WALL_ARROW->"marshal_wall_arrow";case BLOOD_FISSURE->"marshal_blood_fissure";default->"marshal_sand_blade";};}
    public boolean ownedBy(BlindMarshal e){return getOwner()!=null&&getOwner().getUUID().equals(e.getUUID());}
    public void ignoreHits(Set<UUID> ids){ids.stream().limit(16).forEach(sandHits::add);}
    public void launch(BlindMarshal e,int kind,Vec3 at,Vec3 velocity){entityData.set(KIND,Math.max(0,Math.min(2,kind)));setOwner(e);born=level().getGameTime();epoch=e.attack().started();lastTick=born-1;origin=at;setPos(at);setDeltaMovement(velocity);setNoGravity(true);pickup=Pickup.DISALLOWED;setBaseDamage(e.getAttributeValue(Attributes.ATTACK_DAMAGE)*.55);setPierceLevel((byte)0);setCritArrow(false);var d=velocity.lengthSqr()>.001?velocity.normalize():e.fixedFacing();setYRot((float)Math.toDegrees(Math.atan2(-d.x,d.z)));setXRot((float)-Math.toDegrees(Math.atan2(d.y,d.horizontalDistance())));yRotO=getYRot();xRotO=getXRot();}
    @Override public boolean shouldRenderAtSqrDistance(double distance){return Double.isFinite(distance)&&distance<96*96;}
    @Override public void tick(){if(level() instanceof ServerLevel world){long now=world.getGameTime();if(!(getOwner() instanceof BlindMarshal caster)||!caster.isAlive()||born<0||now<born||now-born>=(kind()==BLOOD_FISSURE?100:kind()==WALL_ARROW?60:12)||lastTick>=0&&now-lastTick>1||now<lastTick||kind()!=BLOOD_FISSURE&&caster.attack().started()!=epoch||!caster.loaded(getBoundingBox().expandTowards(getDeltaMovement()).inflate(1))||distanceToSqr(caster)>40*40){discard();return;}lastTick=now;
        if(kind()==SAND_BLADE){var velocity=getDeltaMovement();var remaining=5-position().distanceTo(origin);if(remaining<=0){discard();return;}if(velocity.length()>remaining)velocity=velocity.normalize().scale(remaining);var end=position().add(velocity);var wall=world.clip(new ClipContext(position(),end,ClipContext.Block.COLLIDER,ClipContext.Fluid.NONE,this));var clipped=wall.getType()==HitResult.Type.MISS?end:wall.getLocation();var direction=clipped.subtract(position());double length=direction.length();
            if(length>.001)for(var victim:CombatGeometry.query(world,position(),direction.normalize(),CombatGeometry.Shape.STRIP,length,1.1,0,.55,caster::enemy).stream().limit(16).toList()){if(!caster.isAlive()||isRemoved())return;if(sandHits.size()<16&&!sandHits.contains(victim.getUUID())&&world.clip(new ClipContext(position(),victim.getEyePosition(),ClipContext.Block.COLLIDER,ClipContext.Fluid.NONE,this)).getType()==HitResult.Type.MISS){sandHits.add(victim.getUUID());victim.hurt(caster.damageSources().mobAttack(caster),(float)caster.getAttributeValue(Attributes.ATTACK_DAMAGE)*1.2F);}}
            setPos(clipped);if(wall.getType()!=HitResult.Type.MISS||position().distanceTo(origin)>=4.999)discard();baseTick();return;
        }
        if(kind()==BLOOD_FISSURE&&now-born>=10&&(now-born)%10==0&&now-lastPulse>=10){lastPulse=now;for(var victim:world.getEntitiesOfClass(LivingEntity.class,new AABB(position(),position()).inflate(.8,.6,.8),caster::enemy).stream().limit(16).toList()){if(!caster.isAlive()||isRemoved())return;if(world.clip(new ClipContext(position().add(0,.3,0),victim.getEyePosition(),ClipContext.Block.COLLIDER,ClipContext.Fluid.NONE,this)).getType()==HitResult.Type.MISS)victim.hurt(caster.damageSources().mobAttack(caster),(float)caster.getAttributeValue(Attributes.ATTACK_DAMAGE)*.45F);}}
    }if(kind()==SAND_BLADE){setPos(position().add(getDeltaMovement()));baseTick();}else super.tick();}
    @Override protected boolean canHitEntity(Entity e){return kind()==WALL_ARROW&&getOwner() instanceof BlindMarshal caster&&e instanceof LivingEntity living&&caster.enemy(living)&&super.canHitEntity(e);}
    @Override protected void onHitEntity(EntityHitResult hit){if(kind()==WALL_ARROW)super.onHitEntity(hit);discard();}
    @Override protected void onHitBlock(BlockHitResult hit){discard();}
    @Override protected ItemStack getPickupItem(){return new ItemStack(Items.ARROW);}
    @Override public void addAdditionalSaveData(CompoundTag t){super.addAdditionalSaveData(t);t.putInt("MarshalKind",kind());t.putLong("MarshalBorn",born);t.putLong("MarshalEpoch",epoch);t.putLong("MarshalLastTick",lastTick);t.putLong("MarshalLastPulse",lastPulse);t.putDouble("MarshalOriginX",origin.x);t.putDouble("MarshalOriginY",origin.y);t.putDouble("MarshalOriginZ",origin.z);var ids=new net.minecraft.nbt.ListTag();for(var id:sandHits){var n=new CompoundTag();n.putUUID("Id",id);ids.add(n);}t.put("MarshalSandHits",ids);}
    @Override public void readAdditionalSaveData(CompoundTag t){super.readAdditionalSaveData(t);entityData.set(KIND,Math.max(0,Math.min(2,t.getInt("MarshalKind"))));born=t.contains("MarshalBorn")?t.getLong("MarshalBorn"):-1;epoch=t.getLong("MarshalEpoch");lastTick=t.contains("MarshalLastTick")?t.getLong("MarshalLastTick"):-1;lastPulse=t.contains("MarshalLastPulse")?t.getLong("MarshalLastPulse"):-1;origin=new Vec3(t.getDouble("MarshalOriginX"),t.getDouble("MarshalOriginY"),t.getDouble("MarshalOriginZ"));if(!Double.isFinite(origin.lengthSqr())||origin.distanceToSqr(position())>40*40)born=-1;sandHits.clear();for(var row:t.getList("MarshalSandHits",10)){var n=(CompoundTag)row;if(n.hasUUID("Id")&&sandHits.size()<16)sandHits.add(n.getUUID("Id"));}pickup=Pickup.DISALLOWED;setNoGravity(true);}
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar c){c.add(new AnimationController<MarshalProjectile>(this,"spell",0,s->{s.setAnimation(RawAnimation.begin().thenLoop("animation."+modelId()+".idle"));return software.bernie.geckolib.core.object.PlayState.CONTINUE;}));}
    @Override public AnimatableInstanceCache getAnimatableInstanceCache(){return cache;}
}
