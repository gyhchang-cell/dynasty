package com.dynasty.blueprint;

import net.minecraftforge.event.entity.living.LivingDamageEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Final post-armour damage, before vanilla commits health loss/death/loot. */
@Mod.EventBusSubscriber(modid="dynasty")
public final class PaperSubstitution {
    private PaperSubstitution(){}
    @SubscribeEvent(priority=EventPriority.LOWEST)
    public static void damage(LivingDamageEvent event){
        if(!event.getEntity().level().isClientSide && event.getEntity() instanceof TemplateMob mob
                && mob.preventPaperFatal(event.getSource(),event.getAmount()))
            event.setAmount(Math.min(event.getAmount(),Math.max(0,mob.getHealth()-1)));
    }
}
