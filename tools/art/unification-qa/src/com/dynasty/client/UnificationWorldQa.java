package com.dynasty.client;

import com.dynasty.DynastyWeapons;
import com.dynasty.workshop.*;
import com.dynasty.ritual.*;
import net.minecraft.client.*;
import net.minecraft.client.gui.screens.*;
import net.minecraft.client.multiplayer.*;
import net.minecraft.client.multiplayer.resolver.ServerAddress;
import net.minecraft.core.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.entity.decoration.ArmorStand;
import net.minecraft.world.item.*;
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

/** Two real clients through a loopback TCP connection. Never loads any launcher save. */
@Mod.EventBusSubscriber(modid="dynasty",value=Dist.CLIENT)
public final class UnificationWorldQa {
    static final String MODE=System.getProperty("dynasty.unificationQa","");
    static final Path OUT=Path.of(System.getProperty("dynasty.unificationQa.output","build/unification-client/results"));
    static final boolean HOST=MODE.equals("host");
    static final boolean SOLO=Boolean.getBoolean("dynasty.unificationQa.solo");
    static final List<String> log=new ArrayList<>();
    static boolean started,done;static int ticks,frameWait,last=-1,hostStep=-1;static long deadline=System.nanoTime()+420_000_000_000L;
    static CompletableFuture<Void> setup,change;
    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent e){
        if(MODE.isEmpty()||done||e.phase!=TickEvent.Phase.END)return;var mc=Minecraft.getInstance();
        try{
            if(System.nanoTime()>deadline)throw new AssertionError("Network QA timeout");
            if(mc.getOverlay()!=null)return;
            if(mc.screen instanceof AccessibilityOnboardingScreen)mc.setScreen(new TitleScreen());
            if(!started&&mc.screen instanceof TitleScreen){
                if(!mc.gameDirectory.getCanonicalPath().endsWith("/build/unification-client/"+MODE))throw new AssertionError("Unsafe QA directory");
                started=true;Files.createDirectories(OUT);mc.options.pauseOnLostFocus=false;mc.options.renderDistance().set(4);mc.options.fov().set(65);
                if(!HOST){String address="["+java.net.InetAddress.getLoopbackAddress().getHostAddress()+"]:25586";ConnectScreen.startConnecting(new TitleScreen(),mc,ServerAddress.parseString(address),new ServerData("Dynasty loopback QA",address,false),false);return;}
                GameRules rules=new GameRules();rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false,null);
                mc.createWorldOpenFlows().createFreshLevel("network-"+System.currentTimeMillis(),new LevelSettings("Isolated network QA",GameType.CREATIVE,false,net.minecraft.world.Difficulty.NORMAL,true,rules,WorldDataConfiguration.DEFAULT),new WorldOptions(57,false,false),r->r.registryOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.FLAT).createWorldDimensions());return;
            }
            if(mc.level==null||mc.player==null||++ticks<40)return;
            if(HOST&&setup==null){setup=mc.getSingleplayerServer().submit(()->{
                var server=mc.getSingleplayerServer();server.setUsesAuthentication(false);
                try{server.getConnection().startTcpServerListener(java.net.InetAddress.getLoopbackAddress(),25586);}catch(Exception ex){throw new RuntimeException(ex);}
                var w=server.overworld();w.getGameRules().getRule(GameRules.RULE_DAYLIGHT).set(false,server);w.setDayTime(6000);
                for(int i=0;i<8;i++){var recipe=WorkshopRecipes.ALL.get(i);var item=(BlockItem)new WorkshopRecipes.Cost("dynasty:"+recipe.station(),1).stack().getItem();w.setBlockAndUpdate(station(i),item.getBlock().defaultBlockState());}
                for(int i=0;i<4;i++){var p=new BlockPos(i*3, -60,12);w.setBlockAndUpdate(p,ZhenyuanRitualContent.NODE.get().defaultBlockState().setValue(ZhenyuanNodeBlock.SLOT,i));var node=(ZhenyuanNodeBlockEntity)w.getBlockEntity(p);node.configure(p,i);node.syncRitual(1<<i,0);}
                for(int i=0;i<DynastyTreasures.IDS.size();i++){var item=new WorkshopRecipes.Cost("dynasty:"+DynastyTreasures.IDS.get(i),1).stack();var drop=new net.minecraft.world.entity.item.ItemEntity(w,16+i*2,-58.8,3,item);drop.setNoGravity(true);drop.setNeverPickUp();drop.setDeltaMovement(net.minecraft.world.phys.Vec3.ZERO);w.addFreshEntity(drop);}
            });return;}
            if(HOST){
                if(!setup.isDone())return;setup.join();var server=mc.getSingleplayerServer();
                if(hostStep>=14){if(++frameWait>120)finish(mc,null);return;}
                if(!SOLO&&server.getPlayerList().getPlayerCount()<2)return;
                if(change!=null&&!change.isDone())return;if(change!=null)change.join();
                if(hostStep<0||last==hostStep&&frameWait>(SOLO?100:180)){hostStep++;change=server.submit(()->prepare(server,hostStep));frameWait=0;}
            }
            if(mc.screen!=null)mc.setScreen(null);
            int stage=(int)(mc.level.getDayTime()-6000);if(stage<0||stage>14)return;
            if(stage>=14){finish(mc,null);return;}
            if(stage!=last){last=stage;frameWait=0;}
            camera(mc,stage);
            frameWait++;
            if(stage>=4&&frameWait%12==0){mc.player.swing(net.minecraft.world.InteractionHand.MAIN_HAND);}
            if(stage>=8&&frameWait%40==20&&HOST)serverImpact(mc);
        }catch(Throwable ex){finish(mc,ex);}
    }
    static BlockPos station(int i){return new BlockPos((i%4)*3,-60,4+(i/4)*4);}
    static void prepare(net.minecraft.server.MinecraftServer server,int stage){
        var w=server.overworld();w.setDayTime(6000+stage);
        for(var p:server.getPlayerList().getPlayers()){
            boolean host=p.getGameProfile().getName().equals("DynastyHost");p.teleportTo(w,host?0:4,-60,0,0,0);
            p.getInventory().setItem(0,stage>=6||stage>=4&&host?new ItemStack(DynastyWeapons.QINGLONG_DAO.get()):ItemStack.EMPTY);p.getInventory().selected=0;p.getInventory().setChanged();p.containerMenu.broadcastChanges();
        }
        if(stage<4)for(int i=0;i<8;i++){
            var vat=(WorkshopBlockEntity)w.getBlockEntity(station(i));int target=stage==0?0:stage==1?1:stage==2?vat.recipe().total()/2:vat.recipe().total();
            while(vat.deposited()<target)vat.accept(vat.recipe().next(vat.deposited()).stack());
        }
    }
    static void serverImpact(Minecraft mc){mc.getSingleplayerServer().execute(()->{
        for(var p:mc.getSingleplayerServer().getPlayerList().getPlayers()){
            var pos=p.position().add(0,1,3);
            com.dynasty.network.DynastyNetwork.CHANNEL.send(net.minecraftforge.network.PacketDistributor.NEAR.with(()->new net.minecraftforge.network.PacketDistributor.TargetPoint(pos.x,pos.y,pos.z,48,p.level().dimension())),new com.dynasty.network.WeaponImpactPacket(2,pos.x,pos.y,pos.z,p.getYRot()));
        }
    });}
    static void camera(Minecraft mc,int stage){
        mc.options.hideGui=true;mc.options.setCameraType(CameraType.FIRST_PERSON);
        if(stage>=10){mc.setCameraEntity(mc.player);mc.options.setCameraType(stage%2==0?CameraType.FIRST_PERSON:CameraType.THIRD_PERSON_BACK);mc.player.setXRot(stage<12?-85:85);return;}
        double x=stage<4?4.5:stage==4?4:stage==5?21:2,y=stage<4?-57:stage==4?-58:stage==5?-59:stage==6?-55:stage==7?-51:-58,z=stage<4?16:stage==4?19:stage==5?11:stage==6?-4:stage==7?-4:10;
        var camera=new ArmorStand(mc.level,x,y,z);camera.setYRot(180);camera.setYHeadRot(180);camera.yHeadRotO=180;camera.setXRot(stage<4?28:stage==7?70:stage==6?0:12);camera.setOldPosAndRot();mc.setCameraEntity(camera);
    }
    @SubscribeEvent public static void render(TickEvent.RenderTickEvent e){
        if(MODE.isEmpty()||done||e.phase!=TickEvent.Phase.END||frameWait!=70||last<0)return;var mc=Minecraft.getInstance();
        try(var image=Screenshot.takeScreenshot(mc.getMainRenderTarget())){
            for(int i=0;i<8;i++){var vat=(WorkshopBlockEntity)mc.level.getBlockEntity(station(i));if(vat==null)throw new AssertionError("Station BE not synced");int target=last==0?0:last==1?1:last==2?vat.recipe().total()/2:vat.recipe().total();if(vat.deposited()!=target)throw new AssertionError("Wrong remote progress "+i);}
            image.writeToFile(OUT.resolve("stage-"+last+".png"));log.add("Stage "+last+" players="+mc.level.players().size()+" all 8 station states match server; FPS="+mc.getFps());frameWait++;
        }catch(Throwable ex){finish(mc,ex);}
    }
    static void finish(Minecraft mc,Throwable ex){if(done)return;done=true;if(ex!=null)ex.printStackTrace();log.add(ex==null?(SOLO?"PASS: isolated single client and integrated server; NOT a multiplayer pass.":"PASS: real TCP peer, workshop sync, remote holder and attack packets; screenshots require visual review."):"FAIL: "+ex);try{Files.createDirectories(OUT);Files.write(OUT.resolve(ex==null?"PASS.txt":"FAIL.txt"),log);}catch(Exception ignored){}mc.setCameraEntity(mc.player);mc.stop();}
}
