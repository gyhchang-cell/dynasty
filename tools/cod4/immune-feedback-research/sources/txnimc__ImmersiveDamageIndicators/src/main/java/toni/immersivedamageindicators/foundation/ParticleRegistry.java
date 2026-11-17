package toni.immersivedamageindicators.foundation;


import net.minecraft.core.Registry;
import net.minecraft.core.particles.ParticleType;
import net.minecraft.core.particles.SimpleParticleType;
import net.minecraft.core.registries.BuiltInRegistries;
import toni.immersivedamageindicators.ImmersiveDamageIndicators;
import toni.immersivedamageindicators.particle.DamageParticle;
import toni.lib.utils.VersionUtils;
import net.fabricmc.fabric.api.particle.v1.FabricParticleTypes;

#if fabric
import net.fabricmc.fabric.api.client.particle.v1.ParticleFactoryRegistry;
#endif

#if forge
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.RegistryObject;
#elif neo
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;
#endif

public class ParticleRegistry {
    public static final SimpleParticleType DAMAGE_PARTICLE = FabricParticleTypes.simple(true);

    #if forgelike
    public static final DeferredRegister<ParticleType<?>> PARTICLES = DeferredRegister.create(#if forge ForgeRegistries.PARTICLE_TYPES #else BuiltInRegistries.PARTICLE_TYPE #endif , ImmersiveDamageIndicators.ID);
    public static final #if forge RegistryObject<SimpleParticleType> #else DeferredHolder<ParticleType<?>, SimpleParticleType> #endif DAMAGE_PARTICLE_TYPE = PARTICLES.register("damage", () -> DAMAGE_PARTICLE);
    #endif


    #if fabric
    public static void registerFabric() {
        Registry.register(BuiltInRegistries.PARTICLE_TYPE, VersionUtils.resource(ImmersiveDamageIndicators.ID, "damage"), DAMAGE_PARTICLE);
        ParticleFactoryRegistry.getInstance().register(DAMAGE_PARTICLE, DamageParticle.Factory::new);
    }
    #endif
}
