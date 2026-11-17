package com.grim3212.assorted.doubledoors;

import com.grim3212.assorted.doubledoors.client.data.DoubleDoorsLanguageProvider;
import com.grim3212.assorted.doubledoors.client.data.DoubleDoorsManualProvider;
import com.grim3212.assorted.doubledoors.data.DoubleDoorsBlockTagProvider;
import com.grim3212.assorted.lib.data.ForgeBlockTagProvider;
import net.minecraft.data.PackOutput;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.ModContainer;
import net.neoforged.fml.common.Mod;
import net.neoforged.neoforge.data.event.GatherDataEvent;

@Mod(Constants.MOD_ID)
public class AssortedDoubleDoorsNeoForge {

    /**
     * {@code FMLJavaModLoadingContext} is gone; the mod event bus and the mod container are injected
     * into the {@code @Mod} constructor instead.
     */
    public AssortedDoubleDoorsNeoForge(IEventBus modBus, ModContainer modContainer) {
        modBus.addListener(this::gatherServerData);
        modBus.addListener(this::gatherClientData);

        DoubleDoorsCommonMod.init();
    }

    /**
     * Server datagen. The server and client halves are separate events; if the wrong one runs, the
     * build still succeeds, with "All providers took: 0 ms".
     */
    private void gatherServerData(final GatherDataEvent.Server event) {
        PackOutput packOutput = event.getGenerator().getPackOutput();

        event.addProvider(new ForgeBlockTagProvider(packOutput, event.getWorldLookupProvider(), Constants.MOD_ID, new DoubleDoorsBlockTagProvider(packOutput, event.getWorldLookupProvider())));
    }

    /** Client datagen: models, the language file and the manual, written into common for both loaders. */
    private void gatherClientData(final GatherDataEvent.Client event) {
        PackOutput packOutput = event.getGenerator().getPackOutput();

        event.addProvider(new DoubleDoorsLanguageProvider(packOutput));
        event.addProvider(new DoubleDoorsManualProvider(packOutput));
    }
}
