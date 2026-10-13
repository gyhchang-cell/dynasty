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

/** Original mechanical aircraft, with real bounded flight and authored-platform terrain changes. */
public final class WoodKite extends Monster implements GeoEntity,Combatant {
    public static final String ID="luban_yisha";
    public static final SkillDefinition CUT=new SkillDefinition(521,"kite_wing_cut",24,32,16,220,0,28,0,1.2F,.5,true,true,List.of());
    public static final SkillDefinition BOMBS=new SkillDefinition(522,"kite_bombs",24,60,20,300,0,28,360,.8F,.4,true,true,List.of(24,30,36,42,48,54,60,66));
    public static final SkillDefinition CLAWS=new SkillDefinition(523,"kite_claws",28,20,44,280,0,28,360,1.4F,.8,true,true,List.of(36));
    public static final SkillDefinition WIND=new SkillDefinition(524,"kite_wind",24,80,16,360,0,28,90,0,.045,true,true,List.of());
    public static final SkillDefinition LIGHTNING=new SkillDefinition(525,"kite_lightning",32,64,16,380,0,28,360,1.5F,.7,true,true,List.of(32,48,64,80));
    public static final SkillDefinition METEOR=new SkillDefinition(526,"kite_meteor",60,24,24,500,0,28,360,1.8F,.7,true,true,List.of());
    private static final EntityDataAccessor<Integer> FORM=SynchedEntityData.defineId(WoodKite.class,EntityDataSerializers.INT),SKILL=SynchedEntityData.defineId(WoodKite.class,EntityDataSerializers.INT),PHASE=SynchedEntityData.defineId(WoodKite.class,EntityDataSerializers.INT);
    private static final EntityDataAccessor<Long> BORN=SynchedEntityData.defineId(WoodKite.class,EntityDataSerializers.LONG),SHIFT=SynchedEntityData.defineId(WoodKite.class,EntityDataSerializers.LONG),START=SynchedEntityData.defineId(WoodKite.class,EntityDataSerializers.LONG);
    private static final EntityDataAccessor<BlockPos> ARENA=SynchedEntityData.defineId(WoodKite.class,EntityDataSerializers.BLOCK_POS),LOCK=SynchedEntityData.defineId(WoodKite.class,EntityDataSerializers.BLOCK_POS);
    private static final EntityDataAccessor<Boolean> BOUND=SynchedEntityData.defineId(WoodKite.class,EntityDataSerializers.BOOLEAN);
    private final TimedAttack attack=new TimedAttack();
    private final AnimatableInstanceCache cache=GeckoLibUtil.createInstanceCache(this);
    private final ServerBossEvent bar=new ServerBossEvent(Component.translatable("entity.dynasty."+ID),BossEvent.BossBarColor.PURPLE,BossEvent.BossBarOverlay.PROGRESS);
    private final DynastyBossBarSubscriptions subscriptions=new DynastyBossBarSubscriptions(this,bar);
    private final Set<UUID> hits=new HashSet<>();
    private long lastCombat=-1,deathStart=-1,nextChoice,bombEpoch,animationStamp=Long.MIN_VALUE;
    private static final EntityDataAccessor<Float> ANGLE=SynchedEntityData.defineId(WoodKite.class,EntityDataSerializers.FLOAT);
    private UUID grabbed;
    private String animationKey="";
    private float partial;
    public WoodKite(EntityType<? extends WoodKite> type,Level world){super(type,world);xpReward=180;setNoGravity(true);setPersistenceRequired();}
    @Override protected void defineSynchedData(){super.defineSynchedData();entityData.define(FORM,1);entityData.define(SKILL,0);entityData.define(PHASE,0);entityData.define(BORN,level().getGameTime());entityData.define(SHIFT,-1L);entityData.define(START,-1L);entityData.define(ARENA,BlockPos.ZERO);entityData.define(LOCK,BlockPos.ZERO);entityData.define(BOUND,false);entityData.define(ANGLE,0F);}
    @Override protected void registerGoals(){targetSelector.addGoal(1,new HurtByTargetGoal(this));targetSelector.addGoal(2,new NearestAttackableTargetGoal<>(this,Player.class,true));}
    @Override public Faction faction(){return Faction.CONSTRUCT;}
    @Override public MobRole role(){return MobRole.BEAST;}
    @Override public boolean removeWhenFarAway(double d){return false;}
    @Override public boolean canChangeDimensions(){return false;}
    @Override public boolean causeFallDamage(float distance,float multiplier,DamageSource source){return false;}
    public TimedAttack attack(){return attack;}
    public int form(){return entityData.get(FORM);}
    public int skillId(){return entityData.get(SKILL);}
    public long skillStart(){return entityData.get(START);}
    public long bombEpoch(){return bombEpoch;}
    public List<WoodKiteBomb> bombs(){var bounds=new AABB(centre().add(-22,-4,-22),centre().add(22,20,22));return level() instanceof ServerLevel w&&loaded(bounds)?w.getEntitiesOfClass(WoodKiteBomb.class,bounds,b->b.ownedBy(this)).stream().limit(8).toList():List.of();}
    @Override public boolean shouldRenderAtSqrDistance(double d){return Double.isFinite(d)&&d<128*128;}
    public long born(){return entityData.get(BORN);}
    public long shifted(){return entityData.get(SHIFT);}
    public BlockPos arenaCentre(){return entityData.get(BOUND)?entityData.get(ARENA):null;}
    public Vec3 centre(){return arenaCentre()==null?position():Vec3.atBottomCenterOf(arenaCentre());}
    public Vec3 lockedPoint(){return Vec3.atBottomCenterOf(entityData.get(LOCK));}
    public void bindArena(BlockPos p){entityData.set(ARENA,p.immutable());entityData.set(BOUND,true);}
    public boolean intro(){return level().getGameTime()>=born()&&level().getGameTime()-born()<200;}
    public boolean transition(){return form()==2&&shifted()>=0&&level().getGameTime()>=shifted()&&level().getGameTime()-shifted()<48;}
    public AttackState phase(){return AttackState.values()[Math.max(0,Math.min(4,entityData.get(PHASE)))];}
    public static SkillDefinition skill(int id){return switch(id){case 521->CUT;case 522->BOMBS;case 523->CLAWS;case 524->WIND;case 525->LIGHTNING;case 526->METEOR;default->null;};}
    public boolean enemy(LivingEntity e){return e!=null&&e.isAlive()&&!e.isSpectator()&&!Combatant.allied(this,e)&&!(e instanceof Player p&&p.isCreative());}
    public boolean loaded(AABB box){return level() instanceof ServerLevel w&&com.dynasty.blueprint.artifact.ArtifactAbility.loaded(w,box);}
    private boolean inArena(Vec3 p,double radius){return Double.isFinite(p.lengthSqr())&&p.subtract(centre()).multiply(1,0,1).lengthSqr()<=radius*radius&&p.y>=centre().y-24&&p.y<=centre().y+56;}
    private boolean moveToPoint(Vec3 wanted,double maximum){if(!inArena(wanted,25))return false;var delta=wanted.subtract(position());if(delta.length()>maximum)delta=delta.normalize().scale(maximum);var swept=getBoundingBox().expandTowards(delta);if(!loaded(swept))return false;var before=position();move(MoverType.SELF,delta);setDeltaMovement(Vec3.ZERO);if(position().distanceToSqr(before.add(delta))>.04)return false;return true;}
    private void face(Vec3 d){if(d.horizontalDistanceSqr()<.001)return;setYRot((float)Math.toDegrees(Math.atan2(-d.x,d.z)));setYHeadRot(getYRot());yBodyRot=getYRot();setXRot(0);}
    public boolean startSkill(int id,LivingEntity target){var def=skill(id);if(level().isClientSide||arenaCentre()==null||!isAlive()||intro()||transition()||def==null||form()==1&&(def==LIGHTNING||def==METEOR)||!enemy(target)||!inArena(target.position(),20)||Math.abs(target.getY()-centre().y)>6||def.requiresSight()&&!hasLineOfSight(target))return false;var f=target.position().subtract(centre()).multiply(1,0,1).normalize();if(f.lengthSqr()<.001)f=getLookAngle().multiply(1,0,1).normalize();if(!attack.tryStart(def,level().getGameTime(),position(),f,target.getUUID()))return false;if(def==BOMBS)clearBombs();entityData.set(LOCK,BlockPos.containing(target.position()));entityData.set(ANGLE,(float)Math.atan2(f.z,f.x));hits.clear();grabbed=null;face(f);navigation.stop();setDeltaMovement(Vec3.ZERO);sync();BlueprintVisualEvent.start(this,def,lockedPoint(),f,target.getId());return true;}
    private void sync(){entityData.set(SKILL,attack.current()==null?0:attack.current().id());entityData.set(PHASE,attack.state(level().getGameTime()).ordinal());entityData.set(START,attack.current()!=null?attack.started():deathStart>=0?deathStart:transition()?shifted():intro()?born():-1L);}
    public void parried(int ticks){if(isAlive()&&!intro()&&!transition())stop(Math.max(1,Math.min(40,ticks)));}
    private void stop(int ticks){attack.stun(level().getGameTime(),ticks);grabbed=null;clearBombs();navigation.stop();setDeltaMovement(Vec3.ZERO);BlueprintVisualEvent.cancel(this);sync();}
    private void clearBombs(){bombEpoch++;if(level() instanceof ServerLevel w&&loaded(new AABB(centre().add(-22,-4,-22),centre().add(22,20,22))))for(var bomb:w.getEntitiesOfClass(WoodKiteBomb.class,new AABB(centre().add(-22,-4,-22),centre().add(22,20,22)),b->b.ownedBy(this)))bomb.discard();}
    @Override protected void customServerAiStep(){super.customServerAiStep();combat();}
    @Override public void tick(){super.tick();if(!level().isClientSide&&isNoAi())combat();}
    @Override public void travel(Vec3 input){setNoGravity(true);setDeltaMovement(Vec3.ZERO);setXxa(0);setYya(0);setZza(0);}
    private void combat(){if(!(level() instanceof ServerLevel w)||!isAlive())return;long now=w.getGameTime();if(lastCombat==now)return;if(lastCombat>=0&&(now<lastCombat||now-lastCombat>1)){lastCombat=now;stop(40);return;}lastCombat=now;if(arenaCentre()==null){navigation.stop();return;}bar.setProgress(Math.max(0,getHealth()/getMaxHealth()));
        if(intro()){long t=now-born();var c=centre();if(t<160&&t%10==0){double a=t*.07;w.sendParticles(net.minecraft.core.particles.ParticleTypes.CLOUD,c.x+Math.cos(a)*19,c.y-3,c.z+Math.sin(a)*19,4,1,.3,1,.025);}Vec3 wanted=t<60?c.add(22,-16,0):t<120?c.add(22,(-16+24*(t-60)/60D),0):t<160?c.add(22-31*(t-120)/40D,8-4*(t-120)/40D,0):c.add(-9+9*(t-160)/40D,4*(1-(t-160)/40D),0);moveToPoint(wanted,1.7);face(new Vec3(-1,0,0));sync();return;}
        subscriptions.tick();if(form()==1&&getHealth()<=getMaxHealth()*.6F){attack.cancel();clearBombs();grabbed=null;entityData.set(FORM,2);entityData.set(SHIFT,now);getAttribute(Attributes.FLYING_SPEED).setBaseValue(.68);getAttribute(Attributes.MOVEMENT_SPEED).setBaseValue(.34);BlueprintVisualEvent.cancel(this);}
        if(transition()){moveToPoint(centre().add(0,4,0),1);sync();return;}if(attack.state(now)==AttackState.STUN){sync();return;}
        var current=attack.current();if(current!=null){long age=now-attack.started();var f=attack.direction();var side=new Vec3(-f.z,0,f.x);face(f);
            if(current==CUT){double u=Math.max(0,Math.min(32,age-24));var wanted=centre().add(f.scale(-16+u)).add(side.scale(9*Math.sin(Math.PI*u/32)));if(age<24)wanted=centre().add(f.scale(-16));if(!moveToPoint(wanted,1.7)){stop(40);return;}if(age>=24&&age<56)wingHit(f,side);}
            else if(current==BOMBS){double a=(now-attack.started())*(form()==2?.07:.045);moveToPoint(centre().add(Math.cos(a)*8,8,Math.sin(a)*8),1.5);}
            else if(current==CLAWS){var aim=lockedPoint();if(age<28)moveToPoint(new Vec3(aim.x,centre().y+10,aim.z),1.5);else if(age<=36){double height=10*Math.max(0,1-(age-28)/8D);moveToPoint(new Vec3(aim.x,centre().y+height,aim.z),2);}if(age>36&&age<=48&&grabbed!=null)carryGrabbed(w,age);}
            else if(current==WIND){moveToPoint(centre().subtract(f.scale(10)),1.2);if(age>=24&&age<104)wind(f);}
            else if(current==LIGHTNING)moveToPoint(centre().add(0,10,0),1.5);
            else if(current==METEOR){if(age<=60){moveToPoint(centre().add(0,50,0),2.5);}else if(age<=68){double h=50*Math.max(0,1-(age-60)/8D);if(!moveToPoint(centre().add(0,h,0),8)){stop(40);return;}}if(age>=68&&age<=80&&(age-68)%2==0)groundWave((age-68)/12D*19+1);}
            attack.advance(now,t->impact(w,current,t));sync();return;
        }
        if(!isNoAi()&&now>=nextChoice){var target=getTarget();if(enemy(target)&&inArena(target.position(),20)){int[] order=form()==2?new int[]{525,526,522,523,521,524}:new int[]{522,523,521,524};for(int id:order)if(startSkill(id,target)){nextChoice=now+20;break;}}else if(target!=null&&!inArena(target.position(),20))setTarget(null);}
        if(attack.current()==null){double a=now*.01;moveToPoint(centre().add(Math.cos(a)*7,4,Math.sin(a)*7),form()==2?.68:.4);}sync();
    }
    public Vec3 wingOrigin(Vec3 side){return position().add(side.scale(2.8)).subtract(new Vec3(side.z,0,-side.x).scale(.8125)).add(0,1.75,0);}
    private void wingHit(Vec3 f,Vec3 side){var at=wingOrigin(side);for(var e:CombatGeometry.query((ServerLevel)level(),at,side,CombatGeometry.Shape.STRIP,1.7,2.1,0,.25,this::enemy).stream().limit(16).toList())if(hits.size()<16&&!hits.contains(e.getUUID())&&hit(e,CUT.damageMultiplier(),CUT.knockback()))hits.add(e.getUUID());}
    private boolean hit(LivingEntity e,float multiplier,double knock){if(!isAlive()||!enemy(e)||!hasLineOfSight(e)||!inArena(e.position(),20))return false;double damage=getAttributeValue(Attributes.ATTACK_DAMAGE)*multiplier;if(!Double.isFinite(damage)||damage<=0)return false;if(!e.hurt(damageSources().mobAttack(this),(float)Math.min(512,damage)))return false;if(knock>0)e.knockback(knock,getX()-e.getX(),getZ()-e.getZ());return true;}
    public List<LivingEntity> targets(Vec3 at,double radius,double height){if(!(level() instanceof ServerLevel w)||!loaded(new AABB(at,at).inflate(radius,height,radius)))return List.of();return CombatGeometry.query(w,at,new Vec3(0,0,1),CombatGeometry.Shape.CIRCLE,radius,0,360,height,e->enemy(e)&&inArena(e.position(),20)).stream().limit(16).toList();}
    public Vec3 lightningPoint(int index){double a=entityData.get(ANGLE)+index*Math.PI/2;return centre().add(Math.cos(a)*11,0,Math.sin(a)*11);}
    private void impact(ServerLevel w,SkillDefinition def,int tick){if(def==BOMBS){int i=(tick-24)/6;var bomb=WoodKiteContent.BOMB.get().create(w);if(bomb!=null){bomb.begin(this,i);w.addFreshEntity(bomb);}}else if(def==CLAWS){for(var e:targets(lockedPoint().add(0,.6,0),2.2,1.2))if(grabbed==null&&e instanceof Player&&hit(e,CLAWS.damageMultiplier(),0)){grabbed=e.getUUID();break;}}else if(def==LIGHTNING){var mark=lightningPoint((tick-32)/16);for(var e:targets(mark.add(0,1,0),4,3))hit(e,LIGHTNING.damageMultiplier(),LIGHTNING.knockback());StargazerPlatforms.scar(this,BlockPos.containing(mark));w.sendParticles(net.minecraft.core.particles.ParticleTypes.ELECTRIC_SPARK,mark.x,mark.y+2,mark.z,12,.5,2,.5,.04);}}
    private void carryGrabbed(ServerLevel w,long age){var e=grabbed==null?null:w.getEntity(grabbed);if(!(e instanceof LivingEntity target)||!enemy(target)||!inArena(target.position(),20)||!hasLineOfSight(target)){grabbed=null;return;}var out=lockedPoint().subtract(centre()).multiply(1,0,1).normalize();if(out.lengthSqr()<.001)out=attack.direction();var wanted=target.position().add(out.scale(.55));if(!loaded(target.getBoundingBox().expandTowards(out.scale(.55)))||!level().noCollision(target,target.getBoundingBox().move(out.scale(.55)))){grabbed=null;return;}target.move(MoverType.SELF,out.scale(.55));target.hurtMarked=true;if(age==48){target.knockback(.85,-out.x,-out.z);grabbed=null;}}
    private void wind(Vec3 forward){var origin=position().add(0,1.5,0);for(var e:CombatGeometry.query((ServerLevel)level(),origin,forward,CombatGeometry.Shape.CONE,24,0,90,3,this::enemy).stream().limit(16).toList())if(inArena(e.position(),20)&&hasLineOfSight(e)){double resistance=Math.max(0,Math.min(1,e.getAttributeValue(Attributes.KNOCKBACK_RESISTANCE)));var push=forward.scale(.045*(1-resistance));e.setDeltaMovement(e.getDeltaMovement().add(push));e.hurtMarked=true;}}
    private void groundWave(double radius){var at=centre();for(var e:targets(at.add(0,.25,0),Math.min(20,radius),.5))if(hits.size()<16&&!hits.contains(e.getUUID())&&e.getBoundingBox().minY<at.y+.5&&hit(e,METEOR.damageMultiplier(),METEOR.knockback()))hits.add(e.getUUID());}
    @Override public boolean hurt(DamageSource source,float amount){if(!level().isClientSide&&(intro()||transition())&&!source.is(net.minecraft.tags.DamageTypeTags.BYPASSES_INVULNERABILITY))return false;float before=getHealth();boolean accepted=super.hurt(source,amount);if(accepted&&!level().isClientSide&&isAlive()&&before-getHealth()>=30&&phase()==AttackState.WINDUP)stop(40);return accepted;}
    @Override public void startSeenByPlayer(ServerPlayer p){super.startSeenByPlayer(p);subscriptions.startSeenByPlayer(p);}
    @Override public void stopSeenByPlayer(ServerPlayer p){super.stopSeenByPlayer(p);subscriptions.stopSeenByPlayer(p);}
    @Override public void die(DamageSource source){if(deathStart>=0)return;super.die(source);if(!isDeadOrDying())return;deathStart=level().getGameTime();attack.cancel();clearBombs();grabbed=null;setTarget(null);subscriptions.clear();BlueprintVisualEvent.cancel(this);sync();BlueprintVisualEvent.death(this);StargazerPlatforms.confirmedDeath(this);}
    @Override public void remove(RemovalReason reason){if(reason.shouldDestroy()&&!isDeadOrDying())StargazerPlatforms.destroyed(this);subscriptions.clear();super.remove(reason);}
    @Override protected void tickDeath(){deathTime++;if(level() instanceof ServerLevel){double t=Math.min(1,deathTime/220D);var c=centre();var wanted=c.add(21*t,deathTime<40?8*deathTime/40D:8-80*Math.pow((deathTime-40)/180D,2),0);if(loaded(getBoundingBox().expandTowards(wanted.subtract(position()))))move(MoverType.SELF,wanted.subtract(position()));setDeltaMovement(Vec3.ZERO);if(deathTime>=220)remove(RemovalReason.KILLED);}}
    @Override public void addAdditionalSaveData(CompoundTag n){super.addAdditionalSaveData(n);n.put("KiteAttack",attack.save());n.putInt("KiteForm",form());n.putLong("KiteBorn",born());n.putLong("KiteShift",shifted());n.putLong("KiteDeath",deathStart);n.putLong("KiteLast",lastCombat);n.putLong("KiteLock",entityData.get(LOCK).asLong());n.putDouble("KiteAngle",entityData.get(ANGLE));if(arenaCentre()!=null)n.putLong("KiteArena",arenaCentre().asLong());}
    @Override public void readAdditionalSaveData(CompoundTag n){super.readAdditionalSaveData(n);long now=level().getGameTime();bombEpoch++;entityData.set(FORM,n.getInt("KiteForm")==2?2:1);long birth=n.contains("KiteBorn")?n.getLong("KiteBorn"):now;entityData.set(BORN,birth>=0&&birth<=now?birth:now);long shift=n.contains("KiteShift")?n.getLong("KiteShift"):-1;entityData.set(SHIFT,shift>=0&&shift<=now?shift:-1);var arena=n.contains("KiteArena")?BlockPos.of(n.getLong("KiteArena")):null;if(arena!=null&&(Math.abs(arena.getX()-getX())>32||Math.abs(arena.getZ()-getZ())>32||Math.abs(arena.getY()-getY())>96))arena=null;entityData.set(BOUND,arena!=null);entityData.set(ARENA,arena==null?BlockPos.ZERO:arena);entityData.set(LOCK,n.contains("KiteLock")?BlockPos.of(n.getLong("KiteLock")):blockPosition());long savedDeath=n.contains("KiteDeath")?n.getLong("KiteDeath"):-1;deathStart=isDeadOrDying()&&savedDeath>=0&&savedDeath<=now?savedDeath:-1;lastCombat=n.contains("KiteLast")?n.getLong("KiteLast"):-1;double angle=n.getDouble("KiteAngle");entityData.set(ANGLE,Double.isFinite(angle)?(float)Math.IEEEremainder(angle,Math.PI*2):0F);attack.load(n.getCompound("KiteAttack"),WoodKite::skill,now);attack.cancel();grabbed=null;hits.clear();setNoGravity(true);if(form()==2){getAttribute(Attributes.FLYING_SPEED).setBaseValue(.68);getAttribute(Attributes.MOVEMENT_SPEED).setBaseValue(.34);}sync();}
    public String visualAnimation(){if(isDeadOrDying())return "death";if(intro())return "intro";if(transition())return "overheat";if(phase()==AttackState.STUN)return "stun";return switch(skillId()){case 521->"wing_cut";case 522->"bombs";case 523->"claws";case 524->"wind";case 525->"lightning";case 526->"meteor";default->getY()>centre().y+.3?"fly":"idle";};}
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar c){c.add(new AnimationController<WoodKite>(this,"aircraft",0,s->{partial=s.getPartialTick();var control=s.getController();String name=visualAnimation();long stamp=isDeadOrDying()?skillStart():intro()?born():transition()?shifted():skillStart();String key=form()+"/"+name;if(stamp!=animationStamp||!key.equals(animationKey)){animationStamp=stamp;animationKey=key;control.forceAnimationReset();}control.setAnimation(name.equals("idle")||name.equals("fly")||name.equals("stun")?RawAnimation.begin().thenLoop("animation."+ID+"."+name):RawAnimation.begin().thenPlayAndHold("animation."+ID+"."+name));return software.bernie.geckolib.core.object.PlayState.CONTINUE;}){@Override protected double adjustTick(double tick){boolean reset=shouldResetTick;double local=super.adjustTick(tick);return !reset&&getAnimationState()==AnimationController.State.RUNNING&&animationStamp>=0&&(skillId()!=0||intro()||transition()||isDeadOrDying())?Math.max(0,level().getGameTime()-animationStamp+partial):local;}});}
    @Override public AnimatableInstanceCache getAnimatableInstanceCache(){return cache;}
}
