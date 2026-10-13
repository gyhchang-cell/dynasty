package com.dynasty.cod3;

import com.google.gson.*;
import io.netty.buffer.Unpooled;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.nbt.*;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.gametest.*;
import software.bernie.geckolib.loading.json.raw.Model;
import software.bernie.geckolib.loading.object.*;
import software.bernie.geckolib.util.JsonUtil;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

/** Opt-in headless acceptance: no release classes, no rendering, no user's world. */
@GameTestHolder("dynasty_scenic_qa")
@PrefixGameTestTemplate(false)
public final class ScenicServerQa {
    private static JsonObject asset(String path) throws IOException {
        try(var input=ScenicServerQa.class.getResourceAsStream("/assets/dynasty/"+path)){
            if(input==null)throw new FileNotFoundException(path);
            return JsonParser.parseReader(new InputStreamReader(input,StandardCharsets.UTF_8)).getAsJsonObject();
        }
    }
    @GameTest(template="bow_ritual_test")
    public static void actualGeckoLibDecodesAllNineModelsAndThreeAnimations(GameTestHelper h)throws Exception {
        for(String id:List.of("azure_dragon","mountain_xuanwu","sun_crow")){
            int previous=Integer.MAX_VALUE;
            for(String lod:List.of("","_medium","_far")){
                var json=asset("geo/scenic/"+id+lod+".geo.json");
                var raw=JsonUtil.GEO_GSON.fromJson(json,Model.class);
                var tree=GeometryTree.fromModel(raw);
                h.assertTrue(tree.topLevelBones().size()==1,"Model root invalid: "+id+lod);
                var baked=BakedModelFactory.getForNamespace("dynasty").constructGeoModel(tree);
                h.assertTrue(!baked.topLevelBones().isEmpty(),"Actual GeckoLib bake failed: "+id+lod);
                int cubes=0;
                for(var b:json.getAsJsonArray("minecraft:geometry").get(0).getAsJsonObject().getAsJsonArray("bones"))cubes+=b.getAsJsonObject().getAsJsonArray("cubes").size();
                h.assertTrue(cubes>0&&cubes<previous,"LOD does not reduce geometry: "+id+lod);previous=cubes;
            }
            var animation=JsonUtil.GEO_GSON.fromJson(asset("animations/scenic/"+id+".animation.json").getAsJsonObject("animations"),BakedAnimations.class).getAnimation("animation.scenic.idle");
            h.assertTrue(animation!=null&&animation.length()==80&&animation.boneAnimations().length>0,"Real animation unavailable: "+id);
            try(var input=ScenicServerQa.class.getResourceAsStream("/assets/dynasty/textures/entity/scenic/"+id+".png")){
                var png=javax.imageio.ImageIO.read(input);
                h.assertTrue(png!=null&&png.getWidth()==png.getHeight()&&(png.getWidth()==128||png.getWidth()==256),"PNG unusable: "+id);
            }
        }
        h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=60)
    public static void redesignedScenesPersistAndLateViewersResumeOriginalPackets(GameTestHelper h){
        var level=h.getLevel();var anchor=Vec3.atCenterOf(h.absolutePos(new BlockPos(3,2,3)));var scenes=new ScenicEvents();
        int entityCount=0;for(var ignored:level.getAllEntities())entityCount++;
        for(int number:new int[]{1,10,25})h.assertTrue(scenes.start(level,number,anchor),"Scenic start rejected "+number);
        int after=0;for(var ignored:level.getAllEntities())after++;
        h.assertTrue(after==entityCount,"Scenery created server entities");
        var packets=scenes.packets(level,anchor);h.assertTrue(packets.size()==3,"Missing scene");
        var restored=ScenicEvents.load(scenes.save(new CompoundTag()));
        h.assertTrue(restored.packets(level,anchor).equals(packets),"Save/reload changes anchor, seed or original start");
        for(var packet:packets){
            h.assertTrue(packet.valid()&&packet.entityId()==-1&&packet.scale()==4,"Invalid model packet");
            var buf=new FriendlyByteBuf(Unpooled.buffer());
            try{Cod3VisualPacket.encode(packet,buf);h.assertTrue(Cod3VisualPacket.decode(buf).equals(packet),"Packet codec changes scene");}finally{buf.release();}
        }
        h.runAtTickTime(20,()->{
            var late=restored.packets(level,anchor);h.assertTrue(late.size()==3,"Late observer lost scenes");
            for(int i=0;i<3;i++)h.assertTrue(late.get(i).start()==packets.get(i).start()&&late.get(i).seed()==packets.get(i).seed()&&late.get(i).tick()>=20,"Late observation restarts animation");
            h.succeed();
        });
    }
    @GameTest(template="bow_ritual_test")
    public static void sceneBudgetDuplicatesAndRangeRemainBounded(GameTestHelper h){
        var level=h.getLevel();var anchor=Vec3.atCenterOf(h.absolutePos(new BlockPos(3,2,3)));var scenes=new ScenicEvents();
        // #3 belongs to the underworld; fill only legal overworld definitions.
        for(int number:new int[]{1,2,4,5,6,7,8,9})h.assertTrue(scenes.start(level,number,anchor),"Could not fill legal budget: "+number);
        h.assertTrue(!scenes.start(level,10,anchor)&&!scenes.start(level,1,anchor)&&!scenes.start(level,0,anchor)&&!scenes.start(level,25,new Vec3(Double.NaN,0,0)),"Invalid/duplicate/overflow scene accepted");
        h.assertTrue(scenes.packets(level,anchor.add(256,0,0)).size()==8&&scenes.packets(level,anchor.add(256.01,0,0)).isEmpty(),"Scene region boundary changed");
        h.succeed();
    }
    @GameTest(template="bow_ritual_test")
    public static void restoredExpiredAndFutureScenesCannotRemainActive(GameTestHelper h){
        var level=h.getLevel();var at=Vec3.atCenterOf(h.absolutePos(new BlockPos(3,2,3)));var scenes=new ScenicEvents();
        for(int n:new int[]{1,10,25})scenes.start(level,n,at);
        var saved=scenes.save(new CompoundTag());var entries=saved.getList("Active",10);
        entries.getCompound(0).putLong("Start",level.getGameTime()-ScenicEventDefinition.of(1).duration());
        entries.getCompound(1).putLong("Start",level.getGameTime()+1);
        entries.getCompound(2).putInt("Duration",Integer.MAX_VALUE);
        var packets=ScenicEvents.load(saved).packets(level,at);
        h.assertTrue(packets.size()==1&&packets.get(0).sequence().equals("scenic_25")&&packets.get(0).duration()==ScenicEventDefinition.of(25).duration(),"Restore retained expired/future/tampered lifetime");
        h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=100)
    public static void permanentCavesActuallyPlaceAndRetainClearLitCrossings(GameTestHelper h){
        var level=h.getLevel();int index=0;
        for(String id:List.of("scenic_crystal_canopy","scenic_ice_bloom")){
            var template=level.getStructureManager().getOrCreate(new net.minecraft.resources.ResourceLocation("dynasty",id));
            h.assertTrue(template.getSize().equals(new net.minecraft.core.Vec3i(31,19,31)),"Invalid native NBT dimensions: "+id);
            var origin=h.absolutePos(new BlockPos(0,18,60+index++*40));
            int before=0;for(var ignored:level.getAllEntities())before++;
            h.assertTrue(template.placeInWorld(level,origin,origin,new net.minecraft.world.level.levelgen.structure.templatesystem.StructurePlaceSettings().setIgnoreEntities(false).setKeepLiquids(false).setKnownShape(true),level.random,2),"Template not placed: "+id);
            int after=0;for(var ignored:level.getAllEntities())after++;
            h.assertTrue(before==after,"Permanent cave creates an entity");
            for(int i=0;i<31;i++)for(var floor:List.of(origin.offset(15,0,i),origin.offset(i,0,15))){
                h.assertTrue(level.getBlockState(floor).isSolid(),"Broken crossing floor: "+id);
                for(int y=1;y<=4;y++)h.assertTrue(level.isEmptyBlock(floor.above(y)),"Blocked portal/crossing: "+id);
            }
            var light=origin.offset(id.contains("crystal")?10:7,id.contains("crystal")?15:5,id.contains("crystal")?12:7);
            h.assertTrue(level.getBlockState(light).is(net.minecraft.world.level.block.Blocks.SEA_LANTERN)&&level.getBlockState(light).getLightEmission(level,light)==15,"Cave has no permanent block light");
            h.assertTrue(java.util.Arrays.stream(net.minecraft.core.Direction.values()).anyMatch(d->level.isEmptyBlock(light.relative(d))),"Lamp is sealed inside opaque cubes");
            var roundtrip=new net.minecraft.world.level.levelgen.structure.templatesystem.StructureTemplate();
            roundtrip.load(level.registryAccess().registryOrThrow(net.minecraft.core.registries.Registries.BLOCK).asLookup(),template.save(new CompoundTag()));
            h.assertTrue(roundtrip.getSize().equals(template.getSize()),"Native NBT roundtrip loses cave");
        }
        h.succeed();
    }
    @GameTest(template="bow_ritual_test")
    public static void caveRegistryProducesOnlyOneUndergroundJigsawPiece(GameTestHelper h){
        var level=h.getLevel();var registry=level.registryAccess();var generator=level.getChunkSource().getGenerator();
        var biomes=registry.registryOrThrow(net.minecraft.core.registries.Registries.BIOME);
        for(String id:List.of("scenic_crystal_canopy","scenic_ice_bloom")){
            var structure=registry.registryOrThrow(net.minecraft.core.registries.Registries.STRUCTURE).get(new net.minecraft.resources.ResourceLocation("dynasty",id));
            h.assertTrue(structure instanceof net.minecraft.world.level.levelgen.structure.structures.JigsawStructure,"Missing actual structure registry: "+id);
            h.assertTrue(structure.spawnOverrides().isEmpty(),"Scenery contains mob spawning override");
            var start=structure.generate(registry,generator,generator.getBiomeSource(),level.getChunkSource().randomState(),level.getStructureManager(),level.getSeed(),new net.minecraft.world.level.ChunkPos(0,0),0,level,b->true);
            h.assertTrue(start.isValid()&&start.getPieces().size()==1,"Jigsaw did not produce a single bounded piece: "+id);
            var bounds=start.getBoundingBox();h.assertTrue(bounds.minY()>=-64&&bounds.maxY()<0&&bounds.getXSpan()==31&&bounds.getZSpan()==31,"Cave escapes underground bounds: "+id);
            if(id.contains("ice"))h.assertTrue(!structure.biomes().contains(biomes.getHolderOrThrow(net.minecraft.world.level.biome.Biomes.PLAINS))&&structure.biomes().contains(biomes.getHolderOrThrow(net.minecraft.world.level.biome.Biomes.FROZEN_PEAKS)),"Ice cave ignores cold biome rule");
        }
        h.succeed();
    }
}
