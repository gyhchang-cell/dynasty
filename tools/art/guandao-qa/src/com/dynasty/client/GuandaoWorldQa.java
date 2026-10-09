package com.dynasty.client;

import com.dynasty.DynastyWeapons;
import net.minecraft.client.Minecraft;
import net.minecraft.client.CameraType;
import net.minecraft.client.Screenshot;
import net.minecraft.client.gui.screens.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.entity.decoration.ArmorStand;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.*;
import net.minecraft.world.level.levelgen.WorldOptions;
import net.minecraft.world.level.levelgen.presets.WorldPresets;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.CompletableFuture;

/** Captures the real world framebuffer through normal Forge render events in a disposable world. */
@Mod.EventBusSubscriber(modid="dynasty",value=Dist.CLIENT)
public final class GuandaoWorldQa {
    private static boolean started,done;
    private static CompletableFuture<Void> setup;
    private static long deadline=System.nanoTime()+600_000_000_000L;
    private static int ticks,stage=Integer.getInteger("dynasty.guandaoQa.startStage",0),wait;
    private static ArmorStand camera;
    private static final Path OUT=Path.of(System.getProperty("dynasty.guandaoQa.output","build/guandao-world-qa/results"));
    private static final String[] NAMES={"world-front","world-45","world-side","world-first-person","world-third-person","world-item-entity"};
    private static final List<String> log=new ArrayList<>();
    private static final boolean REGRESSION=Boolean.getBoolean("dynasty.guandaoQa.regression");
    private static final String ROLE=System.getProperty("dynasty.guandaoQa.role","solo");
    private static final boolean NETWORK=!ROLE.equals("solo"),HOST=ROLE.equals("host");
    private static final Path NET_OUT=OUT.resolve(ROLE),COORD=OUT.resolve("coord");
    private static final com.google.gson.Gson JSON=new com.google.gson.Gson();
    private record NetStage(int index,long born,UUID holder,UUID target){}
    private static NetStage netStage;
    private static CompletableFuture<NetStage> netSetup;
    private static CompletableFuture<Void> netReload;
    private static net.minecraft.world.entity.animal.Cow netTarget;
    private static int netObserved=-1;
    private static boolean netCaptured;
    private static boolean wireChecked;
    private static net.minecraft.client.player.RemotePlayer remote;
    private static int views(){return REGRESSION?56:NAMES.length;}
    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent event) {
        if(!Boolean.getBoolean("dynasty.guandaoQa")||done||event.phase!=TickEvent.Phase.END)return;
        var mc=Minecraft.getInstance();
        try {
            if (!wireChecked && mc.getOverlay()==null) {
                var method=net.minecraftforge.network.NetworkRegistry.class.getDeclaredMethod("buildChannelVersions");
                method.setAccessible(true);
                var channels=(Map<?,?>)method.invoke(null);
                var advertised=channels.get(new net.minecraft.resources.ResourceLocation("dynasty:dynasty"));
                String expected=com.dynasty.network.DynastyNetwork.protocolVersion();
                log.add("Forge cached wire schema="+advertised+"; expected="+expected);
                System.out.println("GUANDAO_WIRE_DIAG cached="+advertised+" expected="+expected);
                if (!expected.equals(advertised)) throw new AssertionError("Forge cached an incomplete wire schema before client login");
                if (expected.length()>256) throw new AssertionError("Forge login wire version exceeds 256 characters");
                wireChecked=true;
            }
            if(NETWORK){networkTick(mc);return;}
            if(System.nanoTime()>deadline)throw new AssertionError("QA timed out");
            if(mc.getOverlay()!=null)return;
            if(mc.screen instanceof AccessibilityOnboardingScreen)mc.setScreen(new TitleScreen());
            if(!started&&mc.screen instanceof TitleScreen) {
                String dir=mc.gameDirectory.getCanonicalPath();
                if(!dir.endsWith("/build/guandao-world-qa/client"))throw new AssertionError("Refusing to touch non-QA world: "+dir);
                started=true;Files.createDirectories(OUT);mc.options.renderDistance().set(5);mc.options.fov().set(45);
                mc.options.pauseOnLostFocus=false;
                GameRules rules=new GameRules();rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false,null);
                var settings=new LevelSettings("Guandao visual QA",GameType.CREATIVE,false,net.minecraft.world.Difficulty.PEACEFUL,true,rules,WorldDataConfiguration.DEFAULT);
                mc.createWorldOpenFlows().createFreshLevel("guandao-refinement-"+System.currentTimeMillis(),settings,new WorldOptions(42,false,false),r->r.registryOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.FLAT).createWorldDimensions());
                return;
            }
            if(mc.level==null||mc.player==null||++ticks<60)return;
            if(setup==null) {
                setup=mc.getSingleplayerServer().submit(()->{
                    var server=mc.getSingleplayerServer();var world=server.overworld();world.setDayTime(6000);world.getGameRules().getRule(GameRules.RULE_DAYLIGHT).set(false,server);
                    var player=server.getPlayerList().getPlayers().get(0);player.teleportTo(world,0,-60,0,0,0);
                    player.getInventory().setItem(0,new ItemStack(DynastyWeapons.QINGLONG_DAO.get()));player.getInventory().selected=0;player.getInventory().setChanged();
                    var drop=new ItemEntity(world,4,-59.7,1,new ItemStack(DynastyWeapons.QINGLONG_DAO.get()));drop.setDeltaMovement(net.minecraft.world.phys.Vec3.ZERO);drop.setNoGravity(true);drop.setNeverPickUp();world.addFreshEntity(drop);
                });return;
            }
            if(!setup.isDone())return;setup.join();
            if(mc.screen!=null)mc.setScreen(null);
            if(wait==0){configure(mc);wait=1;}else wait++;
            if(REGRESSION&&remote!=null&&wait%20==10){
                remote.swing(net.minecraft.world.InteractionHand.MAIN_HAND);
                mc.player.swing(net.minecraft.world.InteractionHand.MAIN_HAND);
                if(stage%3==0)ImperialWeaponRenderer.receive(new com.dynasty.network.WeaponImpactPacket(2,0,-57,-4,stage*36));
            }
        }catch(Throwable e){finish(mc,e);}
    }
    private static void configure(Minecraft mc) {
        mc.mouseHandler.releaseMouse();
        if(REGRESSION){
            if(remote==null){
                remote=new net.minecraft.client.player.RemotePlayer(mc.level,new com.mojang.authlib.GameProfile(UUID.fromString("12345678-0000-0000-0000-000000000042"),"ObserverFixture"));
                remote.setPos(2,-60,0);remote.setItemSlot(net.minecraft.world.entity.EquipmentSlot.MAINHAND,new ItemStack(DynastyWeapons.QINGLONG_DAO.get()));
                mc.level.addPlayer(-2042,remote);
            }
            mc.options.hideGui=true;mc.options.setCameraType(CameraType.FIRST_PERSON);
            if(stage>=36){
                // The old orbit never looked upward from INSIDE the pelvis/chest/head.
                // ArmorStand's eye offset is included so the real camera enters the solid volume.
                double eyeY=stage<40?2.6:stage<44?5.4:new double[]{3.1,3.7,4.2}[(stage-44)/4];
                camera=new ArmorStand(mc.level,0,-60+eyeY-1.7775,-4);
                camera.setYRot((stage%4)*90);camera.setXRot(stage<44?-75:-90);
                camera.setYHeadRot(camera.getYRot());camera.yHeadRotO=camera.getYRot();
                camera.setOldPosAndRot();mc.setCameraEntity(camera);return;
            }
            if(stage>=30){mc.setCameraEntity(mc.player);mc.options.setCameraType(stage%2==0?CameraType.FIRST_PERSON:CameraType.THIRD_PERSON_BACK);
                mc.player.setXRot(stage<32?-85:stage<34?85:0);return;}
            // Ground, overhead, below/cape intersections and a second holder use the same real renderer.
            int ring=stage/10;double angle=Math.toRadians((stage%10)*36);
            double radius=ring==0?4:ring==1?1.2:7;
            camera=new ArmorStand(mc.level,Math.sin(angle)*radius,-60+(ring==0?1:ring==1?5:9),-4+Math.cos(angle)*radius);
            camera.setYRot((float)(180-Math.toDegrees(angle)));camera.setXRot(ring==0?-60:ring==1?0:65);
            camera.setYHeadRot(camera.getYRot());camera.yHeadRotO=camera.getYRot();camera.setOldPosAndRot();mc.setCameraEntity(camera);
            remote.swing(net.minecraft.world.InteractionHand.MAIN_HAND);
            if(stage%3==0)ImperialWeaponRenderer.receive(new com.dynasty.network.WeaponImpactPacket(2,0,-57,-4,stage*36));
            return;
        }
        mc.options.hideGui=stage<3||stage==5;mc.options.setCameraType(CameraType.FIRST_PERSON);
        if(stage==3||stage==4){mc.setCameraEntity(mc.player);mc.options.setCameraType(stage==3?CameraType.FIRST_PERSON:CameraType.THIRD_PERSON_FRONT);return;}
        double angle=Math.toRadians(stage==1?45:stage==2?90:0),r=18;
        camera=new ArmorStand(mc.level,Math.sin(angle)*r,-56,Math.cos(angle)*r-4);
        camera.setYRot((float)(180-Math.toDegrees(angle)));camera.setXRot(0);
        if(stage==5){camera.setPos(4,-61,4);camera.setYRot(180);camera.setXRot(8);}
        camera.setYHeadRot(camera.getYRot());camera.yHeadRotO=camera.getYRot();
        camera.setOldPosAndRot();mc.setCameraEntity(camera);
    }
    @SubscribeEvent public static void render(TickEvent.RenderTickEvent event) {
        if(NETWORK){networkRender(event);return;}
        if(!Boolean.getBoolean("dynasty.guandaoQa")||done||event.phase!=TickEvent.Phase.END||wait<100)return;
        var mc=Minecraft.getInstance();if(mc.level==null||mc.player==null||mc.getOverlay()!=null)return;
        try {
            if(mc.getItemRenderer().getModel(new ItemStack(DynastyWeapons.QINGLONG_DAO.get()),mc.level,mc.player,0)==mc.getModelManager().getMissingModel())throw new AssertionError("Missing item model");
            String name=REGRESSION?"camera-regression-"+stage:NAMES[stage];
            try(var image=Screenshot.takeScreenshot(mc.getMainRenderTarget())){
                image.writeToFile(OUT.resolve(name+".png"));
                // A stride of eight aliases the shader's 4x4 Bayer reveal and can report
                // 68% dark for a frame whose actual dark coverage is 56%. Count every pixel.
                if(REGRESSION){int black=0,dark=0,total=0;for(int y=0;y<image.getHeight();y++)for(int x=0;x<image.getWidth();x++){int c=image.getPixelRGBA(x,y);int r=c&255,g=(c>>8)&255,b=(c>>16)&255;if(r<10&&g<10&&b<10)black++;if(r<40&&g<40&&b<40)dark++;total++;}
                    double fraction=black/(double)total,darkFraction=dark/(double)total;log.add(name+" black pixels="+fraction+"; dark pixels="+darkFraction);if(fraction>.96 || stage>=36&&darkFraction>.65)throw new AssertionError("Fullscreen dark occlusion "+name);
                }
            }
            log.add("Captured actual world framebuffer: "+name+"; gameTime="+mc.level.getGameTime()+"; camera="+mc.getCameraEntity().position()+"; yaw="+mc.getCameraEntity().getViewYRot(1)+"; client FPS="+mc.getFps());
            if(++stage==views()){finish(mc,null);return;}wait=0;
        }catch(Throwable e){finish(mc,e);}
    }
    private static void networkTick(Minecraft mc)throws Exception {
        if(System.nanoTime()>deadline)throw new AssertionError("Network QA timed out");
        if(Files.exists(OUT.resolve(HOST?"peer/runtime-FAIL.txt":"host/runtime-FAIL.txt")))throw new AssertionError("Other real client failed");
        // The peer exits after its last capture. Finish before the two-player readiness gate,
        // otherwise a successful peer disconnect strands the host until the QA timeout.
        if(netCaptured&&netObserved==13&&Files.exists(COORD.resolve("complete.txt"))
                &&(!HOST||Files.exists(OUT.resolve("peer/runtime-PASS.txt")))){finish(mc,null);return;}
        if(mc.getOverlay()!=null)return;
        if(mc.screen instanceof AccessibilityOnboardingScreen)mc.setScreen(new TitleScreen());
        if(!started&&mc.screen instanceof TitleScreen){
            if(!mc.gameDirectory.getCanonicalPath().endsWith("/build/guandao-world-qa/"+ROLE))throw new AssertionError("Non-QA directory");
            Files.createDirectories(NET_OUT);Files.createDirectories(COORD);
            if(Files.exists(NET_OUT.resolve("runtime-PASS.txt")))throw new AssertionError("Use a fresh output directory");
            mc.options.pauseOnLostFocus=false;mc.options.renderDistance().set(5);mc.options.fov().set(45);
            if(!HOST&&!Files.exists(COORD.resolve("listening.txt")))return;
            started=true;
            if(HOST){
                GameRules rules=new GameRules();rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false,null);rules.getRule(GameRules.RULE_DAYLIGHT).set(false,null);
                mc.createWorldOpenFlows().createFreshLevel("guandao-network-"+System.currentTimeMillis(),
                    new LevelSettings("Disposable guandao network QA",GameType.CREATIVE,false,net.minecraft.world.Difficulty.NORMAL,true,rules,WorldDataConfiguration.DEFAULT),
                    new WorldOptions(42,false,false),r->r.registryOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.FLAT).createWorldDimensions());
            }else{
                String address="127.0.0.1:25589";
                ConnectScreen.startConnecting(new TitleScreen(),mc,net.minecraft.client.multiplayer.resolver.ServerAddress.parseString(address),
                    new net.minecraft.client.multiplayer.ServerData("Disposable guandao QA",address,false),false);
            }
            return;
        }
        if(mc.screen instanceof DisconnectedScreen)throw new AssertionError("Real TCP client disconnected: "+mc.screen.getTitle().getString());
        if(mc.level==null||mc.player==null)return;
        if(mc.screen!=null)mc.setScreen(null);
        if(HOST&&setup==null){
            setup=mc.getSingleplayerServer().submit(()->{
                var server=mc.getSingleplayerServer();server.overworld().setDayTime(6000);server.setUsesAuthentication(false);
                try{server.getConnection().startTcpServerListener(java.net.InetAddress.getByName("127.0.0.1"),25589);}
                catch(Exception e){throw new RuntimeException(e);}
            });return;
        }
        if(HOST){
            if(!setup.isDone())return;setup.join();
            Files.writeString(COORD.resolve("listening.txt"),"127.0.0.1:25589");
            if(mc.getSingleplayerServer().getPlayerList().getPlayerCount()!=2)return;
            if(netSetup!=null&&netSetup.isDone()){
                netStage=netSetup.join();netSetup=null;
                Path next=COORD.resolve("stage-next.json");Files.writeString(next,JSON.toJson(netStage));
                Files.move(next,COORD.resolve("stage.json"),StandardCopyOption.REPLACE_EXISTING,StandardCopyOption.ATOMIC_MOVE);
            }
            if(netStage==null&&netSetup==null){netSetup=mc.getSingleplayerServer().submit(()->networkPrepare(mc,0));return;}
            if(netStage!=null&&netSetup==null&&Files.exists(COORD.resolve(netStage.index+"-host.txt"))&&Files.exists(COORD.resolve(netStage.index+"-peer.txt"))){
                if(netStage.index==13){Files.writeString(COORD.resolve("complete.txt"),"14 stages captured by two actual TCP clients");}
                else{int next=netStage.index+1;netSetup=mc.getSingleplayerServer().submit(()->networkPrepare(mc,next));}
            }
        }
        if(Files.exists(COORD.resolve("stage.json"))){
            NetStage incoming=JSON.fromJson(Files.readString(COORD.resolve("stage.json")),NetStage.class);
            if(incoming.index!=netObserved){netObserved=incoming.index;netStage=incoming;netCaptured=false;wait=0;netReload=null;networkCamera(mc);}
            if(mc.level.players().size()!=2||mc.level.players().stream().noneMatch(p->p.getUUID().equals(incoming.holder)))return;
            if(netObserved==11){if(netReload==null)netReload=mc.reloadResourcePacks();if(!netReload.isDone())return;netReload.join();}
            wait++;
        }
    }
    private static NetStage networkPrepare(Minecraft mc,int index){
        var server=mc.getSingleplayerServer();var world=server.overworld();
        var players=server.getPlayerList().getPlayers().stream().sorted(Comparator.comparing(p->p.getGameProfile().getName())).toList();
        for(int i=0;i<players.size();i++){
            var player=players.get(i);player.teleportTo(world,i*2,-60,0,0,0);player.getAbilities().flying=true;player.onUpdateAbilities();
            player.getInventory().setItem(0,index==2&&i==1||index==3&&i==0?ItemStack.EMPTY:new ItemStack(DynastyWeapons.QINGLONG_DAO.get()));
            player.getInventory().selected=0;player.getInventory().setChanged();
        }
        if(netTarget!=null)netTarget.discard();
        // Keep the real damage target below the inside-guardian cameras. A floating cow at -56
        // puts its opaque belly/legs across the upward view and even encloses the chest camera,
        // so the black-screen assertion measures vanilla entity occlusion instead of our renderer.
        netTarget=net.minecraft.world.entity.EntityType.COW.create(world);netTarget.moveTo(0,-60,-4,0,0);netTarget.setNoAi(true);netTarget.setNoGravity(true);
        netTarget.getAttribute(net.minecraft.world.entity.ai.attributes.Attributes.MAX_HEALTH).setBaseValue(100000);netTarget.setHealth(100000);world.addFreshEntity(netTarget);
        return new NetStage(index,world.getGameTime(),players.get(index==3?1:0).getUUID(),netTarget.getUUID());
    }
    @SubscribeEvent public static void networkServerTick(TickEvent.ServerTickEvent event){
        if(!NETWORK||!HOST||done||event.phase!=TickEvent.Phase.END||netStage==null||netStage.index<8||netStage.index>10)return;
        var server=event.getServer();var world=server.overworld();
        if((world.getGameTime()-netStage.born)%40==5){
            var holder=server.getPlayerList().getPlayer(netStage.holder);
            if(holder!=null&&netTarget!=null&&netTarget.isAlive()){
                holder.swing(net.minecraft.world.InteractionHand.MAIN_HAND);
                netTarget.invulnerableTime=0;
                netTarget.hurt(world.damageSources().playerAttack(holder),5);
            }
        }
    }
    private static void networkCamera(Minecraft mc){
        mc.options.hideGui=true;mc.options.setCameraType(CameraType.FIRST_PERSON);
        if(netObserved>=1&&netObserved<=4){mc.setCameraEntity(mc.player);mc.options.setCameraType(netObserved==1?CameraType.THIRD_PERSON_BACK:CameraType.FIRST_PERSON);mc.player.setXRot(netObserved==4?-85:0);return;}
        double eyeY=netObserved==5?2.6:netObserved==6?3.1:netObserved==7?5.4:4.2;
        camera=new ArmorStand(mc.level,netObserved==0?0:netObserved==7?.1:0,netObserved==0?-56:-60+eyeY-1.7775,netObserved==0?14:-4);
        camera.setYRot(netObserved==0?180:0);camera.setXRot(netObserved==0?0:netObserved==7?0:-90);
        camera.setYHeadRot(camera.getYRot());camera.yHeadRotO=camera.getYRot();camera.setOldPosAndRot();mc.setCameraEntity(camera);
        mc.options.graphicsMode().set(netObserved==13?net.minecraft.client.GraphicsStatus.FABULOUS:net.minecraft.client.GraphicsStatus.FANCY);
        mc.levelRenderer.allChanged();
    }
    private static void networkRender(TickEvent.RenderTickEvent event){
        if(!Boolean.getBoolean("dynasty.guandaoQa")||done||!NETWORK||event.phase!=TickEvent.Phase.END||netCaptured||wait<100)return;
        var mc=Minecraft.getInstance();if(mc.level==null||mc.player==null||mc.getOverlay()!=null||mc.level.players().size()!=2)return;
        try{
            if(netObserved>=8&&netObserved<=10){
                long phase=(mc.level.getGameTime()-netStage.born)%40;
                long wanted=netObserved==8?18:netObserved==9?31:38;
                if(Math.abs(phase-wanted)>1)return;
                var field=ImperialWeaponRenderer.class.getDeclaredField("DESCENTS");field.setAccessible(true);
                if(((Map<?,?>)field.get(null)).isEmpty())throw new AssertionError("Actual server dragon packet did not reach "+ROLE);
            }
            try(var image=Screenshot.takeScreenshot(mc.getMainRenderTarget())){
                // Preserve the same coverage threshold without sampling one repeated dither phase.
                int dark=0,total=0;for(int y=0;y<image.getHeight();y++)for(int x=0;x<image.getWidth();x++){int c=image.getPixelRGBA(x,y);if((c&255)<40&&((c>>8)&255)<40&&((c>>16)&255)<40)dark++;total++;}
                double fraction=dark/(double)total;image.writeToFile(NET_OUT.resolve(String.format("%02d-network.png",netObserved)));
                if(fraction>.65)throw new AssertionError("Fullscreen dark occlusion stage="+netObserved+" dark="+fraction);
                log.add("stage="+netObserved+" role="+ROLE+" realPlayers="+mc.level.players().size()+" holder="+netStage.holder+" target="+netStage.target+" dark="+fraction+" fps="+mc.getFps());
            }
            Files.writeString(COORD.resolve(netObserved+"-"+ROLE+".txt"),"Actual frame captured by "+mc.player.getUUID());netCaptured=true;
        }catch(Throwable e){finish(mc,e);}
    }
    private static void finish(Minecraft mc,Throwable e){
        if(done)return;done=true;if(e!=null){e.printStackTrace();log.add("FAIL: "+e);}else if(!NETWORK)log.add(REGRESSION?"PASS: camera/intersection and first/third-person views through stage 55, including vertical views inside torso; simultaneous local and client-fixture remote holders, active swings/impact packets. This does NOT replace two real network clients. No launcher save touched.":"PASS: actual in-world screenshots, first/third person and dropped-item model loaded; no launcher save touched.");
        if(NETWORK&&e==null)log.add("PASS: 14 stages with two real TCP clients, A-only/B-only/both holders, first/third person, torso intersections, actual server dragon packets, resource reload and Fabulous rendering.");
        try{Path result=NETWORK?NET_OUT:OUT;Files.createDirectories(result);Files.write(result.resolve(e==null?"runtime-PASS.txt":"runtime-FAIL.txt"),log);}catch(Exception ignored){}
        mc.setCameraEntity(mc.player);mc.stop();
    }
}
