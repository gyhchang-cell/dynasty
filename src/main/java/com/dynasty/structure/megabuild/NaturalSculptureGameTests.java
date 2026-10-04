package com.dynasty.structure.megabuild;

import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.gametest.framework.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.ChunkPos;
import net.minecraftforge.gametest.*;

@GameTestHolder("dynasty") @PrefixGameTestTemplate(false)
public final class NaturalSculptureGameTests {
    @GameTest(template="bow_ritual_test",timeoutTicks=200)
    public static void rareSitesAndTilesSurviveSerialization(GameTestHelper h){
        var level=h.getLevel();var source=level.getChunkSource();var generator=source.getGenerator();
        h.assertTrue(NaturalSculptures.cachedCount()==2,"Natural blueprint cache unavailable: "+NaturalSculptures.cachedCount());
        var registry=level.registryAccess().registryOrThrow(Registries.STRUCTURE);
        boolean dragon=false,manor=false;int checked=0;
        for(int region=2;region<250&&!(dragon&&manor);region++){
            var site=NaturalSculptures.site(level.getSeed(),region*625,625);
            var same=NaturalSculptures.site(level.getSeed(),region*625+624,1249);
            h.assertTrue(site.equals(same),"Tile order changed candidate");
            var structure=registry.get(new ResourceLocation("dynasty",site.id()));
            h.assertTrue(structure!=null,"Missing natural structure registry");
            var chunk=new ChunkPos(site.x()>>4,site.z()>>4);
            var start=structure.generate(level.registryAccess(),generator,generator.getBiomeSource(),source.randomState(),level.getStructureManager(),level.getSeed(),chunk,0,level,b->true);
            if(!start.isValid())continue;
            checked++;
            h.assertTrue(start.getPieces().size()==1,"Tile must have one local piece");
            var piece=start.getPieces().get(0);var box=piece.getBoundingBox();
            h.assertTrue(box.minX()>=chunk.getMinBlockX()&&box.maxX()<=chunk.getMaxBlockX()&&box.minZ()>=chunk.getMinBlockZ()&&box.maxZ()<=chunk.getMaxBlockZ(),"Piece escaped its owning chunk");
            var context=net.minecraft.world.level.levelgen.structure.pieces.StructurePieceSerializationContext.fromLevel(level);
            var nbt=piece.createTag(context);var restored=NaturalSculptures.TILE.get().load(context,nbt);
            h.assertTrue(restored.getBoundingBox().equals(box),"Tile bounds lost on reload");
            h.assertTrue(restored.createTag(context).equals(nbt),"Tile origin/identity changed on reload");
            // Exercise real block placement and preserve an outside sentinel.
            level.getChunk(chunk.x,chunk.z);
            BlockPos sentinel=new BlockPos(box.maxX()+1,box.minY()+5,box.minZ());
            level.setBlockAndUpdate(sentinel,net.minecraft.world.level.block.Blocks.DIAMOND_BLOCK.defaultBlockState());
            restored.postProcess(level,level.structureManager(),generator,net.minecraft.util.RandomSource.create(3),box,chunk,BlockPos.ZERO);
            h.assertTrue(level.getBlockState(sentinel).is(net.minecraft.world.level.block.Blocks.DIAMOND_BLOCK),"Write escaped chunk clip");
            int written=0;for(var p:BlockPos.betweenClosed(box.minX(),box.minY(),box.minZ(),box.maxX(),box.maxY(),box.maxZ()))if(!level.isEmptyBlock(p))written++;
            h.assertTrue(written>64,"Natural tile placed no actual model blocks");
            var adjacent=new ChunkPos(chunk.x+1,chunk.z);
            var neighbor=structure.generate(level.registryAccess(),generator,generator.getBiomeSource(),source.randomState(),level.getStructureManager(),level.getSeed(),adjacent,0,level,b->true);
            h.assertTrue(neighbor.isValid()&&neighbor.getBoundingBox().minY()==box.minY(),"Adjacent tile rejected or changed datum");
            if(site.id().equals("yunqi_manor"))manor=true;else dragon=true;
        }
        h.assertTrue(dragon&&manor,"No viable rare sites for both blueprints (checked="+checked+")");h.succeed();
    }
}
