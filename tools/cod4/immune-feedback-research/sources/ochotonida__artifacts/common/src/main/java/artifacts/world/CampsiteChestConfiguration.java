package artifacts.world;

import artifacts.Artifacts;
import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.level.storage.loot.LootTable;

import java.util.Optional;

public record CampsiteChestConfiguration(
        Optional<Double> mimicChance,
        double trappedChestChance,
        Optional<ResourceKey<LootTable>> chestLootTable
) {

    public static final Codec<CampsiteChestConfiguration> CODEC = RecordCodecBuilder.create(instance -> instance.group(
            Codec.doubleRange(0, 1).optionalFieldOf("mimic_chance").forGetter(CampsiteChestConfiguration::mimicChance),
            Codec.doubleRange(0, 1).optionalFieldOf("trapped_chest_chance", 0D).forGetter(CampsiteChestConfiguration::trappedChestChance),
            ResourceKey.codec(Registries.LOOT_TABLE).optionalFieldOf("chest_loot_table").forGetter(CampsiteChestConfiguration::chestLootTable)
    ).apply(instance, CampsiteChestConfiguration::new));

    public double getMimicChance() {
        return mimicChance().orElse(Artifacts.CONFIG.general.campsite.mimicChance.get());
    }
}
