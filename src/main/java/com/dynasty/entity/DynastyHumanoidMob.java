package com.dynasty.entity;

import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.Level;

/**
 * 王朝人形生物基类：提供统一的属性模板与"叛军"标记。
 * Base class for Dynasty humanoid mobs: shared attribute template and rebel flag.
 */
@SuppressWarnings("null")
public abstract class DynastyHumanoidMob extends Monster {
    private static final net.minecraft.network.syncher.EntityDataAccessor<Long> CHARACTER_ATTACK_START =
            net.minecraft.network.syncher.SynchedEntityData.defineId(DynastyHumanoidMob.class, net.minecraft.network.syncher.EntityDataSerializers.LONG);
    @Override protected void defineSynchedData() {
        super.defineSynchedData();entityData.define(CHARACTER_ATTACK_START,-1L);
    }
    /** Only the three remastered melee roles use this clock. One network update per swing. */
    public int characterAttackDuration(){return this instanceof DynastyBosses.RebelGeneral?24:this instanceof DynastyMobs.RoyalGuard?18:14;}
    public void beginCharacterAttack(){entityData.set(CHARACTER_ATTACK_START,level().getGameTime());}
    public void cancelCharacterAttack(){entityData.set(CHARACTER_ATTACK_START,-1L);}
    public float characterAttackProgress(float partial) {
        long start=entityData.get(CHARACTER_ATTACK_START);float elapsed=level().getGameTime()-start+partial;
        return start<0||elapsed<0||elapsed>=characterAttackDuration()?0:elapsed/characterAttackDuration();
    }

    protected DynastyHumanoidMob(EntityType<? extends DynastyHumanoidMob> type, Level level) {
        super(type, level);
    }

    /** 通用属性模板 / shared attribute template */
    public static AttributeSupplier.Builder stats(double health, double damage, double speed,
                                                  double armor, double followRange) {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, health)
                .add(Attributes.ATTACK_DAMAGE, damage)
                .add(Attributes.MOVEMENT_SPEED, speed)
                .add(Attributes.ARMOR, armor)
                .add(Attributes.FOLLOW_RANGE, followRange);
    }

    public boolean isRebel() {
        return this.getPersistentData().getBoolean("dynasty_rebel");
    }

    public void setRebel(boolean rebel) {
        this.getPersistentData().putBoolean("dynasty_rebel", rebel);
    }
}
