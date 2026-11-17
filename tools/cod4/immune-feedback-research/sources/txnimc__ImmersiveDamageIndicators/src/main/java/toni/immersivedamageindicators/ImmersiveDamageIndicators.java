package toni.immersivedamageindicators;

import net.fabricmc.fabric.api.client.particle.v1.ParticleFactoryRegistry;
import net.fabricmc.fabric.api.event.client.player.ClientPreAttackCallback;
import net.minecraft.core.Registry;
import net.minecraft.core.particles.SimpleParticleType;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.block.Blocks;
import toni.immersivedamageindicators.api.CreateDamageIndicator;
import toni.immersivedamageindicators.foundation.ParticleRegistry;
import toni.immersivedamageindicators.foundation.config.AllConfigs;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import net.fabricmc.fabric.api.particle.v1.FabricParticleTypes;

import toni.immersivedamageindicators.particle.DamageParticle;
import toni.lib.utils.VersionUtils;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

#if FABRIC
    import net.fabricmc.api.ClientModInitializer;
    import net.fabricmc.api.ModInitializer;
    #if mc >= 215
    import fuzs.forgeconfigapiport.fabric.api.v5.ConfigRegistry;
    import fuzs.forgeconfigapiport.fabric.api.v5.client.ConfigScreenFactoryRegistry;
    import net.neoforged.neoforge.client.gui.ConfigurationScreen;
    #elif after_21_1
    import fuzs.forgeconfigapiport.fabric.api.neoforge.v4.NeoForgeConfigRegistry;
    import fuzs.forgeconfigapiport.fabric.api.neoforge.v4.client.ConfigScreenFactoryRegistry;
    import net.neoforged.neoforge.client.gui.ConfigurationScreen;
    #endif

    #if current_20_1
    import fuzs.forgeconfigapiport.api.config.v2.ForgeConfigRegistry;
    #endif
#endif

#if FORGE
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.common.Mod.EventBusSubscriber;
import net.minecraftforge.fml.ModLoadingContext;
import net.minecraftforge.fml.event.lifecycle.FMLClientSetupEvent;
import net.minecraftforge.fml.event.lifecycle.FMLCommonSetupEvent;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
#endif


#if NEO
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.event.lifecycle.FMLClientSetupEvent;
import net.neoforged.fml.event.lifecycle.FMLCommonSetupEvent;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.ModContainer;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.client.gui.IConfigScreenFactory;
import net.neoforged.neoforge.client.gui.ConfigurationScreen;
#endif


#if FORGELIKE
@Mod("immersivedamageindicators")
#endif
public class ImmersiveDamageIndicators #if FABRIC implements ModInitializer, ClientModInitializer #endif
{
    public static final String MODNAME = "Immersive Damage Indicators";
    public static final String ID = "immersivedamageindicators";
    public static final Logger LOGGER = LogManager.getLogger(MODNAME);
    public static final Map<UUID, Float> LAST_ATTACK_SWING = new HashMap<>();

    public ImmersiveDamageIndicators(#if NEO IEventBus modEventBus, ModContainer modContainer #endif) {
        #if FORGE
        var context = FMLJavaModLoadingContext.get();
        var modEventBus = context.getModEventBus();
        #endif

        #if FORGELIKE
        modEventBus.addListener(this::commonSetup);
        modEventBus.addListener(this::clientSetup);

        AllConfigs.register((type, spec) -> {
            #if FORGE
            ModLoadingContext.get().registerConfig(type, spec);
            #elif NEO
            modContainer.registerConfig(type, spec);
            //modContainer.registerExtensionPoint(IConfigScreenFactory.class, ConfigurationScreen::new);
            #endif
        });
        #endif
    }


    #if FABRIC @Override #endif
    public void onInitialize() {
        #if FABRIC
            AllConfigs.register((type, spec) -> {
                #if mc >= 215
                ConfigRegistry.INSTANCE.register(ImmersiveDamageIndicators.ID, type, spec);
                #elif mc >= 211
                NeoForgeConfigRegistry.INSTANCE.register(ImmersiveDamageIndicators.ID, type, spec);
                #else
                ForgeConfigRegistry.INSTANCE.register(ImmersiveDamageIndicators.ID, type, spec);
                #endif
            });
        #endif
    }

    #if FABRIC @Override #endif
    public void onInitializeClient() {
        #if FABRIC
            ParticleRegistry.registerFabric();

            #if AFTER_21_1
            ConfigScreenFactoryRegistry.INSTANCE.register(ImmersiveDamageIndicators.ID, ConfigurationScreen::new);
            #endif
        #endif
    }

    // Forg event stubs to call the Fabric initialize methods, and set up cloth config screen
    #if FORGELIKE
    public void commonSetup(FMLCommonSetupEvent event) { onInitialize(); }
    public void clientSetup(FMLClientSetupEvent event) { onInitializeClient(); }
    #endif
}
