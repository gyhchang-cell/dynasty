package com.dynasty.blueprint;

import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.Level;
import java.util.List;

/** Runtime locations for the validated-first batch; the remaining blueprint stays in the audit catalog. */
public final class TemplateContentDefinitions {
    public record Spawn(String id, ResourceKey<Level> dimension, List<ResourceLocation> biomeTags,
            List<ResourceLocation> structureTags, int minY, int maxY, int minLight, int maxLight,
            String timeWindow, String weatherCondition, int spawnWeight, int minGroup, int maxGroup,
            int localCap, String spawnReason, String specialCondition, String despawnPolicy) {}
    private static ResourceLocation tag(String id) {return new ResourceLocation(id);}
    public static final List<Spawn> ALL = List.of(
        new Spawn("zuwu_daoshou",Level.OVERWORLD,List.of(),List.of(tag("dynasty:blueprint/ritual_sites")),
            -32,220,0,15,"ALL; night weight 10 instead of 8","ANY",8,2,2,2,"STRUCTURE_MARKER",
            "two swordsmen guarding an existing ritual priest; safe solid floor","PERSISTENT_MARKER; 10-minute cooldown after all killed"),
        new Spawn("ludun_jiashi",Level.OVERWORLD,List.of(),List.of(tag("dynasty:blueprint/military_sites")),
            -32,220,0,15,"ALL","ANY",1,1,1,1,"STRUCTURE_MARKER",
            "one shield per military marker; protects ranged/support","PERSISTENT_MARKER; 10-minute cooldown after all killed"),
        new Spawn("fufa_jijiu",Level.OVERWORLD,List.of(),List.of(tag("dynasty:blueprint/ritual_sites")),
            -40,240,0,15,"ALL; night or light <=7 weight 4 instead of 2","ANY",2,1,1,1,"STRUCTURE_MARKER",
            "existing star altar/herbal retreat; one priest with two swordsmen","PERSISTENT_MARKER; 10-minute cooldown after all killed"),
        new Spawn("shanjing_shanxiao",Level.OVERWORLD,List.of(tag("dynasty:blueprint/shanxiao_habitat")),List.of(),
            50,240,0,15,"ALL; daylight chance one quarter","ANY",4,1,3,3,"NATURAL_ECOLOGY",
            "forest/mountain, solid ground, collision-free, max3 within24 blocks","VANILLA_DISTANCE_DESPAWN"),
        new Spawn("juma_changqiangbing",Level.OVERWORLD,List.of(),List.of(tag("dynasty:blueprint/military_sites")),
            -32,220,0,15,"ALL","ANY",1,1,1,1,"STRUCTURE_MARKER","one spearman behind the gate's shield squad","PERSISTENT_MARKER"),
        new Spawn("liannu_zhenzu",Level.OVERWORLD,List.of(),List.of(tag("dynasty:blueprint/military_sites")),
            -32,220,0,15,"ALL","ANY",1,2,2,2,"STRUCTURE_MARKER","two crossbows per gate defensive squad","PERSISTENT_MARKER"),
        new Spawn("tiesuo_chihou",Level.OVERWORLD,List.of(tag("dynasty:blueprint/shanxiao_habitat")),List.of(),
            60,220,0,7,"NIGHT","ANY",2,1,2,2,"NATURAL_ECOLOGY","forest/mountain; at most two within32; no cave below height60","VANILLA_DISTANCE_DESPAWN"),
        new Spawn("kuijun_sishi",Level.OVERWORLD,List.of(),List.of(tag("dynasty:blueprint/battlefields")),
            -32,220,0,7,"NIGHT","ANY",1,3,3,3,"STRUCTURE_MARKER","three powder units in the ruined battlefield squad; never ordinary natural spawning","ENCOUNTER_MEMBERSHIP"),
        new Spawn("zhenwang_zhangqiguan",Level.OVERWORLD,List.of(),List.of(tag("dynasty:blueprint/battlefields")),
            -32,220,0,7,"NIGHT","ANY",1,1,1,1,"STRUCTURE_MARKER","one banner per battlefield encounter; never ordinary natural spawning","ENCOUNTER_MEMBERSHIP"),
        new Spawn("pijia_panjiang_huwei",Level.OVERWORLD,List.of(),List.of(tag("dynasty:blueprint/rebel_guard_sites")),
            -32,300,0,15,"ALL","ANY",1,1,2,2,"STRUCTURE_MARKER","two authored upper-gate positions; shared 32-block cap; no ordinary biome spawn","PERSISTENT_MARKER; 10-minute cooldown after all killed"),
        new Spawn("yinbing_guizu",Level.OVERWORLD,List.of(),List.of(tag("dynasty:blueprint/ghost_sites")),
            -32,220,0,7,"NIGHT OR LOW LIGHT","ANY",2,2,5,5,"STRUCTURE_MARKER","ruined battlefield; stable group size per structure; maximum five spirits within32","PERSISTENT_MARKER; 10-minute cooldown after all killed"),
        new Spawn("shibian_lishi",Level.OVERWORLD,List.of(),List.of(tag("dynasty:blueprint/corpse_sites")),
            -63,48,0,15,"ALL","ANY",1,1,2,2,"STRUCTURE_MARKER","authored imperial tomb antechamber; no ordinary cave spawning","PERSISTENT_MARKER; 10-minute cooldown after all killed"),
        new Spawn("fuhun_baibu_tongzi",Level.OVERWORLD,List.of(),List.of(tag("dynasty:blueprint/shroud_child_sites")),
            -63,64,0,15,"NIGHT OR LOW LIGHT","ANY",1,1,1,1,"STRUCTURE_MARKER","authored imperial tomb west gallery; night or light<=7; maximum one within32","PERSISTENT_MARKER; 10-minute cooldown after all killed"),
        new Spawn("zhiren_jianke",Level.OVERWORLD,List.of(),List.of(tag("dynasty:blueprint/paper_swordsman_sites")),
            -63,64,0,15,"ALL","ANY",1,1,3,3,"STRUCTURE_MARKER","authored imperial tomb courtyard; maximum three within32; no biome spawning","PERSISTENT_MARKER; 10-minute cooldown after all killed")
    );
    static int maximumWeight(Spawn definition) {
        return switch(definition.id()) {case "zuwu_daoshou"->10;case "fufa_jijiu"->4;default->definition.spawnWeight();};
    }
    static int effectiveWeight(Spawn definition,boolean night,int localLight) {
        return switch(definition.id()) {
            case "zuwu_daoshou"->night?10:8;
            case "fufa_jijiu"->night||localLight<=7?4:2;
            default->definition.spawnWeight();
        };
    }
    private TemplateContentDefinitions() {}
}
