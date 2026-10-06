package com.dynasty.blueprint;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.entity.AreaEffectCloud;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.level.Level;

/** Vanilla tracked cloud/effects with an absolute expiry across chunk unload and reload. */
public final class CorpseMiasma extends AreaEffectCloud {
    private long expires = -1,nextPulse;
    private boolean fiery;
    public CorpseMiasma(EntityType<? extends CorpseMiasma> type, Level level) { super(type, level); }
    public void activate(long now) {
        expires=now+80;setDuration(80);setWaitTime(0);setRadius(1.3F);
        setRadiusOnUse(0);setRadiusPerTick(0);setDurationOnUse(0);setFixedColor(0x693480);
        // Custom effects retain their duration; short tails expire after leaving the patch.
        addEffect(new MobEffectInstance(MobEffects.POISON,40,0));
        addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN,40,0));
    }
    public void activateFirePoison(long now){
        fiery=true;expires=now+80;nextPulse=now+10;setDuration(80);setWaitTime(0);setRadius(1.1F);
        setRadiusOnUse(0);setRadiusPerTick(0);setDurationOnUse(0);setFixedColor(0xA54721);
        setParticle(net.minecraft.core.particles.ParticleTypes.FLAME);
    }
    public boolean isFiery(){return fiery;}
    @Override public void tick() {
        if(!level().isClientSide&&(expires<0||level().getGameTime()>=expires)){discard();return;}
        if(fiery&&!level().isClientSide){
            baseTick();if(level().getGameTime()<nextPulse)return;nextPulse=level().getGameTime()+20;
            for(var victim:level().getEntitiesOfClass(net.minecraft.world.entity.LivingEntity.class,getBoundingBox().inflate(0,.3,0),e->e.isAlive()&&!e.isSpectator())){
                if(victim.position().subtract(position()).horizontalDistanceSqr()>getRadius()*getRadius()
                    ||victim instanceof net.minecraft.world.entity.player.Player p&&p.isCreative()
                    ||victim instanceof com.dynasty.blueprint.combat.Combatant c&&c.faction()==com.dynasty.blueprint.combat.Faction.WOODLAND
                    ||getOwner()!=null&&com.dynasty.blueprint.combat.Combatant.allied(getOwner(),victim))continue;
                victim.setSecondsOnFire(2);victim.addEffect(new MobEffectInstance(MobEffects.POISON,40),getOwner());
            }
            return;
        }
        super.tick();
    }
    @Override protected void addAdditionalSaveData(CompoundTag tag) { super.addAdditionalSaveData(tag);tag.putLong("DynastyExpires",expires);tag.putBoolean("Fiery",fiery);tag.putLong("NextPulse",nextPulse); }
    @Override protected void readAdditionalSaveData(CompoundTag tag) { super.readAdditionalSaveData(tag);expires=tag.contains("DynastyExpires")?tag.getLong("DynastyExpires"):-1;fiery=tag.getBoolean("Fiery");nextPulse=Math.max(level().getGameTime()+1,tag.getLong("NextPulse")); }
}
