package artifacts.util;

import artifacts.config.value.Value;
import artifacts.registry.ModDataComponents;
import net.minecraft.world.item.ItemStack;

public class ItemDamageUtil {

    public static boolean isIndestructible(ItemStack stack) {
        Value<Boolean> indestructible = stack.get(ModDataComponents.INDESTRUCTIBLE.get());
        return indestructible != null && indestructible.get();
    }

    public static boolean needsRepair(ItemStack stack) {
        return isIndestructible(stack) && stack.nextDamageWillBreak();
    }

    public static boolean isDisabledOrBroken(ItemStack stack) {
        if (stack.has(ModDataComponents.DISABLED_BY_TOGGLE.get())) {
            return true;
        }
        return ItemDamageUtil.needsRepair(stack);
    }

    // called from ItemStack#processdurabilityChange
    public static int processDurabilityChange(ItemStack stack, int original) {
        // do nothing if the item doesn't have the indestructible component,
        // or if the item is being repaired
        if (!isIndestructible(stack) || original <= 0) {
            return original;
        }
        // don't damage if durability is already at 1 or below
        if (stack.nextDamageWillBreak()) {
            return 0;
        }
        // leave indestructible items at 1 durability (= getMaxDamage - 1)
        int durabilityRemaining = Math.max(0, stack.getMaxDamage() - 1 - stack.getDamageValue());
        return Math.min(original, durabilityRemaining);
    }
}
