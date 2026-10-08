package com.dynasty.structure;

import com.dynasty.DynastyBlocks;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.StructureManager;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.CropBlock;
import net.minecraft.world.level.block.FarmBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.level.levelgen.structure.pieces.StructurePieceSerializationContext;

/** Three distinct 31-block courtyard plans: post house, forest pharmacy, desert caravanserai. */
public class TravelSitePiece extends DynastyStructurePiece {
    final int style;
    public TravelSitePiece(BlockPos origin,int style){
        super(DynastyStructures.TRAVEL_SITE_PIECE.get(),0,makeBoundingBox(origin.getX(),origin.getY(),origin.getZ(),Direction.NORTH,31,13,31));
        setOrientation(Direction.NORTH);this.style=style;
    }
    public TravelSitePiece(StructurePieceSerializationContext ctx,CompoundTag tag){super(DynastyStructures.TRAVEL_SITE_PIECE.get(),tag);style=Math.max(0,Math.min(2,tag.getInt("Style")));}
    @Override protected void addAdditionalSaveData(StructurePieceSerializationContext ctx,CompoundTag tag){super.addAdditionalSaveData(ctx,tag);tag.putInt("Style",style);}
    void loot(WorldGenLevel l,BoundingBox b,RandomSource r,int x,int y,int z,String table){createChest(l,b,r,x,y,z,new ResourceLocation(table));}
    private void room(WorldGenLevel l,BoundingBox b,int x,int z,int w,int d,BlockState wall){
        fill(l,b,x,1,z,x+w,1,z+d,Blocks.SPRUCE_PLANKS.defaultBlockState());
        fill(l,b,x+1,2,z+1,x+w-1,5,z+d-1,Blocks.AIR.defaultBlockState());
        walls(l,b,x,2,z,x+w,5,z+d,wall);
        for(int px:new int[]{x,x+w})for(int pz:new int[]{z,z+d})fill(l,b,px,2,pz,px,5,pz,DynastyBlocks.CRIMSON_PILLAR.get().defaultBlockState());
        fill(l,b,x+w/2,2,z+d,x+w/2+1,4,z+d,Blocks.AIR.defaultBlockState());
        for(int px=x+w/2;px<=x+w/2+1;px++)set(l,b,px,1,z+d+1,Blocks.SPRUCE_STAIRS.defaultBlockState().setValue(net.minecraft.world.level.block.StairBlock.FACING,Direction.NORTH));
        for(int px=x+2;px<x+w-1;px+=3)set(l,b,px,3,z,Blocks.GLASS_PANE.defaultBlockState());
        glazedRoof(l,b,x-1,z-1,x+w+1,z+d+1,6,3);
        set(l,b,x+w/2,5,z+d-1,DynastyBlocks.IMPERIAL_LANTERN.get().defaultBlockState());
        set(l,b,x+2,2,z+2,Blocks.CRAFTING_TABLE.defaultBlockState());
    }
    @Override public void postProcess(WorldGenLevel l,StructureManager m,ChunkGenerator g,RandomSource r,BoundingBox b,ChunkPos cp,BlockPos p){
        var brick=style==2?Blocks.SMOOTH_SANDSTONE.defaultBlockState():DynastyBlocks.PALACE_BRICKS.get().defaultBlockState();
        fill(l,b,0,0,0,30,0,30,brick);
        fill(l,b,0,1,0,30,11,30,Blocks.AIR.defaultBlockState());
        // Open entrance, low boundary and lit approach; no unavoidable jump at the threshold.
        walls(l,b,1,1,1,29,1,29,brick);
        fill(l,b,13,1,27,17,1,30,Blocks.AIR.defaultBlockState());
        for(int[] q:new int[][]{{2,2},{28,2},{2,28},{28,28}}){fill(l,b,q[0],1,q[1],q[0],3,q[1],DynastyBlocks.CRIMSON_PILLAR.get().defaultBlockState());set(l,b,q[0],4,q[1],DynastyBlocks.IMPERIAL_LANTERN.get().defaultBlockState());}
        if(style==0){
            room(l,b,3,3,15,9,brick);room(l,b,3,16,8,9,brick);
            // Stable and open smith's shed occupy the opposite wing, not another closed box.
            fill(l,b,21,1,4,27,1,18,Blocks.COBBLESTONE.defaultBlockState());
            for(int z:new int[]{4,11,18}){fill(l,b,21,2,z,21,4,z,Blocks.OAK_LOG.defaultBlockState());fill(l,b,27,2,z,27,4,z,Blocks.OAK_LOG.defaultBlockState());}
            glazedRoof(l,b,20,3,28,19,5,2);
            for(int z:new int[]{6,13}){set(l,b,26,2,z,Blocks.HAY_BLOCK.defaultBlockState());set(l,b,26,2,z+1,Blocks.WATER_CAULDRON.defaultBlockState());}
            set(l,b,24,2,16,Blocks.SMITHING_TABLE.defaultBlockState());set(l,b,25,2,16,Blocks.ANVIL.defaultBlockState());
            set(l,b,5,2,5,Blocks.SMOKER.defaultBlockState());set(l,b,7,2,5,Blocks.BARREL.defaultBlockState());
            for(int x=5;x<=8;x++)set(l,b,x,2,18,Blocks.BOOKSHELF.defaultBlockState());
            loot(l,b,r,16,2,5,"minecraft:chests/village/village_plains_house");
            story(l,b,23,1,16,30);story(l,b,15,1,22,33);story(l,b,8,1,18,34);story(l,b,25,1,17,40);
            story(l,b,8,2,6,4);story(l,b,7,2,22,7);story(l,b,10,2,20,25);
            loot(l,b,r,24,2,5,"minecraft:chests/village/village_weaponsmith");
        }else if(style==1){
            room(l,b,3,3,11,10,brick);
            for(int z=17;z<=25;z+=4){
                fill(l,b,4,0,z,23,0,z,Blocks.FARMLAND.defaultBlockState().setValue(FarmBlock.MOISTURE,7));
                fill(l,b,4,0,z+1,23,0,z+1,Blocks.WATER.defaultBlockState());
                for(int x=4;x<=23;x++)set(l,b,x,1,z,(z==17?Blocks.WHEAT:z==21?Blocks.CARROTS:Blocks.POTATOES).defaultBlockState().setValue(CropBlock.AGE,7));
            }
            for(int[] q:new int[][]{{20,4},{27,4},{20,11},{27,11}})fill(l,b,q[0],1,q[1],q[0],4,q[1],Blocks.STRIPPED_OAK_LOG.defaultBlockState());
            glazedRoof(l,b,19,3,28,12,5,3);
            set(l,b,22,1,7,Blocks.CAULDRON.defaultBlockState());set(l,b,24,1,7,Blocks.BREWING_STAND.defaultBlockState());
            for(int x=5;x<12;x++)set(l,b,x,2,5,Blocks.BOOKSHELF.defaultBlockState());
            story(l,b,10,1,8,32);story(l,b,23,0,7,35);story(l,b,18,1,25,39);story(l,b,26,0,8,42);
            story(l,b,11,2,5,8);story(l,b,27,1,23,11);story(l,b,9,2,12,22);
            loot(l,b,r,11,2,11,"minecraft:chests/village/village_temple");
        }else{
            room(l,b,3,3,24,7,brick);room(l,b,3,15,7,10,brick);room(l,b,20,15,7,10,brick);
            // Open well court with supply benches and readable paths between all three halls.
            walls(l,b,13,1,14,17,1,18,Blocks.CUT_SANDSTONE.defaultBlockState());
            fill(l,b,14,0,15,16,0,17,Blocks.WATER.defaultBlockState());
            for(int x:new int[]{13,17})fill(l,b,x,2,16,x,4,16,Blocks.OAK_FENCE.defaultBlockState());
            fill(l,b,12,5,14,18,5,18,Blocks.SANDSTONE_SLAB.defaultBlockState());
            set(l,b,5,2,5,Blocks.CARTOGRAPHY_TABLE.defaultBlockState());set(l,b,7,2,5,Blocks.LECTERN.defaultBlockState());
            set(l,b,5,2,17,Blocks.SMOKER.defaultBlockState());set(l,b,22,2,17,Blocks.STONECUTTER.defaultBlockState());
            loot(l,b,r,25,2,5,"minecraft:chests/village/village_cartographer");
            story(l,b,23,1,22,41);story(l,b,9,1,20,37);story(l,b,5,1,8,33);
            story(l,b,15,1,16,7);story(l,b,26,2,23,24);story(l,b,21,2,19,14);
            loot(l,b,r,7,2,17,"minecraft:chests/village/village_desert_house");
        }
        String[][] sites = {{"wayside_shrine","old_weapon_rack","puzzle_box","wayside_tea_stall","broken_stele"},
                {"herb_spot","nameless_tomb","sword_scar_wall","mortuary_room","broken_waterwheel"},
                {"abandoned_armory","battlefield_remnant","ghost_market_boat","old_bellows","ancient_well"}};
        for (int i=0;i<sites[style].length;i++)
            set(l,b,5+i*4,1,28,com.dynasty.expansion.SmallInteractions.ENTRIES.get(sites[style][i]).get().defaultBlockState());
    }
}
