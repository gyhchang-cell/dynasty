package com.dynasty.client;

import com.dynasty.blueprint.SkullBloodPool;
import com.dynasty.blueprint.*;
import com.dynasty.blueprint.client.TemplateMobRenderer;
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
public final class ContinuationClientQa {
    private static final boolean ENABLED=Boolean.getBoolean("dynasty.blueprintQa.rest");
    private static final String ROLE=System.getProperty("dynasty.blueprintQa","");
    private static final boolean HOST=ROLE.equals("host"),SOLO=Boolean.getBoolean("dynasty.blueprintQa.solo");
    private static final String RUN=System.getProperty("dynasty.blueprintQa.run","unset");
    private static final Path ROOT=Path.of(System.getProperty("dynasty.blueprintQa.output","build/blueprint-client/results"));
    private static final Path OUT=ROOT.resolve(ROLE),COORD=ROOT.resolve("coord");
    private static final Gson JSON=new GsonBuilder().setPrettyPrinting().create();
    private record Subject(String id,int primary,int special){}
    private record Scenario(String id,int view,int skill,int mode,int age,String label){}
    private static final Subject[] SUBJECTS={
        new Subject("pijia_panjiang_huwei",20,21),new Subject("yinbing_guizu",22,23),
        new Subject("shibian_lishi",24,0),new Subject("fuhun_baibu_tongzi",25,26),new Subject("zhiren_jianke",27,28)};
    private static final List<Scenario> SCENES=scenes();
    private static List<Scenario> scenes(){
        var result=new ArrayList<Scenario>();
        for(var subject:SUBJECTS){
            for(int view=0;view<3;view++)result.add(new Scenario(subject.id,view,0,0,0,subject.id+"-"+new String[]{"front","side","45"}[view]));
            for(int skill:new int[]{subject.primary,subject.special})if(skill>0){
                var definition=TemplateSkills.byId(skill);
                result.add(new Scenario(subject.id,0,skill,1,Math.max(1,definition.windupTicks()/2),subject.id+"-"+definition.key()+"-tell"));
                result.add(new Scenario(subject.id,0,skill,1,Math.max(2,definition.impactTicks().get(0)+1),subject.id+"-"+definition.key()+"-contact"));
            }
            result.add(new Scenario(subject.id,0,0,2,2,subject.id+"-hurt"));
            boolean paper=subject.id.equals("zhiren_jianke");
            result.add(new Scenario(subject.id,0,0,3,paper?2:20,subject.id+"-death-mid"));
            result.add(new Scenario(subject.id,0,0,3,paper?7:38,subject.id+"-death-late"));
        }return List.copyOf(result);
    }
    private record Stage(int index,String phase,int entityId,String uuid,int skill,long start,long published){}
    private static final List<String> LOG=new ArrayList<>();
    private static final long DEADLINE=System.nanoTime()+600_000_000_000L;
    private static boolean started,done,captured,ready,listener;
    private static int index=-1,observed=-1,settled,diagnosticTicks;
    private static Stage local;
    private static CompletableFuture<Stage> pending;
    private static CompletableFuture<Void> setup;
    private static TemplateMob fixture;
    private static LivingEntity victim;
    private static ArmorStand camera;

    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent event){
        if(!ENABLED||ROLE.isBlank()||done||event.phase!=TickEvent.Phase.END)return;
        var mc=Minecraft.getInstance();
        try{
            if(++diagnosticTicks%100==0)diagnose(mc);
            if(System.nanoTime()>DEADLINE)throw new AssertionError("Basic-mob continuation QA timed out");
            if(Files.exists(ROOT.resolve(HOST?"peer/FAIL.txt":"host/FAIL.txt")))throw new AssertionError("Other client failed");
            if(mc.getOverlay()!=null)return;
            if(started&&mc.screen instanceof DisconnectedScreen)throw new AssertionError("Real peer disconnected before acceptance: "+disconnectReason(mc.screen));
            if(mc.screen instanceof AccessibilityOnboardingScreen)mc.setScreen(new TitleScreen());
            if(!started&&mc.screen instanceof TitleScreen){
                if(!mc.gameDirectory.getCanonicalPath().endsWith("/build/blueprint-client/"+ROLE))throw new AssertionError("Refusing live game directory");
                if(Files.exists(OUT.resolve("PASS.txt"))||Files.exists(OUT.resolve("FAIL.txt")))throw new AssertionError("Run already used");
                Files.createDirectories(OUT);Files.createDirectories(COORD);mc.options.pauseOnLostFocus=false;mc.options.renderDistance().set(4);mc.options.fov().set(55);
                if(!HOST&&!Files.exists(COORD.resolve("listening.txt")))return;started=true;
                if(!HOST){String address="127.0.0.1:25587";ConnectScreen.startConnecting(new TitleScreen(),mc,ServerAddress.parseString(address),new ServerData("Disposable basic-mob QA",address,false),false);}
                else{
                    var rules=new GameRules();rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false,null);rules.getRule(GameRules.RULE_DAYLIGHT).set(false,null);
                    mc.createWorldOpenFlows().createFreshLevel("blueprint-"+RUN+"-"+System.currentTimeMillis(),
                        new LevelSettings("Disposable basic-mob QA",GameType.CREATIVE,false,Difficulty.NORMAL,true,rules,WorldDataConfiguration.DEFAULT),
                        new WorldOptions(57,false,false),registry->registry.registryOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.FLAT).createWorldDimensions());
                }return;
            }
            if(mc.level==null||mc.player==null)return;if(mc.screen!=null)mc.setScreen(null);if(HOST&&observed>=0&&SCENES.get(observed).skill==ArmySkills.CHILD_CURSE){mc.player.setYRot(0);mc.player.setXRot(0);}
            if(HOST&&setup==null){var server=mc.getSingleplayerServer();setup=server.submit(()->{
                var world=server.overworld();world.setDayTime(6000);
                for(int x=-16;x<=16;x++)for(int z=-16;z<=16;z++)world.setBlockAndUpdate(new BlockPos(x,-61,z),Blocks.STONE.defaultBlockState());
                if(!SOLO){server.setUsesAuthentication(false);try{server.getConnection().startTcpServerListener(java.net.InetAddress.getByName("127.0.0.1"),25587);}catch(Exception e){throw new RuntimeException(e);}}
            });return;}
            if(HOST){
                if(!setup.isDone())return;setup.join();
                if(!listener){Files.writeString(COORD.resolve("listening.txt"),RUN);listener=true;}
                var server=mc.getSingleplayerServer();
                if(!SOLO&&server.getPlayerList().getPlayerCount()<2)return;
                if(pending!=null){if(!pending.isDone())return;local=pending.join();pending=null;publish(local);}
                if(index<0){index=0;pending=server.submit(()->prepare(server,index));return;}
                if(local!=null&&local.phase.equals("READY")&&SCENES.get(index).mode>0&&both("ready",index)){pending=server.submit(()->activate(server,index));return;}
                if(both("captured",index)){
                    if(index==SCENES.size()-1){Files.writeString(COORD.resolve("complete.txt"),RUN);if(SOLO||Files.exists(ROOT.resolve("peer/PASS.txt")))finish(mc,null);}
                    else{index++;pending=server.submit(()->prepare(server,index));}return;
                }
            }else if(Files.exists(COORD.resolve("complete.txt"))){finish(mc,null);return;}
            if(!Files.exists(COORD.resolve("elite-stage.json")))return;
            var state=JSON.fromJson(Files.readString(COORD.resolve("elite-stage.json")),Stage.class);
            if(state.index!=observed){observed=state.index;settled=0;ready=false;captured=false;camera=null;}
            local=state;
            if(!(mc.level.getEntity(state.entityId) instanceof TemplateMob elite)||!elite.getUUID().toString().equals(state.uuid))return;
            if(!SOLO&&mc.level.players().size()!=2)return;
            if(camera==null){
                mc.options.hideGui=true;mc.options.setCameraType(CameraType.FIRST_PERSON);
                camera=new ArmorStand(mc.level,SCENES.get(observed).view==1?8:SCENES.get(observed).view==2?6:0,-59.2,SCENES.get(observed).view==1?0:SCENES.get(observed).view==2?6:8);
                camera.setNoGravity(true);camera.setYRot(SCENES.get(observed).view==1?90:SCENES.get(observed).view==2?135:180);camera.setXRot(4);
                camera.setYHeadRot(camera.getYRot());camera.yHeadRotO=camera.getYRot();camera.setOldPosAndRot();mc.setCameraEntity(camera);
            }
            if(++settled>=20&&!ready){ready=true;Files.writeString(COORD.resolve("ready-"+observed+"-"+ROLE+".txt"),state.uuid);}
        }catch(Throwable e){finish(mc,e);}
    }
    private static void diagnose(Minecraft mc)throws Exception{
        var text=new StringBuilder("[Continuation QA] role="+ROLE+" screen="+(mc.screen==null?"none":mc.screen.getClass().getSimpleName())+" players="+(mc.level==null?0:mc.level.players().size()));
        if(mc.screen instanceof ConnectScreen)for(var field:ConnectScreen.class.getDeclaredFields())if(net.minecraft.network.Connection.class.isAssignableFrom(field.getType())){
            field.setAccessible(true);if(field.get(mc.screen) instanceof net.minecraft.network.Connection c&&c.channel()!=null){var channel=c.channel();
                text.append(" client active=").append(channel.isActive()).append(" read=").append(channel.config().isAutoRead()).append(" protocol=").append(channel.attr(net.minecraft.network.Connection.ATTRIBUTE_PROTOCOL).get()).append(" received=").append(c.getAverageReceivedPackets()).append(" sent=").append(c.getAverageSentPackets());
            }
        }
        if(HOST&&mc.getSingleplayerServer()!=null){var connections=mc.getSingleplayerServer().getConnection().getConnections();java.util.List<net.minecraft.network.Connection> copy;
            synchronized(connections){copy=java.util.List.copyOf(connections);}for(var c:copy)if(!c.isMemoryConnection()&&c.channel()!=null){var ch=c.channel();var buffer=ch.unsafe().outboundBuffer();
                text.append(" server active=").append(ch.isActive()).append(" read=").append(ch.config().isAutoRead()).append(" protocol=").append(ch.attr(net.minecraft.network.Connection.ATTRIBUTE_PROTOCOL).get()).append(" pending=").append(buffer==null?-1:buffer.totalPendingWriteBytes());
            }
        }System.out.println(text);
    }
    private static String disconnectReason(net.minecraft.client.gui.screens.Screen screen){
        String result=screen.getTitle().getString();
        for(var field:screen.getClass().getDeclaredFields())if(net.minecraft.network.chat.Component.class.isAssignableFrom(field.getType()))try{
            field.setAccessible(true);if(field.get(screen) instanceof net.minecraft.network.chat.Component text)result+=" | "+text.getString();
        }catch(ReflectiveOperationException ignored){}
        return result;
    }
    private static Stage prepare(MinecraftServer server,int stage){
        var world=server.overworld();var scene=SCENES.get(stage);
        world.getEntitiesOfClass(net.minecraft.world.entity.item.ItemEntity.class,new net.minecraft.world.phys.AABB(-24,-64,-24,24,-40,24)).forEach(Entity::discard);
        world.getEntitiesOfClass(net.minecraft.world.entity.ExperienceOrb.class,new net.minecraft.world.phys.AABB(-24,-64,-24,24,-40,24)).forEach(Entity::discard);
        world.getEntitiesOfClass(CorpseMiasma.class,new net.minecraft.world.phys.AABB(-24,-64,-24,24,-40,24)).forEach(Entity::discard);
        if(fixture!=null){var old=fixture;world.getEntitiesOfClass(SkullBloodPool.class,old.getBoundingBox().inflate(24),p->p.ownedBy(old)).forEach(Entity::discard);old.discard();}
        if(victim!=null&&!(victim instanceof net.minecraft.server.level.ServerPlayer))victim.discard();
        var type=net.minecraftforge.registries.ForgeRegistries.ENTITY_TYPES.getValue(new net.minecraft.resources.ResourceLocation("dynasty",scene.id));
        fixture=(TemplateMob)type.create(world);fixture.moveTo(0,-60,0,0,0);fixture.setYHeadRot(0);fixture.setYBodyRot(0);
        fixture.setNoAi(true);fixture.setNoGravity(true);fixture.setPersistenceRequired();world.addFreshEntity(fixture);
        var cow=EntityType.COW.create(world);cow.setNoAi(true);cow.setNoGravity(true);cow.addEffect(new net.minecraft.world.effect.MobEffectInstance(net.minecraft.world.effect.MobEffects.INVISIBILITY,12000,0,false,false,false));cow.getAttribute(Attributes.MAX_HEALTH).setBaseValue(1000);cow.setHealth(1000);cow.getAttribute(Attributes.KNOCKBACK_RESISTANCE).setBaseValue(1);cow.moveTo(0,-60,2.1,0,0);world.addFreshEntity(cow);victim=cow;
        for(var player:server.getPlayerList().getPlayers()){player.setGameMode(GameType.CREATIVE);player.setInvulnerable(false);player.teleportTo(world,0,-60,16,0,0);player.getAbilities().flying=true;player.onUpdateAbilities();}
        if(scene.skill==ArmySkills.CHILD_CURSE){
            cow.discard();var player=server.getPlayerList().getPlayers().stream().filter(p->p.getGameProfile().getName().equals("BlueprintHost")).findFirst().orElseThrow();
            player.setGameMode(GameType.SURVIVAL);player.setInvulnerable(true);player.teleportTo(world,0,-60,3,0,0);victim=player;
        }
        return snapshot(stage,"READY",world.getGameTime());
    }
    private static Stage activate(MinecraftServer server,int stage){
        var scene=SCENES.get(stage);
        if(scene.mode==3){
            var player=server.getPlayerList().getPlayers().stream().filter(p->p.getGameProfile().getName().equals("BlueprintHost")).findFirst().orElseThrow();
            fixture.hurt(fixture.damageSources().playerAttack(player),10000);if(!fixture.isDeadOrDying())throw new AssertionError("Connected-player kill rejected");
            var hook=server.getAdvancements().getAdvancement(new net.minecraft.resources.ResourceLocation("dynasty","story_slay_"+scene.id));
            if(hook==null||!player.getAdvancements().getOrStartProgress(hook).isDone())throw new AssertionError("Connected-player kill did not award the native advancement "+scene.id);
        }else if(scene.mode==2){
            if(!fixture.hurt(fixture.damageSources().magic(),1))throw new AssertionError("Real hurt never accepted");
        }else if(scene.skill==ArmySkills.AXE_COUNTER){
            for(int n=0;n<3;n++){fixture.invulnerableTime=0;fixture.hurt(fixture.damageSources().mobAttack(victim),1);}
        }else if(scene.skill==ArmySkills.GHOST_PHASE){
            for(int n=0;n<32&&fixture.skillId()!=ArmySkills.GHOST_PHASE;n++){fixture.invulnerableTime=0;fixture.hurt(fixture.damageSources().mobAttack(victim),.01F);}
        }else if(scene.skill==ArmySkills.PAPER_SHED){fixture.hurt(fixture.damageSources().mobAttack(victim),10000);}
        else if(!fixture.startSkill(scene.skill,victim))throw new AssertionError("Server refused action "+scene.label);
        if(scene.mode==1&&fixture.skillId()!=scene.skill)throw new AssertionError("Real reaction did not produce its authored skill "+scene.label+" actual="+fixture.skillId());
        fixture.setDeltaMovement(net.minecraft.world.phys.Vec3.ZERO);
        return snapshot(stage,"ACTIVE",server.overworld().getGameTime());
    }
    private static Stage snapshot(int stage,String phase,long now){return new Stage(stage,phase,fixture.getId(),fixture.getUUID().toString(),fixture.skillId(),fixture.skillStartTime(),now);}
    private static void publish(Stage state)throws Exception{var tmp=COORD.resolve("elite-stage-next.json");Files.writeString(tmp,JSON.toJson(state));Files.move(tmp,COORD.resolve("elite-stage.json"),StandardCopyOption.REPLACE_EXISTING,StandardCopyOption.ATOMIC_MOVE);}
    private static boolean both(String label,int stage){return Files.exists(COORD.resolve(label+"-"+stage+"-host.txt"))&&(SOLO||Files.exists(COORD.resolve(label+"-"+stage+"-peer.txt")));}
    @SubscribeEvent public static void render(TickEvent.RenderTickEvent event){
        if(!ENABLED||done||event.phase!=TickEvent.Phase.END||captured||local==null||!ready)return;
        var mc=Minecraft.getInstance();if(mc.level==null||mc.getOverlay()!=null||!(mc.level.getEntity(local.entityId) instanceof TemplateMob elite))return;
        try{
            var scene=SCENES.get(observed);
            if(scene.mode>0){
                if(!local.phase.equals("ACTIVE"))return;long age=mc.level.getGameTime()-local.published;if(age<scene.age)return;
                int last=scene.mode==3?elite.deathDuration()-1:scene.mode==2?8:TemplateSkills.byId(scene.skill).totalTicks()-1;
                if(age>Math.min(last,scene.age+10))throw new AssertionError("Missed authored pose frame "+scene.label+" age="+age);
                if(elite.skillId()!=local.skill||elite.skillStartTime()!=local.start)throw new AssertionError("Server/client action identity differs");
                if(scene.mode==3&&!elite.isDeadOrDying())throw new AssertionError("Death not synchronized");
            }
            if(!(mc.getEntityRenderDispatcher().getRenderer(elite) instanceof TemplateMobRenderer renderer))throw new AssertionError("Wrong registered renderer");
            if(renderer.getGeoModel().getBone("root").isEmpty())throw new AssertionError("Actual independently authored model was not loaded");
            var controller=elite.getAnimatableInstanceCache().getManagerForId(elite.getId()).getAnimationControllers().get("body");
            String actual=controller==null||controller.getCurrentAnimation()==null?"none":controller.getCurrentAnimation().animation().name();
            String wanted="animation."+elite.blueprintId()+"."+elite.visualAnimation();
            if(!actual.equals(wanted)||controller.getAnimationState().name().equals("STOPPED"))throw new AssertionError("Actual Gecko clip differs "+actual+" expected "+wanted);
            try(NativeImage frame=Screenshot.takeScreenshot(mc.getMainRenderTarget())){
                if(frame.getWidth()<600||frame.getHeight()<400)throw new AssertionError("Framebuffer too small");
                frame.writeToFile(OUT.resolve(String.format("%02d-%s.png",observed,SCENES.get(observed).label)));
            }
            var sample=Map.ofEntries(Map.entry("run",RUN),Map.entry("role",ROLE),Map.entry("stage",observed),Map.entry("entityUUID",elite.getUUID().toString()),Map.entry("skill",elite.skillId()),Map.entry("start",elite.skillStartTime()),Map.entry("clientTime",mc.level.getGameTime()),Map.entry("phase",elite.skillPhase().name()),Map.entry("clip",actual),Map.entry("players",mc.level.players().size()),Map.entry("fps",mc.getFps()));
            Files.writeString(OUT.resolve(String.format("%02d-state.json",observed)),JSON.toJson(sample));LOG.add(sample.toString());
            Files.writeString(COORD.resolve("captured-"+observed+"-"+ROLE+".txt"),elite.getUUID().toString());captured=true;
        }catch(Throwable e){finish(mc,e);}
    }
    private static void finish(Minecraft mc,Throwable error){
        if(done)return;done=true;
        try{Files.createDirectories(OUT);String result=error==null?"PASS: "+(SOLO?"single native client":"two actual loopback TCP clients")+" acknowledged "+SCENES.size()+" registered basic-mob pose/action stages with exact entity UUID, server action epoch and rendered Gecko clips. Five existing actors, three silhouette views, real reaction skills, hurt and connected-player kill/death clips verified. Structure entry, active-combat restart and sustained performance remain separate acceptance.\n":"FAIL: "+error+"\n";
            if(error!=null&&mc.level!=null)try(var frame=Screenshot.takeScreenshot(mc.getMainRenderTarget())){frame.writeToFile(OUT.resolve("FAILED.png"));}
            Files.writeString(OUT.resolve(error==null?"PASS.txt":"FAIL.txt"),String.join("\n",LOG)+"\n"+result);
            if(error!=null)error.printStackTrace();
        }catch(Exception e){e.printStackTrace();}mc.stop();
    }
}
