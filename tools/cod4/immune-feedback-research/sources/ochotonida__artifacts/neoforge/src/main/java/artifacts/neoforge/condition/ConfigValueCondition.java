package artifacts.neoforge.condition;

import artifacts.Artifacts;
import artifacts.config.value.ConfigValue;
import artifacts.neoforge.registry.ModConditions;
import com.mojang.serialization.MapCodec;
import net.neoforged.neoforge.common.conditions.ICondition;

public record ConfigValueCondition(ConfigValue<Boolean> value) implements ICondition {

    public static final MapCodec<ConfigValueCondition> CODEC = Artifacts.CONFIG.general.codec()
            .xmap(ConfigValueCondition::new, ConfigValueCondition::value).fieldOf("value");

    public MapCodec<? extends ICondition> codec() {
        return ModConditions.CONFIG_VALUE.value();
    }

    @Override
    public boolean test(IContext context) {
        return value.get();
    }
}
