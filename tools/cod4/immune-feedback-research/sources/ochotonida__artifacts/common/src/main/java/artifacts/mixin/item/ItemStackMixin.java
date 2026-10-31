package artifacts.mixin.item;

import artifacts.component.itemdamage.StoredComponents;
import artifacts.registry.ModDataComponents;
import artifacts.util.ItemDamageUtil;
import artifacts.util.TooltipHelper;
import com.llamalad7.mixinextras.injector.ModifyReturnValue;
import net.minecraft.core.component.DataComponentType;
import net.minecraft.core.component.DataComponents;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.TooltipDisplay;
import org.jspecify.annotations.Nullable;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

import java.util.Set;
import java.util.function.Consumer;

@Mixin(ItemStack.class)
public abstract class ItemStackMixin {

    @ModifyReturnValue(method = "processDurabilityChange", at = @At(value = "RETURN"))
    private int processDurabilityChange(int original) {
        return ItemDamageUtil.processDurabilityChange((ItemStack) (Object) this, original);
    }

    @Inject(method = "addDetailsToTooltip", at = @At(value = "INVOKE", target = "Lnet/minecraft/world/item/Item;appendHoverText(Lnet/minecraft/world/item/ItemStack;Lnet/minecraft/world/item/Item$TooltipContext;Lnet/minecraft/world/item/component/TooltipDisplay;Ljava/util/function/Consumer;Lnet/minecraft/world/item/TooltipFlag;)V"))
    private void getTooltipLines(Item.TooltipContext context, TooltipDisplay display, @Nullable Player player, TooltipFlag tooltipFlag, Consumer<Component> builder, CallbackInfo ci) {
        ItemStack stack = (ItemStack) (Object) this;
        TooltipHelper.addAbilityDescriptions(builder, stack, context, display, tooltipFlag, player);
    }

    /*
     * On NeoForge the call to addAttributeTooltips is replaced with a call to AttributeUtil.addAttributeTooltips, this is only injected on Fabric.
     * An AddAttributeTooltipsEvent listener calls TooltipHelper.addAttributeTooltips on NeoForge
     */
    @Inject(method = "addDetailsToTooltip", require = 0, at = @At(value = "INVOKE", shift = At.Shift.AFTER, target = "Lnet/minecraft/world/item/ItemStack;addAttributeTooltips(Ljava/util/function/Consumer;Lnet/minecraft/world/item/component/TooltipDisplay;Lnet/minecraft/world/entity/player/Player;)V"))
    private void addAttributeTooltips(Item.TooltipContext context, TooltipDisplay display, @Nullable Player player, TooltipFlag tooltipFlag, Consumer<Component> builder, CallbackInfo ci) {
        TooltipHelper.addAttributeTooltips(builder, (ItemStack) (Object) this, context, display);
    }

    @Inject(method = "setDamageValue", at = @At(value = "RETURN"))
    private void onItemDamageUpdated(int value, CallbackInfo ci) {
        ItemStack stack = (ItemStack) (Object) this;
        // Always restore broken components first, even if the item is already broken
        // This prevents previously broken components from being overridden,
        // even if for some reason the item takes damage when already broken
        // FIXME: broken items don't regain their components when
        //  `can_be_damaged` or `indestructible` are reset to to false in the config
        artifacts$restoreBrokenComponents(stack);
        if (ItemDamageUtil.isIndestructible(stack) && stack.nextDamageWillBreak()) {
            artifacts$disableComponentsOnItemBroken(stack);
        }
    }

    @Inject(method = "applyDamage", at = @At(value = "RETURN"))
    private void onItemDamaged(int newDamage, @Nullable ServerPlayer player, Consumer<Item> onBreak, CallbackInfo ci) {
        ItemStack self = (ItemStack) (Object) this;
        if (ItemDamageUtil.needsRepair(self)) {
            onBreak.accept(self.getItem());
        }
    }

    @Unique
    private void artifacts$disableComponentsOnItemBroken(ItemStack stack) {
        // TODO: consider moving this into a separate component
        Set<DataComponentType<?>> types = Set.of(
                DataComponents.CONSUMABLE,
                DataComponents.BLOCKS_ATTACKS
        );
        StoredComponents brokenComponents = StoredComponents.from(stack, types);
        stack.set(ModDataComponents.BROKEN_COMPONENTS.get(), brokenComponents);
        for (DataComponentType<?> type : types) {
            stack.remove(type);
        }
    }

    @Unique
    private void artifacts$restoreBrokenComponents(ItemStack stack) {
        StoredComponents storedComponents = stack.remove(ModDataComponents.BROKEN_COMPONENTS.get());
        if (storedComponents != null) {
            storedComponents.applyTo(stack);
        }
    }
}
