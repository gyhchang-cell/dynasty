package com.dynasty.cod3;

import com.google.gson.*;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.gametest.*;
import software.bernie.geckolib.loading.json.raw.Model;
import software.bernie.geckolib.loading.object.*;
import software.bernie.geckolib.util.JsonUtil;
import java.io.*;
import java.util.*;

@GameTestHolder("dynasty_scenic_qa")
@PrefixGameTestTemplate(false)
public final class GhostShipServerQa {
    private static JsonObject asset(String path)throws Exception{
        try(var stream=GhostShipServerQa.class.getResourceAsStream("/assets/dynasty/"+path);var reader=new InputStreamReader(stream)){return JsonParser.parseReader(reader).getAsJsonObject();}
    }
    @GameTest(template="bow_ritual_test")
    public static void realShipModelsAnimationAnd512PixelAtlasLoad(GameTestHelper h)throws Exception{
        int[] expected={125,91,63};int i=0;
        for(String lod:List.of("","_medium","_far")){
            var json=asset("geo/scenic/ghost_ship"+lod+".geo.json");var raw=JsonUtil.GEO_GSON.fromJson(json,Model.class);
            var tree=GeometryTree.fromModel(raw);var baked=BakedModelFactory.getForNamespace("dynasty").constructGeoModel(tree);
            h.assertTrue(tree.topLevelBones().size()==1&&!baked.topLevelBones().isEmpty(),"Ship is not actually bakeable");
            var bones=json.getAsJsonArray("minecraft:geometry").get(0).getAsJsonObject().getAsJsonArray("bones");
            int count=0;for(var b:bones)count+=b.getAsJsonObject().getAsJsonArray("cubes").size();
            h.assertTrue(bones.size()==8&&count==expected[i++],"Wrong LOD bones/cubes");
        }
        var animation=JsonUtil.GEO_GSON.fromJson(asset("animations/scenic/ghost_ship.animation.json").getAsJsonObject("animations"),BakedAnimations.class).getAnimation("animation.scenic.idle");
        h.assertTrue(animation!=null&&animation.length()==160&&animation.boneAnimations().length>0,"8 second ship animation failed");
        try(var stream=GhostShipServerQa.class.getResourceAsStream("/assets/dynasty/textures/entity/scenic/ghost_ship.png")){
            var image=javax.imageio.ImageIO.read(stream);h.assertTrue(image!=null&&image.getWidth()==512&&image.getHeight()==512,"Final atlas is not 512px PNG");
        }h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=120)
    public static void realLiquidCourseRejectsLandObstaclesAndPersistsDirection(GameTestHelper h){
        var level=h.getLevel();var center=h.absolutePos(new BlockPos(440,200,440));
        for(int x=-10;x<=10;x++)for(int z=-34;z<=34;z++){
            for(int y=-2;y<=12;y++)level.setBlock(center.offset(x,y,z),y<0?Blocks.WATER.defaultBlockState():Blocks.AIR.defaultBlockState(),2);
        }
        level.setDayTime(18000);level.setWeatherParameters(6000,6000,true,false);level.setRainLevel(1);
        var top=center.below();double height=top.getY()+level.getFluidState(top).getHeight(level,top);
        var anchor=new Vec3(center.getX()+.5,height,center.getZ()+.5);var route=new ScenicGhostShipRoute.Route(anchor,new Vec3(0,0,1));
        h.assertTrue(ScenicGhostShipRoute.valid(level,route),"Real deep water corridor rejected");
        h.assertTrue(ScenicGhostShipRoute.nearObserver(level,anchor,new Vec3(1,0,0))!=null,"Observer looking across a river misses nearby safe course");
        var odd=center.offset(3,0,5);level.setBlock(odd,Blocks.STONE.defaultBlockState(),2);
        h.assertTrue(!ScenicGhostShipRoute.valid(level,route),"One-block obstacle between coarse samples missed");level.setBlock(odd,Blocks.AIR.defaultBlockState(),2);
        level.setBlock(center.offset(1,-2,7),Blocks.STONE.defaultBlockState(),2);
        h.assertTrue(!ScenicGhostShipRoute.valid(level,route),"Keel accepts one-block shallows");level.setBlock(center.offset(1,-2,7),Blocks.WATER.defaultBlockState(),2);
        h.assertTrue(!ScenicGhostShipRoute.valid(level,new ScenicGhostShipRoute.Route(anchor,new Vec3(1,0,1))),"Unsafe diagonal packet accepted");
        h.assertTrue(ScenicGhostShipRoute.visibility(level)>0,"Rain night not eligible");
        var scenes=new ScenicEvents();h.assertTrue(scenes.start(level,3,anchor),"Ship cannot start on actual water");var packet=scenes.packets(level,anchor).get(0);
        h.assertTrue(packet.scale()==1&&packet.duration()==1200&&packet.direction().equals(new Vec3(0,0,1))&&packet.entityId()==-1,"Production packet scales hull or restarts lifetime");
        var restored=ScenicEvents.load(scenes.save(new CompoundTag()));h.assertTrue(restored.packets(level,anchor).equals(List.of(packet)),"Saved ship loses route/clock");
        level.setDayTime(6000);h.assertTrue(restored.packets(level,anchor).isEmpty()&&!new ScenicEvents().start(level,3,anchor),"Daytime ship leaks");
        level.setDayTime(18000);level.setRainLevel(0);h.assertTrue(restored.packets(level,anchor).isEmpty(),"Dry overworld ship leaks");
        level.setRainLevel(1);h.assertTrue(ScenicEventDefinition.of(3).allowsDimension("minecraft:overworld")&&ScenicEventDefinition.of(3).allowsDimension("dynasty:underworld")&&!ScenicEventDefinition.of(3).allowsDimension("dynasty:jiuxiao"),"Ship dimension contract changed");
        for(int t=0;t<=1200;t+=7){var at=ScenicGhostShipRoute.position(packet,t);h.assertTrue(Math.abs(at.z-anchor.z)<=16.001&&at.y==anchor.y,"Ship leaves checked watercourse");double a=ScenicGhostShipRoute.alpha(packet,t,30,1);double cue=ScenicGhostShipRoute.soundVolume(packet,t,0,1);h.assertTrue(a>=0&&a<=.86&&cue>=0&&cue<=.06,"Ship opacity/sound exceeds budget");}
        h.assertTrue(ScenicGhostShipRoute.soundVolume(packet,600,41,1)==0&&ScenicGhostShipRoute.alpha(packet,600,5,1)==0,"Near/fullscreen or far/global sound leak");h.succeed();
    }
}
