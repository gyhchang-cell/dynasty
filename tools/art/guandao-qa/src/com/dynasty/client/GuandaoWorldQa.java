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
public final class GuandaoWorldQa {
    private static boolean started,done;
    private static CompletableFuture<Void> setup;
    private static long deadline=System.nanoTime()+300_000_000_000L;
    private static int ticks,stage,wait;
    private static ArmorStand camera;
    private static final Path OUT=Path.of(System.getProperty("dynasty.guandaoQa.output","build/guandao-world-qa/results"));
    private static final String[] NAMES={"world-front","world-45","world-side","world-first-person","world-third-person","world-item-entity"};
    private static final List<String> log=new ArrayList<>();
    private static final boolean REGRESSION=Boolean.getBoolean("dynasty.guandaoQa.regression");
    private static net.minecraft.client.player.RemotePlayer remote;
    private static int views(){return REGRESSION?36:NAMES.length;}
    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent event) {
        if(!Boolean.getBoolean("dynasty.guandaoQa")||done||event.phase!=TickEvent.Phase.END)return;
        var mc=Minecraft.getInstance();
        try {
            if(System.nanoTime()>deadline)throw new AssertionError("QA timed out");
            if(mc.getOverlay()!=null)return;
            if(mc.screen instanceof AccessibilityOnboardingScreen)mc.setScreen(new TitleScreen());
            if(!started&&mc.screen instanceof TitleScreen) {
                String dir=mc.gameDirectory.getCanonicalPath();
                if(!dir.endsWith("/build/guandao-world-qa/client"))throw new AssertionError("Refusing to touch non-QA world: "+dir);
                started=true;Files.createDirectories(OUT);mc.options.renderDistance().set(5);mc.options.fov().set(45);
                mc.options.pauseOnLostFocus=false;
                GameRules rules=new GameRules();rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false,null);
                var settings=new LevelSettings("Guandao visual QA",GameType.CREATIVE,false,net.minecraft.world.Difficulty.PEACEFUL,true,rules,WorldDataConfiguration.DEFAULT);
                mc.createWorldOpenFlows().createFreshLevel("guandao-refinement-"+System.currentTimeMillis(),settings,new WorldOptions(42,false,false),r->r.registryOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.FLAT).createWorldDimensions());
                return;
            }
            if(mc.level==null||mc.player==null||++ticks<60)return;
            if(setup==null) {
                setup=mc.getSingleplayerServer().submit(()->{
                    var server=mc.getSingleplayerServer();var world=server.overworld();world.setDayTime(6000);world.getGameRules().getRule(GameRules.RULE_DAYLIGHT).set(false,server);
                    var player=server.getPlayerList().getPlayers().get(0);player.teleportTo(world,0,-60,0,0,0);
                    player.getInventory().setItem(0,new ItemStack(DynastyWeapons.QINGLONG_DAO.get()));player.getInventory().selected=0;player.getInventory().setChanged();
                    var drop=new ItemEntity(world,4,-59.7,1,new ItemStack(DynastyWeapons.QINGLONG_DAO.get()));drop.setDeltaMovement(net.minecraft.world.phys.Vec3.ZERO);drop.setNoGravity(true);drop.setNeverPickUp();world.addFreshEntity(drop);
                });return;
            }
            if(!setup.isDone())return;setup.join();
            if(mc.screen!=null)mc.setScreen(null);
            if(wait==0){configure(mc);wait=1;}else wait++;
            if(REGRESSION&&remote!=null&&wait%20==10){
                remote.swing(net.minecraft.world.InteractionHand.MAIN_HAND);
                mc.player.swing(net.minecraft.world.InteractionHand.MAIN_HAND);
                if(stage%3==0)ImperialWeaponRenderer.receive(new com.dynasty.network.WeaponImpactPacket(2,0,-57,-4,stage*36));
            }
        }catch(Throwable e){finish(mc,e);}
    }
    private static void configure(Minecraft mc) {
        if(REGRESSION){
            if(remote==null){
                remote=new net.minecraft.client.player.RemotePlayer(mc.level,new com.mojang.authlib.GameProfile(UUID.fromString("12345678-0000-0000-0000-000000000042"),"ObserverFixture"));
                remote.setPos(2,-60,0);remote.setItemSlot(net.minecraft.world.entity.EquipmentSlot.MAINHAND,new ItemStack(DynastyWeapons.QINGLONG_DAO.get()));
                mc.level.addPlayer(-2042,remote);
            }
            mc.options.hideGui=true;mc.options.setCameraType(CameraType.FIRST_PERSON);
            if(stage>=30){mc.setCameraEntity(mc.player);mc.options.setCameraType(stage%2==0?CameraType.FIRST_PERSON:CameraType.THIRD_PERSON_BACK);
                mc.player.setXRot(stage<32?-85:stage<34?85:0);return;}
            // Ground, overhead, below/cape intersections and a second holder use the same real renderer.
            int ring=stage/10;double angle=Math.toRadians((stage%10)*36);
            double radius=ring==0?4:ring==1?1.2:7;
            camera=new ArmorStand(mc.level,Math.sin(angle)*radius,-60+(ring==0?1:ring==1?5:9),-4+Math.cos(angle)*radius);
            camera.setYRot((float)(180-Math.toDegrees(angle)));camera.setXRot(ring==0?-60:ring==1?0:65);
            camera.setYHeadRot(camera.getYRot());camera.yHeadRotO=camera.getYRot();camera.setOldPosAndRot();mc.setCameraEntity(camera);
            remote.swing(net.minecraft.world.InteractionHand.MAIN_HAND);
            if(stage%3==0)ImperialWeaponRenderer.receive(new com.dynasty.network.WeaponImpactPacket(2,0,-57,-4,stage*36));
            return;
        }
        mc.options.hideGui=stage<3||stage==5;mc.options.setCameraType(CameraType.FIRST_PERSON);
        if(stage==3||stage==4){mc.setCameraEntity(mc.player);mc.options.setCameraType(stage==3?CameraType.FIRST_PERSON:CameraType.THIRD_PERSON_FRONT);return;}
        double angle=Math.toRadians(stage==1?45:stage==2?90:0),r=18;
        camera=new ArmorStand(mc.level,Math.sin(angle)*r,-56,Math.cos(angle)*r-4);
        camera.setYRot((float)(180-Math.toDegrees(angle)));camera.setXRot(0);
        if(stage==5){camera.setPos(4,-61,4);camera.setYRot(180);camera.setXRot(8);}
        camera.setYHeadRot(camera.getYRot());camera.yHeadRotO=camera.getYRot();
        camera.setOldPosAndRot();mc.setCameraEntity(camera);
    }
    @SubscribeEvent public static void render(TickEvent.RenderTickEvent event) {
        if(!Boolean.getBoolean("dynasty.guandaoQa")||done||event.phase!=TickEvent.Phase.END||wait<100)return;
        var mc=Minecraft.getInstance();if(mc.level==null||mc.player==null||mc.getOverlay()!=null)return;
        try {
            if(mc.getItemRenderer().getModel(new ItemStack(DynastyWeapons.QINGLONG_DAO.get()),mc.level,mc.player,0)==mc.getModelManager().getMissingModel())throw new AssertionError("Missing item model");
            String name=REGRESSION?"camera-regression-"+stage:NAMES[stage];
            try(var image=Screenshot.takeScreenshot(mc.getMainRenderTarget())){
                image.writeToFile(OUT.resolve(name+".png"));
                if(REGRESSION){int black=0,total=0;for(int y=0;y<image.getHeight();y+=8)for(int x=0;x<image.getWidth();x+=8){int c=image.getPixelRGBA(x,y);if((c&255)<10&&((c>>8)&255)<10&&((c>>16)&255)<10)black++;total++;}
                    double fraction=black/(double)total;log.add(name+" black pixels="+fraction);if(fraction>.96)throw new AssertionError("Fullscreen black occlusion "+name);
                }
            }
            log.add("Captured actual world framebuffer: "+name+"; gameTime="+mc.level.getGameTime()+"; camera="+mc.getCameraEntity().position()+"; yaw="+mc.getCameraEntity().getViewYRot(1)+"; client FPS="+mc.getFps());
            if(++stage==views()){finish(mc,null);return;}wait=0;
        }catch(Throwable e){finish(mc,e);}
    }
    private static void finish(Minecraft mc,Throwable e){
        if(done)return;done=true;if(e!=null){e.printStackTrace();log.add("FAIL: "+e);}else log.add(REGRESSION?"PASS: 36 world-space camera/intersection and first/third-person views, simultaneous local and client-fixture remote holders, active swings/impact packets. This does NOT replace two real network clients. No launcher save touched.":"PASS: actual in-world screenshots, first/third person and dropped-item model loaded; no launcher save touched.");
        try{Files.createDirectories(OUT);Files.write(OUT.resolve(e==null?"runtime-PASS.txt":"runtime-FAIL.txt"),log);}catch(Exception ignored){}
        mc.setCameraEntity(mc.player);mc.stop();
    }
}
