package com.dynasty.blueprint;
import net.minecraft.world.effect.*;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.*;
/** Server velocity only while submerged; no keyboard, camera, mining or item-use hooks. */
public final class DrowningBindEffect extends MobEffect {
    public DrowningBindEffect(){super(MobEffectCategory.HARMFUL,0x283D49);addAttributeModifier(Attributes.MOVEMENT_SPEED,"a2dd22fc-60fb-4b58-bf7f-341923de1f21",-.35,AttributeModifier.Operation.MULTIPLY_TOTAL);}
    @Override public boolean isDurationEffectTick(int duration,int amplifier){return true;}
    @Override public void applyEffectTick(LivingEntity entity,int amplifier){
        if(!entity.level().isClientSide&&entity.isInWater()&&entity.getDeltaMovement().y>0){
            var v=entity.getDeltaMovement();entity.setDeltaMovement(v.x,0,v.z);entity.hurtMarked=true;
        }
    }
}
