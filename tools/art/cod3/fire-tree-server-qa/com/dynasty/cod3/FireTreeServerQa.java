package com.dynasty.cod3;

import com.dynasty.structure.*;
import com.google.gson.JsonParser;
import net.minecraft.core.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.gametest.framework.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.levelgen.structure.*;
import net.minecraft.world.level.levelgen.structure.pieces.*;
import net.minecraft.world.level.levelgen.structure.templatesystem.*;
import net.minecraftforge.gametest.*;
import java.io.InputStreamReader;
import java.util.*;

@GameTestHolder("dynasty_scenic_qa")
@PrefixGameTestTemplate(false)
public final class FireTreeServerQa {
    @GameTest(template="bow_ritual_test",timeoutTicks=100)
    public static void fireTreeTemplateClipsAcrossChunksAndKeepsLavaSealed(GameTestHelper h){
        var level=h.getLevel();
        // Isolate template placement from pre-existing caves, aquifers and unrelated structures.
        // This fixture tests chunk clipping/sealing, not findGenerationPoint terrain selection.
        var origin=new BlockPos(3200,190,3200);
        var template=level.getStructureManager().get(ScenicFireTreeStructure.ID).orElseThrow();
        h.assertTrue(template.getSize().equals(new Vec3i(47,43,47)),"Native fire-tree NBT size changed");
        var saved=template.save(new CompoundTag());h.assertTrue(saved.getList("entities",10).isEmpty(),"Tree NBT carries entities");
        for(var raw:saved.getList("blocks",10))h.assertTrue(!((CompoundTag)raw).contains("nbt"),"Tree NBT contains block entities");
        var piece=new ScenicFireTreeStructure.Piece(level.getStructureManager(),origin);var bounds=piece.getBoundingBox();
        for(int x=bounds.minX()>>4;x<=bounds.maxX()>>4;x++)for(int z=bounds.minZ()>>4;z<=bounds.maxZ()>>4;z++)level.getChunk(x,z);
        for(var p:BlockPos.betweenClosed(bounds.minX(),bounds.minY(),bounds.minZ(),bounds.maxX(),bounds.maxY(),bounds.maxZ()))level.setBlock(p,Blocks.AIR.defaultBlockState(),2);
        var ids=new HashSet<UUID>();for(var entity:level.getAllEntities())ids.add(entity.getUUID());
        var sentinel=origin.offset(-1,12,20);level.setBlock(sentinel,Blocks.DIAMOND_BLOCK.defaultBlockState(),2);
        for(int x=bounds.minX()>>4;x<=bounds.maxX()>>4;x++)for(int z=bounds.minZ()>>4;z<=bounds.maxZ()>>4;z++){
            var chunk=new ChunkPos(x,z);var clip=new BoundingBox(chunk.getMinBlockX(),level.getMinBuildHeight(),chunk.getMinBlockZ(),chunk.getMaxBlockX(),level.getMaxBuildHeight()-1,chunk.getMaxBlockZ());
            piece.postProcess(level,level.structureManager(),level.getChunkSource().getGenerator(),level.random,clip,chunk,origin);
        }
        h.assertTrue(level.getBlockState(sentinel).is(Blocks.DIAMOND_BLOCK),"Template writes outside its bounds");
        for(var entity:level.getAllEntities())if(bounds.isInside(entity.blockPosition()))h.assertTrue(ids.contains(entity.getUUID()),"Tree placement created entity inside its bounds "+entity.getType()+" at "+entity.blockPosition()+" bounds="+bounds);
        var missingLava=new ArrayList<String>();
        var palette=saved.getList("palette",10);
        for(var raw:saved.getList("blocks",10)){var block=(CompoundTag)raw;if(!palette.getCompound(block.getInt("state")).getString("Name").equals("minecraft:lava"))continue;var pos=block.getList("pos",3);var at=origin.offset(pos.getInt(0),pos.getInt(1),pos.getInt(2));if(!level.getBlockState(at).is(Blocks.LAVA))missingLava.add(at+"="+level.getBlockState(at));}
        int lava=0,lights=0;
        for(var p:BlockPos.betweenClosed(bounds.minX(),bounds.minY(),bounds.minZ(),bounds.maxX(),bounds.maxY(),bounds.maxZ())){
            var state=level.getBlockState(p);if((state.is(Blocks.OCHRE_FROGLIGHT)||state.is(Blocks.SHROOMLIGHT)))lights++;
            if(!state.is(Blocks.LAVA))continue;lava++;
            for(var direction:List.of(Direction.NORTH,Direction.SOUTH,Direction.WEST,Direction.EAST,Direction.DOWN)){
                var neighbor=level.getBlockState(p.relative(direction));h.assertTrue(neighbor.is(Blocks.LAVA)||neighbor.isSolid(),"Unsealed lava at "+p);
            }
        }
        h.assertTrue(lava==424&&lights==20,"Actual chunk-clipped ravine loses lava or lights: "+lava+"/"+lights+" missing="+missingLava);
        for(int x:new int[]{6,7,8,38,39,40})h.assertTrue(level.isEmptyBlock(origin.offset(x,7,0))&&level.isEmptyBlock(origin.offset(x,8,0))&&level.getBlockState(origin.offset(x,6,0)).isSolid(),"Entry stairs obstructed or floating");
        var context=StructurePieceSerializationContext.fromLevel(level);var restored=DynastyStructures.SCENIC_FIRE_TREE_PIECE.get().load(context,piece.createTag(context));
        h.assertTrue(restored.getBoundingBox().equals(bounds),"Saved piece loses origin or bounds");h.succeed();
    }

    @GameTest(template="bow_ritual_test")
    public static void fireTreeSyncUsesLoadedStructureAndStableWorldClock(GameTestHelper h){
        var level=h.getLevel();var structure=level.registryAccess().registryOrThrow(Registries.STRUCTURE).get(ScenicFireTreeStructure.ID);
        h.assertTrue(structure instanceof ScenicFireTreeStructure&&structure.spawnOverrides().isEmpty(),"Fire tree lacks actual non-mob structure registry");
        var origin=h.absolutePos(new BlockPos(-200,30,-200));var viewer=origin.offset(24,20,24);
        h.assertTrue(ScenicFireTreeSite.originNear(level,viewer).isEmpty(),"Height alone invents a fire tree");
        var piece=new ScenicFireTreeStructure.Piece(level.getStructureManager(),origin);var cp=new ChunkPos(origin);
        var start=new StructureStart(structure,cp,0,new PiecesContainer(List.of(piece)));level.getChunk(cp.x,cp.z).setStartForStructure(structure,start);
        h.assertTrue(ScenicFireTreeSite.originNear(level,viewer).orElseThrow().equals(origin),"Loaded start does not supply actual template origin");
        h.assertTrue(ScenicFireTreeSite.originNear(level,origin.offset(500,20,500)).isEmpty(),"Fire tree reaches distant viewer");
        var packet=ScenicFireTreeSite.packet(level,origin);h.assertTrue(packet.valid()&&packet.entityId()==-1&&packet.duration()==2400&&packet.scale()==1&&packet.origin().equals(net.minecraft.world.phys.Vec3.atLowerCornerOf(origin)),"Site packet violates structure frame or bounds");
        h.assertTrue(!new ScenicEvents().start(level,13,packet.origin()),"Old free-floating timed tree can still start");
        h.assertTrue(ScenicFireTreeSite.night(18000,0)&&!ScenicFireTreeSite.night(6000,0)&&!ScenicFireTreeSite.night(18000,1),"Site ignores day/rain gate");h.succeed();
    }

    @GameTest(template="bow_ritual_test")
    public static void fireTreePixelsRemainBudBoundAndBelowSparkBudget(GameTestHelper h)throws Exception{
        var points=new ArrayList<ScenicAurora.Point>();
        try(var stream=FireTreeServerQa.class.getResourceAsStream("/assets/dynasty/scenic/fire_tree.json");var reader=new InputStreamReader(stream)){
            for(var v:JsonParser.parseReader(reader).getAsJsonObject().getAsJsonArray("bud_centers")){var p=v.getAsJsonArray();points.add(new ScenicAurora.Point(p.get(0).getAsDouble(),p.get(1).getAsDouble(),p.get(2).getAsDouble()));}
        }
        for(int tick=0;tick<2400;tick+=17)for(boolean low:List.of(false,true)){
            var quads=ScenicFireTreeLight.mesh(1518,tick,30,low,1,points);h.assertTrue(!quads.isEmpty()&&quads.size()<=160,"Spark budget exceeded");
            for(var q:quads)for(var p:List.of(q.a(),q.b(),q.c(),q.d()))h.assertTrue(Double.isFinite(p.x()+p.y()+p.z())&&points.stream().anyMatch(b->Math.abs(p.x()-b.x())<2&&Math.abs(p.z()-b.z())<2&&p.y()>=b.y()&&p.y()<b.y()+6),"Spark detached from a real bud");
        }
        h.assertTrue(ScenicFireTreeLight.mesh(1,100,161,false,1,points).isEmpty()&&ScenicFireTreeLight.mesh(1,100,30,false,0,points).isEmpty(),"Sparks survive region/weather exit");
        h.assertTrue(ScenicFireTreeLight.soundVolume(0,1)<=.07&&ScenicFireTreeLight.soundVolume(49,1)==0,"Crackle is too loud or global");h.succeed();
    }
}
