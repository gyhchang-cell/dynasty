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
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.ai.goal.target.*;
import net.minecraft.world.entity.ai.navigation.*;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.*;
import net.minecraft.world.phys.*;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.*;
import software.bernie.geckolib.util.GeckoLibUtil;
import java.util.*;

/** Slow blockable beam, five independently warned cells, and two harmless finite decoys. */
public final class FoxMatron extends Monster implements GeoEntity,Combatant {
    public static final String ID="baimian_huxiangu";
    public static final double FIRE_RADIUS=1.25,BEAM_SPEED=.35;
    public static final SkillDefinition MIRROR=new SkillDefinition(351,"fox_mirror",20,32,24,140,0,12,0,.8F,0,true,true,List.of(20));
    public static final SkillDefinition FIRE=new SkillDefinition(352,"fox_fire",20,49,30,200,0,12,360,1,0,true,true,List.of(20,32,44,56,68));
    public static final SkillDefinition SPLIT=new SkillDefinition(353,"fox_split",6,1,24,300,0,12,360,0,0,true,true,List.of(6));
    private static final EntityDataAccessor<Integer> SKILL=SynchedEntityData.defineId(FoxMatron.class,EntityDataSerializers.INT),PHASE=SynchedEntityData.defineId(FoxMatron.class,EntityDataSerializers.INT);
    private static final EntityDataAccessor<Long> START=SynchedEntityData.defineId(FoxMatron.class,EntityDataSerializers.LONG);
    private static final EntityDataAccessor<Boolean> DECOY=SynchedEntityData.defineId(FoxMatron.class,EntityDataSerializers.BOOLEAN);
    private final TimedAttack attack=new TimedAttack();
    private final AnimatableInstanceCache cache=GeckoLibUtil.createInstanceCache(this);
    private boolean beamSpent,lootDropped;
    private UUID owner;
    private long expires,nextChoice,deathStart=-1,animationStart=Long.MIN_VALUE;
    private String site="";
    private float partial;
    public FoxMatron(EntityType<? extends FoxMatron> type,Level level){super(type,level);xpReward=24;setNoGravity(true);moveControl=new FlyingMoveControl(this,12,true);}
    @Override protected PathNavigation createNavigation(Level level){var n=new FlyingPathNavigation(this,level);n.setCanFloat(true);return n;}
    @Override protected void defineSynchedData(){super.defineSynchedData();entityData.define(SKILL,0);entityData.define(PHASE,0);entityData.define(START,-1L);entityData.define(DECOY,false);}
    @Override protected void registerGoals(){goalSelector.addGoal(8,new LookAtPlayerGoal(this,Player.class,16));targetSelector.addGoal(1,new HurtByTargetGoal(this));targetSelector.addGoal(2,new NearestAttackableTargetGoal<>(this,Player.class,true));}
    @Override public Faction faction(){return Faction.SPIRITS;}
    @Override public MobRole role(){return MobRole.RANGED;}
    public boolean isDecoy(){return entityData.get(DECOY);}
    public boolean ownedBy(FoxMatron matron){return owner!=null&&owner.equals(matron.getUUID());}
    public String encounterSite(){return site;}
    public void bindEncounter(String key){int at=key.indexOf('@'),suffix=at<0?-1:key.indexOf(':',at);site=suffix<0?key:key.substring(0,suffix);if(site.length()>256)site="";}
    public TimedAttack attack(){return attack;}
    public boolean beamConsumed(){return beamSpent;}
    public int skillId(){return entityData.get(SKILL);}
    public long skillStart(){return entityData.get(START);}
    public AttackState phase(){return AttackState.values()[Math.max(0,Math.min(4,entityData.get(PHASE)))];}
    public static SkillDefinition skill(int id){return switch(id){case 351->MIRROR;case 352->FIRE;case 353->SPLIT;default->null;};}
    private boolean enemy(LivingEntity e){return e!=null&&e.isAlive()&&!e.isSpectator()&&!Combatant.allied(this,e)&&!(e instanceof Player p&&p.isCreative());}
    public Vec3 firePoint(int index){return attack.origin().add(attack.direction().multiply(1,0,1).normalize().scale(Math.max(0,Math.min(4,index))*1.5));}
    public boolean startSkill(int id,LivingEntity victim){
        var def=skill(id);if(level().isClientSide||!isAlive()||isDecoy()||def==null||!enemy(victim)||distanceToSqr(victim)>144||!hasLineOfSight(victim))return false;
        Vec3 origin=position().add(0,1.3,0),dir=victim.getEyePosition().subtract(origin).normalize();
        if(def==FIRE){origin=victim.position().add(0,.03,0);dir=victim.getDeltaMovement().multiply(1,0,1);if(dir.lengthSqr()<.01)dir=victim.position().subtract(position()).multiply(1,0,1);dir=dir.normalize();}
        if(dir.lengthSqr()<.001)dir=new Vec3(0,0,1);
        if(!attack.tryStart(def,level().getGameTime(),origin,dir,victim.getUUID()))return false;
        beamSpent=false;navigation.stop();setDeltaMovement(Vec3.ZERO);setYRot((float)Math.toDegrees(Math.atan2(-dir.x,dir.z)));setYHeadRot(getYRot());yBodyRot=getYRot();sync();BlueprintVisualEvent.start(this,def,origin,dir,victim.getId());playSound(SoundEvents.FOX_AMBIENT,.8F,1.2F);return true;
    }
    private void sync(){entityData.set(SKILL,attack.current()==null?0:attack.current().id());entityData.set(START,attack.started());entityData.set(PHASE,attack.state(level().getGameTime()).ordinal());}
    @Override protected void customServerAiStep(){super.customServerAiStep();combat();}
    @Override public void tick(){super.tick();if(!level().isClientSide&&isNoAi())combat();}
    @Override public void travel(Vec3 input){if(isAlive()){moveRelative(.04F,input);move(MoverType.SELF,getDeltaMovement());setDeltaMovement(getDeltaMovement().scale(.85));}else super.travel(input);}
    private void combat(){
        if(!isAlive())return;long now=level().getGameTime();
        if(isDecoy()){var parent=owner==null?null:((ServerLevel)level()).getEntity(owner);if(now>=expires||!(parent instanceof FoxMatron real)||!real.isAlive()||real.isDecoy()||distanceToSqr(real)>32*32)discard();return;}
        if(attack.current()!=null){navigation.stop();setDeltaMovement(Vec3.ZERO);var def=attack.current();long age=now-attack.started();if(def==MIRROR&&age>=20&&age<52&&!beamSpent)beam((int)age-20);attack.advance(now,this::impact);sync();}
        if(isNoAi()||attack.state(now)!=AttackState.IDLE)return;var victim=getTarget();if(!enemy(victim)){setTarget(null);return;}
        if(now>=nextChoice){nextChoice=now+12;for(int id:new int[]{352,351})if(startSkill(id,victim))return;}
        var desired=victim.position().add(0,.5,0);if(level().hasChunkAt(BlockPos.containing(desired))&&level().noCollision(this,getType().getDimensions().makeBoundingBox(desired.x,desired.y,desired.z)))moveControl.setWantedPosition(desired.x,desired.y,desired.z,.6);
    }
    private void beam(int age){
        var world=(ServerLevel)level();var a=attack.origin().add(attack.direction().scale(age*BEAM_SPEED));var b=a.add(attack.direction().scale(BEAM_SPEED));
        var block=world.clip(new ClipContext(a,b,ClipContext.Block.COLLIDER,ClipContext.Fluid.NONE,this));if(block.getType()!=HitResult.Type.MISS){beamSpent=true;return;}
        for(var e:world.getEntitiesOfClass(LivingEntity.class,new AABB(a,b).inflate(.2),this::enemy))if(e.getBoundingBox().inflate(.15).clip(a,b).isPresent()||e.getBoundingBox().inflate(.15).contains(a)){
            beamSpent=true;if(e.hurt(damageSources().indirectMagic(this,this),(float)getAttributeValue(Attributes.ATTACK_DAMAGE)*.8F))e.addEffect(new MobEffectInstance(EliteContent.FOX_HAZE.get(),80),this);break;
        }
    }
    private void impact(int frame){
        if(!(level() instanceof ServerLevel world)||attack.current()==null||!isAlive())return;
        if(attack.current()==FIRE){var at=firePoint((frame-20)/12);var feet=BlockPos.containing(at);if(!world.hasChunkAt(feet)||!world.getBlockState(feet.below()).isFaceSturdy(world,feet.below(),Direction.UP)||!world.getBlockState(feet).getCollisionShape(world,feet).isEmpty())return;
            for(var e:CombatGeometry.query(world,at,new Vec3(0,0,1),CombatGeometry.Shape.CIRCLE,FIRE_RADIUS,0,360,3,this::enemy))if(world.clip(new ClipContext(at.add(0,2.5,0),e.getEyePosition(),ClipContext.Block.COLLIDER,ClipContext.Fluid.NONE,this)).getType()==HitResult.Type.MISS){e.hurt(damageSources().indirectMagic(this,this),(float)getAttributeValue(Attributes.ATTACK_DAMAGE));e.addEffect(new MobEffectInstance(MobEffects.POISON,40),this);if(!isAlive())return;}
        }else if(attack.current()==SPLIT){
            var clones=world.getEntitiesOfClass(FoxMatron.class,getBoundingBox().inflate(32),f->f.isAlive()&&f.ownedBy(this));int count=clones.size();
            Vec3 right=new Vec3(-attack.direction().z,0,attack.direction().x).normalize();
            for(int sign:new int[]{-1,1}){
                var at=position().add(right.scale(sign*2.5));var feet=BlockPos.containing(at);if(count>=2)break;
                if(!world.hasChunkAt(feet)||!world.noCollision(null,getType().getDimensions().makeBoundingBox(at.x,at.y,at.z))||world.clip(new ClipContext(position().add(0,.5,0),at.add(0,.5,0),ClipContext.Block.COLLIDER,ClipContext.Fluid.NONE,this)).getType()!=HitResult.Type.MISS)continue;
                var clone=getType().create(world);if(!(clone instanceof FoxMatron f))continue;f.owner=getUUID();f.expires=world.getGameTime()+120;f.entityData.set(DECOY,true);f.getAttribute(Attributes.MAX_HEALTH).setBaseValue(1);f.getAttribute(Attributes.ARMOR).setBaseValue(0);f.setHealth(1);f.xpReward=0;f.setNoAi(true);f.bindEncounter(site);f.moveTo(at.x,at.y,at.z,getYRot(),0);if(world.addFreshEntity(f))count++;
            }
            // The real actor remains the sole attacker and moves sideways only into loaded, clear space.
            for(int sign:new int[]{1,-1}){var at=position().add(right.scale(sign*3));var feet=BlockPos.containing(at);if(world.hasChunkAt(feet)&&world.noCollision(this,getType().getDimensions().makeBoundingBox(at.x,at.y,at.z))&&world.clip(new ClipContext(position().add(0,.5,0),at.add(0,.5,0),ClipContext.Block.COLLIDER,ClipContext.Fluid.NONE,this)).getType()==HitResult.Type.MISS){move(MoverType.SELF,right.scale(sign*3));break;}}
        }
    }
    @Override public boolean hurt(DamageSource source,float amount){float before=getHealth();boolean result=super.hurt(source,amount);if(result&&isAlive()&&!isDecoy()&&before-getHealth()>=12&&attack.ready(353,level().getGameTime())){var target=source.getEntity() instanceof LivingEntity e&&enemy(e)?e:getTarget();if(enemy(target)){attack.cancel();BlueprintVisualEvent.cancel(this);startSkill(353,target);}}return result;}
    @Override public void die(DamageSource source){if(deathStart>=0)return;super.die(source);if(!isDeadOrDying())return;deathStart=level().getGameTime();attack.cancel();navigation.stop();setTarget(null);BlueprintVisualEvent.cancel(this);if(!isDecoy()){if(level() instanceof ServerLevel world)for(var clone:world.getEntitiesOfClass(FoxMatron.class,getBoundingBox().inflate(32),f->f.ownedBy(this)))clone.discard();EliteEncounters.memberDied(this);}entityData.set(SKILL,0);entityData.set(START,deathStart);entityData.set(PHASE,0);}
    @Override protected void dropAllDeathLoot(DamageSource source){if(isDecoy()||lootDropped)return;lootDropped=true;super.dropAllDeathLoot(source);}
    @Override protected void tickDeath(){deathTime++;if(!level().isClientSide&&Math.max(deathTime,level().getGameTime()-deathStart)>=(isDecoy()?1:70))remove(RemovalReason.KILLED);}
    @Override public void addAdditionalSaveData(CompoundTag t){super.addAdditionalSaveData(t);t.put("EliteAttack",attack.save());t.putString("EncounterSite",site);t.putBoolean("FoxDecoy",isDecoy());if(owner!=null)t.putUUID("FoxOwner",owner);t.putLong("FoxExpires",expires);t.putBoolean("BeamSpent",beamSpent);t.putBoolean("LootDropped",lootDropped);t.putLong("DeathStart",deathStart);}
    @Override public void readAdditionalSaveData(CompoundTag t){super.readAdditionalSaveData(t);bindEncounter(t.getString("EncounterSite"));entityData.set(DECOY,t.getBoolean("FoxDecoy"));owner=t.hasUUID("FoxOwner")?t.getUUID("FoxOwner"):null;if(isDecoy())xpReward=0;expires=t.getLong("FoxExpires");beamSpent=t.getBoolean("BeamSpent");lootDropped=t.getBoolean("LootDropped");deathStart=t.contains("DeathStart")?t.getLong("DeathStart"):-1;attack.load(t.getCompound("EliteAttack"),FoxMatron::skill,level().getGameTime());if(isDeadOrDying()){attack.cancel();entityData.set(SKILL,0);entityData.set(START,deathStart);entityData.set(PHASE,0);}else sync();}
    public String visualAnimation(){return isDeadOrDying()?"death":switch(skillId()){case 351->"mirror";case 352->"fire";case 353->"split";default->hurtTime>0?"hurt":getDeltaMovement().lengthSqr()>.001?"walk":"idle";};}
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar controllers){controllers.add(new AnimationController<FoxMatron>(this,"body",0,state->{partial=state.getPartialTick();var c=state.getController();if(animationStart!=skillStart()){animationStart=skillStart();c.forceAnimationReset();}String name=visualAnimation();c.setAnimation(name.equals("idle")||name.equals("walk")?RawAnimation.begin().thenLoop("animation."+ID+"."+name):RawAnimation.begin().thenPlayAndHold("animation."+ID+"."+name));return software.bernie.geckolib.core.object.PlayState.CONTINUE;}){@Override protected double adjustTick(double tick){boolean reset=shouldResetTick;double local=super.adjustTick(tick);return !reset&&getAnimationState()==AnimationController.State.RUNNING&&skillStart()>=0&&(skillId()!=0||isDeadOrDying())?Math.max(0,level().getGameTime()-skillStart()+partial):local;}});}
    @Override public AnimatableInstanceCache getAnimatableInstanceCache(){return cache;}
}
