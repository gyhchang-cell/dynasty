package artifacts.registry;

import artifacts.Artifacts;
import artifacts.entity.MimicEntity;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;

import java.util.function.BiConsumer;

public class ModEntityTypes {

    public static final Register<EntityType<?>> ENTITY_TYPES = Register.create(Registries.ENTITY_TYPE);

    public static final RegistryHolder<EntityType<?>, EntityType<MimicEntity>> MIMIC = ENTITY_TYPES.register("mimic",
            () -> EntityType.Builder.of(MimicEntity::new, MobCategory.MISC)
                    .sized(14 / 16F, 14 / 16F)
                    .clientTrackingRange(8)
                    .build(ResourceKey.create(Registries.ENTITY_TYPE, Artifacts.id("mimic")))
    );

    public static void registerMobAttributes(BiConsumer<EntityType<? extends LivingEntity>, AttributeSupplier> consumer) {
        consumer.accept(ModEntityTypes.MIMIC.get(), MimicEntity.createMobAttributes().build());
    }
}
