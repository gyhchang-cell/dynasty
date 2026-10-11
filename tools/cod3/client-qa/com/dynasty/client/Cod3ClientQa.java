package com.dynasty.client;

import com.dynasty.cod3.*;
import com.dynasty.workshop.*;
import com.google.gson.*;
import com.mojang.blaze3d.platform.NativeImage;
import net.minecraft.client.*;
import net.minecraft.client.gui.screens.*;
import net.minecraft.client.multiplayer.ServerData;
import net.minecraft.client.multiplayer.resolver.ServerAddress;
import net.minecraft.core.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.decoration.ArmorStand;
import net.minecraft.world.entity.monster.Skeleton;
import net.minecraft.world.item.*;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.levelgen.*;
import net.minecraft.world.level.levelgen.presets.WorldPresets;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.network.NetworkHooks;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.CompletableFuture;

/** Two actual Forge JVMs, ordinary client/server packets, disposable world and live renderer screenshots. */
@Mod.EventBusSubscriber(modid="dynasty",value=Dist.CLIENT)
public final class Cod3ClientQa {
    private static final String ROLE=System.getProperty("dynasty.cod3ClientQa.role","");
    private static final boolean HOST=ROLE.equals("host");
    private static final Path ROOT=Path.of(System.getProperty("dynasty.cod3ClientQa.output","build/cod3-client/unset/results"));
    private static final Path OUT=ROOT.resolve(ROLE),COORD=ROOT.resolve("coord");
    private static final Gson JSON=new GsonBuilder().setPrettyPrinting().create();
    private record Spec(int template,boolean low,String special,int station,int scale) {}
    private record Stage(int index,String phase,int owner,String uuid,long start) {}
    private static final List<Spec> SPECS=new ArrayList<>();
    static {
        for(boolean low:new boolean[]{false,true})for(int id=14;id<=40;id++)SPECS.add(new Spec(id,low,"",-1,2));
        SPECS.add(new Spec(18,false,"gecko",-1,2));SPECS.add(new Spec(23,false,"gecko",-1,2));
        SPECS.add(new Spec(29,false,"firstperson",-1,2));
        SPECS.add(new Spec(29,false,"reload",-1,2));
        for(int scale:new int[]{2,3,4})for(int station=0;station<8;station++)SPECS.add(new Spec(0,false,"gui",station,scale));

    }
    private static final List<Map<String,Object>> EVIDENCE=new ArrayList<>();
    private static final long DEADLINE=System.nanoTime()+720_000_000_000L;
    private static boolean started,done,ready,captured,listener,swingStarted;
    private static int index=-1,observed=-1,settled,shot;
    private static Stage local;
    private static CompletableFuture<Stage> pending;
    private static CompletableFuture<Void> setup,reload;
    private static LivingEntity fixture;
    private static long activeStart=-1;
    private static ArmorStand camera;
    private static List<?> frozen;
    private static long nextDiagnostic;
    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent event){
        if(ROLE.isBlank()||done||event.phase!=TickEvent.Phase.END)return;var mc=Minecraft.getInstance();
        try{
            if(System.nanoTime()>nextDiagnostic){nextDiagnostic=System.nanoTime()+5_000_000_000L;Files.createDirectories(OUT);Files.writeString(OUT.resolve("state.txt"),"screen="+mc.screen+" overlay="+mc.getOverlay()+" level="+(mc.level!=null)+" stage="+index+" observed="+observed);}
            if(started&&!HOST&&mc.screen instanceof DisconnectedScreen)throw new AssertionError("Peer disconnected: "+mc.screen.getTitle().getString());
            if(System.nanoTime()>DEADLINE)throw new AssertionError("Native cod3 QA timed out");
            if(Files.exists(ROOT.resolve(HOST?"peer/FAIL.txt":"host/FAIL.txt")))throw new AssertionError("Other client failed");
            if(mc.getOverlay()!=null)return;
            if(mc.screen instanceof AccessibilityOnboardingScreen)mc.setScreen(new TitleScreen());
            if(!started&&mc.screen instanceof TitleScreen){
                if(!mc.gameDirectory.getCanonicalPath().contains("/build/cod3-client/"))throw new AssertionError("Refusing ordinary game directory");
                Files.createDirectories(OUT);Files.createDirectories(COORD);mc.options.pauseOnLostFocus=false;mc.options.renderDistance().set(4);mc.options.fov().set(60);mc.options.framerateLimit().set(60);mc.options.guiScale().set(2);mc.resizeDisplay();
                if(!HOST&&!Files.exists(COORD.resolve("listening.txt")))return;started=true;
                if(!HOST){String address="127.0.0.1:25591";ConnectScreen.startConnecting(new TitleScreen(),mc,ServerAddress.parseString(address),new ServerData("Disposable cod3 QA",address,false),false);}
                else{
                    var rules=new GameRules();rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false,null);rules.getRule(GameRules.RULE_DAYLIGHT).set(false,null);
                    mc.createWorldOpenFlows().createFreshLevel("cod3-qa",new LevelSettings("Disposable cod3 QA",GameType.CREATIVE,false,net.minecraft.world.Difficulty.NORMAL,true,rules,WorldDataConfiguration.DEFAULT),new WorldOptions(310,false,false),registry->registry.registryOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.FLAT).createWorldDimensions());
                }return;
            }
            if(mc.level==null||mc.player==null)return;
            if(mc.screen!=null&&!(mc.screen instanceof WorkshopScreen))mc.setScreen(null);
            if(HOST&&setup==null){var server=mc.getSingleplayerServer();setup=server.submit(()->{
                var world=server.overworld();world.setDayTime(6000);
                for(int x=-20;x<=20;x++)for(int z=-20;z<=20;z++)world.setBlockAndUpdate(new BlockPos(x,-61,z),x<0?Blocks.SAND.defaultBlockState():Blocks.STONE.defaultBlockState());
                int station=0;for(var recipe:WorkshopRecipes.ALL){var block=(BlockItem)new WorkshopRecipes.Cost("dynasty:"+recipe.station(),1).stack().getItem();world.setBlockAndUpdate(new BlockPos(station++-4,-60,-4),block.getBlock().defaultBlockState());}
                server.setUsesAuthentication(false);try{server.getConnection().startTcpServerListener(java.net.InetAddress.getByName("127.0.0.1"),25591);}catch(Exception e){throw new RuntimeException(e);}
            });return;}
            if(HOST){
                if(!setup.isDone())return;setup.join();if(!listener){Files.writeString(COORD.resolve("listening.txt"),"cod3");listener=true;}
                var server=mc.getSingleplayerServer();if(server.getPlayerList().getPlayerCount()<2)return;
                if(pending!=null){if(!pending.isDone())return;local=pending.join();pending=null;publish(local);}
                if(index<0){index=0;pending=server.submit(()->prepare(server,index));return;}
                if(local.phase.equals("READY")&&both("ready",index)){pending=server.submit(()->activate(server,index));return;}
                if(both("captured",index)){
                    if(index==SPECS.size()-1){Files.writeString(COORD.resolve("complete.txt"),"cod3");if(Files.exists(ROOT.resolve("peer/PASS.txt")))finish(mc,null);}
                    else{index++;pending=server.submit(()->prepare(server,index));}return;
                }
            }else if(Files.exists(COORD.resolve("complete.txt"))){finish(mc,null);return;}
            if(!Files.exists(COORD.resolve("stage.json")))return;
            var state=JSON.fromJson(Files.readString(COORD.resolve("stage.json")),Stage.class);var spec=SPECS.get(state.index);
            if(state.index!=observed){observed=state.index;settled=0;ready=false;captured=false;swingStarted=false;shot=0;camera=null;reload=null;frozen=null;Cod3VfxRenderer.receive(new Cod3VisualPacket(mc.level.dimension().location().toString(),14,-1,0,mc.level.getGameTime()-24,24,1,net.minecraft.world.phys.Vec3.ZERO,new net.minecraft.world.phys.Vec3(0,0,1),"",0));}
            local=state;
            if(spec.special.equals("firstperson")&&state.phase.equals("ACTIVE")&&!swingStarted){mc.player.swing(InteractionHand.MAIN_HAND);swingStarted=true;}
            if(mc.level.players().size()!=2||mc.level.getEntity(state.owner)==null)return;
            if(spec.special.equals("gui")){
                mc.options.hideGui=false;
                if(!(mc.screen instanceof WorkshopScreen))return;
                if(mc.options.guiScale().get()!=spec.scale){mc.options.guiScale().set(spec.scale);mc.resizeDisplay();}
            }else{
                if(mc.screen!=null)mc.setScreen(null);mc.options.hideGui=!spec.special.equals("firstperson");mc.options.particles().set(spec.low?ParticleStatus.MINIMAL:ParticleStatus.ALL);
                if(spec.special.equals("firstperson")){mc.options.setCameraType(CameraType.FIRST_PERSON);mc.setCameraEntity(mc.player);}
                else if(camera==null){mc.options.setCameraType(CameraType.FIRST_PERSON);camera=new ArmorStand(mc.level,7,-56,18);camera.setNoGravity(true);camera.setYRot(160);camera.setXRot(12);camera.setYHeadRot(160);camera.yHeadRotO=160;camera.setOldPosAndRot();mc.setCameraEntity(camera);}
            }
            if(++settled>=16&&!ready){
                if(spec.special.equals("reload")){
                    if(reload==null){reload=mc.reloadResourcePacks();return;}if(!reload.isDone())return;reload.join();
                }
                ready=true;Files.writeString(COORD.resolve("ready-"+observed+"-"+ROLE+".txt"),state.uuid);
            }
        }catch(Throwable error){finish(mc,error);}
    }
    private static Stage prepare(MinecraftServer server,int stage){
        activeStart=-1;var world=server.overworld();if(fixture!=null)fixture.discard();var spec=SPECS.get(stage);
        fixture=spec.special.equals("gecko")?NpcContent.NPCS.get("lao_chen").get().create(world):EntityType.SKELETON.create(world);
        fixture.moveTo(0,-60,0,180,0);((Mob)fixture).setNoAi(true);fixture.setNoGravity(true);fixture.setInvulnerable(true);fixture.setItemSlot(EquipmentSlot.MAINHAND,new ItemStack(Items.IRON_SWORD));world.addFreshEntity(fixture);
        for(var player:server.getPlayerList().getPlayers()){
            player.closeContainer();player.setGameMode(GameType.CREATIVE);player.teleportTo(world,spec.special.equals("firstperson")?(player.getGameProfile().getName().equals("Cod3Host")?-4:4):0,-60,8,180,0);player.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(spec.special.equals("firstperson")?net.minecraftforge.registries.ForgeRegistries.ITEMS.getValue(new net.minecraft.resources.ResourceLocation("dynasty","qinglong_dao")):Items.IRON_SWORD));
            if(spec.special.equals("gui")){var pos=new BlockPos(spec.station-4,-60,-4);player.teleportTo(world,pos.getX(),-60,-1,180,0);var be=(WorkshopBlockEntity)world.getBlockEntity(pos);NetworkHooks.openScreen(player,be,pos);}
        }
        return new Stage(stage,"READY",fixture.getId(),fixture.getUUID().toString(),world.getGameTime());
    }
    private static Stage activate(MinecraftServer server,int stage){
        var world=server.overworld();var spec=SPECS.get(stage);activeStart=world.getGameTime();
        if(spec.special.equals("firstperson")){for(var player:server.getPlayerList().getPlayers()){player.swing(InteractionHand.MAIN_HAND);Cod3Vfx.afterimage(player,29,0x91CFE0);}}
        else if(spec.template==18||spec.template==23||spec.template==29){fixture.swing(InteractionHand.MAIN_HAND);Cod3Vfx.afterimage(fixture,spec.template,0);if(spec.template==23)fixture.teleportTo(3,-60,0);}
        else if(spec.template==22||spec.template==36)Cod3Vfx.follow(fixture,spec.template,1);
        else if(spec.template>0)Cod3Vfx.send(world,spec.template,new net.minecraft.world.phys.Vec3(0,-60,0),new net.minecraft.world.phys.Vec3(0,0,1),Cod3Catalog.vfx(spec.template).duration(),1);
        return new Stage(stage,"ACTIVE",fixture.getId(),fixture.getUUID().toString(),activeStart);
    }
    @SubscribeEvent public static void serverTick(TickEvent.ServerTickEvent event){
        if(!HOST||event.phase!=TickEvent.Phase.END||fixture==null||activeStart<0||index<0)return;var spec=SPECS.get(index);long age=fixture.level().getGameTime()-activeStart;
        if(spec.template==18||spec.template==29&&!spec.special.equals("firstperson"))fixture.teleportTo(age*.12,-60,0);
        if(spec.special.equals("firstperson")&&age==3)for(var player:((MinecraftServer)event.getServer()).getPlayerList().getPlayers())player.swing(InteractionHand.MAIN_HAND);
    }
    private static void publish(Stage stage)throws Exception{var tmp=COORD.resolve("next.json");Files.writeString(tmp,JSON.toJson(stage));Files.move(tmp,COORD.resolve("stage.json"),StandardCopyOption.REPLACE_EXISTING,StandardCopyOption.ATOMIC_MOVE);}
    private static boolean both(String label,int stage){return Files.exists(COORD.resolve(label+"-"+stage+"-host.txt"))&&Files.exists(COORD.resolve(label+"-"+stage+"-peer.txt"));}
    @SubscribeEvent public static void render(TickEvent.RenderTickEvent event){
        if(ROLE.isBlank()||done||event.phase!=TickEvent.Phase.END||captured||local==null||!ready||!local.phase.equals("ACTIVE"))return;
        var mc=Minecraft.getInstance();if(mc.level==null||mc.getOverlay()!=null)return;
        try{
            var spec=SPECS.get(observed);long age=mc.level.getGameTime()-local.start;
            int duration=spec.template==0?16:Cod3Catalog.vfx(spec.template).duration();var timing=spec.template==0?null:VfxTimeline.timing(Cod3Catalog.vfx(spec.template),duration);
            int target=spec.template==0?4:shot==0?(int)timing.expandEnd():(int)(timing.sustainEnd()+(duration-timing.sustainEnd())*.45);
            if(age<target)return;if(spec.template>0&&age>=duration)throw new AssertionError("Missed VFX lifetime stage="+observed+" shot="+shot+" age="+age);
            var active=Cod3VfxRenderer.class.getDeclaredField("ACTIVE");active.setAccessible(true);var packets=(List<?>)active.get(null);
            var matching=packets.stream().filter(p->((Cod3VisualPacket)p).template()==spec.template&&((Cod3VisualPacket)p).start()==local.start).toList();
            if(spec.template==22&&matching.stream().anyMatch(p->((Cod3VisualPacket)p).entityId()!=local.owner))throw new AssertionError("Avatar not anchored to caster");
            if(spec.template>0&&matching.isEmpty())throw new AssertionError("Client did not receive ordinary network cue: "+spec);
            Map<String,Object> row=new LinkedHashMap<>();row.put("stage",observed);row.put("spec",spec);row.put("phase",shot==0?"expanded":"collapse");row.put("serverStart",local.start);row.put("clientAge",age);row.put("activeInstances",packets.size());row.put("receivedPackets",matching);
            if(spec.template==18||spec.template==23||spec.template==29||spec.template==36&&shot==0){
                var field=Cod3AfterImages.class.getDeclaredField("FRAMES");field.setAccessible(true);var frames=(Map<?,?>)field.get(null);List<Object> saved=new ArrayList<>();
                for(var p:matching){var deque=(Deque<?>)frames.get(p);if(deque==null||deque.isEmpty())throw new AssertionError("Actual model pose history missing");saved.addAll(deque);}
                row.put("savedFrames",saved.stream().map(Object::toString).toList());
                if(spec.template==23){if(frozen==null)frozen=List.copyOf(saved);else if(!frozen.equals(saved))throw new AssertionError("Teleport residue changed after owner movement");}
                if(spec.special.equals("gecko")&&saved.stream().allMatch(f->f.toString().contains("bones=[]")))throw new AssertionError("Gecko ghosts have no frozen bone poses");
            }
            if(spec.special.equals("gui")){var screen=mc.screen;if(!(screen instanceof WorkshopScreen))throw new AssertionError("Server menu did not open registered screen");if(mc.getWindow().getGuiScaledHeight()<166||mc.getWindow().getGuiScaledWidth()<176)throw new AssertionError("GUI does not fit viewport");row.put("guiWidth",mc.getWindow().getGuiScaledWidth());row.put("guiHeight",mc.getWindow().getGuiScaledHeight());}
            int error=org.lwjgl.opengl.GL11.glGetError();if(error!=0)throw new AssertionError("OpenGL error "+error);
            String label=String.format(Locale.ROOT,"%02d-vfx-%02d-%s-%s-%s",observed,spec.template,spec.low?"low":"near",spec.special,shot==0?"expanded":"collapse");
            try(var image=Screenshot.takeScreenshot(mc.getMainRenderTarget())){image.writeToFile(OUT.resolve(label+".png"));}
            EVIDENCE.add(row);shot++;
            if(spec.template==0||shot==2){captured=true;Files.writeString(COORD.resolve("captured-"+observed+"-"+ROLE+".txt"),local.uuid);}
        }catch(Throwable error){finish(mc,error);}
    }
    private static void finish(Minecraft mc,Throwable error){
        if(done)return;done=true;try{Files.createDirectories(OUT);Files.writeString(OUT.resolve("observations.json"),JSON.toJson(EVIDENCE));Files.writeString(OUT.resolve(error==null?"PASS.txt":"FAIL.txt"),error==null?"PASS "+SPECS.size()+" real-world stages / "+EVIDENCE.size()+" captures; role="+ROLE:error.toString());}catch(Exception ignored){}if(error!=null)error.printStackTrace();mc.stop();
    }
}
