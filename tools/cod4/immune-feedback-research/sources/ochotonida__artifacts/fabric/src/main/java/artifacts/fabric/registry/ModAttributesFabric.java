package artifacts.fabric.registry;

import artifacts.registry.ModAttributes;
import net.minecraft.core.Holder;
import net.minecraft.world.entity.ai.attributes.Attribute;

public class ModAttributesFabric {

    public static final Holder<Attribute> SWIM_SPEED = ModAttributes.createAttribute("swim_speed", 1, 0, 1024);
}
