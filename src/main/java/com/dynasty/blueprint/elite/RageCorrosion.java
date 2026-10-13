package com.dynasty.blueprint.elite;

import net.minecraft.world.effect.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.entity.player.Player;

/** Finite native armor reduction; removable milk/status lifecycle, with one wear pulse per second. */
public final class RageCorrosion extends MobEffect {
    public RageCorrosion(){super(MobEffectCategory.HARMFUL,0x7A2632);addAttributeModifier(Attributes.ARMOR,"724d19a1-e52c-4f2f-9973-714e6fb51e21",-4,AttributeModifier.Operation.ADDITION);}
    @Override public boolean isDurationEffectTick(int ticks,int amplifier){return ticks%20==0;}
    @Override public void applyEffectTick(LivingEntity target,int amplifier){
        if(target.level().isClientSide||!(target instanceof Player player)||player.isCreative())return;
        for(var slot:new EquipmentSlot[]{EquipmentSlot.HEAD,EquipmentSlot.CHEST,EquipmentSlot.LEGS,EquipmentSlot.FEET}){var stack=player.getItemBySlot(slot);if(stack.isDamageableItem())stack.hurtAndBreak(1,player,p->p.broadcastBreakEvent(slot));}
    }
}
