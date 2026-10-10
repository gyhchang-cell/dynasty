package com.dynasty.client;

import com.dynasty.expansion.SecondaryMob;
import com.dynasty.expansion.SecondaryMobs;
import com.google.gson.GsonBuilder;
import net.minecraft.client.*;
import net.minecraft.client.gui.screens.*;
import net.minecraft.core.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.Difficulty;
import net.minecraft.world.entity.decoration.ArmorStand;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.levelgen.*;
import net.minecraft.world.level.levelgen.presets.WorldPresets;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import software.bernie.geckolib.renderer.GeoEntityRenderer;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.CompletableFuture;

/** Art-resource acceptance in a real disposable integrated world, not gameplay acceptance. */
@Mod.EventBusSubscriber(modid="dynasty",value=Dist.CLIENT)
public final class SecondaryArtClientQa {
    private static final boolean ENABLED=Boolean.getBoolean("dynasty.secondaryArtQa");
    private static final Path OUT=Path.of(System.getProperty("dynasty.secondaryArtQa.output","build/secondary-art-native/results"));
    private static final String[] IDS=System.getProperty("dynasty.secondaryArtQa.ids","river_imp,tree_spirit,shrimp_soldier").split(",");
    private static final String[] CLIPS={"idle","wander","hunt","flee","attack","special","evade"};
    private static final List<String> LOG=new ArrayList<>();
    private static boolean started,done,captured;
    private static int stage=-1,settled;
    private static long deadline=System.nanoTime()+600_000_000_000L;
    private static CompletableFuture<Integer> pending;
    private static int entityId;
    private static SecondaryMob fixture;

    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent event){
        if(!ENABLED||done||event.phase!=TickEvent.Phase.END)return;
        var mc=Minecraft.getInstance();
        try{
            // The launch agent also prevents window creation from focusing or showing.
            org.lwjgl.glfw.GLFW.glfwHideWindow(mc.getWindow().getWindow());
            if(System.nanoTime()>deadline)throw new AssertionError("Art QA timeout");
            if(org.lwjgl.glfw.GLFW.glfwGetWindowAttrib(mc.getWindow().getWindow(),org.lwjgl.glfw.GLFW.GLFW_VISIBLE)!=0)throw new AssertionError("Window was shown");
            if(mc.getOverlay()!=null)return;
            if(mc.screen instanceof AccessibilityOnboardingScreen)mc.setScreen(new TitleScreen());
            if(!started&&mc.screen instanceof TitleScreen){
                if(!mc.gameDirectory.getCanonicalPath().contains("/build/secondary-art-native/"))throw new AssertionError("Refusing normal save directory");
                Files.createDirectories(OUT);started=true;
                mc.options.pauseOnLostFocus=false;mc.options.renderDistance().set(3);mc.options.fov().set(50);mc.options.hideGui=true;mc.options.bobView().set(false);
                mc.options.getSoundSourceOptionInstance(net.minecraft.sounds.SoundSource.MASTER).set(0.0);
                var rules=new GameRules();rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false,null);rules.getRule(GameRules.RULE_DAYLIGHT).set(false,null);
                mc.createWorldOpenFlows().createFreshLevel("secondary-art-"+System.currentTimeMillis(),
                    new LevelSettings("Disposable silent art QA",GameType.CREATIVE,false,Difficulty.NORMAL,true,rules,WorldDataConfiguration.DEFAULT),
                    new WorldOptions(57,false,false),registry->registry.registryOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.FLAT).createWorldDimensions());return;
            }
            if(mc.level==null||mc.player==null)return;
            if(mc.screen!=null)mc.setScreen(null);
            if(pending!=null){if(!pending.isDone())return;entityId=pending.join();pending=null;settled=0;captured=false;setCamera(mc);return;}
            if(stage<0||captured){
                if(stage==IDS.length*11-1){finish(mc,null);return;}
                stage++;pending=mc.getSingleplayerServer().submit(()->{try{return prepare(mc,stage);}catch(Exception e){throw new RuntimeException(e);}});return;
            }
            if(mc.level.getEntity(entityId) instanceof SecondaryMob)settled++;
        }catch(Throwable e){finish(mc,e);}
    }
    private static int prepare(Minecraft mc,int s)throws Exception{
        var server=mc.getSingleplayerServer();var world=server.overworld();world.setDayTime(6000);
        if(fixture!=null)fixture.discard();
        for(int x=-9;x<=9;x++)for(int z=-9;z<=9;z++)world.setBlockAndUpdate(new BlockPos(x,-61,z),Blocks.STONE.defaultBlockState());
        String id=IDS[s/11];
        fixture=(id.equals("shrimp_soldier")?SecondaryMobs.SHRIMP.get():SecondaryMobs.TYPES.get(id).get()).create(world);
        fixture.moveTo(0,-60,0,0,0);fixture.setNoAi(true);fixture.setNoGravity(true);fixture.setPersistenceRequired();world.addFreshEntity(fixture);
        int pose=s%11;int state=pose<4?0:pose-4;
        // QA only: select existing synchronized art states. This makes no claim
        // that combat, natural spawning or real-player scenarios were exercised.
        var method=SecondaryMob.class.getDeclaredMethod("animate",int.class,int.class);method.setAccessible(true);method.invoke(fixture,state,10000);
        server.getPlayerList().getPlayers().forEach(p->{p.setGameMode(GameType.CREATIVE);p.teleportTo(world,0,-60,10,180,0);});
        return fixture.getId();
    }
    private static void setCamera(Minecraft mc){
        int pose=stage%11;double yaw=pose==1?45:pose==2?90:pose==3?180:0;
        double angle=Math.toRadians(yaw),distance=IDS[stage/11].equals("tree_spirit")?5.7:3.9;
        var camera=new ArmorStand(mc.level,Math.sin(angle)*distance,-60,Math.cos(angle)*distance);
        double height=IDS[stage/11].equals("shrimp_soldier")?1.25:SecondaryMobs.SPECS.stream().filter(s->s.id().equals(IDS[stage/11])).findFirst().orElseThrow().height();
        camera.setPos(camera.getX(),-60+height/2-camera.getEyeHeight(),camera.getZ());
        camera.setNoGravity(true);camera.setYRot((float)(180-yaw));camera.setXRot(0);camera.setYHeadRot(camera.getYRot());camera.yHeadRotO=camera.getYRot();camera.setOldPosAndRot();
        mc.options.setCameraType(CameraType.FIRST_PERSON);mc.setCameraEntity(camera);
    }
    @SubscribeEvent public static void render(TickEvent.RenderTickEvent event){
        if(!ENABLED||done||captured||pending!=null||stage<0||settled<24||event.phase!=TickEvent.Phase.END)return;
        var mc=Minecraft.getInstance();if(!(mc.level.getEntity(entityId) instanceof SecondaryMob mob))return;
        try{
            if(!(mc.getEntityRenderDispatcher().getRenderer(mob) instanceof GeoEntityRenderer<?> raw))throw new AssertionError("Missing native Gecko renderer");
            @SuppressWarnings("unchecked") var renderer=(GeoEntityRenderer<SecondaryMob>)raw;var model=renderer.getGeoModel();String id=IDS[stage/11];
            if(!model.getTextureResource(mob).equals(new ResourceLocation("dynasty","textures/entity/secondary/"+id+".png")))throw new AssertionError("Wrong atlas binding");
            var baked=model.getBakedModel(model.getModelResource(mob));
            for(String clip:CLIPS)if(model.getAnimation(mob,clip)==null)throw new AssertionError("Unbaked clip "+clip);
            for(String clip:List.of("pounce","coil","stalk","dive","circle","burrow","eruption","pinch","sting","possession","return_water","side_charge"))
                if(model.getAnimation(mob,clip)==null)throw new AssertionError("Unbaked skill clip "+clip);
            String[] anchors=switch(id){
                case "river_imp"->new String[]{"shell","dish","left_foot","right_foot"};
                case "tree_spirit"->new String[]{"left_branch","right_branch","foot_0","branch_3"};
                case "shrimp_soldier"->new String[]{"spear","left_grip","tail_fan","left_antenna"};
                case "carp_spirit"->new String[]{"jaw","tail_fan","dorsal","left_fin"};
                case "snail_maiden"->new String[]{"shell","pelvis","waist","chest"};
                case "lantern_ghost"->new String[]{"hanger","ribs","paper_front","tassel"};
                case "stone_sprite"->new String[]{"boulder","foot_0","foot_3"};
                case "crab_soldier"->new String[]{"left_claw","right_pincer","left_eye","foot_5"};
                case "corpse_beetle"->new String[]{"left_elytron","right_elytron","left_mandible","foot_5"};
                case "venom_scorpion"->new String[]{"left_claw","stinger","tail_3","foot_5"};
                case "clockwork_rat"->new String[]{"key","ears","tail_3","foot_3"};
                case "gray_wolf"->new String[]{"jaw","ears","chest","shin_3"};
                case "wild_boar"->new String[]{"tusks","mane","jaw","foot_3"};
                case "golden_leopard"->new String[]{"jaw","tail_3","chest","shin_3"};
                case "red_fox"->new String[]{"ears","tail_mid","tail_tip","jaw"};
                case "gray_falcon"->new String[]{"beak","breast","left_wingtip","right_foot"};
                case "jingwei_bird"->new String[]{"beak","stone","crest","left_wingtip"};
                case "wooden_magpie"->new String[]{"beak","gears","tail","left_wingtip"};
                case "bat_demon"->new String[]{"ears","jaw","left_wingtip","right_wingtip"};
                default->new String[]{"root","body","head"};};
            for(String anchor:anchors)if(model.getBone(anchor).isEmpty())throw new AssertionError("Missing native bone "+anchor);
            if(id.equals("shrimp_soldier")&&model.getBone("spear").orElseThrow().getParent()!=model.getBone("left_grip").orElseThrow())throw new AssertionError("Weapon detached from grip bone");
            var ctrl=mob.getAnimatableInstanceCache().getManagerForId(mob.getId()).getAnimationControllers().get("body");
            String clip=ctrl==null||ctrl.getCurrentAnimation()==null?"none":ctrl.getCurrentAnimation().animation().name();
            String expected=CLIPS[stage%11<4?0:stage%11-4];if(!clip.equals(expected))throw new AssertionError("Rendered clip "+clip+" differs from "+expected);
            String label=stage%11<4?new String[]{"front","45","side","back"}[stage%11]:expected;
            try(var frame=Screenshot.takeScreenshot(mc.getMainRenderTarget())){frame.writeToFile(OUT.resolve(String.format("%02d-%s-%s.png",stage,id,label)));}
            var state=new LinkedHashMap<String,Object>(Map.of("entity",id,"uuid",mob.getUUID().toString(),"stage",stage,"clip",clip,"width",mob.getBbWidth(),"height",mob.getBbHeight(),"fps",mc.getFps(),"scope","native art state selection; no gameplay/human claim"));
            var rotation=new LinkedHashMap<String,Object>();for(String name:anchors){var bone=model.getBone(name).orElseThrow();rotation.put(name,List.of(bone.getRotX(),bone.getRotY(),bone.getRotZ()));}state.put("boneRotationRadians",rotation);
            Files.writeString(OUT.resolve(String.format("%02d-state.json",stage)),new GsonBuilder().setPrettyPrinting().create().toJson(state));LOG.add(state.toString());captured=true;
        }catch(Throwable e){finish(mc,e);}
    }
    private static void finish(Minecraft mc,Throwable error){
        if(done)return;done=true;
        try{Files.createDirectories(OUT);Files.writeString(OUT.resolve(error==null?"PASS.txt":"FAIL.txt"),String.join("\n",LOG)+"\n"+(error==null?"PASS: "+(IDS.length*11)+" native art stages, dedicated atlases and all 19 clips per entity baked. Gameplay, humans and sustained performance are separate.\n":"FAIL: "+error+"\n"));if(error!=null)error.printStackTrace();}catch(Exception e){e.printStackTrace();}mc.stop();
    }
}
