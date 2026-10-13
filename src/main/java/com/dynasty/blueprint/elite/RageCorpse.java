package com.dynasty.blueprint.elite;

import com.dynasty.blueprint.*;
import com.dynasty.blueprint.combat.*;
import net.minecraft.core.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.syncher.*;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.ai.goal.target.*;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.*;
import net.minecraftforge.event.ForgeEventFactory;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.*;
import software.bernie.geckolib.util.GeckoLibUtil;
import java.util.List;

/** A four-knuckle grave chassis. One server clock, physical flight, no forced chunks or chase warps. */
public final class RageCorpse extends Monster implements GeoEntity,Combatant {
    public static final String ID="banshan_jiazhou_shikuang";
    public static final SkillDefinition SPIN=new SkillDefinition(401,"corpse_spin",22,80,40,220,0,6,360,.8F,.35,true,true,List.of(22,32,42,52,62,72,82,92));
    public static final SkillDefinition LEAP=new SkillDefinition(402,"corpse_leap",14,20,50,240,3,8,360,1.4F,.75,true,true,List.of(33));
    public static final SkillDefinition BLOOD=new SkillDefinition(403,"corpse_blood",16,25,40,200,0,8,30,.7F,.8,true,true,List.of(16,26,36));
    private static final EntityDataAccessor<Integer> SKILL=SynchedEntityData.defineId(RageCorpse.class,EntityDataSerializers.INT),PHASE=SynchedEntityData.defineId(RageCorpse.class,EntityDataSerializers.INT);
    private static final EntityDataAccessor<Long> START=SynchedEntityData.defineId(RageCorpse.class,EntityDataSerializers.LONG);
    private static final EntityDataAccessor<BlockPos> LAND=SynchedEntityData.defineId(RageCorpse.class,EntityDataSerializers.BLOCK_POS);
    private static final EntityDataAccessor<Float> LAND_X=SynchedEntityData.defineId(RageCorpse.class,EntityDataSerializers.FLOAT),LAND_Z=SynchedEntityData.defineId(RageCorpse.class,EntityDataSerializers.FLOAT);
    private final TimedAttack attack=new TimedAttack();
    private final AnimatableInstanceCache cache=GeckoLibUtil.createInstanceCache(this);
    private long lastCombatTick=-1,nextChoice,deathStart=-1,animationStart=Long.MIN_VALUE;
    private float partial;
    private String site="";
    private BlockPos home;
    private boolean lootDropped;
    public RageCorpse(EntityType<? extends RageCorpse> type,Level level){super(type,level);xpReward=34;}
    public TimedAttack attack(){return attack;}
    public int skillId(){return entityData.get(SKILL);}
    public long skillStart(){return entityData.get(START);}
    public Vec3 landing(){return Vec3.atBottomCenterOf(entityData.get(LAND)).add(entityData.get(LAND_X),0,entityData.get(LAND_Z));}
    public AttackState phase(){return AttackState.values()[Math.max(0,Math.min(4,entityData.get(PHASE)))];}
    public String encounterSite(){return site;}
    public void bindEncounter(String key){site=key.length()<=256?key:"";if(home==null&&!site.isBlank())home=blockPosition().immutable();}
    public static SkillDefinition skill(int id){return switch(id){case 401->SPIN;case 402->LEAP;case 403->BLOOD;default->null;};}
    @Override public Faction faction(){return Faction.SPIRITS;}
    @Override public MobRole role(){return MobRole.BEAST;}
    @Override public MobType getMobType(){return MobType.UNDEAD;}
    @Override protected void defineSynchedData(){super.defineSynchedData();entityData.define(SKILL,0);entityData.define(PHASE,0);entityData.define(START,-1L);entityData.define(LAND,BlockPos.ZERO);entityData.define(LAND_X,0F);entityData.define(LAND_Z,0F);}
    @Override protected void registerGoals(){goalSelector.addGoal(0,new FloatGoal(this));goalSelector.addGoal(8,new LookAtPlayerGoal(this,Player.class,20));targetSelector.addGoal(1,new HurtByTargetGoal(this));targetSelector.addGoal(2,new NearestAttackableTargetGoal<>(this,Player.class,true));}
    public boolean enemy(LivingEntity e){return e!=null&&e.isAlive()&&!e.isSpectator()&&!Combatant.allied(this,e)&&!(e instanceof Player p&&p.isCreative());}
    private boolean loaded(AABB box){for(double x:new double[]{box.minX,box.maxX})for(double z:new double[]{box.minZ,box.maxZ})if(!level().hasChunkAt(BlockPos.containing(x,box.minY,z)))return false;return level().getWorldBorder().isWithinBounds(box);}
    private BlockPos leapFloor(Vec3 point){
        var base=BlockPos.containing(point);for(int dy=2;dy>=-3;dy--){var feet=base.above(dy);var box=getType().getDimensions().makeBoundingBox(new Vec3(point.x,feet.getY(),point.z));if(!loaded(box))return null;
            if(level().getFluidState(feet).isEmpty()&&level().getBlockState(feet.below()).isFaceSturdy(level(),feet.below(),Direction.UP)&&level().noCollision(this,box))return feet;
        }return null;
    }
    private void face(Vec3 direction){setYRot((float)Math.toDegrees(Math.atan2(-direction.x,direction.z)));setYHeadRot(getYRot());yBodyRot=getYRot();}
    public boolean startSkill(int id,LivingEntity target){
        var def=skill(id);if(level().isClientSide||!isAlive()||def==null||!enemy(target)||!hasLineOfSight(target)||Math.abs(target.getY()-getY())>3)return false;
        double distance=target.position().subtract(position()).horizontalDistanceSqr();if(distance<def.minRange()*def.minRange()||distance>def.maxRange()*def.maxRange())return false;
        var dir=target.position().subtract(position()).multiply(1,0,1).normalize();if(dir.lengthSqr()<.001)dir=new Vec3(0,0,1);
        var endpoint=position().add(dir.scale(8));var floor=id==402?leapFloor(endpoint):null;if(id==402&&(floor==null||home!=null&&floor.distSqr(home)>32*32))return false;
        if(!attack.tryStart(def,level().getGameTime(),position(),dir,target.getUUID()))return false;
        if(floor!=null){entityData.set(LAND,floor);entityData.set(LAND_X,(float)(endpoint.x-floor.getX()-.5));entityData.set(LAND_Z,(float)(endpoint.z-floor.getZ()-.5));}face(dir);navigation.stop();setDeltaMovement(0,getDeltaMovement().y,0);sync();BlueprintVisualEvent.start(this,def,id==402?landing():position(),dir,target.getId());return true;
    }
    private void sync(){entityData.set(SKILL,attack.current()==null?0:attack.current().id());entityData.set(START,attack.started());entityData.set(PHASE,attack.state(level().getGameTime()).ordinal());}
    @Override protected void customServerAiStep(){super.customServerAiStep();combat();}
    @Override public void tick(){super.tick();if(!level().isClientSide&&isNoAi())combat();}
    // During the bounded twenty-tick parabola, the server's clipped move is the only flight
    // integrator. NoGravity is never enabled, so cancellation/unload immediately restores travel.
    @Override public void travel(Vec3 input){long age=level().getGameTime()-attack.started();if(!level().isClientSide&&attack.current()==LEAP&&age>=14&&age<=33){setDeltaMovement(Vec3.ZERO);return;}super.travel(input);}
    private void stop(int ticks){attack.stun(level().getGameTime(),ticks);BlueprintVisualEvent.cancel(this);setDeltaMovement(0,getDeltaMovement().y,0);sync();}
    private void combat(){
        if(!isAlive())return;long now=level().getGameTime();if(now==lastCombatTick)return;
        if(attack.current()!=null&&lastCombatTick>=0&&(now-lastCombatTick>1||now<lastCombatTick)){attack.cancel();BlueprintVisualEvent.cancel(this);}lastCombatTick=now;
        if(attack.current()!=null){navigation.stop();setDeltaMovement(0,getDeltaMovement().y,0);var def=attack.current();long age=now-attack.started();face(attack.direction());
            if(def==SPIN&&age>=22&&age<102){var delta=attack.direction().scale(.03);if(!loaded(getBoundingBox().expandTowards(delta))){stop(40);return;}var before=position();move(MoverType.SELF,delta);if(position().distanceToSqr(before)<.0001||horizontalCollision){stop(40);return;}}
            if(def==LEAP&&age>=14&&age<=33){double u=(age-13)/20D;var wanted=attack.origin().lerp(landing(),u).add(0,8*u*(1-u),0);var delta=wanted.subtract(position());if(!loaded(getBoundingBox().expandTowards(delta))){stop(40);return;}move(MoverType.SELF,delta);setDeltaMovement(Vec3.ZERO);if(position().distanceToSqr(wanted)>.04&&age<33){stop(40);return;}}
            attack.advance(now,this::impact);
        }
        sync();if(isNoAi()||attack.state(now)!=AttackState.IDLE)return;var target=getTarget();if(home!=null&&(blockPosition().distSqr(home)>32*32||target!=null&&target.blockPosition().distSqr(home)>32*32)){setTarget(null);navigation.moveTo(home.getX()+.5,home.getY(),home.getZ()+.5,.7);return;}
        if(!enemy(target)){setTarget(null);return;}if(now>=nextChoice){nextChoice=now+16;double range=distanceToSqr(target);if(range>25&&startSkill(402,target)||range<25&&startSkill(401,target)||startSkill(403,target))return;}navigation.moveTo(target,.8);
    }
    private void impact(int frame){
        if(!(level() instanceof ServerLevel world)||attack.current()==null||!isAlive())return;var def=attack.current();
        if(def==LEAP){var feet=blockPosition();if(!world.getBlockState(feet.below()).isFaceSturdy(world,feet.below(),Direction.UP)||position().distanceToSqr(landing())>.25){stop(40);return;}crater(world,feet);}
        Vec3 origin=def==BLOOD?position().add(attack.direction().scale(1.2)).add(0,1.5,0):position();
        var targets=CombatGeometry.query(world,origin,attack.direction(),def==BLOOD?CombatGeometry.Shape.SECTOR:CombatGeometry.Shape.CIRCLE,def==BLOOD?8:3,0,def==BLOOD?30:360,def==BLOOD?1.2:2.5,this::enemy);
        for(var victim:targets.stream().limit(16).toList()){
            if(!isAlive()||attack.current()!=def)return;
            if(world.clip(new ClipContext(origin.add(0,def==BLOOD?0:.6,0),victim.getEyePosition(),ClipContext.Block.COLLIDER,ClipContext.Fluid.NONE,this)).getType()!=HitResult.Type.MISS)continue;
            if(victim.hurt(damageSources().mobAttack(this),(float)getAttributeValue(Attributes.ATTACK_DAMAGE)*def.damageMultiplier())){victim.knockback(def.knockback(),getX()-victim.getX(),getZ()-victim.getZ());if(def==BLOOD)victim.addEffect(new MobEffectInstance(EliteContent.RAGE_CORROSION.get(),100),this);}
        }
    }
    private void crater(ServerLevel world,BlockPos feet){
        if(!ForgeEventFactory.getMobGriefingEvent(world,this))return;
        // One shallow bounded impact. Containers, ores, custom palace blocks and protected
        // blocks are never part of this allowlist; normal Forge destruction vetoes still apply.
        for(int dx=-3;dx<=3;dx++)for(int dz=-3;dz<=3;dz++)if(dx*dx+dz*dz<=9){var pos=feet.offset(dx,-1,dz);if(!world.hasChunkAt(pos)||world.getBlockEntity(pos)!=null)continue;var state=world.getBlockState(pos);
            if((state.is(Blocks.STONE)||state.is(Blocks.DIRT)||state.is(Blocks.GRASS_BLOCK)||state.is(Blocks.POLISHED_DEEPSLATE)||state.is(Blocks.DEEPSLATE))&&ForgeEventFactory.onEntityDestroyBlock(this,pos,state))world.destroyBlock(pos,false,this);
        }
    }
    @Override public boolean hurt(DamageSource source,float amount){float before=getHealth();boolean accepted=super.hurt(source,amount);if(accepted&&!level().isClientSide&&isAlive()&&before-getHealth()>=12&&phase()==AttackState.WINDUP)stop(30);return accepted;}
    @Override public void die(DamageSource source){if(deathStart>=0)return;super.die(source);if(!isDeadOrDying())return;deathStart=level().getGameTime();attack.cancel();navigation.stop();setTarget(null);BlueprintVisualEvent.cancel(this);EliteEncounters.memberDied(this);entityData.set(SKILL,0);entityData.set(START,deathStart);entityData.set(PHASE,0);BlueprintVisualEvent.death(this);}
    @Override protected void dropAllDeathLoot(DamageSource source){if(!lootDropped){lootDropped=true;super.dropAllDeathLoot(source);}}
    @Override protected void tickDeath(){deathTime++;if(!level().isClientSide){deathTime=(int)Math.min(80,Math.max(deathTime,level().getGameTime()-deathStart));if(deathTime>=80)remove(RemovalReason.KILLED);}}
    @Override public void addAdditionalSaveData(CompoundTag t){super.addAdditionalSaveData(t);t.put("EliteAttack",attack.save());t.putString("EncounterSite",site);if(home!=null)t.putLong("EncounterHome",home.asLong());t.putLong("Landing",entityData.get(LAND).asLong());t.putFloat("LandingX",entityData.get(LAND_X));t.putFloat("LandingZ",entityData.get(LAND_Z));t.putLong("LastCombatTick",lastCombatTick);t.putLong("DeathStart",deathStart);t.putBoolean("LootDropped",lootDropped);}
    @Override public void readAdditionalSaveData(CompoundTag t){
        super.readAdditionalSaveData(t);home=null;bindEncounter(t.getString("EncounterSite"));
        if(t.contains("EncounterHome")){var saved=BlockPos.of(t.getLong("EncounterHome"));if(saved.distSqr(blockPosition())<=64*64)home=saved;}
        attack.load(t.getCompound("EliteAttack"),RageCorpse::skill,level().getGameTime());
        var land=t.contains("Landing")?BlockPos.of(t.getLong("Landing")):blockPosition();float ox=t.getFloat("LandingX"),oz=t.getFloat("LandingZ");
        if(land.distSqr(blockPosition())<=12*12&&Float.isFinite(ox)&&Float.isFinite(oz)&&Math.abs(ox)<=.51&&Math.abs(oz)<=.51){entityData.set(LAND,land);entityData.set(LAND_X,ox);entityData.set(LAND_Z,oz);}else if(attack.current()==LEAP)attack.cancel();
        lastCombatTick=t.contains("LastCombatTick")?t.getLong("LastCombatTick"):-1;deathStart=t.contains("DeathStart")?t.getLong("DeathStart"):-1;lootDropped=t.getBoolean("LootDropped");
        if(isDeadOrDying()){attack.cancel();entityData.set(SKILL,0);entityData.set(START,deathStart);entityData.set(PHASE,0);}else sync();
    }
    public String visualAnimation(){return isDeadOrDying()?"death":switch(skillId()){case 401->"spin";case 402->"leap";case 403->"blood";default->hurtTime>0?"hurt":getDeltaMovement().horizontalDistanceSqr()>.001?"walk":"idle";};}
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar c){c.add(new AnimationController<RageCorpse>(this,"body",0,state->{partial=state.getPartialTick();var controller=state.getController();if(animationStart!=skillStart()){animationStart=skillStart();controller.forceAnimationReset();}String name=visualAnimation();controller.setAnimation(name.equals("idle")||name.equals("walk")?RawAnimation.begin().thenLoop("animation."+ID+"."+name):RawAnimation.begin().thenPlayAndHold("animation."+ID+"."+name));return software.bernie.geckolib.core.object.PlayState.CONTINUE;}){
        @Override protected double adjustTick(double tick){boolean reset=shouldResetTick;double local=super.adjustTick(tick);return !reset&&getAnimationState()==AnimationController.State.RUNNING&&skillStart()>=0&&(skillId()!=0||isDeadOrDying())?Math.max(0,level().getGameTime()-skillStart()+partial):local;}
    });}
    @Override public AnimatableInstanceCache getAnimatableInstanceCache(){return cache;}
}
