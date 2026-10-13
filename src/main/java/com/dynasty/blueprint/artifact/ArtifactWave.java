package com.dynasty.blueprint.artifact;

import net.minecraft.core.*;
import net.minecraft.core.particles.BlockParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.*;
import net.minecraft.network.syncher.*;
import net.minecraft.server.level.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.level.*;
import net.minecraft.world.phys.*;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.*;
import software.bernie.geckolib.util.GeckoLibUtil;
import java.util.*;

/** One bounded moving earth crest, ten loaded floor cells, at most16distinct accepted victims. */
public final class ArtifactWave extends Entity implements GeoEntity {
    private static final EntityDataAccessor<Long> BORN=SynchedEntityData.defineId(ArtifactWave.class,EntityDataSerializers.LONG);
    private final AnimatableInstanceCache cache=GeckoLibUtil.createInstanceCache(this);
    private UUID owner;
    private Vec3 origin=Vec3.ZERO,facing=new Vec3(0,0,1);
    private long lastTick=-1;
    private int lastCell=-1;
    private float damage;
    private final Set<UUID> hits=new HashSet<>();
    public ArtifactWave(EntityType<? extends ArtifactWave> type,Level level){super(type,level);setNoGravity(true);}
    @Override protected void defineSynchedData(){entityData.define(BORN,-1L);}
    public long born(){return entityData.get(BORN);}
    public boolean ownedBy(ServerPlayer p){return p.getUUID().equals(owner);}
    public void begin(ServerPlayer p,Vec3 f,BlockPos floor){damage=(float)Math.max(0,Math.min(512,p.getAttributeValue(Attributes.ATTACK_DAMAGE)*1.5));owner=p.getUUID();origin=Vec3.atBottomCenterOf(floor);facing=f;entityData.set(BORN,level().getGameTime());setPos(origin);setYRot((float)Math.toDegrees(Math.atan2(-f.x,f.z)));}
    public static BlockPos floor(ServerLevel w,Vec3 at){var b=BlockPos.containing(at);for(int y=1;y>=-1;y--){var p=b.above(y);if(p.getY()<w.getMinBuildHeight()+1||p.getY()+3>=w.getMaxBuildHeight()||!ArtifactAbility.loaded(w,new AABB(p).inflate(2))||!w.getWorldBorder().isWithinBounds(p))return null;if(w.isEmptyBlock(p)&&w.getFluidState(p).isEmpty()&&w.getBlockState(p.below()).isFaceSturdy(w,p.below(),Direction.UP))return p;}return null;}
    @Override public void tick(){super.tick();if(!(level() instanceof ServerLevel w))return;long now=w.getGameTime();var entity=owner==null?null:w.getEntity(owner);if(!(entity instanceof ServerPlayer p)||!p.isAlive()||p.isSpectator()||born()<0||now<born()||now-born()>=20||lastTick>=0&&(now<lastTick||now-lastTick>1)||p.distanceToSqr(this)>32*32){discard();return;}lastTick=now;int cell=(int)(now-born())/2;if(cell==lastCell)return;lastCell=cell;var wanted=origin.add(facing.scale(cell));var ground=floor(w,wanted);if(ground==null||Math.abs(ground.getY()-getY())>1){discard();return;}
        var at=Vec3.atBottomCenterOf(ground);var wall=w.clip(new ClipContext(position().add(0,.35,0),at.add(0,.35,0),ClipContext.Block.COLLIDER,ClipContext.Fluid.NONE,this));if(wall.getType()!=HitResult.Type.MISS){discard();return;}setPos(at);
        for(var target:LongyinAbility.WAVE.targets(p,at.add(0,.3,0),facing))if(hits.size()<16&&!hits.contains(target.getUUID())&&w.clip(new ClipContext(at.add(0,.35,0),target.getEyePosition(),ClipContext.Block.COLLIDER,ClipContext.Fluid.NONE,this)).getType()==HitResult.Type.MISS&&target.hurt(p.damageSources().playerAttack(p),damage)){hits.add(target.getUUID());double resistance=Math.max(0,Math.min(1,target.getAttributeValue(Attributes.KNOCKBACK_RESISTANCE)));target.setDeltaMovement(target.getDeltaMovement().x,Math.max(target.getDeltaMovement().y,.7*(1-resistance)),target.getDeltaMovement().z);target.hurtMarked=true;}
        w.sendParticles(new BlockParticleOption(ParticleTypes.BLOCK,w.getBlockState(ground.below())),at.x,at.y+.3,at.z,6,.35,.15,.35,.04);
    }
    @Override public boolean shouldRenderAtSqrDistance(double d){return Double.isFinite(d)&&d<64*64;}
    @Override protected void addAdditionalSaveData(CompoundTag t){if(owner!=null)t.putUUID("Owner",owner);t.putFloat("Damage",damage);t.putLong("Born",born());t.putLong("LastTick",lastTick);t.putInt("Cell",lastCell);t.putDouble("OriginX",origin.x);t.putDouble("OriginY",origin.y);t.putDouble("OriginZ",origin.z);t.putDouble("FacingX",facing.x);t.putDouble("FacingZ",facing.z);var rows=new ListTag();for(var id:hits){var n=new CompoundTag();n.putUUID("Id",id);rows.add(n);}t.put("Hits",rows);}
    @Override protected void readAdditionalSaveData(CompoundTag t){damage=t.getFloat("Damage");if(!Float.isFinite(damage)||damage<0||damage>512)damage=0;owner=t.hasUUID("Owner")?t.getUUID("Owner"):null;entityData.set(BORN,t.contains("Born")?t.getLong("Born"):-1);lastTick=t.contains("LastTick")?t.getLong("LastTick"):-1;lastCell=t.getInt("Cell");origin=new Vec3(t.getDouble("OriginX"),t.getDouble("OriginY"),t.getDouble("OriginZ"));facing=new Vec3(t.getDouble("FacingX"),0,t.getDouble("FacingZ"));if(!Double.isFinite(origin.lengthSqr())||!Double.isFinite(facing.lengthSqr())||facing.lengthSqr()<.9||facing.lengthSqr()>1.1||origin.distanceToSqr(position())>12*12)entityData.set(BORN,-1L);else facing=facing.normalize();hits.clear();for(var row:t.getList("Hits",10)){var n=(CompoundTag)row;if(n.hasUUID("Id")&&hits.size()<16)hits.add(n.getUUID("Id"));}setNoGravity(true);}
    @Override public net.minecraft.network.protocol.Packet<net.minecraft.network.protocol.game.ClientGamePacketListener> getAddEntityPacket(){return net.minecraftforge.network.NetworkHooks.getEntitySpawningPacket(this);}
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar c){c.add(new AnimationController<ArtifactWave>(this,"crest",0,s->{s.setAnimation(RawAnimation.begin().thenLoop("animation.longyin_ground_crest.idle"));return software.bernie.geckolib.core.object.PlayState.CONTINUE;}));}
    @Override public AnimatableInstanceCache getAnimatableInstanceCache(){return cache;}
}
