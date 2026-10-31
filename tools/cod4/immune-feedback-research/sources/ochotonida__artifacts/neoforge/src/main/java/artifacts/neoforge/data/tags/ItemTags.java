package artifacts.neoforge.data.tags;

import artifacts.Artifacts;
import artifacts.integration.ModCompat;
import artifacts.registry.ModItems;
import net.minecraft.core.Holder;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.data.PackOutput;
import net.minecraft.data.tags.IntrinsicHolderTagsProvider;
import net.minecraft.data.tags.TagAppender;
import net.minecraft.tags.TagKey;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.Items;
import net.neoforged.neoforge.common.Tags;

import java.util.concurrent.CompletableFuture;

public class ItemTags extends IntrinsicHolderTagsProvider<Item> {

    public static final TagKey<Item> ARTIFACTS = createTag("artifacts");
    public static final TagKey<Item> EQUIPPABLE = createTag("equippable");
    // TODO: consider renaming to `equippable/slot_name`
    public static final TagKey<Item> HEAD_EQUIPPABLE = createTag("slot/head");
    public static final TagKey<Item> FACE_EQUIPPABLE = createTag("slot/face");
    public static final TagKey<Item> NECKLACE_EQUIPPABLE = createTag("slot/necklace");
    public static final TagKey<Item> HANDS_EQUIPPABLE = createTag("slot/hands");
    public static final TagKey<Item> BELT_EQUIPPABLE = createTag("slot/belt");
    public static final TagKey<Item> FEET_EQUIPPABLE = createTag("slot/feet");
    public static final TagKey<Item> ALL_EQUIPPABLE = createTag("slot/all");

    // Probably not needed anymore, but kept for compatibility with origins-legacy
    public static final TagKey<Item> ORIGINS_MEAT = TagKey.create(Registries.ITEM, ModCompat.ORIGINS.id("meat"));
    public static final TagKey<Item> ORIGINS_SHIELDS = TagKey.create(Registries.ITEM, ModCompat.ORIGINS.id("shields"));

    private static TagKey<Item> createTag(String name) {
        return TagKey.create(Registries.ITEM, Artifacts.id(name));
    }

    @SuppressWarnings("deprecation")
    public ItemTags(PackOutput packOutput, CompletableFuture<HolderLookup.Provider> lookupProvider) {
        super(packOutput, Registries.ITEM, lookupProvider, (item) -> item.builtInRegistryHolder().key(), Artifacts.MOD_ID);
    }

    @Override
    protected void addTags(HolderLookup.Provider provider) {
        tag(ARTIFACTS).add(BuiltInRegistries.ITEM.stream()
                .filter(item -> BuiltInRegistries.ITEM.getKey(item).getNamespace().equals(Artifacts.MOD_ID))
                .filter(item -> item != ModItems.MIMIC_SPAWN_EGG.value()).toList().toArray(new Item[]{})
        );
        addSlotTags();
        addRepairMaterialTags();
        addOriginsTags();

        tag(net.minecraft.tags.ItemTags.EQUIPPABLE_ENCHANTABLE).addTag(EQUIPPABLE);
        tag(net.minecraft.tags.ItemTags.VANISHING_ENCHANTABLE).addTag(EQUIPPABLE);

        tag(net.minecraft.tags.ItemTags.PIGLIN_LOVED).add(
                ModItems.GOLDEN_HOOK.value(),
                ModItems.CROSS_NECKLACE.value(),
                ModItems.ANTIDOTE_VESSEL.value(),
                ModItems.UNIVERSAL_ATTRACTOR.value()
        );

        tag(net.minecraft.tags.ItemTags.SPEARS).add(
                ModItems.UMBRELLA.value()
        );
    }

    @SuppressWarnings("unchecked")
    private void addSlotTags() {
        tag(EQUIPPABLE).addTags(
                HEAD_EQUIPPABLE,
                FACE_EQUIPPABLE,
                NECKLACE_EQUIPPABLE,
                HANDS_EQUIPPABLE,
                BELT_EQUIPPABLE,
                FEET_EQUIPPABLE,
                ALL_EQUIPPABLE
        );
        tag(HEAD_EQUIPPABLE).add(
                ModItems.PLASTIC_DRINKING_HAT.value(),
                ModItems.NOVELTY_DRINKING_HAT.value(),
                ModItems.VILLAGER_HAT.value(),
                ModItems.SUPERSTITIOUS_HAT.value(),
                ModItems.COWBOY_HAT.value(),
                ModItems.ANGLERS_HAT.value()
        );
        tag(FACE_EQUIPPABLE).add(
                ModItems.SNORKEL.value(),
                ModItems.NIGHT_VISION_GOGGLES.value()
        );
        tag(NECKLACE_EQUIPPABLE).add(
                ModItems.LUCKY_SCARF.value(),
                ModItems.SCARF_OF_INVISIBILITY.value(),
                ModItems.CROSS_NECKLACE.value(),
                ModItems.PANIC_NECKLACE.value(),
                ModItems.SHOCK_PENDANT.value(),
                ModItems.FLAME_PENDANT.value(),
                ModItems.THORN_PENDANT.value(),
                ModItems.CHARM_OF_SINKING.value(),
                ModItems.CHARM_OF_SHRINKING.value()
        );
        tag(HANDS_EQUIPPABLE).add(
                ModItems.DIGGING_CLAWS.value(),
                ModItems.FERAL_CLAWS.value(),
                ModItems.POWER_GLOVE.value(),
                ModItems.FIRE_GAUNTLET.value(),
                ModItems.POCKET_PISTON.value(),
                ModItems.VAMPIRIC_GLOVE.value(),
                ModItems.GOLDEN_HOOK.value(),
                ModItems.ONION_RING.value(),
                ModItems.PICKAXE_HEATER.value(),
                ModItems.WITHERED_BRACELET.value()
        );
        tag(BELT_EQUIPPABLE).add(
                ModItems.CLOUD_IN_A_BOTTLE.value(),
                ModItems.OBSIDIAN_SKULL.value(),
                ModItems.ANTIDOTE_VESSEL.value(),
                ModItems.UNIVERSAL_ATTRACTOR.value(),
                ModItems.CRYSTAL_HEART.value(),
                ModItems.HELIUM_FLAMINGO.value(),
                ModItems.CHORUS_TOTEM.value(),
                ModItems.WARP_DRIVE.value()
        );
        tag(FEET_EQUIPPABLE).add(
                ModItems.AQUA_DASHERS.value(),
                ModItems.BUNNY_HOPPERS.value(),
                ModItems.KITTY_SLIPPERS.value(),
                ModItems.RUNNING_SHOES.value(),
                ModItems.SNOWSHOES.value(),
                ModItems.STEADFAST_SPIKES.value(),
                ModItems.FLIPPERS.value(),
                ModItems.ROOTED_BOOTS.value(),
                ModItems.STRIDER_SHOES.value()
        );
        tag(ALL_EQUIPPABLE).add(
                ModItems.WHOOPEE_CUSHION.value()
        );
    }

    private void addRepairMaterialTags() {
        repairMaterials(ModItems.ANGLERS_HAT).addTag(Tags.Items.LEATHERS);
        repairMaterials(ModItems.ANTIDOTE_VESSEL).add(Items.GOLD_INGOT);
        repairMaterials(ModItems.AQUA_DASHERS).addTag(Tags.Items.LEATHERS);
        repairMaterials(ModItems.BUNNY_HOPPERS).add(Items.GOLDEN_CARROT);
        repairMaterials(ModItems.CHARM_OF_SHRINKING).add(Items.DIAMOND);
        repairMaterials(ModItems.CHARM_OF_SINKING).add(Items.DIAMOND);
        repairMaterials(ModItems.CLOUD_IN_A_BOTTLE).add(Items.PHANTOM_MEMBRANE);
        repairMaterials(ModItems.COWBOY_HAT).addTag(Tags.Items.LEATHERS);
        repairMaterials(ModItems.CROSS_NECKLACE).add(Items.GOLD_INGOT);
        repairMaterials(ModItems.CRYSTAL_HEART).add(Items.DIAMOND);
        repairMaterials(ModItems.DIGGING_CLAWS).add(Items.IRON_INGOT);
        repairMaterials(ModItems.ETERNAL_STEAK).add(Items.COOKED_BEEF);
        repairMaterials(ModItems.EVERLASTING_BEEF).add(Items.BEEF);
        repairMaterials(ModItems.FERAL_CLAWS).add(Items.EMERALD);
        repairMaterials(ModItems.FIRE_GAUNTLET).add(Items.FIRE_CHARGE);
        repairMaterials(ModItems.FLAME_PENDANT).add(Items.DIAMOND);
        repairMaterials(ModItems.FLIPPERS).add(Items.DRIED_KELP);
        repairMaterials(ModItems.GOLDEN_HOOK).add(Items.GOLD_INGOT);
        repairMaterials(ModItems.HELIUM_FLAMINGO).add(Items.RESIN_CLUMP);
        repairMaterials(ModItems.KITTY_SLIPPERS).addTag(net.minecraft.tags.ItemTags.CAT_FOOD);
        repairMaterials(ModItems.LUCKY_SCARF).addTag(net.minecraft.tags.ItemTags.WOOL);
        repairMaterials(ModItems.NIGHT_VISION_GOGGLES).add(Items.GOLDEN_CARROT);
        repairMaterials(ModItems.NOVELTY_DRINKING_HAT).add(Items.RESIN_CLUMP);
        repairMaterials(ModItems.OBSIDIAN_SKULL).add(Items.OBSIDIAN);
        repairMaterials(ModItems.ONION_RING).add(Items.GOLD_INGOT);
        repairMaterials(ModItems.PANIC_NECKLACE).add(Items.DIAMOND);
        repairMaterials(ModItems.PICKAXE_HEATER).add(Items.FIRE_CHARGE);
        repairMaterials(ModItems.PLASTIC_DRINKING_HAT).add(Items.RESIN_CLUMP);
        repairMaterials(ModItems.POCKET_PISTON).add(Items.PISTON);
        repairMaterials(ModItems.POWER_GLOVE).add(Items.RESIN_CLUMP);
        repairMaterials(ModItems.ROOTED_BOOTS).addTag(Tags.Items.LEATHERS);
        repairMaterials(ModItems.RUNNING_SHOES).addTag(Tags.Items.LEATHERS);
        repairMaterials(ModItems.SCARF_OF_INVISIBILITY).addTag(net.minecraft.tags.ItemTags.WOOL);
        repairMaterials(ModItems.SHOCK_PENDANT).add(Items.DIAMOND);
        repairMaterials(ModItems.SNORKEL).addTag(Tags.Items.GLASS_BLOCKS_COLORLESS);
        repairMaterials(ModItems.SNOWSHOES).add(Items.STICK);
        repairMaterials(ModItems.STEADFAST_SPIKES).addTag(Tags.Items.LEATHERS);
        repairMaterials(ModItems.STRIDER_SHOES).add(Items.BASALT);
        repairMaterials(ModItems.SUPERSTITIOUS_HAT).addTag(Tags.Items.LEATHERS);
        repairMaterials(ModItems.THORN_PENDANT).add(Items.DIAMOND);
        repairMaterials(ModItems.UMBRELLA).addTag(net.minecraft.tags.ItemTags.WOODEN_TOOL_MATERIALS);
        repairMaterials(ModItems.UNIVERSAL_ATTRACTOR).add(Items.GOLD_INGOT);
        repairMaterials(ModItems.VAMPIRIC_GLOVE).addTag(Tags.Items.LEATHERS);
        repairMaterials(ModItems.VILLAGER_HAT).add(Items.HAY_BLOCK);
        repairMaterials(ModItems.WARP_DRIVE).add(Items.ENDER_PEARL);
        repairMaterials(ModItems.WHOOPEE_CUSHION).addTag(Tags.Items.LEATHERS);
        repairMaterials(ModItems.WITHERED_BRACELET).add(Items.BONE);
    }

    private void addOriginsTags() {
        tag(ORIGINS_MEAT).add(
                ModItems.EVERLASTING_BEEF.value(),
                ModItems.ETERNAL_STEAK.value()
        );
        tag(ORIGINS_SHIELDS).add(
                ModItems.UMBRELLA.value()
        );
    }

    private TagAppender<Item, Item> repairMaterials(Holder<Item> holder) {
        return tag(TagKey.create(Registries.ITEM, holder.unwrapKey().orElseThrow().identifier().withPrefix("repairs_")));
    }
}
