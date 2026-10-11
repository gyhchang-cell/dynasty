package com.dynasty.blueprint.elite;

import com.dynasty.blueprint.*;
import com.dynasty.blueprint.combat.*;
import net.minecraft.core.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.syncher.*;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.ai.goal.target.*;
import net.minecraft.world.entity.ai.navigation.*;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.*;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.*;
import software.bernie.geckolib.util.GeckoLibUtil;
import java.util.List;

/** Surface climbing uses native block collision. Acid and brood share finite owner budgets. */
public final class SpiderWoman extends Monster implements GeoEntity,Combatant {
    public static final String ID="gudu_tianzhunv";
    public static final SkillDefinition ACID=new SkillDefinition(371,"spider_acid",20,100,30,180,0,8,100,.5F,0,true,true,List.of(20,40,60,80,100));
    public static final SkillDefinition DROP=new SkillDefinition(372,"spider_drop",12,30,35,120,0,6,360,1.25F,.6,true,true,List.of(12));
    public static final SkillDefinition EGGS=new SkillDefinition(373,"spider_eggs",18,1,40,280,0,10,360,0,0,true,true,List.of(18));
    private static final EntityDataAccessor<Integer> SKILL=SynchedEntityData.defineId(SpiderWoman.class,EntityDataSerializers.INT),PHASE=SynchedEntityData.defineId(SpiderWoman.class,EntityDataSerializers.INT);
    private static final EntityDataAccessor<Long> START=SynchedEntityData.defineId(SpiderWoman.class,EntityDataSerializers.LONG);
    private static final EntityDataAccessor<Boolean> CEILING=SynchedEntityData.defineId(SpiderWoman.class,EntityDataSerializers.BOOLEAN),CLIMBING=SynchedEntityData.defineId(SpiderWoman.class,EntityDataSerializers.BOOLEAN);
    private final TimedAttack attack=new TimedAttack();
    private final AnimatableInstanceCache cache=GeckoLibUtil.createInstanceCache(this);
    private long nextChoice,deathStart=-1,animationStart=Long.MIN_VALUE,nextBite;
    private float partial;
    private boolean lootDropped,dropping,dropSpent;
    private String site="";
    private BlockPos home;
    public SpiderWoman(EntityType<? extends SpiderWoman> type,Level level){super(type,level);xpReward=30;}
    public TimedAttack attack(){return attack;}
    public int skillId(){return entityData.get(SKILL);}
    public long skillStart(){return entityData.get(START);}
    public AttackState phase(){return AttackState.values()[Math.max(0,Math.min(4,entityData.get(PHASE)))];}
    public boolean attachedToCeiling(){return entityData.get(CEILING);}
    public String encounterSite(){return site;}
    public void bindEncounter(String key){site=key.length()<=256?key:"";home=blockPosition();}
    public static SkillDefinition skill(int id){return switch(id){case 371->ACID;case 372->DROP;case 373->EGGS;default->null;};}
    @Override public Faction faction(){return Faction.SPIRITS;}
    @Override public MobRole role(){return MobRole.RANGED;}
    @Override protected PathNavigation createNavigation(Level level){return new WallClimberNavigation(this,level);}
    @Override public boolean onClimbable(){return entityData.get(CLIMBING);}
    @Override protected void defineSynchedData(){super.defineSynchedData();entityData.define(SKILL,0);entityData.define(PHASE,0);entityData.define(START,-1L);entityData.define(CEILING,false);entityData.define(CLIMBING,false);}
    @Override protected void registerGoals(){goalSelector.addGoal(0,new FloatGoal(this));goalSelector.addGoal(8,new LookAtPlayerGoal(this,Player.class,18));targetSelector.addGoal(1,new HurtByTargetGoal(this));targetSelector.addGoal(2,new NearestAttackableTargetGoal<>(this,Player.class,true));}
    public boolean enemy(LivingEntity e){return e!=null&&e.isAlive()&&!e.isSpectator()&&!Combatant.allied(this,e)&&!(e instanceof Player p&&p.isCreative());}
    public boolean ceilingSupported(){
        var pos=BlockPos.containing(getX(),getBoundingBox().maxY+.06,getZ());
        return level().hasChunkAt(pos)&&level().getBlockState(pos).isFaceSturdy(level(),pos,Direction.DOWN)
            &&level().noCollision(this,getBoundingBox().deflate(.01));
    }
    public boolean startSkill(int id,LivingEntity victim){
        var def=skill(id);if(level().isClientSide||!isAlive()||def==null||!enemy(victim)||!hasLineOfSight(victim))return false;
        if(id==373? !onGround(): !attachedToCeiling()||!ceilingSupported())return false;
        double distance=position().subtract(victim.position()).horizontalDistanceSqr();if(distance>def.maxRange()*def.maxRange())return false;
        var dir=victim.position().subtract(position()).multiply(1,0,1).normalize();if(dir.lengthSqr()<.001)dir=new Vec3(0,0,1);
        if(!attack.tryStart(def,level().getGameTime(),position(),dir,victim.getUUID()))return false;
        dropping=false;dropSpent=false;navigation.stop();setYRot((float)Math.toDegrees(Math.atan2(-dir.x,dir.z)));setYHeadRot(getYRot());yBodyRot=getYRot();sync();
        BlueprintVisualEvent.start(this,def,attack.origin(),dir,victim.getId());playSound(SoundEvents.SPIDER_AMBIENT,.85F,.55F);return true;
    }
    private void sync(){entityData.set(SKILL,attack.current()==null?0:attack.current().id());entityData.set(START,attack.started());entityData.set(PHASE,attack.state(level().getGameTime()).ordinal());}
    @Override protected void customServerAiStep(){super.customServerAiStep();combat();}
    @Override public void tick(){super.tick();if(!level().isClientSide&&isNoAi())combat();}
    private void combat(){
        if(!isAlive())return;long now=level().getGameTime();
        boolean supported=!dropping&&ceilingSupported();entityData.set(CEILING,supported);entityData.set(CLIMBING,horizontalCollision&&!dropping);setNoGravity(supported);
        if(supported)setDeltaMovement(getDeltaMovement().x,0,getDeltaMovement().z);
        else if(horizontalCollision&&!dropping)setDeltaMovement(getDeltaMovement().x,.16,getDeltaMovement().z);
        if(attack.current()!=null){
            var def=attack.current();long age=now-attack.started();navigation.stop();
            if((def==ACID||def==DROP&&age<12)&&!supported){attack.cancel();BlueprintVisualEvent.cancel(this);}
            else {
                if(!dropping)setDeltaMovement(0,getDeltaMovement().y,0);
                attack.advance(now,this::impact);
                if(dropping&&!dropSpent&&onGround()){
                    dropSpent=true;dropping=false;
                    for(var target:CombatGeometry.query((ServerLevel)level(),position(),Vec3.ZERO,CombatGeometry.Shape.CIRCLE,2,0,360,2,this::enemy).stream().limit(12).toList())
                        if(hasLineOfSight(target)&&target.hurt(damageSources().mobAttack(this),(float)getAttributeValue(Attributes.ATTACK_DAMAGE)*DROP.damageMultiplier()))target.knockback(.6,getX()-target.getX(),getZ()-target.getZ());
                    if(isAlive())setDeltaMovement(attack.direction().scale(-.22).add(0,.3,0));
                    playSound(SoundEvents.SPIDER_STEP,1,.5F);
                }
            }
        }
        if(dropping&&attack.current()!=DROP){dropping=false;dropSpent=true;}
        sync();if(isNoAi()||attack.state(now)!=AttackState.IDLE||now<nextChoice)return;nextChoice=now+10;
        var victim=getTarget();if(!enemy(victim)){setTarget(null);return;}
        if(home!=null&&victim.blockPosition().distSqr(home)>32*32){setTarget(null);navigation.moveTo(home.getX()+.5,home.getY(),home.getZ()+.5,.8);return;}
        for(int id:attachedToCeiling()?new int[]{371,372}:new int[]{373})if(startSkill(id,victim))return;
        if(attachedToCeiling()){
            var step=victim.position().subtract(position()).multiply(1,0,1).normalize().scale(.08);setDeltaMovement(step);
        }else{
            navigation.moveTo(victim,.9);
            if(distanceToSqr(victim)<9&&hasLineOfSight(victim)&&now>=nextBite){nextBite=now+30;doHurtTarget(victim);}
            if(onGround()&&now%20==0)seekWall();
        }
    }
    private void seekWall(){
        // Find a nearby loaded solid surface; the normal climbing navigator and collision do the ascent.
        BlockPos best=null;double distance=100;
        for(int x=-6;x<=6;x++)for(int z=-6;z<=6;z++)if(x*x+z*z>=9&&x*x+z*z<distance){var p=blockPosition().offset(x,1,z);
            if(level().hasChunkAt(p)&&level().getBlockState(p).isFaceSturdy(level(),p,Direction.UP)&&!level().getBlockState(p.above()).isAir()){best=p;distance=x*x+z*z;}}
        if(best!=null)navigation.moveTo(best.getX()+.5,getY()+3,best.getZ()+.5,.8);
    }
    private BlockPos floorAt(Vec3 point){
        var p=BlockPos.containing(point);for(int dy=0;dy<=12;dy++){var feet=p.below(dy);if(!level().hasChunkAt(feet))return null;
            if(level().getBlockState(feet.below()).isFaceSturdy(level(),feet.below(),Direction.UP)&&level().getBlockState(feet).isAir()&&level().getFluidState(feet).isEmpty())return feet;}
        return null;
    }
    private void impact(int frame){
        if(!(level() instanceof ServerLevel world)||attack.current()==null||!isAlive())return;
        if(attack.current()==ACID){
            int alive=world.getEntitiesOfClass(SkullBloodPool.class,getBoundingBox().inflate(32),pool->pool.ownedBy(this)).size();
            if(alive>=6)return;
            double distance=2+2*((frame-20)/20%3);var side=new Vec3(-attack.direction().z,0,attack.direction().x);
            for(int n=-1;n<=1&&alive<6;n++){
                var at=floorAt(attack.origin().add(attack.direction().scale(distance)).add(side.scale(n*1.5)));if(at==null)continue;
                var pool=BlueprintEntities.SKULL_BLOOD_POOL.get().create(world);if(pool==null)continue;
                pool.setPos(at.getX()+.5,at.getY()+.02,at.getZ()+.5);pool.setOwner(this);pool.activateSpiderAcid(world.getGameTime());
                if(world.addFreshEntity(pool))alive++;
            }
        }else if(attack.current()==DROP){
            // Actual downward movement is clipped by blocks. Only its first physical landing can hurt.
            dropping=true;dropSpent=false;entityData.set(CEILING,false);setNoGravity(false);setDeltaMovement(attack.direction().scale(.18).add(0,-.9,0));
        }else if(attack.current()==EGGS){
            int alive=world.getEntitiesOfClass(SpiderBrood.class,getBoundingBox().inflate(32),brood->brood.ownedBy(this)).size();
            var side=new Vec3(-attack.direction().z,0,attack.direction().x);
            for(int n=-1;n<=1&&alive<3;n++){
                var at=floorAt(position().add(attack.direction().scale(2)).add(side.scale(n*1.2)));if(at==null)continue;
                var brood=EliteContent.SPIDER_BROOD.get().create(world);if(brood==null)continue;
                brood.moveTo(at.getX()+.5,at.getY(),at.getZ()+.5,0,0);if(!world.noCollision(brood))continue;brood.launch(this,getTarget());if(world.addFreshEntity(brood))alive++;
            }
        }
    }
    public void clearOwned(){if(level() instanceof ServerLevel world){for(var e:world.getEntitiesOfClass(SpiderBrood.class,getBoundingBox().inflate(48),brood->brood.ownedBy(this)))e.discard();for(var e:world.getEntitiesOfClass(SkullBloodPool.class,getBoundingBox().inflate(48),pool->pool.ownedBy(this)))e.discard();}}
    @Override public boolean hurt(DamageSource source,float amount){
        float before=getHealth();boolean result=super.hurt(source,amount);
        if(result&&!level().isClientSide&&isAlive()&&before-getHealth()>=8&&attack.state(level().getGameTime())==AttackState.WINDUP){
            attack.stun(level().getGameTime(),20);dropping=false;dropSpent=true;navigation.stop();setDeltaMovement(0,getDeltaMovement().y,0);BlueprintVisualEvent.cancel(this);sync();
        }return result;
    }
    @Override public boolean causeFallDamage(float distance,float multiplier,DamageSource source){return false;}
    @Override public void die(DamageSource source){if(deathStart>=0)return;super.die(source);if(!isDeadOrDying())return;deathStart=level().getGameTime();attack.cancel();dropping=false;setNoGravity(false);entityData.set(CEILING,false);clearOwned();navigation.stop();setTarget(null);BlueprintVisualEvent.cancel(this);EliteEncounters.memberDied(this);entityData.set(SKILL,0);entityData.set(START,deathStart);entityData.set(PHASE,0);BlueprintVisualEvent.death(this);}
    @Override protected void dropAllDeathLoot(DamageSource source){if(lootDropped)return;lootDropped=true;super.dropAllDeathLoot(source);}
    @Override protected void tickDeath(){deathTime++;if(!level().isClientSide){deathTime=(int)Math.min(80,Math.max(deathTime,level().getGameTime()-deathStart));if(deathTime>=80)remove(RemovalReason.KILLED);}}
    @Override public void addAdditionalSaveData(CompoundTag t){super.addAdditionalSaveData(t);t.put("EliteAttack",attack.save());t.putString("EncounterSite",site);if(home!=null)t.putLong("Home",home.asLong());t.putLong("DeathStart",deathStart);t.putBoolean("LootDropped",lootDropped);t.putBoolean("Dropping",dropping);t.putBoolean("DropSpent",dropSpent);}
    @Override public void readAdditionalSaveData(CompoundTag t){super.readAdditionalSaveData(t);bindEncounter(t.getString("EncounterSite"));if(t.contains("Home"))home=BlockPos.of(t.getLong("Home"));deathStart=t.contains("DeathStart")?t.getLong("DeathStart"):-1;lootDropped=t.getBoolean("LootDropped");attack.load(t.getCompound("EliteAttack"),SpiderWoman::skill,level().getGameTime());dropping=t.getBoolean("Dropping")&&attack.current()==DROP;dropSpent=t.getBoolean("DropSpent");if(isDeadOrDying()){attack.cancel();entityData.set(SKILL,0);entityData.set(START,deathStart);entityData.set(PHASE,0);}else sync();entityData.set(CEILING,isAlive()&&!dropping&&ceilingSupported());setNoGravity(attachedToCeiling());}
    public String visualAnimation(){return isDeadOrDying()?"death":switch(skillId()){case 371->"acid";case 372->"drop";case 373->"eggs";default->hurtTime>0?"hurt":getDeltaMovement().lengthSqr()>.001?"walk":"idle";};}
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar c){c.add(new AnimationController<SpiderWoman>(this,"body",0,state->{partial=state.getPartialTick();var controller=state.getController();if(animationStart!=skillStart()){animationStart=skillStart();controller.forceAnimationReset();}String name=visualAnimation();controller.setAnimation(name.equals("idle")||name.equals("walk")?RawAnimation.begin().thenLoop("animation."+ID+"."+name):RawAnimation.begin().thenPlayAndHold("animation."+ID+"."+name));return software.bernie.geckolib.core.object.PlayState.CONTINUE;}){
        @Override protected double adjustTick(double tick){boolean reset=shouldResetTick;double local=super.adjustTick(tick);return !reset&&getAnimationState()==AnimationController.State.RUNNING&&skillStart()>=0&&(skillId()!=0||isDeadOrDying())?Math.max(0,level().getGameTime()-skillStart()+partial):local;}
    });}
    @Override public AnimatableInstanceCache getAnimatableInstanceCache(){return cache;}
}
