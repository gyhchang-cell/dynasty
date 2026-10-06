package com.dynasty.blueprint;

import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectCategory;
import net.minecraft.world.item.UseAnim;
import net.minecraftforge.event.entity.living.LivingEntityUseItemEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Delay the native shield raising clock; never seize input or alter the camera. */
@Mod.EventBusSubscriber(modid="dynasty")
public final class SandResonanceEffect extends MobEffect {
    public SandResonanceEffect(){super(MobEffectCategory.HARMFUL,0xC6AD69);}
    @SubscribeEvent public static void start(LivingEntityUseItemEvent.Start event){
        if(event.getEntity().hasEffect(BlueprintEntities.SAND_RESONANCE.get())&&event.getItem().getUseAnimation()==UseAnim.BLOCK)
            event.setDuration(Math.min(Integer.MAX_VALUE-15,event.getDuration())+15);
    }
}
