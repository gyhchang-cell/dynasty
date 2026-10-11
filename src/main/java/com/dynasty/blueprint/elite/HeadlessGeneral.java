package com.dynasty.blueprint.elite;

import com.dynasty.blueprint.BlueprintEntities;
import com.dynasty.blueprint.BlueprintSpawnState;
import com.dynasty.blueprint.BlueprintVisualEvent;
import com.dynasty.blueprint.SkullBloodPool;
import com.dynasty.blueprint.combat.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.syncher.*;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.ai.goal.target.*;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.*;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.*;
import software.bernie.geckolib.util.GeckoLibUtil;
import java.util.List;

/** Three authored actions share the existing server clock; target points never follow the camera. */
public final class HeadlessGeneral extends Monster implements GeoEntity, Combatant {
    public static final String ID="xianzhen_duantoujiang";
    public static final SkillDefinition ROAR=new SkillDefinition(301,"headless_roar",24,6,20,140,0,10,17,1,.4,false,true,List.of(24));
    public static final SkillDefinition SPIN=new SkillDefinition(302,"headless_spin",16,31,30,180,0,3.5,360,1.1F,.35,false,true,List.of(26,36,46));
    public static final SkillDefinition THROW=new SkillDefinition(303,"headless_throw",20,6,24,160,0,2,360,1.2F,.5,true,true,List.of(20));
    private static final EntityDataAccessor<Integer> SKILL=SynchedEntityData.defineId(HeadlessGeneral.class,EntityDataSerializers.INT);
    private static final EntityDataAccessor<Integer> PHASE=SynchedEntityData.defineId(HeadlessGeneral.class,EntityDataSerializers.INT);
    private static final EntityDataAccessor<Long> START=SynchedEntityData.defineId(HeadlessGeneral.class,EntityDataSerializers.LONG);
    private final TimedAttack attack=new TimedAttack();
    private final AnimatableInstanceCache cache=GeckoLibUtil.createInstanceCache(this);
    private Vec3 landing=Vec3.ZERO;
    private long deathStart=-1,nextChoice;
    private boolean lootDropped;
    private float animationPartial;
    private long animationStart=Long.MIN_VALUE;
    private String site="";
    private int comboChoice;
    public HeadlessGeneral(EntityType<? extends HeadlessGeneral> type,Level level){super(type,level);xpReward=25;setMaxUpStep(.6F);}
    public TimedAttack attack(){return attack;}
    public int skillId(){return entityData.get(SKILL);}
    public long skillStart(){return entityData.get(START);}
    public AttackState phase(){return AttackState.values()[Math.min(4,Math.max(0,entityData.get(PHASE)))];}
    public Vec3 landing(){return landing;}
    public void bindEncounter(String key){site=key.length()<=256?key:"";}
    public String encounterSite(){return site;}
    public static SkillDefinition skill(int id){return switch(id){case 301->ROAR;case 302->SPIN;case 303->THROW;default->null;};}
    @Override public Faction faction(){return Faction.SPIRITS;}
    @Override public MobRole role(){return MobRole.MELEE;}
    @Override protected void defineSynchedData(){super.defineSynchedData();entityData.define(SKILL,0);entityData.define(PHASE,0);entityData.define(START,-1L);}
    @Override protected void registerGoals(){
        goalSelector.addGoal(0,new FloatGoal(this));goalSelector.addGoal(7,new WaterAvoidingRandomStrollGoal(this,.6));
        goalSelector.addGoal(8,new LookAtPlayerGoal(this,Player.class,16));goalSelector.addGoal(9,new RandomLookAroundGoal(this));
        targetSelector.addGoal(1,new HurtByTargetGoal(this));targetSelector.addGoal(2,new NearestAttackableTargetGoal<>(this,Player.class,true));
    }
    private boolean enemy(LivingEntity e){return e!=null&&e.isAlive()&&!e.isSpectator()&&!Combatant.allied(this,e)
        &&!(e instanceof Player p&&p.isCreative());}
    public boolean startSkill(int id,LivingEntity victim){
        var def=skill(id);if(level().isClientSide||!isAlive()||def==null||!enemy(victim)||distanceToSqr(victim)>256||!hasLineOfSight(victim))return false;
        if(id==SPIN.id()&&distanceToSqr(victim)>36)return false;
        var direction=victim.position().subtract(position()).multiply(1,0,1).normalize();if(direction.lengthSqr()<.001)direction=getLookAngle().multiply(1,0,1).normalize();
        if(!attack.tryStart(def,level().getGameTime(),position(),direction,victim.getUUID()))return false;
        landing=victim.position();navigation.stop();setYRot((float)Math.toDegrees(Math.atan2(-direction.x,direction.z)));yBodyRot=getYRot();setYHeadRot(getYRot());sync();
        BlueprintVisualEvent.start(this,def,id==THROW.id()?landing:attack.origin(),direction,victim.getId());
        playSound(id==ROAR.id()?SoundEvents.WARDEN_SONIC_CHARGE:SoundEvents.IRON_GOLEM_ATTACK,.7F,.65F);return true;
    }
    @Override protected void customServerAiStep(){super.customServerAiStep();combat();}
    @Override public void tick(){super.tick();if(!level().isClientSide&&isNoAi())combat();}
    private void combat(){
        if(!isAlive())return;long now=level().getGameTime();
        if(attack.current()!=null){navigation.stop();setDeltaMovement(getDeltaMovement().multiply(.2,1,.2));attack.advance(now,this::impact);if(!isAlive())return;sync();}
        if(isNoAi()||attack.state(now)!=AttackState.IDLE)return;
        var victim=getTarget();if(!enemy(victim)){setTarget(null);return;}
        if(now<nextChoice)return;nextChoice=now+10;
        int[] order=distanceToSqr(victim)<=30?new int[]{302,301,303}:new int[]{303,301};
        for(int i=0;i<order.length;i++)if(startSkill(order[Math.floorMod(comboChoice+i,order.length)],victim)){comboChoice++;return;}
        navigation.moveTo(victim,.85);
    }
    private void sync(){entityData.set(SKILL,attack.current()==null?0:attack.current().id());entityData.set(START,attack.started());entityData.set(PHASE,attack.state(level().getGameTime()).ordinal());}
    private void impact(int frame){
        if(!(level() instanceof ServerLevel server)||!isAlive()||attack.current()==null)return;
        var def=attack.current();Vec3 origin=def.id()==THROW.id()?landing:def.id()==SPIN.id()?position():attack.origin();
        // The spin advances by ordinary collision movement, at most two blocks per turn.
        if(def.id()==SPIN.id()){
            var step=attack.direction().scale(2);move(MoverType.SELF,step);origin=position();
            if(horizontalCollision){attack.stun(server.getGameTime(),30);BlueprintVisualEvent.cancel(this);sync();return;}
        }
        var shape=def.id()==ROAR.id()?CombatGeometry.Shape.SECTOR:CombatGeometry.Shape.CIRCLE;
        for(var hit:CombatGeometry.query(server,origin,attack.direction(),shape,def.maxRange(),0,def.angleDegrees(),2.5,e->enemy(e)&&hasLineOfSight(e))){
            if(def.id()==ROAR.id()&&hit instanceof Player player&&player.isBlocking())player.disableShield(true);
            hit.invulnerableTime=0;
            var source=def.id()==ROAR.id()?damageSources().indirectMagic(this,this):damageSources().mobAttack(this);
            if(hit.hurt(source,(float)getAttributeValue(Attributes.ATTACK_DAMAGE)*def.damageMultiplier())){
                var away=hit.position().subtract(origin);hit.knockback(def.knockback(),-away.x,-away.z);
                if(def.id()==ROAR.id())hit.addEffect(new MobEffectInstance(MobEffects.WEAKNESS,60),this);
            }
            if(!isAlive()||attack.current()!=def)return;
        }
        if(def.id()==THROW.id()&&server.getEntitiesOfClass(SkullBloodPool.class,new AABB(landing,landing).inflate(16),Entity::isAlive).size()<4){
            var feet=net.minecraft.core.BlockPos.containing(landing);var floor=feet.below();
            if(server.hasChunkAt(feet)&&server.getBlockState(floor).isFaceSturdy(server,floor,net.minecraft.core.Direction.UP)
                    &&server.getBlockState(feet).getCollisionShape(server,feet).isEmpty()){
                var pool=new SkullBloodPool(BlueprintEntities.SKULL_BLOOD_POOL.get(),server);pool.setOwner(this);pool.activate(server.getGameTime());pool.setRadius(2);
                pool.setPos(landing.x,landing.y+.03,landing.z);server.addFreshEntity(pool);
            }
        }
        playSound(SoundEvents.PLAYER_ATTACK_SWEEP,.8F,.5F);
    }
    /** Rear blows break the head-throw tell; three full spins instead expose a 30-tick recovery. */
    @Override public boolean hurt(DamageSource source,float amount){
        boolean rear=source.getEntity() instanceof LivingEntity attacker
            &&!CombatGeometry.inFront(position(),getLookAngle(),attacker.position(),180);
        boolean accepted=super.hurt(source,amount);
        if(accepted&&isAlive()&&rear&&attack.current()==THROW&&attack.state(level().getGameTime())==AttackState.WINDUP){
            attack.stun(level().getGameTime(),30);BlueprintVisualEvent.cancel(this);sync();
        }
        return accepted;
    }
    @Override public void die(DamageSource source){
        if(deathStart>=0)return;super.die(source);if(!isDeadOrDying())return;
        deathStart=level().getGameTime();attack.cancel();navigation.stop();setTarget(null);
        if(!level().isClientSide){BlueprintVisualEvent.cancel(this);EliteEncounters.memberDied(this);}
        entityData.set(SKILL,0);entityData.set(START,deathStart);entityData.set(PHASE,AttackState.IDLE.ordinal());
    }
    @Override protected void dropAllDeathLoot(DamageSource source){if(lootDropped)return;lootDropped=true;super.dropAllDeathLoot(source);}
    @Override protected void tickDeath(){deathTime++;if(!level().isClientSide){deathTime=(int)Math.min(70,Math.max(deathTime,level().getGameTime()-deathStart));if(deathTime>=70)remove(RemovalReason.KILLED);}}
    @Override public void addAdditionalSaveData(CompoundTag t){super.addAdditionalSaveData(t);t.put("EliteAttack",attack.save());t.putString("EncounterSite",site);t.putLong("DeathStart",deathStart);t.putBoolean("LootDropped",lootDropped);t.putInt("Choice",comboChoice);t.putDouble("LandX",landing.x);t.putDouble("LandY",landing.y);t.putDouble("LandZ",landing.z);}
    @Override public void readAdditionalSaveData(CompoundTag t){
        super.readAdditionalSaveData(t);bindEncounter(t.getString("EncounterSite"));comboChoice=t.getInt("Choice");lootDropped=t.getBoolean("LootDropped");deathStart=t.contains("DeathStart")?t.getLong("DeathStart"):-1;
        landing=new Vec3(t.getDouble("LandX"),t.getDouble("LandY"),t.getDouble("LandZ"));attack.load(t.getCompound("EliteAttack"),HeadlessGeneral::skill,level().getGameTime());
        if(!Double.isFinite(landing.lengthSqr())||landing.distanceToSqr(position())>32*32)attack.cancel();
        if(isDeadOrDying()){attack.cancel();entityData.set(SKILL,0);entityData.set(START,deathStart);entityData.set(PHASE,AttackState.IDLE.ordinal());deathTime=(int)Math.min(70,Math.max(0,level().getGameTime()-deathStart));}else sync();
    }
    public String visualAnimation(){return isDeadOrDying()?"death":switch(skillId()){case 301->"roar";case 302->"spin";case 303->"throw";default->hurtTime>0?"hurt":getDeltaMovement().horizontalDistanceSqr()>.001?"walk":"idle";};}
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar c){
        c.add(new AnimationController<HeadlessGeneral>(this,"body",0,state->{String clip=visualAnimation();var controller=state.getController();
            animationPartial=state.getPartialTick();if(animationStart!=skillStart()){animationStart=skillStart();controller.forceAnimationReset();}
            controller.setAnimation(clip.equals("idle")||clip.equals("walk")?RawAnimation.begin().thenLoop("animation."+ID+"."+clip):RawAnimation.begin().thenPlayAndHold("animation."+ID+"."+clip));
            return software.bernie.geckolib.core.object.PlayState.CONTINUE;}){
            @Override protected double adjustTick(double tick){boolean resetting=shouldResetTick;double local=super.adjustTick(tick);
                if(resetting||getAnimationState()!=AnimationController.State.RUNNING)return local;
                return skillStart()>=0&&(skillId()!=0||isDeadOrDying())?Math.max(0,level().getGameTime()-skillStart()+animationPartial):local;
            }
        });
    }
    @Override public AnimatableInstanceCache getAnimatableInstanceCache(){return cache;}
}
