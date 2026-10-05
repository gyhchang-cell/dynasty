package com.dynasty.blueprint;

import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectCategory;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;

/** Stable modifiers expire normally, including after reloading the entity's potion NBT. */
public final class ArmyAuraEffect extends MobEffect {
    public ArmyAuraEffect(){
        super(MobEffectCategory.BENEFICIAL,0x517b79);
        addAttributeModifier(Attributes.ATTACK_DAMAGE,"ad0c36f2-b701-4b3e-a419-e1acdc184f11",.25,AttributeModifier.Operation.MULTIPLY_TOTAL);
        addAttributeModifier(Attributes.MOVEMENT_SPEED,"ad0c36f2-b701-4b3e-a419-e1acdc184f12",.15,AttributeModifier.Operation.MULTIPLY_TOTAL);
    }
}
