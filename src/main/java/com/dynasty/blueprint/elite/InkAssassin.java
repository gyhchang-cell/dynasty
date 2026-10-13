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
import java.util.List;

/** Folded ink-ray construct. Ordinary collision, finite concealment and a breakable four-anchor field. */
public final class InkAssassin extends Monster implements GeoEntity,Combatant {
    public static final String ID="mojia_jueying_cike";
    public static final SkillDefinition STEALTH=new SkillDefinition(411,"ink_stealth",70,11,30,240,2,10,0,3,0,true,true,List.of(80));
    public static final SkillDefinition FIELD=new SkillDefinition(412,"ink_field",10,46,36,220,0,8,0,1,0,true,true,List.of(15,27,39,51));
    public static final SkillDefinition MIST=new SkillDefinition(413,"ink_mist",8,21,30,200,0,8,0,0,0,true,true,List.of(8));
    private static final EntityDataAccessor<Integer> SKILL=SynchedEntityData.defineId(InkAssassin.class,EntityDataSerializers.INT),PHASE=SynchedEntityData.defineId(InkAssassin.class,EntityDataSerializers.INT);
    private static final EntityDataAccessor<Long> START=SynchedEntityData.defineId(InkAssassin.class,EntityDataSerializers.LONG);
    private static final EntityDataAccessor<BlockPos> MARK=SynchedEntityData.defineId(InkAssassin.class,EntityDataSerializers.BLOCK_POS);
    private static final EntityDataAccessor<Float> MARK_X=SynchedEntityData.defineId(InkAssassin.class,EntityDataSerializers.FLOAT),MARK_Z=SynchedEntityData.defineId(InkAssassin.class,EntityDataSerializers.FLOAT);
    private final TimedAttack attack=new TimedAttack();
    private final AnimatableInstanceCache cache=GeckoLibUtil.createInstanceCache(this);
    private long lastCombatTick=-1,nextChoice,deathStart=-1,animationStart=Long.MIN_VALUE;
    private float partial;
    private String site="";
    private BlockPos home;
    private boolean lootDropped;
    public InkAssassin(EntityType<? extends InkAssassin> t,Level level){super(t,level);xpReward=28;}
    public TimedAttack attack(){return attack;}
    public int skillId(){return entityData.get(SKILL);}
    public long skillStart(){return entityData.get(START);}
    public Vec3 mark(){return Vec3.atBottomCenterOf(entityData.get(MARK)).add(entityData.get(MARK_X),0,entityData.get(MARK_Z));}
    private void mark(Vec3 at){var b=BlockPos.containing(at);entityData.set(MARK,b);entityData.set(MARK_X,(float)(at.x-b.getX()-.5));entityData.set(MARK_Z,(float)(at.z-b.getZ()-.5));}
    public AttackState phase(){return AttackState.values()[Math.max(0,Math.min(4,entityData.get(PHASE)))];}
    public boolean concealed(){long age=level().getGameTime()-skillStart();return skillId()==411&&age>=1&&age<80&&!isDeadOrDying();}
    public String encounterSite(){return site;}
    public void bindEncounter(String key){site=key.length()<=256?key:"";if(home==null&&!site.isBlank())home=blockPosition().immutable();}
    public static SkillDefinition skill(int id){return switch(id){case 411->STEALTH;case 412->FIELD;case 413->MIST;default->null;};}
    @Override public Faction faction(){return Faction.CONSTRUCT;}
    @Override public MobRole role(){return MobRole.MELEE;}
    @Override protected void defineSynchedData(){super.defineSynchedData();entityData.define(SKILL,0);entityData.define(PHASE,0);entityData.define(START,-1L);entityData.define(MARK,BlockPos.ZERO);entityData.define(MARK_X,0F);entityData.define(MARK_Z,0F);}
    @Override protected void registerGoals(){goalSelector.addGoal(0,new FloatGoal(this));goalSelector.addGoal(8,new LookAtPlayerGoal(this,Player.class,16));targetSelector.addGoal(1,new HurtByTargetGoal(this));targetSelector.addGoal(2,new NearestAttackableTargetGoal<>(this,Player.class,true));}
    public boolean enemy(LivingEntity e){return e!=null&&e.isAlive()&&!e.isSpectator()&&!Combatant.allied(this,e)&&!(e instanceof Player p&&p.isCreative());}
    private boolean loaded(AABB box){for(double x:new double[]{box.minX,box.maxX})for(double z:new double[]{box.minZ,box.maxZ})if(!level().hasChunkAt(BlockPos.containing(x,box.minY,z)))return false;return level().getWorldBorder().isWithinBounds(box);}
    private Vec3 floor(Vec3 at,EntityDimensions size){var b=BlockPos.containing(at);for(int dy=1;dy>=-2;dy--){var feet=b.above(dy);var p=new Vec3(at.x,feet.getY(),at.z);var box=size.makeBoundingBox(p);if(!loaded(box))return null;if(level().getFluidState(feet).isEmpty()&&level().getBlockState(feet.below()).isFaceSturdy(level(),feet.below(),Direction.UP)&&level().noCollision(this,box))return p;}return null;}
    private boolean clearRay(Vec3 a,Vec3 b){return level().clip(new ClipContext(a,b,ClipContext.Block.COLLIDER,ClipContext.Fluid.NONE,this)).getType()==HitResult.Type.MISS;}
    private void face(Vec3 d){setYRot((float)Math.toDegrees(Math.atan2(-d.x,d.z)));setYHeadRot(getYRot());yBodyRot=getYRot();}
    private LivingEntity victim(){var e=attack.target()==null?null:((ServerLevel)level()).getEntity(attack.target());return e instanceof LivingEntity v&&enemy(v)?v:null;}
    public Vec3 fieldCorner(int i){return mark().add((i==0||i==3)?-2:2,0,(i<2)?-2:2);}
    public void clearField(){if(level() instanceof ServerLevel w)for(var spike:w.getEntitiesOfClass(InkSpike.class,getBoundingBox().inflate(32),s->s.ownedBy(this)))spike.discard();}
    public void clearOwned(){clearField();if(level() instanceof ServerLevel w)for(var cloud:w.getEntitiesOfClass(InkCloud.class,getBoundingBox().inflate(32),c->c.ownedBy(this)))cloud.discard();}
    private void stop(int ticks){attack.stun(level().getGameTime(),ticks);setInvisible(false);clearField();navigation.stop();setDeltaMovement(0,getDeltaMovement().y,0);BlueprintVisualEvent.cancel(this);sync();}
    public void breakField(InkSpike spike){if(attack.current()==FIELD&&spike.ownedBy(this)&&spike.castStart()==attack.started())stop(30);}
    public boolean startSkill(int id,LivingEntity target){
        var def=skill(id);if(level().isClientSide||!isAlive()||def==null||!enemy(target)||!hasLineOfSight(target)||Math.abs(target.getY()-getY())>2)return false;
        double distance=target.position().subtract(position()).horizontalDistanceSqr();if(distance<def.minRange()*def.minRange()||distance>def.maxRange()*def.maxRange())return false;
        var dir=target.position().subtract(position()).multiply(1,0,1).normalize();if(dir.lengthSqr()<.001)dir=new Vec3(0,0,1);
        if(def==FIELD){var centre=floor(target.position(),getType().getDimensions());if(centre==null)return false;for(int x:new int[]{-2,2})for(int z:new int[]{-2,2}){var p=floor(centre.add(x,0,z),EliteContent.INK_SPIKE.get().getDimensions());if(p==null||Math.abs(p.y-centre.y)>.01||!clearRay(centre.add(0,.5,0),p.add(0,.5,0)))return false;}}
        if(!attack.tryStart(def,level().getGameTime(),position(),dir,target.getUUID()))return false;
        mark(def==FIELD?floor(target.position(),getType().getDimensions()):target.position());navigation.stop();setDeltaMovement(0,getDeltaMovement().y,0);face(dir);sync();
        if(def==FIELD){clearField();for(int i=0;i<4;i++){var spike=EliteContent.INK_SPIKE.get().create(level());if(spike==null){stop(30);return true;}var at=fieldCorner(i);spike.moveTo(at.x,at.y,at.z,0,0);spike.launch(this);if(!level().addFreshEntity(spike)){stop(30);return true;}}}
        if(def==STEALTH&&level() instanceof ServerLevel w)for(var mob:w.getEntitiesOfClass(Mob.class,getBoundingBox().inflate(16),m->m.getTarget()==this).stream().limit(16).toList())mob.setTarget(null);
        BlueprintVisualEvent.start(this,def,mark(),dir,target.getId());return true;
    }
    private void sync(){entityData.set(SKILL,attack.current()==null?0:attack.current().id());entityData.set(START,attack.started());entityData.set(PHASE,attack.state(level().getGameTime()).ordinal());}
    @Override protected void customServerAiStep(){super.customServerAiStep();combat();}
    @Override public void tick(){super.tick();if(!level().isClientSide&&isNoAi())combat();}
    private boolean blink(Vec3 at){if(at==null||at.distanceToSqr(position())>64||Math.abs(at.y-getY())>2||home!=null&&BlockPos.containing(at).distSqr(home)>32*32||!loaded(getBoundingBox().expandTowards(at.subtract(position()))))return false;var floor=floor(at,getType().getDimensions());if(floor==null||Math.abs(floor.y-at.y)>.01||!clearRay(position().add(0,.4,0),at.add(0,.4,0)))return false;teleportTo(at.x,at.y,at.z);return true;}
    private boolean step(Vec3 at){var delta=at.subtract(position());if(!loaded(getBoundingBox().expandTowards(delta))){stop(30);return false;}move(MoverType.SELF,delta);if(position().distanceToSqr(at)>.04){stop(30);return false;}return true;}
    private void combat(){
        if(!isAlive())return;long now=level().getGameTime();if(now==lastCombatTick)return;
        if(attack.current()!=null&&lastCombatTick>=0&&(now-lastCombatTick>1||now<lastCombatTick)){attack.cancel();clearField();setInvisible(false);BlueprintVisualEvent.cancel(this);}lastCombatTick=now;
        if(attack.current()!=null){var def=attack.current();long age=now-attack.started();var target=victim();
            if(target==null||home!=null&&target.blockPosition().distSqr(home)>32*32){stop(20);return;}
            if(def==STEALTH&&age<70){var look=target.getLookAngle().multiply(1,0,1).normalize();if(look.lengthSqr()<.01)look=attack.direction();var point=floor(target.position().subtract(look),getType().getDimensions());if(point!=null)mark(point);if(!isNoAi()&&loaded(getBoundingBox())&&position().distanceToSqr(target.position())>4)navigation.moveTo(mark().x,mark().y,mark().z,1);}
            else{navigation.stop();setDeltaMovement(0,getDeltaMovement().y,0);face(attack.direction());}
            setInvisible(def==STEALTH&&age>=1&&age<80);
            if(def==FIELD&&age>=10&&age<56){if(level().getEntitiesOfClass(InkSpike.class,getBoundingBox().inflate(32),s->s.ownedBy(this)&&s.castStart()==attack.started()).size()!=4){stop(30);return;}
                int segment=age<20?0:age<32?1:age<44?2:3,begin=10+segment*12;int[] starts={0,1,2,3},ends={2,3,0,1};
                if(age==begin&&!blink(fieldCorner(starts[segment]))){stop(30);return;}
                if(age>=begin){double u=(age-begin+1)/10D;var from=fieldCorner(starts[segment]);var to=fieldCorner(ends[segment]);face(to.subtract(from));if(!step(from.lerp(to,Math.min(1,u))))return;}
            }
            if(def==MIST&&age>=1&&age<=6&&!step(position().subtract(attack.direction().scale(.16))))return;
            attack.advance(now,this::impact);if(attack.current()==null){setInvisible(false);clearField();}
        }
        sync();if(isNoAi()||attack.state(now)!=AttackState.IDLE)return;var target=getTarget();if(home!=null&&(blockPosition().distSqr(home)>32*32||target!=null&&target.blockPosition().distSqr(home)>32*32)){setTarget(null);navigation.moveTo(home.getX()+.5,home.getY(),home.getZ()+.5,1);return;}
        if(!enemy(target)){setTarget(null);return;}if(now>=nextChoice){nextChoice=now+16;double d=distanceToSqr(target);if(d>16&&startSkill(411,target)||d<36&&startSkill(412,target)||startSkill(413,target))return;}navigation.moveTo(target,1);
    }
    private void impact(int frame){
        if(!(level() instanceof ServerLevel world)||attack.current()==null)return;var def=attack.current();var target=victim();if(target==null){stop(20);return;}
        if(def==STEALTH){setInvisible(false);if(!blink(mark())){stop(30);return;}face(target.position().subtract(position()));if(distanceToSqr(target)>4||!clearRay(position().add(0,.5,0),target.getEyePosition()))return;var offset=position().subtract(target.position()).multiply(1,0,1).normalize();boolean back=target.getLookAngle().multiply(1,0,1).normalize().dot(offset)<-.5;target.hurt(damageSources().mobAttack(this),(float)getAttributeValue(Attributes.ATTACK_DAMAGE)*(back?3:1));}
        else if(def==FIELD){for(var e:CombatGeometry.query(world,position(),getLookAngle(),CombatGeometry.Shape.CIRCLE,1.1,0,360,2,this::enemy).stream().limit(12).toList())if(clearRay(position().add(0,.4,0),e.getEyePosition())){e.hurt(damageSources().mobAttack(this),(float)getAttributeValue(Attributes.ATTACK_DAMAGE));if(!isAlive()||attack.current()!=def)return;}}
        else if(def==MIST){var clouds=world.getEntitiesOfClass(InkCloud.class,getBoundingBox().inflate(32),c->c.ownedBy(this));int count=clouds.size();var side=new Vec3(-attack.direction().z,0,attack.direction().x);for(int i=-1;i<=1&&count<3;i++){var at=floor(attack.origin().add(attack.direction().scale(2.5)).add(side.scale(i*2.2)),EntityDimensions.fixed(.1F,.1F));if(at==null||!clearRay(position().add(0,.5,0),at.add(0,.5,0)))continue;var cloud=EliteContent.INK_CLOUD.get().create(world);if(cloud!=null){cloud.moveTo(at.x,at.y,at.z,0,0);cloud.launch(this);if(world.addFreshEntity(cloud))count++;}}}
    }
    @Override public boolean hurt(DamageSource source,float amount){float before=getHealth();boolean accepted=super.hurt(source,amount);if(accepted&&!level().isClientSide&&isAlive()&&before-getHealth()>=6&&phase()==AttackState.WINDUP)stop(25);return accepted;}
    @Override public void die(DamageSource source){if(deathStart>=0)return;super.die(source);if(!isDeadOrDying())return;deathStart=level().getGameTime();attack.cancel();clearOwned();setInvisible(false);navigation.stop();setTarget(null);BlueprintVisualEvent.cancel(this);EliteEncounters.memberDied(this);entityData.set(SKILL,0);entityData.set(START,deathStart);entityData.set(PHASE,0);BlueprintVisualEvent.death(this);}
    @Override protected void dropAllDeathLoot(DamageSource source){if(!lootDropped){lootDropped=true;super.dropAllDeathLoot(source);}}
    @Override protected void tickDeath(){deathTime++;if(!level().isClientSide&&Math.max(deathTime,level().getGameTime()-deathStart)>=60)remove(RemovalReason.KILLED);}
    @Override public void addAdditionalSaveData(CompoundTag t){super.addAdditionalSaveData(t);t.put("EliteAttack",attack.save());t.putString("EncounterSite",site);if(home!=null)t.putLong("EncounterHome",home.asLong());t.putLong("InkMark",entityData.get(MARK).asLong());t.putFloat("InkMarkX",entityData.get(MARK_X));t.putFloat("InkMarkZ",entityData.get(MARK_Z));t.putLong("LastCombatTick",lastCombatTick);t.putLong("DeathStart",deathStart);t.putBoolean("LootDropped",lootDropped);}
    @Override public void readAdditionalSaveData(CompoundTag t){
        super.readAdditionalSaveData(t);home=null;bindEncounter(t.getString("EncounterSite"));if(t.contains("EncounterHome")){var p=BlockPos.of(t.getLong("EncounterHome"));if(p.distSqr(blockPosition())<=64*64)home=p;}
        attack.load(t.getCompound("EliteAttack"),InkAssassin::skill,level().getGameTime());var p=t.contains("InkMark")?BlockPos.of(t.getLong("InkMark")):blockPosition();float x=t.getFloat("InkMarkX"),z=t.getFloat("InkMarkZ");if(p.distSqr(blockPosition())<=16*16&&Float.isFinite(x)&&Float.isFinite(z)&&Math.abs(x)<=.51&&Math.abs(z)<=.51){entityData.set(MARK,p);entityData.set(MARK_X,x);entityData.set(MARK_Z,z);}else attack.cancel();lastCombatTick=t.contains("LastCombatTick")?t.getLong("LastCombatTick"):-1;deathStart=t.contains("DeathStart")?t.getLong("DeathStart"):-1;lootDropped=t.getBoolean("LootDropped");
        if(isDeadOrDying()){attack.cancel();setInvisible(false);entityData.set(SKILL,0);entityData.set(START,deathStart);entityData.set(PHASE,0);}else{sync();setInvisible(concealed());}
    }
    public String visualAnimation(){return isDeadOrDying()?"death":switch(skillId()){case 411->"stealth";case 412->"field";case 413->"mist";default->hurtTime>0?"hurt":getDeltaMovement().horizontalDistanceSqr()>.001?"walk":"idle";};}
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar c){c.add(new AnimationController<InkAssassin>(this,"body",0,state->{partial=state.getPartialTick();var controller=state.getController();if(animationStart!=skillStart()){animationStart=skillStart();controller.forceAnimationReset();}String name=visualAnimation();controller.setAnimation(name.equals("idle")||name.equals("walk")?RawAnimation.begin().thenLoop("animation."+ID+"."+name):RawAnimation.begin().thenPlayAndHold("animation."+ID+"."+name));return software.bernie.geckolib.core.object.PlayState.CONTINUE;}){
        @Override protected double adjustTick(double tick){boolean reset=shouldResetTick;double local=super.adjustTick(tick);return !reset&&getAnimationState()==AnimationController.State.RUNNING&&skillStart()>=0&&(skillId()!=0||isDeadOrDying())?Math.max(0,level().getGameTime()-skillStart()+partial):local;}
    });}
    @Override public AnimatableInstanceCache getAnimatableInstanceCache(){return cache;}
}
