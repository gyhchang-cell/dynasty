package com.dynasty.blueprint.elite;

import com.dynasty.blueprint.*;
import com.dynasty.blueprint.combat.*;
import net.minecraft.core.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.syncher.*;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.control.FlyingMoveControl;
import net.minecraft.world.entity.ai.goal.target.*;
import net.minecraft.world.entity.ai.navigation.FlyingPathNavigation;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.*;
import net.minecraft.world.phys.*;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.*;
import software.bernie.geckolib.util.GeckoLibUtil;
import java.util.*;

/** One ordinary colliding flyer, eight articulated heads and a severed central neck. */
public final class GhostCarriageBird extends Monster implements GeoEntity,Combatant {
    public static final String ID="guiche_jiushouniao";
    public static final SkillDefinition PECK=new SkillDefinition(311,"bird_peck",12,61,24,120,0,2.5,360,.5F,0,true,true,
        java.util.stream.IntStream.range(0,16).map(n->12+n*4).boxed().toList());
    public static final SkillDefinition BOMB=new SkillDefinition(312,"bird_bomb",20,1,30,180,0,10,60,1,0,true,true,List.of(20));
    public static final SkillDefinition DIVE=new SkillDefinition(313,"bird_dive",24,50,40,220,0,16,0,1,.4,true,true,List.of());
    private static final EntityDataAccessor<Integer> SKILL=SynchedEntityData.defineId(GhostCarriageBird.class,EntityDataSerializers.INT);
    private static final EntityDataAccessor<Integer> PHASE=SynchedEntityData.defineId(GhostCarriageBird.class,EntityDataSerializers.INT);
    private static final EntityDataAccessor<Long> START=SynchedEntityData.defineId(GhostCarriageBird.class,EntityDataSerializers.LONG);
    private static final EntityDataAccessor<Integer> CAPTIVE=SynchedEntityData.defineId(GhostCarriageBird.class,EntityDataSerializers.INT);
    private final TimedAttack attack=new TimedAttack();
    private final AnimatableInstanceCache cache=GeckoLibUtil.createInstanceCache(this);
    private Vec3 landing=Vec3.ZERO,dive=Vec3.ZERO;
    private UUID captive;
    private double baseY;
    private long releaseAt,deathStart=-1,nextChoice;
    private boolean contacted,lootDropped;
    private String site="";
    private float animationPartial;
    private long animationStart=Long.MIN_VALUE;
    public GhostCarriageBird(EntityType<? extends GhostCarriageBird> type,Level level){
        super(type,level);xpReward=30;setNoGravity(true);
        navigation=new FlyingPathNavigation(this,level);moveControl=new FlyingMoveControl(this,16,true);
    }
    @Override protected void defineSynchedData(){super.defineSynchedData();entityData.define(SKILL,0);entityData.define(PHASE,0);entityData.define(START,-1L);entityData.define(CAPTIVE,-1);}
    @Override protected void registerGoals(){targetSelector.addGoal(1,new HurtByTargetGoal(this));targetSelector.addGoal(2,new NearestAttackableTargetGoal<>(this,Player.class,true));}
    @Override public Faction faction(){return Faction.SPIRITS;}
    @Override public MobRole role(){return MobRole.BEAST;}
    public TimedAttack attack(){return attack;}
    public int skillId(){return entityData.get(SKILL);}
    public long skillStart(){return entityData.get(START);}
    public int captiveId(){return entityData.get(CAPTIVE);}
    public AttackState phase(){return AttackState.values()[Math.min(4,Math.max(0,entityData.get(PHASE)))];}
    public Vec3 landing(){return landing;}
    public Vec3 telegraphOrigin(){return skillId()==PECK.id()?landing:new Vec3(attack.origin().x,landing.y,attack.origin().z);}
    public static Vec3 bloodLanding(Vec3 origin,Vec3 forward,int index){
        var side=new Vec3(forward.z,0,-forward.x);
        return Vec3.atBottomCenterOf(BlockPos.containing(origin.add(forward.scale(3+(index/4)*3)).add(side.scale(-1.8+(index%4)*1.2)))).add(0,.03,0);
    }
    public void bindEncounter(String key){site=key.length()<=256?key:"";}
    public String encounterSite(){return site;}
    public static SkillDefinition skill(int id){return switch(id){case 311->PECK;case 312->BOMB;case 313->DIVE;default->null;};}
    private boolean enemy(LivingEntity e){return e!=null&&e.isAlive()&&!e.isSpectator()&&!Combatant.allied(this,e)&&!(e instanceof Player p&&p.isCreative());}
    private LivingEntity resolve(UUID id){return id!=null&&level() instanceof ServerLevel s&&s.getEntity(id) instanceof LivingEntity e?e:null;}
    public boolean startSkill(int id,LivingEntity victim){
        var def=skill(id);if(level().isClientSide||!isAlive()||def==null||!enemy(victim)||distanceToSqr(victim)>256||!hasLineOfSight(victim))return false;
        if(id==PECK.id()&&(position().subtract(victim.position()).horizontalDistanceSqr()>6.25||getY()<victim.getY()+1))return false;
        var direction=victim.position().subtract(position()).multiply(1,0,1).normalize();if(direction.lengthSqr()<.001)direction=getLookAngle().multiply(1,0,1).normalize();
        if(!attack.tryStart(def,level().getGameTime(),position(),direction,victim.getUUID()))return false;
        landing=victim.position();contacted=false;navigation.stop();setDeltaMovement(Vec3.ZERO);
        dive=landing.add(0,.6,0).subtract(position()).normalize();
        setYRot((float)Math.toDegrees(Math.atan2(-direction.x,direction.z)));yBodyRot=getYRot();setYHeadRot(getYRot());sync();
        BlueprintVisualEvent.start(this,def,telegraphOrigin(),direction,victim.getId());
        playSound(id==BOMB.id()?SoundEvents.GHAST_WARN:SoundEvents.PHANTOM_AMBIENT,.8F,.55F);return true;
    }
    private void sync(){entityData.set(SKILL,attack.current()==null?0:attack.current().id());entityData.set(START,attack.started());entityData.set(PHASE,attack.state(level().getGameTime()).ordinal());}
    @Override protected void customServerAiStep(){super.customServerAiStep();combat();}
    @Override public void tick(){super.tick();if(!level().isClientSide&&isNoAi())combat();}
    @Override public void travel(Vec3 input){
        if(isAlive()){moveRelative(.06F,input);move(MoverType.SELF,getDeltaMovement());setDeltaMovement(getDeltaMovement().scale(.9));}
        else super.travel(input);
    }
    @Override protected void checkFallDamage(double amount,boolean ground,net.minecraft.world.level.block.state.BlockState state,BlockPos pos){if(!isAlive())super.checkFallDamage(amount,ground,state,pos);}
    private void combat(){
        if(!isAlive())return;long now=level().getGameTime();
        if(captive!=null){tickCaptive(now);if(captive!=null){sync();return;}}
        var current=attack.current();
        if(current!=null){
            navigation.stop();setDeltaMovement(Vec3.ZERO);
            if(current==DIVE)tickDive(now);else attack.advance(now,this::impact);
            sync();
        }
        if(isNoAi()||attack.state(now)!=AttackState.IDLE)return;
        var victim=getTarget();if(!enemy(victim)){setTarget(null);return;}
        var hovering=victim.position().add(0,3.5,0);
        if(now>=nextChoice){nextChoice=now+20;
            int[] order=position().subtract(victim.position()).horizontalDistanceSqr()<=6.25?new int[]{311,312,313}:new int[]{312,313};
            for(int id:order)if(startSkill(id,victim))return;
        }
        var feet=BlockPos.containing(hovering);
        if(level().hasChunkAt(feet)&&level().noCollision(this,getType().getDimensions().makeBoundingBox(hovering.x,hovering.y,hovering.z)))moveControl.setWantedPosition(hovering.x,hovering.y,hovering.z,.75);
    }
    private void impact(int frame){
        if(!(level() instanceof ServerLevel server)||!isAlive())return;
        if(attack.current()==PECK){
            for(var hit:CombatGeometry.query(server,landing,attack.direction(),CombatGeometry.Shape.CIRCLE,2.5,0,360,2,
                    e->enemy(e)&&hasLineOfSight(e))){
                hit.invulnerableTime=0;hit.hurt(damageSources().mobAttack(this),(float)getAttributeValue(Attributes.ATTACK_DAMAGE)*.5F);if(!isAlive())return;
            }
        }else if(attack.current()==BOMB){
            // Eight warned landing cells, at most eight clouds belonging to this encounter.
            var forward=attack.direction();
            int alive=server.getEntitiesOfClass(SkullBloodPool.class,getBoundingBox().inflate(24),p->p.ownedBy(this)&&p.isAlive()).size();
            for(int n=0;n<8&&alive<8;n++){
                var at=bloodLanding(telegraphOrigin(),forward,n);var feet=BlockPos.containing(at);
                if(!server.hasChunkAt(feet)||!server.getBlockState(feet.below()).isFaceSturdy(server,feet.below(),Direction.UP)
                        ||!server.getBlockState(feet).getCollisionShape(server,feet).isEmpty())continue;
                if(server.clip(new ClipContext(position(),at,ClipContext.Block.COLLIDER,ClipContext.Fluid.NONE,this)).getType()!=HitResult.Type.MISS)continue;
                var pool=new SkullBloodPool(BlueprintEntities.SKULL_BLOOD_POOL.get(),server);pool.setOwner(this);pool.activate(server.getGameTime());pool.setBirdVenom(true);pool.setPos(at.x,at.y,at.z);
                if(server.addFreshEntity(pool))alive++;
            }
        }
    }
    private void tickDive(long now){
        long age=now-attack.started();
        if(age<24){
            // Ordinary collision movement to a maximum eight blocks over the locked landing.
            double climb=Math.min(.34,landing.y+8-getY());if(climb>0)move(MoverType.SELF,new Vec3(0,climb,0));
            dive=landing.add(0,.6,0).subtract(position()).normalize();return;
        }
        if(!contacted&&age<54){
            var step=dive.scale(.8);var before=position();move(MoverType.SELF,step);
            var victim=resolve(attack.target());
            if(enemy(victim)&&hasLineOfSight(victim)&&getBoundingBox().inflate(.5).intersects(victim.getBoundingBox())){
                contacted=true;
                if(victim instanceof Player p&&p.isBlocking()&&CombatGeometry.inFront(p.position(),p.getLookAngle(),position(),140)){stun(40);return;}
                if(victim.getPersistentData().getLong("DynastyBirdEscapeUntil")>now){stun(40);return;}
                if(victim.hurt(damageSources().mobAttack(this),6)&&isAlive()){
                    captive=victim.getUUID();baseY=victim.getY();releaseAt=now+24;entityData.set(CAPTIVE,victim.getId());
                    victim.getPersistentData().putLong("DynastyBirdEscapeUntil",now+160);victim.addEffect(new MobEffectInstance(MobEffects.SLOW_FALLING,160),this);victim.fallDistance=0;return;
                }
            }
            if(horizontalCollision||verticalCollision||position().distanceToSqr(before)<.002){contacted=true;stun(40);return;}
        }
        if(age>=54&&!contacted){contacted=true;stun(40);return;}
        attack.advance(now,this::impact);
    }
    private void tickCaptive(long now){
        var victim=resolve(captive);
        if(!enemy(victim)||victim.isShiftKeyDown()||distanceToSqr(victim)>25||!hasLineOfSight(victim)||victim.getY()>baseY+6){release();stun(40);return;}
        if(now>=releaseAt){victim.hurt(damageSources().mobAttack(this),6);victim.setDeltaMovement(0,-.2,0);victim.hurtMarked=true;release();stun(40);return;}
        if(level().clip(new ClipContext(victim.getEyePosition(),victim.getEyePosition().add(0,.6,0),ClipContext.Block.COLLIDER,ClipContext.Fluid.NONE,this)).getType()!=HitResult.Type.MISS){release();stun(40);return;}
        move(MoverType.SELF,new Vec3(0,getY()<baseY+6?.18:0,0));
        var pull=position().subtract(victim.position()).multiply(1,0,1);var side=pull.lengthSqr()>.25?pull.normalize().scale(.08):Vec3.ZERO;
        victim.setDeltaMovement(side.x,Math.max(0,Math.min(.18,baseY+6-victim.getY())),side.z);victim.fallDistance=0;victim.hurtMarked=true;
    }
    private void release(){var victim=resolve(captive);if(victim!=null){victim.fallDistance=0;victim.addEffect(new MobEffectInstance(MobEffects.SLOW_FALLING,100),this);}captive=null;releaseAt=0;entityData.set(CAPTIVE,-1);}
    private void stun(int ticks){attack.stun(level().getGameTime(),ticks);navigation.stop();setDeltaMovement(Vec3.ZERO);BlueprintVisualEvent.cancel(this);sync();}
    @Override public boolean hurt(DamageSource source,float amount){boolean accepted=super.hurt(source,amount);if(accepted&&isAlive()&&captive!=null&&amount>=3){release();stun(40);}return accepted;}
    @Override public void die(DamageSource source){
        if(deathStart>=0)return;super.die(source);if(!isDeadOrDying())return;
        deathStart=level().getGameTime();release();attack.cancel();navigation.stop();setNoGravity(false);
        if(level() instanceof ServerLevel server){BlueprintVisualEvent.cancel(this);EliteEncounters.memberDied(this);
            server.getEntitiesOfClass(SkullBloodPool.class,getBoundingBox().inflate(24),p->p.ownedBy(this)).forEach(Entity::discard);}
        entityData.set(SKILL,0);entityData.set(START,deathStart);entityData.set(PHASE,AttackState.IDLE.ordinal());
        BlueprintVisualEvent.death(this);
    }
    @Override protected void dropAllDeathLoot(DamageSource source){if(!lootDropped){lootDropped=true;super.dropAllDeathLoot(source);}}
    @Override protected void tickDeath(){
        deathTime++;
        if(!level().isClientSide){
            // LivingEntity stops ordinary travel once dead. Continue native collision movement
            // during the authored fall instead of leaving a NoAI or flying corpse suspended.
            var motion=getDeltaMovement();var step=new Vec3(motion.x*.8,Math.max(-.8,motion.y-.08),motion.z*.8);
            move(MoverType.SELF,step);setDeltaMovement(onGround()?Vec3.ZERO:step);
            deathTime=(int)Math.max(deathTime,level().getGameTime()-deathStart);if(deathTime>=100)remove(RemovalReason.KILLED);
        }
    }
    @Override public void addAdditionalSaveData(CompoundTag t){super.addAdditionalSaveData(t);t.put("EliteAttack",attack.save());t.putString("EncounterSite",site);t.putLong("DeathStart",deathStart);t.putBoolean("LootDropped",lootDropped);t.putBoolean("Contacted",contacted);
        t.putDouble("LandX",landing.x);t.putDouble("LandY",landing.y);t.putDouble("LandZ",landing.z);t.putDouble("DX",dive.x);t.putDouble("DY",dive.y);t.putDouble("DZ",dive.z);t.putBoolean("WasHolding",captive!=null);}
    @Override public void readAdditionalSaveData(CompoundTag t){
        super.readAdditionalSaveData(t);bindEncounter(t.getString("EncounterSite"));lootDropped=t.getBoolean("LootDropped");deathStart=t.contains("DeathStart")?t.getLong("DeathStart"):-1;contacted=t.getBoolean("Contacted");
        landing=new Vec3(t.getDouble("LandX"),t.getDouble("LandY"),t.getDouble("LandZ"));dive=new Vec3(t.getDouble("DX"),t.getDouble("DY"),t.getDouble("DZ"));
        attack.load(t.getCompound("EliteAttack"),GhostCarriageBird::skill,level().getGameTime());
        if(!Double.isFinite(landing.lengthSqr()+dive.lengthSqr())||landing.distanceToSqr(position())>32*32)attack.cancel();
        if(t.getBoolean("WasHolding"))attack.stun(level().getGameTime(),40);release();
        if(isDeadOrDying()){setNoGravity(false);attack.cancel();entityData.set(SKILL,0);entityData.set(START,deathStart);entityData.set(PHASE,AttackState.IDLE.ordinal());}else{setNoGravity(true);sync();}
    }
    public String visualAnimation(){return isDeadOrDying()?"death":switch(skillId()){case 311->"peck";case 312->"bomb";case 313->"dive";default->hurtTime>0?"hurt":phase()==AttackState.STUN?"stunned":"fly";};}
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar registrar){
        registrar.add(new AnimationController<GhostCarriageBird>(this,"body",0,state->{animationPartial=state.getPartialTick();var c=state.getController();if(animationStart!=skillStart()){animationStart=skillStart();c.forceAnimationReset();}
            var clip="animation."+ID+"."+visualAnimation();c.setAnimation(skillId()==0&&!isDeadOrDying()?RawAnimation.begin().thenLoop(clip):RawAnimation.begin().thenPlayAndHold(clip));return software.bernie.geckolib.core.object.PlayState.CONTINUE;}){
            @Override protected double adjustTick(double tick){boolean reset=shouldResetTick;double value=super.adjustTick(tick);if(reset||getAnimationState()!=AnimationController.State.RUNNING)return value;return skillStart()>=0&&(skillId()!=0||isDeadOrDying())?Math.max(0,level().getGameTime()-skillStart()+animationPartial):value;}
        });
    }
    @Override public AnimatableInstanceCache getAnimatableInstanceCache(){return cache;}
}
