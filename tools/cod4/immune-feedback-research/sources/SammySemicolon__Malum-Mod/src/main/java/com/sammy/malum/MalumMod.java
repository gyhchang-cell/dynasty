package com.sammy.malum;

import com.sammy.malum.compat.attributelib.*;
import com.sammy.malum.compat.create.*;
import com.sammy.malum.compat.farmersdelight.*;
import com.sammy.malum.config.*;
import com.sammy.malum.registry.common.*;
import com.sammy.malum.registry.common.MalumContent;
import com.sammy.malum.registry.common.entity.*;
import com.sammy.malum.registry.common.sound.*;
import net.minecraft.resources.*;
import net.minecraft.util.*;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.*;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.config.ModConfig;
import net.neoforged.neoforge.common.*;
import org.apache.logging.log4j.*;

import static com.sammy.malum.registry.common.entity.MalumEntityDataSerializers.ENTITY_DATA_SERIALIZERS;
import static com.sammy.malum.registry.common.MalumParticles.*;
import static com.sammy.malum.registry.common.MalumAttachmentTypes.ATTACHMENT_TYPES;
import static com.sammy.malum.registry.common.MalumAttributes.*;
import static com.sammy.malum.registry.common.MalumContainers.*;
import static com.sammy.malum.registry.common.MalumMobEffects.*;
import static com.sammy.malum.registry.common.magic.MalumGeasEffectTypes.*;
import static com.sammy.malum.registry.common.magic.rite.MalumSpiritRiteEffectTypes.*;
import static com.sammy.malum.registry.common.magic.rite.MalumSpiritRiteTypes.*;
import static com.sammy.malum.registry.common.enchantment.ModEnchantmentComponents.ENCHANTMENT_COMPONENTS;
import static com.sammy.malum.registry.common.magic.MalumSpiritTypes.SPIRIT_TYPES;
import static com.sammy.malum.registry.common.MalumWorldEventTypes.WORLD_EVENT_TYPES;
import static com.sammy.malum.registry.common.block.MalumBlockEntities.*;
import static com.sammy.malum.registry.common.item.MalumDataComponents.*;
import static com.sammy.malum.registry.common.MalumCreativeTabs.*;
import static com.sammy.malum.registry.common.recipe.MalumRecipeSerializers.*;
import static com.sammy.malum.registry.common.recipe.MalumRecipeTypes.*;
import static com.sammy.malum.registry.common.worldgen.MalumFeatures.*;
import static com.sammy.malum.registry.common.worldgen.MalumStructureTypes.StructurePieceTypes.STRUCTURE_PIECE_TYPES;
import static com.sammy.malum.registry.common.worldgen.MalumStructureTypes.StructureTypes.STRUCTURE_TYPES;

@SuppressWarnings("unused")
@Mod(MalumMod.MALUM)
public class MalumMod {
    public static final Logger LOGGER = LogManager.getLogger();
    public static final String MALUM = "malum";
    public static final RandomSource RANDOM = RandomSource.create();

    public MalumMod(IEventBus modEventBus, ModContainer modContainer) {
        modContainer.registerConfig(ModConfig.Type.CLIENT, ClientConfig.SPEC);
        modContainer.registerConfig(ModConfig.Type.COMMON, CommonConfig.SPEC);

        NeoForgeMod.enableMergedAttributeTooltips();

        FarmersDelightCompat.init();
        AttributeLibCompat.init();
        CreateCompat.init();


        //Content
        MalumContent.register(modEventBus);
        BLOCK_ENTITY_TYPES.register(modEventBus);
        CONTAINERS.register(modEventBus);
        COMPONENTS.register(modEventBus);
        CREATIVE_MODE_TABS.register(modEventBus);
        ENCHANTMENT_COMPONENTS.register(modEventBus);

        //Entities
        MalumEntityTypes.register(modEventBus);
        ATTACHMENT_TYPES.register(modEventBus);
        ENTITY_DATA_SERIALIZERS.register(modEventBus);

        //Entity-Affecting
        ATTRIBUTES.register(modEventBus);
        MOB_EFFECTS.register(modEventBus);

        //User Experience
        PARTICLES.register(modEventBus);
        MalumSoundEvents.register(modEventBus);

        //Recipes
        RECIPE_TYPES.register(modEventBus);
        RECIPE_SERIALIZERS.register(modEventBus);

        //Worldgen
        FEATURE_TYPES.register(modEventBus);
        STRUCTURE_TYPES.register(modEventBus);
        STRUCTURE_PIECE_TYPES.register(modEventBus);

        //World Event
        WORLD_EVENT_TYPES.register(modEventBus);

        //Malum
        SPIRIT_TYPES.register(modEventBus);
        RITE_EFFECT_TYPES.register(modEventBus);
        GEAS_TYPES.register(modEventBus);

        MalumRegistryAliases.registerAliases();
        MalumParticleEffectTypes.init();
    }

    public static ResourceLocation malumPath(String path) {
        return ResourceLocation.fromNamespaceAndPath(MALUM, path);
    }
}