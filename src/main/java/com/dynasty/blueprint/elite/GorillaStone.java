package com.dynasty.blueprint.elite;

import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
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

/** A bounded swept boulder. Three fragments at most; fragments cannot subdivide. */
public final class GorillaStone extends Entity implements GeoEntity {
    public static final String BOULDER_ID="gorilla_cast_boulder",FRAGMENT_ID="gorilla_stone_fragment";
    private final AnimatableInstanceCache cache=GeckoLibUtil.createInstanceCache(this);
    private UUID owner;
    private long born=-1,lastTick=-1;
    private boolean spent;
    public GorillaStone(EntityType<? extends GorillaStone> type,Level level){super(type,level);}
    public boolean fragment(){return getType()==EliteContent.GORILLA_FRAGMENT.get();}
    public String modelId(){return fragment()?FRAGMENT_ID:BOULDER_ID;}
    public boolean ownedBy(BronzeGorilla ape){return ape.getUUID().equals(owner);}
    public void launch(BronzeGorilla ape,Vec3 at,Vec3 velocity){owner=ape.getUUID();born=level().getGameTime();lastTick=born;setPos(at);setDeltaMovement(velocity);}
    @Override protected void defineSynchedData(){}
    private boolean loaded(AABB box){for(double x:new double[]{box.minX,box.maxX})for(double z:new double[]{box.minZ,box.maxZ})if(!level().hasChunkAt(BlockPos.containing(x,box.minY,z)))return false;return level().getWorldBorder().isWithinBounds(box);}
    @Override public void tick(){
        super.tick();if(level().isClientSide)return;
        if(!(level() instanceof ServerLevel world)||owner==null||!(world.getEntity(owner) instanceof BronzeGorilla ape)||!ape.isAlive()){discard();return;}
        long now=world.getGameTime(),age=now-born;
        if(spent||born<0||age<0||age>(fragment()?30:60)||now-lastTick>1||now<lastTick||distanceToSqr(ape)>32*32){discard();return;}if(now==lastTick)return;lastTick=now;
        var velocity=getDeltaMovement();if(!Double.isFinite(velocity.lengthSqr())||velocity.lengthSqr()>4){discard();return;}
        var next=position().add(velocity);var sweep=getBoundingBox().expandTowards(velocity);if(!loaded(sweep)){discard();return;}
        double half=fragment()?.25:.75;var from=position().add(0,half,0);var to=next.add(0,half,0);LivingEntity nearest=null;double best=Double.MAX_VALUE;
        var block=world.clip(new ClipContext(from,to,ClipContext.Block.COLLIDER,ClipContext.Fluid.NONE,this));
        double wall=block.getType()==HitResult.Type.MISS?Double.MAX_VALUE:from.distanceToSqr(block.getLocation());
        // The complete body can touch a wall even when its centre ray misses an edge.
        // Cancel before querying victims in that case, so a large rock cannot hit through it.
        if(world.getBlockCollisions(this,sweep).iterator().hasNext()){shatter(world,ape);return;}
        // Broad phase has a small local cap, then each real bounding box is swept.
        for(var target:world.getEntitiesOfClass(LivingEntity.class,sweep,ape::enemy).stream().limit(16).toList()){
            var box=target.getBoundingBox().inflate(half);var contact=box.contains(from)?java.util.Optional.of(from):box.clip(from,to);if(contact.isEmpty())continue;
            double distance=from.distanceToSqr(contact.get());
            if(distance<best&&distance<wall&&world.clip(new ClipContext(from,target.getEyePosition(),ClipContext.Block.COLLIDER,ClipContext.Fluid.NONE,this)).getType()==HitResult.Type.MISS){best=distance;nearest=target;}
        }
        if(nearest!=null){nearest.hurt(damageSources().thrown(this,ape),(float)ape.getAttributeValue(Attributes.ATTACK_DAMAGE)*(fragment()?.35F:1.2F));shatter(world,ape);return;}
        if(block.getType()!=HitResult.Type.MISS||world.getBlockCollisions(this,sweep).iterator().hasNext()){shatter(world,ape);return;}
        setPos(next);setDeltaMovement(velocity.add(0,-(fragment()?.035:.025),0));
    }
    private void shatter(ServerLevel world,BronzeGorilla ape){
        if(spent)return;spent=true;
        if(!fragment()&&ape.isAlive()){
            var base=getDeltaMovement().multiply(1,0,1).normalize();if(base.lengthSqr()<.001)base=new Vec3(0,0,1);var side=new Vec3(-base.z,0,base.x);
            for(int i=-1;i<=1;i++){
                var shard=EliteContent.GORILLA_FRAGMENT.get().create(world);if(shard==null)continue;var at=position().add(side.scale(i*.4)).add(0,.2,0);var box=shard.getType().getDimensions().makeBoundingBox(at);
                if(!loaded(box)||!world.noCollision(shard,box))continue;
                shard.launch(ape,at,base.scale(.26).add(side.scale(i*.2)).add(0,.18,0));world.addFreshEntity(shard);
            }
        }discard();
    }
    @Override protected void addAdditionalSaveData(CompoundTag t){if(owner!=null)t.putUUID("Owner",owner);t.putLong("Born",born);t.putLong("LastTick",lastTick);t.putBoolean("Spent",spent);}
    @Override protected void readAdditionalSaveData(CompoundTag t){owner=t.hasUUID("Owner")?t.getUUID("Owner"):null;born=t.contains("Born")?t.getLong("Born"):-1;lastTick=t.contains("LastTick")?t.getLong("LastTick"):-1;spent=t.getBoolean("Spent");}
    @Override public Packet<ClientGamePacketListener> getAddEntityPacket(){return NetworkHooks.getEntitySpawningPacket(this);}
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar c){c.add(new AnimationController<>(this,"roll",0,s->{s.setAnimation(RawAnimation.begin().thenLoop("animation."+modelId()+".spin"));return software.bernie.geckolib.core.object.PlayState.CONTINUE;}));}
    @Override public AnimatableInstanceCache getAnimatableInstanceCache(){return cache;}
}
