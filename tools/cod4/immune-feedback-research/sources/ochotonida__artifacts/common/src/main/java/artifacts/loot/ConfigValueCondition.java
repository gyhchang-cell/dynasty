package artifacts.loot;

import artifacts.Artifacts;
import artifacts.config.value.Value;
import artifacts.config.value.ValueTypes;
import artifacts.registry.ModLootConditions;
import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.storage.loot.LootContext;
import net.minecraft.world.level.storage.loot.predicates.LootItemCondition;

public class ConfigValueCondition implements LootItemCondition {

    public static final MapCodec<ConfigValueCondition> CODEC = RecordCodecBuilder.mapCodec(instance -> instance.group(
            ValueTypes.BOOLEAN.codec().fieldOf("value").forGetter(ConfigValueCondition::value)
    ).apply(instance, ConfigValueCondition::new));

    private final Value<Boolean> value;

    protected ConfigValueCondition(Value<Boolean> value) {
        this.value = value;
    }

    protected Value<Boolean> value() {
        return value;
    }

    @Override
    public MapCodec<? extends LootItemCondition> codec() {
        return ModLootConditions.CONFIG_VALUE.value();
    }

    @Override
    public boolean test(LootContext lootContext) {
        return value.get();
    }

    public static Builder canGenerateAsLoot(Item item) {
        Value<Boolean> generatesAsLoot = Artifacts.CONFIG.items.generatesAsLoot(item);
        if (generatesAsLoot == null) {
            throw new IllegalArgumentException();
        }
        return () -> new ConfigValueCondition(generatesAsLoot);
    }
}
