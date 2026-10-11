package com.dynasty.client;

import com.dynasty.blueprint.*;
import com.dynasty.blueprint.elite.*;
import com.google.gson.*;
import net.minecraft.client.*;
import net.minecraft.client.gui.screens.*;
import net.minecraft.client.multiplayer.ServerData;
import net.minecraft.client.multiplayer.resolver.ServerAddress;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.decoration.ArmorStand;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.levelgen.WorldOptions;
import net.minecraft.world.level.levelgen.presets.WorldPresets;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.CompletableFuture;

/** A finite load case in the existing optional QA source set, never packaged in the mod. */
@Mod.EventBusSubscriber(modid="dynasty",value=Dist.CLIENT)
public final class BlueprintStressQa {
    private static final boolean ENABLED=Boolean.getBoolean("dynasty.blueprintQa.stress");
    private static final String ROLE=System.getProperty("dynasty.blueprintQa","");
    private static final boolean HOST=ROLE.equals("host"),SOLO=Boolean.getBoolean("dynasty.blueprintQa.solo");
    private static final Path ROOT=Path.of(System.getProperty("dynasty.blueprintQa.output","build/blueprint-client/results"));
    private static final Path OUT=ROOT.resolve(ROLE),COORD=ROOT.resolve("coord");
    private static final Gson JSON=new GsonBuilder().setPrettyPrinting().create();
    private static final List<Mob> ACTORS=new ArrayList<>();
    private static final List<Map<String,Object>> SERVER=new ArrayList<>(),CLIENT=new ArrayList<>();
    private static final Set<String> RENDERED=new HashSet<>();
    private static final long DEADLINE=System.nanoTime()+900_000_000_000L;
    private static CompletableFuture<Void> setup;
    private static boolean started,listener,done;
    private static long begin=-1,nextSample;
    private static int frames;
    private static ArmorStand camera;
    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent event){
        if(!ENABLED||ROLE.isBlank()||done||event.phase!=TickEvent.Phase.END)return;
        var mc=Minecraft.getInstance();
        try{
            if(System.nanoTime()>DEADLINE)throw new AssertionError("Finite load case timed out");
            if(Files.exists(ROOT.resolve(HOST?"peer/FAIL.txt":"host/FAIL.txt")))throw new AssertionError("Other real client failed");
            if(mc.getOverlay()!=null)return;
            if(mc.screen instanceof AccessibilityOnboardingScreen)mc.setScreen(new TitleScreen());
            if(started&&mc.screen instanceof DisconnectedScreen)throw new AssertionError("Native stress peer disconnected");
            if(!started&&mc.screen instanceof TitleScreen){
                if(!mc.gameDirectory.getCanonicalPath().endsWith("/build/blueprint-client/"+ROLE))throw new AssertionError("Refusing live game directory");
                Files.createDirectories(OUT);Files.createDirectories(COORD);mc.options.pauseOnLostFocus=false;mc.options.renderDistance().set(4);mc.options.fov().set(72);
                if(!HOST&&!Files.exists(COORD.resolve("listening.txt")))return;started=true;
                if(!HOST){String address="127.0.0.1:25587";ConnectScreen.startConnecting(new TitleScreen(),mc,ServerAddress.parseString(address),new ServerData("Disposable finite load case",address,false),false);}
                else{
                    var rules=new GameRules();rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false,null);rules.getRule(GameRules.RULE_DAYLIGHT).set(false,null);
                    mc.createWorldOpenFlows().createFreshLevel("blueprint-stress-"+System.getProperty("dynasty.blueprintQa.run")+"-"+System.currentTimeMillis(),
                        new LevelSettings("Disposable finite load case",GameType.CREATIVE,false,net.minecraft.world.Difficulty.NORMAL,true,rules,WorldDataConfiguration.DEFAULT),new WorldOptions(57,false,false),
                        registry->registry.registryOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.FLAT).createWorldDimensions());
                }return;
            }
            if(mc.level==null||mc.player==null)return;if(mc.screen!=null)mc.setScreen(null);
            if(HOST&&setup==null){setup=mc.getSingleplayerServer().submit(()->prepare(mc.getSingleplayerServer()));return;}
            if(HOST){
                if(!setup.isDone())return;setup.join();var server=mc.getSingleplayerServer();
                if(!listener){if(!SOLO&&!server.publishServer(GameType.CREATIVE,false,25587))throw new AssertionError("Native disposable LAN publication failed");Files.writeString(COORD.resolve("listening.txt"),"stress");listener=true;}
                if(Files.exists(COORD.resolve("complete.txt"))&&(SOLO||Files.exists(ROOT.resolve("peer/PASS.txt")))){finish(mc,null);return;}
                if(!SOLO&&server.getPlayerList().getPlayerCount()!=2)return;
            }else if(Files.exists(COORD.resolve("complete.txt"))){finish(mc,null);return;}
            if(camera==null){camera=new ArmorStand(mc.level,0,-40,39);camera.setYRot(180);camera.setYHeadRot(180);camera.yHeadRotO=180;camera.setXRot(28);camera.setOldPosAndRot();mc.options.hideGui=true;mc.setCameraEntity(camera);}
            if(!mc.levelRenderer.isChunkCompiled(new BlockPos(0,-61,0))||mc.level.getBlockState(new BlockPos(0,-61,0)).isAir())return;
            if(++frames>=40&&!Files.exists(COORD.resolve("ready-"+ROLE+".txt")))Files.writeString(COORD.resolve("ready-"+ROLE+".txt"),"actual native frames and floor ready");
        }catch(Throwable error){finish(mc,error);}
    }
    private static void prepare(MinecraftServer server){
        var world=server.overworld();world.setDayTime(18000);server.setUsesAuthentication(false);
        for(int x=-40;x<=40;x++)for(int z=-40;z<=40;z++)world.setBlockAndUpdate(new BlockPos(x,-61,z),Blocks.STONE.defaultBlockState());
        for(int x=19;x<=30;x++)for(int z=-8;z<=8;z++){
            world.setBlockAndUpdate(new BlockPos(x,-62,z),Blocks.STONE.defaultBlockState());world.setBlockAndUpdate(new BlockPos(x,-61,z),Blocks.WATER.defaultBlockState());world.setBlockAndUpdate(new BlockPos(x,-60,z),Blocks.WATER.defaultBlockState());
        }
        for(var entry:BlueprintEntities.ENTITIES.getEntries()){
            var e=entry.get().create(world);if(e instanceof TemplateMob mob){spawn(mob,ACTORS.size());ACTORS.add(mob);}
        }
        if(ACTORS.size()!=30)throw new AssertionError("Load case must include all thirty real basic types");
        ACTORS.add(spawn(EliteContent.HEADLESS.get().create(world),30));ACTORS.add(spawn(EliteContent.BIRD.get().create(world),31));ACTORS.add(spawn(EliteContent.MECHANIST.get().create(world),32));ACTORS.add(spawn(EliteContent.JINWU.get().create(world),33));ACTORS.add(spawn(EliteContent.FOX.get().create(world),34));ACTORS.add(spawn(EliteContent.HAMMER.get().create(world),35));ACTORS.add(spawn(EliteContent.SPIDER_WOMAN.get().create(world),36));
        for(int n=37;n<48;n++){var type=switch(n%4){case 0->BlueprintEntities.FUFA_JIJIU.get();case 1->BlueprintEntities.KUIJUN_SISHI.get();case 2->BlueprintEntities.TIESUO_CHIHOU.get();default->BlueprintEntities.LIANNU_ZHENZU.get();};ACTORS.add(spawn(type.create(world),n));}
        for(var player:server.getPlayerList().getPlayers()){
            player.teleportTo(world,0,-60,0,0,0);player.setGameMode(player.getGameProfile().getName().equals("BlueprintHost")?GameType.SURVIVAL:GameType.CREATIVE);
            player.getAttribute(Attributes.MAX_HEALTH).setBaseValue(100000);player.setHealth(100000);player.setInvulnerable(false);
        }
    }
    private static <T extends Mob> T spawn(T mob,int slot){
        if(mob==null)throw new AssertionError("Native registry rejected stress actor");double theta=slot*Math.PI*2/48,radius=13+(slot%3)*5;
        mob.moveTo(Math.cos(theta)*radius,-60,Math.sin(theta)*radius,0,0);mob.setPersistenceRequired();
        if(mob instanceof TemplateMob template){template.bindEncounter("qa-finite-pressure");
            if(template.kind()==TemplateMob.Kind.SERPENT||template.kind()==TemplateMob.Kind.DROWNER)template.setPos(23+(slot%3),-60,slot%5-2);
            if(template.kind()==TemplateMob.Kind.SKULL||template.kind()==TemplateMob.Kind.LANTERN_BAT||template.kind()==TemplateMob.Kind.BLIND_FISH||template.kind()==TemplateMob.Kind.YECHA)template.setPos(template.position().add(0,4,0));
        }
        if(mob instanceof Jinwu guard)guard.bindEncounter("qa-finite-pressure");
        if(mob instanceof GhostCarriageBird)mob.setPos(mob.position().add(0,6,0));
        mob.level().addFreshEntity(mob);return mob;
    }
    @SubscribeEvent public static void serverTick(TickEvent.ServerTickEvent event){
        if(!ENABLED||!HOST||event.phase!=TickEvent.Phase.END||ACTORS.isEmpty()||done)return;
        try{
            var server=net.minecraftforge.server.ServerLifecycleHooks.getCurrentServer();var world=server.overworld();
            if(Files.exists(COORD.resolve("complete.txt")))return;
            if(!Files.exists(COORD.resolve("ready-host.txt"))||!SOLO&&!Files.exists(COORD.resolve("ready-peer.txt")))return;
            if(begin<0)begin=world.getGameTime();long age=world.getGameTime()-begin;
            int replaced=0;var host=world.players().stream().filter(p->p.getGameProfile().getName().equals("BlueprintHost")).findFirst().orElseThrow();
            for(int n=0;n<ACTORS.size();n++){
                var mob=ACTORS.get(n);
                if((!mob.isAlive()||mob.isRemoved()||mob.distanceToSqr(host)>40*40)&&replaced<3){mob.discard();mob=(Mob)mob.getType().create(world);spawn(mob,n);ACTORS.set(n,mob);replaced++;}
                if(mob.isAlive()){if(mob.isNoAi())throw new AssertionError("Stress case disables actual AI");if(mob.getTarget()==null&&age%20==0)mob.setTarget(host);}
            }
            if(age%20==0){
                var box=new net.minecraft.world.phys.AABB(-48,-64,-48,48,-20,48);int entities=world.getEntitiesOfClass(Entity.class,box).size();
                if(entities>512)throw new AssertionError("Finite 48-actor case exceeded bounded entity budget: "+entities);
                SERVER.add(Map.of("tick",world.getGameTime(),"actorsAlive",ACTORS.stream().filter(Entity::isAlive).count(),"loadedEntities",entities,"averageTickMs",server.getAverageTickTime(),"hostHealth",host.getHealth()));
                if(SERVER.size()>190)throw new AssertionError("Load samples exceeded finite budget");
            }
            if(age>=3600&&!Files.exists(COORD.resolve("complete.txt"))){
                if(SERVER.size()<180)throw new AssertionError("Less than three real minutes were sampled");
                Files.writeString(OUT.resolve("server-performance.json"),JSON.toJson(Map.of("samples",SERVER,"durationTicks",age,"slotCount",48,"types",37,
                    "scope","Artificial finite 48-slot combat load: all thirty basic types plus seven elites; ordinary AI and physics, bounded replacements after death; no distribution or final balance certification")));
                Files.writeString(COORD.resolve("complete.txt"),"3600 native ticks observed");
            }
        }catch(Throwable error){try{Files.writeString(OUT.resolve("FAIL.txt"),"Server load case failed: "+error);}catch(Exception ignored){}throw new RuntimeException(error);}
    }
    @SubscribeEvent public static void render(TickEvent.RenderTickEvent event){
        if(!ENABLED||done||event.phase!=TickEvent.Phase.END)return;var mc=Minecraft.getInstance();if(mc.level==null||camera==null||mc.getOverlay()!=null)return;
        try{
            for(var e:mc.level.entitiesForRendering())if(e instanceof TemplateMob||e instanceof HeadlessGeneral||e instanceof GhostCarriageBird||e instanceof Mechanist||e instanceof Jinwu||e instanceof HammerGuardian||e instanceof FoxMatron||e instanceof SpiderWoman){
                if(mc.getEntityRenderDispatcher().getRenderer(e) instanceof software.bernie.geckolib.renderer.GeoEntityRenderer<?> renderer&&renderer.getGeoModel().getBone("root").isPresent())
                    RENDERED.add(net.minecraftforge.registries.ForgeRegistries.ENTITY_TYPES.getKey(e.getType()).toString());
            }
            if(System.nanoTime()<nextSample)return;nextSample=System.nanoTime()+1_000_000_000L;
            if(com.dynasty.blueprint.client.TemplateSecondaryMotion.activeStates()>64)throw new AssertionError("Secondary motion exceeded its finite cache");
            var runtime=Runtime.getRuntime();CLIENT.add(Map.of("tick",mc.level.getGameTime(),"fps",mc.getFps(),"heapBytes",runtime.totalMemory()-runtime.freeMemory(),"renderedTypes",RENDERED.size(),"players",mc.level.players().size(),"secondaryStates",com.dynasty.blueprint.client.TemplateSecondaryMotion.activeStates()));
            if(CLIENT.size()>600)throw new AssertionError("Client load samples exceeded finite budget");
        }catch(Throwable error){finish(mc,error);}
    }
    private static void finish(Minecraft mc,Throwable error){
        if(done)return;done=true;
        try{
            if(error==null){
                if(RENDERED.size()!=37||CLIENT.size()<150)throw new AssertionError("Full actual render/load coverage missing: types="+RENDERED.size()+" samples="+CLIENT.size());
                try(var frame=Screenshot.takeScreenshot(mc.getMainRenderTarget())){frame.writeToFile(OUT.resolve("stress-final.png"));}
                Files.writeString(OUT.resolve("client-performance.json"),JSON.toJson(Map.of("samples",CLIENT,"renderedTypes",RENDERED,"scope","Actual native FPS and heap during a finite three-minute combat workload; figures apply to this Mac, render distance4, current frozen resources and concurrent local clients")));
            }
            Files.writeString(OUT.resolve(error==null?"PASS.txt":"FAIL.txt"),error==null?"PASS: finite native three-minute 48-slot workload completed; all 36 actor types rendered with ordinary AI, bounded entity/cache samples. Review measured performance separately; this does not certify world distribution or final encounter balance.\n":"FAIL: "+error+"\n");
        }catch(Throwable failure){failure.printStackTrace();try{Files.writeString(OUT.resolve("FAIL.txt"),"FAIL: "+failure);}catch(Exception ignored){}}
        mc.setCameraEntity(mc.player);mc.stop();
    }
}
