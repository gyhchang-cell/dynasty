package artifacts.component.ability;

import artifacts.equipment.EquipmentSlotAccess;
import net.minecraft.world.entity.LivingEntity;

public interface AbilityTicker<ABILITY extends EquipmentAbility> {

    void wornTick(ABILITY ability, EquipmentSlotAccess slotAccess, LivingEntity entity, boolean isOnCooldown, boolean isDisabled);

    default void onUnequip(ABILITY ability, LivingEntity entity) {

    }
}
