package com.dynasty.cod3;

import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.BiomeTags;

/** Non-combat regional events use actual day/moon/rain predicates, with fixed world anchors. */
public record ScenicEventDefinition(int number,String dimension,int from,int until,Weather weather,int duration,int template) {
    public enum Weather {ANY,CLEAR,RAIN}
    public boolean eligible(ServerPlayer p){
        var l=p.serverLevel();if(!allowsDimension(l.dimension().location().toString()))return false;
        long time=Math.floorMod(l.getDayTime(),24000);if(time<from||time>until)return false;
        if(weather==Weather.CLEAR&&l.isRaining()||weather==Weather.RAIN&&!l.isRaining())return false;
        var biome=l.getBiome(p.blockPosition());
        return switch(number){
            case 3->(dimension.equals(l.dimension().location().toString())||biome.is(BiomeTags.IS_RIVER))&&ScenicGhostShipRoute.visibility(l)>0&&ScenicGhostShipRoute.nearObserver(l,p.position(),p.getLookAngle())!=null;
            case 6->ScenicStoneGodSite.visibility(l)>0&&ScenicStoneGodSite.nearObserver(l,p.position(),p.getLookAngle())!=null;
            case 1,25->biome.is(BiomeTags.IS_MOUNTAIN)&&p.getY()>=90;
            case 4->inStructure(p,"ruined_battlefield")&&ScenicGhostArmySite.find(l,p.position().add(p.getLookAngle().multiply(1,0,1).normalize().scale(96)))!=null;
            case 18->inStructure(p,"ruined_battlefield")&&ScenicGreatWallSite.find(l,p.position().add(p.getLookAngle().multiply(1,0,1).normalize().scale(96)))!=null;
            case 5->ScenicEvents.get(l).recentlyCleared(l)&&(biome.is(net.minecraft.world.level.biome.Biomes.DESERT)||biome.is(net.minecraft.world.level.biome.Biomes.SWAMP)||biome.is(BiomeTags.IS_BADLANDS));
            case 2,20->biome.is(net.minecraft.world.level.biome.Biomes.PLAINS)||biome.is(net.minecraft.world.level.biome.Biomes.SUNFLOWER_PLAINS);
            case 8->l.getWorldBorder().getDistanceToBorder(p)<256;
            case 11->inStructure(p,"great_wall_gate");
            case 12->inStructure(p,"stone_grove");
            case 14->ScenicMirageSite.visibility(l)>0&&ScenicMirageSite.desert(l,p.blockPosition())&&ScenicMirageSite.find(l,p.position().add(p.getLookAngle().multiply(1,0,1).normalize().scale(96)))!=null;
            case 19->biome.is(BiomeTags.IS_FOREST);
            case 7->biome.is(BiomeTags.IS_FOREST)&&l.getMoonPhase()==0;
            // These permanent displays are ordinary blocks in registered structures.
            // Do not spawn the old timed light-field placeholders merely because a player is underground.
            case 9,13,24->false;
            case 22->ScenicGhostMarketSite.find(l,p.position().add(p.getLookAngle().multiply(1,0,1).normalize().scale(96)))!=null;
            case 17->ScenicDragonPalaceSite.nearObserver(l,p.position(),p.getLookAngle())!=null;
            case 10->biome.is(BiomeTags.IS_OCEAN)||dimension.equals("dynasty:dragon_palace");
            case 15->p.getZ()<-2000&&biome.value().coldEnoughToSnow(p.blockPosition());
            default->true;
        };
    }
    public boolean allowsDimension(String id){return number==3?ScenicGhostShipRoute.dimension(id):dimension.equals(id);}
    private static boolean inStructure(ServerPlayer p,String id){
        var structure=p.serverLevel().registryAccess().registryOrThrow(net.minecraft.core.registries.Registries.STRUCTURE).get(net.minecraft.resources.ResourceLocation.fromNamespaceAndPath("dynasty",id));
        return structure!=null&&p.serverLevel().structureManager().getStructureAt(p.blockPosition(),structure).isValid();
    }
    public static ScenicEventDefinition of(int n){
        var row=Cod3Catalog.find("scenic",String.format(java.util.Locale.ROOT,"scenic_%02d",n));
        String dim=switch(n){case 3,22->"dynasty:underworld";case 16,23->"dynasty:jiuxiao";case 17->"dynasty:dragon_palace";default->"minecraft:overworld";};
        int from=switch(n){case 1,12,19->11000;case 2->17000;case 3,7,13,15,20,22,23->13000;case 14->16000;case 11,21->5500;case 6,18,25->0;default->0;};
        int until=switch(n){case 1,12,19->13000;case 2->19000;case 11,21->6500;case 16->12000;case 6,18,25->2500;case 14->22000;default->23999;};
        return new ScenicEventDefinition(n,dim,from,until,java.util.Set.of(3,9,17,22,24).contains(n)?Weather.ANY:java.util.Set.of(4,7,18).contains(n)?Weather.RAIN:Weather.CLEAR,row.get("duration").getAsInt(),switch(n){case 1->17;case 4,18->29;case 5,16,17,23->40;case 7,19->21;case 8->28;case 10->20;case 15->24;default->15;});
    }
}
