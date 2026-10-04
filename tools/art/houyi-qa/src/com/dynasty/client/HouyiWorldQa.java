package com.dynasty.client;

import com.dynasty.DynastyWeapons;
import net.minecraft.client.Minecraft;
import net.minecraft.client.CameraType;
import net.minecraft.client.Screenshot;
import net.minecraft.client.gui.screens.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.entity.decoration.ArmorStand;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.*;
import net.minecraft.world.level.levelgen.WorldOptions;
import net.minecraft.world.level.levelgen.presets.WorldPresets;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.CompletableFuture;

/** Captures the real world framebuffer through normal Forge render events in a disposable world. */
@Mod.EventBusSubscriber(modid="dynasty",value=Dist.CLIENT)
public final class HouyiWorldQa {
    private static boolean started,done;
    private static CompletableFuture<Void> setup;
    private static CompletableFuture<Void> reload;
    private static long deadline=System.nanoTime()+300_000_000_000L;
    private static int ticks,stage,wait;
    private static ArmorStand camera;
    private static final Path OUT=Path.of(System.getProperty("dynasty.houyiQa.output","build/houyi-world-qa/results"));
    private static final String[] NAMES={"world-front","world-45","world-left","world-back","world-right","world-rear45","world-first-person","world-third-person"};
    private static final List<String> log=new ArrayList<>();
    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent event) {
        if(!Boolean.getBoolean("dynasty.houyiQa")||done||event.phase!=TickEvent.Phase.END)return;
        var mc=Minecraft.getInstance();
        try {
            if(System.nanoTime()>deadline)throw new AssertionError("QA timed out");
            if(mc.getOverlay()!=null)return;
            if(mc.screen instanceof AccessibilityOnboardingScreen)mc.setScreen(new TitleScreen());
            if(!started&&mc.screen instanceof TitleScreen) {
                String dir=mc.gameDirectory.getCanonicalPath();
                if(!dir.endsWith("/build/houyi-world-qa/client"))throw new AssertionError("Refusing to touch non-QA world: "+dir);
                started=true;Files.createDirectories(OUT);mc.options.renderDistance().set(5);mc.options.fov().set(45);
                mc.options.pauseOnLostFocus=false;
                GameRules rules=new GameRules();rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false,null);
                var settings=new LevelSettings("Houyi visual QA",GameType.CREATIVE,false,net.minecraft.world.Difficulty.PEACEFUL,true,rules,WorldDataConfiguration.DEFAULT);
                mc.createWorldOpenFlows().createFreshLevel("houyi-remaster-"+System.currentTimeMillis(),settings,new WorldOptions(42,false,false),r->r.registryOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.FLAT).createWorldDimensions());
                return;
            }
            if(mc.level==null||mc.player==null||++ticks<60)return;
            if(setup==null) {
                setup=mc.getSingleplayerServer().submit(()->{
                    var server=mc.getSingleplayerServer();var world=server.overworld();world.setDayTime(6000);world.getGameRules().getRule(GameRules.RULE_DAYLIGHT).set(false,server);
                    var player=server.getPlayerList().getPlayers().get(0);player.teleportTo(world,0,-60,0,0,0);
                    player.getInventory().setItem(0,new ItemStack(DynastyWeapons.HOUYI_BOW.get()));player.getInventory().selected=0;player.getInventory().setChanged();
                    var drop=new ItemEntity(world,4,-59.7,1,new ItemStack(DynastyWeapons.HOUYI_BOW.get()));drop.setDeltaMovement(net.minecraft.world.phys.Vec3.ZERO);drop.setNoGravity(true);drop.setNeverPickUp();world.addFreshEntity(drop);
                });return;
            }
            if(!setup.isDone())return;setup.join();
            if(stage==4&&wait==0) {
                if(reload==null){reload=mc.reloadResourcePacks();return;}
                if(!reload.isDone())return;
                reload.join();
            }
            if(mc.screen!=null)mc.setScreen(null);
            mc.options.keyUse.setDown(true);
            if(!mc.player.isUsingItem())mc.gameMode.useItem(mc.player,net.minecraft.world.InteractionHand.MAIN_HAND);
            if(wait==0){configure(mc);wait=1;}else wait++;
        }catch(Throwable e){finish(mc,e);}
    }
    private static void configure(Minecraft mc) {
        mc.options.hideGui=stage<6;mc.options.setCameraType(CameraType.FIRST_PERSON);
        if(stage>=6){mc.setCameraEntity(mc.player);mc.options.setCameraType(stage==6?CameraType.FIRST_PERSON:CameraType.THIRD_PERSON_FRONT);return;}
        // Archer local +Z faces world -X when caster yaw is zero.
        double[] angles={-90,-45,0,90,180,135};
        double angle=Math.toRadians(angles[stage]),r=19;
        camera=new ArmorStand(mc.level,Math.sin(angle)*r,-56,Math.cos(angle)*r-4);
        camera.setYRot((float)(180-Math.toDegrees(angle)));camera.setXRot(0);
        camera.setYHeadRot(camera.getYRot());camera.yHeadRotO=camera.getYRot();
        camera.setOldPosAndRot();mc.setCameraEntity(camera);
    }
    @SubscribeEvent public static void render(TickEvent.RenderTickEvent event) {
        if(!Boolean.getBoolean("dynasty.houyiQa")||done||event.phase!=TickEvent.Phase.END||wait<100)return;
        var mc=Minecraft.getInstance();if(mc.level==null||mc.player==null||mc.getOverlay()!=null)return;
        try {
            if(mc.getItemRenderer().getModel(new ItemStack(DynastyWeapons.HOUYI_BOW.get()),mc.level,mc.player,0)==mc.getModelManager().getMissingModel())throw new AssertionError("Missing item model");
            try(var image=Screenshot.takeScreenshot(mc.getMainRenderTarget())){image.writeToFile(OUT.resolve(NAMES[stage]+".png"));}
            log.add("Captured actual world framebuffer: "+NAMES[stage]+"; gameTime="+mc.level.getGameTime()+"; camera="+mc.getCameraEntity().position()+"; yaw="+mc.getCameraEntity().getViewYRot(1)+"; client FPS="+mc.getFps());
            if(++stage==NAMES.length){finish(mc,null);return;}wait=0;
        }catch(Throwable e){finish(mc,e);}
    }
    private static void finish(Minecraft mc,Throwable e){
        if(done)return;done=true;if(e!=null){e.printStackTrace();log.add("FAIL: "+e);}else log.add("PASS: actual in-world screenshots, eight views and first/third person model loaded; no launcher save touched.");
        try{Files.createDirectories(OUT);Files.write(OUT.resolve(e==null?"runtime-PASS.txt":"runtime-FAIL.txt"),log);}catch(Exception ignored){}
        mc.options.keyUse.setDown(false);mc.setCameraEntity(mc.player);mc.stop();
    }
}
