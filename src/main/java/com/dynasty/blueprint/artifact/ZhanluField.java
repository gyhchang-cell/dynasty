package com.dynasty.blueprint.artifact;

import com.dynasty.blueprint.combat.Combatant;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.syncher.*;
import net.minecraft.server.level.*;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.*;
import net.minecraftforge.event.entity.living.*;
import net.minecraftforge.eventbus.api.*;
import net.minecraftforge.fml.common.Mod;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.*;
import software.bernie.geckolib.util.GeckoLibUtil;
import java.util.*;

/** Four-second stationary field. Short persisted equipment leases restore on cancel, death or unload. */
@Mod.EventBusSubscriber(modid="dynasty")
public final class ZhanluField extends Entity implements GeoEntity {
    private static final String LEASE="DynastyZhanluLeaseV1";
    private static final UUID SLOW=UUID.fromString("572e6636-5639-44d1-b1e1-4bfdca14e982");
    private static final EntityDataAccessor<Long> BORN=SynchedEntityData.defineId(ZhanluField.class,EntityDataSerializers.LONG);
    private final AnimatableInstanceCache cache=GeckoLibUtil.createInstanceCache(this);
    private final Set<UUID> affected=new HashSet<>();
    private UUID owner;
    private ItemStack held=ItemStack.EMPTY;
    private long lastTick=-1;
    private boolean killed,canceled,finished;
    public ZhanluField(EntityType<? extends ZhanluField> type,Level world){super(type,world);setNoGravity(true);}
    @Override protected void defineSynchedData(){entityData.define(BORN,-1L);}
    public long born(){return entityData.get(BORN);}
    public boolean ownedBy(ServerPlayer p){return p.getUUID().equals(owner);}
    public void begin(ServerPlayer p,BlockPos ground){owner=p.getUUID();held=p.getMainHandItem();entityData.set(BORN,level().getGameTime());setPos(p.getX(),ground.getY()+.025,p.getZ());}
    public static boolean disarmed(Mob m){if(!m.getPersistentData().contains(LEASE,10))return false;var n=m.getPersistentData().getCompound(LEASE);long now=m.level().getGameTime(),until=n.getLong("Until");return n.hasUUID("Field")&&until>now&&until<=now+3;}
    private boolean lease(Mob m,long now){
        var data=m.getPersistentData();if(data.contains(LEASE,10)){var existing=data.getCompound(LEASE);if(disarmed(m)&&!getUUID().equals(existing.getUUID("Field")))return false;if(!disarmed(m))restoreEquipment(m);}
        if(!data.contains(LEASE,10)){var n=new CompoundTag();n.putUUID("Field",getUUID());n.put("Main",m.getMainHandItem().save(new CompoundTag()));n.put("Off",m.getOffhandItem().save(new CompoundTag()));n.putBoolean("Pickup",m.canPickUpLoot());data.put(LEASE,n);m.setItemInHand(InteractionHand.MAIN_HAND,ItemStack.EMPTY);m.setItemInHand(InteractionHand.OFF_HAND,ItemStack.EMPTY);m.setCanPickUpLoot(false);}
        data.getCompound(LEASE).putLong("Until",now+3);var speed=m.getAttribute(Attributes.MOVEMENT_SPEED);if(speed!=null&&speed.getModifier(SLOW)==null)speed.addTransientModifier(new AttributeModifier(SLOW,"dynasty zhanlu ceasefire",-.7,AttributeModifier.Operation.MULTIPLY_TOTAL));return true;
    }
    public static void restoreEquipment(Mob m){
        var data=m.getPersistentData();if(!data.contains(LEASE,10))return;var n=data.getCompound(LEASE).copy();data.remove(LEASE);var speed=m.getAttribute(Attributes.MOVEMENT_SPEED);if(speed!=null)speed.removeModifier(SLOW);m.setCanPickUpLoot(n.getBoolean("Pickup"));
        restoreHand(m,InteractionHand.MAIN_HAND,ItemStack.of(n.getCompound("Main")));restoreHand(m,InteractionHand.OFF_HAND,ItemStack.of(n.getCompound("Off")));
    }
    private static void restoreHand(Mob m,InteractionHand hand,ItemStack original){if(original.isEmpty())return;if(m.getItemInHand(hand).isEmpty())m.setItemInHand(hand,original);else m.spawnAtLocation(original);}
    private void restoreOwned(ServerLevel w,UUID id){var e=w.getEntity(id);if(e instanceof Mob m&&m.getPersistentData().contains(LEASE,10)){var n=m.getPersistentData().getCompound(LEASE);if(n.hasUUID("Field")&&getUUID().equals(n.getUUID("Field")))restoreEquipment(m);}}
    private ServerPlayer caster(ServerLevel w){var e=owner==null?null:w.getEntity(owner);return e instanceof ServerPlayer p?p:null;}
    private boolean holding(ServerPlayer p){return p!=null&&p.isAlive()&&!p.isSpectator()&&!p.isSleeping()&&p.isUsingItem()&&p.getUseItem()==held&&p.getMainHandItem()==held&&p.getMainHandItem().is(ArtifactContent.ZHANLU.get())&&p.onGround()&&p.position().subtract(position()).multiply(1,0,1).lengthSqr()<=.36&&Math.abs(p.getY()-getY())<.5;}
    @Override public void tick(){super.tick();if(!(level() instanceof ServerLevel w))return;long now=w.getGameTime();var p=caster(w);
        if(canceled||born()<0||now<born()||lastTick>=0&&(now<lastTick||now-lastTick>1)||!holding(p)||!ArtifactAbility.loaded(w,new AABB(position().add(-5,-.5,-5),position().add(5,3,5)))){cancel();return;}lastTick=now;
        if(now-born()>=80){finished=true;if(!killed)p.heal(p.getMaxHealth()*.3F);discard();p.stopUsingItem();return;}
        var selected=new HashSet<UUID>();var targets=w.getEntitiesOfClass(Mob.class,new AABB(position().add(-5,-.5,-5),position().add(5,3,5)),m->m.isAlive()&&(m instanceof Enemy||m.getTarget()==p)&&!Combatant.allied(p,m)&&m.position().subtract(position()).multiply(1,0,1).lengthSqr()<=25&&p.hasLineOfSight(m));targets.sort(Comparator.comparingDouble(m->m.distanceToSqr(this)));
        for(var m:targets){if(selected.size()>=16)break;if(lease(m,now))selected.add(m.getUUID());}
        for(var id:affected)if(!selected.contains(id))restoreOwned(w,id);affected.clear();affected.addAll(selected);
    }
    public void cancel(){canceled=true;discard();}
    @Override public void remove(RemovalReason reason){if(!isRemoved()&&level() instanceof ServerLevel w){for(var id:affected)restoreOwned(w,id);affected.clear();var p=caster(w);if(p!=null){var n=p.getPersistentData();if(n.hasUUID("DynastyZhanluField")&&getUUID().equals(n.getUUID("DynastyZhanluField")))n.remove("DynastyZhanluField");}}super.remove(reason);}
    @SubscribeEvent(priority=EventPriority.HIGHEST) public static void restoreOnDeath(LivingDeathEvent e){if(!e.getEntity().level().isClientSide&&e.getEntity() instanceof Mob m)restoreEquipment(m);}
    @SubscribeEvent(priority=EventPriority.LOWEST) public static void death(LivingDeathEvent e){if(e.getEntity().level().isClientSide||e.getSource().is(net.minecraft.world.damagesource.DamageTypes.THORNS))return;if(e.getSource().getEntity() instanceof ServerPlayer p&&e.getEntity() instanceof Mob m&&(m instanceof Enemy||m.getTarget()==p)&&!Combatant.allied(p,m)){var n=p.getPersistentData();if(n.hasUUID("DynastyZhanluField")){var field=p.serverLevel().getEntity(n.getUUID("DynastyZhanluField"));if(field instanceof ZhanluField f&&f.ownedBy(p)&&!f.finished)f.killed=true;}}}
    @SubscribeEvent(priority=EventPriority.HIGH) public static void suppress(LivingAttackEvent e){if(!e.getEntity().level().isClientSide&&e.getSource().getEntity() instanceof Mob m&&disarmed(m))e.setCanceled(true);}
    @SubscribeEvent public static void restore(LivingEvent.LivingTickEvent e){if(!(e.getEntity() instanceof Mob m)||m.level().isClientSide||!m.getPersistentData().contains(LEASE,10))return;if(!m.isAlive()||!disarmed(m))restoreEquipment(m);else{var speed=m.getAttribute(Attributes.MOVEMENT_SPEED);if(speed!=null&&speed.getModifier(SLOW)==null)speed.addTransientModifier(new AttributeModifier(SLOW,"dynasty zhanlu ceasefire",-.7,AttributeModifier.Operation.MULTIPLY_TOTAL));}}
    @Override public boolean shouldRenderAtSqrDistance(double d){return Double.isFinite(d)&&d<64*64;}
    @Override protected void addAdditionalSaveData(CompoundTag n){if(owner!=null)n.putUUID("Owner",owner);n.putLong("Born",born());n.putBoolean("Killed",killed);}
    @Override protected void readAdditionalSaveData(CompoundTag n){owner=n.hasUUID("Owner")?n.getUUID("Owner"):null;entityData.set(BORN,-1L);canceled=true;setNoGravity(true);}
    @Override public net.minecraft.network.protocol.Packet<net.minecraft.network.protocol.game.ClientGamePacketListener> getAddEntityPacket(){return net.minecraftforge.network.NetworkHooks.getEntitySpawningPacket(this);}
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar c){c.add(new AnimationController<ZhanluField>(this,"field",0,s->{s.setAnimation(RawAnimation.begin().thenLoop("animation.zhanlu_ceasefire_field.idle"));return software.bernie.geckolib.core.object.PlayState.CONTINUE;}));}
    @Override public AnimatableInstanceCache getAnimatableInstanceCache(){return cache;}
}
