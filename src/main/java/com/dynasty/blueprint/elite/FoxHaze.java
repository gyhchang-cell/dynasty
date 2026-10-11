package com.dynasty.blueprint.elite;
import net.minecraft.world.effect.*;
import net.minecraft.world.entity.ai.attributes.*;
/** Four-second native status, retaining all ordinary movement controls. */
public final class FoxHaze extends MobEffect {
    public FoxHaze(){super(MobEffectCategory.HARMFUL,0xDE92BB);addAttributeModifier(Attributes.MOVEMENT_SPEED,"0be4f23a-485b-4af7-8cfe-eb67b997feba",-.15,AttributeModifier.Operation.MULTIPLY_TOTAL);}
}
