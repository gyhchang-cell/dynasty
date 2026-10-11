package com.dynasty.blueprint.elite;

import com.dynasty.blueprint.*;
import com.dynasty.blueprint.combat.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.syncher.*;
import net.minecraft.resources.*;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.damagesource.*;
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

/** A fixed tomb guard. Ground rings, collision-stunned charge and one owner-bound returning hammer. */
public final class HammerGuardian extends Monster implements GeoEntity,Combatant {
    public static final String ID="juchui_jinjia_lishi";
    public static final double RING_HALF_WIDTH=.65,WHEEL_WIDTH=2.6,WHEEL_STEP=.12;
    public static final SkillDefinition SLAM=new SkillDefinition(361,"hammer_slam",28,33,36,180,0,6,360,1.2F,.6,false,true,List.of(28,44,60));
    public static final SkillDefinition WHEEL=new SkillDefinition(362,"hammer_wheel",18,49,40,180,2,9,0,.9F,.4,false,true,List.of(18,26,34,42,50,58));
    public static final SkillDefinition THROW=new SkillDefinition(363,"hammer_throw",36,48,30,200,5,HammerChain.RANGE,0,1.1F,.3,true,true,List.of(36));
    private static final EntityDataAccessor<Integer> SKILL=SynchedEntityData.defineId(HammerGuardian.class,EntityDataSerializers.INT),PHASE=SynchedEntityData.defineId(HammerGuardian.class,EntityDataSerializers.INT);
    private static final EntityDataAccessor<Long> START=SynchedEntityData.defineId(HammerGuardian.class,EntityDataSerializers.LONG);
    private final TimedAttack attack=new TimedAttack();
    private final AnimatableInstanceCache cache=GeckoLibUtil.createInstanceCache(this);
    private long nextChoice,deathStart=-1,animationStart=Long.MIN_VALUE;
    private float partial,throwStagger;
    private boolean lootDropped;
    private String site="";
    public HammerGuardian(EntityType<? extends HammerGuardian> type,Level level){super(type,level);xpReward=32;}
    public TimedAttack attack(){return attack;}
    public int skillId(){return entityData.get(SKILL);}
    public long skillStart(){return entityData.get(START);}
    public AttackState phase(){return AttackState.values()[Math.max(0,Math.min(4,entityData.get(PHASE)))];}
    public String encounterSite(){return site;}
    public void bindEncounter(String key){int at=key.indexOf('@'),suffix=at<0?-1:key.indexOf(':',at);site=suffix<0?key:key.substring(0,suffix);if(site.length()>256)site="";}
    public static SkillDefinition skill(int id){return switch(id){case 361->SLAM;case 362->WHEEL;case 363->THROW;default->null;};}
    @Override public Faction faction(){return Faction.DYNASTY_ARMY;}
    @Override public MobRole role(){return MobRole.MELEE;}
    @Override protected void defineSynchedData(){super.defineSynchedData();entityData.define(SKILL,0);entityData.define(PHASE,0);entityData.define(START,-1L);}
    @Override protected void registerGoals(){goalSelector.addGoal(0,new FloatGoal(this));goalSelector.addGoal(8,new LookAtPlayerGoal(this,Player.class,18));goalSelector.addGoal(9,new RandomLookAroundGoal(this));targetSelector.addGoal(1,new HurtByTargetGoal(this));targetSelector.addGoal(2,new NearestAttackableTargetGoal<>(this,Player.class,true));}
    public boolean enemy(LivingEntity e){return e!=null&&e.isAlive()&&!e.isSpectator()&&!Combatant.allied(this,e)&&!(e instanceof Player p&&p.isCreative());}
    public boolean startSkill(int id,LivingEntity victim){
        var def=skill(id);if(level().isClientSide||!isAlive()||def==null||!enemy(victim)||!hasLineOfSight(victim))return false;
        double distance=position().subtract(victim.position()).horizontalDistanceSqr();
        if(distance<def.minRange()*def.minRange()||distance>def.maxRange()*def.maxRange()||Math.abs(victim.getY()-getY())>3)return false;
        var dir=victim.position().subtract(position()).multiply(1,0,1).normalize();if(dir.lengthSqr()<.001)dir=getLookAngle().multiply(1,0,1).normalize();
        if(!attack.tryStart(def,level().getGameTime(),position(),dir,victim.getUUID()))return false;
        throwStagger=0;navigation.stop();setYRot((float)Math.toDegrees(Math.atan2(-dir.x,dir.z)));setYHeadRot(getYRot());yBodyRot=getYRot();sync();
        BlueprintVisualEvent.start(this,def,attack.origin(),dir,victim.getId());playSound(SoundEvents.IRON_GOLEM_STEP,1,.55F);return true;
    }
    private void sync(){entityData.set(SKILL,attack.current()==null?0:attack.current().id());entityData.set(START,attack.started());entityData.set(PHASE,attack.state(level().getGameTime()).ordinal());}
    @Override protected void customServerAiStep(){super.customServerAiStep();combat();}
    @Override public void tick(){super.tick();if(!level().isClientSide&&isNoAi())combat();}
    private void combat(){
        if(!isAlive())return;long now=level().getGameTime();
        if(attack.current()!=null){
            navigation.stop();var def=attack.current();long age=now-attack.started();
            setDeltaMovement(getDeltaMovement().multiply(.05,1,.05));
            if(def==WHEEL&&age>=WHEEL.windupTicks()&&age<WHEEL.windupTicks()+WHEEL.activeTicks()){
                var before=position();move(MoverType.SELF,attack.direction().scale(WHEEL_STEP));
                if(horizontalCollision||position().distanceToSqr(before)<WHEEL_STEP*WHEEL_STEP*.25){stun(60);return;}
            }
            attack.advance(now,this::impact);sync();
        }
        sync();
        if(isNoAi()||attack.state(now)!=AttackState.IDLE||now<nextChoice)return;nextChoice=now+10;
        var victim=getTarget();if(!enemy(victim)){setTarget(null);return;}
        int[] order=distanceToSqr(victim)>25?new int[]{363,362,361}:new int[]{361,362,363};
        for(int id:order)if(startSkill(id,victim))return;
        if(site.isBlank()||victim.position().distanceToSqr(blockPosition().getCenter())<28*28)navigation.moveTo(victim,.75);
    }
    private void impact(int frame){
        if(!(level() instanceof ServerLevel world)||attack.current()==null||!isAlive())return;
        var current=attack.current();
        if(current==SLAM){
            double radius=ringRadius(frame);int hits=0;
            for(var e:world.getEntitiesOfClass(LivingEntity.class,new AABB(attack.origin(),attack.origin()).inflate(radius+RING_HALF_WIDTH,1.1,radius+RING_HALF_WIDTH),this::enemy)){
                if(!ringContains(attack.origin(),radius,e.getBoundingBox())||!hasLineOfSight(e))continue;
                if(++hits>16)break;
                if(e.hurt(shockDamage(),(float)getAttributeValue(Attributes.ATTACK_DAMAGE)*SLAM.damageMultiplier()))e.knockback(SLAM.knockback(),getX()-e.getX(),getZ()-e.getZ());
                if(!isAlive()||attack.current()!=current)return;
            }
        }else if(current==WHEEL){
            for(var e:CombatGeometry.query(world,position(),attack.direction(),CombatGeometry.Shape.STRIP,2.1,WHEEL_WIDTH,0,2.8,this::enemy).stream().limit(16).toList()){
                if(hasLineOfSight(e)&&e.hurt(damageSources().mobAttack(this),(float)getAttributeValue(Attributes.ATTACK_DAMAGE)*WHEEL.damageMultiplier()))e.knockback(WHEEL.knockback(),-attack.direction().x,-attack.direction().z);
                if(!isAlive()||attack.current()!=current)return;
            }
        }else if(current==THROW){
            if(world.getEntitiesOfClass(HammerChain.class,getBoundingBox().inflate(32),e->e.ownedBy(this)).isEmpty()){
                var hammer=EliteContent.HAMMER_CHAIN.get().create(world);if(hammer!=null){hammer.launch(this,attack.direction());world.addFreshEntity(hammer);}
            }
        }
        playSound(SoundEvents.ANVIL_LAND,.9F,.5F);
    }
    public static double ringRadius(int frame){return frame<=28?2:frame<=44?4:6;}
    public static boolean ringContains(Vec3 origin,double radius,AABB box){
        // Jumping raises the feet above the shallow ground wave; a body overhead is safe.
        if(box.minY-origin.y>=.9||box.minY-origin.y<-.6)return false;
        double nearX=Math.max(box.minX,Math.min(origin.x,box.maxX))-origin.x,nearZ=Math.max(box.minZ,Math.min(origin.z,box.maxZ))-origin.z;
        double farX=Math.max(Math.abs(box.minX-origin.x),Math.abs(box.maxX-origin.x)),farZ=Math.max(Math.abs(box.minZ-origin.z),Math.abs(box.maxZ-origin.z));
        double inner=radius==2?0:radius-RING_HALF_WIDTH,outer=radius+RING_HALF_WIDTH;
        return nearX*nearX+nearZ*nearZ<=outer*outer&&farX*farX+farZ*farZ>=inner*inner;
    }
    public DamageSource shockDamage(){var key=ResourceKey.create(Registries.DAMAGE_TYPE,new ResourceLocation("dynasty","hammer_ground_wave"));return new DamageSource(level().registryAccess().registryOrThrow(Registries.DAMAGE_TYPE).getHolderOrThrow(key),this);}
    private void stun(int ticks){attack.stun(level().getGameTime(),ticks);navigation.stop();setDeltaMovement(0,getDeltaMovement().y,0);clearHammer();BlueprintVisualEvent.cancel(this);sync();playSound(SoundEvents.IRON_GOLEM_HURT,1,.5F);}
    @Override public void knockback(double strength,double x,double z){if(attack.current()==WHEEL&&(attack.state(level().getGameTime())==AttackState.WINDUP||attack.state(level().getGameTime())==AttackState.ACTIVE))return;super.knockback(strength,x,z);}
    @Override public boolean hurt(DamageSource source,float amount){float before=getHealth();boolean result=super.hurt(source,amount);if(result&&isAlive()&&attack.current()==THROW&&attack.state(level().getGameTime())==AttackState.WINDUP){throwStagger+=Math.max(0,before-getHealth());if(throwStagger>=10)stun(30);}return result;}
    private void clearHammer(){if(level() instanceof ServerLevel world)for(var e:world.getEntitiesOfClass(HammerChain.class,getBoundingBox().inflate(32),h->h.ownedBy(this)))e.discard();}
    @Override public void die(DamageSource source){if(deathStart>=0)return;super.die(source);if(!isDeadOrDying())return;deathStart=level().getGameTime();attack.cancel();clearHammer();navigation.stop();setTarget(null);BlueprintVisualEvent.cancel(this);EliteEncounters.memberDied(this);entityData.set(SKILL,0);entityData.set(START,deathStart);entityData.set(PHASE,0);}
    @Override protected void dropAllDeathLoot(DamageSource source){if(lootDropped)return;lootDropped=true;super.dropAllDeathLoot(source);}
    @Override protected void tickDeath(){deathTime++;if(!level().isClientSide){deathTime=(int)Math.min(70,Math.max(deathTime,level().getGameTime()-deathStart));if(deathTime>=70)remove(RemovalReason.KILLED);}}
    @Override public void addAdditionalSaveData(CompoundTag t){super.addAdditionalSaveData(t);t.put("EliteAttack",attack.save());t.putString("EncounterSite",site);t.putLong("DeathStart",deathStart);t.putBoolean("LootDropped",lootDropped);t.putFloat("ThrowStagger",throwStagger);}
    @Override public void readAdditionalSaveData(CompoundTag t){super.readAdditionalSaveData(t);bindEncounter(t.getString("EncounterSite"));deathStart=t.contains("DeathStart")?t.getLong("DeathStart"):-1;lootDropped=t.getBoolean("LootDropped");throwStagger=Math.max(0,Math.min(10,t.getFloat("ThrowStagger")));attack.load(t.getCompound("EliteAttack"),HammerGuardian::skill,level().getGameTime());if(isDeadOrDying()){attack.cancel();entityData.set(SKILL,0);entityData.set(START,deathStart);entityData.set(PHASE,0);}else sync();}
    public String visualAnimation(){return isDeadOrDying()?"death":switch(skillId()){case 361->"slam";case 362->"wheel";case 363->"throw";default->hurtTime>0||phase()==AttackState.STUN?"hurt":getDeltaMovement().horizontalDistanceSqr()>.001?"walk":"idle";};}
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar controllers){controllers.add(new AnimationController<HammerGuardian>(this,"body",0,state->{partial=state.getPartialTick();var controller=state.getController();if(animationStart!=skillStart()){animationStart=skillStart();controller.forceAnimationReset();}String name=visualAnimation();controller.setAnimation(name.equals("idle")||name.equals("walk")?RawAnimation.begin().thenLoop("animation."+ID+"."+name):RawAnimation.begin().thenPlayAndHold("animation."+ID+"."+name));return software.bernie.geckolib.core.object.PlayState.CONTINUE;}){
        @Override protected double adjustTick(double tick){boolean reset=shouldResetTick;double local=super.adjustTick(tick);return !reset&&getAnimationState()==AnimationController.State.RUNNING&&skillStart()>=0&&(skillId()!=0||isDeadOrDying())?Math.max(0,level().getGameTime()-skillStart()+partial):local;}
    });}
    @Override public AnimatableInstanceCache getAnimatableInstanceCache(){return cache;}
}
