package com.dynasty.blueprint.elite;

import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.syncher.*;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.*;
import net.minecraft.world.level.*;
import net.minecraft.world.phys.*;
import net.minecraftforge.network.NetworkHooks;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.*;
import software.bernie.geckolib.util.GeckoLibUtil;
import java.util.*;

/** One physical hammer per cast. Hits persist by leg; unloaded gaps cancel instead of replaying. */
public final class HammerChain extends Entity implements GeoEntity {
    public static final int LEG_TICKS=24,LIFETIME=48;
    public static final double RANGE=12;
    private static final EntityDataAccessor<Integer> OWNER=SynchedEntityData.defineId(HammerChain.class,EntityDataSerializers.INT);
    private final AnimatableInstanceCache cache=GeckoLibUtil.createInstanceCache(this);
    private UUID owner;
    private Vec3 origin=Vec3.ZERO,forward=new Vec3(0,0,1);
    private long born=-1,lastTick=-1,epoch=-1,turned=-1;
    private double turnFraction=1;
    private final Set<UUID> outgoing=new HashSet<>(),returning=new HashSet<>();
    public HammerChain(EntityType<? extends HammerChain> type,Level level){super(type,level);}
    public void launch(HammerGuardian caster,Vec3 direction){owner=caster.getUUID();entityData.set(OWNER,caster.getId());born=level().getGameTime();lastTick=born;epoch=caster.attack().started();origin=caster.position().add(0,1.6,0);forward=direction.multiply(1,0,1).normalize();setPos(point(0));}
    public boolean ownedBy(HammerGuardian caster){return caster.getUUID().equals(owner);}
    public UUID ownerId(){return owner;}
    public long born(){return born;}
    private Vec3 point(double t){return origin.add(forward.scale(RANGE*t)).add(0,.65*Math.sin(Math.PI*t)-1.25*t,0);}
    public int ownerEntityId(){return entityData.get(OWNER);}
    @Override protected void defineSynchedData(){entityData.define(OWNER,-1);}
    @Override public void tick(){
        super.tick();if(level().isClientSide)return;
        if(!(level() instanceof ServerLevel world)||born<0||owner==null){discard();return;}
        long now=world.getGameTime(),age=now-born;
        if(age<0||age>LIFETIME||!(world.getEntity(owner) instanceof HammerGuardian caster)||!caster.isAlive()||caster.distanceToSqr(this)>32*32||caster.attack().current()!=HammerGuardian.THROW||caster.attack().started()!=epoch){discard();return;}
        entityData.set(OWNER,caster.getId());
        if(now<lastTick||now-lastTick>1){discard();return;}if(now==lastTick)return;lastTick=now;
        if(turned<0&&age>=LEG_TICKS){turned=now;turnFraction=1;}
        double progress=turned<0?Math.min(1,age/(double)LEG_TICKS):Math.max(0,turnFraction*(1-(now-turned)/(double)LEG_TICKS));
        var destination=point(progress);if(!world.hasChunkAt(BlockPos.containing(destination))){discard();return;}
        var from=position();var block=world.clip(new ClipContext(from,destination,ClipContext.Block.COLLIDER,ClipContext.Fluid.NONE,this));
        if(block.getType()!=HitResult.Type.MISS){
            if(turned>=0){discard();return;}
            turned=now;turnFraction=Math.max(0,(age-1)/(double)LEG_TICKS);return;
        }
        move(MoverType.SELF,destination.subtract(from));
        if(horizontalCollision||verticalCollision){if(turned<0){turned=now;turnFraction=Math.max(0,(age-1)/(double)LEG_TICKS);}else discard();return;}
        var spent=turned<0?outgoing:returning;
        for(var hit:world.getEntitiesOfClass(LivingEntity.class,new AABB(from,position()).inflate(.55),e->caster.enemy(e)&&!spent.contains(e.getUUID()))){
            if(hit.getBoundingBox().inflate(.5).clip(from,position()).isEmpty()||world.clip(new ClipContext(position(),hit.getBoundingBox().getCenter(),ClipContext.Block.COLLIDER,ClipContext.Fluid.NONE,this)).getType()!=HitResult.Type.MISS)continue;
            if(spent.size()>=16)break;spent.add(hit.getUUID());hit.hurt(damageSources().mobProjectile(this,caster),11);
            if(!caster.isAlive()||caster.attack().started()!=epoch){discard();return;}
        }
        if(turned>=0&&now-turned>=LEG_TICKS||age>=LIFETIME)discard();
    }
    @Override protected void addAdditionalSaveData(CompoundTag t){if(owner!=null)t.putUUID("Owner",owner);t.putLong("Born",born);t.putLong("LastTick",lastTick);t.putLong("Epoch",epoch);t.putLong("Turned",turned);t.putDouble("TurnFraction",turnFraction);t.putDouble("X",origin.x);t.putDouble("Y",origin.y);t.putDouble("Z",origin.z);t.putDouble("DX",forward.x);t.putDouble("DZ",forward.z);saveHits(t,"Outgoing",outgoing);saveHits(t,"Returning",returning);}
    private static void saveHits(CompoundTag t,String key,Set<UUID> hits){var list=new net.minecraft.nbt.ListTag();for(var id:hits)list.add(net.minecraft.nbt.StringTag.valueOf(id.toString()));t.put(key,list);}
    private static void loadHits(CompoundTag t,String key,Set<UUID> hits){hits.clear();var list=t.getList(key,8);for(int i=0;i<Math.min(16,list.size());i++)try{hits.add(UUID.fromString(list.getString(i)));}catch(IllegalArgumentException ignored){}}
    @Override protected void readAdditionalSaveData(CompoundTag t){owner=t.hasUUID("Owner")?t.getUUID("Owner"):null;born=t.contains("Born")?t.getLong("Born"):-1;lastTick=t.contains("LastTick")?t.getLong("LastTick"):-1;epoch=t.contains("Epoch")?t.getLong("Epoch"):-1;turned=t.contains("Turned")?t.getLong("Turned"):-1;turnFraction=t.getDouble("TurnFraction");origin=new Vec3(t.getDouble("X"),t.getDouble("Y"),t.getDouble("Z"));forward=new Vec3(t.getDouble("DX"),0,t.getDouble("DZ")).normalize();loadHits(t,"Outgoing",outgoing);loadHits(t,"Returning",returning);if(!Double.isFinite(origin.lengthSqr()+turnFraction)||turnFraction<0||turnFraction>1||origin.distanceToSqr(position())>32*32||forward.lengthSqr()<.9)born=-1;}
    @Override public Packet<ClientGamePacketListener> getAddEntityPacket(){return NetworkHooks.getEntitySpawningPacket(this);}
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar controllers){controllers.add(new AnimationController<HammerChain>(this,"spin",0,state->{state.setAndContinue(RawAnimation.begin().thenLoop("animation.hammer_chain.spin"));return software.bernie.geckolib.core.object.PlayState.CONTINUE;}));}
    @Override public AnimatableInstanceCache getAnimatableInstanceCache(){return cache;}
}
