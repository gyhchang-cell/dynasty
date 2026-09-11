package com.dynasty.entity;

import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerBossEvent;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.BossEvent;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
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
 * 亡故始皇：皇陵深处的 Boss，血量分三阶段。
 * The Undead First Emperor: the boss of the imperial mausoleum, with three health phases.
 */
@SuppressWarnings("null")
public class UndeadFirstEmperor extends Monster {

    private final ServerBossEvent bossEvent =
            new ServerBossEvent(Component.translatable("entity.dynasty.undead_first_emperor"),
                    BossEvent.BossBarColor.YELLOW, BossEvent.BossBarOverlay.PROGRESS);

    private int phase = 0;
    private int summonCooldown = 0;

    public UndeadFirstEmperor(EntityType<? extends UndeadFirstEmperor> type, Level level) {
        super(type, level);
        this.xpReward = 120;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, 1024.0D)
                .add(Attributes.ATTACK_DAMAGE, 1800.0D)
                .add(Attributes.MOVEMENT_SPEED, 0.26D)
                .add(Attributes.ARMOR, 24.0D)
                .add(Attributes.KNOCKBACK_RESISTANCE, 0.6D)
                .add(Attributes.FOLLOW_RANGE, 40.0D);
    }

    @Override
    public boolean removeWhenFarAway(double distance) {
        return false;
    }

    @Override
    public boolean requiresCustomPersistence() {
        return true;
    }

    @Override
    protected void registerGoals() {
        this.goalSelector.addGoal(0, new FloatGoal(this));
        this.goalSelector.addGoal(2, new MeleeAttackGoal(this, 1.15D, false));
        this.goalSelector.addGoal(7, new RandomStrollGoal(this, 0.9D));
        this.goalSelector.addGoal(8, new LookAtPlayerGoal(this, Player.class, 12.0F));
        this.goalSelector.addGoal(9, new RandomLookAroundGoal(this));
        this.targetSelector.addGoal(1, new HurtByTargetGoal(this));
        this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
    }

    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        this.bossEvent.setProgress(this.getHealth() / this.getMaxHealth());

        float ratio = this.getHealth() / this.getMaxHealth();
        if (phase == 0 && ratio <= 0.66F) {
            phase = 1;
            this.addEffect(new MobEffectInstance(MobEffects.DAMAGE_BOOST, Integer.MAX_VALUE, 1, false, false));
            this.addEffect(new MobEffectInstance(MobEffects.DAMAGE_RESISTANCE, Integer.MAX_VALUE, 0, false, false));
            summonMinions(4);
        } else if (phase == 1 && ratio <= 0.33F) {
            phase = 2;
            this.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SPEED, Integer.MAX_VALUE, 1, false, false));
            this.addEffect(new MobEffectInstance(MobEffects.DAMAGE_BOOST, Integer.MAX_VALUE, 2, false, false));
            summonMinions(6);
        }

        if (phase > 0 && --summonCooldown <= 0) {
            summonCooldown = 300;
            summonMinions(2);
        }
    }

    /** 召唤守卫的兵马俑 / summons guarding terracotta warriors */
    private void summonMinions(int count) {
        if (this.level().isClientSide) {
            return;
        }
        for (int i = 0; i < count; i++) {
            TerracottaWarrior minion = DynastyEntities.TERRACOTTA_WARRIOR.get().create(this.level());
            if (minion == null) {
                continue;
            }
            double dx = (this.getRandom().nextDouble() - 0.5D) * 6.0D;
            double dz = (this.getRandom().nextDouble() - 0.5D) * 6.0D;
            minion.moveTo(this.getX() + dx, this.getY(), this.getZ() + dz, this.getRandom().nextFloat() * 360.0F, 0.0F);
            this.level().addFreshEntity(minion);
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
