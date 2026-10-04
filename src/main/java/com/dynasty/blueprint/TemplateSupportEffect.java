package com.dynasty.blueprint;

import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectCategory;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;

/** Vanilla effect persistence handles expiry and removes these stable UUIDs on reload/removal. */
public final class TemplateSupportEffect extends MobEffect {
    public TemplateSupportEffect() {
        super(MobEffectCategory.BENEFICIAL, 0xB92335);
        addAttributeModifier(Attributes.MOVEMENT_SPEED, "d643ad51-760b-4d96-b4ac-e384e701ad11",
                .3, AttributeModifier.Operation.MULTIPLY_TOTAL);
        addAttributeModifier(Attributes.ATTACK_SPEED, "d643ad51-760b-4d96-b4ac-e384e701ad12",
                .3, AttributeModifier.Operation.MULTIPLY_TOTAL);
        addAttributeModifier(Attributes.KNOCKBACK_RESISTANCE, "d643ad51-760b-4d96-b4ac-e384e701ad13",
                1, AttributeModifier.Operation.ADDITION);
    }
}
