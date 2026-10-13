package com.dynasty.client;

import com.dynasty.cod3.*;
import com.google.gson.*;
import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.*;
import net.minecraft.client.*;
import net.minecraft.client.gui.screens.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.level.*;
import net.minecraft.world.level.levelgen.WorldOptions;
import net.minecraft.world.level.levelgen.presets.WorldPresets;
import net.minecraft.world.entity.decoration.ArmorStand;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.lwjgl.glfw.GLFW;
import org.lwjgl.opengl.GL11;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.CompletableFuture;

/** Single silent, hidden integrated client. A disposable world; never opens a user's save. */
@Mod.EventBusSubscriber(modid="dynasty",value=Dist.CLIENT)
public final class ScenicQa {
    private static final Path OUT=Path.of(System.getProperty("dynasty.scenicQa.output","build/scenic-unset"));
    private static final List<String> RESULTS=new ArrayList<>();
    private static final List<Map<String,Object>> VIEWS=new ArrayList<>();
    private static final int[] NUMBERS={1,10,25};
    private static final int[] ANGLES={180,135,90,-90,0,135};
    private static boolean started,done,hidden;
    private static int stage,settle;
    private static CompletableFuture<Void> prepare,reload;
    private static ArmorStand camera;
    private static final Vec3 ANCHOR=new Vec3(0,-60,0);
    private static final long DEADLINE=System.nanoTime()+240_000_000_000L;
    private static void require(boolean ok,String label){if(!ok)throw new AssertionError(label);RESULTS.add("PASS "+label);}
    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent e){
        if(!Boolean.getBoolean("dynasty.scenicQa")||done||e.phase!=TickEvent.Phase.END)return;
        var mc=Minecraft.getInstance();
        try{
            Files.createDirectories(OUT);
            if(!hidden){GLFW.glfwHideWindow(mc.getWindow().getWindow());hidden=true;mc.options.getSoundSourceOptionInstance(net.minecraft.sounds.SoundSource.MASTER).set(0.0);}
            if(System.nanoTime()>DEADLINE)throw new AssertionError("Scenic QA deadline");
            if(mc.getOverlay()!=null)return;
            if(mc.screen instanceof AccessibilityOnboardingScreen)mc.setScreen(new TitleScreen());
            if(!started&&mc.screen instanceof TitleScreen){
                started=true;mc.options.pauseOnLostFocus=false;mc.options.hideGui=true;mc.options.fov().set(55);mc.options.renderDistance().set(4);mc.options.framerateLimit().set(40);
                var rules=new GameRules();rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false,null);rules.getRule(GameRules.RULE_DAYLIGHT).set(false,null);rules.getRule(GameRules.RULE_WEATHER_CYCLE).set(false,null);
                mc.createWorldOpenFlows().createFreshLevel("scenic-qa",new LevelSettings("Disposable scenic QA",GameType.CREATIVE,false,net.minecraft.world.Difficulty.PEACEFUL,true,rules,WorldDataConfiguration.DEFAULT),new WorldOptions(31011,false,false),r->r.registryOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.FLAT).createWorldDimensions());return;
            }
            if(mc.level==null||mc.player==null)return;if(mc.screen!=null)mc.setScreen(null);
            if(prepare==null){
                prepare=mc.getSingleplayerServer().submit(()->{
                    var l=mc.getSingleplayerServer().overworld();var data=ScenicEvents.get(l);l.setDayTime(1000);
                    for(int n:NUMBERS)require(data.start(l,n,ANCHOR),"registered scenic "+n+" starts");
                    var packets=data.packets(l,ANCHOR);require(packets.size()==3,"three bounded visual packets, without mob creation");
                    var tag=data.save(new CompoundTag());require(tag.getList("Active",10).size()==3,"all original anchors/seeds/start times persisted");
                    var p=mc.getSingleplayerServer().getPlayerList().getPlayers().get(0);p.teleportTo(l,0,-60,-100,0,0);
                });return;
            }
            if(!prepare.isDone())return;prepare.join();
            if(stage>=18){
                if(reload==null){reload=mc.reloadResourcePacks();return;}
                if(!reload.isDone())return;reload.join();
                for(String id:List.of("azure_dragon","mountain_xuanwu","sun_crow")){
                    for(String lod:List.of("","_medium","_far")){
                        var actor=new ScenicModels.Actor(id,0);var model=ScenicModels.renderer(id,lod).getGeoModel();
                        require(!model.getBakedModel(model.getModelResource(actor)).topLevelBones().isEmpty(),id+lod+" real GeckoLib model after resource reload");
                        require(model.getAnimation(actor,"animation.scenic.idle")!=null,id+lod+" real animation after resource reload");
                    }
                }
                Files.write(OUT.resolve("PASS.txt"),RESULTS);Files.writeString(OUT.resolve("views.json"),new GsonBuilder().setPrettyPrinting().create().toJson(VIEWS));done=true;mc.stop();return;
            }
            if(settle==0){
                clear();int number=NUMBERS[stage/6];int angle=ANGLES[stage%6];
                // Each angle resumes at a different authoritative age: no observer-local restart.
                long age=160+stage%6*13;long start=mc.level.getGameTime()-age;
                var p=new Cod3VisualPacket(mc.level.dimension().location().toString(),ScenicEventDefinition.of(number).template(),-1,117+number,start,ScenicEventDefinition.of(number).duration(),4,ANCHOR,new Vec3(0,0,1),String.format(Locale.ROOT,"scenic_%02d",number),(int)age);
                Cod3VfxRenderer.receive(p);
                double radius=stage%6==5?64:96;double radians=Math.toRadians(angle);double centerY=number==10?-49:-9;Vec3 target=new Vec3(0,centerY,0);
                Vec3 at=new Vec3(Math.sin(radians)*radius,centerY+7,-Math.cos(radians)*radius);
                camera=new ArmorStand(mc.level,at.x,at.y-1.975,at.z);
                float yaw=(float)Math.toDegrees(Math.atan2(-(target.x-at.x),target.z-at.z));float pitch=(float)-Math.toDegrees(Math.atan2(target.y-at.y,radius));
                camera.setYRot(yaw);camera.setYHeadRot(yaw);camera.setXRot(pitch);camera.setOldPosAndRot();mc.setCameraEntity(camera);
                if(stage%6==5)mc.getSingleplayerServer().submit(()->mc.getSingleplayerServer().overworld().setDayTime(18000));
                else mc.getSingleplayerServer().submit(()->mc.getSingleplayerServer().overworld().setDayTime(1000));
            }
            settle++;
        }catch(Throwable t){finish(t);}
    }
    @SuppressWarnings("unchecked") private static void clear()throws Exception{
        var field=Cod3VfxRenderer.class.getDeclaredField("ACTIVE");field.setAccessible(true);((List<Cod3VisualPacket>)field.get(null)).clear();ScenicModels.clear();
    }
    @SubscribeEvent public static void capture(TickEvent.RenderTickEvent e){
        if(!Boolean.getBoolean("dynasty.scenicQa")||done||e.phase!=TickEvent.Phase.END||settle<32||stage>=18)return;
        try{
            var mc=Minecraft.getInstance();var id=new String[]{"azure_dragon","mountain_xuanwu","sun_crow"}[stage/6];
            String lod=ScenicModels.lod(ANCHOR.distanceTo(mc.gameRenderer.getMainCamera().getPosition()),false);
            var renderer=ScenicModels.renderer(id,lod);var bones=renderer.getGeoModel().getAnimationProcessor().getRegisteredBones();
            require(!bones.isEmpty(),id+" production draw has actual bones, stage "+stage);
            double motion=bones.stream().mapToDouble(b->Math.abs(b.getRotX())+Math.abs(b.getRotY())+Math.abs(b.getRotZ())).sum();
            require(motion>.001,id+" exported animation actually moves joints, stage "+stage);
            int error=GL11.glGetError();require(error==GL11.GL_NO_ERROR,"world renderer GL state "+stage);
            try(var image=Screenshot.takeScreenshot(mc.getMainRenderTarget())){image.writeToFile(OUT.resolve(String.format(Locale.ROOT,"%02d-%s-%d.png",stage,id,ANGLES[stage%6])));}
            VIEWS.add(Map.of("model",id,"lod",lod,"stage",stage,"angle",ANGLES[stage%6],"night",stage%6==5,"distance",stage%6==5?64:96,"boneRotationSum",motion));
            stage++;settle=0;
        }catch(Throwable t){finish(t);}
    }
    private static void finish(Throwable t){done=true;t.printStackTrace();try{Files.writeString(OUT.resolve("FAIL.txt"),t.toString());Files.write(OUT.resolve("partial.txt"),RESULTS);}catch(Exception ignored){}Minecraft.getInstance().stop();}
}
