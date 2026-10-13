package com.dynasty.blueprint.boss;
import com.dynasty.blueprint.combat.CombatGeometry;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.syncher.*;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.level.*;
import net.minecraft.world.phys.*;
import net.minecraftforge.network.NetworkHooks;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.*;
import software.bernie.geckolib.util.GeckoLibUtil;
import java.util.UUID;

/** Original finite six-metre oil patch or one of six growing sixteen-metre ground fissures. */
public final class CauldronGroundSpell extends Entity implements GeoEntity {
    public static final String OIL_ID="taoyan_bounded_corpse_oil",CRACK_ID="taoyan_growing_fire_fissure";
    private static final EntityDataAccessor<Float> LENGTH=SynchedEntityData.defineId(CauldronGroundSpell.class,EntityDataSerializers.FLOAT);
    private final AnimatableInstanceCache cache=GeckoLibUtil.createInstanceCache(this);
    private UUID owner;
    private long born=-1,lastTick=-1,lastPulse=-1;
    private float wallLimit=16;
    public CauldronGroundSpell(EntityType<? extends CauldronGroundSpell> type,Level level){super(type,level);setNoGravity(true);}
    public boolean oil(){return getType()==CauldronPitContent.OIL_POOL.get();}
    public String modelId(){return oil()?OIL_ID:CRACK_ID;}
    public float length(){return entityData.get(LENGTH);}
    public boolean ownedBy(TaoyanCauldron e){return e.getUUID().equals(owner);}
    // The .1m server anchor is not the visible twelve/sixteen-metre spell footprint.
    @Override public boolean shouldRenderAtSqrDistance(double distance){return Double.isFinite(distance)&&distance<96*96;}
    @Override protected void defineSynchedData(){entityData.define(LENGTH,0F);}
    public void launch(TaoyanCauldron caster,Vec3 at,Vec3 direction){owner=caster.getUUID();born=level().getGameTime();lastTick=born-1;setPos(at);setYRot((float)Math.toDegrees(Math.atan2(-direction.x,direction.z)));}
    private Vec3 direction(){double a=Math.toRadians(getYRot());return new Vec3(-Math.sin(a),0,Math.cos(a));}
    @Override public void tick(){super.tick();if(level() instanceof ServerLevel world){long now=world.getGameTime();var e=owner==null?null:world.getEntity(owner);if(!(e instanceof TaoyanCauldron caster)||!caster.isAlive()||born<0||now<born||now-born>=(oil()?160:140)||now<lastTick||lastTick>=0&&now-lastTick>1||distanceToSqr(caster)>32*32||!caster.loaded(new AABB(position(),position()).inflate(oil()?6:17,2,oil()?6:17))){discard();return;}lastTick=now;
        if(!oil()){double wanted=Math.min(wallLimit,Math.min(16,(now-born)/4D));var direction=direction();double valid=0;for(double step=.5;step<=wanted+.001;step+=.5){var at=position().add(direction.scale(step));var floor=caster.floor(at);if(floor==null||Math.abs(floor.getY()-getY())>.1||world.clip(new ClipContext(position().add(0,.2,0),at.add(0,.2,0),ClipContext.Block.COLLIDER,ClipContext.Fluid.NONE,this)).getType()!=HitResult.Type.MISS){wallLimit=(float)Math.max(0,step-.5);break;}valid=step;}entityData.set(LENGTH,(float)Math.min(wanted,valid));}
        if(now-born>=1&&(now-born)%10==0)pulse(caster);
    }}
    public void pulse(TaoyanCauldron caster){if(!(level() instanceof ServerLevel world)||!caster.isAlive()||lastPulse>=0&&level().getGameTime()-lastPulse<10)return;lastPulse=level().getGameTime();double range=oil()?6:length();if(range<=0)return;for(var e:CombatGeometry.query(world,position().add(0,.3,0),direction(),oil()?CombatGeometry.Shape.CIRCLE:CombatGeometry.Shape.STRIP,range,oil()?0:1,360,.8,caster::enemy).stream().limit(16).toList()){
        if(!caster.isAlive()||isRemoved())return;if(Math.abs(e.getY()-getY())>1||world.clip(new ClipContext(position().add(0,.7,0),e.getEyePosition(),ClipContext.Block.COLLIDER,ClipContext.Fluid.NONE,this)).getType()!=HitResult.Type.MISS)continue;
        if(e.hurt(caster.damageSources().mobAttack(caster),(float)caster.getAttributeValue(Attributes.ATTACK_DAMAGE)*(oil()?.45F:.6F)))e.setSecondsOnFire(3);
    }}
    @Override protected void readAdditionalSaveData(CompoundTag t){owner=t.hasUUID("CauldronOwner")?t.getUUID("CauldronOwner"):null;born=t.contains("CauldronBorn")?t.getLong("CauldronBorn"):-1;lastTick=t.contains("CauldronLastTick")?t.getLong("CauldronLastTick"):-1;lastPulse=t.contains("CauldronLastPulse")?t.getLong("CauldronLastPulse"):-1;float f=t.getFloat("FissureLimit");wallLimit=Float.isFinite(f)?Math.max(0,Math.min(16,f)):0;f=t.getFloat("FissureLength");entityData.set(LENGTH,Float.isFinite(f)?Math.max(0,Math.min(wallLimit,f)):0);}
    @Override protected void addAdditionalSaveData(CompoundTag t){if(owner!=null)t.putUUID("CauldronOwner",owner);t.putLong("CauldronBorn",born);t.putLong("CauldronLastTick",lastTick);t.putLong("CauldronLastPulse",lastPulse);t.putFloat("FissureLimit",wallLimit);t.putFloat("FissureLength",length());}
    @Override public Packet<ClientGamePacketListener> getAddEntityPacket(){return NetworkHooks.getEntitySpawningPacket(this);}
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar c){c.add(new AnimationController<CauldronGroundSpell>(this,"spell",0,s->{s.setAnimation(RawAnimation.begin().thenLoop("animation."+modelId()+".idle"));return software.bernie.geckolib.core.object.PlayState.CONTINUE;}));}
    @Override public AnimatableInstanceCache getAnimatableInstanceCache(){return cache;}
}
