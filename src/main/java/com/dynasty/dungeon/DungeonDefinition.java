package com.dynasty.dungeon;

import net.minecraft.resources.ResourceLocation;
import java.util.List;
import java.util.Objects;

/** Placement distances are blocks. Runtime definitions are not the design catalog. */
public record DungeonDefinition(ResourceLocation id, ResourceLocation dimension,
        List<ResourceLocation> biomeTags, String terrainCondition, int spacing, int separation,
        int salt, int minDistanceFromSpawn, String entrancePiece, List<String> piecePool,
        String bossArenaMarker, List<String> eliteMarkers, List<String> mobSpawnMarkers,
        List<String> trapMarkers, List<String> lootMarkers, List<String> shortcutMarkers,
        List<String> secretMarkers, String worldStateKey, List<String> onceLootKeys) {
    public DungeonDefinition {
        Objects.requireNonNull(id); Objects.requireNonNull(dimension);
        if (spacing <= separation || separation < 0 || minDistanceFromSpawn < 0)
            throw new IllegalArgumentException("Invalid dungeon placement distances");
        biomeTags=List.copyOf(biomeTags); piecePool=List.copyOf(piecePool);
        eliteMarkers=List.copyOf(eliteMarkers); mobSpawnMarkers=List.copyOf(mobSpawnMarkers);
        trapMarkers=List.copyOf(trapMarkers); lootMarkers=List.copyOf(lootMarkers);
        shortcutMarkers=List.copyOf(shortcutMarkers); secretMarkers=List.copyOf(secretMarkers);
        onceLootKeys=List.copyOf(onceLootKeys);
    }

    public static final DungeonDefinition PROBE = new DungeonDefinition(
        new ResourceLocation("dynasty:dungeon_framework_probe"),new ResourceLocation("minecraft:overworld"),
        List.of(),"ADMIN_ONLY; no natural StructureSet",8192,4096,106001,0,
        "entrance",List.of("entrance","trial","treasury"),"NOT_A_BOSS_ROOM",
        List.of(),List.of(),List.of("poison_arrow"),List.of("supplies"),
        List.of("trial_door"),List.of(),"cod2_probe",List.of("test_world_reward"));
    public static final DungeonDefinition CHENSHA = new DungeonDefinition(
        new ResourceLocation("dynasty:chensha_xuangong"),new ResourceLocation("minecraft:overworld"),
        List.of(new ResourceLocation("dynasty:dungeons/chensha")),"Dry desert/badlands; underground; bounded relief",8192,4096,106101,2500,
        "sealed_mound",List.of("shendao","nine_chambers","imperial_vault","mercury_lock","artisan_secret","lift_shaft"),
        "zhaoming_emperor",List.of("pilin_zhijinwu","juchui_jinjia_lishi"),List.of("zuwu_daoshou","juma_changqiangbing","shashui_funigui","muxue_feilu"),
        List.of("poison_arrow","resettable_floor","mercury_lock"),List.of("artisan_supplies","imperial_coffin"),
        List.of("return_lift"),List.of("artisan_secret"),"cod2_chensha_v1",List.of("chensha_first_kill"));
}
