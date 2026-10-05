package com.dynasty.client;

import com.dynasty.dungeon.*;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.screens.AccessibilityOnboardingScreen;
import net.minecraft.client.gui.screens.ConnectScreen;
import net.minecraft.client.gui.screens.TitleScreen;
import net.minecraft.client.multiplayer.ServerData;
import net.minecraft.client.multiplayer.resolver.ServerAddress;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.levelgen.WorldOptions;
import net.minecraft.world.level.levelgen.presets.WorldPresets;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.CompletableFuture;

/** Opt-in real clients, disposable worlds, ordinary interaction packets and observed client state. */
@Mod.EventBusSubscriber(modid="dynasty", value=Dist.CLIENT)
public final class DungeonClientQa {
    private static final String ROLE=System.getProperty("dynasty.cod2Qa.role", "");
    private static final boolean HOST=ROLE.equals("host"), SOLO=Boolean.getBoolean("dynasty.cod2Qa.solo");
    private static final Path ROOT=Path.of(System.getProperty("dynasty.cod2Qa.output", "build/cod2-client/results"));
    private static final int PORT=Integer.getInteger("dynasty.cod2Qa.port",25589);
    private static final UUID INSTANCE=UUID.fromString("3c292093-20a5-4453-a2a1-45aec66bc398");
    private static final BlockPos CORE=new BlockPos(-2,-59,2), SEAL=new BlockPos(0,-59,2),
        DOOR=new BlockPos(1,-59,2), STELE=new BlockPos(-1,-59,2), LIFT=new BlockPos(2,-60,2);
    private static final List<BlockPos> MARKERS=List.of(SEAL,DOOR,STELE,LIFT);
    private static final long DEADLINE=System.nanoTime()+600_000_000_000L;
    private static boolean started,finished,acted,reconnected;
    private static volatile int stage=-1;
    private static int observed=-1,frames;
    private static long reconnectAt;
    private static CompletableFuture<Void> setup,reload;

    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent event) {
        if(ROLE.isEmpty()||finished||event.phase!=TickEvent.Phase.END)return;
        Minecraft mc=Minecraft.getInstance();
        try {
            if(System.nanoTime()>DEADLINE)throw new AssertionError("Client timeout at stage "+stage+" screen="+mc.screen);
            if(Files.exists(ROOT.resolve("host-FAIL.txt"))||Files.exists(ROOT.resolve("peer-FAIL.txt"))) {
                finish(mc,"Other client failed");return;
            }
            if(!started&&(mc.screen instanceof TitleScreen||mc.screen instanceof AccessibilityOnboardingScreen)) {
                if(!mc.gameDirectory.getCanonicalPath().contains("/build/cod2-client/"))throw new AssertionError("Non-disposable game directory");
                Files.createDirectories(ROOT);
                if(Files.exists(ROOT.resolve("0-"+ROLE))||Files.exists(ROOT.resolve(ROLE+"-PASS.txt")))throw new AssertionError("Use a fresh cod2ClientRun");
                if(!HOST&&!Files.exists(ROOT.resolve("listening")))return;
                started=true;
                mc.options.pauseOnLostFocus=false;mc.options.renderDistance().set(3);mc.options.simulationDistance().set(5);
                mc.options.framerateLimit().set(30);
                if(!HOST)connect(mc);
                else {
                    GameRules rules=new GameRules();rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false,null);
                    rules.getRule(GameRules.RULE_DAYLIGHT).set(false,null);
                    mc.createWorldOpenFlows().createFreshLevel("dungeon-qa-"+System.currentTimeMillis(),
                        new LevelSettings("Disposable dungeon QA",GameType.CREATIVE,false,net.minecraft.world.Difficulty.NORMAL,true,rules,WorldDataConfiguration.DEFAULT),
                        new WorldOptions(57,false,false),r->r.registryOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.FLAT).createWorldDimensions());
                }
                return;
            }
            if(reconnectAt!=0) {
                if(System.nanoTime()<reconnectAt)return;
                reconnectAt=0;reconnected=true;connect(mc);return;
            }
            if(mc.level==null||mc.player==null)return;
            if(mc.screen!=null)mc.setScreen(null);
            if(HOST&&setup==null) {
                setup=mc.getSingleplayerServer().submit(()->setup(mc));return;
            }
            if(HOST) {
                if(!setup.isDone())return;setup.join();
                if(!Files.exists(ROOT.resolve("listening")))Files.writeString(ROOT.resolve("listening"),"127.0.0.1:"+PORT);
                if(stage<0)publish(0);
                if(acknowledged(stage)&& (SOLO||Files.exists(ROOT.resolve(stage+"-peer")))) {
                    if(stage==5) { Files.writeString(ROOT.resolve("complete"),"Observed six stages");finish(mc,null);return; }
                    publish(stage+1);
                }
            } else {
                if(Files.exists(ROOT.resolve("complete"))) {finish(mc,null);return;}
                if(!Files.exists(ROOT.resolve("stage")))return;
                stage=Integer.parseInt(Files.readString(ROOT.resolve("stage")).trim());
            }
            if(observed!=stage) {observed=stage;acted=false;frames=0;}
            if(acknowledged(stage))return;
            if(!(mc.level.getBlockEntity(SEAL) instanceof DungeonMechanismBlockEntity seal)||!INSTANCE.equals(seal.instance()))return;
            if(stage==0) {
                require(!active(mc,SEAL)&&!open(mc,DOOR)&&!open(mc,STELE),"Initial mechanisms already solved");
                require(mc.getBlockEntityRenderDispatcher().getRenderer(seal)!=null,"Mechanism renderer missing");
                var model=mc.getBlockRenderer().getBlockModel(mc.level.getBlockState(STELE));
                require(model!=mc.getModelManager().getMissingModel(),"Stele model missing");
            } else if(stage==1) {
                if(HOST&&!acted) {use(mc,SEAL);acted=true;}
                if(!active(mc,SEAL)||!open(mc,DOOR))return;
                require(mc.level.getBlockState(DOOR).getCollisionShape(mc.level,DOOR).isEmpty(),"Open door retains client collision");
            } else if(stage==2) {
                if((SOLO||!HOST)&&!acted) {
                    if(!mc.player.getMainHandItem().is(Items.IRON_PICKAXE))return;
                    use(mc,STELE);acted=true;
                }
                if(!open(mc,STELE)||!active(mc,LIFT))return;
                require(mc.level.getBlockState(STELE).getCollisionShape(mc.level,STELE).isEmpty(),"Broken stele retains client collision");
            } else if(stage==3) {
                boolean arrow=false;
                for(var entity:mc.level.entitiesForRendering())if(entity instanceof DungeonTrapArrow projectile) {
                    require(mc.getEntityRenderDispatcher().getRenderer(projectile) instanceof net.minecraft.client.renderer.entity.TippableArrowRenderer,"Poison arrow renderer missing");
                    arrow=true;
                }
                if(!arrow)return;
            } else if(stage==4) {
                if(reload==null) {reload=mc.reloadResourcePacks();return;}
                if(!reload.isDone())return;reload.join();
                if(!open(mc,STELE)||!active(mc,LIFT)||!open(mc,DOOR))return;
            } else if(stage==5) {
                if(!HOST&&!reconnected) {
                    mc.level.disconnect();mc.clearLevel(new TitleScreen());reconnectAt=System.nanoTime()+1_000_000_000L;return;
                }
                if(!open(mc,STELE)||!active(mc,LIFT)||!open(mc,DOOR))return;
                require(INSTANCE.equals(((DungeonMechanismBlockEntity)mc.level.getBlockEntity(LIFT)).instance()),"Reload/rejoin lost BE binding");
            }
            if(++frames<5)return;
            Files.writeString(ROOT.resolve(stage+"-"+ROLE),"PASS stage="+stage+" tick="+mc.level.getGameTime()+" player="+mc.player.getUUID()+"\n");
        } catch(Throwable failure) {finish(mc,failure.toString());}
    }
    private static void setup(Minecraft mc) {
        var server=mc.getSingleplayerServer();var level=server.overworld();
        for(int x=-6;x<=6;x++)for(int z=-3;z<=6;z++)level.setBlockAndUpdate(new BlockPos(x,-60,z),Blocks.STONE.defaultBlockState());
        var blocks=List.of(DungeonContent.CORE.get(),DungeonContent.SEAL.get(),DungeonContent.DOOR.get(),DungeonContent.SHORTCUT_STELE.get(),DungeonContent.ELEVATOR.get());
        var positions=List.of(CORE,SEAL,DOOR,STELE,LIFT);
        for(int i=0;i<positions.size();i++) {
            BlockPos p=positions.get(i);level.setBlockAndUpdate(p,blocks.get(i).defaultBlockState());
            var be=(DungeonMechanismBlockEntity)level.getBlockEntity(p);
            be.configure(INSTANCE,"qa",i>=3?"return_lift":"part_"+i,CORE,i==1?0:-1,i==0?MARKERS:List.of());
            if(i==0)be.configureRoom(1,false,CORE,CORE.offset(6,4,4));
            if(i==4)be.setDestination(new BlockPos(3,-59,0));
        }
        level.setDefaultSpawnPos(new BlockPos(0,-59,0),0);level.setDayTime(6000);
        for(var player:server.getPlayerList().getPlayers())prepare(player);
        if(!SOLO)try {
            server.setUsesAuthentication(false);
            server.getConnection().startTcpServerListener(java.net.InetAddress.getByName("127.0.0.1"),PORT);
        }catch(Exception e){throw new RuntimeException(e);}
    }
    @SubscribeEvent public static void joined(net.minecraftforge.event.entity.player.PlayerEvent.PlayerLoggedInEvent event) {
        if(HOST&&event.getEntity() instanceof net.minecraft.server.level.ServerPlayer player)prepare(player);
    }
    private static void prepare(net.minecraft.server.level.ServerPlayer player) {
        player.setGameMode(GameType.CREATIVE);player.teleportTo(-.5,-59,.5);
        player.getInventory().selected=0;player.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(Items.IRON_PICKAXE));
        player.inventoryMenu.broadcastChanges();
    }
    @SubscribeEvent public static void serverTick(TickEvent.ServerTickEvent event) {
        if(!HOST||stage!=3||event.phase!=TickEvent.Phase.END)return;
        var level=Minecraft.getInstance().getSingleplayerServer().overworld();
        if(level.getGameTime()%20!=0)return;
        var arrow=DungeonContent.TRAP_ARROW.get().create(level);arrow.setPos(0,-56,2);arrow.setNoGravity(true);level.addFreshEntity(arrow);
    }
    private static void use(Minecraft mc,BlockPos pos) {
        mc.gameMode.useItemOn(mc.player,InteractionHand.MAIN_HAND,new BlockHitResult(Vec3.atCenterOf(pos),Direction.NORTH,pos,false));
    }
    private static boolean open(Minecraft mc,BlockPos p){return mc.level.getBlockState(p).getValue(DungeonMechanismBlock.OPEN);}
    private static boolean active(Minecraft mc,BlockPos p){return mc.level.getBlockState(p).getValue(DungeonMechanismBlock.ACTIVE);}
    private static void require(boolean condition,String reason){if(!condition)throw new AssertionError(reason);}
    private static boolean acknowledged(int s){return Files.exists(ROOT.resolve(s+"-"+ROLE));}
    private static void connect(Minecraft mc) {
        String address="127.0.0.1:"+PORT;
        ConnectScreen.startConnecting(new TitleScreen(),mc,ServerAddress.parseString(address),new ServerData("Disposable dungeon QA",address,false),false);
    }
    private static void publish(int next)throws Exception {
        stage=next;Path temp=ROOT.resolve("stage-next");Files.writeString(temp,Integer.toString(stage));
        Files.move(temp,ROOT.resolve("stage"),java.nio.file.StandardCopyOption.REPLACE_EXISTING,java.nio.file.StandardCopyOption.ATOMIC_MOVE);
    }
    private static void finish(Minecraft mc,String failure) {
        finished=true;
        try {Files.createDirectories(ROOT);Files.writeString(ROOT.resolve(ROLE+(failure==null?"-PASS.txt":"-FAIL.txt")),failure==null?"All six client stages passed\n":failure+"\n");}
        catch(Exception e){e.printStackTrace();}
        mc.stop();
    }
}
