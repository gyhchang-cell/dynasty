package com.dynasty.client;

import com.dynasty.dungeon.*;
import com.dynasty.dungeon.client.DungeonMechanismRenderer;
import com.google.gson.GsonBuilder;
import com.mojang.blaze3d.platform.NativeImage;
import net.minecraft.client.*;
import net.minecraft.core.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.Difficulty;
import net.minecraft.world.entity.decoration.ArmorStand;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.item.*;
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

/** One silent disposable actual client: all3 mechanisms, native cargo physics and true hammer health. */
@Mod.EventBusSubscriber(modid="dynasty",value=Dist.CLIENT)
public final class Cod2MechanismClientQa {
    private static final boolean ENABLED=Boolean.getBoolean("dynasty.cod2MechanismQa");
    private static final boolean LIGHTING_ONLY=Boolean.getBoolean("dynasty.cod2MechanismQa.lightingOnly");
    private static final Path OUT=Path.of(System.getProperty("dynasty.cod2MechanismQa.output"));
    private static final BlockPos POS=new BlockPos(0,-60,0),CORE=new BlockPos(-4,-60,4);
    private static final List<Object> REPORT=new ArrayList<>();
    private static final String[] VIEWS={"front","45","side","back"};
    private static boolean started,done,capturing;
    private static int stage;
    private static long deadline=System.nanoTime()+600_000_000_000L;
    private static CompletableFuture<Void> setup,reload;
    private static CompletableFuture<Snapshot> pending;
    private static CompletableFuture<Map<String,Object>> row;
    private static Snapshot current;
    private static ArmorStand camera;
    private static ItemEntity cargo;
    private static UUID currentInstance;
    private static Vec3 startPosition,lastPosition;
    private static double largestNativeStep,maxVerticalSpeed;
    private static final List<Object> TRAJECTORY=new ArrayList<>();
    private record Snapshot(int scene,long born,String mechanism,UUID instance,int cargoId){}
    private static String label(){return stage<12?new String[]{"conveyor","crusher","updraft"}[stage/4]+"-"+VIEWS[stage%4]:
        stage==12?"actual-conveyor-cargo":stage==13?"actual-updraft-flight":stage==14?"crusher-warning":stage==15?"crusher-contact":stage==16?"crusher-recovery":"after-actual-reload";}

    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent event){
        if(!ENABLED||done||event.phase!=TickEvent.Phase.END)return;
        var mc=Minecraft.getInstance();
        try{
            if(System.nanoTime()>deadline)throw new AssertionError("Native mechanism deadline");
            if(!started){
                if(!(mc.screen instanceof net.minecraft.client.gui.screens.TitleScreen))return;
                Files.createDirectories(OUT);started=true;if(LIGHTING_ONLY)stage=4;mc.options.pauseOnLostFocus=false;mc.options.hideGui=true;mc.options.renderDistance().set(4);mc.options.fov().set(55);
                var rules=new GameRules();rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false,null);rules.getRule(GameRules.RULE_DAYLIGHT).set(false,null);rules.getRule(GameRules.RULE_NATURAL_REGENERATION).set(false,null);
                mc.createWorldOpenFlows().createFreshLevel("cod2-mechanisms-qa",new LevelSettings("Disposable3 mechanisms",GameType.CREATIVE,false,Difficulty.NORMAL,true,rules,WorldDataConfiguration.DEFAULT),new WorldOptions(77,false,false),r->r.registryOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.FLAT).createWorldDimensions());return;
            }
            if(mc.level==null||mc.player==null)return;if(mc.screen!=null)mc.setScreen(null);
            var server=mc.getSingleplayerServer();if(server==null)return;
            if(setup==null){setup=server.submit(()->{var level=server.overworld();level.setDayTime(6000);for(int x=-10;x<=12;x++)for(int z=-10;z<=12;z++)level.setBlockAndUpdate(new BlockPos(x,-61,z),Blocks.SMOOTH_STONE.defaultBlockState());});return;}
            if(!setup.isDone()||mc.level.getGameTime()<100)return;setup.join();
            if(capturing){
                if(!row.isDone())return;REPORT.add(row.join());Files.writeString(OUT.resolve("samples.json"),new GsonBuilder().setPrettyPrinting().create().toJson(REPORT)+"\n");
                capturing=false;stage++;
                if(LIGHTING_ONLY&&stage==8){current=null;stage=17;reload=mc.reloadResourcePacks();return;}
                // Warning, impact and recovery are one actual clock cycle and one damaged player.
                if(stage==15||stage==16)return;
                current=null;
                if(stage==18){finish(mc,null);return;}
                if(stage==17){reload=mc.reloadResourcePacks();return;}
                int next=stage;pending=server.submit(()->prepare(server,next));return;
            }
            if(stage==17&&reload!=null){if(!reload.isDone())return;reload.join();REPORT.add(Map.of("reload","actual Minecraft resource reload"));reload=null;pending=server.submit(()->prepare(server,17));return;}
            if(pending==null){pending=server.submit(()->prepare(server,stage));return;}
            if(current==null){if(!pending.isDone())return;current=pending.join();}
            if(camera==null){camera=new ArmorStand(mc.level,0,0,0);camera.setNoGravity(true);mc.options.setCameraType(CameraType.FIRST_PERSON);mc.setCameraEntity(camera);}
            double yaw=stage<12?new double[]{0,45,90,180}[stage%4]:35;
            double center=stage==12?3.5:.5,r=Math.toRadians(yaw);
            camera.setPos(center+Math.sin(r)*8,-56.3-camera.getEyeHeight(),.5-Math.cos(r)*8);
            camera.setYRot((float)yaw);camera.setYHeadRot((float)yaw);camera.yHeadRotO=(float)yaw;camera.setXRot(18);camera.setOldPosAndRot();
        }catch(Throwable e){finish(mc,e);}
    }
    private static Snapshot prepare(MinecraftServer server,int index){
        var world=server.overworld();if(cargo!=null)cargo.discard();cargo=null;TRAJECTORY.clear();largestNativeStep=0;maxVerticalSpeed=0;
        for(int x=-5;x<=7;x++)for(int z=0;z<=4;z++)for(int y=-60;y<=-54;y++)world.setBlockAndUpdate(new BlockPos(x,y,z),Blocks.AIR.defaultBlockState());
        int scene=index<12?index/4:index==12?0:index==13?2:1;
        String mechanism=scene==0?"conveyor_actual":scene==1?"crusher_actual":"updraft_actual";
        var block=scene==0?DungeonContent.CONVEYOR.get():scene==1?DungeonContent.CRUSHER.get():DungeonContent.UPDRAFT.get();
        currentInstance=UUID.randomUUID();var markers=new ArrayList<BlockPos>();
        for(int x=0;x<(index==12?7:1);x++){
            var p=POS.east(x);markers.add(p);world.setBlockAndUpdate(p,block.defaultBlockState().setValue(DungeonMechanismBlock.FACING,index==12?Direction.EAST:Direction.NORTH));
            ((DungeonMechanismBlockEntity)world.getBlockEntity(p)).configure(currentInstance,"mechanism_qa",mechanism,CORE,-1,List.of());
        }
        world.setBlockAndUpdate(CORE,DungeonContent.CORE.get().defaultBlockState());
        var core=(DungeonMechanismBlockEntity)world.getBlockEntity(CORE);core.configure(currentInstance,"mechanism_qa","core",CORE,-1,markers);core.configureRoom(0,false,POS,POS.above(4));
        for(var player:server.getPlayerList().getPlayers()){
            player.setGameMode(index>=14&&index<=16?GameType.SURVIVAL:GameType.CREATIVE);player.setNoGravity(index>=14&&index<=16);player.setInvisible(true);player.clearFire();player.invulnerableTime=0;player.setHealth(20);player.setDeltaMovement(Vec3.ZERO);
            if(index>=14&&index<=16)player.teleportTo(world,.5,-59,.5,0,0);
            else if(index==12||index==13)player.teleportTo(world,-3,-60,0,0,0);
            else player.teleportTo(world,30,-60,30,0,0);
        }
        if(index==12||index==13){
            cargo=new ItemEntity(world,.5,-58.98,.5,new ItemStack(Items.IRON_NUGGET));cargo.setDeltaMovement(Vec3.ZERO);cargo.setPickUpDelay(32767);world.addFreshEntity(cargo);
            startPosition=lastPosition=cargo.position();if(index==12)((DungeonMechanismBlockEntity)world.getBlockEntity(POS)).trigger();
        }
        return new Snapshot(scene,world.getGameTime(),mechanism,currentInstance,cargo==null?-1:cargo.getId());
    }
    @SubscribeEvent public static void serverTick(TickEvent.ServerTickEvent event){
        if(!ENABLED||done||event.phase!=TickEvent.Phase.END||cargo==null||!cargo.isAlive())return;
        largestNativeStep=Math.max(largestNativeStep,cargo.position().distanceTo(lastPosition));lastPosition=cargo.position();maxVerticalSpeed=Math.max(maxVerticalSpeed,cargo.getDeltaMovement().y);
        TRAJECTORY.add(Map.of("position",List.of(cargo.getX(),cargo.getY(),cargo.getZ()),"velocity",List.of(cargo.getDeltaMovement().x,cargo.getDeltaMovement().y,cargo.getDeltaMovement().z),"onGround",cargo.onGround()));
    }
    @SubscribeEvent public static void render(TickEvent.RenderTickEvent event){
        if(!ENABLED||done||capturing||current==null||event.phase!=TickEvent.Phase.END)return;
        var mc=Minecraft.getInstance();if(mc.level==null||mc.getOverlay()!=null)return;
        try{
            long age=mc.level.getGameTime()-current.born;var state=mc.level.getBlockState(POS);
            if(!(mc.level.getBlockEntity(POS) instanceof DungeonMechanismBlockEntity be)||!current.instance.equals(be.instance()))return;
            if(stage<12||stage==17){if(age<20)return;}else if(stage==12){if(age<65)return;}else if(stage==13){if(age<24)return;}
            else{int wanted=stage-13;if(state.getValue(DungeonMechanismBlock.STAGE)!=wanted)return;if(stage==14&&age<4)return;}
            if(mc.getBlockRenderer().getBlockModel(state)==mc.getModelManager().getMissingModel())throw new AssertionError("Actual missing block model");
            if(current.scene==1){
                if(!(mc.getBlockEntityRenderDispatcher().getRenderer(be) instanceof DungeonMechanismRenderer))throw new AssertionError("Wrong actual hammer renderer");
                var head=mc.getModelManager().getModel(DungeonMechanismRenderer.HAMMER_MODEL);
                if(head==mc.getModelManager().getMissingModel()||head.getQuads(state,null,net.minecraft.util.RandomSource.create()).isEmpty())throw new AssertionError("Actual hammer head not baked");
            }
            for(String name:List.of("conveyor","crusher_base","crusher_head","updraft"))try(var stream=mc.getResourceManager().open(new ResourceLocation("dynasty","textures/block/cod2_mechanism/"+name+".png"));var png=NativeImage.read(stream)){if(png.getWidth()!=16||png.getHeight()!=16)throw new AssertionError("Actual non16 texture");}
            if(stage==12||stage==13){var clientCargo=mc.level.getEntity(current.cargoId);if(clientCargo==null)throw new AssertionError("Actual cargo missing client tracking");if(stage==12&&clientCargo.getX()<1.5||stage==13&&clientCargo.getY()<-58.8)return;}
            String view=label();int clientPhase=state.getValue(DungeonMechanismBlock.STAGE);float progress=be.visualProgress(mc.getFrameTime());
            try(var picture=Screenshot.takeScreenshot(mc.getMainRenderTarget())){picture.writeToFile(OUT.resolve(String.format("%02d-%s.png",stage,view)));}
            int captured=stage;row=mc.getSingleplayerServer().submit(()->{
                var world=mc.getSingleplayerServer().overworld();var player=mc.getSingleplayerServer().getPlayerList().getPlayers().get(0);
                var report=new LinkedHashMap<String,Object>();report.put("stage",captured);report.put("view",view);report.put("clientAge",age);report.put("clientPhase",clientPhase);report.put("clientVisualProgress",progress);report.put("actualState",state.toString());report.put("actualHealth",player.getHealth());report.put("instance",current.instance.toString());
                var room=DungeonStateStore.get(world).room(current.instance,"mechanism_qa");var clock=room.hazard(current.mechanism,false);report.put("serverPhase",clock.phase().name());report.put("serverPhaseTicks",clock.ticks());
                if(current.scene==1)report.put("visibleHammerY",DungeonTrapGeometry.hammerY(clientPhase,progress));
                if(captured==14&&player.getHealth()!=20)throw new AssertionError("Warning inflicted damage");
                if((captured==15||captured==16)&&(player.getHealth()>=20||player.getHealth()<16))throw new AssertionError("Actual hammer health outside original bounded contact");
                if(captured==12||captured==13){
                    if(cargo==null||!cargo.isAlive()||cargo.getItem().getCount()!=1)throw new AssertionError("Actual cargo lost or duplicated");
                    var distance=cargo.position().subtract(startPosition);if(captured==12&&distance.x<1||captured==13&&distance.y<.15)throw new AssertionError("Actual natural physics did not move cargo");
                    if(largestNativeStep>.5||maxVerticalSpeed>.330001)throw new AssertionError("Native motion exceeded finite force");
                    report.put("actualCargoUuid",cargo.getUUID().toString());report.put("start",List.of(startPosition.x,startPosition.y,startPosition.z));report.put("end",List.of(cargo.getX(),cargo.getY(),cargo.getZ()));report.put("largestNativeStep",largestNativeStep);report.put("maxVerticalSpeed",maxVerticalSpeed);report.put("nativeTrajectory",new ArrayList<>(TRAJECTORY));
                }
                return report;
            });capturing=true;
        }catch(Throwable e){finish(mc,e);}
    }
    private static void finish(Minecraft mc,Throwable error){
        if(done)return;done=true;
        try{Files.writeString(OUT.resolve(error==null?"PASS.txt":"FAIL.txt"),error==null?(LIGHTING_ONLY?"PASS actual hammer four directions and actual resource reload after the head-lighting repair; earlier native run2 contains unchanged server physics/contact acceptance.\n":"PASS actual3 mechanism models,4 directions each, original room clocks, real dropped-cargo belt travel and updraft flight, real-player hammer warning/contact/recovery health, actual resource reload. One disposable native client; not full dungeon or multiplayer acceptance.\n"):"FAIL: "+error+"\n");if(error!=null)try(var picture=Screenshot.takeScreenshot(mc.getMainRenderTarget())){picture.writeToFile(OUT.resolve("FAILED.png"));}}catch(Exception ignored){}mc.stop();
    }
}
