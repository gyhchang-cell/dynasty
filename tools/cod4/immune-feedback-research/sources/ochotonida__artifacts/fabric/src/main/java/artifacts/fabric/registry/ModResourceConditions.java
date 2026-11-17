package artifacts.fabric.registry;

import artifacts.fabric.condition.ConfigValueCondition;
import net.fabricmc.fabric.api.resource.conditions.v1.ResourceConditions;

public class ModResourceConditions {

    public static void register() {
        ResourceConditions.register(ConfigValueCondition.TYPE);
    }
}
