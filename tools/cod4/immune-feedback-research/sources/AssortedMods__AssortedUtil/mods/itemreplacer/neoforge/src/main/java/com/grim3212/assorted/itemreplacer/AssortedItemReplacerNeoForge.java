package com.grim3212.assorted.itemreplacer;

import com.grim3212.assorted.itemreplacer.client.data.ItemReplacerLanguageProvider;
import com.grim3212.assorted.itemreplacer.client.data.ItemReplacerManualProvider;
import net.minecraft.data.PackOutput;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.ModContainer;
import net.neoforged.fml.common.Mod;
import net.neoforged.neoforge.data.event.GatherDataEvent;

@Mod(Constants.MOD_ID)
public class AssortedItemReplacerNeoForge {

    /**
     * {@code FMLJavaModLoadingContext} is gone; the mod event bus and the mod container are injected
     * into the {@code @Mod} constructor instead.
     */
    public AssortedItemReplacerNeoForge(IEventBus modBus, ModContainer modContainer) {
        modBus.addListener(this::gatherClientData);
    }

    /** Client datagen: models, the language file and the manual, written into common for both loaders. */
    private void gatherClientData(final GatherDataEvent.Client event) {
        PackOutput packOutput = event.getGenerator().getPackOutput();

        event.addProvider(new ItemReplacerLanguageProvider(packOutput));
        event.addProvider(new ItemReplacerManualProvider(packOutput));
    }
}
