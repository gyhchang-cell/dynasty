package artifacts.integration.origins;

import net.minecraft.world.entity.LivingEntity;

public class OriginsCompat {

    public static boolean hasWaterBreathing(LivingEntity entity) {
        return false;
        /* FIXME: Origins 26.1+
        return PowerHolderComponent.hasPowerType(entity, WaterBreathingPowerType.class);
        */
    }
}
