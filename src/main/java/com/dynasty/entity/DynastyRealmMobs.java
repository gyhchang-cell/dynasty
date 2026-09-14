package com.dynasty.entity;

import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
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
import net.minecraft.world.level.Level;

/**
 * 各维度专属小怪（第二十五轮）：每个世界都有自己的一批杂兵，不再是四张地图只刷那几只。
 *
 * jade_guard 玉甲卫（天朝）：厚甲坦克，周期性给自己抗性
 * soul_soldier 冥卒（地府）：命中施加凋零
 * thunder_envoy 雷使（九霄）：命中麻痹（缓慢 + 虚弱）
 * merfolk 鲛人（龙宫）：水下活动，命中减速
 *
 * Per-dimension mobs so every realm gets its own trash waves.
 */
@SuppressWarnings({"null", "removal"})
public final class DynastyRealmMobs {

    private DynastyRealmMobs() {
    }

    /** 通用行为模板 / shared goals */
    private abstract static class RealmMob extends DynastyHumanoidMob {

        protected RealmMob(EntityType<? extends RealmMob> type, Level level) {
            super(type, level);
        }

        @Override
        protected void registerGoals() {
            this.goalSelector.addGoal(0, new FloatGoal(this));
            this.goalSelector.addGoal(2, new MeleeAttackGoal(this, 1.25D, true));
            this.goalSelector.addGoal(7, new RandomStrollGoal(this, 1.0D));
            this.goalSelector.addGoal(8, new LookAtPlayerGoal(this, Player.class, 16.0F));
            this.goalSelector.addGoal(9, new RandomLookAroundGoal(this));
            this.targetSelector.addGoal(1, new HurtByTargetGoal(this));
            this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
        }

        protected static AttributeSupplier.Builder base(double health, double damage, double speed,
                                                        double armor, double follow) {
            return Monster.createMonsterAttributes()
                    .add(Attributes.MAX_HEALTH, health)
                    .add(Attributes.ATTACK_DAMAGE, damage)
                    .add(Attributes.MOVEMENT_SPEED, speed)
                    .add(Attributes.ARMOR, armor)
                    .add(Attributes.FOLLOW_RANGE, follow);
        }
    }

    /** 玉甲卫 / Jade Guard */
    public static class JadeGuard extends RealmMob {

        public JadeGuard(EntityType<? extends JadeGuard> type, Level level) {
            super(type, level);
            this.xpReward = 22;
        }

        public static AttributeSupplier.Builder createAttributes() {
            return base(420.0D, 1100.0D, 0.30D, 40.0D, 42.0D)
                    .add(Attributes.KNOCKBACK_RESISTANCE, 0.6D);
        }

        @Override
        protected void customServerAiStep() {
            super.customServerAiStep();
            if (this.tickCount % 120 == 0) {
                this.addEffect(new MobEffectInstance(MobEffects.DAMAGE_RESISTANCE, 120, 0, true, false));
            }
        }

        @Override
        public boolean doHurtTarget(net.minecraft.world.entity.Entity target) {
            boolean hit = super.doHurtTarget(target);
            if (hit && target instanceof LivingEntity living) {
                living.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 60, 0));
            }
            return hit;
        }
    }

    /** 冥卒 / Soul Soldier */
    public static class SoulSoldier extends RealmMob {

        public SoulSoldier(EntityType<? extends SoulSoldier> type, Level level) {
            super(type, level);
            this.xpReward = 18;
        }

        public static AttributeSupplier.Builder createAttributes() {
            return base(300.0D, 1000.0D, 0.32D, 22.0D, 40.0D);
        }

        @Override
        public boolean doHurtTarget(net.minecraft.world.entity.Entity target) {
            boolean hit = super.doHurtTarget(target);
            if (hit && target instanceof LivingEntity living) {
                living.addEffect(new MobEffectInstance(MobEffects.WITHER, 100, 1));
            }
            return hit;
        }
    }

    /** 雷使 / Thunder Envoy */
    public static class ThunderEnvoy extends RealmMob {

        public ThunderEnvoy(EntityType<? extends ThunderEnvoy> type, Level level) {
            super(type, level);
            this.xpReward = 24;
        }

        public static AttributeSupplier.Builder createAttributes() {
            return base(340.0D, 1200.0D, 0.34D, 26.0D, 42.0D);
        }

        @Override
        public boolean doHurtTarget(net.minecraft.world.entity.Entity target) {
            boolean hit = super.doHurtTarget(target);
            if (hit && target instanceof LivingEntity living) {
                living.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 80, 1));
                living.addEffect(new MobEffectInstance(MobEffects.WEAKNESS, 80, 0));
            }
            return hit;
        }
    }

    /** 鲛人 / Merfolk */
    public static class Merfolk extends RealmMob {

        public Merfolk(EntityType<? extends Merfolk> type, Level level) {
            super(type, level);
            this.xpReward = 20;
        }

        public static AttributeSupplier.Builder createAttributes() {
            return base(360.0D, 1150.0D, 0.33D, 30.0D, 40.0D);
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
        public boolean doHurtTarget(net.minecraft.world.entity.Entity target) {
            boolean hit = super.doHurtTarget(target);
            if (hit && target instanceof LivingEntity living) {
                living.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 60, 0));
            }
            return hit;
        }
    }
}
