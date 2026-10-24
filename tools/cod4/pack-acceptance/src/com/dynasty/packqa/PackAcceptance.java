package com.dynasty.packqa;

import com.google.gson.*;
import com.dynasty.TalismanDiscovery;
import com.dynasty.cod3.BowDrawProgress;
import com.mojang.blaze3d.platform.InputConstants;
import net.minecraft.client.*;
import net.minecraft.client.gui.screens.*;
import net.minecraft.client.gui.screens.inventory.InventoryScreen;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.Difficulty;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.item.*;
import net.minecraft.world.level.*;
import net.minecraft.world.level.levelgen.WorldOptions;
import net.minecraft.world.level.levelgen.presets.WorldPresets;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;
import mezz.jei.api.constants.*;
import mezz.jei.api.recipe.*;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.CompletableFuture;

@Mod("dynastypackqa")
public final class PackAcceptance {
 static final Gson JSON=new GsonBuilder().setPrettyPrinting().create();
 static final Path OUT=Path.of(System.getProperty("dynasty.packqa.output"));
 static void write(String name,Object value)throws Exception{Files.writeString(OUT.resolve(name),JSON.toJson(value));}
 static void log(String text)throws Exception{Files.writeString(OUT.resolve("checks.txt"),text+"\n",StandardOpenOption.CREATE,StandardOpenOption.APPEND);}
 static void check(boolean ok,String text)throws Exception{if(!ok)throw new AssertionError(text);log("PASS "+text);}
 static ItemStack item(String id){return new ItemStack(Objects.requireNonNull(ForgeRegistries.ITEMS.getValue(new ResourceLocation(id))));}
 static String id(ItemStack stack){return ForgeRegistries.ITEMS.getKey(stack.getItem()).toString();}
 static void shot(Minecraft mc,String name)throws Exception{try(var pixels=Screenshot.takeScreenshot(mc.getMainRenderTarget())){pixels.writeToFile(OUT.resolve(name+".png"));}}
 @Mod.EventBusSubscriber(modid="dynastypackqa",value=net.minecraftforge.api.distmarker.Dist.CLIENT)
 public static final class Client {
  static volatile Map<String,Object> serverUse=Map.of();
  static Map<String,Object> renderedHud=Map.of();static int hudSerial,lastCapturedHud;
  @SubscribeEvent(priority=net.minecraftforge.eventbus.api.EventPriority.LOWEST) public static void hud(net.minecraftforge.client.event.RenderGuiEvent.Post event){if(bow!=null){renderedHud=state(Minecraft.getInstance());hudSerial++;}}
  static boolean started,ready,done;static int frames,ticks;static String lastCommand="";
  static CompletableFuture<?> task;static JsonObject active;static int actionFrames;
  static JsonObject bow;static int bowAge;static boolean bowPressed,bowFinished;static Set<Integer> captured=new HashSet<>();static final Map<String,com.mojang.blaze3d.platform.NativeImage> pendingImages=new LinkedHashMap<>();static final List<Object> bowFrames=new ArrayList<>();
  static void server(java.util.function.Consumer<net.minecraft.server.level.ServerPlayer> fn){var m=Minecraft.getInstance();var id=m.player.getUUID();task=m.getSingleplayerServer().submit(()->fn.accept(m.getSingleplayerServer().getPlayerList().getPlayer(id)));}
  static Map<String,Object> state(Minecraft m){var s=new LinkedHashMap<String,Object>();s.put("windowActive",m.isWindowActive());s.put("glfwFocused",org.lwjgl.glfw.GLFW.glfwGetWindowAttrib(m.getWindow().getWindow(),org.lwjgl.glfw.GLFW.GLFW_FOCUSED));s.put("screen",m.screen==null?"none":m.screen.getClass().getName());s.put("world",m.level!=null);s.put("ready",ready);s.put("tick",ticks);s.put("language",m.getLanguageManager().getSelected());s.put("jei",JeiProbe.runtime!=null);s.put("server",serverUse);s.put("guiWidth",m.getWindow().getGuiScaledWidth());s.put("guiHeight",m.getWindow().getGuiScaledHeight());s.put("scale",m.getWindow().getGuiScale());if(m.screen!=null&&m.screen.getClass().getName().equals("mezz.jei.gui.recipes.RecipesGui"))try{s.put("jeiScreen",jeiScreen(m));}catch(Exception ex){s.put("jeiProbeError",ex.toString());}if(m.player!=null){s.put("using",m.player.isUsingItem());s.put("main",id(m.player.getMainHandItem()));s.put("off",id(m.player.getOffhandItem()));s.put("usedHand",m.player.getUsedItemHand().toString());s.put("nativeUseTicks",m.player.getTicksUsingItem());var d=BowDrawProgress.read(m.player);s.put("draw",d==null?null:Map.of("ticks",d.ticks(),"required",d.required(),"full",d.full(),"fraction",d.fraction()));s.put("camera",m.options.getCameraType().toString());s.put("hideGui",m.options.hideGui);}return s;}
  @SubscribeEvent public static void clientTick(TickEvent.ClientTickEvent event){
   if(done||event.phase!=TickEvent.Phase.END)return;ticks++;var m=Minecraft.getInstance();
   try{
    if(m.player!=null&&m.getSingleplayerServer()!=null&&ticks%2==0){var uid=m.player.getUUID();m.getSingleplayerServer().execute(()->{var p=m.getSingleplayerServer().getPlayerList().getPlayer(uid);if(p!=null)serverUse=Map.of("using",p.isUsingItem(),"useTicks",p.getTicksUsingItem(),"main",id(p.getMainHandItem()),"off",id(p.getOffhandItem()),"hand",p.getUsedItemHand().toString(),"arrows",p.getInventory().countItem(Items.ARROW));});}
    if(bow==null||m.player==null||task!=null&&!task.isDone())return;
    if(task!=null){task.join();task=null;}
    ++bowAge;if(!bowPressed&&bowAge<24)return;
    if(!bowPressed){
     String expected=bow.get("item").getAsString();boolean off=bow.has("offhand")&&bow.get("offhand").getAsBoolean();
     if(!id(off?m.player.getOffhandItem():m.player.getMainHandItem()).equals(expected))return;
     m.setScreen(null);m.options.hideGui=false;org.lwjgl.glfw.GLFW.glfwFocusWindow(m.getWindow().getWindow());m.mouseHandler.grabMouse();m.player.setXRot(-25);m.player.setYRot(0);
     m.options.setCameraType(CameraType.valueOf(bow.has("camera")?bow.get("camera").getAsString():"FIRST_PERSON"));
     m.options.keyUse.setDown(true);KeyMapping.click(m.options.keyUse.getKey());bowPressed=true;bowAge=0;log("INPUT native keyUse press "+expected);return;
    }
    int use=m.player.getTicksUsingItem();
    var record=new LinkedHashMap<String,Object>(state(m));record.put("age",bowAge);Files.writeString(OUT.resolve(bow.get("name").getAsString()+"-ticks.jsonl"),new Gson().toJson(record)+"\n",StandardOpenOption.CREATE,StandardOpenOption.APPEND);
    if(bow.has("variant")&&use>=24){String mode=bow.get("variant").getAsString();
     if(mode.equals("gui")&&m.screen==null&&bowAge<55)nativeKey(m,69);
     if(mode.equals("hideGui"))m.options.hideGui=true;
     if(mode.equals("swap")&&m.player.getInventory().selected==0)m.player.getInventory().selected=1;
    }
    if(bowAge>=55){m.options.keyUse.setDown(false);if(m.screen!=null)nativeKey(m,256);bowFinished=true;}
    if(bowAge>=65){for(var saved:pendingImages.entrySet())try(var pixels=saved.getValue()){pixels.writeToFile(OUT.resolve(saved.getKey()+".png"));}pendingImages.clear();m.options.hideGui=false;m.setScreen(null);m.options.setCameraType(CameraType.FIRST_PERSON);write(bow.get("name").getAsString()+"-frames.json",bowFrames);write(bow.get("name").getAsString()+"-result.json",state(m));bow=null;bowFrames.clear();bowFinished=false;}
   }catch(Throwable e){failure(e);bow=null;}
  }
  @SubscribeEvent public static void render(TickEvent.RenderTickEvent event){
   if(done||event.phase!=TickEvent.Phase.END)return;var m=Minecraft.getInstance();
   try{
    if(m.getOverlay()!=null)return;
    if(m.screen instanceof AccessibilityOnboardingScreen)m.setScreen(new TitleScreen());
    if(m.screen!=null&&m.screen.getClass().getName().contains("LoadingErrorScreen")){shot(m,"loading-error");write("FAIL.json",state(m));done=true;m.stop();return;}
    if(!started&&m.screen instanceof TitleScreen){
     check(m.gameDirectory.getCanonicalPath().equals(System.getProperty("dynasty.packqa.instance")),"Fresh private full-pack instance");started=true;
     write("loaded-mods.json",net.minecraftforge.fml.ModList.get().getMods().stream().map(x->Map.of("id",x.getModId(),"version",x.getVersion().toString())).toList());
     var rules=new GameRules();rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false,null);rules.getRule(GameRules.RULE_DAYLIGHT).set(false,null);
     m.createWorldOpenFlows().createFreshLevel("cod4-pack-qa-"+System.currentTimeMillis(),new LevelSettings("COD4 full-pack QA",GameType.SURVIVAL,false,Difficulty.NORMAL,true,rules,WorldDataConfiguration.DEFAULT),new WorldOptions(43,false,false),r->r.registryOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.FLAT).createWorldDimensions());return;
    }
    if(++frames%60==0)write("state.json",state(m));
    if(m.player==null||m.level==null)return;
    if(!ready){if(JeiProbe.runtime==null||frames<120)return;ready=true;m.setScreen(null);shot(m,"fullpack-world");log("PASS Actual full-pack client entered a new integrated-server QA world; JEI runtime active");write("READY.json",state(m));}
    if(bow!=null&&bowPressed&&(hudSerial!=lastCapturedHud||m.options.hideGui||m.screen!=null)){
     lastCapturedHud=hudSerial;
     var d=BowDrawProgress.read(m.player);int t=d==null?-bowAge-1:d.ticks();
     var f=new LinkedHashMap<String,Object>(state(m));f.put("age",bowAge);f.put("hudSerial",hudSerial);f.put("renderedHud",renderedHud);
     int gold=0,blue=0;try(var pixels=Screenshot.takeScreenshot(m.getMainRenderTarget())){
      double scale=m.getWindow().getGuiScale();int x=m.getWindow().getGuiScaledWidth()/2,y=m.getWindow().getGuiScaledHeight()/2+20;
      for(int yy=(int)(y*scale);yy<(int)((y+2)*scale);yy++)for(int xx=(int)((x-15)*scale);xx<(int)((x+15)*scale);xx++){int c=pixels.getPixelRGBA(xx,yy);if((c&0xFFFFFF)==0x70C3EB)gold++;if((c&0xFFFFFF)==0xCEB994)blue++;}
      f.put("goldPixels",gold);f.put("bluePixels",blue);
      boolean sample=d!=null&&(t==0||t==1||t==d.required()-1||t==d.required()||t==d.required()+4||t==28)||bowAge>=56&&bowAge<=58;
      if(sample&&captured.add(t)){var copy=new com.mojang.blaze3d.platform.NativeImage(pixels.getWidth(),pixels.getHeight(),false);copy.copyFrom(pixels);pendingImages.put(bow.get("name").getAsString()+"-t"+t,copy);}
      if(m.screen!=null&&captured.add(Integer.MIN_VALUE)){String image=bow.get("name").getAsString()+"-actual-gui";var copy=new com.mojang.blaze3d.platform.NativeImage(pixels.getWidth(),pixels.getHeight(),false);copy.copyFrom(pixels);pendingImages.put(image,copy);f.put("screenshot",image+".png");}
     }bowFrames.add(f);
    }
    if(active!=null){if(task!=null&&!task.isDone())return;if(task!=null){task.join();task=null;}if(++actionFrames<20)return;String cid=active.get("id").getAsString();shot(m,cid);write(cid+"-result.json",state(m));active=null;}
    Path command=OUT.resolve("command.json");if(!Files.exists(command)||bow!=null||active!=null)return;
    JsonObject c=JsonParser.parseString(Files.readString(command)).getAsJsonObject();String cid=c.get("id").getAsString();if(cid.equals(lastCommand))return;lastCommand=cid;Files.copy(command,OUT.resolve(cid+"-command.json"));dispatch(m,c);active=c;actionFrames=0;
   }catch(Throwable ex){failure(ex);}
  }
  static void failure(Throwable e){e.printStackTrace();try{write((lastCommand.isEmpty()?"startup":lastCommand)+"-FAIL.json",Map.of("error",e.toString(),"trace",Arrays.toString(e.getStackTrace())));}catch(Exception ignored){}active=null;}
  static void dispatch(Minecraft m,JsonObject c)throws Exception{
   String op=c.get("op").getAsString();String cid=c.get("id").getAsString();log("COMMAND "+c);
   switch(op){
    case "shot" -> {}
    case "close" -> {m.setScreen(null);}
    case "language" -> {m.setScreen(null);String lang=c.get("lang").getAsString();m.getLanguageManager().setSelected(lang);m.options.languageCode=lang;task=m.reloadResourcePacks();}
    case "talismans" -> auditTalismans(m,cid);
    case "jei" -> {String target=c.get("item").getAsString();var role=RecipeIngredientRole.valueOf(c.get("role").getAsString());var focus=JeiProbe.runtime.getJeiHelpers().getFocusFactory().createFocus(role,VanillaTypes.ITEM_STACK,item(target));if(m.screen==null)m.setScreen(new InventoryScreen(m.player));JeiProbe.runtime.getRecipesGui().show(List.of(focus));}
    case "info" -> {var focus=JeiProbe.runtime.getJeiHelpers().getFocusFactory().createFocus(RecipeIngredientRole.INPUT,VanillaTypes.ITEM_STACK,item(c.get("item").getAsString()));var r=JeiProbe.runtime.getRecipeManager();var recipes=r.createRecipeLookup(RecipeTypes.INFORMATION).limitFocus(List.of(focus)).get().toList();check(!recipes.isEmpty(),"Native JEI information exists for "+c.get("item"));JeiProbe.runtime.getRecipesGui().showRecipes(r.getRecipeCategory(RecipeTypes.INFORMATION),recipes,List.of(focus));}
    case "key" -> {check(m.screen!=null,"Native screen exists for key navigation");m.screen.keyPressed(c.get("key").getAsInt(),0,0);}
    case "nativeKey" -> {if(c.has("x"))move(m,c.get("x").getAsDouble(),c.get("y").getAsDouble());nativeKey(m,c.get("key").getAsInt());}
    case "nativeMouse" -> {move(m,c.get("x").getAsDouble(),c.get("y").getAsDouble());var press=net.minecraftforge.fml.util.ObfuscationReflectionHelper.findMethod(MouseHandler.class,"m_91530_",long.class,int.class,int.class,int.class);press.invoke(m.mouseHandler,m.getWindow().getWindow(),c.get("button").getAsInt(),1,0);press.invoke(m.mouseHandler,m.getWindow().getWindow(),c.get("button").getAsInt(),0,0);}
    case "focus" -> {org.lwjgl.glfw.GLFW.glfwFocusWindow(m.getWindow().getWindow());}
    case "mouse" -> {check(m.screen!=null,"Native screen exists for mouse navigation");var screen=m.screen;boolean pressed=screen.mouseClicked(c.get("x").getAsDouble(),c.get("y").getAsDouble(),c.get("button").getAsInt());boolean released=screen.mouseReleased(c.get("x").getAsDouble(),c.get("y").getAsDouble(),c.get("button").getAsInt());write(cid+"-input.json",Map.of("pressedHandled",pressed,"releasedHandled",released));}
    case "bow" -> {bow=c.deepCopy();bowAge=0;bowPressed=false;bowFrames.clear();captured.clear();m.setScreen(null);m.options.keyUse.setDown(false);m.player.getInventory().selected=0;server(p->{p.stopUsingItem();p.getInventory().clearContent();p.getInventory().selected=0;p.setGameMode(GameType.SURVIVAL);if(!c.has("noAmmo")||!c.get("noAmmo").getAsBoolean())p.getInventory().setItem(9,new ItemStack(Items.ARROW,64));p.setItemInHand(c.has("offhand")&&c.get("offhand").getAsBoolean()?InteractionHand.OFF_HAND:InteractionHand.MAIN_HAND,item(c.get("item").getAsString()));if(c.has("armorHud")){p.setItemSlot(net.minecraft.world.entity.EquipmentSlot.HEAD,new ItemStack(Items.DIAMOND_HELMET));p.setItemSlot(net.minecraft.world.entity.EquipmentSlot.CHEST,new ItemStack(Items.DIAMOND_CHESTPLATE));p.setItemSlot(net.minecraft.world.entity.EquipmentSlot.LEGS,new ItemStack(Items.DIAMOND_LEGGINGS));p.setItemSlot(net.minecraft.world.entity.EquipmentSlot.FEET,new ItemStack(Items.DIAMOND_BOOTS));p.getAttribute(net.minecraft.world.entity.ai.attributes.Attributes.MAX_HEALTH).setBaseValue(60);p.setAbsorptionAmount(8);}p.setHealth(p.getMaxHealth());p.getFoodData().setFoodLevel(20);});}
    case "finish" -> {m.options.keyUse.setDown(false);write("FINISHED.json",state(m));done=true;m.stop();}
    default -> throw new IllegalArgumentException("Unknown private QA operation "+op);
   }
  }
  static void nativeKey(Minecraft m,int key){m.keyboardHandler.keyPress(m.getWindow().getWindow(),key,0,1,0);m.keyboardHandler.keyPress(m.getWindow().getWindow(),key,0,0,0);}
  static void move(Minecraft m,double x,double y)throws Exception{
   var method=net.minecraftforge.fml.util.ObfuscationReflectionHelper.findMethod(MouseHandler.class,"m_91561_",long.class,double.class,double.class);
   double rawX=x*m.getWindow().getScreenWidth()/m.getWindow().getGuiScaledWidth(),rawY=y*m.getWindow().getScreenHeight()/m.getWindow().getGuiScaledHeight();
   method.invoke(m.mouseHandler,m.getWindow().getWindow(),rawX,rawY);method.invoke(m.mouseHandler,m.getWindow().getWindow(),rawX,rawY);
  }
  static Object field(Object object,String name)throws Exception{var f=object.getClass().getDeclaredField(name);f.setAccessible(true);return f.get(object);}
  static Map<String,Object> jeiScreen(Minecraft m)throws Exception{
   var gui=(mezz.jei.gui.recipes.RecipesGui)m.screen;
   var logic=(mezz.jei.gui.recipes.IRecipeGuiLogic)field(gui,"logic");
   var report=new LinkedHashMap<String,Object>();
   report.put("category",logic.getSelectedRecipeCategory().getRecipeType().getUid().toString());report.put("title",logic.getSelectedRecipeCategory().getTitle().getString());
   report.put("page",logic.getPageString());
   var rows=new ArrayList<Object>();
   for(var o:(List<?>)field(field(gui,"layouts"),"recipeLayoutsWithButtons")){
    var layout=((mezz.jei.gui.recipes.IRecipeLayoutWithButtons<?>)o).getRecipeLayout();var r=layout.getRect();
    var slots=new ArrayList<Object>();for(var slot:layout.getRecipeSlotsView().getSlotViews()){
     var data=new LinkedHashMap<String,Object>();data.put("role",slot.getRole().toString());data.put("items",slot.getItemStacks().map(PackAcceptance::id).toList());
     if(slot instanceof mezz.jei.api.gui.ingredient.IRecipeSlotDrawable draw){var a=draw.getRect();data.put("x",r.getX()+a.getX()+8);data.put("y",r.getY()+a.getY()+8);}
     slots.add(data);
    }
    var row=new LinkedHashMap<String,Object>();row.put("slots",slots);
    if(layout.getRecipe() instanceof mezz.jei.api.recipe.vanilla.IJeiIngredientInfoRecipe info){
     row.put("description",info.getDescription().stream().map(x->x.getString()).toList());
     var wrapped=new ArrayList<Object>();for(var widget:(List<?>)field(layout,"allWidgets")){
      if(widget instanceof mezz.jei.library.gui.widgets.ScrollBoxRecipeWidget box){var contents=field(box,"contents");if(contents instanceof mezz.jei.common.gui.elements.DrawableWrappedText){
       var lines=(List<?>)field(contents,"descriptionLines");wrapped.add(Map.of("lines",lines.stream().map(x->((net.minecraft.network.chat.FormattedText)x).getString()).toList(),"height",field(contents,"height"),"visibleHeight",box.getContentAreaHeight()));
      }}
     }row.put("actualWrappedText",wrapped);
    }
    if(layout.getRecipe() instanceof net.minecraft.world.item.crafting.Recipe<?> recipe)row.put("recipe",recipe.getId().toString());rows.add(row);
   }report.put("layouts",rows);return report;
  }
  static void auditTalismans(Minecraft m,String name)throws Exception{
   var out=new LinkedHashMap<String,Object>();var r=JeiProbe.runtime.getRecipeManager();var ff=JeiProbe.runtime.getJeiHelpers().getFocusFactory();
   for(String id:TalismanDiscovery.IDS){var stack=item("dynasty:"+id);check(!stack.isEmpty(),"Registered original talisman "+id);var input=ff.createFocus(RecipeIngredientRole.INPUT,VanillaTypes.ITEM_STACK,stack);var output=ff.createFocus(RecipeIngredientRole.OUTPUT,VanillaTypes.ITEM_STACK,stack);
    var info=r.createRecipeLookup(RecipeTypes.INFORMATION).limitFocus(List.of(input)).get().toList();
    check(!info.isEmpty(),"JEI actual information lookup "+id);
    var text=info.stream().flatMap(x->x.getDescription().stream()).map(x->x.getString()).toList();
    check(text.stream().noneMatch(x->x.contains("jei.dynasty.")),"Resolved JEI descriptions "+id);
    check(!stack.getHoverName().getString().equals(stack.getDescriptionId()),"Resolved talisman name "+id);
    var craft=r.createRecipeLookup(RecipeTypes.CRAFTING).limitFocus(List.of(output)).get().map(x->x.getId().toString()).toList();
    out.put(id,Map.of("displayName",stack.getHoverName().getString(),"description",text,"recipeIds",craft,"inputCategories",r.createRecipeCategoryLookup().limitFocus(List.of(input)).get().map(x->x.getRecipeType().getUid().toString()).toList(),"outputCategories",r.createRecipeCategoryLookup().limitFocus(List.of(output)).get().map(x->x.getRecipeType().getUid().toString()).toList()));
   }
   var negative=ff.createFocus(RecipeIngredientRole.INPUT,VanillaTypes.ITEM_STACK,new ItemStack(Items.DIRT));var irrelevant=r.createRecipeLookup(RecipeTypes.INFORMATION).limitFocus(List.of(negative)).get().toList();check(irrelevant.stream().flatMap(x->x.getDescription().stream()).noneMatch(x->x.getString().contains("一次性符")||x.getString().contains("single-use talisman")),"Unrelated dirt does not receive talisman information");
   check(TalismanDiscovery.details("not_a_talisman").length==0,"Unknown talisman ID has no descriptions");
   var filter=JeiProbe.runtime.getIngredientFilter();filter.setFilterText("__cod4_no_such_talisman_927__");check(filter.getFilteredItemStacks().isEmpty(),"Native JEI negative search has no results");filter.setFilterText("");write(name+"-audit.json",out);
  }
 }
}
