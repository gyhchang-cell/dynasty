package com.dynasty.worldevent;

import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.Level;

/** Custom night-fog forecast is separate from vanilla rain/thunder; it samples loaded participant biomes only. */
public final class WorldEventWeather {
    static boolean fogNight(long seed,long day){return Math.floorMod(mix(seed^day*0x9e3779b97f4a7c15L),7)==0;}
    private static long mix(long n){n=(n^(n>>>30))*0xbf58476d1ce4e5b9L;n=(n^(n>>>27))*0x94d049bb133111ebL;return n^(n>>>31);}
    public static boolean fogAt(ServerLevel level,BlockPos pos){
        long clock=Math.floorMod(level.getDayTime(),24000),day=Math.floorDiv(level.getDayTime(),24000);
        return level.dimension().equals(Level.OVERWORLD)&&clock>=16000&&clock<=21000
            &&fogNight(level.getSeed(),day)&&level.hasChunkAt(pos)&&pos.getY()>=level.getSeaLevel()-8
            &&level.getBiome(pos).value().hasPrecipitation()&&level.getBiome(pos).value().getModifiedClimateSettings().downfall()>=.35F;
    }
    private WorldEventWeather(){}
}
