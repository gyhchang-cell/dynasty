package it.hurts.sskirillss.relics.items.relics.base.data.loot.misc;

import it.hurts.sskirillss.relics.items.relics.base.data.loot.LootEntry;

public class LootEntries {
    public static final LootEntry WILDCARD = LootEntry.builder()
            .dimension(".*")
            .biome(".*")
            .table("[\\w]+:chests\\/[\\w_\\/]*[\\w]+[\\w_\\/]*")
            .weight(100)
            .build();

    public static final LootEntry OVERWORLD = LootEntry.builder()
            .dimension("minecraft:overworld")
            .biome(".*")
            .table("[\\w]+:chests\\/[\\w_\\/]*[\\w]+[\\w_\\/]*")
            .weight(100)
            .build();

    public static final LootEntry NETHER_LIKE = LootEntry.builder()
            .dimension(".*")
            .biome(".*")
            .table("[\\w]+:chests\\/[\\w_\\/]*(nether|infern|hell|chasm|lava|magma|m[eo]lt|fire|flame|blaze|ember|pyre)[\\w_\\/]*",
                    "minecraft:chests/ruined_portal")
            .weight(500)
            .build();

    public static final LootEntry THE_NETHER = LootEntry.builder()
            .dimension("minecraft:the_nether")
            .biome(".*")
            .table("[\\w]+:chests\\/[\\w_\\/]*[\\w]+[\\w_\\/]*")
            .weight(100)
            .build();

    public static final LootEntry END_LIKE = LootEntry.builder()
            .dimension(".*")
            .biome(".*")
            .table("[\\w]+:chests\\/[\\w_\\/]*(end|stronghold)[\\w_\\/]*")
            .weight(500)
            .build();

    public static final LootEntry THE_END = LootEntry.builder()
            .dimension("minecraft:the_end")
            .biome(".*")
            .table("[\\w]+:chests\\/[\\w_\\/]*[\\w]+[\\w_\\/]*")
            .weight(100)
            .build();

    public static final LootEntry DESERT = LootEntry.builder()
            .dimension(".*")
            .biome("[\\w]+:.*(desert|badlands|outback)[\\w_\\/]*")
            .table("[\\w]+:chests\\/[\\w_\\/]*[\\w]+[\\w_\\/]*")
            .weight(300)
            .build();

    public static final LootEntry SAVANNA = LootEntry.builder()
            .dimension(".*")
            .biome("[\\w]+:.*(savanna|steppe|prairie)[\\w_\\/]*")
            .table("[\\w]+:chests\\/[\\w_\\/]*[\\w]+[\\w_\\/]*")
            .weight(300)
            .build();

    public static final LootEntry FOREST = LootEntry.builder()
            .dimension(".*")
            .biome("[\\w]+:.*(forest|wood|timberland|silva|wildwood|garden|grove)[\\w_\\/]*")
            .table("[\\w]+:chests\\/[\\w_\\/]*[\\w]+[\\w_\\/]*")
            .weight(300)
            .build();

    public static final LootEntry MOUNTAIN = LootEntry.builder()
            .dimension(".*")
            .biome("[\\w]+:.*(mountain|peak|summit|ridge|alp|highland|hill|cliff|height)[\\w_\\/]*")
            .table("[\\w]+:chests\\/[\\w_\\/]*[\\w]+[\\w_\\/]*")
            .weight(300)
            .build();

    public static final LootEntry AQUATIC = LootEntry.builder()
            .dimension(".*")
            .biome("[\\w]+:.*(ocean|sea|marine|pelagic|beach|shore|coast|strand|sandbank|river|stream|creek|brook|water|tributary)[\\w_\\/]*")
            .table("[\\w]+:chests\\/[\\w_\\/]*[\\w]+[\\w_\\/]*")
            .weight(300)
            .build();

    public static final LootEntry TROPIC = LootEntry.builder()
            .dimension(".*")
            .biome("[\\w]+:.*(jungle|rainforest|tropic|wildwood|thicket|boscage|humid|bamboo)[\\w_\\/]*")
            .table("[\\w]+:chests\\/[\\w_\\/]*[\\w]+[\\w_\\/]*")
            .weight(300)
            .build();

    public static final LootEntry TAIGA = LootEntry.builder()
            .dimension(".*")
            .biome("[\\w]+:.*(taiga|pine)[\\w_\\/]*")
            .table("[\\w]+:chests\\/[\\w_\\/]*[\\w]+[\\w_\\/]*")
            .weight(300)
            .build();

    public static final LootEntry PLAINS = LootEntry.builder()
            .dimension(".*")
            .biome("[\\w]+:.*(plain|fiel|prairie|steppe|meadow|flat|grass|bush)[\\w_\\/]*")
            .table("[\\w]+:chests\\/[\\w_\\/]*[\\w]+[\\w_\\/]*")
            .weight(300)
            .build();

    public static final LootEntry SWAMP = LootEntry.builder()
            .dimension(".*")
            .biome("[\\w]+:.*(swamp|marsh|bog|fen|wetland|quagmire|morass|slough|bayou|mud)[\\w_\\/]*")
            .table("[\\w]+:chests\\/[\\w_\\/]*[\\w]+[\\w_\\/]*")
            .weight(300)
            .build();

    public static final LootEntry FROST = LootEntry.builder()
            .dimension(".*")
            .biome("[\\w]+:.*(fro[sz]|ic[ey]|glac|cold|snow)[\\w_\\/]*")
            .table("[\\w]+:chests\\/[\\w_\\/]*[\\w]+[\\w_\\/]*")
            .weight(300)
            .build();

    public static final LootEntry CAVE = LootEntry.builder()
            .dimension(".*")
            .biome("[\\w]+:.*(cave|cavern|grotto|hollow|den|chamber|crypt|subterranean)[\\w_\\/]*")
            .table("[\\w]+:chests\\/[\\w_\\/]*[\\w]+[\\w_\\/]*")
            .weight(300)
            .build();

    public static final LootEntry SCULK = LootEntry.builder()
            .dimension(".*")
            .biome("[\\w]+:.*(sculk|warden)[\\w_\\/]*",
                    "minecraft:deep_dark")
            .table("[\\w]+:chests\\/[\\w_\\/]*[\\w]+[\\w_\\/]*")
            .weight(500)
            .build();

    public static final LootEntry VILLAGE = LootEntry.builder()
            .dimension(".*")
            .biome(".*")
            .table("[\\w]+:chests\\/[\\w_\\/]*(village|pillage)[\\w_\\/]*")
            .weight(500)
            .build();

    public static final LootEntry BASTION = LootEntry.builder()
            .dimension(".*")
            .biome(".*")
            .table("[\\w]+:chests\\/[\\w_\\/]*(bastion|piglin)[\\w_\\/]*")
            .weight(500)
            .build();

    public static final LootEntry MINESHAFT = LootEntry.builder()
            .dimension(".*")
            .biome(".*")
            .table("[\\w]+:chests\\/[\\w_\\/]*(mine)[\\w_\\/]*")
            .weight(500)
            .build();
}