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
    private static final boolean BOSS_FINAL=Boolean.getBoolean("dynasty.secondaryArtQa.bossFinal");
    private static final boolean BOSS_AUDIT=BOSS_FINAL||Boolean.getBoolean("dynasty.secondaryArtQa.bossAudit");
    private static final int STAGES=BOSS_FINAL?11:BOSS_AUDIT?4:11;
    private static final String[] BOSS_CLIPS={"idle","walk","attack","cast","hurt","death"};
    private static final Path OUT=Path.of(System.getProperty("dynasty.secondaryArtQa.output","build/secondary-art-native/results"));
    private static final String[] IDS=System.getProperty("dynasty.secondaryArtQa.ids","river_imp,tree_spirit,shrimp_soldier").split(",");
    private static final String[] CLIPS={"idle","wander","hunt","flee","attack","special","evade"};
    private static final List<String> LOG=new ArrayList<>();
    private static final Set<String> TEXTURES_CHECKED=new HashSet<>();
    private static boolean started,done,captured;
    private static int stage=-1,settled;
    private static long deadline=System.nanoTime()+600_000_000_000L;
    private static CompletableFuture<Integer> pending;
    private static int entityId;
    private static net.minecraft.world.entity.Mob fixture;

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
                if(BOSS_AUDIT)LegacyCuboidExport.dragon(OUT);
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
                if(stage==IDS.length*STAGES-1){finish(mc,null);return;}
                stage++;pending=mc.getSingleplayerServer().submit(()->{try{return prepare(mc,stage);}catch(Exception e){throw new RuntimeException(e);}});return;
            }
            if(mc.level.getEntity(entityId) instanceof net.minecraft.world.entity.Mob mob){
                settled++;
                if(BOSS_FINAL&&stage%STAGES>=5&&settled==20){
                    if(!(mc.getEntityRenderDispatcher().getRenderer(mob) instanceof BossCuboidRenderer<?> renderer))throw new AssertionError("No cuboid boss replacement");
                    renderer.getAnimatable().getAnimatableInstanceCache().getManagerForId(mob.getId()).tryTriggerAnimation("body","art_check_"+BOSS_CLIPS[stage%STAGES-5]);
                }
            }
        }catch(Throwable e){finish(mc,e);}
    }
    private static int prepare(Minecraft mc,int s)throws Exception{
        var server=mc.getSingleplayerServer();var world=server.overworld();world.setDayTime(6000);
        if(fixture!=null)fixture.discard();
        for(int x=-9;x<=9;x++)for(int z=-9;z<=9;z++)world.setBlockAndUpdate(new BlockPos(x,-61,z),Blocks.STONE.defaultBlockState());
        String id=IDS[s/STAGES];
        fixture=BOSS_AUDIT?(net.minecraft.world.entity.Mob)net.minecraftforge.registries.ForgeRegistries.ENTITY_TYPES.getValue(new ResourceLocation("dynasty",id)).create(world):
            (id.equals("shrimp_soldier")?SecondaryMobs.SHRIMP.get():SecondaryMobs.TYPES.get(id).get()).create(world);
        fixture.moveTo(0,-60,0,0,0);fixture.setNoAi(true);fixture.setNoGravity(true);fixture.setPersistenceRequired();world.addFreshEntity(fixture);
        if(BOSS_FINAL){
            fixture.setItemSlot(net.minecraft.world.entity.EquipmentSlot.MAINHAND,new net.minecraft.world.item.ItemStack(id.equals("dragon_king")?net.minecraft.world.item.Items.TRIDENT:net.minecraft.world.item.Items.STONE_SWORD));
            fixture.setItemSlot(net.minecraft.world.entity.EquipmentSlot.OFFHAND,new net.minecraft.world.item.ItemStack(net.minecraft.world.item.Items.SHIELD));
        }
        // NoAI does not suppress the swindler's existing custom aiStep pose.
        // Use its existing completed-deception fixture flag for this isolated
        // art-state matrix. This is not a swindling/gameplay acceptance test.
        if(id.equals("swindler")){var field=SecondaryMob.class.getDeclaredField("deceptionStage");field.setAccessible(true);field.setInt(fixture,3);}
        int pose=s%STAGES;int state=pose<4?0:pose-4;
        // QA only: select existing synchronized art states. This makes no claim
        // that combat, natural spawning or real-player scenarios were exercised.
        if(!BOSS_AUDIT){var method=SecondaryMob.class.getDeclaredMethod("animate",int.class,int.class);method.setAccessible(true);method.invoke(fixture,state,10000);}
        server.getPlayerList().getPlayers().forEach(p->{p.setGameMode(GameType.CREATIVE);p.teleportTo(world,0,-60,10,180,0);});
        return fixture.getId();
    }
    private static void setCamera(Minecraft mc){
        int pose=stage%STAGES;double yaw=pose==1?45:pose==2?90:pose==3?180:0;
        if(BOSS_FINAL)yaw=pose==1?45:pose==2?90:pose==3?-90:pose==4?180:0;
        if(BOSS_AUDIT){
            double angle=Math.toRadians(yaw),distance=fixture.getBbHeight()>3?11:5.8;
            var camera=new ArmorStand(mc.level,Math.sin(angle)*distance,-60,Math.cos(angle)*distance);
            camera.setPos(camera.getX(),-60+fixture.getBbHeight()/2-camera.getEyeHeight(),camera.getZ());
            camera.setNoGravity(true);camera.setYRot((float)(180-yaw));camera.setXRot(0);camera.setYHeadRot(camera.getYRot());camera.yHeadRotO=camera.getYRot();camera.setOldPosAndRot();
            mc.options.setCameraType(CameraType.FIRST_PERSON);mc.setCameraEntity(camera);return;
        }
        double angle=Math.toRadians(yaw),distance=IDS[stage/11].equals("tree_spirit")?5.7:3.9;
        var camera=new ArmorStand(mc.level,Math.sin(angle)*distance,-60,Math.cos(angle)*distance);
        double height=IDS[stage/11].equals("shrimp_soldier")?1.25:SecondaryMobs.SPECS.stream().filter(s->s.id().equals(IDS[stage/11])).findFirst().orElseThrow().height();
        camera.setPos(camera.getX(),-60+height/2-camera.getEyeHeight(),camera.getZ());
        camera.setNoGravity(true);camera.setYRot((float)(180-yaw));camera.setXRot(0);camera.setYHeadRot(camera.getYRot());camera.yHeadRotO=camera.getYRot();camera.setOldPosAndRot();
        mc.options.setCameraType(CameraType.FIRST_PERSON);mc.setCameraEntity(camera);
    }
    @SubscribeEvent public static void render(TickEvent.RenderTickEvent event){
        if(!ENABLED||done||captured||pending!=null||stage<0||settled<24||event.phase!=TickEvent.Phase.END)return;
        var mc=Minecraft.getInstance();
        if(BOSS_AUDIT){
            if(!(mc.level.getEntity(entityId) instanceof net.minecraft.world.entity.Mob mob))return;
            try{
                String id=IDS[stage/STAGES];int pose=stage%STAGES;
                if(!BOSS_FINAL&&id.equals("dragon_emperor"))LegacyCuboidExport.dragon(OUT);
                String view=BOSS_FINAL?(pose<5?new String[]{"front","45","right","left","back"}[pose]:BOSS_CLIPS[pose-5]):new String[]{"front","45","side","back"}[pose];
                if(BOSS_FINAL){
                    if(!(mc.getEntityRenderDispatcher().getRenderer(mob) instanceof BossCuboidRenderer<?> renderer))throw new AssertionError("Missing final boss renderer");
                    var visual=renderer.getAnimatable();var model=renderer.getGeoModel();model.getBakedModel(model.getModelResource(visual));
                    for(String clip:BOSS_CLIPS)if(model.getAnimation(visual,clip)==null)throw new AssertionError("Missing boss clip "+clip);
                    for(String bone:List.of("root","body","chest","neck","head","jaw","left_arm","right_arm","left_grip","right_grip"))if(model.getBone(bone).isEmpty())throw new AssertionError("Missing boss bone "+bone);
                    for(String side:List.of("left","right"))if(model.getBone(side+"_grip").orElseThrow().getParent()!=model.getBone(side+"_hand").orElseThrow())throw new AssertionError("Detached equipped item anchor");
                    try(var stream=mc.getResourceManager().open(model.getTextureResource(visual));var image=com.mojang.blaze3d.platform.NativeImage.read(stream)){
                        if(image.getWidth()!=16||image.getHeight()!=16)throw new AssertionError("Boss texture not 16px");
                        Set<Integer> colors=new HashSet<>();
                        for(int y=0;y<16;y++)for(int x=0;x<16;x++){
                            int rgb=image.getPixelRGBA(x,y);colors.add(rgb);
                            if((x==0||x==15||y==0||y==15)&&rgb!=-1)throw new AssertionError("Boss texture missing white margin");
                            if(rgb!=image.getPixelRGBA(x-x%2,y-y%2))throw new AssertionError("Boss texture has sub2px detail");
                        }
                        if(colors.size()!=4)throw new AssertionError("Boss color budget");
                    }
                    if(pose>=5){
                        var ctrl=visual.getAnimatableInstanceCache().getManagerForId(mob.getId()).getAnimationControllers().get("body");
                        if(ctrl.getCurrentAnimation()==null||!ctrl.getCurrentAnimation().animation().name().equals(view))throw new AssertionError("Boss rendered wrong QA resource pose: "+view);
                    }
                }
                Map<String,Object> record=Map.of("entity",id,"stage",stage,"viewOrClip",view,"renderer",mc.getEntityRenderDispatcher().getRenderer(mob).getClass().getName(),"width",mob.getBbWidth(),"height",mob.getBbHeight(),"scope",BOSS_FINAL?"native final resources and automatic clip selection; natural combat remains pending":"native existing boss art baseline; no gameplay claim");
                Files.writeString(OUT.resolve(String.format("%02d-state.json",stage)),new GsonBuilder().setPrettyPrinting().create().toJson(record));LOG.add(record.toString());
                try(var shot=net.minecraft.client.Screenshot.takeScreenshot(mc.getMainRenderTarget())){shot.writeToFile(OUT.resolve(String.format("%02d-%s-%s.png",stage,id,view)));}
                captured=true;
            }catch(Throwable e){finish(mc,e);}return;
        }
        if(!(mc.level.getEntity(entityId) instanceof SecondaryMob mob))return;
        try{
            if(!(mc.getEntityRenderDispatcher().getRenderer(mob) instanceof GeoEntityRenderer<?> raw))throw new AssertionError("Missing native Gecko renderer");
            @SuppressWarnings("unchecked") var renderer=(GeoEntityRenderer<SecondaryMob>)raw;var model=renderer.getGeoModel();String id=IDS[stage/11];
            if(!model.getTextureResource(mob).equals(new ResourceLocation("dynasty","textures/entity/secondary/"+id+".png")))throw new AssertionError("Wrong atlas binding");
            if(TEXTURES_CHECKED.add(id))try(var stream=mc.getResourceManager().open(model.getTextureResource(mob));var image=com.mojang.blaze3d.platform.NativeImage.read(stream)){
                if(image.getWidth()!=16||image.getHeight()!=16)throw new AssertionError("Not actual 16px texture");
                Set<Integer> colors=new HashSet<>();
                for(int y=0;y<16;y++)for(int x=0;x<16;x++){
                    int rgb=image.getPixelRGBA(x,y);colors.add(rgb);
                    if((x==0||x==15||y==0||y==15)&&rgb!=-1)throw new AssertionError("Missing white texture margin");
                    if(rgb!=image.getPixelRGBA(x-x%2,y-y%2))throw new AssertionError("Sub-2px texture detail");
                }
                if(colors.size()!=4)throw new AssertionError("Wrong texture color count");
            }
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
                case "giant_python"->new String[]{"segment_1","segment_6","jaw","tongue"};
                case "stone_worm"->new String[]{"segment_1","segment_6","jaw","head"};
                case "locust_swarm"->new String[]{"insect_0","insect_13","insect_0_left_wing","insect_13_right_wing"};
                case "drowning_ghost"->new String[]{"hair","rags","left_forearm","jaw"};
                case "paper_money_ghost"->new String[]{"paper_0","paper_7","head","tail_tip"};
                case "wandering_spirit"->new String[]{"mask","mantle","front_robe","knot"};
                case "bandit_thug"->new String[]{"pelvis","waist","chest","blade","left_pauldron"};
                case "night_watchman"->new String[]{"lantern","clapper","left_hand","right_hand"};
                case "herb_picker"->new String[]{"basket","hat","sickle","right_hand"};
                case "famished_refugee"->new String[]{"rags","bundle","staff","left_hand"};
                case "swindler"->new String[]{"robe","abacus","left_cuff","right_hand"};
                case "paper_cut_child"->new String[]{"pelvis","chest","ribbons","left_elbow"};
                default->new String[]{"root","body","head"};};
            for(String anchor:anchors)if(model.getBone(anchor).isEmpty())throw new AssertionError("Missing native bone "+anchor);
            if(id.equals("shrimp_soldier")&&model.getBone("spear").orElseThrow().getParent()!=model.getBone("left_grip").orElseThrow())throw new AssertionError("Weapon detached from grip bone");
            Map<String,String> grips=switch(id){
                case "bandit_thug"->Map.of("blade","left_hand");
                case "night_watchman"->Map.of("lantern","left_hand","clapper","right_hand");
                case "herb_picker"->Map.of("sickle","right_hand");
                case "famished_refugee"->Map.of("staff","left_hand");
                case "swindler"->Map.of("abacus","right_hand");
                default->Map.of();};
            for(var grip:grips.entrySet())if(model.getBone(grip.getKey()).orElseThrow().getParent()!=model.getBone(grip.getValue()).orElseThrow())throw new AssertionError("Detached profession prop "+grip.getKey());
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
        String success=BOSS_FINAL?"PASS: "+(IDS.length*STAGES)+" native boss resource stages, 6 baked clips, pixel16 and held-item anchors. Automatic resource poses; natural combat/skill clocks and human acceptance remain pending.\n":
            BOSS_AUDIT?"PASS: "+(IDS.length*STAGES)+" native existing boss baseline views; resource/animation remaster and gameplay acceptance remain pending.\n":
            "PASS: "+(IDS.length*11)+" native art stages, dedicated atlases and all 19 clips per entity baked. Gameplay, humans and sustained performance are separate.\n";
        try{Files.createDirectories(OUT);Files.writeString(OUT.resolve(error==null?"PASS.txt":"FAIL.txt"),String.join("\n",LOG)+"\n"+(error==null?success:"FAIL: "+error+"\n"));if(error!=null)error.printStackTrace();}catch(Exception e){e.printStackTrace();}mc.stop();
    }
}
