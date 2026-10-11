package com.dynasty.client;

import com.dynasty.dungeon.*;
import com.google.gson.GsonBuilder;
import com.mojang.blaze3d.platform.NativeImage;
import net.minecraft.client.*;
import net.minecraft.core.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.Difficulty;
import net.minecraft.world.entity.decoration.ArmorStand;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.levelgen.WorldOptions;
import net.minecraft.world.level.levelgen.presets.WorldPresets;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.CompletableFuture;

/** Optional disposable native client; no production registration, state shortcuts or player saves. */
@Mod.EventBusSubscriber(modid="dynasty",value=Dist.CLIENT)
public final class Cod2CloudClientQa {
    private static final boolean ENABLED=Boolean.getBoolean("dynasty.cod2CloudQa");
    private static final Path OUT=Path.of(System.getProperty("dynasty.cod2CloudQa.output","build/disabled-cloud-qa"));
    private static final BlockPos POS=new BlockPos(0,-58,0),CORE=new BlockPos(-4,-60,4);
    private static final List<Object> REPORT=new ArrayList<>();
    private static final String[] VIEWS={"front","45","side","back"};
    private static boolean started,done,capturing,armed;
    private static CompletableFuture<Snapshot> arm;
    private static int stage;
    private static final long DEADLINE=System.nanoTime()+420_000_000_000L;
    private static CompletableFuture<Void> setup,reload;
    private static CompletableFuture<Snapshot> pending;
    private static CompletableFuture<Map<String,Object>> row;
    private static Snapshot current;
    private static ArmorStand camera;
    private record Snapshot(boolean flame,long born,String mechanism,UUID instance){}
    private static String label(){return stage<4?VIEWS[stage]:new String[]{"warning","fallen","recovering","restored","after-reload"}[stage-4];}
    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent event){
        if(!ENABLED||done||event.phase!=TickEvent.Phase.END)return;var mc=Minecraft.getInstance();
        try{
            if(System.nanoTime()>DEADLINE)throw new AssertionError("Native vent timeout, stage="+stage);
            if(!started){
                if(!(mc.screen instanceof net.minecraft.client.gui.screens.TitleScreen))return;
                Files.createDirectories(OUT);started=true;mc.options.pauseOnLostFocus=false;mc.options.hideGui=true;mc.options.renderDistance().set(4);mc.options.fov().set(55);
                var rules=new GameRules();rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false,null);rules.getRule(GameRules.RULE_DAYLIGHT).set(false,null);rules.getRule(GameRules.RULE_NATURAL_REGENERATION).set(false,null);
                mc.createWorldOpenFlows().createFreshLevel("cod2-cloud-qa",new LevelSettings("Disposable vents",GameType.CREATIVE,false,Difficulty.NORMAL,true,rules,WorldDataConfiguration.DEFAULT),new WorldOptions(78,false,false),r->r.registryOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.FLAT).createWorldDimensions());return;
            }
            if(mc.level==null||mc.player==null)return;if(mc.screen!=null)mc.setScreen(null);var server=mc.getSingleplayerServer();if(server==null)return;
            if(setup==null){setup=server.submit(()->{var world=server.overworld();world.setDayTime(6000);for(int x=-10;x<=12;x++)for(int z=-10;z<=12;z++)world.setBlockAndUpdate(new BlockPos(x,-61,z),Blocks.SMOOTH_STONE.defaultBlockState());});return;}
            if(!setup.isDone()||mc.level.getGameTime()<100)return;setup.join();
            if(capturing){
                if(!row.isDone())return;REPORT.add(row.join());Files.writeString(OUT.resolve("samples.json"),new GsonBuilder().setPrettyPrinting().create().toJson(REPORT)+"\n");capturing=false;stage++;
                if(stage==5||stage==6||stage==7)return;
                current=null;armed=false;if(stage==9){finish(mc,null);return;}if(stage==8){reload=mc.reloadResourcePacks();return;}
                int next=stage;pending=server.submit(()->prepare(server,next));return;
            }
            if(reload!=null){if(!reload.isDone())return;reload.join();REPORT.add(Map.of("reload","actual Minecraft resource reload"));reload=null;pending=server.submit(()->prepare(server,8));return;}
            if(pending==null){pending=server.submit(()->prepare(server,stage));return;}
            if(current==null){if(!pending.isDone())return;current=pending.join();mc.levelRenderer.allChanged();}
            if(camera==null){camera=new ArmorStand(mc.level,0,0,0);camera.setNoGravity(true);mc.options.setCameraType(CameraType.FIRST_PERSON);mc.setCameraEntity(camera);}
            double yaw=stage<4?new double[]{0,45,90,180}[stage%4]:135,r=Math.toRadians(yaw);
            camera.setPos(.5+Math.sin(r)*6,-55.1-camera.getEyeHeight(),.5-Math.cos(r)*6);
            // Render a fully loaded fixture before a real survival player enters the original clock range.
            if((stage==4)&&!armed){
                if(arm==null&&mc.level.getGameTime()-current.born>=60){var ready=current;arm=server.submit(()->{
                    for(var p:server.getPlayerList().getPlayers()){p.setGameMode(GameType.SURVIVAL);p.setNoGravity(false);p.teleportTo(server.overworld(),.5,-55.5,.5,0,0);p.setDeltaMovement(Vec3.ZERO);p.fallDistance=0;}
                    return new Snapshot(ready.flame,server.overworld().getGameTime(),ready.mechanism,ready.instance);
                });}
                if(arm!=null&&arm.isDone()){current=arm.join();arm=null;armed=true;}
            }
            // Vanilla suppresses position packets for a detached QA camera. Forward the real local
            // physics result through its ordinary serverbound packet; never set server movement here.
            if(armed&&stage>=4&&stage<=7)mc.player.connection.send(new net.minecraft.network.protocol.game.ServerboundMovePlayerPacket.PosRot(
                mc.player.getX(),mc.player.getY(),mc.player.getZ(),mc.player.getYRot(),mc.player.getXRot(),mc.player.onGround()));
            camera.setYRot((float)yaw);camera.setYHeadRot((float)yaw);camera.yHeadRotO=(float)yaw;camera.setXRot(20);camera.setOldPosAndRot();
        }catch(Throwable e){finish(mc,e);}
    }
    private static Snapshot prepare(MinecraftServer server,int n){
        var world=server.overworld();world.removeBlock(POS,false);world.removeBlock(CORE,false);
        var id=UUID.randomUUID();String mechanism="cloud_qa";
        world.setBlockAndUpdate(POS,DungeonContent.CLOUD.get().defaultBlockState());
        ((DungeonMechanismBlockEntity)world.getBlockEntity(POS)).configure(id,"cloud_qa",mechanism,CORE,-1,List.of());
        world.setBlockAndUpdate(CORE,DungeonContent.CORE.get().defaultBlockState());var core=(DungeonMechanismBlockEntity)world.getBlockEntity(CORE);core.configure(id,"cloud_qa","core",CORE,-1,List.of(POS));core.configureRoom(0,false,POS,POS.above(3));
        for(var p:server.getPlayerList().getPlayers()){
            p.setGameMode(GameType.SPECTATOR);p.setNoGravity(true);p.clearFire();p.setHealth(p.getMaxHealth());p.setDeltaMovement(Vec3.ZERO);p.hurtMarked=true;
            p.teleportTo(world,.5,-56,.5,0,0);
        }
        return new Snapshot(false,world.getGameTime(),mechanism,id);
    }
    @SubscribeEvent public static void render(TickEvent.RenderTickEvent event){
        if(!ENABLED||done||capturing||current==null||event.phase!=TickEvent.Phase.END)return;var mc=Minecraft.getInstance();if(mc.level==null||mc.getOverlay()!=null)return;
        try{
            if((stage==4)&&!armed)return;
            long age=mc.level.getGameTime()-current.born;var state=mc.level.getBlockState(POS);
            if(!(mc.level.getBlockEntity(POS) instanceof DungeonMechanismBlockEntity be)||!current.instance.equals(be.instance()))return;
            int phase=state.getValue(DungeonMechanismBlock.STAGE);
            if(stage<4||stage==8){if(age<40)return;}
            else if(stage==4){if(phase!=1||age<16)return;}
            else if(stage==5){if(phase!=2||age<45)return;}
            else if(stage==6){if(phase!=3||be.visualProgress(0)<.55)return;}
            else if(stage==7){if(phase!=0||age<96)return;}
            var model=mc.getModelManager().getModel(com.dynasty.dungeon.client.DungeonMechanismRenderer.CLOUD_MODEL);
            if(model==mc.getModelManager().getMissingModel())throw new AssertionError("Missing cloud model");
            try(var stream=mc.getResourceManager().open(new ResourceLocation("dynasty","textures/block/cod2_cloud/cloud.png"));var png=NativeImage.read(stream)){if(png.getWidth()!=16||png.getHeight()!=16)throw new AssertionError("Non16 actual PNG");}
            String view=label();try(var pic=Screenshot.takeScreenshot(mc.getMainRenderTarget())){pic.writeToFile(OUT.resolve(String.format("%02d-%s.png",stage,view)));}
            int captured=stage;var snapshot=current;double localY=mc.player.getY();row=mc.getSingleplayerServer().submit(()->{
                var world=mc.getSingleplayerServer().overworld();var p=mc.getSingleplayerServer().getPlayerList().getPlayers().get(0);var clock=DungeonStateStore.get(world).room(snapshot.instance,"cloud_qa").hazard(snapshot.mechanism,false);
                var result=new LinkedHashMap<String,Object>();result.put("stage",captured);result.put("view",view);result.put("instance",snapshot.instance.toString());result.put("clientAge",age);result.put("clientPhase",phase);result.put("serverPhase",clock.phase().name());result.put("health",p.getHealth());result.put("maxHealth",p.getMaxHealth());result.put("injury",com.dynasty.DynastyInjury.of(p));result.put("fireTicks",p.getRemainingFireTicks());result.put("playerPosition",List.of(p.getX(),p.getY(),p.getZ()));result.put("state",state.toString());
                boolean empty=world.getBlockState(POS).getCollisionShape(world,POS).isEmpty();result.put("collisionEmpty",empty);result.put("clientPhysicalY",localY);
                if(captured==4&&(empty||Math.abs(p.getY()+57)>.05))throw new AssertionError("Warning must support actual landed player: "+result);
                if(captured==5&&(!empty||p.getY()>-58.2))throw new AssertionError("Player must really fall after collision loss: "+result);
                if(captured==6&&!empty)throw new AssertionError("Recovery cannot re-solidify early: "+result);
                if(captured==7&&empty)throw new AssertionError("Cloud must restore actual collision: "+result);
                return result;
            });capturing=true;
        }catch(Throwable e){finish(mc,e);}
    }
    private static void finish(Minecraft mc,Throwable error){
        if(done)return;done=true;
        try{Files.writeString(OUT.resolve(error==null?"PASS.txt":"FAIL.txt"),error==null?"PASS cloud four directions, real player landing triggers warning then physical falling, recovery and restored collision, actual resource reload. One silent disposable client.\n":"FAIL: "+error+"\n");}catch(Exception ignored){}mc.stop();
    }
}
