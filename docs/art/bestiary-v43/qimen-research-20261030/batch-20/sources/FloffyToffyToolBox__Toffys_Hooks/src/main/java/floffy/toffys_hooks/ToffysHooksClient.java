package floffy.toffys_hooks;

import floffy.toffys_hooks.item.HookItem;
import floffy.toffys_hooks.register.ModEntities;
import floffy.toffys_hooks.register.ModItems;
import floffy.toffys_hooks.render.entity.HookRenderer;
import floffy.toffys_hooks.util.PlayerWithHookData;
import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.rendering.v1.EntityRendererRegistry;
import net.fabricmc.fabric.api.itemgroup.v1.ItemGroupEvents;
import net.minecraft.client.item.ModelPredicateProviderRegistry;
import net.minecraft.entity.player.PlayerEntity;
import net.minecraft.item.ItemGroups;
import net.minecraft.item.Items;
import net.minecraft.util.Identifier;

public class ToffysHooksClient implements ClientModInitializer {

    @Override
    public void onInitializeClient() {

        EntityRendererRegistry.register(ModEntities.HOOK_ENTITY, HookRenderer::new);
        makeHooksItem();

        ItemGroupEvents.modifyEntriesEvent(ItemGroups.TOOLS).register((content) -> {
            content.addAfter(Items.NETHERITE_HOE, ModItems.GRAPPLE_HOOK);
            content.addAfter(Items.NETHERITE_HOE, ModItems.HOOK_AXE);
        });
        ItemGroupEvents.modifyEntriesEvent(ItemGroups.COMBAT).register((content) -> {
            content.addAfter(Items.NETHERITE_BOOTS, ModItems.ICE_SKATES);
        });
        ItemGroupEvents.modifyEntriesEvent(ItemGroups.COMBAT).register((content) -> {
            content.addAfter(Items.NETHERITE_BOOTS, ModItems.CLIMBING_HOOK);
        });
        ItemGroupEvents.modifyEntriesEvent(ItemGroups.INGREDIENTS).register((content) -> {
                content.addAfter(Items.NETHERITE_INGOT ,ModItems.HOOK);
        });
    }
    public void makeHooksItem() {
    ModelPredicateProviderRegistry.register(ModItems.GRAPPLE_HOOK, new Identifier("grappling_hook_extended"), (stack, clientLevel, livingEntity, i) -> {
        if (livingEntity == null) {
            return 0.0F;
        } else {
            boolean bl = livingEntity.getMainHandStack() == stack;
            boolean bl2 = livingEntity.getOffHandStack() == stack;
            if (livingEntity.getActiveItem().getItem() instanceof HookItem) {
                bl2 = false;
            }

            return (bl || bl2) && livingEntity instanceof PlayerEntity && ((PlayerWithHookData)livingEntity).getHook() != null ? 1.0F : 0.0F;
        }
    });
    }
}