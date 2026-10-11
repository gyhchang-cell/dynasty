package com.dynasty.blueprint.elite;

import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.syncher.*;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.effect.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.*;
import net.minecraft.world.phys.*;
import net.minecraftforge.network.NetworkHooks;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.*;
import software.bernie.geckolib.util.GeckoLibUtil;
import java.util.UUID;

/** Exactly two helix contacts; native wall clips, a finite absolute life, no terrain explosion. */
public final class AlchemistOrb extends Entity implements GeoEntity {
    public static final String ID="alchemist_cast_orb";
    private static final EntityDataAccessor<Integer> SIDE=SynchedEntityData.defineId(AlchemistOrb.class,EntityDataSerializers.INT);
    private static final EntityDataAccessor<Boolean> PILL=SynchedEntityData.defineId(AlchemistOrb.class,EntityDataSerializers.BOOLEAN);
    private final AnimatableInstanceCache cache=GeckoLibUtil.createInstanceCache(this);
    private UUID owner;private long born=-1,lastTick=-1,epoch=-1;private Vec3 origin=Vec3.ZERO,forward=new Vec3(0,0,1);
    public AlchemistOrb(EntityType<? extends AlchemistOrb> type,Level level){super(type,level);}
    public boolean ownedBy(Alchemist caster){return caster.getUUID().equals(owner);}public int side(){return entityData.get(SIDE);}public boolean pill(){return entityData.get(PILL);}
    private Vec3 point(double age){if(pill())return origin.add(forward.scale(age)).add(0,-.025*age*age,0);var right=new Vec3(-forward.z,0,forward.x).normalize();if(right.lengthSqr()<.1)right=new Vec3(1,0,0);double phase=age*.32+(side()<0?Math.PI:0);return origin.add(forward.scale(age*.3)).add(right.scale(.65*Math.cos(phase))).add(0,.65*Math.sin(phase),0);}
    public void launch(Alchemist caster,Vec3 from,Vec3 direction,int side){owner=caster.getUUID();born=level().getGameTime();lastTick=born;epoch=caster.attack().started();origin=from;forward=direction.normalize();entityData.set(SIDE,side<0?-1:1);setPos(point(0));}
    public void launchPill(Alchemist caster,Vec3 from,Vec3 landing,int side){owner=caster.getUUID();born=level().getGameTime();lastTick=born;epoch=caster.attack().started();origin=from;forward=landing.subtract(from).scale(1D/24).add(0,.6,0);entityData.set(SIDE,side<0?-1:1);entityData.set(PILL,true);setPos(from);}
    @Override protected void defineSynchedData(){entityData.define(SIDE,1);entityData.define(PILL,false);}
    @Override public void tick(){
        super.tick();if(level().isClientSide)return;
        if(!(level() instanceof ServerLevel world)||born<0||owner==null||!(world.getEntity(owner) instanceof Alchemist caster)||!caster.isAlive()||caster.attack().current()!=(pill()?Alchemist.PELLS:Alchemist.HELIX)||caster.attack().started()!=epoch){discard();return;}
        long now=world.getGameTime(),age=now-born;if(age<0||age>40||now-lastTick>1||now<lastTick||distanceToSqr(caster)>32*32){discard();return;}if(now==lastTick)return;lastTick=now;
        var next=point(age);if(!world.hasChunkAt(BlockPos.containing(next))){discard();return;}
        var block=world.clip(new ClipContext(position(),next,ClipContext.Block.COLLIDER,ClipContext.Fluid.NONE,this));var end=block.getType()==HitResult.Type.MISS?next:block.getLocation();
        Vec3 nearest=null;double distance=Double.MAX_VALUE;
        for(var victim:world.getEntitiesOfClass(LivingEntity.class,new AABB(position(),end).inflate(.3),caster::enemy)){
            var contact=victim.getBoundingBox().inflate(.2).clip(position(),end);if(contact.isPresent()&&contact.get().distanceToSqr(position())<distance){nearest=contact.get();distance=nearest.distanceToSqr(position());}
        }
        if(nearest!=null){burst(world,caster,nearest);return;}
        setPos(end);if(block.getType()!=HitResult.Type.MISS||age==40){burst(world,caster,end);return;}
    }
    private void burst(ServerLevel world,Alchemist caster,Vec3 at){
        discard();if(pill()){caster.releaseMercury(at.add(0,.08,0));world.sendParticles(net.minecraft.core.particles.ParticleTypes.SMOKE,at.x,at.y,at.z,8,.3,.2,.3,.02);return;}
        for(var target:world.getEntitiesOfClass(LivingEntity.class,new AABB(at,at).inflate(2),caster::enemy).stream().limit(12).toList()){
            if(target.getBoundingBox().getCenter().distanceToSqr(at)>4||world.clip(new ClipContext(at.add(0,.15,0),target.getEyePosition(),ClipContext.Block.COLLIDER,ClipContext.Fluid.NONE,this)).getType()!=HitResult.Type.MISS)continue;
            if(target.hurt(damageSources().indirectMagic(this,caster),7)){
                if(side()>0)target.setSecondsOnFire(2);else target.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN,40),caster);
                if(target instanceof Player p&&!p.isCreative())p.getFoodData().setSaturation(Math.max(0,p.getFoodData().getSaturationLevel()-2));
            }
        }
        world.sendParticles(side()>0?net.minecraft.core.particles.ParticleTypes.FLAME:net.minecraft.core.particles.ParticleTypes.SOUL_FIRE_FLAME,at.x,at.y,at.z,12,.4,.4,.4,.025);
    }
    @Override protected void addAdditionalSaveData(CompoundTag t){if(owner!=null)t.putUUID("Owner",owner);t.putLong("Born",born);t.putLong("LastTick",lastTick);t.putLong("Epoch",epoch);t.putInt("Side",side());t.putBoolean("Pill",pill());t.putDouble("X",origin.x);t.putDouble("Y",origin.y);t.putDouble("Z",origin.z);t.putDouble("DX",forward.x);t.putDouble("DY",forward.y);t.putDouble("DZ",forward.z);}
    @Override protected void readAdditionalSaveData(CompoundTag t){owner=t.hasUUID("Owner")?t.getUUID("Owner"):null;born=t.contains("Born")?t.getLong("Born"):-1;lastTick=t.contains("LastTick")?t.getLong("LastTick"):-1;epoch=t.contains("Epoch")?t.getLong("Epoch"):-1;entityData.set(SIDE,t.getInt("Side")<0?-1:1);entityData.set(PILL,t.getBoolean("Pill"));origin=new Vec3(t.getDouble("X"),t.getDouble("Y"),t.getDouble("Z"));forward=new Vec3(t.getDouble("DX"),t.getDouble("DY"),t.getDouble("DZ"));if(!Double.isFinite(origin.lengthSqr()+forward.lengthSqr())||forward.lengthSqr()<.001||forward.lengthSqr()>4||!pill()&&Math.abs(forward.lengthSqr()-1)>.01||origin.distanceToSqr(position())>16*16)born=-1;}
    @Override public Packet<ClientGamePacketListener> getAddEntityPacket(){return NetworkHooks.getEntitySpawningPacket(this);}
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar c){c.add(new AnimationController<>(this,"orb",0,s->{s.setAnimation(RawAnimation.begin().thenLoop("animation."+ID+".spin"));return software.bernie.geckolib.core.object.PlayState.CONTINUE;}));}
    @Override public AnimatableInstanceCache getAnimatableInstanceCache(){return cache;}
}
