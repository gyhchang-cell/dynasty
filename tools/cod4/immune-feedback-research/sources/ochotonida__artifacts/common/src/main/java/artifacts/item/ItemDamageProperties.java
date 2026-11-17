package artifacts.item;

import artifacts.config.value.Value;
import net.minecraft.tags.TagKey;
import net.minecraft.world.item.Item;

public interface ItemDamageProperties {

    /**
     * Whether this item can be damaged
     */
    boolean canBeDamaged();

    /**
     * Whether this item can be repaired when damaged
     */
    boolean canBeRepaired();

    /**
     * Whether this item should be destroyed when its durability reaches 0
     */
    Value<Boolean> indestructible();

    /**
     * The maximum damage this item can take, must be greater than 0
     */
    int getMaxDamage();

    /**
     * The materials this item can be repaired with
     */
    TagKey<Item> getRepairMaterials();
}
