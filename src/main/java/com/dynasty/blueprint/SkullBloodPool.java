package com.dynasty.blueprint;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.entity.AreaEffectCloud;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.level.Level;

/** Bounded native cloud; armour corrosion pulses once per second with no unload catch-up. */
public final class SkullBloodPool extends AreaEffectCloud {
    private long expires=-1,nextWear;
    public SkullBloodPool(EntityType<? extends SkullBloodPool> type,Level level){super(type,level);}
    public void activate(long now){
        expires=now+80;nextWear=now+20;setDuration(80);setWaitTime(0);setRadius(1.2F);
        setRadiusOnUse(0);setRadiusPerTick(0);setDurationOnUse(0);setFixedColor(0x481B23);
    }
    @Override public void tick(){
        if(!level().isClientSide&&(expires<0||level().getGameTime()>=expires)){discard();return;}
        if(level().isClientSide){super.tick();return;}
        // Native tracking/particles, with server pulses restricted to hostile living targets.
        baseTick();if(level().getGameTime()<nextWear)return;nextWear=level().getGameTime()+20;
        for(var victim:level().getEntitiesOfClass(net.minecraft.world.entity.LivingEntity.class,getBoundingBox().inflate(0,.3,0),e->e.isAlive()&&!e.isSpectator())){
            if(victim.position().subtract(position()).horizontalDistanceSqr()>getRadius()*getRadius())continue;
            if(victim instanceof com.dynasty.blueprint.combat.Combatant spirit&&spirit.faction()==com.dynasty.blueprint.combat.Faction.SPIRITS
                ||getOwner()!=null&&com.dynasty.blueprint.combat.Combatant.allied(getOwner(),victim))continue;
            if(victim instanceof Player p&&p.isCreative())continue;
            victim.addEffect(new MobEffectInstance(MobEffects.POISON,40,0),getOwner());
            if(!(victim instanceof Player player))continue;
            if(player.position().subtract(position()).horizontalDistanceSqr()>getRadius()*getRadius())continue;
            for(var slot:new EquipmentSlot[]{EquipmentSlot.HEAD,EquipmentSlot.CHEST,EquipmentSlot.LEGS,EquipmentSlot.FEET}){
                var stack=player.getItemBySlot(slot);if(stack.isDamageableItem())stack.hurtAndBreak(1,player,p->p.broadcastBreakEvent(slot));
            }
        }
    }
    @Override protected void addAdditionalSaveData(CompoundTag tag){super.addAdditionalSaveData(tag);tag.putLong("DynastyExpires",expires);tag.putLong("NextWear",nextWear);}
    @Override protected void readAdditionalSaveData(CompoundTag tag){super.readAdditionalSaveData(tag);expires=tag.contains("DynastyExpires")?tag.getLong("DynastyExpires"):-1;nextWear=Math.max(level().getGameTime()+1,tag.getLong("NextWear"));}
}
