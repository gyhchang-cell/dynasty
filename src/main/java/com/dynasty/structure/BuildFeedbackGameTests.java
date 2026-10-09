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

@GameTestHolder(Dynasty.MODID) @PrefixGameTestTemplate(false)
public final class BuildFeedbackGameTests {
    @GameTest(template="bow_ritual_test",timeoutTicks=100)
    public static void threeTravelPlansHaveDistinctUsableWorkstations(GameTestHelper h){
        List<Map<BlockPos,BlockState>> plans=new ArrayList<>();
        for(int style=0;style<3;style++){
            Map<BlockPos,BlockState> blocks=new HashMap<>();List<String> loot=new ArrayList<>();
            var p=new TravelSitePiece(BlockPos.ZERO,style){
                @Override protected void set(WorldGenLevel l,BoundingBox b,int x,int y,int z,BlockState s){
                    h.assertTrue(x>=0&&x<31&&z>=0&&z<31&&y>=0&&y<13,"Travel site writes outside its bounds");blocks.put(new BlockPos(x,y,z),s);
                }
                @Override void loot(WorldGenLevel l,BoundingBox b,RandomSource r,int x,int y,int z,String table){
                    loot.add(table);set(l,b,x,y,z,Blocks.CHEST.defaultBlockState());
                }
            };
            p.postProcess(null,null,null,RandomSource.create(0),p.getBoundingBox(),null,BlockPos.ZERO);
            h.assertTrue(blocks.get(new BlockPos(15,1,29)).isAir(),"Courtyard entry blocked");
            h.assertTrue(loot.size()==(style==1?1:2),"Missing supply chest");
            for(String table:loot)h.assertTrue(h.getLevel().getServer().getLootData().getLootTable(new ResourceLocation(table))!=net.minecraft.world.level.storage.loot.LootTable.EMPTY,"Loot table absent: "+table);
            h.assertTrue(blocks.values().stream().anyMatch(s -> s.is(Blocks.SPRUCE_STAIRS)),"Doorsteps need actual stairs");
            plans.add(blocks);
        }
        h.assertTrue(plans.get(0).values().stream().anyMatch(s -> s.is(Blocks.ANVIL)),"Post house smith missing");
        h.assertTrue(plans.get(1).values().stream().anyMatch(s -> s.is(Blocks.BREWING_STAND)),"Pharmacy brewing station missing");
        h.assertTrue(plans.get(2).values().stream().anyMatch(s -> s.is(Blocks.CARTOGRAPHY_TABLE)),"Caravan map desk missing");
        h.assertTrue(!plans.get(0).equals(plans.get(1))&&!plans.get(1).equals(plans.get(2)),"Plans must not be palette swaps");
        h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=100)
    public static void importedEditsAreAppliedToProductionTemplates(GameTestHelper h){
        Map<BlockPos,BlockState> blocks=new HashMap<>();
        var a=new AcademyPiece(DynastyStructures.ACADEMY_PIECE.get(),0,BlockPos.ZERO){
            @Override protected void set(WorldGenLevel l,BoundingBox b,int x,int y,int z,BlockState s){blocks.put(new BlockPos(x,y,z),s);}
            @Override protected boolean createChest(WorldGenLevel l,BoundingBox b,RandomSource r,int x,int y,int z,ResourceLocation t){return true;}
        };
        a.postProcess(null,null,null,RandomSource.create(0),a.getBoundingBox(),null,BlockPos.ZERO);
        h.assertTrue(blocks.values().stream().filter(s -> s.is(Blocks.LIGHT)).count()==297,"Player's academy lighting must be present");
        // Every reviewed row, including deletions, must win over the procedural baseline.
        verifyEdits(h,"academy",blocks);blocks.clear();
        var g=new WallGatePiece(DynastyStructures.WALL_GATE_PIECE.get(),0,BlockPos.ZERO){
            @Override protected void set(WorldGenLevel l,BoundingBox b,int x,int y,int z,BlockState s){blocks.put(new BlockPos(x,y,z),s);}
            @Override protected boolean createChest(WorldGenLevel l,BoundingBox b,RandomSource r,int x,int y,int z,ResourceLocation t){return true;}
        };
        g.postProcess(null,null,null,RandomSource.create(0),g.getBoundingBox(),null,BlockPos.ZERO);
        verifyEdits(h,"gate",blocks);h.succeed();
    }
    static void verifyEdits(GameTestHelper h,String id,Map<BlockPos,BlockState> blocks){
        try(var input=BuildFeedbackGameTests.class.getResourceAsStream("/data/dynasty/build_overrides/"+id+".json")){
            var rows=com.google.gson.JsonParser.parseReader(new java.io.InputStreamReader(input)).getAsJsonArray();
            for(var row:rows){var o=row.getAsJsonObject();var c=o.getAsJsonArray("pos");var s=blocks.get(new BlockPos(c.get(0).getAsInt(),c.get(1).getAsInt(),c.get(2).getAsInt()));
                var expected=net.minecraft.commands.arguments.blocks.BlockStateParser.parseForBlock(net.minecraft.core.registries.BuiltInRegistries.BLOCK.asLookup(),o.get("state").getAsString(),false).blockState();
                h.assertTrue(s.equals(expected),"Imported edit lost: "+row);
            }
        }catch(Exception e){throw new IllegalStateException(e);}
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=100)
    public static void tombEntranceHasContinuousLadderAndBottomExit(GameTestHelper h){
        Map<BlockPos,BlockState> blocks=new HashMap<>();
        var p=new TombAccessPiece(new BlockPos(0,-19,0),65){
            @Override protected void set(WorldGenLevel l,BoundingBox b,int x,int y,int z,BlockState s){
                h.assertTrue(x>=0&&x<6&&z>=0&&z<6&&y>=0&&y<getBoundingBox().getYSpan(),"Shaft outside piece bounds");blocks.put(new BlockPos(x,y,z),s);
            }
        };
        p.postProcess(null,null,null,RandomSource.create(0),p.getBoundingBox(),null,BlockPos.ZERO);
        int top=p.getBoundingBox().getYSpan()-6;
        for(int y=1;y<=top+1;y++)h.assertTrue(blocks.get(new BlockPos(2,y,1)).is(Blocks.LADDER),"Broken ladder at "+y);
        h.assertTrue(blocks.get(new BlockPos(3,1,5)).isAir()&&blocks.get(new BlockPos(3,2,5)).isAir(),"Exit into tomb blocked");
        h.assertTrue(blocks.get(new BlockPos(3,top,0)).isAir()&&blocks.get(new BlockPos(3,top+1,0)).isAir(),"Surface door blocked");
        h.succeed();
    }
}
