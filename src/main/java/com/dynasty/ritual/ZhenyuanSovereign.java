package com.dynasty.ritual;

import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerBossEvent;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.util.Mth;
import net.minecraft.world.BossEvent;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import org.joml.Vector3f;

/** The ritual's exclusive boss. No explosions, block changes, loose loot or invisible room-wide hits. */
public final class ZhenyuanSovereign extends Monster implements software.bernie.geckolib.animatable.GeoEntity {
    private final software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache animationCache = software.bernie.geckolib.util.GeckoLibUtil.createInstanceCache(this);
    @Override public software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache getAnimatableInstanceCache() { return animationCache; }
    @Override public void registerControllers(software.bernie.geckolib.core.animation.AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new software.bernie.geckolib.core.animation.AnimationController<>(this,"body",5,state ->
                state.setAndContinue(software.bernie.geckolib.core.animation.RawAnimation.begin().thenLoop(
                        combatReady() && state.isMoving()?"animation.sovereign.walk":"animation.sovereign.idle"))));
    }
    public static final int INTRO_LENGTH = 280;
    private static final net.minecraft.network.syncher.EntityDataAccessor<Integer> INTRO_TICK =
            net.minecraft.network.syncher.SynchedEntityData.defineId(ZhenyuanSovereign.class, net.minecraft.network.syncher.EntityDataSerializers.INT);
    private static final net.minecraft.network.syncher.EntityDataAccessor<Boolean> INTRO_RUNNING =
            net.minecraft.network.syncher.SynchedEntityData.defineId(ZhenyuanSovereign.class, net.minecraft.network.syncher.EntityDataSerializers.BOOLEAN);
    public enum ArrivalStage { SEALED, AWAKENING, INTRO, COMBAT }
    public static ArrivalStage stageAt(int tick) {
        return tick < 60 ? ArrivalStage.SEALED : tick < 140 ? ArrivalStage.AWAKENING : tick < INTRO_LENGTH ? ArrivalStage.INTRO : ArrivalStage.COMBAT;
    }
    @Override protected void defineSynchedData() {
        super.defineSynchedData(); entityData.define(INTRO_TICK, 0); entityData.define(INTRO_RUNNING, false);
    }
    public int introTick() { return entityData.get(INTRO_TICK); }
    public boolean introRunning() { return entityData.get(INTRO_RUNNING); }
    public boolean combatReady() { return introTick() >= INTRO_LENGTH; }
    public void applyEncounterGate(boolean active) {
        if(level() instanceof ServerLevel server) {
            var session=ZhenyuanRitualSavedData.get(server).forBoss(getUUID());
            if(session!=null)entityData.set(INTRO_TICK,session.bossIntroTick);
        }
        entityData.set(INTRO_RUNNING, active && !combatReady());
        setNoAi(!active || !combatReady()); setInvulnerable(!active || !combatReady());
        bar.setVisible(active && introTick() >= 190);
        if(!active || !combatReady()) { setTarget(null); getNavigation().stop(); setDeltaMovement(Vec3.ZERO); }
    }
    @Override public boolean hurt(net.minecraft.world.damagesource.DamageSource source, float amount) {
        return combatReady() && !isNoAi() && super.hurt(source, amount);
    }
    @Override public boolean doHurtTarget(Entity target) { return combatReady() && !isNoAi() && super.doHurtTarget(target); }
    @Override public boolean isPushable() { return combatReady() && !isNoAi() && super.isPushable(); }
    @Override public void push(double x,double y,double z) { if(combatReady()&&!isNoAi())super.push(x,y,z); }
    @Override public void tick() {
        if(level() instanceof ServerLevel server) {
            boolean active=ZhenyuanRitualService.isEncounterActive(getUUID(),server);
            var data=ZhenyuanRitualSavedData.get(server); var session=data.forBoss(getUUID());
            if(session!=null) entityData.set(INTRO_TICK, session.bossIntroTick);
            applyEncounterGate(active);
            if(active && !combatReady()) {
                int t=introTick()+1; entityData.set(INTRO_TICK,t);
                if(session!=null) { session.bossIntroTick=t;session.bossFightStarted=t>=INTRO_LENGTH;data.setDirty(); }
                if(t==12||t==32||t==54) playSound(SoundEvents.WARDEN_HEARTBEAT,1.2F+(t/54F),.55F);
                if(t==190) {
                    playSound(SoundEvents.WARDEN_EMERGE,2,.6F);
                    for(var p:server.players()) if(p.distanceToSqr(this)<90*90) {
                        p.connection.send(new net.minecraft.network.protocol.game.ClientboundSetTitlesAnimationPacket(12,50,22));
                        p.connection.send(new net.minecraft.network.protocol.game.ClientboundSetTitleTextPacket(Component.literal("§6镇渊帝君")));
                    }
                }
                if(t==230) {
                    playSound(SoundEvents.ENDER_DRAGON_GROWL,3,.55F);
                    for(var p:server.getEntitiesOfClass(ServerPlayer.class,getBoundingBox().inflate(10))) {
                        if(p.isSpectator())continue;
                        Vec3 d=p.position().subtract(position());p.knockback(.45,-d.x,-d.z);p.hurtMarked=true;
                    }
                }
                applyEncounterGate(active);
            }
        }
        super.tick();
        if(!level().isClientSide && introTick()>=160 && !combatReady()) {
            var player=ZhenyuanRitualService.participant((ServerLevel)level(),getUUID());
            if(player!=null) {
                float yaw=(float)(Mth.atan2(player.getZ()-getZ(),player.getX()-getX())*180/Math.PI)-90;
                setYHeadRot(Mth.rotLerp(.06F,yHeadRot,yaw));
            }
        }
    }
    private final ServerBossEvent bar = new ServerBossEvent(Component.literal("镇渊帝君 · 封印守望"),
            BossEvent.BossBarColor.YELLOW, BossEvent.BossBarOverlay.NOTCHED_10);
    private int cooldown = 100, warning = 0, pattern = 0, castPhase = 0, announcedPhase = -1;
    private Vec3 castOrigin = Vec3.ZERO;

    public ZhenyuanSovereign(EntityType<? extends ZhenyuanSovereign> type, Level level) {
        super(type, level);
        xpReward = 0;
        setPersistenceRequired();
        applyEncounterGate(false);
    }
    public static AttributeSupplier.Builder attributes() {
        return Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH, 90000)
                .add(Attributes.ATTACK_DAMAGE, 1800).add(Attributes.ARMOR, 35)
                .add(Attributes.ARMOR_TOUGHNESS, 12).add(Attributes.MOVEMENT_SPEED, .27)
                .add(Attributes.KNOCKBACK_RESISTANCE, 1).add(Attributes.FOLLOW_RANGE, 90);
    }
    @Override protected void registerGoals() {
        goalSelector.addGoal(0, new FloatGoal(this));
        goalSelector.addGoal(2, new MeleeAttackGoal(this, 1.05, true));
        goalSelector.addGoal(8, new LookAtPlayerGoal(this, Player.class, 48));
        targetSelector.addGoal(1, new NearestAttackableTargetGoal<>(this, Player.class, true));
    }
    public int ritualPhase() { return ZhenyuanAttackPattern.phase(getHealth() / getMaxHealth()); }
    @Override public boolean removeWhenFarAway(double distance) { return false; }
    @Override protected boolean shouldDespawnInPeaceful() { return false; }
    @Override public boolean causeFallDamage(float distance, float multiplier, net.minecraft.world.damagesource.DamageSource source) { return false; }

    @Override protected void customServerAiStep() {
        if(!combatReady()) return;
        super.customServerAiStep();
        if (!(level() instanceof ServerLevel server)) return;
        if (!ZhenyuanRitualService.isEncounterActive(getUUID(), server)) { getNavigation().stop(); return; }
        int phase = ritualPhase();
        bar.setProgress(Mth.clamp(getHealth() / getMaxHealth(), 0, 1));
        if (phase != announcedPhase) {
            announcedPhase = phase;
            bar.setName(Component.literal("镇渊帝君 · " + new String[]{"封印守望", "四象裂变", "归墟终裁"}[phase]));
            bar.setColor(phase == 2 ? BossEvent.BossBarColor.RED : phase == 1 ? BossEvent.BossBarColor.PURPLE : BossEvent.BossBarColor.YELLOW);
            playSound(SoundEvents.ENDER_DRAGON_GROWL, 1.4F, .72F + phase * .08F);
        }
        if (warning > 0) {
            getNavigation().stop();
            if (warning % 3 == 0) showWarning(server);
            if (--warning == 0) detonate(server);
            return;
        }
        LivingEntity target = getTarget();
        if (target == null || !target.isAlive() || --cooldown > 0) return;
        castPhase = phase;
        pattern = (pattern + 1) % (phase == 0 ? 2 : 3);
        castOrigin = pattern == 1 ? target.position() : position();
        warning = ZhenyuanAttackPattern.WARNING_TICKS;
        cooldown = phase == 2 ? 78 : phase == 1 ? 112 : 150;
        playSound(SoundEvents.BEACON_POWER_SELECT, 1.2F, .65F);
        String instruction = switch (pattern) {
            case 0 -> "§6[帝君·环震] §f避开金色圆环！";
            case 1 -> "§d[帝君·落印] §f离开脚下封印！";
            default -> "§c[帝君·十方裁决] §f站到十字光带之间！";
        };
        for (ServerPlayer p : server.players()) if (p.distanceToSqr(this) < 100 * 100)
            p.displayClientMessage(Component.literal(instruction), true);
    }
    private void showWarning(ServerLevel server) {
        DustParticleOptions gold = new DustParticleOptions(new Vector3f(1, .62F, .18F), 1.6F);
        if (pattern == 2) {
            for (int i = -21; i <= 21; i++) for (double edge : new double[]{-1.35, 1.35}) {
                particle(server, gold, i, edge); particle(server, gold, edge, i);
            }
        } else {
            double radius = pattern == 1 ? 4.5 : ZhenyuanAttackPattern.ringRadius(castPhase);
            for (int i = 0; i < 72; i++) {
                double a = i * Math.PI / 36;
                for (double edge : pattern == 0 ? new double[]{radius - 1.6, radius + 1.6} : new double[]{radius})
                    particle(server, gold, Math.cos(a) * edge, Math.sin(a) * edge);
            }
        }
    }
    private void particle(ServerLevel level, DustParticleOptions type, double x, double z) {
        level.sendParticles(type, castOrigin.x + x, castOrigin.y + .14, castOrigin.z + z, 1, 0, .025, 0, 0);
    }
    private void detonate(ServerLevel server) {
        showWarning(server);
        playSound(SoundEvents.GENERIC_EXPLODE, 1.0F, 1.4F);
        for (ServerPlayer victim : server.getEntitiesOfClass(ServerPlayer.class,
                new AABB(castOrigin, castOrigin).inflate(23, 4, 23))) {
            if (victim.isCreative() || victim.isSpectator()) continue;
            Vec3 d = victim.position().subtract(castOrigin);
            if (Math.abs(d.y) < 3.5 && ZhenyuanAttackPattern.hit(pattern, castPhase, d.x, d.z)) {
                victim.hurt(damageSources().mobAttack(this), (float) getAttributeValue(Attributes.ATTACK_DAMAGE) * (1 + castPhase * .2F));
                victim.knockback(.7, -d.x, -d.z);
            }
        }
    }
    @Override public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        tag.putInt("ArrivalTick",introTick());
        tag.putInt("RitualCooldown", cooldown); tag.putInt("RitualWarning", warning);
        tag.putInt("RitualPattern", pattern); tag.putInt("RitualCastPhase", castPhase);
        tag.putDouble("CastX", castOrigin.x); tag.putDouble("CastY", castOrigin.y); tag.putDouble("CastZ", castOrigin.z);
    }
    @Override public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        entityData.set(INTRO_TICK,tag.contains("ArrivalTick")?Mth.clamp(tag.getInt("ArrivalTick"),0,INTRO_LENGTH):INTRO_LENGTH);
        applyEncounterGate(false);
        cooldown = Math.max(40, tag.getInt("RitualCooldown"));
        warning = tag.getInt("RitualWarning") > 0 ? ZhenyuanAttackPattern.WARNING_TICKS : 0;
        pattern = Mth.clamp(tag.getInt("RitualPattern"), 0, 2); castPhase = Mth.clamp(tag.getInt("RitualCastPhase"), 0, 2);
        castOrigin = new Vec3(tag.getDouble("CastX"), tag.getDouble("CastY"), tag.getDouble("CastZ"));
        if (!Double.isFinite(castOrigin.lengthSqr())) { castOrigin = position(); warning = 0; }
    }
    @Override public void startSeenByPlayer(ServerPlayer p) {
        super.startSeenByPlayer(p);
        if (!(p instanceof net.minecraftforge.common.util.FakePlayer)) bar.addPlayer(p);
    }
    @Override public void stopSeenByPlayer(ServerPlayer p) { super.stopSeenByPlayer(p); bar.removePlayer(p); }
    @Override public void remove(Entity.RemovalReason reason) { bar.removeAllPlayers(); super.remove(reason); }
}
