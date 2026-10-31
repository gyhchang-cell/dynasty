package com.dynasty.infusion;

import java.nio.file.*;
import java.util.*;
import java.util.concurrent.CompletableFuture;
import com.dynasty.network.DynastyNetwork;
import com.mojang.blaze3d.pipeline.TextureTarget;
import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.VertexSorting;
import net.minecraft.client.*;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.*;
import net.minecraft.client.multiplayer.ServerData;
import net.minecraft.client.multiplayer.resolver.ServerAddress;
import net.minecraft.core.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.*;
import net.minecraft.world.level.*;
import net.minecraft.world.level.levelgen.WorldOptions;
import net.minecraft.world.level.levelgen.presets.WorldPresets;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.network.NetworkHooks;
import net.minecraftforge.registries.ForgeRegistries;
import org.joml.Matrix4f;

/** Opt-in isolated real TCP clients. Not included in the shipped mod. */
@Mod.EventBusSubscriber(modid="dynasty",value=Dist.CLIENT)
public final class InfusionClientQa {
    static final String ROLE=System.getProperty("dynasty.infusionQa","");
    static final boolean HOST=ROLE.equals("host"),RESUME=Boolean.getBoolean("dynasty.infusionQa.resume");
    static final Path OUT=Path.of(System.getProperty("dynasty.infusionQa.output","build/infusion-client/results"));
    static final BlockPos POS=new BlockPos(2,-60,2);
    static int phase,ticks,wait,oldRevision,localeIndex;
    static boolean started,finished,render;
    static CompletableFuture<Void> work,reload;
    static final List<String> evidence=new ArrayList<>();
    static long deadline=System.nanoTime()+600_000_000_000L;
    static void marker(String name)throws Exception{Files.createDirectories(OUT);Files.writeString(OUT.resolve(name),"ready");}
    static boolean marked(String name){return Files.exists(OUT.resolve(name));}
    static void check(boolean ok,String message){if(!ok)throw new AssertionError(message);evidence.add(message);}
    static ItemStack stack(String id,int n){return new ItemStack(ForgeRegistries.ITEMS.getValue(new ResourceLocation("dynasty",id)),n);}
    static ServerPlayer host(MinecraftServer s){return s.getPlayerList().getPlayers().stream().filter(p->p.getGameProfile().getName().equals("InfusionHost")).findFirst().orElseThrow();}
    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent e){
        if(ROLE.isEmpty()||finished||e.phase!=TickEvent.Phase.END)return;
        var mc=Minecraft.getInstance();
        try{
            if(System.nanoTime()>deadline)throw new AssertionError("QA timeout phase="+phase);
            if(mc.getOverlay()!=null)return;
            if(HOST&&started&&RESUME&&mc.screen instanceof ConfirmScreen confirm&&confirm.getTitle().getContents() instanceof net.minecraft.network.chat.contents.TranslatableContents title&&title.getKey().equals("selectWorld.backupQuestion.experimental")){
                for(var child:confirm.children())if(child instanceof net.minecraft.client.gui.components.Button button&&button.getMessage().equals(net.minecraft.network.chat.CommonComponents.GUI_PROCEED)){button.onPress();return;}
                throw new AssertionError("Missing proceed button for isolated QA world");
            }
            if(mc.screen instanceof AccessibilityOnboardingScreen)mc.setScreen(new TitleScreen());
            if(!started&&mc.screen instanceof TitleScreen){
                if(!mc.gameDirectory.getCanonicalPath().endsWith("/build/infusion-client/"+ROLE))throw new AssertionError("Unsafe QA directory");
                if(!HOST&&!marked("host-listening"))return;
                started=true;Files.createDirectories(OUT);mc.options.pauseOnLostFocus=false;mc.options.renderDistance().set(2);
                if(!HOST){String address="127.0.0.1:39699";ConnectScreen.startConnecting(new TitleScreen(),mc,ServerAddress.parseString(address),new ServerData("Infusion QA",address,false),false);return;}
                if(RESUME){mc.createWorldOpenFlows().loadLevel(new TitleScreen(),Files.readString(OUT.resolve("world-name")));return;}
                var rules=new GameRules();rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false,null);
                String worldName="infusion-qa-"+System.currentTimeMillis();Files.writeString(OUT.resolve("world-name"),worldName);
                mc.createWorldOpenFlows().createFreshLevel(worldName,new LevelSettings("Infusion QA",GameType.CREATIVE,false,net.minecraft.world.Difficulty.PEACEFUL,true,rules,WorldDataConfiguration.DEFAULT),new WorldOptions(77,false,false),r->r.registryOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.FLAT).createWorldDimensions());return;
            }
            if(mc.level==null||mc.player==null||++ticks<60)return;
            if(work!=null){if(!work.isDone())return;work.join();work=null;}
            var server=mc.getSingleplayerServer();
            if(HOST&&phase==0){phase=1;work=server.submit(()->{
                var world=server.overworld();var p=host(server);p.teleportTo(world,2,-60,0,0,0);
                if(RESUME){var be=(InfusionBlockEntity)world.getBlockEntity(POS);check(be!=null&&InfusionTraits.active(be.getItem(0)).contains("shanxiao_claw")&&be.getItem(1).getCount()==4,"Actual process restart restored table inventory");return;}
                server.setUsesAuthentication(false);try{server.getConnection().startTcpServerListener(java.net.InetAddress.getByName("127.0.0.1"),39699);marker("host-listening");}catch(Exception ex){throw new RuntimeException(ex);}
                world.setBlockAndUpdate(POS,InfusionContent.TABLE.get().defaultBlockState());
            });return;}
            if(HOST&&RESUME&&phase==1){finish(mc,null,"restart");return;}
            if(HOST&&phase==1){if(server.getPlayerList().getPlayerCount()<2)return;phase=2;work=server.submit(()->{
                var be=(InfusionBlockEntity)server.overworld().getBlockEntity(POS);be.setItem(0,new ItemStack(Items.IRON_SWORD));be.setItem(1,stack("cinnabar",4));
                for(var p:server.getPlayerList().getPlayers()){p.teleportTo(server.overworld(),2,-60,0,0,0);p.setGameMode(GameType.SURVIVAL);p.experienceLevel=9;var a=server.getAdvancements().getAdvancement(new ResourceLocation("dynasty","get_jade"));p.getAdvancements().award(a,"has_item");NetworkHooks.openScreen(p,be,POS);}
            });return;}
            if(!HOST&&phase==0)phase=2;
            if(phase==2&&mc.player.containerMenu instanceof InfusionMenu m&&m.material().getCount()==4&&m.status()==0){oldRevision=m.revision();marker(ROLE+"-ready");phase=3;}
            if(phase==3&&HOST&&marked("peer-ready")){var m=(InfusionMenu)mc.player.containerMenu;DynastyNetwork.CHANNEL.sendToServer(new InfusionRequest(m.containerId,0,-1,oldRevision));phase=4;return;}
            if(phase==3&&!HOST&&InfusionTraits.active(((InfusionMenu)mc.player.containerMenu).gear()).size()==1){var m=(InfusionMenu)mc.player.containerMenu;DynastyNetwork.CHANNEL.sendToServer(new InfusionRequest(m.containerId,1,0,oldRevision));marker("peer-stale-sent");phase=4;return;}
            if(phase==4&&HOST&&marked("peer-stale-sent")&&++wait>40){phase=5;work=server.submit(()->{
                var a=host(server);var b=server.getPlayerList().getPlayers().stream().filter(p->p!=a).findFirst().orElseThrow();var m=(InfusionMenu)a.containerMenu;var be=(InfusionBlockEntity)server.overworld().getBlockEntity(POS);
                check(a.experienceLevel==6&&b.experienceLevel==9&&be.getItem(1).getCount()==2&&InfusionTraits.active(be.getItem(0)).size()==1,"Two real clients: one apply, stale peer removal rejected, exact XP/material costs");
                m.quickMoveStack(a,0);var gear=a.getInventory().items.stream().filter(s->s.is(Items.IRON_SWORD)).findFirst().orElseThrow();a.getInventory().removeItemNoUpdate(a.getInventory().findSlotMatchingItem(gear));var drop=a.drop(gear,false);drop.setNoPickUpDelay();drop.setPos(b.getX(),b.getY(),b.getZ());drop.playerTouch(b);
                var held=b.getInventory().items.stream().filter(s->s.is(Items.IRON_SWORD)).findFirst().orElseThrow();check(InfusionTraits.active(held).contains("cinnabar"),"Shift-click then actual dropped-item pickup preserves infusion on other player");
                b.setGameMode(GameType.CREATIVE);b.teleportTo(server.getLevel(Level.NETHER),0,80,0,0,0);b.teleportTo(server.overworld(),2,-60,0,0,0);check(InfusionTraits.active(held).contains("cinnabar"),"Cross-dimension transfer preserves stack data");
                be.setItem(0,InfusionTraits.preview(new ItemStack(Items.IRON_SWORD),InfusionTraits.get("shanxiao_claw"),0,false));be.setItem(1,stack("cinnabar",4));
                for(var p:server.getPlayerList().getPlayers())NetworkHooks.openScreen(p,be,POS);
                try{marker("network-passed");}catch(Exception ex){throw new RuntimeException(ex);}
            });return;}
            if(marked("network-passed")&&phase>=4&&phase<6){phase=6;wait=0;}
            if(phase==6&&mc.screen instanceof InfusionScreen&&++wait>40){
                if(reload==null){mc.getLanguageManager().setSelected(localeIndex==0?"en_us":"zh_cn");reload=mc.reloadResourcePacks();return;}
                if(reload.isDone()){reload.join();render=true;phase=7;}
            }
            if(phase==8){if(++localeIndex<2){reload=null;wait=0;phase=6;}else{marker(ROLE+"-screens-done");phase=9;}}
            if(phase==9&&(!HOST||marked("peer-screens-done")))finish(mc,null,ROLE);
        }catch(Throwable error){finish(mc,error,ROLE);}
    }
    @SubscribeEvent public static void render(TickEvent.RenderTickEvent e){
        if(!render||e.phase!=TickEvent.Phase.END||finished)return;render=false;var mc=Minecraft.getInstance();
        try{
            check(InfusionTraits.ALL.size()==95,"Runtime has 95 material definitions");
            var screen=mc.screen;String language=localeIndex==0?"en":"zh";
            for(int scale:new int[]{2,3,4})capture(mc,screen,language+"-1080p-scale"+scale,1920,1080,scale,false);
            capture(mc,screen,language+"-640x480",640,480,2,false);capture(mc,screen,language+"-960x540-hover",960,540,2,true);
            InfusionJeiQa.verify(mc,language);
            phase=8;
        }catch(Throwable ex){finish(mc,ex,ROLE);}
    }
    static void capture(Minecraft mc,Screen screen,String name,int width,int height,int scale,boolean hover)throws Exception{
        int w=width/scale,h=height/scale;screen.init(mc,w,h);var projection=new Matrix4f(RenderSystem.getProjectionMatrix());var sorting=RenderSystem.getVertexSorting();var target=new TextureTarget(width,height,true,Minecraft.ON_OSX);var model=RenderSystem.getModelViewStack();model.pushPose();
        try{target.setClearColor(.12f,.15f,.13f,1);target.clear(Minecraft.ON_OSX);target.bindWrite(true);model.setIdentity();model.translate(0,0,-11000);RenderSystem.applyModelViewMatrix();RenderSystem.setProjectionMatrix(new Matrix4f().setOrtho(0,w,h,0,1000,21000),VertexSorting.ORTHOGRAPHIC_Z);RenderSystem.disableDepthTest();RenderSystem.enableBlend();RenderSystem.defaultBlendFunc();RenderSystem.setShaderColor(1,1,1,1);var g=new GuiGraphics(mc,mc.renderBuffers().bufferSource());screen.renderWithTooltip(g,hover?(w-176)/2+32:-100,hover?(h-202)/2+65:-100,0);g.flush();try(var image=Screenshot.takeScreenshot(target)){image.writeToFile(OUT.resolve(ROLE+"-"+name+".png"));}}
        finally{model.popPose();RenderSystem.applyModelViewMatrix();RenderSystem.setProjectionMatrix(projection,sorting);target.destroyBuffers();mc.getMainRenderTarget().bindWrite(true);screen.init(mc,mc.getWindow().getGuiScaledWidth(),mc.getWindow().getGuiScaledHeight());}
    }
    static void finish(Minecraft mc,Throwable error,String name){finished=true;try{Files.createDirectories(OUT);Files.writeString(OUT.resolve(name+(error==null?"-PASS.txt":"-FAIL.txt")),String.join("\n",evidence)+(error==null?"\n":error.toString()));}catch(Exception ignored){}if(error!=null)error.printStackTrace();mc.stop();}
}
