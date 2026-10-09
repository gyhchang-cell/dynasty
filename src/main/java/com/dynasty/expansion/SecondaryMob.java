package com.dynasty.expansion;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.ai.goal.target.*;
import net.minecraft.world.entity.ai.navigation.*;
import net.minecraft.world.entity.ai.control.*;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.item.*;
import net.minecraft.world.level.Level;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.*;
import net.minecraft.world.phys.Vec3;
import net.minecraft.network.syncher.*;
import net.minecraft.sounds.*;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.*;
import software.bernie.geckolib.util.GeckoLibUtil;

/** One small goal set per mob. No boss bar, global manager, or per-insect entities. */
public class SecondaryMob extends PathfinderMob implements GeoEntity {
    public static final class Hostile extends SecondaryMob implements Enemy {
        public Hostile(EntityType<? extends SecondaryMob> type,Level level,SecondaryMobs.Spec spec){super(type,level,spec);}
    }
    private static final EntityDataAccessor<Integer> STATE=SynchedEntityData.defineId(SecondaryMob.class,EntityDataSerializers.INT);
    public final SecondaryMobs.Spec spec;
    private final AnimatableInstanceCache cache=GeckoLibUtil.createInstanceCache(this);
    private int specialCooldown, fleeTicks, shellTicks, animationTicks;
    private boolean friendly;
    private ItemStack stolen=ItemStack.EMPTY;
    public SecondaryMob(EntityType<? extends SecondaryMob> type,Level level,SecondaryMobs.Spec spec) {
        super(type,level);this.spec=spec;
        if(spec.flying()) { moveControl=new FlyingMoveControl(this,20,true);navigation=new FlyingPathNavigation(this,level);setNoGravity(true); }
        if(spec.aquatic()) { moveControl=new SmoothSwimmingMoveControl(this,85,10,.1F,.5F,false);navigation=new WaterBoundPathNavigation(this,level); }
        goalSelector.addGoal(0,new FloatGoal(this));
        goalSelector.addGoal(1,new Goal() {
            { setFlags(java.util.EnumSet.of(Flag.MOVE,Flag.LOOK)); }
            @Override public boolean canUse() { return fleeTicks>0; }
            @Override public void tick() {
                LivingEntity attacker=getLastHurtByMob();
                if(attacker!=null) {Vec3 away=position().subtract(attacker.position()).normalize().scale(8);getNavigation().moveTo(getX()+away.x,getY(),getZ()+away.z,1.4);}
            }
        });
        goalSelector.addGoal(2,new MeleeAttackGoal(this,1.1,false) {
            @Override public boolean canUse() { return !friendly && !spec.id().equals("famished_refugee") && !spec.id().equals("herb_picker") && !spec.id().equals("snail_maiden") && super.canUse(); }
        });
        goalSelector.addGoal(5,spec.flying()?new WaterAvoidingRandomFlyingGoal(this,1):new RandomStrollGoal(this,.8));
        goalSelector.addGoal(6,new LookAtPlayerGoal(this,Player.class,8));
        goalSelector.addGoal(7,new RandomLookAroundGoal(this));
        targetSelector.addGoal(1,new HurtByTargetGoal(this));
        if(!spec.neutral()) targetSelector.addGoal(2,new NearestAttackableTargetGoal<>(this,Player.class,true));
        xpReward=spec.neutral()?0:2;
    }
    @Override protected void registerGoals() { /* spec is assigned after the vanilla constructor */ }
    @Override protected void defineSynchedData() { super.defineSynchedData();entityData.define(STATE,0); }
    public String animation() { return switch(entityData.get(STATE)) { case 1->"wander";case 2->"hunt";case 3->"flee";case 4->"attack";case 5->"special";case 6->"evade";default->"idle"; }; }
    private void animate(int state,int ticks) { entityData.set(STATE,state);animationTicks=ticks; }
    @Override public boolean isAlliedTo(Entity other) {
        if(getPersistentData().hasUUID("cod4Summoner")) {
            var owner=getPersistentData().getUUID("cod4Summoner");
            if(other.getUUID().equals(owner) || other.getPersistentData().hasUUID("cod4Summoner") && other.getPersistentData().getUUID("cod4Summoner").equals(owner))return true;
        }
        return super.isAlliedTo(other);
    }
    @Override public boolean canBreatheUnderwater() { return spec!=null && spec.aquatic() || super.canBreatheUnderwater(); }
    @Override public MobType getMobType() { return spec!=null && (spec.family().equals("ghost") || spec.id().equals("drowning_ghost"))?MobType.UNDEAD:super.getMobType(); }
    @Override public void travel(Vec3 input) {
        if(spec!=null && spec.aquatic() && isInWater()) { moveRelative(.08F,input);move(MoverType.SELF,getDeltaMovement());setDeltaMovement(getDeltaMovement().scale(.9)); }
        else super.travel(input);
    }
    @Override public void aiStep() {
        super.aiStep();
        if(level().isClientSide || !isAlive()) return;
        if(specialCooldown>0)specialCooldown--;
        if(fleeTicks>0)fleeTicks--;
        if(shellTicks>0)shellTicks--;
        if(animationTicks>0)animationTicks--;else entityData.set(STATE,fleeTicks>0?3:getTarget()!=null?2:getDeltaMovement().horizontalDistanceSqr()>.001?1:0);
        if(friendly || spec.id().equals("famished_refugee") || spec.id().equals("herb_picker") || spec.id().equals("snail_maiden"))setTarget(null);
        if(getPersistentData().hasUUID("cod4Summoner")) SummonedGuard.tick(this);
        LivingEntity target=getTarget();
        if(spec.family().equals("ghost")) { noPhysics=target!=null;setNoGravity(true);if(target!=null) setDeltaMovement(target.getEyePosition().subtract(position()).normalize().scale(.1)); }
        if(spec.flying() && target!=null && tickCount%10==0) getMoveControl().setWantedPosition(target.getX(),target.getEyeY()+1,target.getZ(),1.2);
        if(spec.id().equals("clockwork_rat") && stolen.isEmpty() && tickCount%20==0) {
            var items=level().getEntitiesOfClass(ItemEntity.class,getBoundingBox().inflate(2),e->!e.getItem().isEmpty());
            if(!items.isEmpty()) { stolen=items.get(0).getItem().split(1);fleeTicks=80; }
        }
        if(spec.id().equals("night_watchman") && tickCount%40==0)addEffect(new MobEffectInstance(MobEffects.NIGHT_VISION,60));
        if(target==null || !hasLineOfSight(target) || specialCooldown>0) return;
        double distance=distanceToSqr(target);
        if(distance>100) return;
        switch(spec.id()) {
            case "night_watchman","wooden_magpie" -> {
                for(var mob:level().getEntitiesOfClass(SecondaryMob.class,getBoundingBox().inflate(12),m->m.spec.id().equals(spec.id()))) if(mob!=this && !mob.friendly)mob.setTarget(target);
                playSound(SoundEvents.NOTE_BLOCK_HAT.get(),1,.7F);specialCooldown=100;animate(5,20);
            }
            case "tree_spirit","river_imp","lantern_ghost","jingwei_bird" -> {
                if(distance>4) { var arrow=new net.minecraft.world.entity.projectile.Arrow(level(),this);Vec3 d=target.getEyePosition().subtract(getEyePosition());arrow.shoot(d.x,d.y,d.z,1.2F,5);arrow.setBaseDamage(spec.damage()/6);arrow.pickup=net.minecraft.world.entity.projectile.AbstractArrow.Pickup.DISALLOWED;level().addFreshEntity(arrow); }
                if(spec.id().equals("lantern_ghost")){target.addEffect(new MobEffectInstance(MobEffects.BLINDNESS,40));ExpansionEffects.apply(target,ExpansionEffects.SOUL,60);}
                specialCooldown=70;animate(5,16);
            }
            case "wild_boar","bandit_thug","golden_leopard","gray_falcon","bat_demon","carp_spirit","stone_sprite","stone_worm","corpse_beetle","crab_soldier" -> {
                if(distance>3) {Vec3 leap=target.position().subtract(position()).normalize().scale(.6);setDeltaMovement(leap.x,spec.aquatic()?.5:spec.flying()?leap.y:.2,leap.z);}
                specialCooldown=60;animate(5,15);
                if(spec.id().equals("stone_sprite"))addEffect(new MobEffectInstance(MobEffects.DAMAGE_RESISTANCE,40));
            }
            case "gray_wolf" -> {
                int recruited=0;
                for(var wolf:level().getEntitiesOfClass(SecondaryMob.class,getBoundingBox().inflate(8),m->m.spec.id().equals("gray_wolf"))) {
                    if(wolf==this || recruited>=2)continue;wolf.setTarget(target);double side=(++recruited==1?1:-1)*2;wolf.getNavigation().moveTo(target.getX()+side,target.getY(),target.getZ()-side,1.2);
                }
                specialCooldown=80;
            }
            case "locust_swarm" -> { if(distance<3) {doHurtTarget(target);specialCooldown=20;} }
            default -> { }
        }
    }
    @Override public boolean doHurtTarget(Entity victim) {
        if(isAlliedTo(victim))return false;
        boolean hit=super.doHurtTarget(victim);
        if(!hit || !(victim instanceof LivingEntity target))return hit;
        animate(4,12);
        switch(spec.id()) {
            case "giant_python","crab_soldier","tree_spirit" -> {
                ExpansionEffects.apply(target,ExpansionEffects.STAGGER,30);
                if(spec.id().equals("giant_python") && !ExpansionEffects.boss(target)) {target.setAirSupply(Math.max(0,target.getAirSupply()-40));target.hurt(target.damageSources().drown(),2);}
            }
            case "drowning_ghost","river_imp" -> {ExpansionEffects.apply(target,ExpansionEffects.FROST,80);target.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN,60,1));if(isInWater()){target.push(0,-.18,0);target.setAirSupply(Math.max(0,target.getAirSupply()-20));}}
            case "venom_scorpion","corpse_beetle" -> {target.addEffect(new MobEffectInstance(MobEffects.POISON,80,0));if(spec.id().equals("corpse_beetle")){ExpansionEffects.apply(target,ExpansionEffects.BREAK,80);ExpansionEffects.apply(target,ExpansionEffects.SHA,80);}}
            case "wandering_spirit","paper_money_ghost" -> {
                ExpansionEffects.apply(target,ExpansionEffects.YIN,100);
                if(spec.id().equals("paper_money_ghost") && target instanceof Player p && stolen.isEmpty())for(var coin:p.getInventory().items)if(coin.is(ExpansionContent.item("copper_coin"))){stolen=coin.split(1);break;}
            }
            case "bat_demon" -> {heal(4);target.addEffect(new MobEffectInstance(MobEffects.BLINDNESS,30));}
            case "wild_boar","stone_sprite","stone_worm" -> {if(!ExpansionEffects.boss(target)){target.knockback(.5,getX()-target.getX(),getZ()-target.getZ());if(spec.id().equals("stone_worm"))target.push(0,.4,0);}}
            case "red_fox" -> {if(target instanceof Player p && stolen.isEmpty()) for(int i=0;i<p.getInventory().items.size();i++) {ItemStack food=p.getInventory().items.get(i);if(food.isEdible()){stolen=food.split(1);fleeTicks=60;animate(6,15);break;}}}
            default -> { }
        }
        return true;
    }
    @Override public boolean hurt(DamageSource source,float amount) {
        if(shellTicks>0 && !source.is(net.minecraft.tags.DamageTypeTags.BYPASSES_INVULNERABILITY))return false;
        if(spec!=null && spec.id().equals("snail_maiden")) {shellTicks=40;animate(5,40);}
        boolean result=super.hurt(source,amount);
        if(result && spec!=null && (spec.neutral() || getHealth()<getMaxHealth()*.25F)) {fleeTicks=80;animate(3,30);}
        return result;
    }
    @Override protected InteractionResult mobInteract(Player p,InteractionHand hand) {
        ItemStack stack=p.getItemInHand(hand);
        if(spec.id().equals("famished_refugee") && stack.isEdible() && !friendly) {
            if(!level().isClientSide){friendly=true;fleeTicks=0;setTarget(null);heal(10);if(!p.getAbilities().instabuild)stack.shrink(1);}
            return InteractionResult.sidedSuccess(level().isClientSide);
        }
        if((spec.id().equals("herb_picker") || spec.id().equals("swindler")) && stack.is(ExpansionContent.item("copper_coin")) && specialCooldown==0) {
            if(!level().isClientSide){if(!p.getAbilities().instabuild)stack.shrink(1);if(spec.id().equals("herb_picker")) {
                    ItemStack herbs=new ItemStack(com.dynasty.DynastyItems.TEA.get(),2);
                    if(!p.getInventory().add(herbs))p.drop(herbs,false);
                    p.displayClientMessage(net.minecraft.network.chat.Component.translatable("message.dynasty.cod4.herbs"),true);
                } else spawnAtLocation(Items.DEAD_BUSH);specialCooldown=200;if(spec.id().equals("swindler"))fleeTicks=80;}
            return InteractionResult.sidedSuccess(level().isClientSide);
        }
        return super.mobInteract(p,hand);
    }
    @Override protected void dropCustomDeathLoot(DamageSource s,int looting,boolean recentlyHit) {super.dropCustomDeathLoot(s,looting,recentlyHit);if(!stolen.isEmpty()){spawnAtLocation(stolen);stolen=ItemStack.EMPTY;}}
    @Override public void addAdditionalSaveData(CompoundTag nbt) {super.addAdditionalSaveData(nbt);nbt.putBoolean("Cod4Friendly",friendly);nbt.put("Cod4Stolen",stolen.save(new CompoundTag()));nbt.putInt("Cod4Cooldown",specialCooldown);}
    @Override public void readAdditionalSaveData(CompoundTag nbt) {super.readAdditionalSaveData(nbt);friendly=nbt.getBoolean("Cod4Friendly");stolen=ItemStack.of(nbt.getCompound("Cod4Stolen"));specialCooldown=Math.max(0,Math.min(200,nbt.getInt("Cod4Cooldown")));}
    @Override public AnimatableInstanceCache getAnimatableInstanceCache() {return cache;}
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {controllers.add(new AnimationController<>(this,"body",4,state->state.setAndContinue(RawAnimation.begin().thenLoop(animation()))));}
}
