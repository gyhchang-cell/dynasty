package com.dynasty.structure.megabuild;

import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.world.SimpleContainer;
import net.minecraft.world.item.Items;
import net.minecraftforge.gametest.*;

@GameTestHolder("dynasty_cod6") @PrefixGameTestTemplate(false)
public final class Cod6QuarryGameTests {
    @GameTest(template="bow_ritual_test",timeoutTicks=100)
    public static void solidMirroredOreAndRoutes(GameTestHelper h) {
        MiningEstate.main(new String[0]);
        var b=new MiningEstate(77).blueprint();int minerals=0;
        for(int tier=0;tier<3;tier++)for(int x=10;x<=38;x++)for(int z=14+tier*18;z<=26+tier*18;z++)for(int y=1;y<=3+tier*3;y++) {
            var k=b.at(x,y,z);
            h.assertTrue(k.name().startsWith("ORE_")||k.name().startsWith("RAW_"),"Hollow or non-ore cell");
            h.assertTrue(k==b.at(95-x,y,z),"Unequal mirrored mineral value");minerals+=2;
        }
        for(int rot=0;rot<4;rot++)h.assertTrue(b.rotate(rot).solidCount()==b.solidCount(),"Rotation lost blocks");
        h.assertTrue(b.at(70,3,78).name().startsWith("RAW_")||b.at(70,3,78).name().startsWith("ORE_"),"Former house not mineral");
        System.out.println("COD6 quarry solid bench mineral cells="+minerals);h.succeed();
    }
    @GameTest(template="bow_ritual_test")
    public static void hundredSeedFinalInventoryStatistics(GameTestHelper h) {
        int slots=0,items=0;
        for(int seed=0;seed<100;seed++) {
            var chest=new SimpleContainer(27);MiningRewards.fillNew(chest,seed);int nonempty=0;
            for(int i=0;i<27;i++)if(!chest.getItem(i).isEmpty()) {
                var s=chest.getItem(i);nonempty++;items+=s.getCount();
                h.assertTrue(s.getCount()>=8&&s.getCount()<=12,"Stack outside requested range");
                h.assertTrue(!s.is(Items.IRON_INGOT)&&!s.is(Items.GOLD_INGOT)&&!s.is(Items.COPPER_INGOT),"Smelted reward");
            }
            h.assertTrue(nonempty==9,"Final inventory is not one third full");slots+=nonempty;
            var saved=chest.createTag();MiningRewards.fillNew(chest,999);
            h.assertTrue(saved.equals(chest.createTag()),"Old inventory overwritten");
        }
        double mean=(double)items/slots;h.assertTrue(mean>9.8&&mean<10.2,"Unexpected stack mean "+mean);
        System.out.println("COD6 100 seeds: nonempty="+slots+"/2700, stackMean="+mean);h.succeed();
    }
    @GameTest(template="bow_ritual_test")
    public static void oldLayoutAndPlayerChestPreserved(GameTestHelper h) {
        var level=h.getLevel();var origin=h.absolutePos(new BlockPos(0,2,0));
        var piece=new MegabuildPiece(MegabuildStructures.MINING_PIECE.get(),0,origin,MegabuildStructures::mining,0,0,96,36);
        var pos=origin.offset(39,1,29);level.getChunkAt(pos);
        var clip=new net.minecraft.world.level.levelgen.structure.BoundingBox(pos);
        piece.postProcess(level,level.structureManager(),level.getChunkSource().getGenerator(),level.random,clip,new net.minecraft.world.level.ChunkPos(pos),pos);
        var chest=(net.minecraft.world.level.block.entity.ChestBlockEntity)level.getBlockEntity(pos);
        h.assertTrue(chest!=null,"New mine chest missing");chest.clearContent();chest.setItem(2,new net.minecraft.world.item.ItemStack(Items.DIAMOND,17));
        piece.postProcess(level,level.structureManager(),level.getChunkSource().getGenerator(),level.random,clip,new net.minecraft.world.level.ChunkPos(pos),pos);
        h.assertTrue(chest.getItem(2).getCount()==17&&chest.getItem(2).is(Items.DIAMOND),"Player inventory changed");
        var tag=piece.createTag(null);tag.putInt("MegabuildLayout",4);
        var restored=new MegabuildPiece(MegabuildStructures.MINING_PIECE.get(),tag,MegabuildStructures::mining,96,36);
        h.assertTrue(restored.createTag(null).getInt("MegabuildLayout")==4,"Old layout silently upgraded");
        tag.putInt("MegabuildLayout",5);
        var previousCod6=new MegabuildPiece(MegabuildStructures.MINING_PIECE.get(),tag,MegabuildStructures::mining,96,36);
        h.assertTrue(previousCod6.createTag(null).getInt("MegabuildLayout")==5,"Existing cod6 save was upgraded");
        h.assertTrue(MechanicalPatrols.spiderPositions(previousCod6).isEmpty(),"Legacy solid benches must not spawn spiders inside ore");
        var legacyCell=origin.offset(17,6,66);level.getChunkAt(legacyCell);
        previousCod6.postProcess(level,level.structureManager(),level.getChunkSource().getGenerator(),level.random,
            new net.minecraft.world.level.levelgen.structure.BoundingBox(legacyCell),new net.minecraft.world.level.ChunkPos(legacyCell),legacyCell);
        h.assertTrue(level.getBlockState(legacyCell).isAir(),"Layout 5 unexpectedly gained a gallery roof on reload");
        h.assertTrue(new MiningEstate(0).blueprint().at(17,6,66)==Blueprint.Kind.FLOOR,"Layout 6 gallery roof missing");
        try { MegabuildTemplateExport.write(new MiningEstate(0).blueprint(),java.nio.file.Path.of("../cod6-export/tiangong_mining_estate.nbt")); }
        catch(Exception ex){throw new RuntimeException(ex);}
        h.succeed();
    }
}
