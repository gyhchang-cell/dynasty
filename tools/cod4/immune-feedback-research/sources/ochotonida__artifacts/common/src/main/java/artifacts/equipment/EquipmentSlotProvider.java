package artifacts.equipment;

import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;

import java.util.function.BiFunction;

public interface EquipmentSlotProvider {

    /**
     * Reduces all items equipped in this slot provider into a single value
     * by iteratively applying a combining function, skipping empty slots.
     *
     * @param <ACC> the type of the accumulated result
     * @param entity the entity whose equipment slots will be iterated over
     * @param init the initial accumulator value
     * @param f a function that takes the current accumulated value and the current {@link ItemStack}
     *          and returns the next accumulated value
     * @return the final accumulated value, or {@code init} if no items are equipped on the entity
     */
    <ACC> ACC reduceEquipment(LivingEntity entity, ACC init, BiFunction<EquipmentSlotAccess, ACC, ACC> f);

    /**
     * Equips the item in the first available slot
     *
     * @param entity The entity to equip the item on
     * @param stack The item to equip
     * @param allowSwapping Whether the item can be equipped in a slot that already has an item
     * @return The item that was previously equipped in the chosen slot,
     *         or {@code stack} if no valid slot was found
     */
    ItemStack tryEquip(LivingEntity entity, ItemStack stack, boolean allowSwapping);

}
