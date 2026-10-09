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
    private int deceptionStage, hardenTicks, rollingTicks;
    private java.util.UUID customer;
    private static final java.util.UUID HARDENING=java.util.UUID.nameUUIDFromBytes("dynasty:stone_sprite_hardening".getBytes(java.nio.charset.StandardCharsets.UTF_8));
    private boolean friendly;
    private ItemStack stolen=ItemStack.EMPTY;
    public SecondaryMob(EntityType<? extends SecondaryMob> type,Level level,SecondaryMobs.Spec spec) {
        super(type,level);this.spec=spec;
        if(spec.flying()) { moveControl=new FlyingMoveControl(this,20,true);navigation=new FlyingPathNavigation(this,level);setNoGravity(true); }
        if(spec.aquatic()) { moveControl=new SmoothSwimmingMoveControl(this,85,10,.1F,.5F,false);navigation=new WaterBoundPathNavigation(this,level); }
        goalSelector.addGoal(0,new FloatGoal(this));
        goalSelector.addGoal(1,new Goal(){
            {setFlags(java.util.EnumSet.of(Flag.MOVE,Flag.LOOK));}
            @Override public boolean canUse(){return rollingTicks>0;}
            @Override public void tick(){getNavigation().stop();}
        });
        goalSelector.addGoal(1,new Goal() {
            { setFlags(java.util.EnumSet.of(Flag.MOVE,Flag.LOOK)); }
            @Override public boolean canUse() { return fleeTicks>0; }
            @Override public void tick() {
                LivingEntity attacker=getLastHurtByMob();
                if(attacker==null && customer!=null)attacker=level().getPlayerByUUID(customer);
                if(attacker!=null) {Vec3 away=position().subtract(attacker.position()).normalize().scale(8);getNavigation().moveTo(getX()+away.x,getY(),getZ()+away.z,1.4);}
            }
        });
        goalSelector.addGoal(2,new MeleeAttackGoal(this,1.1,false) {
            @Override public boolean canUse() { return !friendly && rollingTicks==0 && !spec.id().equals("locust_swarm") && !spec.id().equals("swindler") && !spec.id().equals("famished_refugee") && !spec.id().equals("herb_picker") && !spec.id().equals("snail_maiden") && super.canUse(); }
            @Override public boolean canContinueToUse(){return rollingTicks==0&&!friendly&&super.canContinueToUse();}
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
        if(hardenTicks>0 && --hardenTicks==0)getAttribute(net.minecraft.world.entity.ai.attributes.Attributes.ARMOR).removeModifier(HARDENING);
        if(animationTicks>0)animationTicks--;else entityData.set(STATE,fleeTicks>0?3:getTarget()!=null?2:getDeltaMovement().horizontalDistanceSqr()>.001?1:0);
        if(spec.id().equals("swindler") && deceptionStage<3){setTarget(null);getNavigation().stop();animate(5,2);}
        if(friendly || spec.id().equals("famished_refugee") || spec.id().equals("herb_picker") || spec.id().equals("snail_maiden"))setTarget(null);
        if(getPersistentData().hasUUID("cod4Summoner")) SummonedGuard.tick(this);
        LivingEntity target=getTarget();
        if(rollingTicks>0){
            rollingTicks--;animate(5,2);
            if(horizontalCollision)rollingTicks=0;
            else if(target!=null && touching(target)){doHurtTarget(target);rollingTicks=0;}
        }
        if(spec.id().equals("locust_swarm") && specialCooldown==0){
            for(var victim:level().getEntitiesOfClass(Player.class,getBoundingBox(),p->p.isAlive()&&!p.isSpectator()&&!p.isCreative()&&!isAlliedTo(p)))
                if(contactAttack(victim))break;
        }
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
            case "stone_sprite" -> {beginStoneRoll(target);specialCooldown=60;}
            case "wild_boar","bandit_thug","golden_leopard","gray_falcon","bat_demon","carp_spirit","stone_worm","corpse_beetle","crab_soldier" -> {
                if(distance>3) {Vec3 leap=target.position().subtract(position()).normalize().scale(.6);setDeltaMovement(leap.x,spec.aquatic()?.5:spec.flying()?leap.y:.2,leap.z);}
                specialCooldown=60;animate(5,15);
            }
            case "gray_wolf" -> {
                int recruited=0;
                for(var wolf:level().getEntitiesOfClass(SecondaryMob.class,getBoundingBox().inflate(8),m->m.spec.id().equals("gray_wolf"))) {
                    if(wolf==this || recruited>=2)continue;wolf.setTarget(target);double side=(++recruited==1?1:-1)*2;wolf.getNavigation().moveTo(target.getX()+side,target.getY(),target.getZ()-side,1.2);
                }
                specialCooldown=80;
            }
            case "locust_swarm" -> { /* Damage is owned by actual body contact above. */ }
            default -> { }
        }
    }
    public boolean touching(LivingEntity target){return getBoundingBox().intersects(target.getBoundingBox());}
    public boolean contactAttack(LivingEntity target){
        if(!spec.id().equals("locust_swarm")||specialCooldown>0||!touching(target)||isAlliedTo(target))return false;
        if(!doHurtTarget(target))return false;
        specialCooldown=20;return true;
    }
    public void beginStoneRoll(LivingEntity target){
        if(!spec.id().equals("stone_sprite"))return;
        var armor=getAttribute(net.minecraft.world.entity.ai.attributes.Attributes.ARMOR);
        armor.removeModifier(HARDENING);
        armor.addTransientModifier(new net.minecraft.world.entity.ai.attributes.AttributeModifier(HARDENING,"stone hardening",12,net.minecraft.world.entity.ai.attributes.AttributeModifier.Operation.ADDITION));
        hardenTicks=40;rollingTicks=16;getNavigation().stop();
        Vec3 direction=target.position().subtract(position()).multiply(1,0,1).normalize().scale(.65);
        setDeltaMovement(direction.x,.08,direction.z);hurtMarked=true;animate(5,16);
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
        if(result && spec!=null && spec.id().equals("swindler")){deceptionStage=3;fleeTicks=200;animate(3,200);if(source.getEntity() instanceof Player p)customer=p.getUUID();}
        return result;
    }
    @Override protected InteractionResult mobInteract(Player p,InteractionHand hand) {
        ItemStack stack=p.getItemInHand(hand);
        if(spec.id().equals("swindler"))return swindle(p,hand);
        if(spec.id().equals("famished_refugee") && stack.isEdible() && !friendly) {
            if(!level().isClientSide){friendly=true;fleeTicks=0;setTarget(null);heal(10);if(!p.getAbilities().instabuild)stack.shrink(1);}
            return InteractionResult.sidedSuccess(level().isClientSide);
        }
        if(spec.id().equals("herb_picker") && stack.is(ExpansionContent.item("copper_coin")) && specialCooldown==0) {
            if(!level().isClientSide){if(!p.getAbilities().instabuild)stack.shrink(1);
                    ItemStack herbs=new ItemStack(com.dynasty.DynastyItems.TEA.get(),2);
                    if(!p.getInventory().add(herbs))p.drop(herbs,false);
                    p.displayClientMessage(net.minecraft.network.chat.Component.translatable("message.dynasty.cod4.herbs"),true);
                specialCooldown=200;}
            return InteractionResult.sidedSuccess(level().isClientSide);
        }
        return super.mobInteract(p,hand);
    }
    private InteractionResult swindle(Player p,InteractionHand hand){
        if(hand!=InteractionHand.MAIN_HAND)return InteractionResult.PASS;
        if(level().isClientSide)return InteractionResult.SUCCESS;
        ItemStack held=p.getItemInHand(hand);
        if(deceptionStage==0){deceptionStage=1;animate(5,2);tell(p,"swindler_injured");return InteractionResult.CONSUME;}
        if(deceptionStage==1 && held.is(ExpansionContent.item("copper_coin"))){
            customer=p.getUUID();deceptionStage=2;
            if(!p.getAbilities().instabuild)stolen=held.split(1);
            var fake=new ItemStack(Items.DEAD_BUSH);fake.getOrCreateTag().putUUID("cod4Swindler",getUUID());
            fake.setHoverName(net.minecraft.network.chat.Component.translatable("item.dynasty.cod4.false_medicine"));
            if(!p.getInventory().add(fake))p.drop(fake,false);
            tell(p,"swindler_suspect");return InteractionResult.CONSUME;
        }
        if(deceptionStage==2 && p.isShiftKeyDown() && p.getUUID().equals(customer) && held.is(Items.DEAD_BUSH)
                && held.hasTag() && held.getTag().hasUUID("cod4Swindler") && held.getTag().getUUID("cod4Swindler").equals(getUUID())){
            deceptionStage=3;fleeTicks=200;setTarget(null);getNavigation().stop();animate(3,200);
            tell(p,"swindler_exposed");return InteractionResult.CONSUME;
        }
        tell(p,deceptionStage==1?"swindler_injured":deceptionStage==2?"swindler_suspect":"swindler_exposed");
        return InteractionResult.CONSUME;
    }
    private static void tell(Player p,String key){p.displayClientMessage(net.minecraft.network.chat.Component.translatable("message.dynasty.cod4."+key),true);}
    @Override protected void dropCustomDeathLoot(DamageSource s,int looting,boolean recentlyHit) {super.dropCustomDeathLoot(s,looting,recentlyHit);if(!stolen.isEmpty()){spawnAtLocation(stolen);stolen=ItemStack.EMPTY;}}
    @Override public void addAdditionalSaveData(CompoundTag nbt) {super.addAdditionalSaveData(nbt);nbt.putBoolean("Cod4Friendly",friendly);nbt.put("Cod4Stolen",stolen.save(new CompoundTag()));nbt.putInt("Cod4Cooldown",specialCooldown);nbt.putInt("Cod4Deception",deceptionStage);nbt.putInt("Cod4Flee",fleeTicks);if(customer!=null)nbt.putUUID("Cod4Customer",customer);}
    @Override public void readAdditionalSaveData(CompoundTag nbt) {super.readAdditionalSaveData(nbt);friendly=nbt.getBoolean("Cod4Friendly");stolen=ItemStack.of(nbt.getCompound("Cod4Stolen"));specialCooldown=Math.max(0,Math.min(200,nbt.getInt("Cod4Cooldown")));deceptionStage=Math.max(0,Math.min(3,nbt.getInt("Cod4Deception")));fleeTicks=Math.max(0,Math.min(200,nbt.getInt("Cod4Flee")));customer=nbt.hasUUID("Cod4Customer")?nbt.getUUID("Cod4Customer"):null;getAttribute(net.minecraft.world.entity.ai.attributes.Attributes.ARMOR).removeModifier(HARDENING);hardenTicks=0;rollingTicks=0;}
    @Override public AnimatableInstanceCache getAnimatableInstanceCache() {return cache;}
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {controllers.add(new AnimationController<>(this,"body",4,state->state.setAndContinue(RawAnimation.begin().thenLoop(animation()))));}
}
