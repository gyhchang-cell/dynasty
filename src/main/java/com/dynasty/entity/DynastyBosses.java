package com.dynasty.entity;

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
    public static class DragonEmperor extends DynastyHumanoidMob {

        private final ServerBossEvent bossEvent = new ServerBossEvent(
                Component.translatable("entity.dynasty.dragon_emperor"),
                BossEvent.BossBarColor.RED, BossEvent.BossBarOverlay.PROGRESS);
        private int phase = 0;
        private int fireballCooldown = 100;
        private int summonCooldown = 200;

        public DragonEmperor(EntityType<? extends DragonEmperor> type, Level level) {
            super(type, level);
            this.xpReward = 500;
        }

        public static AttributeSupplier.Builder createAttributes() {
            return Monster.createMonsterAttributes()
                    .add(Attributes.MAX_HEALTH, 1024.0D)
                    .add(Attributes.ATTACK_DAMAGE, 2048.0D)
                    .add(Attributes.MOVEMENT_SPEED, 0.30D)
                    .add(Attributes.ARMOR, 24.0D)
                    .add(Attributes.KNOCKBACK_RESISTANCE, 1.0D)
                    .add(Attributes.FOLLOW_RANGE, 48.0D);
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
            if (target != null) {
                if (--this.fireballCooldown <= 0) {
                    this.fireballCooldown = phase == 2 ? 60 : 100;
                    shootFireball(target);
                }
                if (--this.summonCooldown <= 0) {
                    this.summonCooldown = 400;
                    summon(2);
                }
            }
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
    public static class RebelGeneral extends DynastyHumanoidMob {

        private final ServerBossEvent bossEvent = new ServerBossEvent(
                Component.translatable("entity.dynasty.rebel_general"),
                BossEvent.BossBarColor.RED, BossEvent.BossBarOverlay.NOTCHED_10);
        private int chargeCooldown = 120;
        private int summonCooldown = 300;

        public RebelGeneral(EntityType<? extends RebelGeneral> type, Level level) {
            super(type, level);
            this.setRebel(true);
            this.xpReward = 300;
        }

        public static AttributeSupplier.Builder createAttributes() {
            return Monster.createMonsterAttributes()
                    .add(Attributes.MAX_HEALTH, 1024.0D)
                    .add(Attributes.ATTACK_DAMAGE, 1500.0D)
                    .add(Attributes.MOVEMENT_SPEED, 0.31D)
                    .add(Attributes.ARMOR, 24.0D)
                    .add(Attributes.KNOCKBACK_RESISTANCE, 0.95D)
                    .add(Attributes.FOLLOW_RANGE, 44.0D);
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
            if (--this.chargeCooldown <= 0) {
                this.chargeCooldown = 160;
                // 冲锋 / charge
                this.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SPEED, 100, 2, false, false));
                this.playSound(SoundEvents.RAVAGER_ROAR, 2.0F, 1.2F);
                target.knockback(1.5D, this.getX() - target.getX(), this.getZ() - target.getZ());
            }
            if (--this.summonCooldown <= 0) {
                this.summonCooldown = 500;
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
    public static class EunuchMastermind extends DynastyHumanoidMob {

        private final ServerBossEvent bossEvent = new ServerBossEvent(
                Component.translatable("entity.dynasty.eunuch_mastermind"),
                BossEvent.BossBarColor.PURPLE, BossEvent.BossBarOverlay.NOTCHED_6);
        private int hexCooldown = 100;
        private int summonCooldown = 240;

        public EunuchMastermind(EntityType<? extends EunuchMastermind> type, Level level) {
            super(type, level);
            this.xpReward = 260;
        }

        public static AttributeSupplier.Builder createAttributes() {
            return Monster.createMonsterAttributes()
                    .add(Attributes.MAX_HEALTH, 1024.0D)
                    .add(Attributes.ATTACK_DAMAGE, 900.0D)
                    .add(Attributes.MOVEMENT_SPEED, 0.29D)
                    .add(Attributes.ARMOR, 24.0D)
                    .add(Attributes.KNOCKBACK_RESISTANCE, 0.5D)
                    .add(Attributes.FOLLOW_RANGE, 40.0D);
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
            if (--this.hexCooldown <= 0) {
                this.hexCooldown = 140;
                // 阴毒咒术 / hex: weaken and blind nearby players
                for (Player player : this.level().getEntitiesOfClass(Player.class,
                        this.getBoundingBox().inflate(12.0D))) {
                    player.addEffect(new MobEffectInstance(MobEffects.WEAKNESS, 160, 0));
                    player.addEffect(new MobEffectInstance(MobEffects.BLINDNESS, 100, 0));
                }
                this.playSound(SoundEvents.WITCH_DRINK, 1.5F, 0.9F);
            }
            if (--this.summonCooldown <= 0) {
                this.summonCooldown = 320;
                for (int i = 0; i < 3; i++) {
                    DynastyMobs.Assassin assassin = DynastyEntities.ASSASSIN.get().create(this.level());
                    if (assassin == null) {
                        continue;
                    }
                    double dx = (this.getRandom().nextDouble() - 0.5D) * 8.0D;
                    double dz = (this.getRandom().nextDouble() - 0.5D) * 8.0D;
                    assassin.moveTo(this.getX() + dx, this.getY(), this.getZ() + dz, 0.0F, 0.0F);
                    this.level().addFreshEntity(assassin);
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
}
