package com.dynasty.blueprint.elite;

import com.dynasty.blueprint.*;
import com.dynasty.blueprint.combat.*;
import net.minecraft.core.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.syncher.*;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.control.FlyingMoveControl;
import net.minecraft.world.entity.ai.navigation.FlyingPathNavigation;
import net.minecraft.world.entity.ai.goal.target.*;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.*;
import net.minecraft.world.phys.*;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.*;
import software.bernie.geckolib.util.GeckoLibUtil;
import java.util.List;

/** A raptor, not a winged human: two real talons draw a bow, bounded native flight and arrows. */
public final class GoldenEagle extends Monster implements GeoEntity,Combatant {
    public static final String ID="liefeng_jindiao_yushi";
    public static final SkillDefinition RAIN=new SkillDefinition(441,"eagle_rain",30,50,36,240,3,16,360,1,0,true,true,List.of(30));
    public static final SkillDefinition FAN=new SkillDefinition(442,"eagle_fan",12,20,40,240,0,16,180,.6F,0,true,true,List.of(12));
    public static final SkillDefinition DIVE=new SkillDefinition(443,"eagle_dive",16,16,100,300,3,12,360,1.5F,1.2,true,true,List.of(31));
    private static final EntityDataAccessor<Integer> SKILL=SynchedEntityData.defineId(GoldenEagle.class,EntityDataSerializers.INT),PHASE=SynchedEntityData.defineId(GoldenEagle.class,EntityDataSerializers.INT);
    private static final EntityDataAccessor<Long> START=SynchedEntityData.defineId(GoldenEagle.class,EntityDataSerializers.LONG);
    private static final EntityDataAccessor<BlockPos> LAND=SynchedEntityData.defineId(GoldenEagle.class,EntityDataSerializers.BLOCK_POS);
    private static final EntityDataAccessor<Float> LAND_X=SynchedEntityData.defineId(GoldenEagle.class,EntityDataSerializers.FLOAT),LAND_Z=SynchedEntityData.defineId(GoldenEagle.class,EntityDataSerializers.FLOAT);
    private final TimedAttack attack=new TimedAttack();
    private final AnimatableInstanceCache cache=GeckoLibUtil.createInstanceCache(this);
    private long lastCombatTick=-1,nextChoice,deathStart=-1,animationStart=Long.MIN_VALUE;
    private float partial;
    private String site="";
    private BlockPos home;
    private boolean lootDropped;
    public GoldenEagle(EntityType<? extends GoldenEagle> type,Level level){
        super(type,level);xpReward=32;setNoGravity(true);navigation=new FlyingPathNavigation(this,level);
        moveControl=new FlyingMoveControl(this,16,true){@Override public void tick(){
            if(!isAlive()||attack.current()!=null||attack.state(level().getGameTime())==AttackState.STUN){setYya(0);setZza(0);return;}super.tick();
        }};
    }
    public TimedAttack attack(){return attack;}
    public int skillId(){return entityData.get(SKILL);}
    public long skillStart(){return entityData.get(START);}
    public Vec3 landing(){return Vec3.atBottomCenterOf(entityData.get(LAND)).add(entityData.get(LAND_X),0,entityData.get(LAND_Z));}
    public AttackState phase(){return AttackState.values()[Math.max(0,Math.min(4,entityData.get(PHASE)))];}
    public String encounterSite(){return site;}
    public void bindEncounter(String key){site=key.length()<=256?key:"";if(home==null&&!site.isBlank())home=blockPosition().immutable();}
    public static SkillDefinition skill(int id){return switch(id){case 441->RAIN;case 442->FAN;case 443->DIVE;default->null;};}
    @Override public Faction faction(){return Faction.WOODLAND;}
    @Override public MobRole role(){return MobRole.BEAST;}
    @Override protected void defineSynchedData(){super.defineSynchedData();entityData.define(SKILL,0);entityData.define(PHASE,0);entityData.define(START,-1L);entityData.define(LAND,BlockPos.ZERO);entityData.define(LAND_X,0F);entityData.define(LAND_Z,0F);}
    @Override protected void registerGoals(){targetSelector.addGoal(1,new HurtByTargetGoal(this));targetSelector.addGoal(2,new NearestAttackableTargetGoal<>(this,Player.class,true));}
    public boolean enemy(LivingEntity e){return e!=null&&e.isAlive()&&!e.isSpectator()&&!Combatant.allied(this,e)&&!(e instanceof Player p&&p.isCreative());}
    public boolean loaded(AABB box){for(double x:new double[]{box.minX,box.maxX})for(double z:new double[]{box.minZ,box.maxZ})if(!level().hasChunkAt(BlockPos.containing(x,box.minY,z)))return false;return box.minY>=level().getMinBuildHeight()&&box.maxY<level().getMaxBuildHeight()&&level().getWorldBorder().isWithinBounds(box);}
    private Vec3 floor(Vec3 point,int above,int below){
        var base=BlockPos.containing(point);for(int dy=above;dy>=-below;dy--){var feet=base.above(dy);var at=new Vec3(point.x,feet.getY(),point.z);var box=getType().getDimensions().makeBoundingBox(at);
            if(!loaded(box))return null;if(level().getBlockState(feet.below()).isFaceSturdy(level(),feet.below(),Direction.UP)&&level().getFluidState(feet).isEmpty()&&level().noCollision(this,box))return at;
        }return null;
    }
    private void face(Vec3 direction){setYRot((float)Math.toDegrees(Math.atan2(-direction.x,direction.z)));setYHeadRot(getYRot());yBodyRot=getYRot();setXRot(0);}
    public boolean startSkill(int id,LivingEntity target){
        var def=skill(id);if(level().isClientSide||!isAlive()||def==null||!enemy(target)||!hasLineOfSight(target)||Math.abs(target.getY()-getY())>6)return false;
        double distance=target.position().subtract(position()).horizontalDistanceSqr();if(distance<def.minRange()*def.minRange()||distance>def.maxRange()*def.maxRange())return false;
        var mark=floor(target.position(),2,3);if(mark==null||home!=null&&mark.distanceToSqr(Vec3.atBottomCenterOf(home))>32*32)return false;
        var dir=mark.subtract(position()).multiply(1,0,1).normalize();if(dir.lengthSqr()<.001)dir=new Vec3(0,0,1);
        if(def==RAIN){var side=new Vec3(-dir.z,0,dir.x);mark=floor(mark.add(side.scale(-13/16D)),1,2);if(mark==null)return false;}
        if(!attack.tryStart(def,level().getGameTime(),position(),dir,target.getUUID()))return false;
        var block=BlockPos.containing(mark);entityData.set(LAND,block);entityData.set(LAND_X,(float)(mark.x-block.getX()-.5));entityData.set(LAND_Z,(float)(mark.z-block.getZ()-.5));
        face(dir);navigation.stop();setYya(0);setZza(0);setDeltaMovement(Vec3.ZERO);sync();BlueprintVisualEvent.start(this,def,landing(),dir,target.getId());return true;
    }
    private void sync(){entityData.set(SKILL,attack.current()==null?0:attack.current().id());entityData.set(START,attack.started());entityData.set(PHASE,attack.state(level().getGameTime()).ordinal());}
    @Override protected void customServerAiStep(){super.customServerAiStep();combat();}
    @Override public void tick(){super.tick();if(!level().isClientSide&&isNoAi())combat();}
    private boolean grounded(){return !isAlive()||phase()==AttackState.STUN||skillId()==443&&level().getGameTime()-skillStart()>=31;}
    @Override public void travel(Vec3 input){
        if(grounded()){setNoGravity(false);super.travel(input);return;}
        long age=level().getGameTime()-attack.started();if(!level().isClientSide&&attack.current()==DIVE&&age>=16&&age<=30){setDeltaMovement(Vec3.ZERO);return;}
        setNoGravity(true);moveRelative(.05F,input);var delta=getDeltaMovement();
        if(!level().isClientSide&&!loaded(getBoundingBox().expandTowards(delta))){setDeltaMovement(Vec3.ZERO);navigation.stop();return;}
        move(MoverType.SELF,delta);setDeltaMovement(getDeltaMovement().scale(.85));fallDistance=0;
    }
    @Override public boolean causeFallDamage(float distance,float multiplier,DamageSource source){return false;}
    private void stop(int ticks){attack.stun(level().getGameTime(),ticks);navigation.stop();setYya(0);setZza(0);setNoGravity(false);setDeltaMovement(0,Math.min(0,getDeltaMovement().y),0);clearArrows();BlueprintVisualEvent.cancel(this);sync();}
    private void combat(){
        if(!isAlive())return;long now=level().getGameTime();if(now==lastCombatTick)return;
        if(attack.current()!=null&&lastCombatTick>=0&&(now-lastCombatTick>1||now<lastCombatTick)){attack.cancel();clearArrows();BlueprintVisualEvent.cancel(this);}lastCombatTick=now;
        setNoGravity(!grounded());
        if(attack.current()!=null){navigation.stop();setYya(0);setZza(0);var def=attack.current();long age=now-attack.started();face(attack.direction());
            if(def==DIVE&&age>=16&&age<=31){double u=(age-15)/16D;var wanted=attack.origin().lerp(landing(),u);var delta=wanted.subtract(position());
                if(!loaded(getBoundingBox().expandTowards(delta))){stop(40);return;}move(MoverType.SELF,delta);setDeltaMovement(Vec3.ZERO);
                if(position().distanceToSqr(wanted)>.04){stop(40);return;}
            }else if(!grounded())setDeltaMovement(Vec3.ZERO);
            attack.advance(now,this::impact);
        }
        sync();if(isNoAi()||attack.state(now)!=AttackState.IDLE)return;var target=getTarget();
        if(home!=null&&(blockPosition().distSqr(home)>32*32||target!=null&&target.blockPosition().distSqr(home)>32*32)){setTarget(null);target=null;}
        if(enemy(target)&&now>=nextChoice){nextChoice=now+16;if(startSkill(441,target)||startSkill(442,target)||startSkill(443,target))return;}
        // Probe only nine loaded vertical cells; hover is four metres above actual ground.
        var desired=enemy(target)?target.position().add(attack.direction().scale(-6)):home!=null?Vec3.atBottomCenterOf(home):position();
        var ground=floor(new Vec3(desired.x,getY()-4,desired.z),2,6);if(ground==null){setDeltaMovement(Vec3.ZERO);navigation.stop();return;}
        var hover=ground.add(0,4,0);var box=getType().getDimensions().makeBoundingBox(hover);
        if(loaded(box)&&level().noCollision(this,box))navigation.moveTo(hover.x,hover.y,hover.z,.8);else navigation.stop();
    }
    /** Exported full-draw tip centre (13,10,-27+10), bow pivot(13,10,-12), -45deg. */
    public Vec3 bowMuzzle(){var f=attack.direction();var side=new Vec3(-f.z,0,f.x);double d=5/Math.sqrt(2);return position().add(side.scale(-13/16D)).add(f.scale((12+d)/16)).add(0,(10+d)/16,0);}
    public Vec3 wingMuzzle(int sign){var f=attack.direction();var side=new Vec3(-f.z,0,f.x);double a=Math.toRadians(10);double x=sign*(9+18*Math.cos(a)),y=23-18*Math.sin(a);return position().add(side.scale(-x/16)).add(f.scale(-3/16D)).add(0,y/16,0);}
    public int ownedArrowCount(){return level() instanceof ServerLevel world?world.getEntitiesOfClass(EagleArrow.class,getBoundingBox().inflate(48),e->e.ownedBy(this)).size():0;}
    public boolean launchArrow(int kind,Vec3 from,Vec3 velocity,Vec3 apex){
        if(!(level() instanceof ServerLevel world)||!isAlive()||ownedArrowCount()>=80)return false;
        var arrow=EliteContent.EAGLE_ARROW.get().create(world);if(arrow==null)return false;
        if(!loaded(arrow.getType().getDimensions().makeBoundingBox(from))||!world.noCollision(arrow,arrow.getType().getDimensions().makeBoundingBox(from)))return false;
        arrow.launch(this,kind,from,velocity,apex);return world.addFreshEntity(arrow);
    }
    private void impact(int frame){
        if(!(level() instanceof ServerLevel world)||attack.current()==null||!isAlive())return;var def=attack.current();
        if(def==RAIN){var from=bowMuzzle();double distance=Math.max(1,landing().subtract(from).dot(attack.direction()));var apex=from.add(attack.direction().scale(distance)).add(0,distance,0);launchArrow(EagleArrow.MARKER,from,apex.subtract(from).normalize().scale(.9),apex);return;}
        if(def==FAN){var f=attack.direction();var side=new Vec3(-f.z,0,f.x);
            for(int i=0;i<36&&isAlive()&&attack.current()==FAN;i++){double a=Math.toRadians(-90+i*180D/35);var d=f.scale(Math.cos(a)).add(side.scale(Math.sin(a)));var from=wingMuzzle(i<18?1:-1);
                double down=(landing().y-from.y)/Math.max(4,landing().subtract(position()).horizontalDistance());launchArrow(EagleArrow.FEATHER,from,new Vec3(d.x,down,d.z).normalize().scale(1.05),Vec3.ZERO);
            }return;
        }
        var feet=blockPosition();if(position().distanceToSqr(landing())>.25||!world.getBlockState(feet.below()).isFaceSturdy(world,feet.below(),Direction.UP)){stop(40);return;}
        setNoGravity(false);fallDistance=0;
        for(var victim:CombatGeometry.query(world,position(),attack.direction(),CombatGeometry.Shape.CIRCLE,2,0,360,3,this::enemy).stream().limit(16).toList()){
            if(!isAlive()||attack.current()!=DIVE)return;if(!hasLineOfSight(victim))continue;
            if(victim.hurt(damageSources().mobAttack(this),(float)getAttributeValue(Attributes.ATTACK_DAMAGE)*DIVE.damageMultiplier()))victim.knockback(DIVE.knockback(),getX()-victim.getX(),getZ()-victim.getZ());
        }
    }
    private void clearArrows(){if(level() instanceof ServerLevel world)for(var arrow:world.getEntitiesOfClass(EagleArrow.class,getBoundingBox().inflate(48),e->e.ownedBy(this)).stream().limit(80).toList())arrow.discard();}
    @Override public boolean hurt(DamageSource source,float amount){float before=getHealth();boolean accepted=super.hurt(source,amount);if(accepted&&!level().isClientSide&&isAlive()&&before-getHealth()>=8){long age=level().getGameTime()-attack.started();if(attack.current()==DIVE&&age>=29&&age<=31)stop(100);else if(phase()==AttackState.WINDUP)stop(30);}return accepted;}
    @Override public void die(DamageSource source){if(deathStart>=0)return;super.die(source);if(!isDeadOrDying())return;deathStart=level().getGameTime();attack.cancel();navigation.stop();setTarget(null);setNoGravity(false);setYya(0);setZza(0);clearArrows();BlueprintVisualEvent.cancel(this);EliteEncounters.memberDied(this);entityData.set(SKILL,0);entityData.set(START,deathStart);entityData.set(PHASE,0);BlueprintVisualEvent.death(this);}
    @Override protected void dropAllDeathLoot(DamageSource source){if(!lootDropped){lootDropped=true;super.dropAllDeathLoot(source);}}
    @Override protected void tickDeath(){deathTime++;if(!level().isClientSide){deathTime=(int)Math.min(90,Math.max(deathTime,level().getGameTime()-deathStart));if(deathTime>=90)remove(RemovalReason.KILLED);}}
    @Override public void addAdditionalSaveData(CompoundTag t){super.addAdditionalSaveData(t);t.put("EliteAttack",attack.save());t.putString("EncounterSite",site);if(home!=null)t.putLong("EncounterHome",home.asLong());t.putLong("Landing",entityData.get(LAND).asLong());t.putFloat("LandingX",entityData.get(LAND_X));t.putFloat("LandingZ",entityData.get(LAND_Z));t.putLong("LastCombatTick",lastCombatTick);t.putLong("DeathStart",deathStart);t.putBoolean("LootDropped",lootDropped);}
    @Override public void readAdditionalSaveData(CompoundTag t){
        super.readAdditionalSaveData(t);home=null;bindEncounter(t.getString("EncounterSite"));if(t.contains("EncounterHome")){var h=BlockPos.of(t.getLong("EncounterHome"));if(h.distSqr(blockPosition())<=64*64)home=h;}
        attack.load(t.getCompound("EliteAttack"),GoldenEagle::skill,level().getGameTime());var land=t.contains("Landing")?BlockPos.of(t.getLong("Landing")):blockPosition();float ox=t.getFloat("LandingX"),oz=t.getFloat("LandingZ");
        if(land.distSqr(blockPosition())<=24*24&&Float.isFinite(ox)&&Float.isFinite(oz)&&Math.abs(ox)<=.51&&Math.abs(oz)<=.51){entityData.set(LAND,land);entityData.set(LAND_X,ox);entityData.set(LAND_Z,oz);}else attack.cancel();
        lastCombatTick=t.contains("LastCombatTick")?t.getLong("LastCombatTick"):-1;deathStart=t.contains("DeathStart")?t.getLong("DeathStart"):-1;lootDropped=t.getBoolean("LootDropped");setNoGravity(!grounded());
        if(isDeadOrDying()){attack.cancel();entityData.set(SKILL,0);entityData.set(START,deathStart);entityData.set(PHASE,0);}else sync();
    }
    public String visualAnimation(){return isDeadOrDying()?"death":switch(skillId()){case 441->"rain";case 442->"fan";case 443->"dive";default->hurtTime>0?"hurt":getDeltaMovement().lengthSqr()>.001?"fly":"idle";};}
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar c){c.add(new AnimationController<GoldenEagle>(this,"body",0,state->{partial=state.getPartialTick();var controller=state.getController();if(animationStart!=skillStart()){animationStart=skillStart();controller.forceAnimationReset();}String name=visualAnimation();controller.setAnimation(name.equals("idle")||name.equals("fly")?RawAnimation.begin().thenLoop("animation."+ID+"."+name):RawAnimation.begin().thenPlayAndHold("animation."+ID+"."+name));return software.bernie.geckolib.core.object.PlayState.CONTINUE;}){
        @Override protected double adjustTick(double tick){boolean reset=shouldResetTick;double local=super.adjustTick(tick);return !reset&&getAnimationState()==AnimationController.State.RUNNING&&skillStart()>=0&&(skillId()!=0||isDeadOrDying())?Math.max(0,level().getGameTime()-skillStart()+partial):local;}
    });}
    @Override public AnimatableInstanceCache getAnimatableInstanceCache(){return cache;}
}
