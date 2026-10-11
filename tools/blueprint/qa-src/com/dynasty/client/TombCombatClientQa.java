package com.dynasty.client;

import com.dynasty.blueprint.*;
import com.dynasty.structure.*;
import com.google.gson.*;
import net.minecraft.client.*;
import net.minecraft.client.gui.screens.*;
import net.minecraft.client.multiplayer.ServerData;
import net.minecraft.client.multiplayer.resolver.ServerAddress;
import net.minecraft.core.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.*;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.decoration.ArmorStand;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.levelgen.*;
import net.minecraft.world.level.levelgen.flat.*;
import net.minecraft.world.level.levelgen.presets.WorldPresets;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.CompletableFuture;

/** Finite native acceptance of the existing generated tomb and ordinary three-actor AI. */
@Mod.EventBusSubscriber(modid="dynasty",value=Dist.CLIENT)
public final class TombCombatClientQa {
    private static final boolean ENABLED=Boolean.getBoolean("dynasty.blueprintQa.tombCombat");
    private static final String ROLE=System.getProperty("dynasty.blueprintQa","");
    private static final String RUN=System.getProperty("dynasty.blueprintQa.run","");
    private static final String RESUME=System.getProperty("dynasty.blueprintQa.resumeWorld","");
    private static final String PREVIOUS=System.getProperty("dynasty.blueprintQa.previousRun","");
    private static final boolean HOST=ROLE.equals("host"),SOLO=Boolean.getBoolean("dynasty.blueprintQa.solo");
    private static final Path ROOT=Path.of(System.getProperty("dynasty.blueprintQa.output","build/blueprint-client/results"));
    private static final Path OUT=ROOT.resolve(ROLE),COORD=ROOT.resolve("coord");
    private static final Gson JSON=new GsonBuilder().setPrettyPrinting().create();
    private static final String SITE="dynasty:imperial_tomb@0";
    private static final List<Map<String,Object>> SAMPLES=new ArrayList<>(),EVENTS=new ArrayList<>();
    private static final Map<TemplateMob.Kind,TemplateMob> ACTORS=new EnumMap<>(TemplateMob.Kind.class);
    private static JsonObject checkpoint;
    private static CompletableFuture<Void> setup,reload;
    private static boolean started,listener,done,ready,combat,escape,escaped,returned,rejoined,reloadObserved;
    private static long begin=-1,escapeAt=-1,lastSample=-1,lastNativeSample=-1,curseEpoch=-1,slashEpoch=-2;
    private static int frames,disconnectPhase,heartbeat;
    private static ArmorStand camera;
    private static BlockPos water,entry;
    private static final Set<String> RENDERED=new HashSet<>();
    private static final long DEADLINE=System.nanoTime()+900_000_000_000L;

    private static FlatLevelSource terrain(net.minecraft.core.RegistryAccess registry){
        var settings=FlatLevelGeneratorSettings.getDefault(registry.lookupOrThrow(Registries.BIOME),registry.lookupOrThrow(Registries.STRUCTURE_SET),registry.lookupOrThrow(Registries.PLACED_FEATURE));
        settings.getLayersInfo().clear();settings.getLayersInfo().add(new FlatLayerInfo(127,Blocks.STONE));settings.getLayersInfo().add(new FlatLayerInfo(1,Blocks.GRASS_BLOCK));settings.updateLayers();return new FlatLevelSource(settings);
    }
    @SubscribeEvent public static void client(TickEvent.ClientTickEvent e){
        if(!ENABLED||ROLE.isBlank()||done||e.phase!=TickEvent.Phase.END)return;
        var mc=Minecraft.getInstance();
        try{
            if(System.nanoTime()>DEADLINE)throw new AssertionError("Finite tomb combat acceptance timed out");
            if(Files.exists(ROOT.resolve(HOST?"peer/FAIL.txt":"host/FAIL.txt")))throw new AssertionError("Other native client failed");
            if(++heartbeat%40==0){Files.createDirectories(OUT);Files.writeString(OUT.resolve("client-live.json"),JSON.toJson(Map.of("screen",mc.screen==null?"NONE":mc.screen.getClass().getName(),"overlay",mc.getOverlay()==null?"NONE":mc.getOverlay().getClass().getName(),"world",mc.level!=null,"player",mc.player!=null,"started",started,"disconnectPhase",disconnectPhase)));}
            if(started&&disconnectPhase==0&&mc.screen instanceof DisconnectedScreen)throw new AssertionError("Actual peer disconnected during native login: "+disconnectReason(mc.screen));
            if(HOST&&started&&!RESUME.isEmpty()&&mc.screen instanceof ConfirmScreen confirm&&confirm.getTitle().getContents() instanceof net.minecraft.network.chat.contents.TranslatableContents title&&title.getKey().equals("selectWorld.backupQuestion.experimental")){
                for(var child:confirm.children())if(child instanceof net.minecraft.client.gui.components.Button button&&button.getMessage().equals(net.minecraft.network.chat.CommonComponents.GUI_PROCEED)){button.onPress();return;}
                throw new AssertionError("Disposable world lacks native Proceed action");
            }
            if(mc.getOverlay()!=null)return;
            if(mc.screen instanceof AccessibilityOnboardingScreen)mc.setScreen(new TitleScreen());
            if(!started&&mc.screen instanceof TitleScreen){
                if(!mc.gameDirectory.getCanonicalPath().endsWith("/build/blueprint-client/"+ROLE))throw new AssertionError("Refusing live game directory");
                Files.createDirectories(OUT);Files.createDirectories(COORD);mc.options.pauseOnLostFocus=false;mc.options.renderDistance().set(4);mc.options.fov().set(100);
                if(!HOST&&!Files.exists(COORD.resolve("listening.txt")))return;
                started=true;
                if(!HOST)connect(mc);
                else if(!RESUME.isEmpty()){
                    if(!RESUME.matches("blueprint-[A-Za-z0-9_.-]+")||!PREVIOUS.matches("[A-Za-z0-9_.-]+"))throw new AssertionError("Disposable native world required");
                    checkpoint=JSON.fromJson(Files.readString(ROOT.resolveSibling(PREVIOUS).resolve("host/checkpoint.json")),JsonObject.class);
                    mc.createWorldOpenFlows().loadLevel(new TitleScreen(),RESUME);
                }else{
                    var rules=new GameRules();rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false,null);rules.getRule(GameRules.RULE_DAYLIGHT).set(false,null);
                    mc.createWorldOpenFlows().createFreshLevel("blueprint-tomb-"+RUN+"-"+System.currentTimeMillis(),new LevelSettings("Disposable generated tomb combat",GameType.CREATIVE,false,net.minecraft.world.Difficulty.NORMAL,true,rules,WorldDataConfiguration.DEFAULT),new WorldOptions(57,false,false),registry->registry.registryOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.FLAT).createWorldDimensions().replaceOverworldGenerator(registry,terrain(registry)));
                }return;
            }
            if(!HOST&&disconnectPhase==1&&mc.level==null){camera=null;ready=false;frames=0;Files.writeString(COORD.resolve("peer-left.txt"),"Actual native client connection closed");disconnectPhase=2;connect(mc);return;}
            if(mc.level==null||mc.player==null)return;if(mc.screen!=null)mc.setScreen(null);
            if(HOST&&setup==null){setup=mc.getSingleplayerServer().submit(()->prepare(mc.getSingleplayerServer()));return;}
            if(HOST){
                if(!setup.isDone())return;setup.join();var server=mc.getSingleplayerServer();
                if(!listener){if(!SOLO&&!server.publishServer(GameType.CREATIVE,false,25587))throw new AssertionError("LAN publication failed");Files.writeString(COORD.resolve("listening.txt"),"native tomb");listener=true;}
                if(Files.exists(COORD.resolve("complete.txt"))&&(SOLO||Files.exists(ROOT.resolve("peer/PASS.txt")))){finish(mc,null);return;}
            }else if(Files.exists(COORD.resolve("complete.txt"))){finish(mc,null);return;}
            if(!Files.exists(COORD.resolve("view.json")))return;
            var view=JSON.fromJson(Files.readString(COORD.resolve("view.json")),JsonObject.class);var p=BlockPos.of(view.get("water").getAsLong());
            if(camera==null){camera=new ArmorStand(mc.level,p.getX()+4,p.getY()+.25,p.getZ());camera.setYRot(90);camera.setYHeadRot(90);camera.yHeadRotO=90;camera.setXRot(12);camera.setOldPosAndRot();mc.options.hideGui=true;mc.setCameraEntity(camera);}
            if(!mc.levelRenderer.isChunkCompiled(p)||mc.level.getBlockState(p.below()).isAir())return;
            if(++frames>=40&&!ready){ready=true;Files.writeString(COORD.resolve("ready-"+ROLE+".txt"),"Actual native floor/frame ready");}
            if(!RESUME.isEmpty()){
                float yaw=(mc.level.getGameTime()/10%4)*90;camera.setYRot(yaw);camera.setYHeadRot(yaw);camera.yHeadRotO=yaw;return;
            }
            if(Files.exists(COORD.resolve("reload.txt"))&&reload==null){reload=mc.reloadResourcePacks();return;}
            if(reload!=null&&reload.isDone()&&!Files.exists(COORD.resolve("reloaded-"+ROLE+".txt"))){reload.join();Files.writeString(COORD.resolve("reloaded-"+ROLE+".txt"),"Actual pack reload completed");}
            if(!HOST&&!SOLO&&disconnectPhase==0&&Files.exists(COORD.resolve("rejoin.txt"))){disconnectPhase=1;mc.level.disconnect();mc.clearLevel(new TitleScreen());return;}
            if(!HOST&&disconnectPhase==2&&ready&&!Files.exists(COORD.resolve("peer-rejoined.txt"))){disconnectPhase=3;Files.writeString(COORD.resolve("peer-rejoined.txt"),"Actual native TCP reconnect and rendered floor");}
        }catch(Throwable failure){finish(mc,failure);}
    }
    private static String disconnectReason(net.minecraft.client.gui.screens.Screen screen){
        String result=screen.getTitle().getString();
        for(var field:screen.getClass().getDeclaredFields())if(net.minecraft.network.chat.Component.class.isAssignableFrom(field.getType()))try{
            field.setAccessible(true);if(field.get(screen) instanceof net.minecraft.network.chat.Component text)result+=" | "+text.getString();
        }catch(ReflectiveOperationException ignored){}return result;
    }
    private static void connect(Minecraft mc){String address="127.0.0.1:25587";ConnectScreen.startConnecting(new TitleScreen(),mc,ServerAddress.parseString(address),new ServerData("Disposable generated tomb",address,false),false);}
    private static void prepare(MinecraftServer server){
        var world=server.overworld();world.setDayTime(18000);server.setUsesAuthentication(false);
        if(RESUME.isEmpty()){
            var registry=world.registryAccess();var structure=registry.registryOrThrow(Registries.STRUCTURE).get(new net.minecraft.resources.ResourceLocation("dynasty","imperial_tomb"));
            var generator=world.getChunkSource().getGenerator();var origin=new ChunkPos(0,0);
            var start=structure.generate(registry,generator,generator.getBiomeSource(),world.getChunkSource().randomState(),world.getStructureManager(),world.getSeed(),origin,0,world,b->true);
            if(!start.isValid())throw new AssertionError("Production tomb generator rejected native fixture");
            world.getChunk(0,0).setStartForStructure(structure,start);
            var tomb=start.getPieces().stream().filter(TombPiece.class::isInstance).map(TombPiece.class::cast).findFirst().orElseThrow();water=tomb.drownerPositions().get(0);entry=water.offset(5,-1,0);
            var box=start.getBoundingBox();
            for(int x=box.minX()>>4;x<=box.maxX()>>4;x++)for(int z=box.minZ()>>4;z<=box.maxZ()>>4;z++){
                var chunk=world.getChunk(x,z);chunk.addReferenceForStructure(structure,origin.toLong());var clip=new net.minecraft.world.level.levelgen.structure.BoundingBox(x*16,box.minY(),z*16,x*16+15,box.maxY(),z*16+15);
                for(var piece:start.getPieces())piece.postProcess(world,world.structureManager(),generator,net.minecraft.util.RandomSource.create(5),clip,chunk.getPos(),BlockPos.ZERO);
            }
            if(!world.getFluidState(water).is(net.minecraft.tags.FluidTags.WATER)||!world.getFluidState(water.below()).is(net.minecraft.tags.FluidTags.WATER))throw new AssertionError("Actual authored two-layer basin missing");
            world.getGameRules().getRule(GameRules.RULE_DOMOBSPAWNING).set(true,server);
        }else{water=BlockPos.of(checkpoint.get("water").getAsLong());entry=BlockPos.of(checkpoint.get("entry").getAsLong());}
        for(var player:server.getPlayerList().getPlayers()){player.teleportTo(world,entry.getX()+.5,entry.getY(),entry.getZ()+.5,180,0);player.setGameMode(player.getGameProfile().getName().equals("BlueprintHost")?GameType.SURVIVAL:GameType.CREATIVE);player.getAttribute(Attributes.MAX_HEALTH).setBaseValue(1000);player.setHealth(1000);player.setInvulnerable(false);}
        try{Files.writeString(COORD.resolve("view.json"),JSON.toJson(Map.of("water",water.asLong())));Files.writeString(OUT.resolve("world.txt"),world.getServer().getWorldData().getLevelName());}
        catch(Exception failure){throw new RuntimeException(failure);}
    }
    private static Map<String,Object> actor(TemplateMob mob){return Map.of("id",mob.blueprintId(),"uuid",mob.getUUID().toString(),"entityId",mob.getId(),"skill",mob.skillId(),"start",mob.skillStartTime(),"attack",mob.attack().save().toString(),"signal",mob.saveWithoutId(new CompoundTag()).getCompound("TombTacticalSignal").toString(),"position",mob.position().toString());}
    private static void discover(net.minecraft.server.level.ServerLevel world){
        ACTORS.clear();
        for(var suffix:List.of("tomb_drowner","shroud_child","paper_swordsmen")){
            var marker=BlueprintSpawnState.get(world).markers.get(SITE+":"+suffix);if(marker==null||marker.members.isEmpty())continue;
            for(var id:marker.members)if(world.getEntity(id) instanceof TemplateMob mob&&mob.isAlive()){
                if(mob.kind()==TemplateMob.Kind.PAPER&&mob.distanceToSqr(Vec3.atCenterOf(water))>10*10)continue;
                if(mob.isNoAi()||mob.isNoGravity()||!mob.encounterSite().equals(SITE))throw new AssertionError("Production member simulation/site lost");ACTORS.put(mob.kind(),mob);
            }
        }
    }
    @SubscribeEvent public static void server(TickEvent.ServerTickEvent e){
        if(!ENABLED||!HOST||done||water==null||e.phase!=TickEvent.Phase.END)return;
        var server=net.minecraftforge.server.ServerLifecycleHooks.getCurrentServer();var world=server.overworld();
        try{
            if(!Files.exists(COORD.resolve("ready-host.txt"))||!SOLO&&!Files.exists(COORD.resolve("ready-peer.txt")))return;
            if(begin<0)begin=world.getGameTime();long age=world.getGameTime()-begin;
            if(age>2400)throw new AssertionError("Ordinary tomb actors did not complete the finite flow");
            discover(world);if(ACTORS.size()!=3){
                if(age%20==0)Files.writeString(OUT.resolve("spawning-live.json"),JSON.toJson(Map.of("age",age,"actors",ACTORS.values().stream().map(TombCombatClientQa::actor).toList(),"markers",BlueprintSpawnState.get(world).markers.values().stream().filter(m->m.key.startsWith(SITE)).map(m->Map.of("key",m.key,"produced",m.produced,"members",m.members.stream().map(UUID::toString).toList(),"nextSpawn",m.nextSpawn)).toList(),"entrants",world.players().stream().map(p->p.position().toString()).toList())));
                return;
            }
            var host=world.players().stream().filter(p->p.getGameProfile().getName().equals("BlueprintHost")).findFirst().orElseThrow();
            var drowner=ACTORS.get(TemplateMob.Kind.DROWNER);var child=ACTORS.get(TemplateMob.Kind.CHILD);var paper=ACTORS.get(TemplateMob.Kind.PAPER);
            if(!RESUME.isEmpty()){
                Files.writeString(OUT.resolve("combat-live.json"),JSON.toJson(Map.of("sample",Map.of("tick",world.getGameTime(),"actors",ACTORS.values().stream().map(TombCombatClientQa::actor).toList()))));
                if(age<120)return;
                for(var saved:checkpoint.getAsJsonArray("actors")){
                    var row=saved.getAsJsonObject();var uuid=UUID.fromString(row.get("uuid").getAsString());
                    if(!(world.getEntity(uuid) instanceof TemplateMob mob))throw new AssertionError("Native restart lost member "+uuid);
                    if(!mob.encounterSite().equals(SITE))throw new AssertionError("Native restart changed authored site");
                    var old=TagParser.parseTag(row.get("attack").getAsString());var current=mob.attack().save();
                    for(var key:old.getCompound("Cooldowns").getAllKeys())if(current.getCompound("Cooldowns").getLong(key)<old.getCompound("Cooldowns").getLong(key))throw new AssertionError("Native restart reset cooldown");
                    if(world.getGameTime()>old.getLong("Started")+104&&mob.skillStartTime()==old.getLong("Started")&&mob.skillId()!=0)throw new AssertionError("Expired action survived native first ticks");
                }
                Files.writeString(OUT.resolve("combat-live.json"),JSON.toJson(Map.of("sample",Map.of("tick",world.getGameTime(),"actors",ACTORS.values().stream().map(TombCombatClientQa::actor).toList()))));
                Files.writeString(OUT.resolve("restart.json"),JSON.toJson(Map.of("actors",ACTORS.values().stream().map(TombCombatClientQa::actor).toList(),"tick",world.getGameTime(),"hostBound",host.hasEffect(BlueprintEntities.DROWNING_BIND.get()),"scope","Native process loads original generated world, same three UUIDs/site and non-reset cooldowns; expired control cannot remain permanent")));
                Files.writeString(COORD.resolve("complete.txt"),"native tomb restart");return;
            }
            if(!returned&&escapeAt<0&&host.position().distanceToSqr(Vec3.atCenterOf(water))>9)host.teleportTo(world,water.getX()+.5,water.getY(),water.getZ()+.5,180,0);
            var childSignal=child.saveWithoutId(new CompoundTag()).getCompound("TombTacticalSignal");
            var paperSignal=paper.saveWithoutId(new CompoundTag()).getCompound("TombTacticalSignal");
            boolean bind=host.hasEffect(BlueprintEntities.DROWNING_BIND.get());
            if(bind&&childSignal.hasUUID("Victim")&&childSignal.getUUID("Victim").equals(host.getUUID())&&paperSignal.hasUUID("Victim")&&paperSignal.getUUID("Victim").equals(host.getUUID())){
                if(!combat){combat=true;EVENTS.add(Map.of("event","actual_bind_handoff","tick",world.getGameTime(),"source",drowner.getUUID().toString(),"child",child.getUUID().toString(),"paper",paper.getUUID().toString(),"victim",host.getUUID().toString()));}
                if(child.skillId()==ArmySkills.CHILD_CURSE&&child.attack().target().equals(host.getUUID()))curseEpoch=childSignal.getLong("ActionStart");
                if(paper.skillId()==ArmySkills.PAPER_SLASH&&paper.attack().target().equals(host.getUUID()))slashEpoch=paperSignal.getLong("ActionStart");
                if(curseEpoch==slashEpoch&&curseEpoch==drowner.skillStartTime()&&!escape){
                    escape=true;escapeAt=world.getGameTime();EVENTS.add(Map.of("event","autonomous_curse_and_front_slash_same_pool_epoch","tick",escapeAt,"actors",ACTORS.values().stream().map(TombCombatClientQa::actor).toList(),"health",host.getHealth()));
                    host.teleportTo(world,entry.getX()+.5,entry.getY(),entry.getZ()+.5,0,0);
                }
            }
            if(escapeAt>=0&&!escaped&&world.getGameTime()-escapeAt>=120){
                if(host.hasEffect(BlueprintEntities.DROWNING_BIND.get())||host.hasEffect(BlueprintEntities.SOUL_BIND.get()))throw new AssertionError("Leaving the real basin leaves permanent control");
                escaped=true;EVENTS.add(Map.of("event","actual_escape_effects_expired","tick",world.getGameTime()));Files.writeString(COORD.resolve("reload.txt"),"native combat pack reload");
            }
            if(escaped&&!reloadObserved&&Files.exists(COORD.resolve("reloaded-host.txt"))&&(SOLO||Files.exists(COORD.resolve("reloaded-peer.txt")))){
                reloadObserved=true;EVENTS.add(Map.of("event","actual_resource_reload","tick",world.getGameTime()));
                if(SOLO)rejoined=true;else Files.writeString(COORD.resolve("rejoin.txt"),"actual peer reconnect");
            }
            if(!SOLO&&reloadObserved&&Files.exists(COORD.resolve("peer-left.txt"))&&Files.exists(COORD.resolve("peer-rejoined.txt"))&&world.players().size()==2){rejoined=true;}
            if(rejoined&&!returned){returned=true;host.teleportTo(world,water.getX()+.5,water.getY(),water.getZ()+.5,180,0);EVENTS.add(Map.of("event",SOLO?"solo_return":"actual_peer_return","tick",world.getGameTime()));}
            if(world.getGameTime()!=lastSample&&age%4==0){lastSample=world.getGameTime();SAMPLES.add(Map.of("tick",lastSample,"actors",ACTORS.values().stream().map(TombCombatClientQa::actor).toList(),"players",world.players().size(),"health",host.getHealth(),"bound",bind,"childLOS",child.hasLineOfSight(host),"paperLOS",paper.hasLineOfSight(host),"hostPosition",host.position().toString()));
                Files.writeString(OUT.resolve("combat-live.json"),JSON.toJson(Map.of("age",age,"combat",combat,"escape",escape,"escaped",escaped,"returned",returned,"sample",SAMPLES.get(SAMPLES.size()-1))));
            }
            if(SAMPLES.size()>610)throw new AssertionError("Finite combat sample budget exceeded");
            if(returned&&drowner.waterPool()&&bind&&drowner.actionAge(0)>=32){
                Files.writeString(OUT.resolve("combat.json"),JSON.toJson(Map.of("samples",SAMPLES,"events",EVENTS,"scope","Existing production tomb and ordinary AI: actual water control, same victim handoff, autonomous rear curse/front slash, escape, actual pack reload and peer reconnect where applicable")));
                Files.writeString(COORD.resolve("complete.txt"),"actual native tomb combat");
            }
        }catch(Throwable failure){try{Files.writeString(OUT.resolve("FAIL.txt"),"Server tomb acceptance failed: "+failure);}catch(Exception ignored){}throw new RuntimeException(failure);}
    }
    @SubscribeEvent public static void stopping(net.minecraftforge.event.server.ServerStoppingEvent e){
        if(!ENABLED||!HOST||water==null)return;
        try{Files.writeString(OUT.resolve("checkpoint.json"),JSON.toJson(Map.of("tick",e.getServer().overworld().getGameTime(),"water",water.asLong(),"entry",entry.asLong(),"actors",ACTORS.values().stream().map(TombCombatClientQa::actor).toList())));}catch(Exception failure){throw new RuntimeException(failure);}
    }
    @SubscribeEvent public static void render(TickEvent.RenderTickEvent e){
        if(!ENABLED||done||e.phase!=TickEvent.Phase.END||camera==null)return;var mc=Minecraft.getInstance();
        if(mc.level==null||mc.getOverlay()!=null||mc.level.getGameTime()==lastNativeSample)return;lastNativeSample=mc.level.getGameTime();
        try{
            var latest=OUT.getParent().resolve("host/combat-live.json");if(!Files.exists(latest))return;
            var row=JSON.fromJson(Files.readString(latest),JsonObject.class).getAsJsonObject("sample");
            if(Math.abs(mc.level.getGameTime()-row.get("tick").getAsLong())>40)return;
            for(var value:row.getAsJsonArray("actors")){
                var actor=value.getAsJsonObject();var entity=mc.level.getEntity(actor.get("entityId").getAsInt());
                if(!(entity instanceof TemplateMob mob)||!mob.getUUID().toString().equals(actor.get("uuid").getAsString()))continue;
                if(mc.getEntityRenderDispatcher().getRenderer(mob) instanceof software.bernie.geckolib.renderer.GeoEntityRenderer<?> renderer&&renderer.getGeoModel().getBone("root").isPresent())RENDERED.add(mob.blueprintId());
            }
        }catch(Throwable failure){finish(mc,failure);}
    }
    private static void finish(Minecraft mc,Throwable error){
        if(done)return;done=true;
        try{
            if(error==null){if(RENDERED.size()!=3)throw new AssertionError("Real rendered trio coverage missing: "+RENDERED);try(var frame=Screenshot.takeScreenshot(mc.getMainRenderTarget())){frame.writeToFile(OUT.resolve("tomb-combat-final.png"));}
                Files.writeString(OUT.resolve("PASS.txt"),"PASS: actual generated tomb trio rendered with normal AI, finite autonomous coordination, escape and native lifecycle observations. Scope is recorded in combat/restart JSON.\n");}
            else if(!Files.exists(OUT.resolve("FAIL.txt")))Files.writeString(OUT.resolve("FAIL.txt"),"FAIL: "+error);
        }catch(Throwable failure){failure.printStackTrace();try{Files.writeString(OUT.resolve("FAIL.txt"),"FAIL: "+failure);}catch(Exception ignored){}}
        mc.setCameraEntity(mc.player);mc.stop();
    }
}
