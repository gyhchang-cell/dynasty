package com.dynasty.client;

import com.dynasty.dungeon.*;
import com.dynasty.expansion.ExpansionContent;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.screens.*;
import net.minecraft.client.multiplayer.ServerData;
import net.minecraft.client.multiplayer.resolver.ServerAddress;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.network.protocol.game.ServerboundPlayerActionPacket;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.inventory.ChestMenu;
import net.minecraft.world.inventory.ClickType;
import net.minecraft.world.inventory.CraftingMenu;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.entity.ChestBlockEntity;
import net.minecraft.world.level.levelgen.WorldOptions;
import net.minecraft.world.level.levelgen.presets.WorldPresets;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.api.distmarker.Dist;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.CompletableFuture;

/** Disposable real clients: native mining packets, movement, shared chest, crafting and fresh-JVM reload. */
@Mod.EventBusSubscriber(modid="dynasty",value=Dist.CLIENT)
public final class ChenshaArtisanClientQa {
    private static final String ROLE=System.getProperty("dynasty.cod2Qa.role","");
    private static final boolean HOST=ROLE.equals("host"),SOLO=Boolean.getBoolean("dynasty.cod2Qa.solo"),RESUME=Boolean.getBoolean("dynasty.cod2Qa.resume"),SHORTCUT=Boolean.getBoolean("dynasty.cod2Qa.shortcut");
    private static final Path ROOT=Path.of(System.getProperty("dynasty.cod2Qa.output","build/cod2-client/results"));
    private static final int PORT=25589;
    private static final BlockPos ORIGIN=new BlockPos(64,-56,64),CHEST=ORIGIN.offset(52,25,91),TABLE=ORIGIN.offset(55,25,91);
    private static final BlockPos STELE=ORIGIN.offset(ChenshaPiece.returnSteleOffsets().get(2)),LIFT=ORIGIN.offset(41,1,8),LANDING=ORIGIN.offset(41,73,8);
    private static final UUID INSTANCE=ChenshaStructure.instanceId(57,ORIGIN);
    private static final List<BlockPos> WALL=java.util.stream.IntStream.rangeClosed(51,53).boxed()
        .flatMap(x->java.util.stream.IntStream.rangeClosed(25,26).mapToObj(y->ORIGIN.offset(x,y,87))).toList();
    private static final long DEADLINE=System.nanoTime()+600_000_000_000L;
    private static boolean started,finished,acted,reconnected;
    private static int diagnostics,stage=-1,observed=-1,frames,digTicks,digSequence,craftAction;
    private static BlockPos digging;
    private static long reconnectAt;
    private static volatile int columns,serverStage=-1;
    private static CompletableFuture<Void> setup,reload;

    private static int finalStage(){return RESUME?(SHORTCUT?4:3):(SHORTCUT?10:7);}
    private static boolean shortcutOpen(Minecraft mc){
        if(!(mc.level.getBlockEntity(LIFT) instanceof DungeonMechanismBlockEntity lift)||!lift.getBlockState().getValue(DungeonMechanismBlock.ACTIVE))return false;
        for(int n=0;n<4;n++){var state=mc.level.getBlockState(ORIGIN.offset(ChenshaPiece.returnSteleOffsets().get(n)));
            if(!state.is(DungeonContent.SHORTCUT_STELE.get())||state.getValue(DungeonMechanismBlock.OPEN)!=(n==2))return false;
        }return true;
    }
    private static boolean ride(Minecraft mc){
        if(mc.player.getY()<LANDING.getY()-.1){open(mc,LIFT);return false;}
        mc.player.setYRot(0);mc.options.keyLeft.setDown(mc.player.getX()<LANDING.getX()+1.6);
        if(mc.player.getX()<LANDING.getX()+1.6)return false;
        mc.options.keyLeft.setDown(false);require(mc.player.getY()<LANDING.getY()+1,"Lift did not arrive at authored entrance floor");return true;
    }
    private static void require(boolean condition,String message){if(!condition)throw new AssertionError(message);}
    private static boolean ack(int n){return Files.exists(ROOT.resolve(n+"-"+ROLE));}
    private static void publish(int n)throws Exception{stage=n;Files.writeString(ROOT.resolve("stage"),Integer.toString(n));}
    private static void click(Minecraft mc,int slot,int button,ClickType type){mc.gameMode.handleInventoryMouseClick(mc.player.containerMenu.containerId,slot,button,type,mc.player);}
    private static void open(Minecraft mc,BlockPos pos){mc.gameMode.useItemOn(mc.player,InteractionHand.MAIN_HAND,new BlockHitResult(Vec3.atCenterOf(pos),Direction.NORTH,pos,false));}
    private static void connect(Minecraft mc){ConnectScreen.startConnecting(new TitleScreen(),mc,ServerAddress.parseString("127.0.0.1:"+PORT),new ServerData("Disposable artisan QA","127.0.0.1:"+PORT,false),false);}
    private static int count(Minecraft mc,Item item){return mc.player.getInventory().countItem(item);}
    private static int chestPlans(ChestMenu menu){int n=0;for(int slot=0;slot<27;slot++)if(menu.getSlot(slot).getItem().is(DungeonContent.HIGH_GRADE_PLAN.get()))n+=menu.getSlot(slot).getItem().getCount();return n;}
    private static boolean chestEmpty(ChestMenu menu){for(int slot=0;slot<27;slot++)if(!menu.getSlot(slot).getItem().isEmpty())return false;return true;}
    private static int inventorySlot(Minecraft mc,Item item,int first){for(int slot=first;slot<mc.player.containerMenu.slots.size();slot++)if(mc.player.containerMenu.getSlot(slot).getItem().is(item))return slot;return -1;}
    private static void put(Minecraft mc,Item item,int... grid){
        int source=inventorySlot(mc,item,10);require(source>=10,"Craft ingredient missing: "+item);click(mc,source,0,ClickType.PICKUP);
        for(int slot:grid)click(mc,slot,1,ClickType.PICKUP);
        if(!mc.player.containerMenu.getCarried().isEmpty())click(mc,source,0,ClickType.PICKUP);
    }
    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent event){
        if(ROLE.isEmpty()||finished||event.phase!=TickEvent.Phase.END)return;var mc=Minecraft.getInstance();
        try{
            require(System.nanoTime()<DEADLINE,"Artisan QA timed out at stage "+stage+" screen="+mc.screen);
            if(Files.exists(ROOT.resolve("host-FAIL.txt"))||Files.exists(ROOT.resolve("peer-FAIL.txt"))){finish(mc,"Other client failed");return;}
            if(!started&&(mc.screen instanceof TitleScreen||mc.screen instanceof AccessibilityOnboardingScreen)){
                require(mc.gameDirectory.getCanonicalPath().contains("/build/cod2-client/"),"A disposable client directory is mandatory");
                Files.createDirectories(ROOT);require(!Files.exists(ROOT.resolve(ROLE+"-PASS.txt")),"Use fresh result directory");
                if(!HOST&&!Files.exists(ROOT.resolve("listening")))return;started=true;
                mc.options.pauseOnLostFocus=false;mc.options.renderDistance().set(4);mc.options.simulationDistance().set(5);mc.options.framerateLimit().set(30);
                if(!HOST)connect(mc);
                else if(RESUME)mc.createWorldOpenFlows().loadLevel(new TitleScreen(),"artisan-qa");
                else{
                    var rules=new GameRules();rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false,null);rules.getRule(GameRules.RULE_DAYLIGHT).set(false,null);
                    mc.createWorldOpenFlows().createFreshLevel("artisan-qa",new LevelSettings("Disposable artisan QA",GameType.SURVIVAL,false,
                        net.minecraft.world.Difficulty.NORMAL,true,rules,WorldDataConfiguration.DEFAULT),new WorldOptions(57,false,false),
                        r->r.registryOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.FLAT).createWorldDimensions());
                }return;
            }
            if(started&&mc.level==null&&++diagnostics%40==0){
                var ui=mc.screen;
                Files.writeString(ROOT.resolve(ROLE+"-loading.txt"),ui==null?"null":ui.getClass().getName()+"\n"+ui.getTitle().getString()+"\n"+
                    ui.children().stream().map(c->c instanceof net.minecraft.client.gui.components.AbstractWidget w?w.getMessage().getString():c.getClass().getName()).toList());
            }
            if(HOST&&RESUME&&started&&mc.screen instanceof BackupConfirmScreen confirm){
                for(var child:confirm.children())if(child instanceof net.minecraft.client.gui.components.Button button
                    &&button.getMessage().getString().equals(Component.translatable("selectWorld.backupJoinSkipButton").getString())){
                    // This is a fresh copy of our disposable QA save; use vanilla's native confirmation.
                    button.onPress();return;
                }
            }
            if(HOST&&RESUME&&started&&mc.screen instanceof ConfirmScreen confirm
                &&(confirm.getTitle().getString().equals(Component.translatable("selectWorld.warning.experimental.title").getString())
                    ||confirm.getTitle().getString().equals(Component.translatable("selectWorld.backupQuestion.experimental").getString()))){
                for(var child:confirm.children())if(child instanceof net.minecraft.client.gui.components.Button button
                    &&(button.getMessage().getString().equals(net.minecraft.network.chat.CommonComponents.GUI_PROCEED.getString())
                        ||button.getMessage().getString().equals(net.minecraft.network.chat.CommonComponents.GUI_YES.getString()))){
                    button.onPress();return;
                }
            }
            if(reconnectAt!=0){if(System.nanoTime()<reconnectAt)return;reconnectAt=0;reconnected=true;connect(mc);return;}
            if(mc.level==null||mc.player==null)return;
            if(mc.screen instanceof PauseScreen)mc.setScreen(null);
            if(mc.level.getGameTime()%40==0)Files.writeString(ROOT.resolve(ROLE+"-status.txt"),"stage="+stage+" columns="+columns+" serverStage="+serverStage+" screen="+mc.screen+" position="+mc.player.position());
            if(HOST&&setup==null){setup=mc.getSingleplayerServer().submit(()->setup(mc));return;}
            if(HOST){if(!setup.isDone()||columns<24)return;setup.join();
                if(stage<0){Files.writeString(ROOT.resolve("listening"),"Native server ready");publish(0);}
                if(ack(stage)&&(SOLO||Files.exists(ROOT.resolve(stage+"-peer")))){
                    if(stage==finalStage()){Files.writeString(ROOT.resolve("complete"),"All artisan stages observed");finish(mc,null);return;}publish(stage+1);
                }
            }else{if(Files.exists(ROOT.resolve("complete"))){finish(mc,null);return;}if(!Files.exists(ROOT.resolve("stage")))return;stage=Integer.parseInt(Files.readString(ROOT.resolve("stage")).trim());}
            if(observed!=stage){observed=stage;acted=false;frames=0;reload=null;craftAction=0;}
            if(ack(stage))return;
            require(mc.player.isAlive(),"Artisan player died during native entry");
            require(mc.getItemRenderer().getModel(new ItemStack(DungeonContent.HIGH_GRADE_PLAN.get()),mc.level,mc.player,0)!=mc.getModelManager().getMissingModel(),"High-grade plan has a missing item model");
            for(var item:List.of(DungeonContent.HIGH_GRADE_PLAN.get(),ExpansionContent.item("qimen_gear"))){
                var model=mc.getItemRenderer().getModel(new ItemStack(item),mc.level,mc.player,0);
                require(!model.getParticleIcon().contents().name().equals(net.minecraft.client.renderer.texture.MissingTextureAtlasSprite.getLocation()),"Missing plan/gear atlas texture: "+item);
            }
            require(!Component.translatable("item.dynasty.high_grade_mechanism_plan").getString().equals("item.dynasty.high_grade_mechanism_plan"),"Plan translation missing");
            if(RESUME){
                if(stage==0){
                    if(SHORTCUT){if(!shortcutOpen(mc))return;require(mc.player.getY()>=LANDING.getY()-.1,"Native saved player lost entrance-floor arrival");}
                    else{for(var p:WALL)if(!mc.level.getBlockState(p).isAir())return;
                    require(mc.level.getBlockState(TABLE).is(Blocks.CRAFTING_TABLE),"Saved workbench missing");}
                    require(count(mc,DungeonContent.HIGH_GRADE_PLAN.get())==0,"Consumed plan returned after fresh JVM/world reload");
                    require(count(mc,ExpansionContent.item("qimen_gear"))==(HOST?8:0),"Saved native crafted gear ownership/count changed");
                }else if(stage==1){if(!(mc.player.containerMenu instanceof ChestMenu menu)){open(mc,CHEST);return;}if(!chestEmpty(menu))throw new AssertionError("Looted chest refilled after real server restart");
                }else if(stage==2){if(!HOST&&!reconnected){mc.player.closeContainer();mc.level.disconnect();mc.clearLevel(new TitleScreen());reconnectAt=System.nanoTime()+1_000_000_000L;return;}
                    if(!(mc.player.containerMenu instanceof ChestMenu menu)){open(mc,CHEST);return;}require(chestEmpty(menu),"Reconnection replayed chest contents");
                }else if(stage==3){if(!acted){reload=mc.reloadResourcePacks();acted=true;return;}if(!reload.isDone())return;reload.join();require(count(mc,ExpansionContent.item("qimen_gear"))==(HOST?8:0),"Reload duplicated or lost crafted gear");}
                else if(stage==4){if(!shortcutOpen(mc)||!ride(mc))return;}
            }else if(stage==0){
                boolean open=true;for(var p:WALL)open&=mc.level.getBlockState(p).isAir();
                if(!open){if(!HOST)return;
                    if(digging==null||mc.level.getBlockState(digging).isAir()){
                        digging=WALL.stream().filter(p->!mc.level.getBlockState(p).isAir()).findFirst().orElseThrow();digTicks=0;
                        require(mc.level.getBlockState(digging).is(Blocks.CRACKED_STONE_BRICKS),"Authored entrance isn't the breakable brick");
                        mc.getConnection().send(new ServerboundPlayerActionPacket(ServerboundPlayerActionPacket.Action.START_DESTROY_BLOCK,digging,Direction.NORTH,++digSequence));
                    }
                    if(++digTicks==40)mc.getConnection().send(new ServerboundPlayerActionPacket(ServerboundPlayerActionPacket.Action.STOP_DESTROY_BLOCK,digging,Direction.NORTH,++digSequence));
                    mc.player.swing(InteractionHand.MAIN_HAND);return;
                }
            }else if(stage==1){
                mc.player.setYRot(0);mc.player.setXRot(0);mc.options.keyUp.setDown(mc.player.getZ()<ORIGIN.getZ()+88.5);
                if(mc.player.getZ()<ORIGIN.getZ()+88.5)return;
                mc.options.keyUp.setDown(false);require(mc.player.getY()>=ORIGIN.getY()+24.9,"Player fell instead of walking through the hidden entrance");
            }else if(stage==2){
                if(!(mc.player.containerMenu instanceof ChestMenu menu)){open(mc,CHEST);return;}
                require(chestPlans(menu)==1,"Both native viewers must initially see one shared high-grade plan");
            }else if(stage==3){
                if(!(mc.player.containerMenu instanceof ChestMenu menu)){open(mc,CHEST);return;}
                if(HOST&&count(mc,DungeonContent.HIGH_GRADE_PLAN.get())==0){for(int slot=0;slot<27;slot++)if(menu.getSlot(slot).getItem().is(DungeonContent.HIGH_GRADE_PLAN.get())){click(mc,slot,0,ClickType.QUICK_MOVE);return;}}
                if(chestPlans(menu)!=0)return;require(count(mc,DungeonContent.HIGH_GRADE_PLAN.get())==(HOST?1:0),"Shared chest duplicated/lost plan ownership");
            }else if(stage==4){
                if(!(mc.player.containerMenu instanceof ChestMenu menu)){open(mc,CHEST);return;}
                if(HOST&&!chestEmpty(menu)){for(int slot=0;slot<27;slot++)if(!menu.getSlot(slot).getItem().isEmpty()){click(mc,slot,0,ClickType.QUICK_MOVE);return;}}
                if(!chestEmpty(menu))return;
            }else if(stage==5){
                if(!acted){mc.player.closeContainer();reload=mc.reloadResourcePacks();acted=true;return;}if(!reload.isDone())return;reload.join();
                if(!HOST&&!reconnected){mc.level.disconnect();mc.clearLevel(new TitleScreen());reconnectAt=System.nanoTime()+1_000_000_000L;return;}
                if(!(mc.player.containerMenu instanceof ChestMenu menu)){open(mc,CHEST);return;}require(chestEmpty(menu),"Resource reload/reconnect refilled chest");
            }else if(stage==6){
                if(!(mc.player.containerMenu instanceof CraftingMenu)){mc.player.closeContainer();open(mc,TABLE);return;}
                if(HOST){
                    if(craftAction==0){
                        if(count(mc,Items.IRON_INGOT)<4||count(mc,Items.COPPER_INGOT)<2||count(mc,Items.REDSTONE)<1)return;
                        put(mc,DungeonContent.HIGH_GRADE_PLAN.get(),1);put(mc,Items.IRON_INGOT,2,3,4,5);put(mc,Items.COPPER_INGOT,6,7);put(mc,Items.REDSTONE,8);craftAction=1;return;
                    }
                    if(craftAction==1){if(!mc.player.containerMenu.getSlot(0).getItem().is(ExpansionContent.item("qimen_gear")))return;click(mc,0,0,ClickType.QUICK_MOVE);craftAction=2;return;}
                    if(count(mc,ExpansionContent.item("qimen_gear"))!=8)return;
                    if(!mc.player.getMainHandItem().is(ExpansionContent.item("qimen_gear"))){int slot=inventorySlot(mc,ExpansionContent.item("qimen_gear"),10);require(slot>=10,"Native craft didn't enter inventory");click(mc,slot,0,ClickType.SWAP);return;}
                    require(count(mc,DungeonContent.HIGH_GRADE_PLAN.get())==0,"Native craft did not consume its unique plan");
                }else{
                    boolean held=false;for(var p:mc.level.players())if(p.getGameProfile().getName().equals("DungeonHost")&&p.getMainHandItem().is(ExpansionContent.item("qimen_gear"))&&p.getMainHandItem().getCount()==8)held=true;
                    if(!held)return;require(count(mc,ExpansionContent.item("qimen_gear"))==0,"Observer received a duplicate crafted reward");
                }
                if(!Files.exists(ROOT.resolve("native-craft.txt")))return;
            }else if(stage==7){mc.player.closeContainer();require(count(mc,ExpansionContent.item("qimen_gear"))==(HOST?8:0),"Final gear count changed");}
            else if(stage==8){
                if(!acted&&HOST){
                    if(!mc.player.getMainHandItem().is(Items.IRON_PICKAXE)){
                        for(int slot=0;slot<9;slot++)if(mc.player.getInventory().getItem(slot).is(Items.IRON_PICKAXE)){
                            mc.player.getInventory().selected=slot;
                            mc.getConnection().send(new net.minecraft.network.protocol.game.ServerboundSetCarriedItemPacket(slot));break;
                        }return;
                    }
                    mc.getConnection().send(new ServerboundPlayerActionPacket(ServerboundPlayerActionPacket.Action.START_DESTROY_BLOCK,STELE,Direction.NORTH,++digSequence));acted=true;
                }
                if(!shortcutOpen(mc))return;
                require(mc.level.getBlockState(STELE).getCollisionShape(mc.level,STELE).isEmpty(),"Struck corner retained client collision");
            }else if(stage==9){if(!shortcutOpen(mc)||!ride(mc))return;
            }else if(stage==10){
                if(!acted){reload=mc.reloadResourcePacks();acted=true;return;}if(!reload.isDone())return;reload.join();
                if(!HOST&&!reconnected){mc.level.disconnect();mc.clearLevel(new TitleScreen());reconnectAt=System.nanoTime()+1_000_000_000L;return;}
                if(!shortcutOpen(mc))return;require(mc.player.getY()>=LANDING.getY()-.1,"Reconnection lost entrance-floor landing");
            }
            if(++frames<5)return;
            if(stage==2||stage==3||stage==6||SHORTCUT&&(stage==8||stage==9||RESUME&&stage==4)||RESUME&&stage==1)net.minecraft.client.Screenshot.grab(mc.gameDirectory,"artisan-"+stage+"-"+ROLE+".png",mc.getMainRenderTarget(),c->{});
            Files.writeString(ROOT.resolve(stage+"-"+ROLE),"PASS stage="+stage+" tick="+mc.level.getGameTime()+" player="+mc.player.getUUID()+"\n");
        }catch(Throwable failure){finish(mc,failure.toString());}
    }
    private static void setup(Minecraft mc){
        var server=mc.getSingleplayerServer();var level=server.overworld();
        if(RESUME)columns=24;else level.setDefaultSpawnPos(ORIGIN.offset(52,25,84),0);
        for(var player:server.getPlayerList().getPlayers())prepare(player);
        if(!SOLO)try{server.setUsesAuthentication(false);server.getConnection().startTcpServerListener(java.net.InetAddress.getByName("127.0.0.1"),PORT);}catch(Exception e){throw new RuntimeException(e);}
    }
    private static void prepare(ServerPlayer p){
        p.setGameMode(GameType.SURVIVAL);p.setNoGravity(!RESUME&&columns<24);
        if(SHORTCUT&&RESUME&&stage<=0){p.inventoryMenu.broadcastChanges();return;}
        if(SHORTCUT&&!RESUME&&stage>=9){p.teleportTo(LANDING.getX()+1.6,LANDING.getY(),LANDING.getZ()+.5);return;}
        p.teleportTo(ORIGIN.getX()+(p.getGameProfile().getName().equals("DungeonHost")?51.5:53.5),ORIGIN.getY()+25,ORIGIN.getZ()+(stage<1&&!RESUME?84.5:88.5));
        p.setYRot(0);p.setXRot(0);
        if(!RESUME&&stage<1){p.getInventory().clearContent();p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(Items.IRON_PICKAXE));p.setHealth(20);}
        p.inventoryMenu.broadcastChanges();
    }
    @SubscribeEvent public static void joined(PlayerEvent.PlayerLoggedInEvent event){if(HOST&&event.getEntity() instanceof ServerPlayer p)prepare(p);}
    @SubscribeEvent public static void serverTick(TickEvent.ServerTickEvent event){
        if(!HOST||finished||setup==null||!setup.isDone()||event.phase!=TickEvent.Phase.END)return;
        try{
            var level=event.getServer().overworld();
            if(!RESUME&&columns<24){
                int x=columns%4,z=columns/4;var chunk=new ChunkPos(ORIGIN.offset(x*16,0,z*16));level.getChunk(chunk.x,chunk.z);
                var clip=new BoundingBox(chunk.getMinBlockX(),level.getMinBuildHeight(),chunk.getMinBlockZ(),chunk.getMaxBlockX(),level.getMaxBuildHeight()-1,chunk.getMaxBlockZ());
                new ChenshaPiece(ORIGIN,x,z,INSTANCE).postProcess(level,level.structureManager(),level.getChunkSource().getGenerator(),net.minecraft.util.RandomSource.create(57),clip,chunk,ORIGIN);
                if(++columns==24)for(var p:event.getServer().getPlayerList().getPlayers())prepare(p);return;
            }
            if(SHORTCUT&&stage!=serverStage){
                if(!RESUME&&stage==8){
                    for(var p:event.getServer().getPlayerList().getPlayers()){
                        p.teleportTo(STELE.getX()+(p.getGameProfile().getName().equals("DungeonHost")?.5:-1.5),STELE.getY(),STELE.getZ()-1.5);
                        p.setYRot(0);p.setXRot(15);p.setHealth(20);
                        for(int slot=0;slot<9;slot++)if(p.getInventory().getItem(slot).is(Items.IRON_PICKAXE)){p.getInventory().selected=slot;break;}
                        p.inventoryMenu.broadcastChanges();
                    }
                }
                if(!RESUME&&stage==9||RESUME&&stage==4){
                    for(var p:event.getServer().getPlayerList().getPlayers()){p.teleportTo(LIFT.getX()+1.5,LIFT.getY(),LIFT.getZ()+.5);p.setHealth(20);}
                }
                if(RESUME&&stage==1)for(var p:event.getServer().getPlayerList().getPlayers())prepare(p);
                if(stage!=6)serverStage=stage;
            }
            if(!RESUME&&stage==6&&serverStage!=6){serverStage=6;
                for(var p:event.getServer().getPlayerList().getPlayers())if(p.getGameProfile().getName().equals("DungeonHost")){
                    p.getInventory().add(new ItemStack(Items.IRON_INGOT,4));p.getInventory().add(new ItemStack(Items.COPPER_INGOT,2));p.getInventory().add(new ItemStack(Items.REDSTONE));p.inventoryMenu.broadcastChanges();
                }
            }
            if(!RESUME&&stage==6)for(var p:event.getServer().getPlayerList().getPlayers())if(p.getGameProfile().getName().equals("DungeonHost")
                &&p.getInventory().countItem(ExpansionContent.item("qimen_gear"))==8&&p.getInventory().countItem(DungeonContent.HIGH_GRADE_PLAN.get())==0){
                require(((ChestBlockEntity)level.getBlockEntity(CHEST)).isEmpty(),"Server chest changed during crafting");
                Files.writeString(ROOT.resolve("native-craft.txt"),"Native server inventory: eight gears, consumed plan, empty chest\n");
            }
        }catch(Throwable failure){finish(Minecraft.getInstance(),failure.toString());}
    }
    private static void finish(Minecraft mc,String failure){
        if(finished)return;finished=true;mc.options.keyUp.setDown(false);mc.options.keyLeft.setDown(false);
        try{Files.createDirectories(ROOT);Files.writeString(ROOT.resolve(ROLE+(failure==null?"-PASS.txt":"-FAIL.txt")),failure==null?
            ("All "+(finalStage()+1)+" native "+(SHORTCUT?"artisan/shortcut":"artisan")+(RESUME?" fresh-JVM restart":" client")+" stages passed"):failure);}catch(Exception ignored){}
        mc.execute(mc::stop);
    }
    private ChenshaArtisanClientQa(){}
}
