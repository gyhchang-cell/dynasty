package com.dynasty.client;

import com.dynasty.entity.DynastyEntities;
import com.dynasty.blueprint.elite.*;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Final art selection. Legacy Cod2 registration runs at NORMAL before this listener. */
@Mod.EventBusSubscriber(modid="dynasty",bus=Mod.EventBusSubscriber.Bus.MOD,value=Dist.CLIENT)
public final class BossEightArtBindings {
    private BossEightArtBindings() {}
    @SubscribeEvent(priority=EventPriority.LOWEST)
    public static void register(EntityRenderersEvent.RegisterRenderers event) {
        event.registerEntityRenderer(DynastyEntities.UNDEAD_FIRST_EMPEROR.get(),c ->
                new BossFormsRenderer.Core<>(c,DynastyEntities.UNDEAD_FIRST_EMPEROR.get(),"undead_first_emperor"));
        event.registerEntityRenderer(DynastyEntities.EUNUCH_MASTERMIND.get(),c ->
                new BossFormsRenderer.Core<>(c,DynastyEntities.EUNUCH_MASTERMIND.get(),"eunuch_mastermind"));
        event.registerEntityRenderer(DynastyEntities.REBEL_GENERAL.get(),c ->
                new BossFormsRenderer.Core<>(c,DynastyEntities.REBEL_GENERAL.get(),"rebel_general"));
        event.registerEntityRenderer(EliteContent.HEADLESS.get(),c -> new BossFormsRenderer.Elite<>(c,HeadlessGeneral.ID,2.3f));
        event.registerEntityRenderer(EliteContent.MECHANIST.get(),c -> new BossFormsRenderer.Elite<>(c,Mechanist.ID,2.1f));
        event.registerEntityRenderer(EliteContent.JINWU.get(),c -> new BossFormsRenderer.Elite<>(c,Jinwu.ID,2.0f));
        event.registerEntityRenderer(EliteContent.FOX.get(),c -> new BossFormsRenderer.Elite<>(c,FoxMatron.ID,1.7f));
        event.registerEntityRenderer(EliteContent.HAMMER.get(),c -> new BossFormsRenderer.Elite<>(c,HammerGuardian.ID,2.3f));
        event.registerEntityRenderer(EliteContent.HAMMER_CHAIN.get(),BossFormsRenderer.Chain::new);
    }
}
