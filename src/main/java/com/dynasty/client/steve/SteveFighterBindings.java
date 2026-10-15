package com.dynasty.client.steve;

import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.eventbus.api.*;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.*;

/** Explicit human combatants only. Nonhumans and the three approved royal bosses are excluded. */
@Mod.EventBusSubscriber(modid="dynasty",bus=Mod.EventBusSubscriber.Bus.MOD,value=Dist.CLIENT)
public final class SteveFighterBindings {
    public static final String[] IDS={"archer","imperial_soldier","royal_guard","rebel_soldier","assassin","bandit_thug","night_watchman","zuwu_daoshou","ludun_jiashi","juma_changqiangbing","liannu_zhenzu","tiesuo_chihou","kuijun_sishi","pijia_panjiang_huwei"};
    @SuppressWarnings("unchecked")
    @SubscribeEvent(priority=EventPriority.LOWEST)
    public static void register(EntityRenderersEvent.RegisterRenderers event){
        for(String id:IDS){var type=ForgeRegistries.ENTITY_TYPES.getValue(new ResourceLocation("dynasty",id));if(type==null)throw new IllegalStateException("Missing existing human "+id);event.registerEntityRenderer((EntityType<Mob>)type,c->new SteveFighterRenderer<>(c,id));}
    }
}
