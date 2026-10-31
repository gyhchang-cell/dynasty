package artifacts.neoforge.registry;

import artifacts.neoforge.condition.ConfigValueCondition;
import artifacts.registry.Register;
import com.mojang.serialization.MapCodec;
import net.minecraft.core.Holder;
import net.neoforged.neoforge.common.conditions.ICondition;
import net.neoforged.neoforge.registries.NeoForgeRegistries;

public class ModConditions {

    public static final Register<MapCodec<? extends ICondition>> CONDITIONS = Register.create(NeoForgeRegistries.Keys.CONDITION_CODECS);

    public static final Holder<MapCodec<? extends ICondition>> CONFIG_VALUE = CONDITIONS.register("config_value", () -> ConfigValueCondition.CODEC);
}
