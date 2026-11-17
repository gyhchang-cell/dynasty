package artifacts.registry;

import artifacts.world.placement.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.level.levelgen.placement.PlacementModifierType;

import java.util.function.Supplier;

public class ModPlacementModifierTypes {

    public static final Register<PlacementModifierType<?>> PLACEMENT_MODIFIER_TYPES = Register.create(Registries.PLACEMENT_MODIFIER_TYPE);

    public static final RegistryHolder<PlacementModifierType<?>, PlacementModifierType<CeilingHeightFilter>> CEILING_HEIGHT_FILTER = register("ceiling_height_filter", () -> () -> CeilingHeightFilter.CODEC);
    public static final RegistryHolder<PlacementModifierType<?>, PlacementModifierType<CampsiteCountPlacement>> CAMPSITE_COUNT = register("campsite_count", () -> () -> CampsiteCountPlacement.CODEC);
    public static final RegistryHolder<PlacementModifierType<?>, PlacementModifierType<CampsiteHeightRangePlacement>> CAMPSITE_HEIGHT_RANGE = register("campsite_height_range", () -> () -> CampsiteHeightRangePlacement.CODEC);
    public static final RegistryHolder<PlacementModifierType<?>, PlacementModifierType<ConfigValueFilter>> CONFIG_VALUE_FILTER = register("config_value_filter", () -> () -> ConfigValueFilter.CODEC);
    public static final RegistryHolder<PlacementModifierType<?>, PlacementModifierType<SurfaceFlatnessFilter>> SURFACE_FLATNESS_FILTER = register("surface_flatness_filter", () -> () -> SurfaceFlatnessFilter.CODEC);

    private static <T extends PlacementModifierType<?>> RegistryHolder<PlacementModifierType<?>, T> register(String name, Supplier<T> supplier) {
        return PLACEMENT_MODIFIER_TYPES.register(name, supplier);
    }
}
