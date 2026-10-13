package com.dynasty.blueprint.elite;

import com.dynasty.blueprint.combat.AttackState;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.syncher.*;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.item.*;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.*;
import net.minecraftforge.common.ToolActions;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.*;
import software.bernie.geckolib.util.GeckoLibUtil;

/** Native arrow ray collision, shield/armor pipeline and finite per-caster instances. */
public final class EagleArrow extends AbstractArrow implements GeoEntity {
    public static final int MARKER=0,FALLING=1,FEATHER=2;
    public static final String ID="eagle_finite_gold_arrow";
    private static final EntityDataAccessor<Integer> KIND=SynchedEntityData.defineId(EagleArrow.class,EntityDataSerializers.INT);
    private final AnimatableInstanceCache cache=GeckoLibUtil.createInstanceCache(this);
    private long born=-1,epoch=-1,lastTick=-1;
    private Vec3 apex=Vec3.ZERO;
    public EagleArrow(EntityType<? extends EagleArrow> type,Level level){super(type,level);pickup=Pickup.DISALLOWED;}
    @Override protected void defineSynchedData(){super.defineSynchedData();entityData.define(KIND,MARKER);}
    public int kind(){return entityData.get(KIND);}
    public boolean ownedBy(GoldenEagle e){return getOwner()!=null&&e.getUUID().equals(getOwner().getUUID());}
    public void launch(GoldenEagle caster,int kind,Vec3 from,Vec3 velocity,Vec3 point){
        entityData.set(KIND,Math.max(0,Math.min(2,kind)));setOwner(caster);born=level().getGameTime();epoch=caster.attack().started();lastTick=born-1;apex=point;
        setPos(from);setDeltaMovement(velocity);setNoGravity(kind!=FEATHER);pickup=Pickup.DISALLOWED;
        setBaseDamage(caster.getAttributeValue(Attributes.ATTACK_DAMAGE)*(kind==FEATHER?.6:1));setCritArrow(false);setPierceLevel((byte)0);
        var v=velocity.normalize();setYRot((float)Math.toDegrees(Math.atan2(-v.x,v.z)));setXRot((float)-Math.toDegrees(Math.atan2(v.y,v.horizontalDistance())));yRotO=getYRot();xRotO=getXRot();
    }
    @Override public void tick(){
        if(!level().isClientSide){long now=level().getGameTime();
            if(!(getOwner() instanceof GoldenEagle caster)||!caster.isAlive()||born<0||now<born||now-born>=(kind()==MARKER?30:60)||lastTick>=0&&now-lastTick>1||now<lastTick||caster.attack().started()!=epoch||caster.phase()==AttackState.STUN||distanceToSqr(caster)>(kind()==FEATHER?16*16:48*48)||!caster.loaded(getBoundingBox().expandTowards(getDeltaMovement()))){discard();return;}lastTick=now;
            if(kind()==MARKER&&position().distanceToSqr(apex)<=1){
                for(int i=0;i<24;i++){double angle=i%6*Math.PI/3+(i/6%2)*Math.PI/6;double radius=.7+(i/6)*1.05;
                    caster.launchArrow(FALLING,apex.add(Math.cos(angle)*radius,0,Math.sin(angle)*radius),new Vec3(0,-.8,0),Vec3.ZERO);
                }discard();return;
            }
        }
        super.tick();
    }
    @Override protected boolean canHitEntity(Entity e){return kind()!=MARKER&&e instanceof LivingEntity living&&getOwner() instanceof GoldenEagle caster&&caster.enemy(living)&&super.canHitEntity(e);}
    @Override protected void onHitBlock(BlockHitResult hit){discard();}
    @Override protected void onHitEntity(EntityHitResult hit){
        if(kind()==FALLING&&hit.getEntity() instanceof Player player&&overheadShield(player,position())){
            if(!level().isClientSide){var shield=player.getUseItem();var hand=player.getUsedItemHand();shield.hurtAndBreak(1,player,p->p.broadcastBreakEvent(hand));}discard();return;
        }
        float before=hit.getEntity() instanceof LivingEntity living?living.getHealth():0;super.onHitEntity(hit);
        if(!level().isClientSide&&kind()==FEATHER&&hit.getEntity() instanceof LivingEntity living&&living.getHealth()<before&&!(living instanceof Player player&&player.isCreative())){
            // A hard feather spends native armour durability; it does not bypass the armour pipeline.
            for(var slot:new EquipmentSlot[]{EquipmentSlot.HEAD,EquipmentSlot.CHEST,EquipmentSlot.LEGS,EquipmentSlot.FEET}){var stack=living.getItemBySlot(slot);if(stack.getItem() instanceof ArmorItem)stack.hurtAndBreak(2,living,e->e.broadcastBreakEvent(slot));}
        }
        discard();
    }
    public static boolean overheadShield(Player player,Vec3 contact){return player.isBlocking()&&player.getUseItem().canPerformAction(ToolActions.SHIELD_BLOCK)&&player.getLookAngle().y>.3&&player.getLookAngle().dot(contact.subtract(player.getEyePosition()).normalize())>.35;}
    @Override protected ItemStack getPickupItem(){return new ItemStack(Items.ARROW);}
    @Override public void addAdditionalSaveData(CompoundTag t){super.addAdditionalSaveData(t);t.putInt("EagleKind",kind());t.putLong("EagleBorn",born);t.putLong("EagleEpoch",epoch);t.putLong("EagleLastTick",lastTick);t.putDouble("ApexX",apex.x);t.putDouble("ApexY",apex.y);t.putDouble("ApexZ",apex.z);}
    @Override public void readAdditionalSaveData(CompoundTag t){super.readAdditionalSaveData(t);entityData.set(KIND,Math.max(0,Math.min(2,t.getInt("EagleKind"))));born=t.contains("EagleBorn")?t.getLong("EagleBorn"):-1;epoch=t.getLong("EagleEpoch");lastTick=t.contains("EagleLastTick")?t.getLong("EagleLastTick"):-1;apex=new Vec3(t.getDouble("ApexX"),t.getDouble("ApexY"),t.getDouble("ApexZ"));if(!Double.isFinite(apex.lengthSqr())||kind()==MARKER&&apex.distanceToSqr(position())>24*24)born=-1;setNoGravity(kind()!=FEATHER);pickup=Pickup.DISALLOWED;}
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar c){c.add(new AnimationController<EagleArrow>(this,"arrow",0,s->{s.setAnimation(RawAnimation.begin().thenLoop("animation."+ID+".idle"));return software.bernie.geckolib.core.object.PlayState.CONTINUE;}));}
    @Override public AnimatableInstanceCache getAnimatableInstanceCache(){return cache;}
}
