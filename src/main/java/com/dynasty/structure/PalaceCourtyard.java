package com.dynasty.structure;

import com.dynasty.DynastyBlocks;
import com.dynasty.worldgen.DynastyBuildKit;
import net.minecraft.core.Direction;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.structure.BoundingBox;

/** 64-block, walkable palace campus. Local coordinates always flow through chunk-clipped placement. */
final class PalaceCourtyard {
    private PalaceCourtyard() {}
    static void build(PalacePiece p, WorldGenLevel w, BoundingBox b, RandomSource r) {
        var stone=DynastyBlocks.PALACE_BRICKS.get().defaultBlockState();
        var white=DynastyBlocks.MARBLE_BLOCK.get().defaultBlockState();
        var jade=DynastyBlocks.JADE_BLOCK.get().defaultBlockState();
        var red=DynastyBlocks.CRIMSON_PILLAR.get().defaultBlockState();
        var lamp=DynastyBlocks.IMPERIAL_LANTERN.get().defaultBlockState();
        var air=Blocks.AIR.defaultBlockState();
        // Continuous terrace and clear circulation volume. No random damage or hidden traps.
        p.fill(w,b,0,0,0,63,0,63,stone);
        p.fill(w,b,1,1,1,62,1,62,stone);
        p.fill(w,b,2,2,2,61,2,61,white);
        p.fill(w,b,3,3,3,60,3,60,white);
        p.fill(w,b,3,4,3,60,28,60,air);
        p.walls(w,b,3,4,3,60,8,60,stone);
        p.walls(w,b,3,9,3,60,9,60,white);
        // Two-tone stone paving: quiet inset bands break up the large white courtyard.
        for(int z:new int[]{14,27,50,55})p.fill(w,b,8,3,z,55,3,z,Blocks.SMOOTH_STONE.defaultBlockState());
        for(int x:new int[]{19,44})p.fill(w,b,x,3,13,x,3,55,Blocks.SMOOTH_STONE.defaultBlockState());
        // A continuous green tile coping gives the walls a finished profile.
        for(int i=3;i<=60;i++) {
            p.set(w,b,i,10,3,DynastyBuildKit.facing(Blocks.DARK_PRISMARINE_STAIRS.defaultBlockState(),Direction.SOUTH));
            p.set(w,b,i,10,60,DynastyBuildKit.facing(Blocks.DARK_PRISMARINE_STAIRS.defaultBlockState(),Direction.NORTH));
            p.set(w,b,3,10,i,DynastyBuildKit.facing(Blocks.DARK_PRISMARINE_STAIRS.defaultBlockState(),Direction.EAST));
            p.set(w,b,60,10,i,DynastyBuildKit.facing(Blocks.DARK_PRISMARINE_STAIRS.defaultBlockState(),Direction.WEST));
        }
        // Repeated stone plinth / timber bays make the perimeter readable at a distance.
        for(int i=7;i<=56;i+=7)for(int side:new int[]{3,60}) {
            p.fill(w,b,i,4,side,i,8,side,red);
            p.fill(w,b,side,4,i,side,8,i,red);
            p.set(w,b,i,10,side,jade);p.set(w,b,side,10,i,jade);
        }
        // Front gate has three passages; an uninterrupted seven-block ceremonial axis.
        p.fill(w,b,28,4,59,35,9,60,air);
        for(int x:new int[]{22,40})p.fill(w,b,x,4,59,x+1,7,60,air);
        for(int x:new int[]{20,25,27,36,38,43}) {
            p.fill(w,b,x,4,58,x,11,58,red);
            p.fill(w,b,x-1,10,57,x+1,10,59,Blocks.DARK_OAK_SLAB.defaultBlockState());
            p.set(w,b,x,9,57,lamp);
        }
        p.fill(w,b,20,11,58,43,11,58,red);
        p.glazedRoof(w,b,18,55,45,62,12,4);
        p.glazedRoof(w,b,25,56,38,61,16,3);
        p.set(w,b,31,11,57,DynastyBlocks.PLAQUE.get().defaultBlockState());
        for(int k=0;k<3;k++)p.fill(w,b,28,k+1,63-k,35,k+1,63-k,
                DynastyBuildKit.facing(Blocks.QUARTZ_STAIRS.defaultBlockState(),Direction.NORTH));
        p.fill(w,b,29,3,34,34,3,59,jade);
        for(int z=35;z<=56;z+=3) {
            p.set(w,b,28,3,z,Blocks.CHISELED_STONE_BRICKS.defaultBlockState());
            p.set(w,b,35,3,z,Blocks.CHISELED_STONE_BRICKS.defaultBlockState());
        }
        // Twin side halls: archive / cartography to the west, workshops to the east.
        hall(p,w,b,8,29,18,48,false);
        hall(p,w,b,45,29,55,48,true);
        // Paired reflecting pools leave the centre and side-hall doors clear.
        for(int x:new int[]{22,38}) {
            p.fill(w,b,x,3,39,x+3,3,48,stone);
            p.fill(w,b,x+1,3,40,x+2,3,47,Blocks.WATER.defaultBlockState());
            // A bridge across each pool, aligned with the hall entrances.
            p.fill(w,b,x,3,43,x+3,3,44,Blocks.DARK_OAK_PLANKS.defaultBlockState());
            for(int z:new int[]{38,49}) {
                p.set(w,b,x,4,z,Blocks.STONE_BRICK_WALL.defaultBlockState());
                p.set(w,b,x,5,z,lamp);
            }
        }
        // Covered peripheral promenades, open underneath and connected around each hall.
        for(int x:new int[]{5,58}) {
            for(int z=12;z<=51;z+=5) {
                p.fill(w,b,x,4,z,x,8,z,red);
                p.set(w,b,x,9,z,lamp);
            }
            p.glazedRoof(w,b,x-1,12,x+1,51,10,1);
        }
        // Rear garden: two planted courts, pond, a central bridge and two reading pavilions.
        for(int x:new int[]{19,36}) {
            p.fill(w,b,x,3,6,x+8,3,11,Blocks.GRASS_BLOCK.defaultBlockState());
            for(int dx=0;dx<=8;dx+=4) {
                p.set(w,b,x+dx,4,7,Blocks.AZALEA.defaultBlockState());
                p.set(w,b,x+dx,4,10,Blocks.FLOWERING_AZALEA.defaultBlockState());
            }
        }
        p.fill(w,b,29,3,5,34,3,11,Blocks.WATER.defaultBlockState());
        p.fill(w,b,29,3,8,34,3,9,Blocks.DARK_OAK_PLANKS.defaultBlockState());
        gardenTree(p,w,b,23,10);gardenTree(p,w,b,40,10);
        gardenTree(p,w,b,12,21);gardenTree(p,w,b,51,21);
        pavilion(p,w,b,7,6);pavilion(p,w,b,49,6);
        pavilion(p,w,b,7,51);pavilion(p,w,b,49,51);
        p.set(w,b,13,4,9,Blocks.LECTERN.defaultBlockState());
        p.set(w,b,51,4,9,Blocks.CARTOGRAPHY_TABLE.defaultBlockState());
        // Ceremonial props sit off the travel axis, not in a wall of decorations.
        p.set(w,b,25,4,52,DynastyBlocks.TAIKO_DRUM.get().defaultBlockState());
        p.set(w,b,38,4,52,DynastyBlocks.CHIME_BELL.get().defaultBlockState());
        p.set(w,b,25,4,35,DynastyBlocks.INCENSE_BURNER.get().defaultBlockState());
        p.set(w,b,38,4,35,DynastyBlocks.INCENSE_BURNER.get().defaultBlockState());
        // Same four parent loot rolls as the old palace; side rooms are worth visiting.
        p.lootChest(w,b,r,10,4,32);p.lootChest(w,b,r,53,4,32);
        p.lootChest(w,b,r,10,4,9);p.lootChest(w,b,r,53,4,9);
    }
    private static void gardenTree(PalacePiece p,WorldGenLevel w,BoundingBox b,int x,int z) {
        p.fill(w,b,x-2,3,z-2,x+2,3,z+2,Blocks.MOSS_BLOCK.defaultBlockState());
        p.fill(w,b,x,4,z,x,7,z,Blocks.CHERRY_LOG.defaultBlockState());
        var leaf=Blocks.CHERRY_LEAVES.defaultBlockState()
                .setValue(net.minecraft.world.level.block.LeavesBlock.PERSISTENT,true);
        for(int y=7;y<=9;y++) {
            int radius=y==9?1:2;
            for(int dx=-radius;dx<=radius;dx++)for(int dz=-radius;dz<=radius;dz++) {
                if(Math.abs(dx)+Math.abs(dz)>radius+1)continue;
                p.set(w,b,x+dx,y,z+dz,leaf);
            }
        }
        // Keep the northern walking strip beside the garden bridge unobstructed.
        for(int dx:new int[]{-2,2})p.set(w,b,x+dx,4,z+2,Blocks.FLOWERING_AZALEA.defaultBlockState());
    }
    private static void hall(PalacePiece p,WorldGenLevel w,BoundingBox b,int x0,int z0,int x1,int z1,boolean workshop) {
        var red=DynastyBlocks.CRIMSON_PILLAR.get().defaultBlockState();
        var white=DynastyBlocks.MARBLE_BLOCK.get().defaultBlockState();
        var wood=Blocks.DARK_OAK_PLANKS.defaultBlockState();
        p.fill(w,b,x0,3,z0,x1,3,z1,wood);
        p.walls(w,b,x0,4,z0,x1,9,z1,white);
        // Side entrance facing the court and doors at both ends make an actual through-route.
        int doorX=workshop?x0:x1;
        p.fill(w,b,doorX,4,42,doorX,7,45,Blocks.AIR.defaultBlockState());
        for(int z:new int[]{z0,z1})p.fill(w,b,x0+4,4,z,x0+6,7,z,Blocks.AIR.defaultBlockState());
        for(int z=z0;z<=z1;z+=4)for(int x:new int[]{x0,x1}) {
            p.fill(w,b,x,4,z,x,10,z,red);
            p.set(w,b,x,10,z,DynastyBlocks.BRONZE_BLOCK.get().defaultBlockState());
        }
        for(int z:new int[]{34,38})for(int x:new int[]{x0,x1})
            p.fill(w,b,x,6,z,x,8,z+1,Blocks.DARK_OAK_FENCE.defaultBlockState());
        p.glazedRoof(w,b,x0-1,z0-1,x1+1,z1+1,11,4);
        for(int z:new int[]{33,39,46}) {
            p.set(w,b,x0+5,9,z,DynastyBlocks.IMPERIAL_LANTERN.get().defaultBlockState());
            if(workshop) {
                p.set(w,b,x1-1,4,z,Blocks.SMITHING_TABLE.defaultBlockState());
                p.set(w,b,x1-1,4,z+1,Blocks.BLAST_FURNACE.defaultBlockState());
            } else {
                p.fill(w,b,x0+1,4,z,x0+1,6,z+1,Blocks.BOOKSHELF.defaultBlockState());
                p.set(w,b,x1-2,4,z,Blocks.LECTERN.defaultBlockState());
            }
        }
        p.set(w,b,x0+2,4,46,workshop?Blocks.ANVIL.defaultBlockState():Blocks.CARTOGRAPHY_TABLE.defaultBlockState());
    }
    private static void pavilion(PalacePiece p,WorldGenLevel w,BoundingBox b,int x,int z) {
        for(int dx:new int[]{0,6})for(int dz:new int[]{0,5}) {
            p.fill(w,b,x+dx,4,z+dz,x+dx,8,z+dz,DynastyBlocks.CRIMSON_PILLAR.get().defaultBlockState());
            p.set(w,b,x+dx,9,z+dz,DynastyBlocks.IMPERIAL_LANTERN.get().defaultBlockState());
        }
        p.glazedRoof(w,b,x-1,z-1,x+7,z+6,10,3);
        p.set(w,b,x+3,4,z+2,Blocks.DARK_OAK_STAIRS.defaultBlockState());
    }
}
