package com.dynasty;

import net.minecraft.core.registries.Registries;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;

@GameTestHolder(Dynasty.MODID)
@PrefixGameTestTemplate(false)
public final class CompassBridgeGameTests {
    @GameTest(template="bow_ritual_test",timeoutTicks=30)
    public static void registeredDestinationsWithoutOptionalMods(GameTestHelper h) {
        var registry=h.getLevel().registryAccess();
        h.assertTrue(h.getLevel().getServer().getCommands().getDispatcher().getRoot().getChild("dynasty_find")!=null,
                "Optional navigation command must register without compass jars");
        for(var d:DynastyCompassBridge.DESTINATIONS) {
            var id=new ResourceLocation("dynasty",d.target());
            boolean exists=d.biome()?registry.registryOrThrow(Registries.BIOME).containsKey(id)
                    :registry.registryOrThrow(Registries.STRUCTURE).containsKey(id);
            h.assertTrue(exists,"Unregistered destination: "+id);
            h.assertTrue(h.getLevel().getServer().levelKeys().stream().anyMatch(k->k.location()
                    .equals(new ResourceLocation("dynasty",d.dimension()))),"Missing dimension "+d.dimension());
        }
        h.succeed();
    }
}
