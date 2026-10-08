package com.dynasty.cod3;

import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.BiomeTags;

/** Non-combat regional events use actual day/moon/rain predicates, with fixed world anchors. */
public record ScenicEventDefinition(int number,String dimension,int from,int until,Weather weather,int duration,int template) {
    public enum Weather {ANY,CLEAR,RAIN}
    public boolean eligible(ServerPlayer p){
        var l=p.serverLevel();if(!l.dimension().location().toString().equals(dimension))return false;
        long time=Math.floorMod(l.getDayTime(),24000);if(time<from||time>until)return false;
        if(weather==Weather.CLEAR&&l.isRaining()||weather==Weather.RAIN&&!l.isRaining())return false;
        var biome=l.getBiome(p.blockPosition());
        return switch(number){
            case 1,6,25->biome.is(BiomeTags.IS_MOUNTAIN)&&p.getY()>=90;
            case 4,18->inStructure(p,"ruined_battlefield");
            case 5->biome.is(net.minecraft.world.level.biome.Biomes.DESERT)||biome.is(net.minecraft.world.level.biome.Biomes.SWAMP)||biome.is(BiomeTags.IS_BADLANDS);
            case 11->inStructure(p,"great_wall_gate");
            case 12->inStructure(p,"stone_grove");
            case 14->biome.is(net.minecraft.world.level.biome.Biomes.DESERT)||biome.is(BiomeTags.IS_BADLANDS);
            case 19->biome.is(BiomeTags.IS_FOREST);
            case 7->biome.is(BiomeTags.IS_FOREST)&&l.getMoonPhase()==0;
            case 9,24->p.getY()<0;
            case 10,17->biome.is(BiomeTags.IS_OCEAN)||dimension.equals("dynasty:dragon_palace");
            case 13->p.getY()<40;
            case 15->p.getZ()<-2000&&biome.value().coldEnoughToSnow(p.blockPosition());
            default->true;
        };
    }
    private static boolean inStructure(ServerPlayer p,String id){
        var structure=p.serverLevel().registryAccess().registryOrThrow(net.minecraft.core.registries.Registries.STRUCTURE).get(new net.minecraft.resources.ResourceLocation("dynasty",id));
        return structure!=null&&p.serverLevel().structureManager().getStructureAt(p.blockPosition(),structure).isValid();
    }
    public static ScenicEventDefinition of(int n){
        var row=Cod3Catalog.find("scenic",String.format(java.util.Locale.ROOT,"scenic_%02d",n));
        String dim=switch(n){case 3,22->"dynasty:underworld";case 16,23->"dynasty:jiuxiao";case 17->"dynasty:dragon_palace";default->"minecraft:overworld";};
        int from=switch(n){case 1,12,19->11000;case 2->17000;case 3,7,13,14,15,20,22,23->13000;case 11,21->5500;case 6,18,25->0;default->0;};
        int until=switch(n){case 1,12,19->13000;case 2->19000;case 11,21->6500;case 16->12000;case 6,18,25->2500;default->23999;};
        return new ScenicEventDefinition(n,dim,from,until,java.util.Set.of(9,17,24).contains(n)?Weather.ANY:java.util.Set.of(3,4,7,18).contains(n)?Weather.RAIN:Weather.CLEAR,row.get("duration").getAsInt(),switch(n){case 1->17;case 4,18->29;case 5,16,17,23->40;case 7,19->21;case 8->28;case 10->20;case 15->24;default->15;});
    }
}
