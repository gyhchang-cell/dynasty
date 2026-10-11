package com.dynasty.client;

import com.dynasty.blueprint.SkullBloodPool;
import com.dynasty.blueprint.elite.*;
import com.dynasty.blueprint.elite.client.HeadlessRenderer;
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
public final class HeadlessClientQa {
    private static final boolean ENABLED=Boolean.getBoolean("dynasty.blueprintQa.elite");
    private static final String ROLE=System.getProperty("dynasty.blueprintQa","");
    private static final boolean HOST=ROLE.equals("host"),SOLO=Boolean.getBoolean("dynasty.blueprintQa.solo");
    private static final String RUN=System.getProperty("dynasty.blueprintQa.run","unset");
    private static final Path ROOT=Path.of(System.getProperty("dynasty.blueprintQa.output","build/blueprint-client/results"));
    private static final Path OUT=ROOT.resolve(ROLE),COORD=ROOT.resolve("coord");
    private static final Gson JSON=new GsonBuilder().setPrettyPrinting().create();
    private static final String[] NAMES={"front","side","45","roar-tell","roar-release","spin-tell","spin-one","spin-two","spin-three","spin-recovery","throw-tell","throw-contact","hurt","death-kneeling","death-empty-armour"};
    private static final int[] SKILLS={0,0,0,301,301,302,302,302,302,302,303,303,0,0,0};
    private static final int[] AGES={0,0,0,14,25,12,27,37,47,60,12,21,2,42,65};
    private record Stage(int index,String phase,int entityId,String uuid,int skill,long start,long published){}
    private static final List<String> LOG=new ArrayList<>();
    private static final long DEADLINE=System.nanoTime()+600_000_000_000L;
    private static boolean started,done,captured,ready,listener;
    private static int index=-1,observed=-1,settled;
    private static Stage local;
    private static CompletableFuture<Stage> pending;
    private static CompletableFuture<Void> setup;
    private static HeadlessGeneral fixture;
    private static LivingEntity victim;
    private static ArmorStand camera;

    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent event){
        if(!ENABLED||ROLE.isBlank()||done||event.phase!=TickEvent.Phase.END)return;
        var mc=Minecraft.getInstance();
        try{
            if(System.nanoTime()>DEADLINE)throw new AssertionError("Elite QA timed out");
            if(Files.exists(ROOT.resolve(HOST?"peer/FAIL.txt":"host/FAIL.txt")))throw new AssertionError("Other client failed");
            if(mc.getOverlay()!=null)return;
            if(started&&mc.screen instanceof DisconnectedScreen)throw new AssertionError("Real peer disconnected before acceptance");
            if(mc.screen instanceof AccessibilityOnboardingScreen)mc.setScreen(new TitleScreen());
            if(!started&&mc.screen instanceof TitleScreen){
                if(!mc.gameDirectory.getCanonicalPath().endsWith("/build/blueprint-client/"+ROLE))throw new AssertionError("Refusing live game directory");
                if(Files.exists(OUT.resolve("PASS.txt"))||Files.exists(OUT.resolve("FAIL.txt")))throw new AssertionError("Run already used");
                Files.createDirectories(OUT);Files.createDirectories(COORD);mc.options.pauseOnLostFocus=false;mc.options.renderDistance().set(4);mc.options.fov().set(55);
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
                if(!SOLO){server.setUsesAuthentication(false);try{server.getConnection().startTcpServerListener(java.net.InetAddress.getByName("127.0.0.1"),25587);}catch(Exception e){throw new RuntimeException(e);}}
            });return;}
            if(HOST){
                if(!setup.isDone())return;setup.join();
                if(!listener){Files.writeString(COORD.resolve("listening.txt"),RUN);listener=true;}
                var server=mc.getSingleplayerServer();
                if(Files.exists(COORD.resolve("complete.txt"))&&(SOLO||Files.exists(ROOT.resolve("peer/PASS.txt")))){finish(mc,null);return;}
                if(!SOLO&&server.getPlayerList().getPlayerCount()<2)return;
                if(pending!=null){if(!pending.isDone())return;local=pending.join();pending=null;publish(local);}
                if(index<0){index=0;pending=server.submit(()->prepare(server,index));return;}
                if(local!=null&&local.phase.equals("READY")&&index>=3&&both("ready",index)){pending=server.submit(()->activate(server,index));return;}
                if(both("captured",index)){
                    if(index==NAMES.length-1){Files.writeString(COORD.resolve("complete.txt"),RUN);if(SOLO||Files.exists(ROOT.resolve("peer/PASS.txt")))finish(mc,null);}
                    else{index++;pending=server.submit(()->prepare(server,index));}return;
                }
            }else if(Files.exists(COORD.resolve("complete.txt"))){finish(mc,null);return;}
            if(!Files.exists(COORD.resolve("elite-stage.json")))return;
            var state=JSON.fromJson(Files.readString(COORD.resolve("elite-stage.json")),Stage.class);
            if(state.index!=observed){observed=state.index;settled=0;ready=false;captured=false;camera=null;}
            local=state;
            if(!(mc.level.getEntity(state.entityId) instanceof HeadlessGeneral elite)||!elite.getUUID().toString().equals(state.uuid))return;
            if(!SOLO&&mc.level.players().size()!=2)return;
            if(camera==null){
                mc.options.hideGui=true;mc.options.setCameraType(CameraType.FIRST_PERSON);
                camera=new ArmorStand(mc.level,observed==1?8:observed==2?6:0,-59.2,observed==1?0:observed==2?6:8);
                camera.setNoGravity(true);camera.setYRot(observed==1?90:observed==2?135:180);camera.setXRot(4);
                camera.setYHeadRot(camera.getYRot());camera.yHeadRotO=camera.getYRot();camera.setOldPosAndRot();mc.setCameraEntity(camera);
            }
            if(!mc.levelRenderer.isChunkCompiled(new BlockPos(0,-61,0))||mc.level.getBlockState(new BlockPos(0,-61,0)).isAir())return;
            if(!(mc.getEntityRenderDispatcher().getRenderer(elite) instanceof software.bernie.geckolib.renderer.GeoEntityRenderer<?> renderer))throw new AssertionError("Wrong native renderer during readiness");
            if(renderer.getGeoModel().getBone("neck_seal").isEmpty()||renderer.getGeoModel().getBone("held_head").isEmpty())return;
            if(++settled>=20&&!ready){ready=true;Files.writeString(COORD.resolve("ready-"+observed+"-"+ROLE+".txt"),state.uuid);}
        }catch(Throwable e){finish(mc,e);}
    }
    private static Stage prepare(MinecraftServer server,int stage){
        var world=server.overworld();
        if(fixture!=null){var old=fixture;world.getEntitiesOfClass(SkullBloodPool.class,old.getBoundingBox().inflate(24),p->p.getOwner()==old).forEach(Entity::discard);old.discard();}
        if(victim!=null)victim.discard();
        fixture=EliteContent.HEADLESS.get().create(world);fixture.moveTo(0,-60,0,0,0);fixture.setNoAi(true);fixture.setNoGravity(true);fixture.setPersistenceRequired();world.addFreshEntity(fixture);
        var cow=EntityType.COW.create(world);cow.setNoAi(true);cow.setNoGravity(true);cow.addEffect(new net.minecraft.world.effect.MobEffectInstance(net.minecraft.world.effect.MobEffects.INVISIBILITY,12000,0,false,false,false));cow.getAttribute(Attributes.MAX_HEALTH).setBaseValue(1000);cow.setHealth(1000);cow.moveTo(0,-60,3,180,0);world.addFreshEntity(cow);victim=cow;
        for(var player:server.getPlayerList().getPlayers()){player.setGameMode(GameType.CREATIVE);player.teleportTo(world,0,-60,16,180,0);player.getAbilities().flying=true;player.onUpdateAbilities();}
        return snapshot(stage,"READY",world.getGameTime());
    }
    private static Stage activate(MinecraftServer server,int stage){
        if(stage>=13){
            var player=server.getPlayerList().getPlayers().stream().filter(p->p.getGameProfile().getName().equals("BlueprintHost")).findFirst().orElseThrow();
            fixture.hurt(fixture.damageSources().playerAttack(player),10000);if(!fixture.isDeadOrDying())throw new AssertionError("Connected-player kill rejected");
            var hook=server.getAdvancements().getAdvancement(new net.minecraft.resources.ResourceLocation("dynasty","blueprint/kill_xianzhen_duantoujiang"));
            if(hook==null||!player.getAdvancements().getOrStartProgress(hook).isDone())throw new AssertionError("Connected-player kill did not award the native advancement");
        }
        else if(stage==12){if(!fixture.hurt(fixture.damageSources().mobAttack(victim),4))throw new AssertionError("Hurt rejected");}
        else if(!fixture.startSkill(SKILLS[stage],victim))throw new AssertionError("Server refused elite action "+stage);
        return snapshot(stage,"ACTIVE",server.overworld().getGameTime());
    }
    private static Stage snapshot(int stage,String phase,long now){return new Stage(stage,phase,fixture.getId(),fixture.getUUID().toString(),fixture.skillId(),fixture.skillStart(),now);}
    private static void publish(Stage state)throws Exception{var tmp=COORD.resolve("elite-stage-next.json");Files.writeString(tmp,JSON.toJson(state));Files.move(tmp,COORD.resolve("elite-stage.json"),StandardCopyOption.REPLACE_EXISTING,StandardCopyOption.ATOMIC_MOVE);}
    private static boolean both(String label,int stage){return Files.exists(COORD.resolve(label+"-"+stage+"-host.txt"))&&(SOLO||Files.exists(COORD.resolve(label+"-"+stage+"-peer.txt")));}
    @SubscribeEvent public static void render(TickEvent.RenderTickEvent event){
        if(!ENABLED||done||event.phase!=TickEvent.Phase.END||captured||local==null||!ready)return;
        var mc=Minecraft.getInstance();if(mc.level==null||mc.getOverlay()!=null||!(mc.level.getEntity(local.entityId) instanceof HeadlessGeneral elite))return;
        try{
            if(observed>=3){if(!local.phase.equals("ACTIVE"))return;long age=mc.level.getGameTime()-local.published;if(age<AGES[observed])return;
                int last=observed==4?29:observed==12?8:observed>=13?69:AGES[observed]+10;if(age>last)throw new AssertionError("Missed authored pose frame "+observed+" age="+age);
                if(elite.skillId()!=local.skill||elite.skillStart()!=local.start)throw new AssertionError("Server/client action identity differs");
                if(observed>=13&&!elite.isDeadOrDying())throw new AssertionError("Death not synchronized");
            }
            if(!(mc.getEntityRenderDispatcher().getRenderer(elite) instanceof software.bernie.geckolib.renderer.GeoEntityRenderer<?> renderer))throw new AssertionError("Wrong renderer");
            if(renderer.getGeoModel().getBone("head").isPresent()||renderer.getGeoModel().getBone("neck_seal").isEmpty()||renderer.getGeoModel().getBone("held_head").isEmpty())throw new AssertionError("Headless silhouette bones missing: ordinaryHead="+renderer.getGeoModel().getBone("head").isPresent()+" seal="+renderer.getGeoModel().getBone("neck_seal").isPresent()+" held="+renderer.getGeoModel().getBone("held_head").isPresent()+" camera="+mc.gameRenderer.getMainCamera().getPosition());
            var controller=elite.getAnimatableInstanceCache().getManagerForId(elite.getId()).getAnimationControllers().get("body");
            String actual=controller==null||controller.getCurrentAnimation()==null?"none":controller.getCurrentAnimation().animation().name();
            String wanted="animation."+HeadlessGeneral.ID+"."+elite.visualAnimation();
            if(!actual.equals(wanted)||controller.getAnimationState().name().equals("STOPPED"))throw new AssertionError("Actual Gecko clip differs "+actual+" expected "+wanted);
            if(observed>=13){
                var root=renderer.getGeoModel().getBone("root").orElseThrow();
                var knee=renderer.getGeoModel().getBone("left_knee").orElseThrow();
                var head=renderer.getGeoModel().getBone("held_head").orElseThrow();
                var pelvis=renderer.getGeoModel().getBone("pelvis").orElseThrow();
                if(root.getPosY()+pelvis.getPosY()>-4||Math.abs(knee.getRotX())<1||head.getScaleX()>.1F)
                    throw new AssertionError("Death must lower the armour and bend knees after the head dissolves: combinedY="+(root.getPosY()+pelvis.getPosY())+" kneeX="+knee.getRotX()+" headScale="+head.getScaleX());
            }
            try(NativeImage frame=Screenshot.takeScreenshot(mc.getMainRenderTarget())){
                if(frame.getWidth()<600||frame.getHeight()<400)throw new AssertionError("Framebuffer too small");
                frame.writeToFile(OUT.resolve(String.format("%02d-headless-%s.png",observed,NAMES[observed])));
            }
            var sample=Map.ofEntries(Map.entry("run",RUN),Map.entry("role",ROLE),Map.entry("stage",observed),Map.entry("entityUUID",elite.getUUID().toString()),Map.entry("skill",elite.skillId()),Map.entry("start",elite.skillStart()),Map.entry("clientTime",mc.level.getGameTime()),Map.entry("phase",elite.phase().name()),Map.entry("clip",actual),Map.entry("players",mc.level.players().size()),Map.entry("fps",mc.getFps()));
            Files.writeString(OUT.resolve(String.format("%02d-state.json",observed)),JSON.toJson(sample));LOG.add(sample.toString());
            Files.writeString(COORD.resolve("captured-"+observed+"-"+ROLE+".txt"),elite.getUUID().toString());captured=true;
        }catch(Throwable e){finish(mc,e);}
    }
    private static void finish(Minecraft mc,Throwable error){
        if(done)return;done=true;
        try{Files.createDirectories(OUT);String result=error==null?"PASS: "+(SOLO?"single native client":"two actual loopback TCP clients")+" acknowledged 15 elite pose/action stages with exact entity UUID, server action epoch and rendered Gecko clips. Structure entry, active-combat restart and sustained performance remain separate acceptance.\n":"FAIL: "+error+"\n";
            if(error!=null&&mc.level!=null)try(var frame=Screenshot.takeScreenshot(mc.getMainRenderTarget())){frame.writeToFile(OUT.resolve("FAILED.png"));}
            Files.writeString(OUT.resolve(error==null?"PASS.txt":"FAIL.txt"),String.join("\n",LOG)+"\n"+result);
            if(error!=null)error.printStackTrace();
        }catch(Exception e){e.printStackTrace();}mc.stop();
    }
}
