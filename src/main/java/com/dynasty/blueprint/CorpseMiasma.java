package com.dynasty.blueprint;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.entity.AreaEffectCloud;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.level.Level;

/** Vanilla tracked cloud/effects with an absolute expiry across chunk unload and reload. */
public final class CorpseMiasma extends AreaEffectCloud {
    private long expires = -1;
    public CorpseMiasma(EntityType<? extends CorpseMiasma> type, Level level) { super(type, level); }
    public void activate(long now) {
        expires=now+80;setDuration(80);setWaitTime(0);setRadius(1.3F);
        setRadiusOnUse(0);setRadiusPerTick(0);setDurationOnUse(0);setFixedColor(0x693480);
        // Custom effects retain their duration; short tails expire after leaving the patch.
        addEffect(new MobEffectInstance(MobEffects.POISON,40,0));
        addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN,40,0));
    }
    @Override public void tick() {
        if(!level().isClientSide&&(expires<0||level().getGameTime()>=expires)){discard();return;}
        super.tick();
    }
    @Override protected void addAdditionalSaveData(CompoundTag tag) { super.addAdditionalSaveData(tag);tag.putLong("DynastyExpires",expires); }
    @Override protected void readAdditionalSaveData(CompoundTag tag) { super.readAdditionalSaveData(tag);expires=tag.contains("DynastyExpires")?tag.getLong("DynastyExpires"):-1; }
}
