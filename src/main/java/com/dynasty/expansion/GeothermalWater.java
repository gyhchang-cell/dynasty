package com.dynasty.expansion;

import java.util.*;
import net.minecraft.core.*;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.FluidTags;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;

/** A shallow water/bubble-column bath touching a real submerged magma heat source.
 * Ordinary water and scenery flags are insufficient. Reads only already-loaded native chunks. */
final class GeothermalWater {
    static final int MAX_WATER_CELLS=128;
    static boolean warm(Level level,BlockPos feet){
        if(!(level instanceof ServerLevel server)||!water(server,feet))return false;
        var pending=new ArrayDeque<BlockPos>();var visited=new HashSet<BlockPos>();pending.add(feet.immutable());visited.add(feet.immutable());
        while(!pending.isEmpty()){
            var current=pending.removeFirst();var below=current.below();
            if(loaded(server,below)&&server.getBlockState(below).is(Blocks.MAGMA_BLOCK))return true;
            for(var direction:Direction.values()){
                var next=current.relative(direction);
                if(Math.abs(next.getX()-feet.getX())>4||Math.abs(next.getZ()-feet.getZ())>4||Math.abs(next.getY()-feet.getY())>3||visited.contains(next)||!water(server,next))continue;
                if(visited.size()==MAX_WATER_CELLS)continue;
                visited.add(next);pending.addLast(next.immutable());
            }
        }return false;
    }
    private static boolean loaded(ServerLevel level,BlockPos pos){return !level.isOutsideBuildHeight(pos)&&level.getChunkSource().getChunkNow(pos.getX()>>4,pos.getZ()>>4)!=null;}
    private static boolean water(ServerLevel level,BlockPos pos){return loaded(level,pos)&&level.getFluidState(pos).is(FluidTags.WATER);}
    private GeothermalWater(){}
}
