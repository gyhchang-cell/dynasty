package com.dynasty.client;

import com.dynasty.entity.DynastyEntities;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Dedicated general art without changing the shared guard/archer character mesh. */
@Mod.EventBusSubscriber(modid="dynasty", bus=Mod.EventBusSubscriber.Bus.MOD, value=Dist.CLIENT)
public final class BossEightArtBindings {
    private BossEightArtBindings() {}

    @SubscribeEvent(priority=EventPriority.LOWEST)
    public static void register(EntityRenderersEvent.RegisterRenderers event) {
        event.registerEntityRenderer(DynastyEntities.REBEL_GENERAL.get(), context ->
                new BossCuboidRenderer<>(context, DynastyEntities.REBEL_GENERAL.get(), "rebel_general"));
    }
}
