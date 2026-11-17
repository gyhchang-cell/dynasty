package com.dynasty.client;
import com.dynasty.army.*;
import net.minecraft.client.*;
import net.minecraft.client.gui.*;
import net.minecraft.client.gui.components.*;
import net.minecraft.client.gui.screens.*;
import net.minecraft.network.chat.Component;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.Difficulty;
import net.minecraft.world.level.*;
import net.minecraft.world.level.levelgen.*;
import net.minecraft.world.level.levelgen.presets.WorldPresets;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import com.mojang.blaze3d.pipeline.*;
import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.VertexSorting;
import org.joml.Matrix4f;
import java.nio.file.*;
import java.util.*;
@Mod.EventBusSubscriber(modid="dynasty",value=Dist.CLIENT)
public final class ArmyUiRuntimeQa{
 static final boolean ON=Boolean.getBoolean("dynasty.armyUiQa");
 static final Path OUT=Path.of(System.getProperty("dynasty.armyUiQa.output","build/army-ui"));
 static boolean started,done;static int ready;static final List<String>LOG=new ArrayList<>();
 @SubscribeEvent public static void tick(TickEvent.ClientTickEvent e){
  if(!ON||done||e.phase!=TickEvent.Phase.END)return;var mc=Minecraft.getInstance();
  try{
   if(mc.getOverlay()!=null)return;if(mc.screen instanceof AccessibilityOnboardingScreen)mc.setScreen(new TitleScreen());
   if(!started&&mc.screen instanceof TitleScreen){
    if(!mc.gameDirectory.getAbsolutePath().contains("/build/boss-eight-native/"))throw new AssertionError("Not isolated");
    started=true;mc.options.renderDistance().set(2);mc.options.pauseOnLostFocus=false;GameRules rules=new GameRules();rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false,null);
    var settings=new LevelSettings("UI fixture",GameType.CREATIVE,false,Difficulty.PEACEFUL,true,rules,WorldDataConfiguration.DEFAULT);
    mc.createWorldOpenFlows().createFreshLevel("army-ui-"+System.currentTimeMillis(),settings,new WorldOptions(42,false,false),r->r.registryOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.FLAT).createWorldDimensions());
   }
  }catch(Throwable t){fail(mc,t);}
 }
 @SubscribeEvent public static void render(TickEvent.RenderTickEvent e){
  if(!ON||done||e.phase!=TickEvent.Phase.END)return;var mc=Minecraft.getInstance();if(mc.level==null||mc.player==null||mc.getOverlay()!=null||++ready<40)return;
  try{
   done=true;Files.createDirectories(OUT);
   for(int[] size:new int[][]{{420,280},{320,240},{640,360}}){
    var menu=new ArmyMenu(99,mc.player.getInventory(),null);menu.view.set(0,0);menu.view.set(1,125);menu.view.set(2,1);menu.view.set(114,65535);menu.view.set(121,65535);
    var screen=new ArmyRosterScreen(menu,mc.player.getInventory(),Component.literal("虎符"));mc.setScreen(screen);screen.resize(mc,size[0],size[1]);check(screen);capture(mc,screen,size,"empty");
    for(var child:screen.children())if(child instanceof Button b&&b.getMessage().getString().contains("银"))require(!b.active,"Recruitment disabled away from desk");
    menu.view.set(0,43);for(int i=0;i<36;i++){menu.view.set(6+i*3,i%3);menu.view.set(7+i*3,20+i);menu.view.set(8+i*3,i<12?1:0);}screen.resize(mc,size[0],size[1]);click(screen,"#1 ");check(screen);capture(mc,screen,size,"roster");
    click(screen,"›");require(screen.children().stream().anyMatch(c->c instanceof Button b&&b.getMessage().getString().startsWith("#7 ")),"Pagination displays next six soldiers");capture(mc,screen,size,"page2");
    click(screen,"军阵");check(screen);capture(mc,screen,size,"formation");click(screen,"预设 ");require(screen.children().stream().anyMatch(c->c instanceof Button b&&b.getMessage().getString().equals("预设 2 ›")),"Preset selector cycles without sending server action");
    menu.view.set(116,1);menu.view.set(117,4);menu.view.set(114,36);menu.view.set(121,0);screen.tick();screen.resize(mc,size[0],size[1]);check(screen);capture(mc,screen,size,"beyond36");
    require(screen.children().stream().anyMatch(c->c instanceof Button b&&b.getMessage().getString().startsWith("#37 ")),"Second roster window displays soldier37");
    require(screen.children().stream().anyMatch(c->c instanceof Button b&&b.getMessage().getString().equals("37")),"Formation slot37 is available");
    click(screen,"关卡");check(screen);capture(mc,screen,size,"encounters");
    var desk=new ArmyMenu(100,mc.player.getInventory(),net.minecraft.core.BlockPos.ZERO);desk.view.set(4,1);desk.view.set(1,50);desk.view.set(114,65535);desk.view.set(121,65535);
    var shop=new ArmyRosterScreen(desk,mc.player.getInventory(),Component.literal("募兵台"));mc.setScreen(shop);shop.resize(mc,size[0],size[1]);check(shop);capture(mc,shop,size,"recruit");
    require(shop.children().stream().anyMatch(c->c instanceof Button b&&b.active&&b.getMessage().getString().startsWith("确认购买")),"Paid recruitment available at desk with sufficient funds");
    desk.view.set(1,0);shop.resize(mc,size[0],size[1]);require(shop.children().stream().anyMatch(c->c instanceof Button b&&!b.active&&b.getMessage().getString().startsWith("确认购买")),"Cannot buy without silver");

   }
   Files.write(OUT.resolve("PASS.txt"),LOG);mc.stop();
  }catch(Throwable t){fail(mc,t);}
 }
 static void click(Screen s,String prefix){var b=s.children().stream().filter(c->c instanceof Button q&&q.getMessage().getString().startsWith(prefix)).map(c->(Button)c).findFirst().orElseThrow();require(b.active,"Enabled UI control "+prefix);b.onPress();}
 static void check(Screen s){var buttons=s.children().stream().filter(c->c instanceof AbstractWidget).map(c->(AbstractWidget)c).filter(b->b.visible).toList();for(var b:buttons)require(b.getX()>=0&&b.getY()>=0&&b.getX()+b.getWidth()<=s.width&&b.getY()+b.getHeight()<=s.height,"Fits: "+b.getMessage().getString());for(int i=0;i<buttons.size();i++)for(int j=i+1;j<buttons.size();j++){var a=buttons.get(i);var b=buttons.get(j);boolean overlap=a.getX()<b.getX()+b.getWidth()&&a.getX()+a.getWidth()>b.getX()&&a.getY()<b.getY()+b.getHeight()&&a.getY()+a.getHeight()>b.getY();require(!overlap,"No overlap: "+a.getMessage().getString()+" / "+b.getMessage().getString());}}
 static void capture(Minecraft mc,Screen screen,int[] size,String state)throws Exception{
  int w=size[0],h=size[1],scale=3;Matrix4f projection=new Matrix4f(RenderSystem.getProjectionMatrix());var sorting=RenderSystem.getVertexSorting();RenderTarget target=new TextureTarget(w*scale,h*scale,true,Minecraft.ON_OSX);var model=RenderSystem.getModelViewStack();model.pushPose();
  try{target.setClearColor(.035f,.065f,.07f,1);target.clear(Minecraft.ON_OSX);target.bindWrite(true);model.setIdentity();model.translate(0,0,-11000);RenderSystem.applyModelViewMatrix();RenderSystem.setProjectionMatrix(new Matrix4f().setOrtho(0,w,h,0,1000,21000),VertexSorting.ORTHOGRAPHIC_Z);RenderSystem.setShaderColor(1,1,1,1);RenderSystem.disableDepthTest();RenderSystem.enableBlend();RenderSystem.defaultBlendFunc();screen.setFocused(null);var g=new GuiGraphics(mc,mc.renderBuffers().bufferSource());screen.renderWithTooltip(g,-100,-100,0);g.flush();try(var image=Screenshot.takeScreenshot(target)){image.writeToFile(OUT.resolve("army-"+state+"-"+w+"x"+h+".png"));}}
  finally{model.popPose();RenderSystem.applyModelViewMatrix();RenderSystem.setProjectionMatrix(projection,sorting);target.destroyBuffers();mc.getMainRenderTarget().bindWrite(true);}
 }
 static void require(boolean ok,String text){if(!ok)throw new AssertionError(text);LOG.add("PASS: "+text);}
 static void fail(Minecraft mc,Throwable t){done=true;t.printStackTrace();try{Files.createDirectories(OUT);Files.writeString(OUT.resolve("FAIL.txt"),t.toString());}catch(Exception ignored){}mc.stop();}
}
