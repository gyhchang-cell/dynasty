package artifacts.integration.accessories;

public class AccessoriesCompat {

    public static void setup() {
        /* FIXME: accessories 26.1+
        EquipmentSlotManager.register(new AccessoriesSlotProvider());

        AccessoryChangeCallback.EVENT.register(
                (prevStack, currentStack, slotReference, _) -> ArtifactHooks.onItemChanged(slotReference.entity(), prevStack, currentStack)
        );

        OnDropCallback.EVENT.register(AccessoriesCompat::onDropItem);
    }

    private static DropRule onDropItem(DropRule dropRule, ItemStack stack, SlotReference reference, DamageSource damageSource) {
        if (dropRule == DropRule.DEFAULT && DamageSourceHelper.shouldDestroyWornItemOnDeath(reference.entity(), stack)) {
            return DropRule.DESTROY;
        }
        return dropRule;
        */
    }
}
