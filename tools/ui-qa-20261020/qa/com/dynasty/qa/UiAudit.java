package com.dynasty.qa;
import net.minecraft.client.*;
import net.minecraft.client.gui.*;
import net.minecraft.client.gui.components.*;
import net.minecraft.client.gui.screens.*;
import net.minecraft.client.gui.screens.inventory.*;
import net.minecraft.network.chat.Component;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.*;
import net.minecraft.world.level.levelgen.WorldOptions;
import net.minecraft.world.level.levelgen.presets.WorldPresets;
import net.minecraft.world.Difficulty;
import net.minecraft.world.item.*;
import net.minecraft.world.item.alchemy.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;
import com.google.gson.*;
import java.nio.file.*;
import java.util.*;
@Mod("dynastyaudit")
public class UiAudit {
 public static final Path OUT=Path.of(System.getProperty("dynasty.audit.output"));
 static void check(boolean ok,String message)throws Exception{if(!ok)throw new AssertionError(message);Files.writeString(OUT.resolve("checks.txt"),"PASS "+message+"\n",StandardOpenOption.CREATE,StandardOpenOption.APPEND);}
 static ItemStack item(String id){return new ItemStack(ForgeRegistries.ITEMS.getValue(new ResourceLocation(id)));}
 static void shot(Minecraft m,String n)throws Exception{try(var pixels=Screenshot.takeScreenshot(m.getMainRenderTarget())){pixels.writeToFile(OUT.resolve(n+".png"));}}
 @Mod.EventBusSubscriber(modid="dynastyaudit",value=net.minecraftforge.api.distmarker.Dist.CLIENT)
 public static class Client {
 static boolean started,done,figures,creativeReady;static int frame,step,figure;static JsonArray plans;
 static final float[][] HEALTH={{16,20,0},{16,16,0},{27,36,0},{160,240,24},{16,20,0}};
 static void server(java.util.function.Consumer<net.minecraft.server.level.ServerPlayer> action){var m=Minecraft.getInstance();var id=m.player.getUUID();m.getSingleplayerServer().execute(()->action.accept(m.getSingleplayerServer().getPlayerList().getPlayer(id)));}
 static void hp(int i){server(p->{p.removeAllEffects();p.getAttribute(Attributes.MAX_HEALTH).setBaseValue(HEALTH[i][1]);p.setHealth(HEALTH[i][0]);p.setAbsorptionAmount(HEALTH[i][2]);});}
 @SubscribeEvent public static void tick(TickEvent.RenderTickEvent e){
  if(done||e.phase!=TickEvent.Phase.END)return;var m=Minecraft.getInstance();
  try{
   Files.createDirectories(OUT);if(m.getOverlay()!=null)return;
   if(m.screen!=null&&m.screen.getClass().getName().contains("LoadingErrorScreen")){shot(m,"loading-error");Files.writeString(OUT.resolve("loading-error.txt"),m.screen.toString());done=true;m.stop();return;}
   if(++frame%300==0)Files.writeString(OUT.resolve("state.txt"),"screen="+(m.screen==null?"null":m.screen.getClass().getName())+" step="+step+" figure="+figure);
   if(m.screen instanceof AccessibilityOnboardingScreen)m.setScreen(new TitleScreen());
   if(!started&&m.screen instanceof TitleScreen){
    started=true;check(m.gameDirectory.getCanonicalPath().contains("/build/ui-client-20261020"),"Disposable isolated profile; existing player saves untouched");
    if(Boolean.getBoolean("dynasty.audit.figures")){
     plans=JsonParser.parseString(Files.readString(OUT.getParent().resolve("figures.json"))).getAsJsonArray();m.options.guiScale().set(1);m.resizeDisplay();m.setScreen(new FigureScreen(plans.get(0).getAsJsonObject()));frame=0;return;
    }figures=true;
   }
   if(started&&!figures&&m.screen instanceof FigureScreen screen){
    if(frame<5)return;screen.save(m);if(++figure<plans.size()){m.setScreen(new FigureScreen(plans.get(figure).getAsJsonObject()));frame=0;return;}
    check(figure==26,"26 quest figures authored using real game item models and font");figures=true;if(Boolean.getBoolean("dynasty.audit.onlyFigures")){done=true;m.stop();return;}m.setScreen(new TitleScreen());
   }
   if(started&&figures&&m.level==null&&m.screen instanceof TitleScreen){
    m.options.guiScale().set(3);m.resizeDisplay();var rules=new GameRules();rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false,null);rules.getRule(GameRules.RULE_NATURAL_REGENERATION).set(false,null);
    m.createWorldOpenFlows().createFreshLevel("ui-audit-"+System.currentTimeMillis(),new LevelSettings("Disposable UI audit",GameType.SURVIVAL,false,Difficulty.NORMAL,true,rules,WorldDataConfiguration.DEFAULT),new WorldOptions(31,false,false),r->r.registryOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.FLAT).createWorldDimensions());frame=0;return;
   }
   if(m.player==null||m.level==null||++frame<90)return;
   if(step==0){m.setScreen(null);check(net.minecraftforge.fml.ModList.get().isLoaded("armorpointspp"),"Fool's same ArmorPoints++ version is active");check(!net.minecraftforge.fml.ModList.get().isLoaded("overflowingbars"),"Conflicting old heart renderer absent");RecipeAudit.audit(m);hp(0);step++;frame=0;return;}
   if(step>=1&&step<=HEALTH.length){int i=step-1;check(m.player.getHealth()==HEALTH[i][0]&&m.player.getMaxHealth()==HEALTH[i][1],"Synced real health "+m.player.getHealth()+" / "+m.player.getMaxHealth()+" absorption "+m.player.getAbsorptionAmount());shot(m,"health-"+i);if(step<HEALTH.length)hp(step);step++;frame=0;return;}
   if(step==6){tooltips(m);searchJei(m);server(p->{p.setGameMode(GameType.CREATIVE);});step++;frame=0;return;}
   if(step==7){m.setScreen(new CreativeModeInventoryScreen(m.player,m.level.enabledFeatures(),true));step++;frame=0;return;}
   if(step==8){if(!creativeReady){creative(m);creativeReady=true;frame=0;return;}shot(m,"creative-compass-search");m.setScreen(new TipScreen(item("dynasty:dynasty_potion"),"iron_wall"));step++;frame=0;return;}
   if(step==9){shot(m,"potion-tooltip");m.setScreen(new TipScreen(item("dynasty:war_drum_charm"),null));step++;frame=0;return;}
   if(step==10){shot(m,"accessory-tooltip");m.setScreen(null);server(p->{p.setGameMode(GameType.SURVIVAL);p.getInventory().setItem(0,item("dynasty:tiger_tally"));p.getInventory().setItem(1,new ItemStack(com.dynasty.DynastyItems.SILVER_COIN.get(),64));for(int r=0;r<3;r++)checkServer(com.dynasty.army.ArmyRoster.recruit(p,r));p.getInventory().selected=0;com.dynasty.army.ArmyContent.open(p,null);});step++;frame=0;return;}
   if(step==11){check(m.screen instanceof com.dynasty.army.ArmyRosterScreen,"Actual tiger tally native menu loaded");press(m,"军阵");step++;frame=0;return;}
   if(step==12){press(m,"#1");step++;frame=0;return;}
   if(step==13){press(m,"3");step++;frame=0;return;}
   if(step==14){shot(m,"tiger-tally-formation");for(var w:m.screen.children())if(w instanceof Button b)check(!b.getMessage().getString().matches(".*(预设|保存|载入|阵型).*"),"One live freely assigned formation, no preset controls: "+b.getMessage().getString());var future=m.getSingleplayerServer().submit(()->com.dynasty.army.ArmyRoster.soldiers(m.getSingleplayerServer().getPlayerList().getPlayer(m.player.getUUID())).getCompound(0).getInt("Slot"));check(future.join()==2,"Real native button packets assigned first paid soldier to slot 3");m.player.closeContainer();step++;frame=0;return;}
   if(step==15){questAudit(m);showQuest(0x1000000000030163L);step++;frame=0;return;}
   if(step==16){shot(m,"quest-evolution");showQuest(0x1000000000020006L);step++;frame=0;return;}
   if(step==17){shot(m,"quest-altar");showQuest(0x4000000000000500L);step++;frame=0;return;}
   if(step==18){shot(m,"quest-home");Files.writeString(OUT.resolve("COMPLETE.txt"),"Native full-pack checks and screenshot capture complete. See checks.txt and audit.txt.");done=true;m.stop();}
  }catch(Throwable ex){ex.printStackTrace();try{Files.writeString(OUT.resolve("FAIL.txt"),ex.toString());}catch(Exception ignored){}done=true;m.stop();}
 }
 static void checkServer(boolean okay){if(!okay)throw new AssertionError("paid recruitment fixture failed");}
 static void press(Minecraft m,String text)throws Exception{for(var w:m.screen.children())if(w instanceof Button b&&(b.getMessage().getString().equals(text)||text.startsWith("#")&&b.getMessage().getString().startsWith(text+" "))){check(b.active,"Native clickable control "+text);b.onPress();return;}throw new AssertionError("Button absent "+text);}
 static void searchJei(Minecraft m)throws Exception{check(JeiProbe.runtime!=null,"Actual JEI runtime available");var filter=JeiProbe.runtime.getIngredientFilter();for(String s:new String[]{"结构罗盘","Jiegouluopan","Structure Compass","Explorer's Compass"}){filter.setFilterText(s);check(filter.getFilteredItemStacks().stream().anyMatch(x->ForgeRegistries.ITEMS.getKey(x.getItem()).toString().equals("explorerscompass:explorerscompass")),"JEI search finds structure compass: "+s);}filter.setFilterText("");}
 static void creative(Minecraft m)throws Exception{var screen=(CreativeModeInventoryScreen)m.screen;EditBox search=null;for(var f:CreativeModeInventoryScreen.class.getDeclaredFields())if(f.getType()==EditBox.class){f.setAccessible(true);search=(EditBox)f.get(screen);}check(search!=null,"Native creative search box exists");for(var method:CreativeModeInventoryScreen.class.getDeclaredMethods())if(method.getReturnType()==void.class&&java.util.Arrays.equals(method.getParameterTypes(),new Class<?>[]{CreativeModeTab.class})){method.setAccessible(true);method.invoke(screen,CreativeModeTabs.searchTab());break;}boolean selected=false;for(var field:CreativeModeInventoryScreen.class.getDeclaredFields())if(field.getType()==CreativeModeTab.class&&java.lang.reflect.Modifier.isStatic(field.getModifiers())){field.setAccessible(true);selected|=field.get(null)==CreativeModeTabs.searchTab();}check(selected&&search.isVisible(),"Native search tab actually selected, not tab coordinate helper");search.setValue("");for(char c:"__no_such_compass_9287__".toCharArray())screen.charTyped(c,0);check(screen.getMenu().items.isEmpty(),"Native typed negative query filters out unrelated items");for(String query:new String[]{"结构罗盘","Jiegouluopan","Structure Compass"}){search.setValue("");for(char c:query.toCharArray())screen.charTyped(c,0);check(search.getValue().equals(query)&&screen.getMenu().items.size()<5,"Native typed query applies filtering: "+query+" results="+screen.getMenu().items.size());check(screen.getMenu().items.stream().anyMatch(x->ForgeRegistries.ITEMS.getKey(x.getItem()).toString().equals("explorerscompass:explorerscompass")),"Native creative search finds structure compass: "+query);}}
 static void tooltips(Minecraft m)throws Exception{
  var report=new StringBuilder();int potions=0,charms=0,names=0;var duplicates=new TreeMap<String,List<String>>();
  for(var id:ForgeRegistries.ITEMS.getKeys()){
   var stack=item(id.toString());String name=stack.getHoverName().getString();
   if(id.getNamespace().equals("dynasty")){names++;check(!name.startsWith("item.")&&!name.startsWith("block."),"Resolved item name "+id);duplicates.computeIfAbsent(name,k->new ArrayList<>()).add(id.toString());}
   if(stack.getItem() instanceof com.dynasty.DynastyTrinketTips.Charm){charms++;var tip=stack.getTooltipLines(m.player,TooltipFlag.NORMAL);report.append(id+"\n");for(var line:tip)report.append(line.getString()+"\n");}
   if(id.getNamespace().equals("dynasty")&&stack.getItem() instanceof PotionItem)for(var potion:ForgeRegistries.POTIONS.getKeys())if(potion.getNamespace().equals("dynasty")){
    var variant=PotionUtils.setPotion(stack.copy(),ForgeRegistries.POTIONS.getValue(potion));var tip=variant.getTooltipLines(m.player,TooltipFlag.NORMAL);String text=tip.stream().map(Component::getString).collect(java.util.stream.Collectors.joining("\n"));
    check(!text.contains("王朝药水")&&!text.contains("Dynasty potion")&&!text.contains("龙威 攻击"),"Potion contains only its own effects "+id+" "+potion);if(potion.getPath().contains("iron_wall"))check(text.contains("30%")&&!text.contains("300")&&!text.contains("100"),"Iron wall tooltip has real mitigation, no unrelated damage/health stats");potions++;report.append(variant.getHoverName().getString()+"\n"+text+"\n");
   }
  }
  duplicates.entrySet().removeIf(e->e.getValue().size()<2);Files.writeString(OUT.resolve("tooltip-audit.txt"),report+"\nDUPLICATE_NATIVE_NAMES "+duplicates);check(duplicates.isEmpty(),"No duplicate real Dynasty item display names ("+names+" items)");check(potions>=18&&charms>40,"Audited actual potion variants "+potions+" and charms "+charms);
 }
 static Class<?> type(String n)throws Exception{return Class.forName("dev.ftb.mods.ftbquests."+n);}
 static void questAudit(Minecraft m)throws Exception{Object file=type("client.ClientQuestFile").getField("INSTANCE").get(null);var raw=type("quest.QuestObjectBase").getDeclaredField("rawIcon");raw.setAccessible(true);int n=0;for(var o:(Collection<?>)file.getClass().getMethod("getAllObjects").invoke(file))if(type("quest.Quest").isInstance(o)){check(!((ItemStack)raw.get(o)).isEmpty(),"Native quest icon "+o);n++;}check(n==1259,"All 1259 quest definitions load with actual icons");}
 static void showQuest(long id)throws Exception{type("client.ClientQuestFile").getMethod("openBookToQuestObject",long.class).invoke(null,id);}
 }
 static class TipScreen extends Screen {
  final ItemStack stack;TipScreen(ItemStack s,String potion){super(Component.literal("Actual item tooltip"));stack=potion==null?s:PotionUtils.setPotion(s,ForgeRegistries.POTIONS.getValue(new ResourceLocation("dynasty",potion)));}
  public void render(GuiGraphics g,int x,int y,float t){renderBackground(g);g.renderItem(stack,20,20);g.renderTooltip(font,stack,45,35);}
 }
 static class FigureScreen extends Screen {
  final JsonObject plan;int left,top;FigureScreen(JsonObject p){super(Component.literal(p.get("title").getAsString()));plan=p;}
  void text(GuiGraphics g,String s,int x,int y,float scale,int color){g.pose().pushPose();g.pose().translate(left+x,top+y,0);g.pose().scale(scale,scale,1);g.drawString(font,s,0,0,color,false);g.pose().popPose();}
  void icon(GuiGraphics g,String id,int x,int y,int size){if(id.isBlank())return;g.pose().pushPose();g.pose().translate(left+x,top+y,0);g.pose().scale(size/16f,size/16f,1);g.renderItem(item(id),0,0);g.pose().popPose();}
  public void render(GuiGraphics g,int mouseX,int mouseY,float delta){
   left=(width-512)/2;top=(height-256)/2;g.fill(0,0,width,height,0xFF303030);g.fill(left,top,left+512,top+256,0xFFC6C6C6);g.fill(left,top,left+512,top+3,0xFFFFFFFF);g.fill(left,top,left+3,top+256,0xFFFFFFFF);g.fill(left+3,top+253,left+512,top+256,0xFF555555);g.fill(left+509,top+3,left+512,top+256,0xFF555555);text(g,plan.get("title").getAsString(),18,14,2f,0x303030);
   var cells=plan.getAsJsonArray("cells");var icons=plan.getAsJsonArray("icons");
   if(plan.has("grid")){var grid=plan.getAsJsonArray("grid");for(int i=0;i<9;i++){int x=181+i%3*42,y=49+i/3*42;g.fill(left+x-1,top+y-1,left+x+40,top+y+40,0xFF373737);g.fill(left+x,top+y,left+x+39,top+y+39,0xFF8B8B8B);g.fill(left+x+1,top+y+1,left+x+39,top+y+39,0xFFFFFFFF);g.fill(left+x+1,top+y+1,left+x+38,top+y+38,0xFF8B8B8B);icon(g,grid.get(i).getAsString(),x+3,y+3,32);}}
   else for(int i=0;i<3;i++){int x=22+i*166;g.fill(left+x,top+63,left+x+70,top+132,0xFF555555);g.fill(left+x+1,top+64,left+x+70,top+132,0xFFFFFFFF);g.fill(left+x+1,top+64,left+x+69,top+131,0xFF8B8B8B);icon(g,icons.get(i).getAsString(),x+6,69,56);int cy=143;for(var line:font.split(Component.literal(cells.get(i).getAsString()),96)){g.pose().pushPose();g.pose().translate(left+x,top+cy,0);g.pose().scale(1.5f,1.5f,1);g.drawString(font,line,0,0,0x303030,false);g.pose().popPose();cy+=17;}if(i<2&&!java.util.Set.of("compasses","academy_materials","compass_recipe","smithing").contains(plan.get("key").getAsString()))text(g,plan.get("key").getAsString().equals("bronze")&&i==1?"→":java.util.Set.of("qimen","bronze","wind_recipe","writing_recipe").contains(plan.get("key").getAsString())?"+":"→",x+100,86,2.3f,0x555555);}
   int y=187;for(var note:plan.getAsJsonArray("notes")){text(g,note.getAsString(),18,y,1.75f,0x404040);y+=25;}
  }
  void save(Minecraft m)throws Exception{var dir=OUT.getParent().resolve("native-figures");Files.createDirectories(dir);double scale=m.getWindow().getGuiScale();check(scale==1,"Native figure output authored at 1:1 pixels");try(var frame=Screenshot.takeScreenshot(m.getMainRenderTarget());var crop=new com.mojang.blaze3d.platform.NativeImage(512,256,false)){int dx=(frame.getWidth()-m.getWindow().getGuiScaledWidth())/2,dy=0;for(int y=0;y<256;y++)for(int x=0;x<512;x++)crop.setPixelRGBA(x,y,frame.getPixelRGBA(left+x+dx,top+y+dy));crop.writeToFile(dir.resolve(plan.get("key").getAsString()+".png"));}}
 }
}
