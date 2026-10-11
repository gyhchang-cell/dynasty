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
    private boolean birdVenom,spiderAcid;
    public void activateSpiderAcid(long now){activate(now);spiderAcid=true;expires=now+100;setDuration(100);setRadius(1.65F);setFixedColor(0x75B54A);}
    public void setBirdVenom(boolean value){birdVenom=value;if(value)setFixedColor(0x6B162A);}
    public boolean ownedBy(net.minecraft.world.entity.LivingEntity mob){return getOwner()!=null&&getOwner().getUUID().equals(mob.getUUID());}
    public SkullBloodPool(EntityType<? extends SkullBloodPool> type,Level level){super(type,level);}
    public void activate(long now){
        expires=now+80;nextWear=now+20;setDuration(80);setWaitTime(0);setRadius(1.2F);
        setRadiusOnUse(0);setRadiusPerTick(0);setDurationOnUse(0);setFixedColor(0x481B23);
    }
    @Override public void tick(){
        if(!level().isClientSide&&(expires<0||level().getGameTime()>=expires)){discard();return;}
        if(level().isClientSide){super.tick();return;}
        if(birdVenom&&getOwner()!=null&&getOwner().isDeadOrDying()){discard();return;}
        if(spiderAcid&&(getOwner()==null||!getOwner().isAlive()||getOwner().distanceToSqr(this)>32*32)){discard();return;}
        // Native tracking/particles, with server pulses restricted to hostile living targets.
        baseTick();if(level().getGameTime()<nextWear)return;nextWear=level().getGameTime()+20;
        for(var victim:level().getEntitiesOfClass(net.minecraft.world.entity.LivingEntity.class,getBoundingBox().inflate(0,.3,0),e->e.isAlive()&&!e.isSpectator())){
            if(victim.position().subtract(position()).horizontalDistanceSqr()>getRadius()*getRadius())continue;
            if(spiderAcid&&!getOwner().hasLineOfSight(victim))continue;
            if(victim instanceof com.dynasty.blueprint.combat.Combatant spirit&&spirit.faction()==com.dynasty.blueprint.combat.Faction.SPIRITS
                ||getOwner()!=null&&com.dynasty.blueprint.combat.Combatant.allied(getOwner(),victim))continue;
            if(victim instanceof Player p&&p.isCreative())continue;
            victim.addEffect(new MobEffectInstance(MobEffects.POISON,40,0),getOwner());
            if(spiderAcid)victim.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN,40,1),getOwner());
            if(birdVenom){victim.addEffect(new MobEffectInstance(MobEffects.WEAKNESS,40),getOwner());victim.addEffect(new MobEffectInstance(MobEffects.WITHER,40),getOwner());continue;}
            if(!(victim instanceof Player player))continue;
            if(player.position().subtract(position()).horizontalDistanceSqr()>getRadius()*getRadius())continue;
            for(var slot:new EquipmentSlot[]{EquipmentSlot.HEAD,EquipmentSlot.CHEST,EquipmentSlot.LEGS,EquipmentSlot.FEET}){
                var stack=player.getItemBySlot(slot);if(stack.isDamageableItem())stack.hurtAndBreak(1,player,p->p.broadcastBreakEvent(slot));
            }
        }
    }
    @Override protected void addAdditionalSaveData(CompoundTag tag){super.addAdditionalSaveData(tag);tag.putLong("DynastyExpires",expires);tag.putLong("NextWear",nextWear);tag.putBoolean("BirdVenom",birdVenom);tag.putBoolean("SpiderAcid",spiderAcid);}
    @Override protected void readAdditionalSaveData(CompoundTag tag){super.readAdditionalSaveData(tag);expires=tag.contains("DynastyExpires")?tag.getLong("DynastyExpires"):-1;nextWear=Math.max(level().getGameTime()+1,tag.getLong("NextWear"));setBirdVenom(tag.getBoolean("BirdVenom"));spiderAcid=tag.getBoolean("SpiderAcid");if(spiderAcid)setFixedColor(0x75B54A);}
}
