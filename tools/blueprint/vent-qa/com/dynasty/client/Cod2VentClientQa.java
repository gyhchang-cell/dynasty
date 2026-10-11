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
public final class Cod2VentClientQa {
    private static final boolean ENABLED=Boolean.getBoolean("dynasty.cod2VentQa");
    private static final Path OUT=Path.of(System.getProperty("dynasty.cod2VentQa.output","build/disabled-vent-qa"));
    private static final BlockPos POS=new BlockPos(0,-60,0),CORE=new BlockPos(-4,-60,4);
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
    private static String label(){return stage<8?(stage<4?"steam-":"flame-")+VIEWS[stage%4]:stage<14?(stage<11?"steam-":"flame-")+new String[]{"warning","active","cooldown"}[(stage-8)%3]:"after-resource-reload";}
    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent event){
        if(!ENABLED||done||event.phase!=TickEvent.Phase.END)return;var mc=Minecraft.getInstance();
        try{
            if(System.nanoTime()>DEADLINE)throw new AssertionError("Native vent timeout, stage="+stage);
            if(!started){
                if(!(mc.screen instanceof net.minecraft.client.gui.screens.TitleScreen))return;
                Files.createDirectories(OUT);started=true;mc.options.pauseOnLostFocus=false;mc.options.hideGui=true;mc.options.renderDistance().set(4);mc.options.fov().set(55);
                var rules=new GameRules();rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false,null);rules.getRule(GameRules.RULE_DAYLIGHT).set(false,null);rules.getRule(GameRules.RULE_NATURAL_REGENERATION).set(false,null);
                mc.createWorldOpenFlows().createFreshLevel("cod2-vents-qa",new LevelSettings("Disposable vents",GameType.CREATIVE,false,Difficulty.NORMAL,true,rules,WorldDataConfiguration.DEFAULT),new WorldOptions(78,false,false),r->r.registryOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.FLAT).createWorldDimensions());return;
            }
            if(mc.level==null||mc.player==null)return;if(mc.screen!=null)mc.setScreen(null);var server=mc.getSingleplayerServer();if(server==null)return;
            if(setup==null){setup=server.submit(()->{var world=server.overworld();world.setDayTime(6000);for(int x=-10;x<=12;x++)for(int z=-10;z<=12;z++)world.setBlockAndUpdate(new BlockPos(x,-61,z),Blocks.SMOOTH_STONE.defaultBlockState());});return;}
            if(!setup.isDone()||mc.level.getGameTime()<100)return;setup.join();
            if(capturing){
                if(!row.isDone())return;REPORT.add(row.join());Files.writeString(OUT.resolve("samples.json"),new GsonBuilder().setPrettyPrinting().create().toJson(REPORT)+"\n");capturing=false;stage++;
                if(stage==9||stage==10||stage==12||stage==13)return;
                current=null;armed=false;if(stage==15){finish(mc,null);return;}if(stage==14){reload=mc.reloadResourcePacks();return;}
                int next=stage;pending=server.submit(()->prepare(server,next));return;
            }
            if(reload!=null){if(!reload.isDone())return;reload.join();REPORT.add(Map.of("reload","actual Minecraft resource reload"));reload=null;pending=server.submit(()->prepare(server,14));return;}
            if(pending==null){pending=server.submit(()->prepare(server,stage));return;}
            if(current==null){if(!pending.isDone())return;current=pending.join();mc.levelRenderer.allChanged();}
            if(camera==null){camera=new ArmorStand(mc.level,0,0,0);camera.setNoGravity(true);mc.options.setCameraType(CameraType.FIRST_PERSON);mc.setCameraEntity(camera);}
            double yaw=stage<8?new double[]{0,45,90,180}[stage%4]:135,r=Math.toRadians(yaw);
            camera.setPos(.5+Math.sin(r)*6,-57.1-camera.getEyeHeight(),.5-Math.cos(r)*6);
            // Render a fully loaded fixture before a real survival player enters the original clock range.
            if((stage==8||stage==11)&&!armed){
                if(arm==null&&mc.level.getGameTime()-current.born>=60){var ready=current;arm=server.submit(()->{
                    for(var p:server.getPlayerList().getPlayers())p.setGameMode(GameType.SURVIVAL);
                    return new Snapshot(ready.flame,server.overworld().getGameTime(),ready.mechanism,ready.instance);
                });}
                if(arm!=null&&arm.isDone()){current=arm.join();arm=null;armed=true;}
            }
            camera.setYRot((float)yaw);camera.setYHeadRot((float)yaw);camera.yHeadRotO=(float)yaw;camera.setXRot(20);camera.setOldPosAndRot();
        }catch(Throwable e){finish(mc,e);}
    }
    private static Snapshot prepare(MinecraftServer server,int n){
        var world=server.overworld();world.removeBlock(POS,false);world.removeBlock(CORE,false);boolean flame=n>=4&&n<8||n>=11&&n<14;
        var id=UUID.randomUUID();String mechanism=(flame?"flame":"steam")+"_actual";boolean live=n>=8&&n<14;
        world.setBlockAndUpdate(POS,(flame?DungeonContent.FLAME.get():DungeonContent.STEAM.get()).defaultBlockState().setValue(DungeonMechanismBlock.FACING,live?Direction.SOUTH:Direction.NORTH));
        ((DungeonMechanismBlockEntity)world.getBlockEntity(POS)).configure(id,"vent_qa",mechanism,CORE,-1,List.of());
        world.setBlockAndUpdate(CORE,DungeonContent.CORE.get().defaultBlockState());var core=(DungeonMechanismBlockEntity)world.getBlockEntity(CORE);core.configure(id,"vent_qa","core",CORE,-1,List.of(POS));core.configureRoom(0,false,POS,POS.above(3));
        for(var p:server.getPlayerList().getPlayers()){
            // A prior 3/20 hit adds six injury points: its next tick caps health at 19.64.
            // Cure only this disposable fixture through the existing API before resetting health.
            com.dynasty.DynastyInjury.treat(p,com.dynasty.DynastyInjury.MAX,"QA fixture reset");com.dynasty.DynastyInjury.tick(p);p.removeAllEffects();
            p.setGameMode(live?GameType.SPECTATOR:GameType.CREATIVE);p.setNoGravity(live);p.setInvisible(true);p.clearFire();p.invulnerableTime=0;p.setHealth(20);p.setDeltaMovement(Vec3.ZERO);p.hurtMarked=true;
            p.teleportTo(world,live?.5:30,-60,live?2:30,0,0);
        }
        return new Snapshot(flame,world.getGameTime(),mechanism,id);
    }
    @SubscribeEvent public static void render(TickEvent.RenderTickEvent event){
        if(!ENABLED||done||capturing||current==null||event.phase!=TickEvent.Phase.END)return;var mc=Minecraft.getInstance();if(mc.level==null||mc.getOverlay()!=null)return;
        try{
            if((stage==8||stage==11)&&!armed)return;
            long age=mc.level.getGameTime()-current.born;var state=mc.level.getBlockState(POS);
            if(!(mc.level.getBlockEntity(POS) instanceof DungeonMechanismBlockEntity be)||!current.instance.equals(be.instance()))return;
            int phase=state.getValue(DungeonMechanismBlock.STAGE);
            if(stage<8||stage==14){if(age<20)return;}else{int wanted=1+(stage-8)%3;if(phase!=wanted||wanted==1&&age<12)return;}
            if(mc.getBlockRenderer().getBlockModel(state)==mc.getModelManager().getMissingModel())throw new AssertionError("Missing actual vent model");
            for(String name:List.of("steam","flame"))try(var stream=mc.getResourceManager().open(new ResourceLocation("dynasty","textures/block/cod2_vents/"+name+".png"));var png=NativeImage.read(stream)){if(png.getWidth()!=16||png.getHeight()!=16)throw new AssertionError("Non16 actual PNG");}
            String view=label();try(var pic=Screenshot.takeScreenshot(mc.getMainRenderTarget())){pic.writeToFile(OUT.resolve(String.format("%02d-%s.png",stage,view)));}
            int captured=stage;var snapshot=current;row=mc.getSingleplayerServer().submit(()->{
                var world=mc.getSingleplayerServer().overworld();var p=mc.getSingleplayerServer().getPlayerList().getPlayers().get(0);var clock=DungeonStateStore.get(world).room(snapshot.instance,"vent_qa").hazard(snapshot.mechanism,false);
                var result=new LinkedHashMap<String,Object>();result.put("stage",captured);result.put("view",view);result.put("instance",snapshot.instance.toString());result.put("clientAge",age);result.put("clientPhase",phase);result.put("serverPhase",clock.phase().name());result.put("health",p.getHealth());result.put("maxHealth",p.getMaxHealth());result.put("injury",com.dynasty.DynastyInjury.of(p));result.put("fireTicks",p.getRemainingFireTicks());result.put("playerPosition",List.of(p.getX(),p.getY(),p.getZ()));result.put("state",state.toString());
                if(captured==8||captured==11){if(p.getHealth()!=20||p.isOnFire())throw new AssertionError("Warning caused early injury: "+result);}
                if(captured==9||captured==10||captured==12||captured==13){if(p.getHealth()>=20||p.getHealth()<14||!p.isOnFire())throw new AssertionError("Missing or excessive actual vent injury: "+result);}
                for(int z=1;z<=4;z++)if(!world.getBlockState(POS.south(z)).isAir())throw new AssertionError("Vent placed terrain/fire blocks");
                return result;
            });capturing=true;
        }catch(Throwable e){finish(mc,e);}
    }
    private static void finish(Minecraft mc,Throwable error){
        if(done)return;done=true;
        try{Files.writeString(OUT.resolve(error==null?"PASS.txt":"FAIL.txt"),error==null?"PASS2 actual vent models four directions, same-cycle warning/active/cooldown for each, real player damage/burning only after warning, no fire blocks, actual resource reload. One silent disposable client.\n":"FAIL: "+error+"\n");}catch(Exception ignored){}mc.stop();
    }
}
