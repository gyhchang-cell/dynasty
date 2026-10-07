package com.dynasty.client;

import com.dynasty.dungeon.*;
import com.dynasty.worldevent.*;
import com.dynasty.worldevent.client.WorldEventVisuals;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.screens.*;
import net.minecraft.client.multiplayer.ServerData;
import net.minecraft.client.multiplayer.resolver.ServerAddress;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.item.*;
import net.minecraft.world.level.*;
import net.minecraft.world.level.levelgen.WorldOptions;
import net.minecraft.world.level.levelgen.presets.WorldPresets;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.CompletableFuture;

/** Disposable actual TCP client verification. No screenshots or game-world artifacts belong in Git. */
@Mod.EventBusSubscriber(modid="dynasty",value=Dist.CLIENT)
public final class WorldEventClientQa {
    private static final String ROLE=System.getProperty("dynasty.cod2Qa.role","");
    private static final boolean HOST=ROLE.equals("host"),SOLO=Boolean.getBoolean("dynasty.cod2Qa.solo");
    private static final Path ROOT=Path.of(System.getProperty("dynasty.cod2Qa.output","build/world-qa"));
    private static final int PORT=25589;
    private static final net.minecraft.resources.ResourceKey<Level> TARGET=net.minecraft.resources.ResourceKey.create(Registries.DIMENSION,new net.minecraft.resources.ResourceLocation("dynasty:underworld"));
    private static final BlockPos CENTER=new BlockPos(0,-60,0),CRUSHER=new BlockPos(-2,-61,2),CORE=new BlockPos(-4,-61,2);
    private static final long DEADLINE=System.nanoTime()+600_000_000_000L;
    private static boolean started,finished,acted,reconnected;
    private static volatile int stage=-1,serverStage=-1;
    private static int observed=-1,frames,captured=-1;
    private static long reconnectAt;
    private static CompletableFuture<Void> setup,reload;
    private static UUID active;
    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent e){
        if(ROLE.isEmpty()||finished||e.phase!=TickEvent.Phase.END)return;var mc=Minecraft.getInstance();
        try{
            if(System.nanoTime()>DEADLINE)throw new AssertionError("World client timeout at stage "+stage+" screen="+mc.screen);
            if(Files.exists(ROOT.resolve("host-FAIL.txt"))||Files.exists(ROOT.resolve("peer-FAIL.txt"))){finish(mc,"Other client failed");return;}
            if(!started&&(mc.screen instanceof TitleScreen||mc.screen instanceof AccessibilityOnboardingScreen)){
                if(!mc.gameDirectory.getCanonicalPath().contains("/build/cod2-client/"))throw new AssertionError("Disposable directory required");
                Files.createDirectories(ROOT);if(Files.exists(ROOT.resolve("0-"+ROLE)))throw new AssertionError("Fresh output required");
                if(!HOST&&!Files.exists(ROOT.resolve("listening")))return;started=true;mc.options.pauseOnLostFocus=false;
                mc.options.renderDistance().set(3);mc.options.simulationDistance().set(5);mc.options.framerateLimit().set(30);
                if(!HOST)connect(mc);else{
                    var rules=new GameRules();rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false,null);rules.getRule(GameRules.RULE_DAYLIGHT).set(false,null);
                    mc.createWorldOpenFlows().createFreshLevel("world-qa-"+System.currentTimeMillis(),new LevelSettings("Disposable event QA",GameType.SURVIVAL,false,net.minecraft.world.Difficulty.NORMAL,true,rules,WorldDataConfiguration.DEFAULT),
                        new WorldOptions(57,false,false),r->r.registryOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.FLAT).createWorldDimensions());
                }return;
            }
            if(reconnectAt!=0){if(System.nanoTime()<reconnectAt)return;reconnectAt=0;reconnected=true;connect(mc);return;}
            if(mc.level==null||mc.player==null)return;if(mc.screen!=null)mc.setScreen(null);
            if(HOST&&setup==null){setup=mc.getSingleplayerServer().submit(()->setup(mc));return;}
            if(HOST){
                if(!setup.isDone())return;setup.join();if(!Files.exists(ROOT.resolve("listening")))Files.writeString(ROOT.resolve("listening"),"127.0.0.1:"+PORT);
                if(stage<0)publish(0);if(ack(stage)&&(SOLO||Files.exists(ROOT.resolve(stage+"-peer")))){
                    if(stage==9){Files.writeString(ROOT.resolve("complete"),"Ten actual world client stages observed");finish(mc,null);return;}publish(stage+1);
                }
            }else{if(Files.exists(ROOT.resolve("complete"))){finish(mc,null);return;}if(!Files.exists(ROOT.resolve("stage")))return;stage=Integer.parseInt(Files.readString(ROOT.resolve("stage")).trim());}
            if(observed!=stage){observed=stage;acted=false;frames=0;}if(ack(stage))return;
            if(mc.level.getGameTime()%40==0)Files.writeString(ROOT.resolve(ROLE+"-status"),"stage="+stage+" serverStage="+serverStage+" dimension="+mc.level.dimension().location()+" gameTime="+mc.level.getGameTime()+"\n");
            if(stage==0){
                for(var item:WorldEventItems.ITEMS.getEntries())require(mc.getItemRenderer().getModel(new ItemStack(item.get()),mc.level,mc.player,0)!=mc.getModelManager().getMissingModel(),"Missing real event reward item model "+item.getId());
                require(WorldEventVisuals.activeStates()==0,"Event visual state leaked before start");
            }else if(stage==1){
                if(!WorldEventVisuals.has("yinbing_jiedao")||WorldEventVisuals.phantomCount()!=8||!WorldEventVisuals.processionFog())return;
                long actual=java.util.stream.StreamSupport.stream(mc.level.entitiesForRendering().spliterator(),false).filter(entity->entity instanceof com.dynasty.blueprint.TemplateMob m&&m.kind()==com.dynasty.blueprint.TemplateMob.Kind.GHOST).count();
                if(actual<6)return;require(WorldEventVisuals.activeStates()<=3,"Visual state cap exceeded");
            }else if(stage==2){
                if(!acted){reload=mc.reloadResourcePacks();acted=true;return;}if(!reload.isDone())return;reload.join();
                if(!WorldEventVisuals.has("yinbing_jiedao")||WorldEventVisuals.phantomCount()!=8||!WorldEventVisuals.processionFog())return;
            }else if(stage==3){
                if(!HOST&&!reconnected){mc.level.disconnect();mc.clearLevel(new TitleScreen());reconnectAt=System.nanoTime()+1_000_000_000L;return;}
                if(!WorldEventVisuals.has("yinbing_jiedao")||WorldEventVisuals.phantomCount()!=8||!WorldEventVisuals.processionFog())return;
            }else if(stage==4){if(WorldEventVisuals.activeStates()!=0||WorldEventVisuals.phantomCount()!=0)return;
            }else if(stage==5){
                if(!WorldEventVisuals.has("xuanniao_zhige")||WorldEventVisuals.celestialDraws()<5)return;
                require(mc.player.hasEffect(MobEffects.LUCK)&&mc.player.hasEffect(MobEffects.DAMAGE_BOOST),"Real celestial buff packets missing");
                require(mc.player.getMainHandItem().is(Items.IRON_SWORD)&&mc.player.getMainHandItem().getDamageValue()==125,"Weapon repair not synchronized");
            }else if(stage==6){if(WorldEventVisuals.activeStates()!=0)return;
            }else if(stage==7){
                if(!(mc.level.getBlockEntity(CRUSHER) instanceof DungeonMechanismBlockEntity be)||!be.validBinding())return;
                require(be.getRenderBoundingBox().maxY>=CRUSHER.getY()+4,"Moving hammer render bounds clipped");
                for(var p:List.of(CRUSHER,new BlockPos(5,-61,2),new BlockPos(6,-61,2),new BlockPos(7,-61,2),new BlockPos(8,-61,2),new BlockPos(9,-61,2)))
                    if(mc.getBlockRenderer().getBlockModel(mc.level.getBlockState(p))==mc.getModelManager().getMissingModel())return;
                if(frames<45){frames++;return;}
            }else if(stage==8){if(!WorldEventVisuals.hasActive("xuanniao_zhige")||WorldEventVisuals.celestialDraws()<5)return;
            }else if(stage==9){
                if(!mc.level.dimension().equals(TARGET))return;if(WorldEventVisuals.activeStates()!=0||WorldEventVisuals.phantomCount()!=0||WorldEventVisuals.processionFog())return;
            }
            if(++frames<8)return;
            if(List.of(1,5,7).contains(stage)&&captured!=stage){captured=stage;net.minecraft.client.Screenshot.grab(mc.gameDirectory,"events-"+stage+"-"+ROLE+".png",mc.getMainRenderTarget(),message->{});}
            Files.writeString(ROOT.resolve(stage+"-"+ROLE),"PASS stage="+stage+" tick="+mc.level.getGameTime()+" player="+mc.player.getUUID()+"\n");
        }catch(Throwable failure){finish(mc,failure.toString());}
    }
    private static void setup(Minecraft mc){
        var server=mc.getSingleplayerServer();var level=server.overworld();level.setDefaultSpawnPos(CENTER,0);level.setDayTime(6000);
        for(var player:server.getPlayerList().getPlayers())prepare(player);
        if(!SOLO)try{server.setUsesAuthentication(false);server.getConnection().startTcpServerListener(java.net.InetAddress.getByName("127.0.0.1"),PORT);}catch(Exception e){throw new RuntimeException(e);}
    }
    @SubscribeEvent public static void joined(net.minecraftforge.event.entity.player.PlayerEvent.PlayerLoggedInEvent e){if(HOST&&e.getEntity() instanceof net.minecraft.server.level.ServerPlayer p)prepare(p);}
    private static void prepare(net.minecraft.server.level.ServerPlayer p){
        p.setGameMode(GameType.SURVIVAL);p.teleportTo(p.server.overworld(),p.getGameProfile().getName().equals("DungeonHost")?-.5:1.5,-60,-5.5,0,0);p.getFoodData().setFoodLevel(20);p.setHealth(20);
    }
    @SubscribeEvent public static void serverTick(TickEvent.ServerTickEvent e){
        if(!HOST||setup==null||!setup.isDone()||e.phase!=TickEvent.Phase.END||stage==serverStage)return;
        final int stage=WorldEventClientQa.stage;
        var server=Minecraft.getInstance().getSingleplayerServer();var level=server.overworld();serverStage=stage;
        com.dynasty.Dynasty.LOGGER.info("[cod2 world QA] server stage {}",stage);
        var owner=server.getPlayerList().getPlayers().stream().filter(p->p.getGameProfile().getName().equals("DungeonHost")).findFirst().orElseThrow();
        if(stage==1||stage==5||stage==8){
            if(stage==5||stage==8)for(var p:server.getPlayerList().getPlayers()){var sword=new ItemStack(Items.IRON_SWORD);sword.setDamageValue(200);p.getInventory().selected=0;p.setItemInHand(InteractionHand.MAIN_HAND,sword);p.inventoryMenu.broadcastChanges();}
            String id=stage==1?"yinbing_jiedao":"xuanniao_zhige";
            require(server.getCommands().performPrefixedCommand(owner.createCommandSourceStack().withPermission(4),"dynasty event start "+id)==1,"Real debug command failed "+id);
            active=WorldEventStore.get(level).instances.values().stream().filter(i->i.active()&&i.definition.getPath().equals(id)).map(i->i.uuid).findFirst().orElseThrow();
            if(stage==5||stage==8){var center=WorldEventStore.get(level).instances.get(active).center;
                for(var p:server.getPlayerList().getPlayers())p.teleportTo(level,center.getX()+(p.getGameProfile().getName().equals("DungeonHost")?.5:2.5),center.getY(),center.getZ()-40.5,30,-35);
            }
        }
        if(stage==4||stage==6)require(server.getCommands().performPrefixedCommand(owner.createCommandSourceStack().withPermission(4),"dynasty event stop "+active)==1,"Real stop failed");
        if(stage==7){
            var instance=UUID.randomUUID();var positions=List.of(CRUSHER,new BlockPos(5,-61,2),new BlockPos(6,-61,2),new BlockPos(7,-61,2),new BlockPos(8,-61,2),new BlockPos(9,-61,2));
            var blocks=List.of(DungeonContent.CRUSHER.get(),DungeonContent.CONVEYOR.get(),DungeonContent.STEAM.get(),DungeonContent.MINE.get(),DungeonContent.ARROW_RAIN.get(),DungeonContent.WIND_FIELD.get());
            var profiles=DungeonTrapProfile.values();level.setBlockAndUpdate(CORE,DungeonContent.CORE.get().defaultBlockState());var core=(DungeonMechanismBlockEntity)level.getBlockEntity(CORE);
            core.configure(instance,"qa","core",CORE,-1,positions);core.configureRoom(0,false,CORE,CORE.offset(15,4,6));
            for(int n=0;n<positions.size();n++){var pos=positions.get(n);level.setBlockAndUpdate(pos,blocks.get(n).defaultBlockState());((DungeonMechanismBlockEntity)level.getBlockEntity(pos)).configure(instance,"qa",profiles[n].id,CORE,-1,List.of());}
            for(var p:server.getPlayerList().getPlayers())p.teleportTo(level,p.getGameProfile().getName().equals("DungeonHost")?-.5:1.5,-60,-4.5,25,-10);
        }
        if(stage==9){
            var nether=server.getLevel(TARGET);require(nether!=null,"Existing Dynasty underworld unavailable");var landing=new BlockPos(0,80,0);nether.getChunkAt(landing);
            for(int x=-2;x<=2;x++)for(int z=-2;z<=2;z++){nether.setBlockAndUpdate(landing.offset(x,-1,z),net.minecraft.world.level.block.Blocks.STONE.defaultBlockState());for(int y=0;y<=3;y++)nether.setBlockAndUpdate(landing.offset(x,y,z),net.minecraft.world.level.block.Blocks.AIR.defaultBlockState());}
            for(var p:List.copyOf(server.getPlayerList().getPlayers())){
                p.teleportTo(nether,p.getGameProfile().getName().equals("DungeonHost")?-.5:1.5,80,.5,0,0);
                require(p.level().dimension().equals(TARGET),"Existing portal/ritual dimension policy rejected QA destination");
                com.dynasty.Dynasty.LOGGER.info("[cod2 world QA] transferred {} to {}",p.getGameProfile().getName(),p.level().dimension().location());
            }
        }
    }
    private static void require(boolean value,String reason){if(!value)throw new AssertionError(reason);}
    private static boolean ack(int s){return Files.exists(ROOT.resolve(s+"-"+ROLE));}
    private static void publish(int s)throws Exception{stage=s;var temp=ROOT.resolve("stage-next");Files.writeString(temp,Integer.toString(s));Files.move(temp,ROOT.resolve("stage"),StandardCopyOption.REPLACE_EXISTING,StandardCopyOption.ATOMIC_MOVE);}
    private static void connect(Minecraft mc){String address="127.0.0.1:"+PORT;ConnectScreen.startConnecting(new TitleScreen(),mc,ServerAddress.parseString(address),new ServerData("Disposable world QA",address,false),false);}
    private static void finish(Minecraft mc,String reason){finished=true;try{Files.createDirectories(ROOT);Files.writeString(ROOT.resolve(ROLE+(reason==null?"-PASS.txt":"-FAIL.txt")),reason==null?"All ten world client stages passed\n":reason+"\n");}catch(Exception e){e.printStackTrace();}mc.stop();}
}
