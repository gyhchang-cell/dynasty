package com.dynasty.blueprint.boss;

import com.dynasty.blueprint.BlueprintVisualEvent;
import com.dynasty.blueprint.combat.*;
import com.dynasty.entity.DynastyBossBarSubscriptions;
import net.minecraft.core.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.syncher.*;
import net.minecraft.server.level.*;
import net.minecraft.world.BossEvent;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
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

/** A blind oath shrine on a skeletal horse, then a stalking iron gate. Catalog Boss2, never final. */
public final class BlindMarshal extends Monster implements GeoEntity,Combatant {
    public static final String ID="gongsun_wuwang";
    public static final SkillDefinition TRAMPLE=new SkillDefinition(511,"wuwang_trample",20,48,12,240,3,14,0,1.3F,1.2,true,true,List.of(67));
    public static final SkillDefinition SLASH=new SkillDefinition(512,"wuwang_slash",16,1,43,180,0,10,140,1.2F,.8,true,true,List.of(16));
    public static final SkillDefinition LISTEN=new SkillDefinition(513,"wuwang_listen",0,80,20,240,0,20,360,1.4F,.9,true,true,List.of());
    public static final SkillDefinition ARROWS=new SkillDefinition(514,"wuwang_arrows",24,1,55,260,0,20,360,.5F,0,true,true,List.of(24));
    public static final SkillDefinition ONSLAUGHT=new SkillDefinition(515,"wuwang_onslaught",16,56,16,260,2,10,140,1.2F,.7,true,true,List.of(16,24,32,40,48,56,64));
    public static final SkillDefinition STORM=new SkillDefinition(516,"wuwang_storm",24,104,32,400,0,20,360,1.3F,.8,true,true,List.of(24,40,64,88,112));
    public static final SkillDefinition FAST_SLASH=new SkillDefinition(517,"wuwang_slash",8,1,21,90,0,10,140,1.2F,.8,true,true,List.of(8));
    private static final EntityDataAccessor<Integer> FORM=SynchedEntityData.defineId(BlindMarshal.class,EntityDataSerializers.INT),SKILL=SynchedEntityData.defineId(BlindMarshal.class,EntityDataSerializers.INT),PHASE=SynchedEntityData.defineId(BlindMarshal.class,EntityDataSerializers.INT);
    private static final EntityDataAccessor<Long> START=SynchedEntityData.defineId(BlindMarshal.class,EntityDataSerializers.LONG),BORN=SynchedEntityData.defineId(BlindMarshal.class,EntityDataSerializers.LONG),SHIFT=SynchedEntityData.defineId(BlindMarshal.class,EntityDataSerializers.LONG);
    private static final EntityDataAccessor<BlockPos> ARENA=SynchedEntityData.defineId(BlindMarshal.class,EntityDataSerializers.BLOCK_POS),LOCK=SynchedEntityData.defineId(BlindMarshal.class,EntityDataSerializers.BLOCK_POS);
    private static final EntityDataAccessor<Boolean> BOUND=SynchedEntityData.defineId(BlindMarshal.class,EntityDataSerializers.BOOLEAN);
    private static final EntityDataAccessor<Long> CUE=SynchedEntityData.defineId(BlindMarshal.class,EntityDataSerializers.LONG);
    private final TimedAttack attack=new TimedAttack();
    private final AnimatableInstanceCache cache=GeckoLibUtil.createInstanceCache(this);
    private final ServerBossEvent bar=new ServerBossEvent(Component.translatable("entity.dynasty."+ID),BossEvent.BossBarColor.RED,BossEvent.BossBarOverlay.PROGRESS);
    private final DynastyBossBarSubscriptions subscriptions=new DynastyBossBarSubscriptions(this,bar);
    private long lastCombat=-1,deathStart=-1,nextChoice,animationStamp=Long.MIN_VALUE;
    private String animationKey="";
    private float partial;
    private boolean heardThisAction,lootDropped;
    private Vec3 orbitStart=Vec3.ZERO;
    private double orbitAngle;
    public BlindMarshal(EntityType<? extends BlindMarshal> type,Level level){super(type,level);xpReward=180;}
    public int form(){return entityData.get(FORM);}
    public int skillId(){return entityData.get(SKILL);}
    public long skillStart(){return entityData.get(START);}
    public long born(){return entityData.get(BORN);}
    public long shifted(){return entityData.get(SHIFT);}
    public long cue(){return entityData.get(CUE);}
    public BlockPos arenaCentre(){return entityData.get(BOUND)?entityData.get(ARENA):null;}
    public Vec3 lockedPoint(){return Vec3.atBottomCenterOf(entityData.get(LOCK));}
    public TimedAttack attack(){return attack;}
    public AttackState phase(){return AttackState.values()[Math.max(0,Math.min(4,entityData.get(PHASE)))];}
    public boolean intro(){return born()<0||level().getGameTime()-born()<180;}
    public boolean transition(){return shifted()>=0&&level().getGameTime()-shifted()<60;}
    public boolean stormActive(){long age=level().getGameTime()-skillStart();return isAlive()&&skillId()==516&&age>=24&&age<128;}
    public void bindArena(BlockPos at){entityData.set(ARENA,at.immutable());entityData.set(BOUND,true);entityData.set(BORN,level().getGameTime());entityData.set(LOCK,blockPosition());setPersistenceRequired();}
    public static SkillDefinition skill(int id){return switch(id){case 511->TRAMPLE;case 512->SLASH;case 513->LISTEN;case 514->ARROWS;case 515->ONSLAUGHT;case 516->STORM;case 517->FAST_SLASH;default->null;};}
    @Override public Faction faction(){return Faction.SPIRITS;}
    @Override public MobRole role(){return MobRole.BEAST;}
    @Override protected void defineSynchedData(){super.defineSynchedData();entityData.define(FORM,1);entityData.define(SKILL,0);entityData.define(PHASE,0);entityData.define(START,-1L);entityData.define(BORN,-1L);entityData.define(SHIFT,-1L);entityData.define(ARENA,BlockPos.ZERO);entityData.define(LOCK,BlockPos.ZERO);entityData.define(BOUND,false);entityData.define(CUE,-1L);}
    @Override protected void registerGoals(){targetSelector.addGoal(1,new HurtByTargetGoal(this));targetSelector.addGoal(2,new NearestAttackableTargetGoal<>(this,Player.class,true));}
    public boolean enemy(LivingEntity e){return e!=null&&e.isAlive()&&!e.isSpectator()&&!Combatant.allied(this,e)&&!(e instanceof Player p&&p.isCreative());}
    public boolean loaded(AABB b){if(!Double.isFinite(b.minX+b.maxX+b.minY+b.maxY+b.minZ+b.maxZ)||b.getXsize()>48||b.getZsize()>48||b.minY<level().getMinBuildHeight()||b.maxY>=level().getMaxBuildHeight()||!level().getWorldBorder().isWithinBounds(b))return false;for(int x=net.minecraft.util.Mth.floor(b.minX)>>4;x<=net.minecraft.util.Mth.floor(b.maxX)>>4;x++)for(int z=net.minecraft.util.Mth.floor(b.minZ)>>4;z<=net.minecraft.util.Mth.floor(b.maxZ)>>4;z++)if(!level().hasChunkAt(new BlockPos(x<<4,0,z<<4)))return false;return true;}
    public BlockPos floor(Vec3 at){var b=BlockPos.containing(at);for(int y=2;y>=-3;y--){var p=b.above(y);if(!loaded(new AABB(p).inflate(1)))return null;if(level().isEmptyBlock(p)&&level().getFluidState(p).isEmpty()&&level().getBlockState(p.below()).isFaceSturdy(level(),p.below(),Direction.UP))return p;}return null;}
    public boolean legalFloor(BlockPos at){if(at==null)return false;var b=getDimensions(getPose()).makeBoundingBox(at.getX()+.5,at.getY(),at.getZ()+.5);if(!loaded(b)||!level().noCollision(this,b)||arenaCentre()!=null&&at.distSqr(arenaCentre())>12*12)return false;for(int x=-2;x<=2;x++)for(int z=-2;z<=2;z++)if(!level().getBlockState(at.offset(x,-1,z)).isFaceSturdy(level(),at.offset(x,-1,z),Direction.UP)||!level().getFluidState(at.offset(x,0,z)).isEmpty())return false;return true;}
    private void face(Vec3 d){if(d.horizontalDistanceSqr()<.001)return;setYRot((float)Math.toDegrees(Math.atan2(-d.x,d.z)));setYHeadRot(getYRot());yBodyRot=getYRot();}
    public Vec3 fixedFacing(){if(!level().isClientSide)return attack.direction();double a=Math.toRadians(getYRot());return new Vec3(-Math.sin(a),0,Math.cos(a));}
    public double meleeRadius(){return skillId()==516?4:4.3;}
    public double meleeAngle(){return skillId()==516?120:140;}
    public Vec3 meleeOrigin(){return position().add(0,bladeTip().y-getY(),0);}
    public Vec3 bladeTip(){double a=Math.toRadians(form()==1?120:100);return position().add(fixedFacing().scale((18+50*Math.sin(a))/16)).add(0,((form()==1?43:27)+50*Math.cos(a))/16,0);}
    public boolean startSkill(int id,LivingEntity victim){var def=skill(id);if(level().isClientSide||!isAlive()||intro()||transition()||def==null||!enemy(victim)||!hasLineOfSight(victim)||Math.abs(victim.getY()-getY())>5||form()==1&&(id>=515)||form()==2&&(id==511||id==512))return false;double d=position().subtract(victim.position()).horizontalDistance();if(d<def.minRange()||d>def.maxRange())return false;var f=victim.position().subtract(position()).multiply(1,0,1).normalize();if(f.lengthSqr()<.001)f=new Vec3(0,0,1);var locked=floor(victim.position());if(locked==null||arenaCentre()!=null&&locked.distSqr(arenaCentre())>14*14)return false;if(def==TRAMPLE&&!legalFloor(locked))return false;
        if(!attack.tryStart(def,level().getGameTime(),position(),f,victim.getUUID()))return false;entityData.set(LOCK,locked);heardThisAction=false;entityData.set(CUE,-1L);var centre=arenaCentre()==null?attack.origin():Vec3.atBottomCenterOf(arenaCentre());var delta=attack.origin().subtract(centre);orbitAngle=delta.horizontalDistanceSqr()>.1?Math.atan2(delta.z,delta.x):Math.atan2(-f.z,-f.x);orbitStart=centre.add(Math.cos(orbitAngle)*9,0,Math.sin(orbitAngle)*9);face(f);navigation.stop();setDeltaMovement(0,getDeltaMovement().y,0);sync();BlueprintVisualEvent.start(this,def,lockedPoint(),f,victim.getId());return true;}
    private void sync(){entityData.set(SKILL,attack.current()==null?0:attack.current().id());entityData.set(START,attack.current()!=null?attack.started():deathStart>=0?deathStart:transition()?shifted():intro()?born():-1L);entityData.set(PHASE,attack.state(level().getGameTime()).ordinal());}
    public void parried(int ticks){if(isAlive()&&!intro()&&!transition())stop(Math.max(1,Math.min(40,ticks)));}
    private void stop(int ticks){attack.stun(level().getGameTime(),ticks);clearEffects();navigation.stop();BlueprintVisualEvent.cancel(this);sync();}
    @Override protected void customServerAiStep(){super.customServerAiStep();combat();}
    @Override public void tick(){super.tick();if(!level().isClientSide&&isNoAi())combat();}
    private void combat(){if(!isAlive())return;long now=level().getGameTime();if(now==lastCombat)return;if(born()<0)entityData.set(BORN,now);if(lastCombat>=0&&(now<lastCombat||now-lastCombat>1)&&attack.current()!=null){attack.cancel();clearEffects();BlueprintVisualEvent.cancel(this);}lastCombat=now;
        if(intro()){navigation.stop();setDeltaMovement(0,getDeltaMovement().y,0);sync();return;}
        if(form()==1&&getHealth()<=getMaxHealth()*.5F){attack.cancel();clearEffects();BlueprintVisualEvent.cancel(this);entityData.set(FORM,2);entityData.set(SHIFT,now);getAttribute(Attributes.MOVEMENT_SPEED).setBaseValue(.22);navigation.stop();}
        bar.setProgress(Math.max(0,getHealth()/getMaxHealth()));subscriptions.tick();if(transition()){navigation.stop();setDeltaMovement(0,getDeltaMovement().y,0);sync();return;}
        if(attack.current()!=null){navigation.stop();if(!(attack.current()==LISTEN&&heardThisAction)&&!(attack.current()==STORM&&cue()>=attack.started()&&now-cue()<20))face(attack.direction());long age=now-attack.started();
            if(attack.current()==TRAMPLE&&age>=20&&age<68){var centre=arenaCentre()==null?attack.origin():Vec3.atBottomCenterOf(arenaCentre());Vec3 wanted;
                if(age<36)wanted=attack.origin().lerp(orbitStart,(age-19)/16D);
                else if(age<56){double a=orbitAngle+(age-35)*Math.PI/40;wanted=centre.add(Math.cos(a)*9,0,Math.sin(a)*9);}
                else {var edge=centre.add(Math.cos(orbitAngle+Math.PI/2)*9,0,Math.sin(orbitAngle+Math.PI/2)*9);wanted=edge.lerp(lockedPoint(),(age-55)/12D);}
                var floor=floor(wanted);if(floor==null||!legalFloor(floor)||Math.abs(floor.getY()-attack.origin().y)>.1){stop(40);return;}var delta=wanted.subtract(position());if(delta.lengthSqr()>1.7*1.7||!clippedMove(delta)){stop(40);return;}face(delta);
            }else if(attack.current()==ONSLAUGHT&&age>=16&&age<=64&&(age-16)%8==0){var floor=floor(position().add(attack.direction().scale(.75)));if(floor==null||!legalFloor(floor)||Math.abs(floor.getY()-getY())>.1||!clippedMove(attack.direction().scale(.75))){stop(40);return;}}
            else setDeltaMovement(0,getDeltaMovement().y,0);
            if(attack.current()==LISTEN&&age<80&&!heardThisAction)listen(now);
            if(attack.current()!=null)attack.advance(now,this::impact);
        }
        sync();if(isNoAi()||attack.state(now)!=AttackState.IDLE)return;var victim=getTarget();var arena=arenaCentre();if(arena!=null&&(blockPosition().distSqr(arena)>13*13||victim!=null&&victim.blockPosition().distSqr(arena)>15*15)){setTarget(null);navigation.moveTo(arena.getX()+.5,arena.getY(),arena.getZ()+.5,.7);return;}if(!enemy(victim)){setTarget(null);return;}
        if(now>=nextChoice){nextChoice=now+20;int[] ids=form()==1?new int[]{511,512,513,514}:new int[]{515,517,513,514,516};for(int i=0;i<ids.length;i++)if(startSkill(ids[(i+Math.floorMod(tickCount/20,ids.length))%ids.length],victim))return;}navigation.moveTo(victim,.8);
    }
    private boolean clippedMove(Vec3 delta){var previous=position();move(MoverType.SELF,delta);setDeltaMovement(0,0,0);return position().distanceToSqr(previous.add(delta))<.02;}
    public List<MarshalProjectile> effects(){return level() instanceof ServerLevel w?w.getEntitiesOfClass(MarshalProjectile.class,getBoundingBox().inflate(32),e->e.ownedBy(this)):List.of();}
    private void clearEffects(){for(var e:effects().stream().limit(32).toList())e.discard();}
    private boolean hit(LivingEntity e,float multiplier,double knock){if(!isAlive()||!enemy(e)||!hasLineOfSight(e))return false;if(!e.hurt(damageSources().mobAttack(this),(float)getAttributeValue(Attributes.ATTACK_DAMAGE)*multiplier))return false;if(knock>0)e.knockback(knock,getX()-e.getX(),getZ()-e.getZ());return true;}
    public MarshalProjectile launch(int kind,Vec3 from,Vec3 velocity){if(!(level() instanceof ServerLevel w)||!isAlive()||effects().size()>=32||!loaded(new AABB(from,from).expandTowards(velocity).inflate(.5)))return null;var e=BlindMarshalContent.PROJECTILE.get().create(w);if(e!=null){e.launch(this,kind,from,velocity);if(w.addFreshEntity(e))return e;}return null;}
    private void impact(int tick){if(!(level() instanceof ServerLevel w)||!isAlive()||attack.current()==null)return;var def=attack.current();
        if(def==TRAMPLE){for(var e:CombatGeometry.query(w,position(),attack.direction(),CombatGeometry.Shape.CIRCLE,3,0,360,2,this::enemy).stream().limit(16).toList())if(hit(e,def.damageMultiplier(),def.knockback()))e.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN,24,4));return;}
        if(def==SLASH||def==FAST_SLASH||def==ONSLAUGHT){var port=bladeTip();var hitIds=new HashSet<UUID>();for(var victim:CombatGeometry.query(w,meleeOrigin(),attack.direction(),CombatGeometry.Shape.SECTOR,meleeRadius(),0,meleeAngle(),1.1,this::enemy).stream().limit(16).toList())if(hit(victim,def.damageMultiplier(),def.knockback()))hitIds.add(victim.getUUID());var blade=launch(MarshalProjectile.SAND_BLADE,port,attack.direction().scale(.5));if(blade!=null)blade.ignoreHits(hitIds);if(def==ONSLAUGHT){var floor=floor(port);if(floor!=null)launch(MarshalProjectile.BLOOD_FISSURE,Vec3.atBottomCenterOf(floor).add(0,.1,0),Vec3.ZERO);}return;}
        if(def==ARROWS){var centre=arenaCentre()==null?position():Vec3.atBottomCenterOf(arenaCentre());for(int i=0;i<24&&isAlive();i++){double a=(i%8)*Math.PI/4;var from=centre.add(Math.cos(a)*12,14,Math.sin(a)*12);double spread=(i/8-1)*2.5;var aim=lockedPoint().add(Math.cos(a+Math.PI/2)*spread,1,Math.sin(a+Math.PI/2)*spread);launch(MarshalProjectile.WALL_ARROW,from,aim.subtract(from).normalize().scale(.9));}return;}
        if(def==STORM){if(tick==24){setHealth(Math.max(1,getHealth()-getMaxHealth()*.025F));return;}var target=attack.target()==null?null:w.getEntity(attack.target());if(!(target instanceof LivingEntity victim)||!enemy(victim)||!hasLineOfSight(victim))return;var landing=teleportNear(victim);if(landing!=null){teleportTo(landing.getX()+.5,landing.getY(),landing.getZ()+.5);var f=victim.position().subtract(position()).multiply(1,0,1).normalize();face(f);entityData.set(CUE,w.getGameTime());for(var e:CombatGeometry.query(w,meleeOrigin(),f,CombatGeometry.Shape.SECTOR,meleeRadius(),0,meleeAngle(),1.1,this::enemy).stream().limit(16).toList())hit(e,def.damageMultiplier(),def.knockback());}}
    }
    private BlockPos teleportNear(LivingEntity victim){for(int i=0;i<8;i++){double a=(i+Math.floorMod(tickCount,8))*Math.PI/4;var p=floor(victim.position().add(Math.cos(a)*3.5,0,Math.sin(a)*3.5));if(p!=null&&legalFloor(p)&&Math.abs(p.getY()-getY())<=1)return p;}return null;}
    private void listen(long now){if(!(level() instanceof ServerLevel w))return;for(var p:w.players().stream().filter(this::enemy).filter(p->distanceToSqr(p)<=20*20).limit(16).toList()){
        long cue=BlindMarshalNoise.heard(p);if(cue<attack.started()||cue>now||now-cue>8||!hasLineOfSight(p))continue;var at=teleportNear(p);if(at==null)continue;heardThisAction=true;entityData.set(CUE,now);teleportTo(at.getX()+.5,at.getY(),at.getZ()+.5);var f=p.position().subtract(position()).multiply(1,0,1).normalize();face(f);hit(p,LISTEN.damageMultiplier(),LISTEN.knockback());break;
    }}
    @Override public boolean hurt(DamageSource source,float amount){if(!level().isClientSide&&(intro()||transition())&&!source.is(net.minecraft.tags.DamageTypeTags.BYPASSES_INVULNERABILITY))return false;float before=getHealth();boolean accepted=super.hurt(source,amount);if(accepted&&!level().isClientSide&&isAlive()&&before-getHealth()>=30&&phase()==AttackState.WINDUP)stop(40);return accepted;}
    @Override public void startSeenByPlayer(ServerPlayer p){super.startSeenByPlayer(p);subscriptions.startSeenByPlayer(p);}
    @Override public void stopSeenByPlayer(ServerPlayer p){super.stopSeenByPlayer(p);subscriptions.stopSeenByPlayer(p);}
    @Override public void remove(RemovalReason reason){subscriptions.clear();if(!level().isClientSide&&isAlive()&&reason.shouldDestroy()){clearEffects();MarshalCourtyards.destroyed(this);}super.remove(reason);}
    @Override public void die(DamageSource source){if(deathStart>=0)return;super.die(source);if(!isDeadOrDying())return;deathStart=level().getGameTime();attack.cancel();clearEffects();navigation.stop();setTarget(null);subscriptions.clear();BlueprintVisualEvent.cancel(this);sync();MarshalCourtyards.confirmedDeath(this);}
    @Override protected void dropAllDeathLoot(DamageSource source){if(!lootDropped){lootDropped=true;super.dropAllDeathLoot(source);}}
    @Override protected void tickDeath(){deathTime++;if(!level().isClientSide&&deathTime>=240)remove(RemovalReason.KILLED);}
    @Override public void addAdditionalSaveData(CompoundTag t){super.addAdditionalSaveData(t);t.put("MarshalAttack",attack.save());t.putInt("MarshalForm",form());t.putLong("MarshalBorn",born());t.putLong("MarshalShift",shifted());t.putLong("MarshalDeath",deathStart);t.putLong("MarshalLastTick",lastCombat);t.putLong("MarshalLocked",entityData.get(LOCK).asLong());t.putBoolean("MarshalHeard",heardThisAction);t.putLong("MarshalCue",cue());t.putBoolean("MarshalLootDropped",lootDropped);t.putDouble("MarshalOrbitAngle",orbitAngle);if(arenaCentre()!=null)t.putLong("MarshalArena",arenaCentre().asLong());}
    @Override public void readAdditionalSaveData(CompoundTag t){super.readAdditionalSaveData(t);long now=level().getGameTime();entityData.set(FORM,t.getInt("MarshalForm")==2?2:1);entityData.set(BORN,t.contains("MarshalBorn")?Math.min(now,t.getLong("MarshalBorn")):now);long shifted=t.contains("MarshalShift")?t.getLong("MarshalShift"):-1;entityData.set(SHIFT,form()==2&&shifted>=0&&shifted<=now?shifted:-1);var arena=t.contains("MarshalArena")?BlockPos.of(t.getLong("MarshalArena")):null;if(arena!=null&&arena.distSqr(blockPosition())>64*64)arena=null;entityData.set(BOUND,arena!=null);entityData.set(ARENA,arena==null?BlockPos.ZERO:arena);entityData.set(LOCK,t.contains("MarshalLocked")?BlockPos.of(t.getLong("MarshalLocked")):blockPosition());lastCombat=t.contains("MarshalLastTick")?t.getLong("MarshalLastTick"):-1;deathStart=t.contains("MarshalDeath")?t.getLong("MarshalDeath"):-1;heardThisAction=t.getBoolean("MarshalHeard");long cue=t.contains("MarshalCue")?t.getLong("MarshalCue"):-1;entityData.set(CUE,cue>=0&&cue<=now?cue:-1);lootDropped=t.getBoolean("MarshalLootDropped");attack.load(t.getCompound("MarshalAttack"),BlindMarshal::skill,now);orbitAngle=t.getDouble("MarshalOrbitAngle");if(!Double.isFinite(orbitAngle)||lockedPoint().distanceToSqr(position())>32*32){orbitAngle=0;attack.cancel();}var centre=arena==null?attack.origin():Vec3.atBottomCenterOf(arena);orbitStart=centre.add(Math.cos(orbitAngle)*9,0,Math.sin(orbitAngle)*9);if(isDeadOrDying())attack.cancel();if(form()==2)getAttribute(Attributes.MOVEMENT_SPEED).setBaseValue(.22);sync();}
    public String visualAnimation(){if(isDeadOrDying())return "death";if(intro())return "intro";if(transition())return "morph";if((skillId()==513||skillId()==516)&&cue()>=skillStart()&&level().getGameTime()-cue()<20)return "slash";return switch(skillId()){case 511->"trample";case 512,517->"slash";case 513->"listen";case 514->"arrows";case 515->"onslaught";case 516->"storm";default->hurtTime>0?"hurt":getDeltaMovement().horizontalDistanceSqr()>.001?"walk":"idle";};}
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar c){c.add(new AnimationController<BlindMarshal>(this,"marshal",0,s->{partial=s.getPartialTick();var controller=s.getController();String name=visualAnimation();long stamp=isDeadOrDying()?skillStart():intro()?born():transition()?shifted():(skillId()==513||skillId()==516)&&name.equals("slash")?cue()-16:skillStart();String key=form()+"/"+name;if(stamp!=animationStamp||!key.equals(animationKey)){animationStamp=stamp;animationKey=key;controller.forceAnimationReset();}controller.setAnimation(name.equals("idle")||name.equals("walk")?RawAnimation.begin().thenLoop("animation."+ID+"."+name):RawAnimation.begin().thenPlayAndHold("animation."+ID+"."+name));return software.bernie.geckolib.core.object.PlayState.CONTINUE;}){
        @Override protected double adjustTick(double tick){boolean reset=shouldResetTick;double local=super.adjustTick(tick);return !reset&&getAnimationState()==AnimationController.State.RUNNING&&animationStamp>=0&&(skillId()!=0||intro()||transition()||isDeadOrDying())?Math.max(0,level().getGameTime()-animationStamp+partial)*(skillId()==517?2:1):local;}
    });}
    @Override public AnimatableInstanceCache getAnimatableInstanceCache(){return cache;}
}
