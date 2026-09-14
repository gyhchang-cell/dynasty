package com.dynasty.entity;

import com.dynasty.DynastyBossCombat;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerBossEvent;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.BossEvent;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.RandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.DragonFireball;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

/**
 * 王朝 Boss 集合：龙帝、叛将、宦官首脑。
 * Dynasty bosses: the Dragon Emperor, the Rebel General and the Eunuch Mastermind.
 */
public final class DynastyBosses {

    private DynastyBosses() {
    }

    /** 龙帝：天朝之主，龙息火球与召军之术并用。 */
    public static class DragonEmperor extends DynastyHumanoidMob implements DynastyBossCombat.BarHolder {

        private final ServerBossEvent bossEvent = new ServerBossEvent(
                Component.translatable("entity.dynasty.dragon_emperor"),
                BossEvent.BossBarColor.RED, BossEvent.BossBarOverlay.PROGRESS);
        private int phase = 0;
        private int fireballCooldown = 100;
        private int summonCooldown = 200;
        /** 龙焰爆发冷却 / dragon flame burst cooldown */
        private int burstCooldown = 160;
        /** 追击瞬移 / blink-after-fleeing cooldown */
        private int blinkCooldown = 140;
        /** 号召禁军 / rally cooldown */
        private int rallyCooldown = 240;

        public DragonEmperor(EntityType<? extends DragonEmperor> type, Level level) {
            super(type, level);
            this.xpReward = 500;
        }

        public static AttributeSupplier.Builder createAttributes() {
            return Monster.createMonsterAttributes()
                    .add(Attributes.MAX_HEALTH, 1024.0D)
                    .add(Attributes.ATTACK_DAMAGE, 2596.0D)
                    .add(Attributes.MOVEMENT_SPEED, 0.33D)
                    .add(Attributes.ARMOR, 60.0D)
                    .add(Attributes.KNOCKBACK_RESISTANCE, 1.0D)
                    .add(Attributes.FOLLOW_RANGE, 48.0D);
        }

        @Override
        public ServerBossEvent dynastyBossBar() {
            return this.bossEvent;
        }

        @Override
        public boolean fireImmune() {
            return true;
        }

        @Override
        public boolean requiresCustomPersistence() {
            return true;
        }

        @Override
        protected void registerGoals() {
            this.goalSelector.addGoal(0, new FloatGoal(this));
            this.goalSelector.addGoal(2, new MeleeAttackGoal(this, 1.1D, true));
            this.goalSelector.addGoal(7, new RandomStrollGoal(this, 0.9D));
            this.goalSelector.addGoal(8, new LookAtPlayerGoal(this, Player.class, 20.0F));
            this.goalSelector.addGoal(9, new RandomLookAroundGoal(this));
            this.targetSelector.addGoal(1, new HurtByTargetGoal(this));
            this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
        }

        @Override
        protected void customServerAiStep() {
            super.customServerAiStep();
            this.bossEvent.setProgress(this.getHealth() / this.getMaxHealth());
            float ratio = this.getHealth() / this.getMaxHealth();
            if (phase == 0 && ratio <= 0.7F) {
                phase = 1;
                roar();
                this.addEffect(new MobEffectInstance(MobEffects.DAMAGE_RESISTANCE, Integer.MAX_VALUE, 0, false, false));
                summon(3);
            } else if (phase == 1 && ratio <= 0.35F) {
                phase = 2;
                roar();
                this.addEffect(new MobEffectInstance(MobEffects.DAMAGE_BOOST, Integer.MAX_VALUE, 2, false, false));
                this.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SPEED, Integer.MAX_VALUE, 1, false, false));
                summon(5);
            }
            LivingEntity target = this.getTarget();
            if (target == null) {
                return;
            }
            double dist = this.distanceTo(target);
            if (--this.fireballCooldown <= 0) {
                this.fireballCooldown = phase == 2 ? 45 : 80;
                shootFireball(target);
            }
            if (--this.summonCooldown <= 0) {
                this.summonCooldown = 300;
                // 小怪太多就先不召，避免卡顿 / cap the summons
                if (!DynastyBossAI.tooManyMinions(this.level(), this, 24.0D, 12)) {
                    summon(2);
                }
            }
            // 龙焰爆发：发作前 1 秒先给预警（粒子+吼声），玩家有机会跑开
            // telegraphed dragon flame burst
            if (--this.burstCooldown <= 0) {
                this.burstCooldown = phase == 2 ? 120 : 200;
                flameBurst();
            } else if (this.burstCooldown == 20) {
                DynastyBossAI.telegraph(this.level(), this, 6.0D, SoundEvents.ENDER_DRAGON_AMBIENT);
            }
            // 玩家一直跑就瞬移到背后，禁止放风筝 / no kiting the emperor
            if (--this.blinkCooldown <= 0 && dist > 26.0D) {
                this.blinkCooldown = 160;
                DynastyBossAI.blinkBehind(this, target);
            }
            // 狂暴阶段号召禁军 / rally the imperial guard while enraged
            if (this.phase == 2 && --this.rallyCooldown <= 0) {
                this.rallyCooldown = 240;
                DynastyBossAI.rally(this.level(), this, 18.0D);
            }
        }

        /** 龙焰爆发 / burst of dragon fire around the emperor */
        private void flameBurst() {
            if (this.level().isClientSide) {
                return;
            }
            float damage = (float) (600.0D
                    + com.dynasty.DynastyAttributes.value(this, Attributes.ATTACK_DAMAGE, 0.0D) * 0.4D);
            for (LivingEntity victim : this.level().getEntitiesOfClass(LivingEntity.class,
                    this.getBoundingBox().inflate(6.0D), e -> e != this && e.isAlive())) {
                victim.hurt(this.damageSources().mobAttack(this), damage);
                victim.setSecondsOnFire(6);
                if (victim instanceof Player player) {
                    player.addEffect(new MobEffectInstance(MobEffects.WEAKNESS, 100, 0));
                }
            }
            if (this.level() instanceof net.minecraft.server.level.ServerLevel server) {
                server.sendParticles(net.minecraft.core.particles.ParticleTypes.FLAME,
                        this.getX(), this.getY() + 1.0D, this.getZ(), 120, 3.0D, 1.2D, 3.0D, 0.02D);
                server.sendParticles(net.minecraft.core.particles.ParticleTypes.LAVA,
                        this.getX(), this.getY() + 0.5D, this.getZ(), 30, 2.5D, 0.8D, 2.5D, 0.0D);
            }
            this.playSound(SoundEvents.ENDER_DRAGON_GROWL, 3.0F, 0.8F);
        }

        private void shootFireball(LivingEntity target) {
            Vec3 dir = new Vec3(target.getX() - this.getX(), target.getEyeY() - this.getEyeY(),
                    target.getZ() - this.getZ()).normalize();
            DragonFireball fireball = new DragonFireball(this.level(), this,
                    dir.x, dir.y, dir.z);
            fireball.moveTo(this.getX(), this.getEyeY() - 0.3D, this.getZ(), 0.0F, 0.0F);
            this.level().addFreshEntity(fireball);
            this.playSound(SoundEvents.ENDER_DRAGON_SHOOT, 2.0F, 0.8F);
        }

        private void summon(int count) {
            if (this.level().isClientSide) {
                return;
            }
            for (int i = 0; i < count; i++) {
                EntityType<? extends DynastyHumanoidMob> type = (i % 2 == 0)
                        ? DynastyEntities.ROYAL_GUARD.get() : DynastyEntities.ARCHER.get();
                DynastyHumanoidMob guard = type.create(this.level());
                if (guard == null) {
                    continue;
                }
                double dx = (this.getRandom().nextDouble() - 0.5D) * 8.0D;
                double dz = (this.getRandom().nextDouble() - 0.5D) * 8.0D;
                guard.moveTo(this.getX() + dx, this.getY(), this.getZ() + dz,
                        this.getRandom().nextFloat() * 360.0F, 0.0F);
                this.level().addFreshEntity(guard);
            }
        }

        private void roar() {
            this.playSound(SoundEvents.ENDER_DRAGON_GROWL, 3.0F, 0.7F);
        }

        @Override
        public void startSeenByPlayer(ServerPlayer player) {
            super.startSeenByPlayer(player);
            this.bossEvent.addPlayer(player);
        }

        @Override
        public void stopSeenByPlayer(ServerPlayer player) {
            super.stopSeenByPlayer(player);
            this.bossEvent.removePlayer(player);
        }

        @Override
        public void remove(Entity.RemovalReason reason) {
            this.bossEvent.removeAllPlayers();
            super.remove(reason);
        }
    }

    /** 叛将：拥兵自重的叛军首领，冲锋陷阵并召唤叛军。 */
    public static class RebelGeneral extends DynastyHumanoidMob implements DynastyBossCombat.BarHolder {

        private final ServerBossEvent bossEvent = new ServerBossEvent(
                Component.translatable("entity.dynasty.rebel_general"),
                BossEvent.BossBarColor.RED, BossEvent.BossBarOverlay.NOTCHED_10);
        private int chargeCooldown = 120;
        private int summonCooldown = 300;
        /** 掷矛冷却 / spear cooldown */
        private int spearCooldown = 90;
        /** 阶段（0 普通 / 1 狂暴）/ phase */
        private int phase = 0;

        public RebelGeneral(EntityType<? extends RebelGeneral> type, Level level) {
            super(type, level);
            this.setRebel(true);
            this.xpReward = 300;
        }

        public static AttributeSupplier.Builder createAttributes() {
            return Monster.createMonsterAttributes()
                    .add(Attributes.MAX_HEALTH, 1024.0D)
                    .add(Attributes.ATTACK_DAMAGE, 1900.0D)
                    .add(Attributes.MOVEMENT_SPEED, 0.33D)
                    .add(Attributes.ARMOR, 50.0D)
                    .add(Attributes.KNOCKBACK_RESISTANCE, 1.0D)
                    .add(Attributes.FOLLOW_RANGE, 44.0D);
        }

        @Override
        public ServerBossEvent dynastyBossBar() {
            return this.bossEvent;
        }

        @Override
        public boolean requiresCustomPersistence() {
            return true;
        }

        @Override
        protected void registerGoals() {
            this.goalSelector.addGoal(0, new FloatGoal(this));
            this.goalSelector.addGoal(2, new MeleeAttackGoal(this, 1.2D, true));
            this.goalSelector.addGoal(7, new RandomStrollGoal(this, 0.9D));
            this.goalSelector.addGoal(8, new LookAtPlayerGoal(this, Player.class, 20.0F));
            this.goalSelector.addGoal(9, new RandomLookAroundGoal(this));
            this.targetSelector.addGoal(1, new HurtByTargetGoal(this));
            this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
            this.targetSelector.addGoal(3, new NearestAttackableTargetGoal<>(this, ImperialSoldier.class, true));
        }

        @Override
        protected void customServerAiStep() {
            super.customServerAiStep();
            this.bossEvent.setProgress(this.getHealth() / this.getMaxHealth());
            LivingEntity target = this.getTarget();
            if (target == null) {
                return;
            }
            double dist = this.distanceTo(target);
            // 残血狂暴 / enrage below one third health
            if (this.phase == 0 && this.getHealth() / this.getMaxHealth() <= 0.33F) {
                this.phase = 1;
                DynastyBossAI.enrage(this, 1);
            }
            // 冲锋：提前 1 秒预警，然后突进撞飞 / telegraphed charge
            if (--this.chargeCooldown <= 0) {
                this.chargeCooldown = this.phase == 1 ? 80 : 120;
                this.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SPEED, 100, 2, false, false));
                DynastyBossAI.dash(this, target, 1.1D);
            } else if (this.chargeCooldown == 20) {
                DynastyBossAI.telegraph(this.level(), this, 4.0D, SoundEvents.RAVAGER_AMBIENT);
            }
            // 远程掷矛：玩家跑远就丢矛 / throw spears at range
            if (--this.spearCooldown <= 0 && dist > 10.0D) {
                this.spearCooldown = 70;
                DynastyBossAI.shootSpear(this, target, DynastyBossAI.damage(this, 0.45F));
            }
            if (--this.summonCooldown <= 0) {
                this.summonCooldown = 360;
                if (DynastyBossAI.tooManyMinions(this.level(), this, 24.0D, 14)) {
                    return;
                }
                for (int i = 0; i < 4; i++) {
                    DynastyMobs.RebelSoldier rebel = DynastyEntities.REBEL_SOLDIER.get().create(this.level());
                    if (rebel == null) {
                        continue;
                    }
                    double dx = (this.getRandom().nextDouble() - 0.5D) * 8.0D;
                    double dz = (this.getRandom().nextDouble() - 0.5D) * 8.0D;
                    rebel.moveTo(this.getX() + dx, this.getY(), this.getZ() + dz, 0.0F, 0.0F);
                    this.level().addFreshEntity(rebel);
                }
                // 顺便激励一次手下 / rally the rebels
                DynastyBossAI.rally(this.level(), this, 16.0D);
            }
        }

        @Override
        public void startSeenByPlayer(ServerPlayer player) {
            super.startSeenByPlayer(player);
            this.bossEvent.addPlayer(player);
        }

        @Override
        public void stopSeenByPlayer(ServerPlayer player) {
            super.stopSeenByPlayer(player);
            this.bossEvent.removePlayer(player);
        }

        @Override
        public void remove(Entity.RemovalReason reason) {
            this.bossEvent.removeAllPlayers();
            super.remove(reason);
        }
    }

    /** 宦官首脑：幕后权阉，施放虚弱与失明，并放出刺客。 */
    public static class EunuchMastermind extends DynastyHumanoidMob implements DynastyBossCombat.BarHolder {

        private final ServerBossEvent bossEvent = new ServerBossEvent(
                Component.translatable("entity.dynasty.eunuch_mastermind"),
                BossEvent.BossBarColor.PURPLE, BossEvent.BossBarOverlay.NOTCHED_6);
        private int hexCooldown = 100;
        private int summonCooldown = 240;
        /** 被贴身时闪开 / escape blink cooldown */
        private int escapeCooldown = 60;
        /** 毒雾 / poison cloud cooldown */
        private int cloudCooldown = 160;
        /** 躲避远距离玩家 / blink-after-fleeing cooldown */
        private int blinkCooldown = 140;
        /** 阶段 / phase */
        private int phase = 0;

        public EunuchMastermind(EntityType<? extends EunuchMastermind> type, Level level) {
            super(type, level);
            this.xpReward = 260;
        }

        public static AttributeSupplier.Builder createAttributes() {
            return Monster.createMonsterAttributes()
                    .add(Attributes.MAX_HEALTH, 1024.0D)
                    .add(Attributes.ATTACK_DAMAGE, 1400.0D)
                    .add(Attributes.MOVEMENT_SPEED, 0.31D)
                    .add(Attributes.ARMOR, 45.0D)
                    .add(Attributes.KNOCKBACK_RESISTANCE, 0.85D)
                    .add(Attributes.FOLLOW_RANGE, 40.0D);
        }

        @Override
        public ServerBossEvent dynastyBossBar() {
            return this.bossEvent;
        }

        @Override
        public boolean requiresCustomPersistence() {
            return true;
        }

        @Override
        protected void registerGoals() {
            this.goalSelector.addGoal(0, new FloatGoal(this));
            this.goalSelector.addGoal(2, new MeleeAttackGoal(this, 1.15D, true));
            this.goalSelector.addGoal(7, new RandomStrollGoal(this, 0.9D));
            this.goalSelector.addGoal(8, new LookAtPlayerGoal(this, Player.class, 20.0F));
            this.goalSelector.addGoal(9, new RandomLookAroundGoal(this));
            this.targetSelector.addGoal(1, new HurtByTargetGoal(this));
            this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
        }

        @Override
        protected void customServerAiStep() {
            super.customServerAiStep();
            this.bossEvent.setProgress(this.getHealth() / this.getMaxHealth());
            // 残血狂暴 / enrage
            if (this.phase == 0 && this.getHealth() / this.getMaxHealth() <= 0.25F) {
                this.phase = 1;
                DynastyBossAI.enrage(this, 1);
            }
            if (--this.hexCooldown <= 0) {
                this.hexCooldown = this.phase == 1 ? 80 : 110;
                // 阴毒咒术 / hex: weaken and blind nearby players
                for (Player player : this.level().getEntitiesOfClass(Player.class,
                        this.getBoundingBox().inflate(12.0D))) {
                    player.addEffect(new MobEffectInstance(MobEffects.WEAKNESS, 160, 0));
                    player.addEffect(new MobEffectInstance(MobEffects.BLINDNESS, 100, 0));
                }
                this.playSound(SoundEvents.WITCH_DRINK, 1.5F, 0.9F);
            }
            // 毒雾：范围中毒 / poison cloud
            if (--this.cloudCooldown <= 0) {
                this.cloudCooldown = 150;
                DynastyBossAI.poisonCloud(this.level(), this, 6.0D);
            }
            LivingEntity target = this.getTarget();
            if (target != null) {
                double dist = this.distanceTo(target);
                // 被近战贴身就闪开，逼玩家换位 / blink away from melee huggers
                if (--this.escapeCooldown <= 0 && dist < 3.5D) {
                    this.escapeCooldown = 90;
                    DynastyBossAI.blinkAway(this, target, 9.0D);
                }
                // 玩家跑远就瞬移追 / chase runners
                if (--this.blinkCooldown <= 0 && dist > 22.0D) {
                    this.blinkCooldown = 150;
                    DynastyBossAI.blinkBehind(this, target);
                }
            }
            if (--this.summonCooldown <= 0) {
                this.summonCooldown = 240;
                if (DynastyBossAI.tooManyMinions(this.level(), this, 24.0D, 12)) {
                    return;
                }
                for (int i = 0; i < 3; i++) {
                    // 刺客与弓兵混编 / mix of assassins and archers
                    net.minecraft.world.entity.Mob minion = (i == 2
                            ? DynastyEntities.ARCHER.get().create(this.level())
                            : DynastyEntities.ASSASSIN.get().create(this.level()));
                    if (minion == null) {
                        continue;
                    }
                    double dx = (this.getRandom().nextDouble() - 0.5D) * 8.0D;
                    double dz = (this.getRandom().nextDouble() - 0.5D) * 8.0D;
                    minion.moveTo(this.getX() + dx, this.getY(), this.getZ() + dz, 0.0F, 0.0F);
                    this.level().addFreshEntity(minion);
                }
                this.playSound(SoundEvents.EVOKER_PREPARE_SUMMON, 1.5F, 1.0F);
            }
        }

        @Override
        public void startSeenByPlayer(ServerPlayer player) {
            super.startSeenByPlayer(player);
            this.bossEvent.addPlayer(player);
        }

        @Override
        public void stopSeenByPlayer(ServerPlayer player) {
            super.stopSeenByPlayer(player);
            this.bossEvent.removePlayer(player);
        }

        @Override
        public void remove(Entity.RemovalReason reason) {
            this.bossEvent.removeAllPlayers();
            super.remove(reason);
        }
    }

    /**
     * 九霄天将：云海之上的守将，擅长落雷、冲锋与召唤云兵。
     * The Nine-Heaven General: lightning, charges and sky guards.
     */
    public static class NineHeavenGeneral extends DynastyHumanoidMob implements DynastyBossCombat.BarHolder {

        private final ServerBossEvent bossEvent = new ServerBossEvent(
                Component.translatable("entity.dynasty.nine_heaven_general"),
                BossEvent.BossBarColor.BLUE, BossEvent.BossBarOverlay.NOTCHED_12);
        private int boltCooldown = 90;
        private int dashCooldown = 150;
        private int spearCooldown = 100;
        private int summonCooldown = 260;
        private int phase = 0;

        public NineHeavenGeneral(EntityType<? extends NineHeavenGeneral> type, Level level) {
            super(type, level);
            this.xpReward = 420;
        }

        public static AttributeSupplier.Builder createAttributes() {
            return Monster.createMonsterAttributes()
                    .add(Attributes.MAX_HEALTH, 1024.0D)
                    .add(Attributes.ATTACK_DAMAGE, 2048.0D)
                    .add(Attributes.MOVEMENT_SPEED, 0.36D)
                    .add(Attributes.ARMOR, 55.0D)
                    .add(Attributes.KNOCKBACK_RESISTANCE, 1.0D)
                    .add(Attributes.FOLLOW_RANGE, 56.0D);
        }

        @Override
        public ServerBossEvent dynastyBossBar() {
            return this.bossEvent;
        }

        @Override
        public boolean requiresCustomPersistence() {
            return true;
        }

        @Override
        protected void registerGoals() {
            this.goalSelector.addGoal(0, new FloatGoal(this));
            this.goalSelector.addGoal(2, new MeleeAttackGoal(this, 1.25D, true));
            this.goalSelector.addGoal(7,
                    new net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal(this, 1.0D));
            this.goalSelector.addGoal(8, new LookAtPlayerGoal(this, Player.class, 24.0F));
            this.goalSelector.addGoal(9, new RandomLookAroundGoal(this));
            this.targetSelector.addGoal(1, new HurtByTargetGoal(this));
            this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
            this.targetSelector.addGoal(3, new NearestAttackableTargetGoal<>(this, ImperialSoldier.class, true));
        }


        @Override
        protected void customServerAiStep() {
            super.customServerAiStep();
            this.bossEvent.setProgress(this.getHealth() / this.getMaxHealth());
            float ratio = this.getHealth() / this.getMaxHealth();
            if (phase == 0 && ratio <= 0.6F) {
                phase = 1;
                summonSkyGuards(3);
                DynastyBossAI.enrage(this, 1);
            } else if (phase == 1 && ratio <= 0.3F) {
                phase = 2;
                summonSkyGuards(4);
                DynastyBossAI.enrage(this, 2);
            }
            LivingEntity target = this.getTarget();
            if (target == null) {
                return;
            }
            double dist = this.distanceTo(target);
            // 落雷：先预警 1 秒再劈 / telegraphed lightning strike
            if (--this.boltCooldown <= 0 && dist > 3.5D) {
                this.boltCooldown = phase == 2 ? 55 : 90;
                DynastyBossAI.telegraph(this.level(), this, 4.0D, SoundEvents.TRIDENT_THUNDER);
                DynastyBossAI.callLightning(this.level(), target, DynastyBossAI.damage(this, 0.7F));
            }
            // 冲锋切入 / charge into melee
            if (--this.dashCooldown <= 0 && dist > 4.0D) {
                this.dashCooldown = 150;
                DynastyBossAI.dash(this, target, 1.15D);
            }
            // 掷矛：远程压制 / spear throw
            if (--this.spearCooldown <= 0 && dist > 8.0D) {
                this.spearCooldown = 80;
                DynastyBossAI.shootSpear(this, target, DynastyBossAI.damage(this, 0.5F));
            }
            // 召唤云兵（有上限）/ summon sky guards with a cap
            if (--this.summonCooldown <= 0) {
                this.summonCooldown = 280;
                if (!DynastyBossAI.tooManyMinions(this.level(), this, 26.0D, 12)) {
                    summonSkyGuards(3);
                    DynastyBossAI.rally(this.level(), this, 18.0D);
                }
            }
        }

        private void summonSkyGuards(int count) {
            if (this.level().isClientSide) {
                return;
            }
            for (int i = 0; i < count; i++) {
                EntityType<? extends DynastyHumanoidMob> type = (i % 2 == 0)
                        ? DynastyEntities.ARCHER.get() : DynastyEntities.ROYAL_GUARD.get();
                DynastyHumanoidMob guard = type.create(this.level());
                if (guard == null) {
                    continue;
                }
                double dx = (this.getRandom().nextDouble() - 0.5D) * 8.0D;
                double dz = (this.getRandom().nextDouble() - 0.5D) * 8.0D;
                guard.moveTo(this.getX() + dx, this.getY(), this.getZ() + dz,
                        this.getRandom().nextFloat() * 360.0F, 0.0F);
                this.level().addFreshEntity(guard);
            }
        }

        @Override
        public void die(net.minecraft.world.damagesource.DamageSource source) {
            if (source.getEntity() instanceof ServerPlayer player) {
                com.dynasty.DynastyAdvancements.award(player, "slay_sky_general");
            }
            super.die(source);
        }

        @Override
        public void startSeenByPlayer(ServerPlayer player) {
            super.startSeenByPlayer(player);
            this.bossEvent.addPlayer(player);
        }

        @Override
        public void stopSeenByPlayer(ServerPlayer player) {
            super.stopSeenByPlayer(player);
            this.bossEvent.removePlayer(player);
        }

        @Override
        public void remove(Entity.RemovalReason reason) {
            this.bossEvent.removeAllPlayers();
            super.remove(reason);
        }
    }

    /**
     * 东海龙王：龙宫之主，操控雷电与潮汐，召集虾兵蟹将。
     * The Dragon King of the East Sea: lightning, tidal pulls and shrimp/crab soldiers.
     */
    public static class DragonKing extends DynastyHumanoidMob implements DynastyBossCombat.BarHolder {

        private final ServerBossEvent bossEvent = new ServerBossEvent(
                Component.translatable("entity.dynasty.dragon_king"),
                BossEvent.BossBarColor.BLUE, BossEvent.BossBarOverlay.NOTCHED_10);
        private int boltCooldown = 80;
        private int tideCooldown = 170;
        private int tridentCooldown = 100;
        private int summonCooldown = 250;
        private int phase = 0;

        public DragonKing(EntityType<? extends DragonKing> type, Level level) {
            super(type, level);
            this.xpReward = 460;
        }

        public static AttributeSupplier.Builder createAttributes() {
            return Monster.createMonsterAttributes()
                    .add(Attributes.MAX_HEALTH, 1024.0D)
                    .add(Attributes.ATTACK_DAMAGE, 2048.0D)
                    .add(Attributes.MOVEMENT_SPEED, 0.33D)
                    .add(Attributes.ARMOR, 62.0D)
                    .add(Attributes.KNOCKBACK_RESISTANCE, 1.0D)
                    .add(Attributes.FOLLOW_RANGE, 52.0D);
        }

        @Override
        public ServerBossEvent dynastyBossBar() {
            return this.bossEvent;
        }

        @Override
        public boolean canBreatheUnderwater() {
            return true;
        }

        @Override
        public boolean isPushedByFluid() {
            return false;
        }

        @Override
        public boolean requiresCustomPersistence() {
            return true;
        }

        @Override
        protected void registerGoals() {
            this.goalSelector.addGoal(0, new FloatGoal(this));
            this.goalSelector.addGoal(2, new MeleeAttackGoal(this, 1.2D, true));
            this.goalSelector.addGoal(7, new RandomStrollGoal(this, 0.9D));
            this.goalSelector.addGoal(8, new LookAtPlayerGoal(this, Player.class, 24.0F));
            this.goalSelector.addGoal(9, new RandomLookAroundGoal(this));
            this.targetSelector.addGoal(1, new HurtByTargetGoal(this));
            this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
            this.targetSelector.addGoal(3, new NearestAttackableTargetGoal<>(this, ImperialSoldier.class, true));
        }


        @Override
        protected void customServerAiStep() {
            super.customServerAiStep();
            this.bossEvent.setProgress(this.getHealth() / this.getMaxHealth());
            float ratio = this.getHealth() / this.getMaxHealth();
            if (phase == 0 && ratio <= 0.6F) {
                phase = 1;
                summonTide(4);
                DynastyBossAI.enrage(this, 1);
            } else if (phase == 1 && ratio <= 0.3F) {
                phase = 2;
                summonTide(5);
                DynastyBossAI.enrage(this, 2);
            }
            LivingEntity target = this.getTarget();
            if (target == null) {
                return;
            }
            double dist = this.distanceTo(target);
            // 落雷：先预警 / telegraphed lightning
            if (--this.boltCooldown <= 0 && dist > 3.5D) {
                this.boltCooldown = phase == 2 ? 50 : 80;
                DynastyBossAI.telegraph(this.level(), this, 4.0D, SoundEvents.TRIDENT_THUNDER);
                DynastyBossAI.callLightning(this.level(), target, DynastyBossAI.damage(this, 0.7F));
            }
            // 潮汐漩涡：把玩家拉近并减速 / tidal pull
            if (--this.tideCooldown <= 0) {
                this.tideCooldown = phase == 2 ? 110 : 170;
                DynastyBossAI.telegraph(this.level(), this, 9.0D, SoundEvents.ELDER_GUARDIAN_CURSE);
                tidePull();
            }
            // 掷三叉戟 / trident throw
            if (--this.tridentCooldown <= 0 && dist > 6.0D) {
                this.tridentCooldown = 90;
                DynastyBossAI.shootSpear(this, target, DynastyBossAI.damage(this, 0.55F));
            }
            // 虾兵蟹将 / shrimp and crab soldiers
            if (--this.summonCooldown <= 0) {
                this.summonCooldown = 250;
                if (!DynastyBossAI.tooManyMinions(this.level(), this, 26.0D, 14)) {
                    summonTide(3);
                    DynastyBossAI.rally(this.level(), this, 18.0D);
                }
            }
        }

        /** 潮汐：把 12 格内的玩家往龙王这边拉，并给缓慢 / whirlpool pull */
        private void tidePull() {
            if (this.level().isClientSide) {
                return;
            }
            for (Player player : this.level().getEntitiesOfClass(Player.class,
                    this.getBoundingBox().inflate(12.0D))) {
                Vec3 dir = new Vec3(this.getX() - player.getX(), 0.0D, this.getZ() - player.getZ());
                if (dir.lengthSqr() > 1.0E-3D) {
                    dir = dir.normalize().scale(0.85D);
                    player.push(dir.x, 0.28D, dir.z);
                    player.hurtMarked = true;
                }
                player.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 100, 0));
            }
            if (this.level() instanceof net.minecraft.server.level.ServerLevel server) {
                server.sendParticles(net.minecraft.core.particles.ParticleTypes.BUBBLE_COLUMN_UP,
                        this.getX(), this.getY() + 1.0D, this.getZ(), 120, 5.0D, 1.0D, 5.0D, 0.05D);
                server.sendParticles(net.minecraft.core.particles.ParticleTypes.SPLASH,
                        this.getX(), this.getY() + 0.5D, this.getZ(), 60, 4.0D, 0.5D, 4.0D, 0.1D);
            }
        }

        private void summonTide(int count) {
            if (this.level().isClientSide) {
                return;
            }
            for (int i = 0; i < count; i++) {
                net.minecraft.world.entity.Mob guard;
                if (i % 2 == 0) {
                    guard = DynastyEntities.IMPERIAL_SOLDIER.get().create(this.level());
                } else {
                    guard = DynastyEntities.ARCHER.get().create(this.level());
                }
                if (guard == null) {
                    continue;
                }
                double dx = (this.getRandom().nextDouble() - 0.5D) * 9.0D;
                double dz = (this.getRandom().nextDouble() - 0.5D) * 9.0D;
                guard.moveTo(this.getX() + dx, this.getY(), this.getZ() + dz,
                        this.getRandom().nextFloat() * 360.0F, 0.0F);
                guard.setCustomName(Component.literal("§b虾兵蟹将"));
                this.level().addFreshEntity(guard);
            }
        }

        @Override
        public void die(net.minecraft.world.damagesource.DamageSource source) {
            if (source.getEntity() instanceof ServerPlayer player) {
                com.dynasty.DynastyAdvancements.award(player, "slay_dragon_king");
            }
            super.die(source);
        }

        @Override
        public void startSeenByPlayer(ServerPlayer player) {
            super.startSeenByPlayer(player);
            this.bossEvent.addPlayer(player);
        }

        @Override
        public void stopSeenByPlayer(ServerPlayer player) {
            super.stopSeenByPlayer(player);
            this.bossEvent.removePlayer(player);
        }

        @Override
        public void remove(Entity.RemovalReason reason) {
            this.bossEvent.removeAllPlayers();
            super.remove(reason);
        }
    }

}
