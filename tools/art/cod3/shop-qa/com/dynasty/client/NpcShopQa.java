package com.dynasty.client;

import com.dynasty.cod3.*;
import com.dynasty.expansion.*;
import net.minecraft.client.*;
import net.minecraft.client.gui.screens.*;
import net.minecraft.core.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.*;
import net.minecraft.world.entity.decoration.ArmorStand;
import net.minecraft.world.item.*;
import net.minecraft.world.level.*;
import net.minecraft.world.level.levelgen.*;
import net.minecraft.world.level.levelgen.presets.WorldPresets;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.lwjgl.glfw.GLFW;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.CompletableFuture;

/** One muted disposable client: actual networking, live renderer, GUI and integrated-server transactions. */
@Mod.EventBusSubscriber(modid="dynasty",value=Dist.CLIENT)
public final class NpcShopQa {
    static final Path OUT=Path.of(System.getProperty("dynasty.npcShopQa.output","build/npc-shop-unset"));
    static boolean started,done,art;static int phase,settled;static CompletableFuture<List<Integer>> checks;static List<Integer> ids;
    static CompletableFuture<Void> change;static final long DEADLINE=System.nanoTime()+300_000_000_000L;
    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent event){
        if(!Boolean.getBoolean("dynasty.npcShopQa")||done||event.phase!=TickEvent.Phase.END)return;
        var mc=Minecraft.getInstance();
        try{
            GLFW.glfwHideWindow(mc.getWindow().getWindow());mc.options.getSoundSourceOptionInstance(net.minecraft.sounds.SoundSource.MASTER).set(0.0);
            if(System.nanoTime()>DEADLINE)throw new AssertionError("QA timeout phase "+phase);
            if(mc.getOverlay()!=null)return;
            if(mc.screen instanceof AccessibilityOnboardingScreen)mc.setScreen(new TitleScreen());
            if(!started&&mc.screen instanceof TitleScreen){
                Files.createDirectories(OUT);started=true;mc.options.pauseOnLostFocus=false;mc.options.renderDistance().set(3);mc.options.framerateLimit().set(40);mc.options.guiScale().set(2);
                var rules=new GameRules();rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false,null);rules.getRule(GameRules.RULE_DAYLIGHT).set(false,null);
                mc.createWorldOpenFlows().createFreshLevel("npc-shop-"+System.currentTimeMillis(),new LevelSettings("Disposable NPC QA",GameType.CREATIVE,false,net.minecraft.world.Difficulty.PEACEFUL,true,rules,WorldDataConfiguration.DEFAULT),new WorldOptions(42,false,false),r->r.registryOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.FLAT).createWorldDimensions());return;
            }
            if(mc.level==null||mc.player==null)return;
            if(checks==null){checks=mc.getSingleplayerServer().submit(()->NpcShopChecks.run(mc.getSingleplayerServer().overworld()));return;}
            if(!checks.isDone())return;ids=checks.join();
            if(change!=null){if(!change.isDone())return;change.join();change=null;settled=0;return;}
            if(!art){art=true;NpcShopArt.drawAll(OUT);Files.write(OUT.resolve("server-PASS.txt"),NpcShopChecks.LOG);}
            if(phase==0){
                for(int id:ids){var e=mc.level.getEntity(id);if(!(e instanceof DynastyNpcEntity npc)||!(mc.getEntityRenderDispatcher().getRenderer(npc) instanceof Cod3NpcRenderer))return;}
                var camera=new ArmorStand(mc.level,0,-59.5,12);camera.setYRot(180);camera.setXRot(8);camera.setYHeadRot(180);camera.setOldPosAndRot();mc.setCameraEntity(camera);mc.options.hideGui=true;
                if(++settled<30)return;shot("world-npcs");mc.setCameraEntity(mc.player);mc.options.hideGui=false;
                change=mc.getSingleplayerServer().submit(()->{var p=mc.getSingleplayerServer().getPlayerList().getPlayers().get(0);p.teleportTo(p.serverLevel(),0,-60,3,180,0);p.getInventory().clearContent();});phase=1;return;
            }
            if(phase==1){
                var npc=(DynastyNpcEntity)mc.level.getEntity(ids.get(0));mc.gameMode.interact(mc.player,npc,InteractionHand.MAIN_HAND);phase=2;settled=0;return;
            }
            if(phase==2){if(!(mc.screen instanceof NpcTradingScreens.Trades)||mc.player.containerMenu instanceof NpcTradeMenu m&&m.getOffers().isEmpty())return;
                if(++settled<15)return;shot("trade-native");mc.gameMode.handleInventoryButtonClick(mc.player.containerMenu.containerId,1);phase=3;settled=0;return;}
            if(phase==3){if(!(mc.screen instanceof NpcTradingScreens.Services))return;
                change=mc.getSingleplayerServer().submit(()->{var p=mc.getSingleplayerServer().getPlayerList().getPlayers().get(0);var m=(NpcServiceMenu)p.containerMenu;m.getSlot(0).set(NpcShopChecks.gear());m.getSlot(1).set(NpcShopChecks.coins(64));m.broadcastChanges();});phase=4;return;}
            if(phase==4){if(++settled<15)return;shot("repair-native");mc.gameMode.handleInventoryButtonClick(mc.player.containerMenu.containerId,20);phase=5;settled=0;return;}
            if(phase==5){if(mc.player.containerMenu.getSlot(2).getItem().isEmpty())return;
                NpcShopChecks.require(mc.player.containerMenu.getSlot(2).getItem().getDamageValue()==0&&mc.player.containerMenu.getSlot(1).getItem().getCount()==48,"client/server sync paid repair result via real container button packet");
                if(++settled<15)return;shot("repair-result-native");mc.gameMode.handleInventoryButtonClick(mc.player.containerMenu.containerId,2);phase=6;settled=0;return;}
            if(phase==6){if(!(mc.player.containerMenu instanceof NpcServiceMenu m)||m.page()!=2)return;
                change=mc.getSingleplayerServer().submit(()->{var p=mc.getSingleplayerServer().getPlayerList().getPlayers().get(0);var menu=(NpcServiceMenu)p.containerMenu;menu.quickMoveStack(p,2);menu.getSlot(0).set(new ItemStack(Items.DIAMOND_CHESTPLATE));menu.broadcastChanges();});phase=7;return;}
            if(phase==7){if(++settled<15)return;shot("enchant-native");mc.gameMode.handleInventoryButtonClick(mc.player.containerMenu.containerId,20);phase=8;settled=0;return;}
            if(phase==8){if(mc.player.containerMenu.getSlot(2).getItem().isEmpty())return;
                NpcShopChecks.require(mc.player.containerMenu.getSlot(2).getItem().isEnchanted()&&mc.player.containerMenu.getSlot(1).getItem().getCount()==16,"client/server sync paid enchantment output via real packet");
                if(++settled<15)return;shot("enchant-result-native");mc.gameMode.handleInventoryButtonClick(mc.player.containerMenu.containerId,0);phase=9;settled=0;return;}
            if(phase==9){if(!(mc.screen instanceof NpcTradingScreens.Trades))return;
                if(++settled<15)return;shot("return-trade-native");
                for(var egg:NpcContent.EGGS){var s=new ItemStack(egg.get());var e=(net.minecraftforge.common.ForgeSpawnEggItem)s.getItem();NpcShopChecks.require(mc.getItemColors().getColor(s,0)==e.getColor(0)&&mc.getItemColors().getColor(s,1)==e.getColor(1),"actual client NPC item tint "+s.getDescriptionId());}
                for(var spec:SecondaryMobs.SPECS){var item=net.minecraftforge.registries.ForgeRegistries.ITEMS.getValue(new net.minecraft.resources.ResourceLocation("dynasty",spec.id()+"_spawn_egg"));var egg=(net.minecraftforge.common.ForgeSpawnEggItem)item;NpcShopChecks.require(mc.getItemColors().getColor(new ItemStack(item),0)==egg.getColor(0),"actual secondary egg tint "+spec.id());}
                Files.write(OUT.resolve("PASS.txt"),NpcShopChecks.LOG);done=true;mc.stop();
            }
        }catch(Throwable failure){try{Files.createDirectories(OUT);Files.writeString(OUT.resolve("FAIL.txt"),failure.toString());}catch(Exception ignored){}failure.printStackTrace();done=true;mc.stop();}
    }
    static void shot(String name)throws Exception{try(var im=Screenshot.takeScreenshot(Minecraft.getInstance().getMainRenderTarget())){im.writeToFile(OUT.resolve(name+".png"));}}
}
