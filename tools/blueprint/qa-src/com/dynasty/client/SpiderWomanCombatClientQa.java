package com.dynasty.client;

import com.dynasty.blueprint.BlueprintSpawnState;
import com.dynasty.blueprint.combat.AttackState;
import com.dynasty.blueprint.elite.*;

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
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.CompletableFuture;

/** Finite native lifecycle acceptance, compiled only by the existing optional blueprint QA source set. */
@Mod.EventBusSubscriber(modid="dynasty",value=Dist.CLIENT)
public final class SpiderWomanCombatClientQa {
    private static final boolean ENABLED=Boolean.getBoolean("dynasty.blueprintQa.spiderWomanCombat");
    private static final String ROLE=System.getProperty("dynasty.blueprintQa","");
    private static final boolean HOST=ROLE.equals("host"),SOLO=Boolean.getBoolean("dynasty.blueprintQa.solo");
    private static final String RUN=System.getProperty("dynasty.blueprintQa.run","");
    private static final String RESUME=System.getProperty("dynasty.blueprintQa.resumeWorld",""),PREVIOUS=System.getProperty("dynasty.blueprintQa.previousRun","");
    private static final Path ROOT=Path.of(System.getProperty("dynasty.blueprintQa.output","build/blueprint-client/results")),OUT=ROOT.resolve(ROLE),COORD=ROOT.resolve("coord");
    private static final Gson JSON=new GsonBuilder().setPrettyPrinting().create();
    private static final String SITE="minecraft:overworld/dynasty:tiangong_mining_estate@0:spider_woman";
    private static final long DEADLINE=System.nanoTime()+900_000_000_000L;
    private static final Set<Integer> RELEASED=new HashSet<>();
    private static final List<Map<String,Object>> SAMPLES=new ArrayList<>(),EVENTS=new ArrayList<>();
    private static JsonObject checkpoint;
    private static SpiderWoman mob;
    private static BlockPos feet;
    private static ArmorStand camera;
    private static CompletableFuture<Void> setup,reload;
    private static boolean started,done,listener,ready,rendered,reloadObserved,rejoinRequested,rejoined,firstTick,isolated,ceilingSeen,landingSeen,eggBroken;
    private static long begin=-1,lastSample=-1;
    private static int frames,disconnectPhase;
    private static UUID pendingEgg;
    private static long eggArmed=-1;
    private static float previousHealth=1000;

    private static FlatLevelSource terrain(RegistryAccess registry){
        var settings=FlatLevelGeneratorSettings.getDefault(registry.lookupOrThrow(Registries.BIOME),registry.lookupOrThrow(Registries.STRUCTURE_SET),registry.lookupOrThrow(Registries.PLACED_FEATURE));
        settings.getLayersInfo().clear();settings.getLayersInfo().add(new FlatLayerInfo(127,Blocks.STONE));settings.getLayersInfo().add(new FlatLayerInfo(1,Blocks.GRASS_BLOCK));settings.updateLayers();return new FlatLevelSource(settings);
    }
    @SubscribeEvent public static void client(TickEvent.ClientTickEvent e){
        if(!ENABLED||ROLE.isBlank()||done||e.phase!=TickEvent.Phase.END)return;
        var mc=Minecraft.getInstance();
        try{
            if(System.nanoTime()>DEADLINE)throw new AssertionError("Finite spider-woman lifecycle timed out");
            if(Files.exists(ROOT.resolve(HOST?"peer/FAIL.txt":"host/FAIL.txt")))throw new AssertionError("Other native client failed");
            if(started&&disconnectPhase==0&&mc.screen instanceof DisconnectedScreen)throw new AssertionError("Native login disconnected: "+disconnectReason(mc.screen));
            if(HOST&&started&&!RESUME.isEmpty()&&mc.screen instanceof ConfirmScreen confirm&&confirm.getTitle().getContents() instanceof net.minecraft.network.chat.contents.TranslatableContents title&&title.getKey().equals("selectWorld.backupQuestion.experimental")){
                for(var child:confirm.children())if(child instanceof net.minecraft.client.gui.components.Button button&&button.getMessage().equals(net.minecraft.network.chat.CommonComponents.GUI_PROCEED)){button.onPress();return;}
                throw new AssertionError("Disposable world lacks native Proceed action");
            }
            if(mc.getOverlay()!=null)return;
            if(mc.screen instanceof AccessibilityOnboardingScreen)mc.setScreen(new TitleScreen());
            if(!started&&mc.screen instanceof TitleScreen){
                if(!mc.gameDirectory.getCanonicalPath().endsWith("/build/blueprint-client/"+ROLE))throw new AssertionError("Refusing live game directory");
                Files.createDirectories(OUT);Files.createDirectories(COORD);mc.options.pauseOnLostFocus=false;mc.options.renderDistance().set(4);mc.options.fov().set(80);
                if(!HOST&&!Files.exists(COORD.resolve("listening.txt")))return;
                started=true;
                if(!HOST)connect(mc);
                else if(!RESUME.isEmpty()){
                    if(!RESUME.matches("blueprint-[A-Za-z0-9_.-]+")||!PREVIOUS.matches("[A-Za-z0-9_.-]+"))throw new AssertionError("Owned disposable world required");
                    checkpoint=JSON.fromJson(Files.readString(ROOT.resolveSibling(PREVIOUS).resolve("host/checkpoint.json")),JsonObject.class);
                    mc.createWorldOpenFlows().loadLevel(new TitleScreen(),RESUME);
                }else{
                    var rules=new GameRules();rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false,null);rules.getRule(GameRules.RULE_DAYLIGHT).set(false,null);
                    mc.createWorldOpenFlows().createFreshLevel("blueprint-spider-woman-"+RUN+"-"+System.currentTimeMillis(),new LevelSettings("Disposable production spider-woman lifecycle",GameType.CREATIVE,false,net.minecraft.world.Difficulty.NORMAL,true,rules,WorldDataConfiguration.DEFAULT),new WorldOptions(57,false,false),registry->registry.registryOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.FLAT).createWorldDimensions().replaceOverworldGenerator(registry,terrain(registry)));
                }return;
            }
            if(!HOST&&disconnectPhase==1&&mc.level==null){camera=null;frames=0;ready=false;Files.writeString(COORD.resolve("peer-left.txt"),"Actual TCP client closed");disconnectPhase=2;connect(mc);return;}
            if(mc.level==null||mc.player==null)return;if(mc.screen!=null)mc.setScreen(null);
            if(HOST&&setup==null){setup=mc.getSingleplayerServer().submit(()->prepare(mc.getSingleplayerServer()));return;}
            if(HOST){
                if(!setup.isDone())return;setup.join();var server=mc.getSingleplayerServer();
                if(!listener){if(!SOLO&&!server.publishServer(GameType.CREATIVE,false,25587))throw new AssertionError("Native LAN publication failed");Files.writeString(COORD.resolve("listening.txt"),RUN);listener=true;}
                if(Files.exists(COORD.resolve("complete.txt"))&&(SOLO||Files.exists(ROOT.resolve("peer/PASS.txt")))){finish(mc,null);return;}
            }else if(Files.exists(COORD.resolve("complete.txt"))){finish(mc,null);return;}
            if(!Files.exists(COORD.resolve("view.json")))return;
            var view=JSON.fromJson(Files.readString(COORD.resolve("view.json")),JsonObject.class);var p=BlockPos.of(view.get("feet").getAsLong());
            if(camera==null){camera=new ArmorStand(mc.level,p.getX()+.5,p.getY()+.4,p.getZ()-6);camera.setYRot(0);camera.setYHeadRot(0);camera.yHeadRotO=0;camera.setXRot(6);camera.setOldPosAndRot();mc.options.hideGui=true;mc.setCameraEntity(camera);}
            if(!mc.levelRenderer.isChunkCompiled(p)||mc.level.getBlockState(p.below(3)).isAir())return;
            if(++frames>=40&&!ready){ready=true;Files.writeString(COORD.resolve("ready-"+ROLE+".txt"),"Actual native floor ready");}
            var liveFile=ROOT.resolve("host/combat-live.json");
            if(Files.exists(liveFile)){
                var live=JSON.fromJson(Files.readString(liveFile),JsonObject.class).getAsJsonObject("actor");
                var parts=live.get("position").getAsString().replace("(","").replace(")","").split(",");
                camera.moveTo(Double.parseDouble(parts[0]),Double.parseDouble(parts[1])+1,Double.parseDouble(parts[2])-9,0,4);camera.setOldPosAndRot();
            }
            if(!RESUME.isEmpty())return;
            if(Files.exists(COORD.resolve("reload.txt"))&&reload==null){reload=mc.reloadResourcePacks();return;}
            if(reload!=null&&reload.isDone()&&!Files.exists(COORD.resolve("reloaded-"+ROLE+".txt"))){reload.join();Files.writeString(COORD.resolve("reloaded-"+ROLE+".txt"),"Actual pack reload completed");}
            if(!HOST&&!SOLO&&disconnectPhase==0&&Files.exists(COORD.resolve("rejoin.txt"))){disconnectPhase=1;mc.level.disconnect();mc.clearLevel(new TitleScreen());return;}
            if(!HOST&&disconnectPhase==2&&ready&&!Files.exists(COORD.resolve("peer-rejoined.txt"))){disconnectPhase=3;Files.writeString(COORD.resolve("peer-rejoined.txt"),"Actual TCP reconnection and rendered native floor");}
        }catch(Throwable failure){finish(mc,failure);}
    }
    private static void publishJson(Path file,Object value)throws java.io.IOException{
        var next=file.resolveSibling(file.getFileName()+".next");Files.writeString(next,JSON.toJson(value));
        Files.move(next,file,StandardCopyOption.REPLACE_EXISTING,StandardCopyOption.ATOMIC_MOVE);
    }
    private static String disconnectReason(net.minecraft.client.gui.screens.Screen screen){
        String result=screen.getTitle().getString();
        for(var field:screen.getClass().getDeclaredFields())if(net.minecraft.network.chat.Component.class.isAssignableFrom(field.getType()))try{
            field.setAccessible(true);if(field.get(screen) instanceof net.minecraft.network.chat.Component text)result+=" | "+text.getString();
        }catch(ReflectiveOperationException ignored){}return result;
    }
    private static void connect(Minecraft mc){String address="127.0.0.1:25587";ConnectScreen.startConnecting(new TitleScreen(),mc,ServerAddress.parseString(address),new ServerData("Disposable production spider-woman",address,false),false);}
    private static void prepare(MinecraftServer server){
        var world=server.overworld();world.setDayTime(18000);server.setUsesAuthentication(false);
        if(RESUME.isEmpty()){
            var registry=world.registryAccess();var structure=registry.registryOrThrow(Registries.STRUCTURE).get(new net.minecraft.resources.ResourceLocation("dynasty","tiangong_mining_estate"));var generator=world.getChunkSource().getGenerator();var origin=new ChunkPos(0,0);
            var start=structure.generate(registry,generator,generator.getBiomeSource(),world.getChunkSource().randomState(),world.getStructureManager(),world.getSeed(),origin,0,world,b->true);
            if(!start.isValid())throw new AssertionError("Actual production structure invalid");world.getChunk(0,0).setStartForStructure(structure,start);
            feet=start.getPieces().stream().flatMap(piece->com.dynasty.structure.megabuild.MechanicalPatrols.spiderWomanPositions(piece).stream()).findFirst().orElseThrow();
            for(int x=(feet.getX()-16)>>4;x<=(feet.getX()+16)>>4;x++)for(int z=(feet.getZ()-16)>>4;z<=(feet.getZ()+16)>>4;z++){
                var chunk=world.getChunk(x,z);chunk.addReferenceForStructure(structure,origin.toLong());var b=start.getBoundingBox();var clip=new net.minecraft.world.level.levelgen.structure.BoundingBox(x*16,b.minY(),z*16,x*16+15,b.maxY(),z*16+15);
                for(var p:start.getPieces())p.postProcess(world,world.structureManager(),generator,net.minecraft.util.RandomSource.create(3),clip,chunk.getPos(),BlockPos.ZERO);
            }
            world.getGameRules().getRule(GameRules.RULE_DOMOBSPAWNING).set(true,server);
        }else feet=BlockPos.of(checkpoint.get("feet").getAsLong());
        for(var player:world.players()){player.teleportTo(world,feet.getX()+.5,feet.getY()-2,feet.getZ()-8.5,0,0);player.setGameMode(player.getGameProfile().getName().equals("BlueprintHost")?GameType.SURVIVAL:GameType.CREATIVE);player.getAttribute(Attributes.MAX_HEALTH).setBaseValue(1000);player.setHealth(1000);player.setInvulnerable(false);}
        try{Files.writeString(COORD.resolve("view.json"),JSON.toJson(Map.of("feet",feet.asLong())));}catch(Exception failure){throw new RuntimeException(failure);}
    }
    @SubscribeEvent public static void joined(net.minecraftforge.event.entity.player.PlayerEvent.PlayerLoggedInEvent event){
        if(!ENABLED||!HOST||feet==null||!(event.getEntity() instanceof net.minecraft.server.level.ServerPlayer player)
            ||!player.getGameProfile().getName().equals("BlueprintPeer"))return;
        // A detached render camera does not change the real server entity-tracking centre.
        // Keep the native observer in range on both initial login and actual reconnection.
        player.teleportTo(player.server.overworld(),feet.getX()+.5,feet.getY()-2,feet.getZ()-8.5,0,0);
        player.setGameMode(GameType.CREATIVE);
    }
    private static Map<String,Object> state(SpiderWoman m){return Map.of("uuid",m.getUUID().toString(),"entityId",m.getId(),"site",m.encounterSite(),"position",m.position().toString(),"attack",m.attack().save().toString(),"skill",m.skillId(),"start",m.skillStart(),"phase",m.phase().name());}
    private static java.util.List<Map<String,Object>> summons(net.minecraft.server.level.ServerLevel world,SpiderWoman m){return world.getEntitiesOfClass(Entity.class,m.getBoundingBox().inflate(32),e->e instanceof SpiderBrood b&&b.ownedBy(m)||e instanceof com.dynasty.blueprint.SkullBloodPool p&&p.ownedBy(m)).stream().map(e->Map.<String,Object>of("uuid",e.getUUID().toString(),"id",e.getType().toString(),"nbt",e.saveWithoutId(new CompoundTag()).toString())).toList();}
    private static net.minecraft.world.phys.Vec3 nativeStand(net.minecraft.server.level.ServerLevel world,net.minecraft.server.level.ServerPlayer player,net.minecraft.world.phys.Vec3 centre,double distance){
        for(int n=0;n<32;n++){double angle=n*Math.PI/16;var point=new net.minecraft.world.phys.Vec3(centre.x+Math.sin(angle)*distance,feet.getY()-2,centre.z+Math.cos(angle)*distance);var floor=BlockPos.containing(point).below();
            if(!world.hasChunkAt(floor)||!world.getBlockState(floor).isFaceSturdy(world,floor,Direction.UP)||!world.noCollision(player,player.getDimensions(player.getPose()).makeBoundingBox(point)))continue;
            if(world.clip(new net.minecraft.world.level.ClipContext(centre.add(0,.3,0),point.add(0,player.getEyeHeight(),0),net.minecraft.world.level.ClipContext.Block.COLLIDER,net.minecraft.world.level.ClipContext.Fluid.NONE,mob)).getType()==net.minecraft.world.phys.HitResult.Type.MISS)return point;
        }return null;
    }
    @SubscribeEvent public static void first(net.minecraftforge.event.entity.living.LivingEvent.LivingTickEvent e){
        if(!ENABLED||!HOST||RESUME.isEmpty()||firstTick||checkpoint==null||!(e.getEntity() instanceof SpiderWoman m)||m.level().isClientSide||!m.getUUID().toString().equals(checkpoint.getAsJsonObject("actor").get("uuid").getAsString()))return;
        firstTick=true;try{
            var previous=TagParser.parseTag(checkpoint.getAsJsonObject("actor").get("attack").getAsString());var current=m.attack().save();
            for(var key:previous.getCompound("Cooldowns").getAllKeys())if(current.getCompound("Cooldowns").getLong(key)<previous.getCompound("Cooldowns").getLong(key))throw new AssertionError("First native tick reset cooldown");
            if(previous.getInt("Skill")!=0&&m.level().getGameTime()-previous.getLong("Started")<SpiderWoman.skill(previous.getInt("Skill")).totalTicks()&&(!Arrays.equals(previous.getIntArray("Fired"),current.getIntArray("Fired"))||previous.getLong("Started")!=current.getLong("Started")))throw new AssertionError("Unexpired consumed action identity changed on first native tick");
            Files.createDirectories(OUT);Files.writeString(OUT.resolve("first-native-tick.json"),JSON.toJson(Map.of("tick",m.level().getGameTime(),"actor",state(m),"previous",previous.toString())));
        }catch(Throwable failure){throw new RuntimeException(failure);}
    }
    @SubscribeEvent public static void server(TickEvent.ServerTickEvent e){
        if(!ENABLED||!HOST||done||feet==null||e.phase!=TickEvent.Phase.END)return;var server=net.minecraftforge.server.ServerLifecycleHooks.getCurrentServer();var world=server.overworld();
        try{
            if(Files.exists(COORD.resolve("complete.txt")))return;
            if(!Files.exists(COORD.resolve("ready-host.txt"))||!SOLO&&!Files.exists(COORD.resolve("ready-peer.txt")))return;
            if(begin<0)begin=world.getGameTime();long age=world.getGameTime()-begin;if(age>2400)throw new AssertionError("Normal autonomous spider-woman did not finish finite acceptance: released="+RELEASED+" actor="+(mob==null?"null":state(mob)));
            if(mob==null){var marker=BlueprintSpawnState.get(world).markers.get(SITE);if(marker==null||marker.members.size()!=1)return;var member=world.getEntity(marker.members.iterator().next());if(!(member instanceof SpiderWoman m))return;mob=m;}
            if(!mob.isAlive()||mob.isNoAi()||!mob.encounterSite().equals(SITE))throw new AssertionError("Production identity or normal simulation lost: "+state(mob));
            var host=world.players().stream().filter(p->p.getGameProfile().getName().equals("BlueprintHost")).findFirst().orElseThrow();
            if(!isolated){
                var others=world.getEntitiesOfClass(net.minecraft.world.entity.Mob.class,mob.getBoundingBox().inflate(48),actor->!(actor instanceof SpiderWoman)&&!(actor instanceof SpiderBrood));others.forEach(Entity::discard);
                world.getGameRules().getRule(GameRules.RULE_DOMOBSPAWNING).set(false,server);isolated=true;
                EVENTS.add(Map.of("event","isolated_registered_actor_after_ordinary_structure_spawn","removedOtherActors",others.size(),"tick",world.getGameTime()));
            }
            ceilingSeen|=mob.attachedToCeiling()&&mob.isNoGravity();
            if(Math.abs(host.distanceTo(mob)-3.2)>1.2||!mob.hasLineOfSight(host)){
                var safe=nativeStand(world,host,mob.position(),3);if(safe!=null)host.teleportTo(world,safe.x,safe.y,safe.z,180,0);
            }
            if(host.getHealth()<previousHealth&&mob.skillId()==372&&mob.onGround())landingSeen=true;previousHealth=host.getHealth();
            long now=world.getGameTime();var attack=mob.attack().save();if(attack.getIntArray("Fired").length>0)RELEASED.add(mob.skillId());
            if(now!=lastSample&&age%4==0){lastSample=now;SAMPLES.add(Map.of("tick",now,"actor",state(mob),"hostHealth",host.getHealth(),"players",world.players().size()));publishJson(OUT.resolve("combat-live.json"),SAMPLES.get(SAMPLES.size()-1));}
            if(!RESUME.isEmpty()){
                if(age<300)return;if(!firstTick)throw new AssertionError("No first native entity tick observed");
                if(!mob.getUUID().toString().equals(checkpoint.getAsJsonObject("actor").get("uuid").getAsString()))throw new AssertionError("Native restart changed UUID");
                var marker=BlueprintSpawnState.get(world).markers.get(SITE);if(marker==null||marker.produced!=1||!marker.members.contains(mob.getUUID()))throw new AssertionError("Restart lost the actual structure ledger");
                for(var previous:checkpoint.getAsJsonArray("summons")){var id=UUID.fromString(previous.getAsJsonObject().get("uuid").getAsString());if(world.getEntity(id)!=null)throw new AssertionError("Original acid or brood survived its absolute expiry");}
                Files.writeString(OUT.resolve("restart.json"),JSON.toJson(Map.of("samples",SAMPLES,"scope","Actual original save and native process: first entity tick preserves consumed frame and cooldown, same UUID/site; encounter ledger persists without duplicating the consumed action")));Files.writeString(COORD.resolve("complete.txt"),RUN);return;
            }
            if(RELEASED.containsAll(List.of(371,372,373))&&!reloadObserved){Files.writeString(COORD.resolve("reload.txt"),RUN);if(Files.exists(COORD.resolve("reloaded-host.txt"))&&(SOLO||Files.exists(COORD.resolve("reloaded-peer.txt")))){reloadObserved=true;EVENTS.add(Map.of("event","actual_resource_reload","tick",now,"actor",state(mob)));if(SOLO)rejoined=true;} }
            if(reloadObserved&&!SOLO&&!rejoinRequested&&mob.phase()==AttackState.WINDUP){rejoinRequested=true;Files.writeString(COORD.resolve("rejoin.txt"),RUN);EVENTS.add(Map.of("event","peer_disconnect_during_autonomous_windup","tick",now,"actor",state(mob)));}
            if(rejoinRequested&&!rejoined&&Files.exists(COORD.resolve("peer-left.txt"))&&Files.exists(COORD.resolve("peer-rejoined.txt"))&&world.players().size()==2){rejoined=true;EVENTS.add(Map.of("event","actual_peer_reconnected","tick",now,"actor",state(mob)));}
            var brood=world.getEntitiesOfClass(SpiderBrood.class,mob.getBoundingBox().inflate(32),b->b.ownedBy(mob));
            var pools=world.getEntitiesOfClass(com.dynasty.blueprint.SkullBloodPool.class,mob.getBoundingBox().inflate(32),p->p.ownedBy(mob));
            if(brood.size()>3||pools.size()>6)throw new AssertionError("Native acid/brood ownership budget exceeded");
            if(!eggBroken&&RELEASED.containsAll(List.of(371,372,373))){
                if(pendingEgg==null){var egg=brood.stream().filter(b->!b.hatched()&&b.isAlive()).findFirst().orElse(null);if(egg!=null){pendingEgg=egg.getUUID();eggArmed=now;host.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND,new net.minecraft.world.item.ItemStack(com.dynasty.DynastyGear.SWORD_BRONZE.get()));host.resetAttackStrengthTicker();}}
                if(pendingEgg!=null&&now-eggArmed>=24){var entity=world.getEntity(pendingEgg);if(entity instanceof SpiderBrood egg&&!egg.hatched()){
                    var safe=nativeStand(world,host,egg.position(),1.5);if(safe!=null){host.teleportTo(world,safe.x,safe.y,safe.z,180,0);host.attack(egg);if(!egg.isRemoved()||egg.hatched())throw new AssertionError("Actual charged bronze-player attack did not break the native unhatched egg");eggBroken=true;EVENTS.add(Map.of("event","actual_bronze_player_broke_ordinary_egg","tick",now,"egg",pendingEgg.toString()));}
                }else{pendingEgg=null;eggArmed=-1;}}
            }
            if(rejoined&&ceilingSeen&&landingSeen&&eggBroken&&mob.skillId()==371&&attack.getIntArray("Fired").length>0&&!pools.isEmpty()){
                Files.writeString(OUT.resolve("combat.json"),JSON.toJson(Map.of("samples",SAMPLES,"events",EVENTS,"released",RELEASED,"scope","Actual mining-estate generator and ordinary climbing AI, all three autonomous releases, real landing contact and actual charged bronze-player egg destruction, pack reload and actual TCP disconnect/reconnect where applicable; checkpoint during a consumed attack")));Files.writeString(COORD.resolve("complete.txt"),RUN);
            }
        }catch(Throwable failure){try{Files.writeString(OUT.resolve("failed-samples.json"),JSON.toJson(Map.of("samples",SAMPLES,"released",RELEASED,"events",EVENTS)));Files.writeString(OUT.resolve("FAIL.txt"),"Server lifecycle acceptance failed: "+failure);}catch(Exception ignored){}throw new RuntimeException(failure);}
    }
    @SubscribeEvent public static void stopping(net.minecraftforge.event.server.ServerStoppingEvent e){
        if(!ENABLED||!HOST||mob==null)return;try{Files.writeString(OUT.resolve("checkpoint.json"),JSON.toJson(Map.of("tick",e.getServer().overworld().getGameTime(),"feet",feet.asLong(),"actor",state(mob),"summons",summons(e.getServer().overworld(),mob))));}catch(Exception failure){throw new RuntimeException(failure);}
    }
    @SubscribeEvent public static void render(TickEvent.RenderTickEvent e){
        if(!ENABLED||done||e.phase!=TickEvent.Phase.END||camera==null)return;var mc=Minecraft.getInstance();if(mc.level==null||mc.getOverlay()!=null)return;
        try{var file=ROOT.resolve("host/combat-live.json");if(!Files.exists(file))return;var state=JSON.fromJson(Files.readString(file),JsonObject.class).getAsJsonObject("actor");
            if(mc.level.getEntity(state.get("entityId").getAsInt()) instanceof SpiderWoman current&&current.getUUID().toString().equals(state.get("uuid").getAsString())&&mc.getEntityRenderDispatcher().getRenderer(current) instanceof software.bernie.geckolib.renderer.GeoEntityRenderer<?> r&&r.getGeoModel().getBone("root").isPresent()){rendered=true;Files.writeString(OUT.resolve("observed-native.json"),JSON.toJson(Map.of("actor",state,"tick",mc.level.getGameTime(),"players",mc.level.players().size())));}
        }catch(Throwable failure){finish(mc,failure);}
    }
    private static void finish(Minecraft mc,Throwable failure){
        if(done)return;done=true;try{if(failure==null){if(!rendered)throw new AssertionError("Native spider-woman renderer never observed");try(var frame=Screenshot.takeScreenshot(mc.getMainRenderTarget())){frame.writeToFile(OUT.resolve("combat-final.png"));}Files.writeString(OUT.resolve("PASS.txt"),"PASS: actual production spider-woman native lifecycle; detailed finite scope in combat/restart and first-native-tick JSON.\n");}else if(!Files.exists(OUT.resolve("FAIL.txt")))Files.writeString(OUT.resolve("FAIL.txt"),"FAIL: "+failure);
        }catch(Throwable error){try{Files.writeString(OUT.resolve("FAIL.txt"),"FAIL: "+error);}catch(Exception ignored){}}mc.setCameraEntity(mc.player);mc.stop();
    }
}
