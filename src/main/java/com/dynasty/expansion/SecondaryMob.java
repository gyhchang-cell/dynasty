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
    final SecondaryCombatActions combatActions=new SecondaryCombatActions(this);
    private static final java.util.List<String> SKILL_ANIMATIONS=java.util.List.of("pounce","coil","stalk","dive","circle","burrow","eruption","pinch","sting","possession","return_water","side_charge");
    private int specialCooldown, fleeTicks, shellTicks, animationTicks;
    private int deceptionStage, hardenTicks, rollingTicks;
    private int waterDragTicks;
    private long waterDragReady;
    private int projectileWindup;
    private java.util.UUID pendingProjectile;
    private java.util.UUID draggedTarget;
    private net.minecraft.core.BlockPos waterAnchor,cropFleeOrigin;
    public static final int CROP_FLEE_TICKS=120;
    public boolean cropPest(){return java.util.Set.of("locust_swarm","corpse_beetle","venom_scorpion").contains(spec.id());}
    public boolean repelFromCrop(net.minecraft.core.BlockPos origin){
        if(level().isClientSide||!isAlive()||isNoAi()||!cropPest()||getPersistentData().hasUUID("cod4Summoner")||cropFleeOrigin!=null&&fleeTicks>0
            ||distanceToSqr(Vec3.atCenterOf(origin))>64)return false;
        cropFleeOrigin=origin.immutable();fleeTicks=CROP_FLEE_TICKS;setTarget(null);combatActions.reset();getNavigation().stop();animate(3,CROP_FLEE_TICKS);return true;
    }
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
            private int nextMove;
            @Override public boolean canUse() { return fleeTicks>0; }
            @Override public void start(){nextMove=0;}
            @Override public void tick() {
                if(cropFleeOrigin!=null){
                    if(tickCount<nextMove)return;nextMove=tickCount+10;
                    Vec3 away=position().subtract(Vec3.atCenterOf(cropFleeOrigin)).multiply(1,0,1).normalize();
                    if(away.lengthSqr()<.01)away=new Vec3(1,0,0);
                    getNavigation().moveTo(getX()+away.x*8,getY(),getZ()+away.z*8,1.4);return;
                }
                LivingEntity attacker=getLastHurtByMob();
                if(attacker==null && customer!=null)attacker=level().getPlayerByUUID(customer);
                if(attacker!=null) {Vec3 away=position().subtract(attacker.position()).normalize().scale(8);getNavigation().moveTo(getX()+away.x,getY(),getZ()+away.z,1.4);}
            }
        });
        if(spec.id().equals("clockwork_rat"))goalSelector.addGoal(1,new Goal(){
            private ItemEntity bait;private int nextMove,nextScan;
            {setFlags(java.util.EnumSet.of(Flag.MOVE,Flag.LOOK));}
            @Override public boolean canUse(){
                if(!stolen.isEmpty()||fleeTicks>0||tickCount<nextScan)return false;
                nextScan=tickCount+10;
                bait=level().getEntitiesOfClass(ItemEntity.class,getBoundingBox().inflate(8),
                    e->e.isAlive()&&e.getItem().is(ExpansionContent.item("qimen_gear"))&&distanceToSqr(e)<=64&&hasLineOfSight(e))
                    .stream().min(java.util.Comparator.comparingDouble(SecondaryMob.this::distanceToSqr)).orElse(null);
                return bait!=null;
            }
            @Override public boolean canContinueToUse(){return stolen.isEmpty()&&fleeTicks==0&&bait!=null&&bait.isAlive()
                &&bait.getItem().is(ExpansionContent.item("qimen_gear"))&&distanceToSqr(bait)<=64&&hasLineOfSight(bait);}
            @Override public void start(){nextMove=0;}
            @Override public void tick(){getLookControl().setLookAt(bait,30,30);if(--nextMove<=0){nextMove=10;getNavigation().moveTo(bait,1.3);}}
            @Override public void stop(){bait=null;getNavigation().stop();}
        });
        goalSelector.addGoal(2,new MeleeAttackGoal(this,1.1,false) {
            @Override public boolean canUse() { return !friendly && rollingTicks==0 && !combatActions.active() && !spec.id().equals("locust_swarm") && !spec.id().equals("swindler") && !spec.id().equals("famished_refugee") && !spec.id().equals("herb_picker") && !spec.id().equals("snail_maiden") && super.canUse(); }
            @Override public boolean canContinueToUse(){return rollingTicks==0&&!friendly&&!combatActions.active()&&super.canContinueToUse();}
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
    public String animation() { int state=entityData.get(STATE);if(state>=7&&state<7+SKILL_ANIMATIONS.size())return SKILL_ANIMATIONS.get(state-7);return switch(state) { case 1->"wander";case 2->"hunt";case 3->"flee";case 4->"attack";case 5->"special";case 6->"evade";default->"idle"; }; }
    void skillAnimation(String name){int index=SKILL_ANIMATIONS.indexOf(name);animate(index<0?name.equals("evade")?6:5:index+7,12);}
    private void animate(int state,int ticks) { entityData.set(STATE,state);animationTicks=ticks; }
    @Override public boolean isAlliedTo(Entity other) {
        if(getPersistentData().hasUUID("cod4Summoner")) {
            var owner=getPersistentData().getUUID("cod4Summoner");
            if(other.getUUID().equals(owner) || other.getPersistentData().hasUUID("cod4Summoner") && other.getPersistentData().getUUID("cod4Summoner").equals(owner))return true;
        }
        return super.isAlliedTo(other);
    }
    @Override public boolean checkSpawnObstruction(net.minecraft.world.level.LevelReader world){
        // Native Mob rejects all liquids by default. Aquatic actors must still
        // pass real obstruction while allowing their required water habitat.
        return spec!=null&&spec.aquatic()?world.isUnobstructed(this):super.checkSpawnObstruction(world);
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
        if(fleeTicks>0)fleeTicks--;if(fleeTicks==0)cropFleeOrigin=null;
        if(shellTicks>0)shellTicks--;
        if(hardenTicks>0 && --hardenTicks==0)getAttribute(net.minecraft.world.entity.ai.attributes.Attributes.ARMOR).removeModifier(HARDENING);
        if(animationTicks>0)animationTicks--;else entityData.set(STATE,fleeTicks>0?3:getTarget()!=null?2:getDeltaMovement().horizontalDistanceSqr()>.001?1:0);
        if(spec.id().equals("swindler") && deceptionStage<3){setTarget(null);getNavigation().stop();animate(5,2);}
        if(friendly || spec.id().equals("famished_refugee") || spec.id().equals("herb_picker") || spec.id().equals("snail_maiden"))setTarget(null);
        if(getPersistentData().hasUUID("cod4Summoner")) SummonedGuard.tick(this);
        tickWaterDrag();
        tickRangedSkill();
        combatActions.tick();
        LivingEntity target=getTarget();
        if(rollingTicks>0){
            rollingTicks--;animate(5,2);
            if(horizontalCollision)rollingTicks=0;
            else if(target!=null && touching(target)){doHurtTarget(target);rollingTicks=0;}
        }
        if(spec.id().equals("locust_swarm") && specialCooldown==0 && fleeTicks==0){
            for(var victim:level().getEntitiesOfClass(Player.class,getBoundingBox(),p->p.isAlive()&&!p.isSpectator()&&!p.isCreative()&&!isAlliedTo(p)))
                if(contactAttack(victim))break;
        }
        if(spec.family().equals("ghost")) { noPhysics=target!=null;setNoGravity(true);if(target!=null) setDeltaMovement(target.getEyePosition().subtract(position()).normalize().scale(.1)); }
        if(spec.flying() && target!=null && fleeTicks==0 && !combatActions.active() && tickCount%10==0) getMoveControl().setWantedPosition(target.getX(),target.getEyeY()+1,target.getZ(),1.2);
        if(spec.id().equals("clockwork_rat") && stolen.isEmpty() && tickCount%20==0) {
            var items=level().getEntitiesOfClass(ItemEntity.class,getBoundingBox().inflate(2),e->!e.getItem().isEmpty());
            if(!items.isEmpty()) {
                // Prefer the actual gear bait, but retain the original one-item theft/return ledger for all drops.
                var chosen=items.stream().filter(e->e.isAlive()&&e.getItem().is(ExpansionContent.item("qimen_gear"))&&hasLineOfSight(e))
                    .min(java.util.Comparator.comparingDouble(this::distanceToSqr)).orElse(items.get(0));
                stolen=chosen.getItem().split(1);if(chosen.getItem().isEmpty())chosen.discard();fleeTicks=80;
            }
        }
        if(spec.id().equals("night_watchman") && tickCount%40==0)addEffect(new MobEffectInstance(MobEffects.NIGHT_VISION,60));
        if(target==null || !hasLineOfSight(target) || specialCooldown>0 || combatActions.active() || fleeTicks>0) return;
        double distance=distanceToSqr(target);
        if(distance>100) return;
        if(combatActions.begin(target)){specialCooldown=80;return;}
        switch(spec.id()) {
            case "night_watchman","wooden_magpie" -> {
                for(var mob:level().getEntitiesOfClass(SecondaryMob.class,getBoundingBox().inflate(12),m->m.spec.id().equals(spec.id()))) if(mob!=this && !mob.friendly)mob.setTarget(target);
                playSound(SoundEvents.NOTE_BLOCK_HAT.get(),1,.7F);specialCooldown=100;animate(5,20);
            }
            case "tree_spirit","river_imp","lantern_ghost","jingwei_bird" -> {
                if(distance>4)beginRangedSkill(target);
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
    public boolean beginRangedSkill(LivingEntity target){
        if(projectileWindup>0||level().isClientSide||target==null||!target.isAlive()||isAlliedTo(target)||!hasLineOfSight(target))return false;
        pendingProjectile=target.getUUID();projectileWindup=6;getNavigation().stop();animate(5,16);return true;
    }
    public void tickRangedSkill(){
        if(projectileWindup<=0||!(level() instanceof net.minecraft.server.level.ServerLevel server))return;
        if(--projectileWindup>0)return;
        var target=server.getEntity(pendingProjectile);pendingProjectile=null;
        if(target instanceof LivingEntity living)fireSkillProjectile(living);
    }
    public SecondaryProjectile fireSkillProjectile(LivingEntity target){
        if(level().isClientSide||target==null||!target.isAlive()||isAlliedTo(target)||!hasLineOfSight(target)||distanceToSqr(target)>256)return null;
        int kind=switch(spec.id()){case "tree_spirit"->SecondaryProjectile.SEED;case "lantern_ghost"->SecondaryProjectile.LIGHT;
            case "river_imp"->SecondaryProjectile.WATER;case "jingwei_bird"->SecondaryProjectile.STONE;default->-1;};
        if(kind<0)return null;
        var projectile=SecondaryMobs.PROJECTILE.get().create(level());if(projectile==null)return null;
        projectile.kind(kind);projectile.setOwner(this);projectile.setPos(getEyePosition());
        Vec3 aim=target.getEyePosition().subtract(getEyePosition());
        if(kind==SecondaryProjectile.STONE)aim=aim.add(0,Math.sqrt(aim.horizontalDistanceSqr())*.035,0);
        projectile.shoot(aim.x,aim.y,aim.z,1.2F,1);
        if(!level().addFreshEntity(projectile))return null;
        animate(5,16);return projectile;
    }
    public boolean beginWaterDrag(LivingEntity target){
        if(level().isClientSide||waterDragTicks>0||level().getGameTime()<waterDragReady||target==null||!target.isAlive()||isAlliedTo(target)||ExpansionEffects.boss(target)
                ||distanceToSqr(target)>81||!hasLineOfSight(target)
                ||!java.util.Set.of("river_imp","drowning_ghost").contains(spec.id()))return false;
        net.minecraft.core.BlockPos nearest=null;double best=Double.MAX_VALUE;
        for(var pos:net.minecraft.core.BlockPos.betweenClosed(blockPosition().offset(-4,-2,-4),blockPosition().offset(4,2,4))){
            if(!level().hasChunkAt(pos)||!level().getFluidState(pos).is(net.minecraft.tags.FluidTags.WATER))continue;
            double d=target.distanceToSqr(Vec3.atCenterOf(pos));
            if(d<best&&level().clip(new net.minecraft.world.level.ClipContext(target.getEyePosition(),Vec3.atCenterOf(pos).add(0,.5,0),
                    net.minecraft.world.level.ClipContext.Block.COLLIDER,net.minecraft.world.level.ClipContext.Fluid.NONE,target)).getType()==net.minecraft.world.phys.HitResult.Type.MISS){best=d;nearest=pos.immutable();}
        }
        if(nearest==null)return false;
        waterAnchor=nearest;draggedTarget=target.getUUID();waterDragTicks=30;waterDragReady=level().getGameTime()+100;animate(5,30);
        CombatFeedback.tether(this,Vec3.atCenterOf(nearest));return true;
    }
    public void tickWaterDrag(){
        if(waterDragTicks<=0||!(level() instanceof net.minecraft.server.level.ServerLevel server))return;
        var entity=server.getEntity(draggedTarget);
        if(!(entity instanceof LivingEntity target)||!target.isAlive()||ExpansionEffects.boss(target)||isAlliedTo(target)
                ||distanceToSqr(target)>144||!hasLineOfSight(target)||!server.hasChunkAt(waterAnchor)
                ||!server.getFluidState(waterAnchor).is(net.minecraft.tags.FluidTags.WATER)) {waterDragTicks=0;return;}
        waterDragTicks--;animate(5,2);
        Vec3 direction=Vec3.atCenterOf(waterAnchor).subtract(target.position()).multiply(1,0,1);
        if(direction.lengthSqr()>.04){
            var old=target.getDeltaMovement();var next=new Vec3(old.x,0,old.z).add(direction.normalize().scale(.065));
            if(old.horizontalDistanceSqr()<=.0625){if(next.horizontalDistanceSqr()>.0625)next=next.normalize().scale(.25);target.setDeltaMovement(next.x,old.y,next.z);target.hurtMarked=true;}
        }
        if(target.isInWater()){if(target.getDeltaMovement().y>-.2)target.push(0,-.025,0);if(waterDragTicks%10==0)CombatFeedback.send(target,CombatFeedback.WATER);}
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
        if(isAlliedTo(victim)||cropFleeOrigin!=null&&fleeTicks>0)return false;
        boolean hit=super.doHurtTarget(victim);
        if(!hit || !(victim instanceof LivingEntity target))return hit;
        animate(4,12);
        combatActions.successfulMelee(target);
        switch(spec.id()) {
            case "giant_python","crab_soldier","tree_spirit" -> {
                ExpansionEffects.apply(target,ExpansionEffects.STAGGER,30);
                if(spec.id().equals("giant_python") && !ExpansionEffects.boss(target)) {target.setAirSupply(Math.max(0,target.getAirSupply()-40));target.hurt(target.damageSources().drown(),2);}
            }
            case "drowning_ghost","river_imp" -> {ExpansionEffects.apply(target,ExpansionEffects.FROST,80);target.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN,60,1));beginWaterDrag(target);if(isInWater()){target.push(0,-.18,0);target.setAirSupply(Math.max(0,target.getAirSupply()-20));}}
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
        if(result&&source.getEntity() instanceof LivingEntity attacker)combatActions.evade(attacker);
        if(result && spec!=null && (spec.neutral() || getHealth()<getMaxHealth()*.25F)) {fleeTicks=80;animate(3,30);}
        if(result && spec!=null && spec.id().equals("swindler")){deceptionStage=3;fleeTicks=200;animate(3,200);if(source.getEntity() instanceof Player p)customer=p.getUUID();}
        return result;
    }
    @Override protected InteractionResult mobInteract(Player p,InteractionHand hand) {
        ItemStack stack=p.getItemInHand(hand);
        if(spec.id().equals("wooden_magpie")&&stack.is(ExpansionContent.item("qimen_cable"))){
            if(hand!=InteractionHand.MAIN_HAND||!isAlive()||!p.isAlive()||p.isSpectator()||p.level()!=level()||distanceToSqr(p)>16)return InteractionResult.PASS;
            if(getHealth()>=getMaxHealth())return InteractionResult.PASS;
            if(!level().isClientSide){heal(20);if(!p.getAbilities().instabuild)stack.shrink(1);animate(5,12);tell(p,"magpie_repaired");}
            return InteractionResult.sidedSuccess(level().isClientSide);
        }
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
    @Override public void addAdditionalSaveData(CompoundTag nbt) {super.addAdditionalSaveData(nbt);nbt.putBoolean("Cod4Friendly",friendly);nbt.put("Cod4Stolen",stolen.save(new CompoundTag()));nbt.putInt("Cod4Cooldown",specialCooldown);nbt.putInt("Cod4Deception",deceptionStage);nbt.putInt("Cod4Flee",fleeTicks);if(cropFleeOrigin!=null&&fleeTicks>0)nbt.putLong("Cod4CropFleeOrigin",cropFleeOrigin.asLong());else nbt.remove("Cod4CropFleeOrigin");if(customer!=null)nbt.putUUID("Cod4Customer",customer);}
    @Override public void readAdditionalSaveData(CompoundTag nbt) {super.readAdditionalSaveData(nbt);friendly=nbt.getBoolean("Cod4Friendly");stolen=ItemStack.of(nbt.getCompound("Cod4Stolen"));specialCooldown=Math.max(0,Math.min(200,nbt.getInt("Cod4Cooldown")));deceptionStage=Math.max(0,Math.min(3,nbt.getInt("Cod4Deception")));fleeTicks=Math.max(0,Math.min(200,nbt.getInt("Cod4Flee")));cropFleeOrigin=nbt.contains("Cod4CropFleeOrigin",net.minecraft.nbt.Tag.TAG_LONG)&&fleeTicks>0&&cropPest()?net.minecraft.core.BlockPos.of(nbt.getLong("Cod4CropFleeOrigin")):null;
        if(cropFleeOrigin!=null&&(distanceToSqr(Vec3.atCenterOf(cropFleeOrigin))>4096||!level().getWorldBorder().isWithinBounds(cropFleeOrigin)))cropFleeOrigin=null;
        customer=nbt.hasUUID("Cod4Customer")?nbt.getUUID("Cod4Customer"):null;getAttribute(net.minecraft.world.entity.ai.attributes.Attributes.ARMOR).removeModifier(HARDENING);hardenTicks=0;rollingTicks=0;combatActions.reset();waterDragTicks=0;waterDragReady=0;draggedTarget=null;waterAnchor=null;projectileWindup=0;pendingProjectile=null;}
    @Override public AnimatableInstanceCache getAnimatableInstanceCache() {return cache;}
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {controllers.add(new AnimationController<>(this,"body",4,state->state.setAndContinue(RawAnimation.begin().thenLoop(animation()))));}
}
