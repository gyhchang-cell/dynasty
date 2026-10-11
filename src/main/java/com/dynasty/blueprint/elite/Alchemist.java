package com.dynasty.blueprint.elite;

import com.dynasty.blueprint.*;
import com.dynasty.blueprint.combat.*;
import net.minecraft.core.*;
import net.minecraft.nbt.*;
import net.minecraft.network.syncher.*;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.damagesource.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.ai.goal.target.*;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.*;
import net.minecraft.world.phys.*;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.*;
import software.bernie.geckolib.util.GeckoLibUtil;
import java.util.*;

/** Three distinct finite casts, native collisions and a counterable ten-second shell. */
public final class Alchemist extends Monster implements GeoEntity,Combatant {
    public static final String ID="yinyang_liandan_fangshi";
    public static final SkillDefinition HELIX=new SkillDefinition(381,"alchemist_helix",16,40,24,160,3,14,20,1,0,true,true,List.of(16));
    public static final SkillDefinition SEA=new SkillDefinition(382,"alchemist_fire_sea",24,1,36,240,0,8,360,1,0,true,true,List.of(24));
    public static final SkillDefinition PELLS=new SkillDefinition(383,"alchemist_mercury",22,1,32,300,0,12,360,1,0,true,true,List.of(22));
    private static final EntityDataAccessor<Integer> SKILL=SynchedEntityData.defineId(Alchemist.class,EntityDataSerializers.INT),PHASE=SynchedEntityData.defineId(Alchemist.class,EntityDataSerializers.INT);
    private static final EntityDataAccessor<Long> START=SynchedEntityData.defineId(Alchemist.class,EntityDataSerializers.LONG),SHELL=SynchedEntityData.defineId(Alchemist.class,EntityDataSerializers.LONG);
    private final TimedAttack attack=new TimedAttack();private final AnimatableInstanceCache cache=GeckoLibUtil.createInstanceCache(this);
    private final Map<UUID,Long> reflected=new HashMap<>();
    private long nextChoice,deathStart=-1,animationStart=Long.MIN_VALUE;private float partial;private boolean lootDropped;private String site="";private BlockPos home;
    public Alchemist(EntityType<? extends Alchemist> t,Level level){super(t,level);xpReward=28;}
    public TimedAttack attack(){return attack;}public int skillId(){return entityData.get(SKILL);}public long skillStart(){return entityData.get(START);}
    public AttackState phase(){return AttackState.values()[Math.max(0,Math.min(4,entityData.get(PHASE)))];}
    public boolean shellActive(){return level().getGameTime()<entityData.get(SHELL)&&isAlive();}
    public long shellUntil(){return entityData.get(SHELL);}
    public String encounterSite(){return site;}public void bindEncounter(String key){site=key.length()<=256?key:"";if(home==null&&!site.isEmpty())home=blockPosition().immutable();}
    public static SkillDefinition skill(int id){return switch(id){case 381->HELIX;case 382->SEA;case 383->PELLS;default->null;};}
    @Override public Faction faction(){return Faction.SPIRITS;}@Override public MobRole role(){return MobRole.RANGED;}
    @Override protected void defineSynchedData(){super.defineSynchedData();entityData.define(SKILL,0);entityData.define(PHASE,0);entityData.define(START,-1L);entityData.define(SHELL,-1L);}
    @Override protected void registerGoals(){goalSelector.addGoal(0,new FloatGoal(this));goalSelector.addGoal(8,new LookAtPlayerGoal(this,Player.class,18));targetSelector.addGoal(1,new HurtByTargetGoal(this));targetSelector.addGoal(2,new NearestAttackableTargetGoal<>(this,Player.class,true));}
    public boolean enemy(LivingEntity e){return e!=null&&e.isAlive()&&!e.isSpectator()&&!Combatant.allied(this,e)&&!(e instanceof Player p&&p.isCreative());}
    public boolean startSkill(int id,LivingEntity victim){
        var def=skill(id);if(level().isClientSide||!isAlive()||def==null||!enemy(victim)||!hasLineOfSight(victim)||distanceToSqr(victim)>def.maxRange()*def.maxRange()||distanceToSqr(victim)<def.minRange()*def.minRange())return false;
        var dir=victim.getEyePosition().subtract(getEyePosition()).normalize();if(dir.lengthSqr()<.001)dir=new Vec3(0,0,1);
        Vec3 origin=id==382?position():getEyePosition();
        if(!attack.tryStart(def,level().getGameTime(),origin,dir,victim.getUUID()))return false;
        navigation.stop();setDeltaMovement(0,getDeltaMovement().y,0);setYRot((float)Math.toDegrees(Math.atan2(-dir.x,dir.z)));setYHeadRot(getYRot());yBodyRot=getYRot();sync();BlueprintVisualEvent.start(this,def,origin,dir,victim.getId());playSound(SoundEvents.EVOKER_PREPARE_ATTACK,.7F,.6F);return true;
    }
    private void sync(){entityData.set(SKILL,attack.current()==null?0:attack.current().id());entityData.set(START,attack.started());entityData.set(PHASE,attack.state(level().getGameTime()).ordinal());}
    @Override protected void customServerAiStep(){super.customServerAiStep();combat();}
    @Override public void tick(){super.tick();if(!level().isClientSide&&isNoAi())combat();}
    private void combat(){
        if(!isAlive())return;long now=level().getGameTime();reflected.entrySet().removeIf(e->e.getValue()<=now);
        if(attack.current()!=null){navigation.stop();setDeltaMovement(0,getDeltaMovement().y,0);attack.advance(now,this::impact);}sync();
        if(isNoAi()||attack.state(now)!=AttackState.IDLE)return;var victim=getTarget();if(home!=null&&(blockPosition().distSqr(home)>32*32||victim!=null&&victim.blockPosition().distSqr(home)>32*32)){setTarget(null);navigation.moveTo(home.getX()+.5,home.getY(),home.getZ()+.5,.85);return;}if(!enemy(victim)){setTarget(null);return;}
        if(now>=nextChoice){nextChoice=now+12;for(int id:new int[]{383,382,381})if(startSkill(id,victim))return;}
        if(distanceToSqr(victim)>100)navigation.moveTo(victim,.85);else if(distanceToSqr(victim)<16){var back=position().subtract(victim.position()).multiply(1,0,1).normalize().scale(3);var at=position().add(back);if(level().hasChunkAt(BlockPos.containing(at))&&level().noCollision(this,getType().getDimensions().makeBoundingBox(at)))navigation.moveTo(at.x,at.y,at.z,.7);}
    }
    private Vec3 floorAt(Vec3 point){var p=BlockPos.containing(point);for(int dy=2;dy>=-8;dy--){var at=p.above(dy);if(!level().hasChunkAt(at))return null;if(level().getBlockState(at.below()).isFaceSturdy(level(),at.below(),Direction.UP)&&level().getBlockState(at).isAir()&&level().getFluidState(at).isEmpty())return Vec3.atBottomCenterOf(at).add(0,.03,0);}return null;}
    private void zone(ServerLevel world,Vec3 at,boolean fire){
        if(at==null)return;int count=world.getEntitiesOfClass(AlchemistZone.class,getBoundingBox().inflate(32),z->z.ownedBy(this)).size();if(count>=3)return;
        var cloud=EliteContent.ALCHEMIST_ZONE.get().create(world);if(cloud==null)return;cloud.setPos(at);cloud.launch(this,fire);world.addFreshEntity(cloud);
    }
    private void impact(int frame){
        if(!(level() instanceof ServerLevel world)||!isAlive()||attack.current()==null)return;
        if(attack.current()==HELIX){if(!world.getEntitiesOfClass(AlchemistOrb.class,getBoundingBox().inflate(32),o->o.ownedBy(this)).isEmpty())return;for(int side:new int[]{-1,1}){var orb=EliteContent.ALCHEMIST_ORB.get().create(world);orb.launch(this,attack.origin(),attack.direction(),side);world.addFreshEntity(orb);}}
        else if(attack.current()==SEA)zone(world,floorAt(attack.origin()),true);
        else if(attack.current()==PELLS){
            entityData.set(SHELL,world.getGameTime()+200);var victim=world.getEntity(attack.target());
            if(victim instanceof LivingEntity living&&enemy(living)&&world.getEntitiesOfClass(AlchemistOrb.class,getBoundingBox().inflate(32),o->o.ownedBy(this)).isEmpty()){
                var right=new Vec3(-attack.direction().z,0,attack.direction().x).normalize();
                for(int side:new int[]{-1,1}){var at=floorAt(living.position().add(right.scale(side*2)));if(at==null)continue;var pill=EliteContent.ALCHEMIST_ORB.get().create(world);if(pill!=null){pill.launchPill(this,getEyePosition(),at,side);world.addFreshEntity(pill);}}
            }
        }
    }
    public void releaseMercury(Vec3 contact){if(level() instanceof ServerLevel world&&isAlive())zone(world,floorAt(contact),false);}
    @Override public boolean hurt(DamageSource source,float amount){
        float before=getHealth();boolean result=super.hurt(source,amount);if(!result||level().isClientSide||!isAlive())return result;float accepted=before-getHealth();long now=level().getGameTime();
        if(accepted>=8&&attack.state(now)==AttackState.WINDUP){attack.stun(now,20);BlueprintVisualEvent.cancel(this);sync();}
        if(accepted>0&&shellActive()&&!source.is(DamageTypes.THORNS)&&source.getEntity() instanceof LivingEntity attacker&&enemy(attacker)&&distanceToSqr(attacker)<=32*32&&(reflected.containsKey(attacker.getUUID())||reflected.size()<16)&&now>=reflected.getOrDefault(attacker.getUUID(),0L)){reflected.put(attacker.getUUID(),now+20);attacker.hurt(damageSources().thorns(this),Math.min(4,accepted*.3F));}
        return result;
    }
    public void clearOwned(){if(level() instanceof ServerLevel world){world.getEntitiesOfClass(AlchemistOrb.class,getBoundingBox().inflate(48),o->o.ownedBy(this)).forEach(Entity::discard);world.getEntitiesOfClass(AlchemistZone.class,getBoundingBox().inflate(48),z->z.ownedBy(this)).forEach(Entity::discard);}}
    @Override public void die(DamageSource source){if(deathStart>=0)return;super.die(source);if(!isDeadOrDying())return;deathStart=level().getGameTime();attack.cancel();entityData.set(SHELL,-1L);clearOwned();navigation.stop();setTarget(null);BlueprintVisualEvent.cancel(this);EliteEncounters.memberDied(this);entityData.set(SKILL,0);entityData.set(START,deathStart);entityData.set(PHASE,0);BlueprintVisualEvent.death(this);}
    @Override protected void dropAllDeathLoot(DamageSource source){if(!lootDropped){lootDropped=true;super.dropAllDeathLoot(source);}}
    @Override protected void tickDeath(){deathTime++;if(!level().isClientSide){deathTime=(int)Math.min(80,Math.max(deathTime,level().getGameTime()-deathStart));if(deathTime>=80)remove(RemovalReason.KILLED);}}
    @Override public void addAdditionalSaveData(CompoundTag t){super.addAdditionalSaveData(t);t.put("EliteAttack",attack.save());t.putString("EncounterSite",site);if(home!=null)t.putLong("EncounterHome",home.asLong());t.putLong("ShellUntil",entityData.get(SHELL));t.putLong("DeathStart",deathStart);t.putBoolean("LootDropped",lootDropped);var list=new ListTag();reflected.entrySet().stream().limit(16).forEach(entry->{var item=new CompoundTag();item.putUUID("Attacker",entry.getKey());item.putLong("Until",entry.getValue());list.add(item);});t.put("Reflected",list);}
    @Override public void readAdditionalSaveData(CompoundTag t){super.readAdditionalSaveData(t);home=null;bindEncounter(t.getString("EncounterSite"));if(t.contains("EncounterHome")){var saved=BlockPos.of(t.getLong("EncounterHome"));if(saved.distSqr(blockPosition())<=64*64)home=saved;}long now=level().getGameTime();attack.load(t.getCompound("EliteAttack"),Alchemist::skill,now);entityData.set(SHELL,Math.min(now+200,t.getLong("ShellUntil")));deathStart=t.contains("DeathStart")?t.getLong("DeathStart"):-1;lootDropped=t.getBoolean("LootDropped");reflected.clear();var list=t.getList("Reflected",Tag.TAG_COMPOUND);for(int i=0;i<Math.min(16,list.size());i++){var item=list.getCompound(i);if(item.hasUUID("Attacker")&&item.getLong("Until")>now)reflected.put(item.getUUID("Attacker"),Math.min(now+20,item.getLong("Until")));}if(isDeadOrDying()){attack.cancel();entityData.set(SKILL,0);entityData.set(START,deathStart);entityData.set(PHASE,0);}else sync();}
    public String visualAnimation(){return isDeadOrDying()?"death":switch(skillId()){case 381->"helix";case 382->"sea";case 383->"pells";default->hurtTime>0?"hurt":getDeltaMovement().horizontalDistanceSqr()>.001?"walk":"idle";};}
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar c){c.add(new AnimationController<Alchemist>(this,"body",0,state->{partial=state.getPartialTick();var controller=state.getController();if(animationStart!=skillStart()){animationStart=skillStart();controller.forceAnimationReset();}String name=visualAnimation();controller.setAnimation(name.equals("idle")||name.equals("walk")?RawAnimation.begin().thenLoop("animation."+ID+"."+name):RawAnimation.begin().thenPlayAndHold("animation."+ID+"."+name));return software.bernie.geckolib.core.object.PlayState.CONTINUE;}){
        @Override protected double adjustTick(double tick){boolean reset=shouldResetTick;double local=super.adjustTick(tick);return !reset&&getAnimationState()==AnimationController.State.RUNNING&&skillStart()>=0&&(skillId()!=0||isDeadOrDying())?Math.max(0,level().getGameTime()-skillStart()+partial):local;}
    });}
    @Override public AnimatableInstanceCache getAnimatableInstanceCache(){return cache;}
}
