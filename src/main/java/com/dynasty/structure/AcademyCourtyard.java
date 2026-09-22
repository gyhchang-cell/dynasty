package com.dynasty.structure;

import com.dynasty.DynastyBlocks;
import com.dynasty.worldgen.DynastyBuildKit;
import net.minecraft.core.Direction;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.structure.BoundingBox;

/** 46-block academy: walkable lecture hall, two functional wings and a bridge garden. */
final class AcademyCourtyard {
    private static final ResourceLocation LOOT = new ResourceLocation("dynasty", "chests/temple");
    static void build(AcademyPiece p, WorldGenLevel w, BoundingBox b, RandomSource random) {
        var stone=DynastyBlocks.MARBLE_BLOCK.get().defaultBlockState();
        var brick=DynastyBlocks.PALACE_BRICKS.get().defaultBlockState();
        var jade=DynastyBlocks.JADE_BLOCK.get().defaultBlockState();
        var column=DynastyBlocks.CRIMSON_PILLAR.get().defaultBlockState();
        var lamp=DynastyBlocks.IMPERIAL_LANTERN.get().defaultBlockState();
        var air=Blocks.AIR.defaultBlockState();
        // Clear terrain before furnishings; every write remains clipped to the current chunk.
        p.fill(w,b,0,0,0,45,0,45,brick);
        p.fill(w,b,1,1,1,44,1,44,stone);
        p.fill(w,b,0,2,0,45,17,45,air);
        p.walls(w,b,1,2,1,44,5,44,brick);
        p.walls(w,b,1,6,1,44,6,44,Blocks.DARK_PRISMARINE_SLAB.defaultBlockState());
        for(int i=4;i<=40;i+=6) {
            for(int edge:new int[]{1,44}) {
                p.fill(w,b,i,2,edge,i,5,edge,column);
                p.fill(w,b,edge,2,i,edge,5,i,column);
            }
        }
        // Main hall and wings are separate volumes, with two-block garden alleys between eaves.
        room(p,w,b,14,5,31,23,8);
        room(p,w,b,3,7,10,26,6);
        room(p,w,b,35,7,42,26,6);
        p.fill(w,b,21,2,23,24,5,23,air);
        p.fill(w,b,10,2,16,10,4,18,air);
        p.fill(w,b,35,2,16,35,4,18,air);
        p.fill(w,b,21,1,24,24,1,44,jade);
        p.fill(w,b,11,1,16,13,1,18,jade);
        p.fill(w,b,32,1,16,34,1,18,jade);
        p.fill(w,b,14,2,16,14,4,18,air);
        p.fill(w,b,31,2,16,31,4,18,air);

        // Lecture desks, readable aisle, actual enchanting library (15 unobstructed shelves).
        for(int x:new int[]{17,19,26,28})for(int z:new int[]{16,20}) {
            p.set(w,b,x,2,z,Blocks.LECTERN.defaultBlockState());
            p.set(w,b,x,2,z+1,DynastyBuildKit.facing(Blocks.SPRUCE_STAIRS.defaultBlockState(),Direction.NORTH));
        }
        p.set(w,b,22,2,9,Blocks.ENCHANTING_TABLE.defaultBlockState());
        for(int x=20;x<=24;x++)for(int z=7;z<=11;z++)
            if((x==20||x==24||z==7||z==11)&&!(x==22&&z==11))
                p.set(w,b,x,2,z,Blocks.BOOKSHELF.defaultBlockState());
        p.set(w,b,16,2,7,DynastyBlocks.INCENSE_BURNER.get().defaultBlockState());
        p.set(w,b,29,2,7,DynastyBlocks.CHIME_BELL.get().defaultBlockState());

        // West wing: reading alcoves, map desk and a navigable two-block aisle.
        for(int z=9;z<=24;z+=3) {
            p.fill(w,b,4,2,z,4,3,z,Blocks.BOOKSHELF.defaultBlockState());
            p.set(w,b,6,2,z,Blocks.LECTERN.defaultBlockState());
        }
        p.set(w,b,8,2,9,Blocks.CARTOGRAPHY_TABLE.defaultBlockState());
        p.set(w,b,8,2,24,Blocks.CRAFTING_TABLE.defaultBlockState());
        // East wing: useful workstations, not decorative fake machines.
        BlockState[] stations={Blocks.CRAFTING_TABLE.defaultBlockState(),Blocks.STONECUTTER.defaultBlockState(),
                Blocks.SMITHING_TABLE.defaultBlockState(),Blocks.FURNACE.defaultBlockState(),
                Blocks.BREWING_STAND.defaultBlockState(),Blocks.WATER_CAULDRON.defaultBlockState()};
        for(int i=0;i<stations.length;i++)p.set(w,b,41,2,9+i*3,stations[i]);
        for(int z:new int[]{10,22})p.set(w,b,37,2,z,DynastyBlocks.SCREEN.get().defaultBlockState());

        // Twin sunken pools: sealed bottoms, walkable bridges at courtyard floor level.
        for(int x:new int[]{6,29}) {
            p.fill(w,b,x,1,31,x+10,1,38,stone);
            p.fill(w,b,x+1,1,32,x+9,1,37,Blocks.WATER.defaultBlockState());
            p.fill(w,b,x,1,34,x+10,1,35,Blocks.SPRUCE_PLANKS.defaultBlockState());
            for(int xx:new int[]{x,x+10})for(int z:new int[]{31,38}) {
                p.set(w,b,xx,2,z,Blocks.STONE_BRICK_WALL.defaultBlockState());
                p.set(w,b,xx,3,z,lamp);
            }
            for(int xx:new int[]{x+2,x+8})p.set(w,b,xx,2,32,Blocks.LILY_PAD.defaultBlockState());
        }
        // Covered transverse promenade, kept clear below the roof.
        p.glazedRoof(w,b,4,27,41,30,6,2);
        for(int x=5;x<=40;x+=5) {
            if(x>=20&&x<=25)continue;
            p.fill(w,b,x,2,28,x,5,28,column);
            p.set(w,b,x,5,29,lamp);
        }
        // Gatehouse, open entrance and a one-step approach from natural ground.
        p.fill(w,b,20,2,43,25,6,44,air);
        for(int x:new int[]{19,26})p.fill(w,b,x,2,43,x,7,43,column);
        p.glazedRoof(w,b,18,41,27,45,8,2);
        p.fill(w,b,20,1,45,25,1,45,DynastyBuildKit.facing(Blocks.QUARTZ_STAIRS.defaultBlockState(),Direction.NORTH));
        for(int x:new int[]{19,26})p.set(w,b,x,6,42,lamp);
        for(int x:new int[]{19,26})for(int z:new int[]{25,33,39}) {
            p.set(w,b,x,2,z,Blocks.STONE_BRICK_WALL.defaultBlockState());
            p.set(w,b,x,3,z,lamp);
        }
        // Three original-tier chests; expansion does not multiply high-value loot.
        p.lootChest(w,b,random,8,2,12,LOOT);
        p.lootChest(w,b,random,37,2,24,LOOT);
        p.lootChest(w,b,random,29,2,8,LOOT);
    }

    private static void room(AcademyPiece p,WorldGenLevel w,BoundingBox b,int x0,int z0,int x1,int z1,int top) {
        var brick=DynastyBlocks.PALACE_BRICKS.get().defaultBlockState();
        var column=DynastyBlocks.CRIMSON_PILLAR.get().defaultBlockState();
        var wood=Blocks.SPRUCE_PLANKS.defaultBlockState();
        p.fill(w,b,x0,1,z0,x1,1,z1,wood);
        p.walls(w,b,x0,2,z0,x1,top,z1,brick);
        for(int x:new int[]{x0,x1})for(int z:new int[]{z0,z1})p.fill(w,b,x,2,z,x,top,z,column);
        // Recessed light-transmitting windows, framed by continuous timber lintels.
        for(int z=z0+3;z<z1-1;z+=4)for(int x:new int[]{x0,x1})
            p.fill(w,b,x,3,z,x,4,z+1,Blocks.GLASS_PANE.defaultBlockState());
        p.walls(w,b,x0,top,z0,x1,top,z1,column);
        p.glazedRoof(w,b,x0-1,z0-1,x1+1,z1+1,top+1,3);
        int mid=(x0+x1)/2;
        p.fill(w,b,mid,top+4,z0+2,mid,top+4,z1-2,DynastyBlocks.JADE_BLOCK.get().defaultBlockState());
        for(int z:new int[]{z0+2,z1-2})
            p.set(w,b,mid,top-1,z,DynastyBlocks.IMPERIAL_LANTERN.get().defaultBlockState());
    }
}
