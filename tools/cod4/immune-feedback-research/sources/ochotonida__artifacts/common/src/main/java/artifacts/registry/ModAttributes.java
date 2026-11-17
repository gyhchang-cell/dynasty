package artifacts.registry;

import artifacts.platform.PlatformServices;
import net.minecraft.core.Holder;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.RangedAttribute;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Supplier;

public class ModAttributes {

    public static final Register<Attribute> ATTRIBUTES = Register.create(Registries.ATTRIBUTE);

    public static final List<Holder<Attribute>> PLAYER_ATTRIBUTES = new ArrayList<>();
    public static final List<Holder<Attribute>> GENERIC_ATTRIBUTES = new ArrayList<>();

    public static final Holder<Attribute> ENTITY_EXPERIENCE = createPlayerAttribute("entity_experience", 1, 0, 64);
    public static final Holder<Attribute> VILLAGER_REPUTATION = createPlayerAttribute("villager_reputation", 0, 0, 1024);

    public static final Holder<Attribute> ATTACK_BURNING_DURATION = createAttribute("attack_burning_duration", 0, 0, 60);
    public static final Holder<Attribute> DRINKING_SPEED = createAttribute("drinking_speed", 1, 1, Double.MAX_VALUE);
    public static final Holder<Attribute> EATING_SPEED = createAttribute("eating_speed", 1, 1, Double.MAX_VALUE);
    public static final Holder<Attribute> FLATULENCE = createAttribute("flatulence", 0, 0, 1);
    public static final Holder<Attribute> INVINCIBILITY_TICKS = createAttribute("invincibility_ticks", 0, 0, 20 * 60);
    public static final Holder<Attribute> MOUNT_SPEED = createAttribute("mount_speed", 1, 1, 1024);
    public static final Holder<Attribute> MOVEMENT_SPEED_ON_SNOW = createAttribute("movement_speed_on_snow", 1, 0, 1024);
    public static final Holder<Attribute> SLIP_RESISTANCE = createAttribute("slip_resistance", 0, 0, 1);
    public static final Holder<Attribute> SPRINTING_SPEED = createAttribute("sprinting_speed", 1, 1, 1024);
    public static final Holder<Attribute> SPRINTING_STEP_HEIGHT = createAttribute("sprinting_step_height", 0, 0, 10);
    public static final Holder<Attribute> SWIM_SPEED = PlatformServices.getPlatformHelper().getSwimSpeedAttribute();

    public static Holder<Attribute> createPlayerAttribute(String name, double d, double min, double max) {
        Holder<Attribute> attribute = register(name, d, min, max);
        PLAYER_ATTRIBUTES.add(attribute);
        return attribute;
    }

    public static Holder<Attribute> createAttribute(String name, double d, double min, double max) {
        Holder<Attribute> attribute = register(name, d, min, max);
        GENERIC_ATTRIBUTES.add(attribute);
        return attribute;
    }

    private static Holder<Attribute> register(String name, double d, double min, double max) {
        return register(name, () -> new RangedAttribute("attribute.artifacts.%s".formatted(name), d, min, max).setSyncable(true));
    }

    private static Holder<Attribute> register(String name, Supplier<? extends Attribute> supplier) {
        return ATTRIBUTES.register(name, supplier).holder();
    }
}
