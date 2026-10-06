package com.dynasty.blueprint;

import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectCategory;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraftforge.event.entity.living.LivingEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Finite server debuff; ordinary input, gravity, knockback and item use remain available. */
@Mod.EventBusSubscriber(modid="dynasty")
public final class SoulBindEffect extends MobEffect {
    public SoulBindEffect(){this("cf42ff1d-d435-42fb-8c15-564f6455cba9");}
    public SoulBindEffect(String modifier){
        super(MobEffectCategory.HARMFUL,0xDBD1B5);
        addAttributeModifier(Attributes.MOVEMENT_SPEED,modifier,-.95,AttributeModifier.Operation.MULTIPLY_TOTAL);
    }
    @SubscribeEvent public static void jumped(LivingEvent.LivingJumpEvent event){
        var entity=event.getEntity();
        if(!entity.level().isClientSide&&(entity.hasEffect(BlueprintEntities.SOUL_BIND.get())||entity.hasEffect(BlueprintEntities.ROOT_GRIP.get()))){
            var v=entity.getDeltaMovement();entity.setDeltaMovement(v.x,Math.min(0,v.y),v.z);entity.hurtMarked=true;
        }
    }
}
