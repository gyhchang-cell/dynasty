package com.grim3212.assorted.damagenumbers;

import com.grim3212.assorted.damagenumbers.client.data.DamageNumbersLanguageProvider;
import com.grim3212.assorted.damagenumbers.client.data.DamageNumbersManualProvider;
import net.minecraft.data.PackOutput;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.ModContainer;
import net.neoforged.fml.common.Mod;
import net.neoforged.neoforge.data.event.GatherDataEvent;

@Mod(Constants.MOD_ID)
public class AssortedDamageNumbersNeoForge {

    /**
     * {@code FMLJavaModLoadingContext} is gone; the mod event bus and the mod container are injected
     * into the {@code @Mod} constructor instead.
     */
    public AssortedDamageNumbersNeoForge(IEventBus modBus, ModContainer modContainer) {
        modBus.addListener(this::gatherClientData);
    }

    /** Client datagen: models, the language file and the manual, written into common for both loaders. */
    private void gatherClientData(final GatherDataEvent.Client event) {
        PackOutput packOutput = event.getGenerator().getPackOutput();

        event.addProvider(new DamageNumbersLanguageProvider(packOutput));
        event.addProvider(new DamageNumbersManualProvider(packOutput));
    }
}
