package artifacts.component.ability;

import artifacts.config.value.Value;
import artifacts.config.value.ValueTypes;
import com.mojang.serialization.Codec;
import com.mojang.serialization.DataResult;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.item.enchantment.Enchantment;
import net.minecraft.world.item.enchantment.Enchantments;

import java.util.List;

public record EnchantmentLevelModifier(ResourceKey<Enchantment> enchantment, Value<Integer> amount) implements EquipmentAbility {

    public static final List<ResourceKey<Enchantment>> SUPPORTED_ENCHANTMENTS = List.of(
            Enchantments.FORTUNE,
            Enchantments.LOOTING,
            Enchantments.LURE,
            Enchantments.LUCK_OF_THE_SEA
    );

    public static final Codec<EnchantmentLevelModifier> CODEC = RecordCodecBuilder.create(instance -> instance.group(
            ResourceKey.codec(Registries.ENCHANTMENT)
                    .validate(enchantment -> SUPPORTED_ENCHANTMENTS.contains(enchantment)
                            ? DataResult.success(enchantment)
                            : DataResult.error(() -> "Unsupported enchantment: %s".formatted(enchantment.identifier())))
                    .fieldOf("enchantment").forGetter(EnchantmentLevelModifier::enchantment),
            ValueTypes.ENCHANTMENT_LEVEL.codec().optionalFieldOf("level", Value.of(1)).forGetter(EnchantmentLevelModifier::amount)
    ).apply(instance, EnchantmentLevelModifier::new));

    public static final StreamCodec<RegistryFriendlyByteBuf, EnchantmentLevelModifier> STREAM_CODEC = StreamCodec.composite(
            ResourceKey.streamCodec(Registries.ENCHANTMENT),
            EnchantmentLevelModifier::enchantment,
            ValueTypes.ENCHANTMENT_LEVEL.streamCodec(),
            EnchantmentLevelModifier::amount,
            EnchantmentLevelModifier::new
    );

    @Override
    public boolean isNonCosmetic() {
        return amount.get() > 0;
    }

    @Override
    public void addToTooltip(TooltipWriter writer) {
        String enchantmentName = enchantment().identifier().getPath();
        if (amount().get() == 1) {
            writer.add("%s.single_level".formatted(enchantmentName));
        } else {
            writer.add("%s.multiple_levels".formatted(enchantmentName), amount().get());
        }
    }
}
