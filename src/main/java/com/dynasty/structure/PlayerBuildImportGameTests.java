package com.dynasty.structure;

import com.dynasty.Dynasty;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;

@GameTestHolder(Dynasty.MODID)
@PrefixGameTestTemplate(false)
public class PlayerBuildImportGameTests {
    @GameTest(template="bow_ritual_test",timeoutTicks=100)
    public static void exportBaselineForReadOnlyBuildComparison(GameTestHelper h) throws Exception {
        String directory=System.getProperty("dynasty.exportLayouts");
        if(directory==null){h.succeed();return;}
        var rows=new java.util.TreeMap<String,String>();
        var academy=new AcademyPiece(DynastyStructures.ACADEMY_PIECE.get(),0,BlockPos.ZERO){
            @Override protected void set(WorldGenLevel l,BoundingBox b,int x,int y,int z,BlockState s){rows.put(x+","+y+","+z,net.minecraft.commands.arguments.blocks.BlockStateParser.serialize(s));}
            @Override protected boolean createChest(WorldGenLevel l,BoundingBox b,RandomSource r,int x,int y,int z,ResourceLocation loot){return true;}
        };
        academy.postProcess(null,null,null,RandomSource.create(0),academy.getBoundingBox(),new net.minecraft.world.level.ChunkPos(0,0),BlockPos.ZERO);
        var root=java.nio.file.Path.of(directory);java.nio.file.Files.createDirectories(root);
        var gson=new com.google.gson.Gson();
        java.nio.file.Files.writeString(root.resolve("academy-baseline.json"),gson.toJson(rows));rows.clear();
        var gate=new WallGatePiece(DynastyStructures.WALL_GATE_PIECE.get(),0,BlockPos.ZERO){
            @Override protected void set(WorldGenLevel l,BoundingBox b,int x,int y,int z,BlockState s){rows.put(x+","+y+","+z,net.minecraft.commands.arguments.blocks.BlockStateParser.serialize(s));}
            @Override protected boolean createChest(WorldGenLevel l,BoundingBox b,RandomSource r,int x,int y,int z,ResourceLocation loot){return true;}
        };
        gate.postProcess(null,null,null,RandomSource.create(0),gate.getBoundingBox(),new net.minecraft.world.level.ChunkPos(0,0),BlockPos.ZERO);
        java.nio.file.Files.writeString(root.resolve("gate-baseline.json"),gson.toJson(rows));h.succeed();
    }
}
