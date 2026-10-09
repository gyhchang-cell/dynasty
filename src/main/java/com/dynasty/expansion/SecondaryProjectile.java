package com.dynasty.expansion;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.syncher.*;
import net.minecraft.world.effect.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.projectile.ThrowableItemProjectile;
import net.minecraft.world.item.*;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.*;

/** One real, finite projectile per ranged action. Visuals never apply a second hit. */
public final class SecondaryProjectile extends ThrowableItemProjectile implements net.minecraftforge.entity.IEntityAdditionalSpawnData {
    public static final int SEED=0, LIGHT=1, WATER=2, STONE=3;
    private static final EntityDataAccessor<Integer> KIND=SynchedEntityData.defineId(SecondaryProjectile.class,EntityDataSerializers.INT);
    public SecondaryProjectile(EntityType<? extends SecondaryProjectile> type,Level level){super(type,level);}
    @Override protected void defineSynchedData(){super.defineSynchedData();entityData.define(KIND,SEED);}
    public int kind(){return entityData.get(KIND);}
    public void kind(int kind){entityData.set(KIND,Math.max(SEED,Math.min(STONE,kind)));}
    @Override public net.minecraft.network.protocol.Packet<net.minecraft.network.protocol.game.ClientGamePacketListener> getAddEntityPacket(){return net.minecraftforge.network.NetworkHooks.getEntitySpawningPacket(this);}
    @Override public void writeSpawnData(net.minecraft.network.FriendlyByteBuf b){b.writeVarInt(kind());b.writeInt(getOwner()==null?-1:getOwner().getId());}
    @Override public void readSpawnData(net.minecraft.network.FriendlyByteBuf b){kind(b.readVarInt());int owner=b.readInt();if(owner>=0)setOwner(level().getEntity(owner));}
    @Override protected Item getDefaultItem(){return switch(kind()){case LIGHT->Items.GLOWSTONE_DUST;case WATER->Items.PRISMARINE_CRYSTALS;case STONE->Items.FLINT;default->Items.WHEAT_SEEDS;};}
    @Override protected float getGravity(){return kind()==STONE?.035F:kind()==SEED?.008F:0;}
    @Override protected boolean canHitEntity(Entity e){return super.canHitEntity(e)&&!(getOwner() instanceof LivingEntity owner&&owner.isAlliedTo(e));}
    @Override protected void onHitEntity(EntityHitResult hit){
        super.onHitEntity(hit);
        if(level().isClientSide||!(getOwner() instanceof SecondaryMob owner)||!(hit.getEntity() instanceof LivingEntity target)
                ||!target.isAlive()||owner.isAlliedTo(target))return;
        if(!target.hurt(damageSources().mobAttack(owner),(float)Math.max(1,owner.spec.damage()/6)))return;
        switch(kind()){
            case LIGHT->{target.addEffect(new MobEffectInstance(MobEffects.BLINDNESS,40));ExpansionEffects.apply(target,ExpansionEffects.SOUL,60);CombatFeedback.send(target,CombatFeedback.STAR);}
            case SEED->{ExpansionEffects.apply(target,ExpansionEffects.STAGGER,30);CombatFeedback.send(target,CombatFeedback.STAGGER);
                if(!ExpansionEffects.boss(target)&&target.level() instanceof net.minecraft.server.level.ServerLevel server){
                    var packet=new com.dynasty.cod3.Cod3VisualPacket(server.dimension().location().toString(),14,target.getId(),target.getUUID().getLeastSignificantBits(),
                        server.getGameTime(),30,1,target.position(),target.getLookAngle(),"secondary_roots",0,0x749644);
                    com.dynasty.network.DynastyNetwork.CHANNEL.send(net.minecraftforge.network.PacketDistributor.NEAR.with(()->
                        new net.minecraftforge.network.PacketDistributor.TargetPoint(target.getX(),target.getY(),target.getZ(),32,server.dimension())),packet);
                }}
            case WATER->{owner.beginWaterDrag(target);CombatFeedback.send(target,CombatFeedback.WATER);}
            case STONE->CombatFeedback.send(target,CombatFeedback.HEAVY);
            default->{}
        }
    }
    @Override protected void onHit(HitResult hit){super.onHit(hit);if(!level().isClientSide)discard();}
    @Override public void tick(){if(!level().isClientSide&&tickCount>=40){discard();return;}super.tick();}
    @Override public void addAdditionalSaveData(CompoundTag n){super.addAdditionalSaveData(n);n.putInt("Cod4ProjectileKind",kind());n.putInt("Cod4ProjectileAge",tickCount);}
    @Override public void readAdditionalSaveData(CompoundTag n){super.readAdditionalSaveData(n);kind(n.getInt("Cod4ProjectileKind"));tickCount=Math.max(0,Math.min(40,n.getInt("Cod4ProjectileAge")));}
}
