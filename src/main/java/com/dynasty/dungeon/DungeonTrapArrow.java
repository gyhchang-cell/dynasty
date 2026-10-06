package com.dynasty.dungeon;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.projectile.Arrow;
import net.minecraft.world.level.Level;

/** Short-lived server-fired poison arrows. No pickup, terrain changes or orphaned projectiles. */
public final class DungeonTrapArrow extends Arrow {
    private int remainingTicks=40;

    public DungeonTrapArrow(EntityType<? extends DungeonTrapArrow> type,Level level){
        super(type,level);
        pickup=Pickup.DISALLOWED;
        setBaseDamage(1.5);
        addEffect(new MobEffectInstance(MobEffects.POISON,60,0));
    }
    @Override public void tick(){
        if(!level().isClientSide&&--remainingTicks<=0){discard();return;}
        super.tick();
    }
    @Override public void addAdditionalSaveData(CompoundTag tag){
        super.addAdditionalSaveData(tag);tag.putInt("DungeonRemainingTicks",remainingTicks);
    }
    @Override public void readAdditionalSaveData(CompoundTag tag){
        super.readAdditionalSaveData(tag);
        remainingTicks=tag.contains("DungeonRemainingTicks")?Math.max(1,Math.min(40,tag.getInt("DungeonRemainingTicks"))):40;
        pickup=Pickup.DISALLOWED;
    }
}
