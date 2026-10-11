package com.dynasty.client;

import com.dynasty.blueprint.SkullBloodPool;
import com.dynasty.blueprint.elite.*;
import com.dynasty.blueprint.elite.client.HammerGuardianRenderer;
import com.google.gson.*;
import com.mojang.blaze3d.platform.NativeImage;
import net.minecraft.client.*;
import net.minecraft.client.gui.screens.*;
import net.minecraft.client.multiplayer.ServerData;
import net.minecraft.client.multiplayer.resolver.ServerAddress;
import net.minecraft.core.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.Difficulty;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.decoration.ArmorStand;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.levelgen.*;
import net.minecraft.world.level.levelgen.presets.WorldPresets;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.CompletableFuture;

/** Optional native-client slice of the existing blueprint QA source set, absent from the mod JAR. */
@Mod.EventBusSubscriber(modid="dynasty",value=Dist.CLIENT)
public final class HammerGuardianClientQa {
    private static final boolean ENABLED=Boolean.getBoolean("dynasty.blueprintQa.hammer");
    private static final String ROLE=System.getProperty("dynasty.blueprintQa","");
    private static final boolean HOST=ROLE.equals("host"),SOLO=Boolean.getBoolean("dynasty.blueprintQa.solo");
    private static final String RUN=System.getProperty("dynasty.blueprintQa.run","unset");
    private static final Path ROOT=Path.of(System.getProperty("dynasty.blueprintQa.output","build/blueprint-client/results"));
    private static final Path OUT=ROOT.resolve(ROLE),COORD=ROOT.resolve("coord");
    private static final Gson JSON=new GsonBuilder().setPrettyPrinting().create();
    private static final String[] NAMES={"front","side","45","back","walk","slam-tell","slam-impact","wheel-tell","wheel-active","throw-tell","throw-release","hurt","death-kneeling","death-collapse","production-tomb-entry"};
    private static final int[] SKILLS={0,0,0,0,0,361,361,362,362,363,363,0,0,0,0};
    private static final int[] AGES={0,0,0,0,1,22,29,14,36,30,39,2,32,65,0};
    private record Stage(int index,String phase,int entityId,String uuid,int skill,long start,long published){}
    private static final List<String> LOG=new ArrayList<>();
    private static final long DEADLINE=System.nanoTime()+600_000_000_000L;
    private static boolean started,done,captured,ready,listener;
    private static int index=-1,observed=-1,settled;
    private static Stage local;
    private static CompletableFuture<Stage> pending;
    private static CompletableFuture<Void> setup;
    private static HammerGuardian fixture;
    private static LivingEntity victim;
    private static ArmorStand camera;

    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent event){
        if(!ENABLED||ROLE.isBlank()||done||event.phase!=TickEvent.Phase.END)return;
        var mc=Minecraft.getInstance();
        try{
            if(System.nanoTime()>DEADLINE)throw new AssertionError("Elite QA timed out");
            if(Files.exists(ROOT.resolve(HOST?"peer/FAIL.txt":"host/FAIL.txt")))throw new AssertionError("Other client failed");
            if(mc.getOverlay()!=null)return;
            if(started&&mc.screen instanceof DisconnectedScreen)throw new AssertionError("Real peer disconnected before acceptance: "+disconnectReason(mc.screen));
            if(mc.screen instanceof AccessibilityOnboardingScreen)mc.setScreen(new TitleScreen());
            if(!started&&mc.screen instanceof TitleScreen){
                if(!mc.gameDirectory.getCanonicalPath().endsWith("/build/blueprint-client/"+ROLE))throw new AssertionError("Refusing live game directory");
                if(Files.exists(OUT.resolve("PASS.txt"))||Files.exists(OUT.resolve("FAIL.txt")))throw new AssertionError("Run already used");
                Files.createDirectories(OUT);Files.createDirectories(COORD);mc.options.pauseOnLostFocus=false;mc.options.renderDistance().set(4);mc.options.fov().set(65);
                if(!HOST&&!Files.exists(COORD.resolve("listening.txt")))return;started=true;
                if(!HOST){String address="127.0.0.1:25587";ConnectScreen.startConnecting(new TitleScreen(),mc,ServerAddress.parseString(address),new ServerData("Disposable elite QA",address,false),false);}
                else{
                    var rules=new GameRules();rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false,null);rules.getRule(GameRules.RULE_DAYLIGHT).set(false,null);
                    mc.createWorldOpenFlows().createFreshLevel("blueprint-"+RUN+"-"+System.currentTimeMillis(),
                        new LevelSettings("Disposable elite QA",GameType.CREATIVE,false,Difficulty.NORMAL,true,rules,WorldDataConfiguration.DEFAULT),
                        new WorldOptions(57,false,false),registry->registry.registryOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.FLAT).createWorldDimensions());
                }return;
            }
            if(mc.level==null||mc.player==null)return;if(mc.screen!=null)mc.setScreen(null);
            if(HOST&&setup==null){var server=mc.getSingleplayerServer();setup=server.submit(()->{
                var world=server.overworld();world.setDayTime(6000);
                for(int x=-16;x<=16;x++)for(int z=-16;z<=16;z++)world.setBlockAndUpdate(new BlockPos(x,-61,z),Blocks.STONE.defaultBlockState());
                if(!SOLO)server.setUsesAuthentication(false);
            });return;}
            if(HOST){
                if(!setup.isDone())return;setup.join();
                var server=mc.getSingleplayerServer();
                if(!listener){if(!SOLO&&!server.publishServer(GameType.CREATIVE,false,25587))throw new AssertionError("Native disposable LAN publication failed");Files.writeString(COORD.resolve("listening.txt"),RUN);listener=true;}
                if(Files.exists(COORD.resolve("complete.txt"))&&(SOLO||Files.exists(ROOT.resolve("peer/PASS.txt")))){finish(mc,null);return;}
                if(!SOLO&&server.getPlayerList().getPlayerCount()<2)return;
                if(pending!=null){if(!pending.isDone())return;local=pending.join();pending=null;publish(local);}
                if(index<0){index=0;pending=server.submit(()->prepare(server,index));return;}
                if(index>=14&&local!=null&&local.phase.equals("SPAWNING")){pending=server.submit(()->pollEntry(server,index));return;}
                if(local!=null&&local.phase.equals("READY")&&index>=4&&both("ready",index)){pending=server.submit(()->activate(server,index));return;}
                if(both("captured",index)){
                    if(index==NAMES.length-1){Files.writeString(COORD.resolve("complete.txt"),RUN);if(SOLO||Files.exists(ROOT.resolve("peer/PASS.txt")))finish(mc,null);}
                    else{index++;pending=server.submit(()->prepare(server,index));}return;
                }
            }else if(Files.exists(COORD.resolve("complete.txt"))){finish(mc,null);return;}
            if(!Files.exists(COORD.resolve("elite-stage.json")))return;
            var state=JSON.fromJson(Files.readString(COORD.resolve("elite-stage.json")),Stage.class);
            if(state.index!=observed){observed=state.index;settled=0;ready=false;captured=false;camera=null;}
            local=state;
            if(state.phase.equals("SPAWNING"))return;
            if(!(mc.level.getEntity(state.entityId) instanceof HammerGuardian elite)||!elite.getUUID().toString().equals(state.uuid))return;
            if(!SOLO&&mc.level.players().size()!=2)return;
            if(camera==null){
                mc.options.hideGui=true;mc.options.setCameraType(CameraType.FIRST_PERSON);
                var offset=observed>=14?new net.minecraft.world.phys.Vec3(0,1.7,-6):new net.minecraft.world.phys.Vec3(observed==1?10:observed==2?7:0,1.8,observed==1?0:observed==2?7:observed==3?-10:10);
                camera=new ArmorStand(mc.level,elite.getX()+offset.x,elite.getY()+offset.y,elite.getZ()+offset.z);
                camera.setNoGravity(true);camera.setYRot(observed>=14?0:observed==1?90:observed==2?135:observed==3?0:180);camera.setXRot(4);
                camera.setYHeadRot(camera.getYRot());camera.yHeadRotO=camera.getYRot();camera.setOldPosAndRot();mc.setCameraEntity(camera);
            }
            var floor=observed>=14?elite.blockPosition().below():new BlockPos(0,-61,0);
            if(!mc.levelRenderer.isChunkCompiled(floor)||mc.level.getBlockState(floor).isAir())return;
            if(!(mc.getEntityRenderDispatcher().getRenderer(elite) instanceof software.bernie.geckolib.renderer.GeoEntityRenderer<?> r)||r.getGeoModel().getBone("root").isEmpty())return;
            for(String bone:new String[]{"left_hand","right_hand","right_hammer","right_knee","right_foot","chest","right_upper_arm","right_forearm"})r.getGeoModel().getBone(bone).orElseThrow().setTrackingMatrices(true);
            if(++settled>=20&&!ready){ready=true;Files.writeString(COORD.resolve("ready-"+observed+"-"+ROLE+".txt"),state.uuid);}
        }catch(Throwable e){finish(mc,e);}
    }
    private static Stage prepare(MinecraftServer server,int stage){
        var world=server.overworld();
        if(fixture!=null)fixture.discard();
        world.getEntitiesOfClass(net.minecraft.world.entity.item.ItemEntity.class,new net.minecraft.world.phys.AABB(-24,-64,-24,24,-40,24)).forEach(Entity::discard);
        if(victim!=null)victim.discard();
        if(stage>=14)return prepareEntry(server,stage);
        fixture=EliteContent.HAMMER.get().create(world);fixture.moveTo(0,-60,0,0,0);fixture.setNoAi(true);fixture.setNoGravity(true);fixture.setPersistenceRequired();world.addFreshEntity(fixture);
        var cow=EntityType.COW.create(world);cow.setNoAi(true);cow.setNoGravity(true);cow.addEffect(new net.minecraft.world.effect.MobEffectInstance(net.minecraft.world.effect.MobEffects.INVISIBILITY,12000,0,false,false,false));cow.getAttribute(Attributes.MAX_HEALTH).setBaseValue(1000);cow.setHealth(1000);cow.moveTo(0,-60,stage==7||stage==8?6:stage==9||stage==10?8:3,180,0);world.addFreshEntity(cow);victim=cow;
        for(var player:server.getPlayerList().getPlayers()){player.setGameMode(GameType.CREATIVE);player.teleportTo(world,0,-60,16,180,0);player.getAbilities().flying=true;player.onUpdateAbilities();}
        return snapshot(stage,"READY",world.getGameTime());
    }
    private static Stage activate(MinecraftServer server,int stage){
        if(stage>=14)return snapshot(stage,"ACTIVE",server.overworld().getGameTime());
        if(stage>=12){
            var player=server.getPlayerList().getPlayers().stream().filter(p->p.getGameProfile().getName().equals("BlueprintHost")).findFirst().orElseThrow();
            fixture.hurt(fixture.damageSources().playerAttack(player),10000);if(!fixture.isDeadOrDying())throw new AssertionError("Connected-player kill rejected");
            var hook=server.getAdvancements().getAdvancement(new net.minecraft.resources.ResourceLocation("dynasty","blueprint/kill_juchui_jinjia_lishi"));
            if(hook==null||!player.getAdvancements().getOrStartProgress(hook).isDone())throw new AssertionError("Connected-player kill did not award the native advancement");
        }
        else if(stage==4){fixture.setDeltaMovement(.18,0,0);}
        else if(stage==11){if(!fixture.hurt(fixture.damageSources().mobAttack(victim),4))throw new AssertionError("Hurt rejected");}
        else if(!fixture.startSkill(SKILLS[stage],victim))throw new AssertionError("Server refused elite action "+stage);
        return snapshot(stage,"ACTIVE",server.overworld().getGameTime());
    }
    private static String entryKey;
    private static Stage prepareEntry(MinecraftServer server,int stage){
        var world=server.overworld();var registry=world.registryAccess();
        var structureId="imperial_tomb";entryKey="dynasty:"+structureId+"@0:hammer_guardian";
        var structure=registry.registryOrThrow(Registries.STRUCTURE).get(new net.minecraft.resources.ResourceLocation("dynasty",structureId));
        if(structure==null)throw new AssertionError("Native Tiangong structure registry missing");
        var settings=net.minecraft.world.level.levelgen.flat.FlatLevelGeneratorSettings.getDefault(registry.lookupOrThrow(Registries.BIOME),registry.lookupOrThrow(Registries.STRUCTURE_SET),registry.lookupOrThrow(Registries.PLACED_FEATURE));
        settings.getLayersInfo().clear();settings.getLayersInfo().add(new net.minecraft.world.level.levelgen.flat.FlatLayerInfo(127,Blocks.STONE));settings.getLayersInfo().add(new net.minecraft.world.level.levelgen.flat.FlatLayerInfo(1,Blocks.GRASS_BLOCK));settings.updateLayers();
        var generator=new net.minecraft.world.level.levelgen.FlatLevelSource(settings);var origin=new net.minecraft.world.level.ChunkPos(0,0);
        var start=structure.generate(registry,generator,generator.getBiomeSource(),world.getChunkSource().randomState(),world.getStructureManager(),world.getSeed(),origin,0,world,b->true);
        if(!start.isValid())throw new AssertionError("Production city generator rejected fixture");
        world.getChunk(0,0).setStartForStructure(structure,start);
        var points=start.getPieces().stream().map(piece->piece instanceof com.dynasty.structure.TombPiece tomb?tomb.hammerPosition():null).filter(java.util.Objects::nonNull).toList();
        if(points.size()!=1)throw new AssertionError("Actual workshop marker missing or duplicated "+points);
        var feet=points.get(0);
        for(int x=(feet.getX()-16)>>4;x<=(feet.getX()+16)>>4;x++)for(int z=(feet.getZ()-16)>>4;z<=(feet.getZ()+16)>>4;z++){
            var chunk=world.getChunk(x,z);chunk.addReferenceForStructure(structure,origin.toLong());
            var bounds=start.getBoundingBox();var clip=new net.minecraft.world.level.levelgen.structure.BoundingBox(x*16,bounds.minY(),z*16,x*16+15,bounds.maxY(),z*16+15);
            for(var piece:start.getPieces())piece.postProcess(world,world.structureManager(),generator,net.minecraft.util.RandomSource.create(3),clip,chunk.getPos(),BlockPos.ZERO);
        }
        if(!world.getBlockState(feet.below()).isFaceSturdy(world,feet.below(),Direction.UP))throw new AssertionError("Workshop marker lacks actual generated floor "+feet);
        world.getGameRules().getRule(GameRules.RULE_DOMOBSPAWNING).set(true,server);
        for(var player:server.getPlayerList().getPlayers()){player.setGameMode(GameType.CREATIVE);player.teleportTo(world,feet.getX()+.5,feet.getY(),feet.getZ()-8.5,0,0);}
        return new Stage(stage,"SPAWNING",-1,"",0,-1,world.getGameTime());
    }
    private static Stage pollEntry(MinecraftServer server,int stage){
        var world=server.overworld();var marker=com.dynasty.blueprint.BlueprintSpawnState.get(world).markers.get(entryKey);
        if(marker==null||marker.members.isEmpty())return new Stage(stage,"SPAWNING",-1,"",0,-1,world.getGameTime());
        if(marker.produced!=1||marker.members.size()!=1)throw new AssertionError("Production city duplicated an elite");
        var entity=world.getEntity(marker.members.iterator().next());
        if(!(entity instanceof HammerGuardian mob))throw new AssertionError("Wrong real workshop actor "+entity);
        fixture=mob;
        if(mob.isNoAi()||mob.isNoGravity()||!mob.encounterSite().equals(entryKey.substring(0,entryKey.lastIndexOf(':'))))throw new AssertionError("Production site or normal simulation lost");
        try{Files.writeString(OUT.resolve(stage==14?"world-tomb-entry.json":"world-gate-entry.json"),JSON.toJson(Map.of("uuid",mob.getUUID().toString(),"site",mob.encounterSite(),"produced",marker.produced,"position",mob.position().toString(),"players",world.players().size(),"scope","Real existing tomb/gate generator and authored guard floor, then ordinary EliteEncounters ticks; QA never spawns this actor")));}
        catch(Exception e){throw new RuntimeException(e);}
        return snapshot(stage,"READY",world.getGameTime());
    }
    private static Stage snapshot(int stage,String phase,long now){return new Stage(stage,phase,fixture.getId(),fixture.getUUID().toString(),fixture.skillId(),fixture.skillStart(),now);}
    private static void publish(Stage state)throws Exception{var tmp=COORD.resolve("elite-stage-next.json");Files.writeString(tmp,JSON.toJson(state));Files.move(tmp,COORD.resolve("elite-stage.json"),StandardCopyOption.REPLACE_EXISTING,StandardCopyOption.ATOMIC_MOVE);}
    private static boolean both(String label,int stage){return Files.exists(COORD.resolve(label+"-"+stage+"-host.txt"))&&(SOLO||Files.exists(COORD.resolve(label+"-"+stage+"-peer.txt")));}
    @SubscribeEvent public static void render(TickEvent.RenderTickEvent event){
        if(!ENABLED||done||event.phase!=TickEvent.Phase.END||captured||local==null||!ready)return;
        var mc=Minecraft.getInstance();if(mc.level==null||mc.getOverlay()!=null||!(mc.level.getEntity(local.entityId) instanceof HammerGuardian elite))return;
        try{
            if(observed>=4&&observed<14){if(!local.phase.equals("ACTIVE"))return;long age=mc.level.getGameTime()-local.published;if(age<AGES[observed])return;
                int last=observed==4?5:observed==6?35:observed==11?8:observed>=12?69:AGES[observed]+10;if(age>last)throw new AssertionError("Missed authored pose frame "+observed+" age="+age);
                if(elite.skillId()!=local.skill||elite.skillStart()!=local.start)throw new AssertionError("Server/client action identity differs");
                if(observed>=12&&!elite.isDeadOrDying())throw new AssertionError("Death not synchronized");
            }
            if(!(mc.getEntityRenderDispatcher().getRenderer(elite) instanceof software.bernie.geckolib.renderer.GeoEntityRenderer<?> renderer))throw new AssertionError("Wrong renderer");
            for(String bone:new String[]{"pelvis","waist","chest","head","left_hammer","right_hammer","right_hand","right_knee","dropped_right_hammer"})
                if(renderer.getGeoModel().getBone(bone).isEmpty())throw new AssertionError("Authored segmented craft rig missing "+bone);
            var controller=elite.getAnimatableInstanceCache().getManagerForId(elite.getId()).getAnimationControllers().get("body");
            String actual=controller==null||controller.getCurrentAnimation()==null?"none":controller.getCurrentAnimation().animation().name();
            String wanted="animation."+HammerGuardian.ID+"."+elite.visualAnimation();
            if(!actual.equals(wanted)||controller.getAnimationState().name().equals("STOPPED"))throw new AssertionError("Actual Gecko clip differs "+actual+" expected "+wanted);
            if(observed>=12&&observed<14){
                var knee=renderer.getGeoModel().getBone("right_knee").orElseThrow();
                var pelvis=renderer.getGeoModel().getBone("pelvis").orElseThrow();
                if(Math.abs(knee.getRotX())<1.4||Math.abs(renderer.getGeoModel().getBone("left_knee").orElseThrow().getRotX())<1.4||Math.abs(renderer.getGeoModel().getBone("chest").orElseThrow().getRotX())<.5||renderer.getGeoModel().getBone("root").orElseThrow().getPosY()>-2)throw new AssertionError("Actual two-knee collapsed death pose missing");
            }
            if(observed>=14&&(elite.isNoAi()||elite.isNoGravity()))throw new AssertionError("Production entry disabled actual AI or gravity");
            if(observed==10){
                if(!renderer.getGeoModel().getBone("right_hammer").orElseThrow().isHidden())throw new AssertionError("Thrown hammer remained in the hand");
                boolean seen=false;for(var entity:mc.level.entitiesForRendering())if(entity instanceof HammerChain chain&&chain.ownerEntityId()==elite.getId()){seen=true;if(!(mc.getEntityRenderDispatcher().getRenderer(chain) instanceof HammerGuardianRenderer.ChainRenderer))throw new AssertionError("Actual chain projectile renderer missing");}
                if(!seen)throw new AssertionError("Owner-bound physical hammer absent during released throw");
            }
            if(observed>=12&&observed<14&&(!renderer.getGeoModel().getBone("right_hammer").orElseThrow().isHidden()||renderer.getGeoModel().getBone("dropped_right_hammer").orElseThrow().isHidden()))throw new AssertionError("Death did not exchange held and dropped hammer bones");
            try(NativeImage frame=Screenshot.takeScreenshot(mc.getMainRenderTarget())){
                if(frame.getWidth()<600||frame.getHeight()<400)throw new AssertionError("Framebuffer too small");
                frame.writeToFile(OUT.resolve(String.format("%02d-hammer-%s.png",observed,NAMES[observed])));
            }
            var sample=Map.ofEntries(Map.entry("run",RUN),Map.entry("role",ROLE),Map.entry("stage",observed),Map.entry("entityUUID",elite.getUUID().toString()),Map.entry("skill",elite.skillId()),Map.entry("start",elite.skillStart()),Map.entry("clientTime",mc.level.getGameTime()),Map.entry("phase",elite.phase().name()),Map.entry("clip",actual),Map.entry("players",mc.level.players().size()),Map.entry("fps",mc.getFps()));
            Files.writeString(OUT.resolve(String.format("%02d-state.json",observed)),JSON.toJson(sample));LOG.add(sample.toString());
            Files.writeString(COORD.resolve("captured-"+observed+"-"+ROLE+".txt"),elite.getUUID().toString());captured=true;
        }catch(Throwable e){finish(mc,e);}
    }
    private static String disconnectReason(net.minecraft.client.gui.screens.Screen screen){
        String reason=screen.getTitle().getString();for(var field:screen.getClass().getDeclaredFields())try{if(net.minecraft.network.chat.Component.class.isAssignableFrom(field.getType())){field.setAccessible(true);reason+=" | "+((net.minecraft.network.chat.Component)field.get(screen)).getString();}}catch(ReflectiveOperationException ignored){}return reason;
    }
    private static void finish(Minecraft mc,Throwable error){
        if(done)return;done=true;
        try{Files.createDirectories(OUT);String result=error==null?"PASS: "+(SOLO?"single native client":"two actual loopback TCP clients")+" acknowledged 14 elite pose/action stages and the production tomb guard stage with exact entity UUID, server action epoch and rendered Gecko clips. Active-combat lifecycle and final balance remain separate acceptance.\n":"FAIL: "+error+"\n";
            if(error!=null&&mc.level!=null)try(var frame=Screenshot.takeScreenshot(mc.getMainRenderTarget())){frame.writeToFile(OUT.resolve("FAILED.png"));}
            Files.writeString(OUT.resolve(error==null?"PASS.txt":"FAIL.txt"),String.join("\n",LOG)+"\n"+result);
            if(error!=null)error.printStackTrace();
        }catch(Exception e){e.printStackTrace();}mc.stop();
    }
}
