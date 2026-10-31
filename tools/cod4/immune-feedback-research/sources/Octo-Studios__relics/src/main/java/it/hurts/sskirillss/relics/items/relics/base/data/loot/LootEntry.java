package it.hurts.sskirillss.relics.items.relics.base.data.loot;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

@Data
@Builder
@AllArgsConstructor
public class LootEntry {
    @Builder.Default
    private List<String> dimensions;
    @Builder.Default
    private List<String> biomes;
    @Builder.Default
    private List<String> tables;
    @Builder.Default
    private int weight = 1;

    public static class LootEntryBuilder {
        private List<String> dimensions = new ArrayList<>();
        private List<String> biomes = new ArrayList<>();
        private List<String> tables = new ArrayList<>();

        public LootEntryBuilder dimension(String... dimensions) {
            return dimensions(Arrays.asList(dimensions));
        }

        public LootEntryBuilder dimensions(List<String> dimensions) {
            this.dimensions.addAll(dimensions);

            return this;
        }

        public LootEntryBuilder biome(String... biomes) {
            return biomes(Arrays.asList(biomes));
        }

        public LootEntryBuilder biomes(List<String> biomes) {
            this.biomes.addAll(biomes);

            return this;
        }

        public LootEntryBuilder table(String... table) {
            return tables(Arrays.asList(table));
        }

        public LootEntryBuilder tables(List<String> tables) {
            this.tables.addAll(tables);

            return this;
        }
    }
}