package com.dynasty.structure;

import com.dynasty.Dynasty;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;
import java.util.*;

/** Captures the actual production placement calls, not a duplicate schematic. */
@GameTestHolder(Dynasty.MODID)
@PrefixGameTestTemplate(false)
public final class AcademyLayoutGameTests {
    private static final class Capture extends AcademyPiece {
        final Map<BlockPos,BlockState> cells=new HashMap<>();
        int chests;
        Capture(){super(DynastyStructures.ACADEMY_PIECE.get(),0,BlockPos.ZERO);}
        @Override protected void set(WorldGenLevel w,BoundingBox b,int x,int y,int z,BlockState s) {
            if(x<0||x>=SIZE||z<0||z>=SIZE||y<0||y>=HEIGHT)
                throw new AssertionError("Placement escapes declared bounds: "+x+","+y+","+z);
            cells.put(new BlockPos(x,y,z),s);
        }
        @Override void lootChest(WorldGenLevel w,BoundingBox b,RandomSource r,int x,int y,int z,ResourceLocation table) {
            chests++;set(w,b,x,y,z,Blocks.CHEST.defaultBlockState());
        }
        BlockState at(int x,int y,int z){return cells.getOrDefault(new BlockPos(x,y,z),Blocks.AIR.defaultBlockState());}
        boolean walk(int x,int z){return x>=0&&x<SIZE&&z>=0&&z<SIZE
                &&!at(x,1,z).isAir()&&at(x,1,z).getFluidState().isEmpty()
                &&at(x,2,z).isAir()&&at(x,3,z).isAir();}
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=40)
    public static void academyBoundsRoutesAndAmenities(GameTestHelper h) {
        h.assertTrue(com.dynasty.puzzle.PuzzleBlocks.STAR_DIAL.get().defaultBlockState()
                .hasProperty(com.dynasty.puzzle.PuzzleBlocks.FACING),"Puzzle dial facing was not registered");
        h.assertTrue(com.dynasty.puzzle.PuzzleBlocks.ELEMENT_LAMP.get().defaultBlockState()
                .hasProperty(com.dynasty.puzzle.PuzzleBlocks.SYMBOL),"Lamp symbol was not registered");
        h.assertTrue(!net.minecraftforge.registries.ForgeRegistries.ITEMS.getValue(
                new ResourceLocation("dynasty","star_dial")).equals(
                com.dynasty.puzzle.PuzzleBlocks.STAR_DIAL.get().asItem()),"Puzzle item replaced the existing accessory");
        Capture p=new Capture();
        AcademyCourtyard.build(p,null,p.getBoundingBox(),RandomSource.create(1));
        h.assertTrue(p.chests==3,"Retain three loot chests, not extra palace-tier farming");
        h.assertTrue(p.at(22,2,9).is(Blocks.ENCHANTING_TABLE),"Enchanting station missing");
        long shelves=0;
        for(int x=20;x<=24;x++)for(int z=7;z<=11;z++)if(p.at(x,2,z).is(Blocks.BOOKSHELF))shelves++;
        h.assertTrue(shelves==15,"Enchanting library requires 15 surrounding shelves");
        h.assertTrue(p.at(41,2,21).is(Blocks.BREWING_STAND),"Brewing station missing");
        h.assertTrue(p.at(41,2,12).is(Blocks.STONECUTTER),"Stonecutting station missing");
        Set<BlockPos> seen=new HashSet<>();ArrayDeque<BlockPos> queue=new ArrayDeque<>();
        queue.add(new BlockPos(22,2,44));seen.add(queue.peek());
        while(!queue.isEmpty()) {
            var at=queue.remove();
            for(int[] d:new int[][]{{1,0},{-1,0},{0,1},{0,-1}}) {
                var next=at.offset(d[0],0,d[1]);
                if(p.walk(next.getX(),next.getZ())&&seen.add(next))queue.add(next);
            }
        }
        for(int[] target:new int[][]{{22,13},{7,17},{38,17},{22,10},{11,34},{34,34}})
            h.assertTrue(seen.contains(new BlockPos(target[0],2,target[1])),"Unreachable room/bridge: "+Arrays.toString(target));
        h.succeed();
    }
}
