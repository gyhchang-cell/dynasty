package artifacts.loot;

import artifacts.Artifacts;
import artifacts.registry.ModLootConditions;
import com.mojang.serialization.Codec;
import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.minecraft.world.level.storage.loot.LootContext;
import net.minecraft.world.level.storage.loot.predicates.LootItemCondition;

public record ArtifactRarityAdjustedChance(float defaultProbability) implements LootItemCondition {

    public static final MapCodec<ArtifactRarityAdjustedChance> CODEC = RecordCodecBuilder.mapCodec(instance ->
            instance.group(Codec.FLOAT.fieldOf("default_probability").forGetter(ArtifactRarityAdjustedChance::defaultProbability))
                    .apply(instance, ArtifactRarityAdjustedChance::new)
    );

    @Override
    public MapCodec<? extends LootItemCondition> codec() {
        return ModLootConditions.ARTIFACT_RARITY_ADJUSTED_CHANCE.value();
    }

    @Override
    public boolean test(LootContext context) {
        if (Artifacts.CONFIG.general.artifactRarity.get() > 9999) {
            return false;
        }
        float r = (float) (double) Artifacts.CONFIG.general.artifactRarity.get();
        float p = defaultProbability;
        float adjustedProbability = p / (p + r - r * p);
        return context.getRandom().nextFloat() < adjustedProbability;
    }

    public static LootItemCondition.Builder adjustedChance(float probability) {
        return () -> new ArtifactRarityAdjustedChance(probability);
    }
}
