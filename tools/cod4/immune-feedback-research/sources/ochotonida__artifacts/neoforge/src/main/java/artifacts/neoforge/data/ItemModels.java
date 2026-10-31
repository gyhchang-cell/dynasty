package artifacts.neoforge.data;

import artifacts.Artifacts;
import artifacts.client.item.property.NeedsRepair;
import artifacts.config.ConfigEntryKey;
import artifacts.registry.ModItems;
import net.minecraft.client.data.models.BlockModelGenerators;
import net.minecraft.client.data.models.ItemModelGenerators;
import net.minecraft.client.data.models.ModelProvider;
import net.minecraft.client.data.models.model.ItemModelUtils;
import net.minecraft.client.data.models.model.ModelLocationUtils;
import net.minecraft.client.data.models.model.ModelTemplates;
import net.minecraft.client.renderer.item.ItemModel;
import net.minecraft.client.renderer.item.properties.select.DisplayContext;
import net.minecraft.core.Holder;
import net.minecraft.data.PackOutput;
import net.minecraft.resources.Identifier;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemDisplayContext;

import java.util.List;

public class ItemModels extends ModelProvider {

    public ItemModels(PackOutput packOutput) {
        super(packOutput, Artifacts.MOD_ID);
    }

    @Override
    protected void registerModels(BlockModelGenerators blockModels, ItemModelGenerators itemModels) {
       getKnownItems()
               .map(Holder::value)
               .filter(item -> item != ModItems.MIMIC_SPAWN_EGG.value())
               .filter(item -> item != ModItems.UMBRELLA.value())
               .forEach(item -> {
                   // yikes
                   // noinspection DataFlowIssue,deprecation
                   if (Artifacts.CONFIG.items.getValues().containsKey(new ConfigEntryKey("items", "%s.durability.indestructible".formatted(item.builtInRegistryHolder().getKey().identifier().getPath())))) {
                       Identifier normal = itemModels.createFlatItemModel(item, ModelTemplates.FLAT_ITEM);
                       Identifier broken = itemModels.createFlatItemModel(item, "_broken", ModelTemplates.FLAT_ITEM);
                       itemModels.generateBooleanDispatch(item, new NeedsRepair(), ItemModelUtils.plainModel(broken), ItemModelUtils.plainModel(normal));
                   } else {
                       itemModels.generateFlatItem(item, ModelTemplates.FLAT_ITEM);
                   }
               });

       itemModels.declareCustomModelItem(ModItems.MIMIC_SPAWN_EGG.value());
       createUmbrellaModel(ModItems.UMBRELLA.value(), itemModels);
    }

    private static void createUmbrellaModel(Item item, ItemModelGenerators itemModels) {
        ItemModel.Unbaked inventoryDefault = ItemModelUtils.plainModel(itemModels.createFlatItemModel(item, ModelTemplates.FLAT_ITEM));
        ItemModel.Unbaked inventoryBroken = ItemModelUtils.plainModel(itemModels.createFlatItemModel(item, "_broken", ModelTemplates.FLAT_ITEM));
        ItemModel.Unbaked inventory = ItemModelUtils.conditional(new NeedsRepair(), inventoryBroken, inventoryDefault);
        ItemModel.Unbaked heldNonBlockingModel = ItemModelUtils.plainModel(ModelLocationUtils.getModelLocation(item, "_held"));
        ItemModel.Unbaked heldBlockingModel = ItemModelUtils.plainModel(ModelLocationUtils.getModelLocation(item, "_held_blocking"));
        ItemModel.Unbaked heldModel = ItemModelUtils.conditional(ItemModelUtils.isUsingItem(), heldBlockingModel, heldNonBlockingModel);

        List<ItemDisplayContext> heldDisplayContexts = List.of(
                ItemDisplayContext.FIRST_PERSON_LEFT_HAND,
                ItemDisplayContext.FIRST_PERSON_RIGHT_HAND,
                ItemDisplayContext.THIRD_PERSON_LEFT_HAND,
                ItemDisplayContext.THIRD_PERSON_RIGHT_HAND,
                ItemDisplayContext.HEAD
        );
        itemModels.itemModelOutput.accept(item, ItemModelUtils.select(
                new DisplayContext(), inventory, ItemModelUtils.when(heldDisplayContexts, heldModel)
        ));
    }
}
