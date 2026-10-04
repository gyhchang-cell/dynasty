package com.dynasty.ritual;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.LightBlock;
import java.util.LinkedHashSet;
import java.util.Set;

/** Sparse, permanent air-only lighting. Does not touch architecture or ritual ownership. */
public final class ZhenyuanSceneLighting {
    private ZhenyuanSceneLighting() {}
    public static Set<BlockPos> mouth(ServerLevel level,BlockPos center,Iterable<BlockPos> nodes) {
        Set<BlockPos> placed=new LinkedHashSet<>();
        for(BlockPos node:nodes) probe(level,node.offset(3,0,0),placed,11);
        for(int x=-27;x<=27;x+=9)for(int z=-27;z<=27;z+=9) {
            if(x*x+z*z>29*29)continue;
            probe(level,center.offset(x,0,z),placed,Math.abs(x)<=9&&Math.abs(z)<=9?11:10);
        }
        return placed;
    }
    private static void probe(ServerLevel level,BlockPos anchor,Set<BlockPos> placed,int strength) {
        for(int offset=0;offset<=20;offset++) {
            int dy=offset==0?0:(offset%2==1?(offset+1)/2:-offset/2);
            BlockPos feet=anchor.offset(0,dy,0),light=feet.above(3);
            if(!level.getBlockState(feet.below()).isFaceSturdy(level,feet.below(),Direction.UP))continue;
            if(!level.isEmptyBlock(feet)||!level.isEmptyBlock(feet.above())||!level.isEmptyBlock(feet.above(2)))continue;
            if(placed.stream().anyMatch(p->p.distSqr(light)<49))return;
            if(level.isEmptyBlock(light)) {
                level.setBlock(light,Blocks.LIGHT.defaultBlockState().setValue(LightBlock.LEVEL,strength),2);
                placed.add(light);
            } else if(level.getBlockState(light).is(Blocks.LIGHT)) placed.add(light);
            return;
        }
    }
}
