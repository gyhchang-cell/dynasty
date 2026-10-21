package com.dynasty.qa;
import net.minecraft.client.*;
import net.minecraft.client.gui.screens.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.level.*;
import net.minecraft.world.level.levelgen.WorldOptions;
import net.minecraft.world.level.levelgen.presets.WorldPresets;
import net.minecraft.world.Difficulty;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraft.world.item.*;
import net.minecraft.world.item.crafting.*;
import net.minecraft.world.inventory.*;
import java.nio.file.*;
import java.util.*;
@Mod("dynastyaudit")
public class PlayAudit {
 public PlayAudit(){System.out.println("AUDIT_HELPER_CONSTRUCTED");}
 @Mod.EventBusSubscriber(modid="dynastyaudit",value=net.minecraftforge.api.distmarker.Dist.CLIENT)
 public static class Client {
 static boolean started,done;static int frame,step;static final Path OUT=Path.of(System.getProperty("dynasty.audit.output"));
 static void shot(Minecraft m,String n){Screenshot.grab(OUT.toFile(),n,m.getMainRenderTarget(),msg->{});}
 @SubscribeEvent public static void tick(TickEvent.RenderTickEvent e){
  if(done||e.phase!=TickEvent.Phase.END)return;var m=Minecraft.getInstance();
  try{
   if(++frame%300==0){Files.createDirectories(OUT);Files.writeString(OUT.resolve("state.txt"),"screen="+(m.screen==null?"null":m.screen.getClass().getName())+" overlay="+m.getOverlay()+" started="+started+" step="+step);shot(m,"state.png");}
   if(m.getOverlay()!=null)return;
   if(m.screen instanceof AccessibilityOnboardingScreen)m.setScreen(new TitleScreen());
   if(!started&&m.screen instanceof TitleScreen){started=true;Files.createDirectories(OUT);
    var rules=new GameRules();rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false,null);rules.getRule(GameRules.RULE_NATURAL_REGENERATION).set(false,null);
    m.createWorldOpenFlows().createFreshLevel("audit-only",new LevelSettings("Disposable audit",GameType.SURVIVAL,false,Difficulty.NORMAL,true,rules,WorldDataConfiguration.DEFAULT),new WorldOptions(31,false,false),r->r.registryOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.FLAT).createWorldDimensions());return;
   }
   if(m.player==null||m.level==null||++frame<100)return;
   if(step==0){m.setScreen(null);var id=m.player.getUUID();m.getSingleplayerServer().execute(()->{var p=m.getSingleplayerServer().getPlayerList().getPlayer(id);p.getAttribute(net.minecraft.world.entity.ai.attributes.Attributes.MAX_HEALTH).setBaseValue(36);p.setHealth(27);});audit(m);step++;frame=0;}
   else if(step==1){shot(m,"full-pack-health.png");com.dynasty.navigation.CreatureCompassScreen.open();step++;frame=0;}
   else if(step==2){shot(m,"full-pack-creature-compass.png");if(JeiProbe.runtime==null)throw new AssertionError("JEI absent");
    var f=JeiProbe.runtime.getJeiHelpers().getFocusFactory().createFocus(mezz.jei.api.recipe.RecipeIngredientRole.OUTPUT,mezz.jei.api.constants.VanillaTypes.ITEM_STACK,new ItemStack(com.dynasty.DynastyItems.SKY_TOKEN.get()));JeiProbe.runtime.getRecipesGui().show(List.of(f));step++;frame=0;
   }else if(step==3){shot(m,"full-pack-sky-token.png");m.setScreen(new FixtureScreen());step++;frame=0;
   }else if(step==4){shot(m,"item-and-block-fixtures.png");Files.writeString(OUT.resolve("COMPLETE.txt"),"Full production mod list client audit completed. Inspect report and screenshots; completion does not mean every assertion passed.");done=true;m.stop();}
  }catch(Throwable ex){try{Files.writeString(OUT.resolve("FAIL.txt"),ex.toString());}catch(Exception ignored){}done=true;m.stop();}
 }
 static class FixtureScreen extends Screen {
  FixtureScreen(){super(net.minecraft.network.chat.Component.literal("贴图实绘检查"));}
  public void render(net.minecraft.client.gui.GuiGraphics g,int x,int y,float p){renderBackground(g);g.drawString(font,title,20,20,0xFFFFFF);
   String[] ids={"cauldron_bone_ritual","cauldron_abyss_oil","marshal_oath_socket","taiqing_ancient_sword_case","longyin_zhanma_duanyue_dao","zhanlu_rendao_bamian_jian","evocation_talisman"};
   for(int i=0;i<ids.length;i++){var item=net.minecraftforge.registries.ForgeRegistries.ITEMS.getValue(new net.minecraft.resources.ResourceLocation("dynasty",ids[i]));int yy=55+i*42;g.pose().pushPose();g.pose().translate(24,yy,0);g.pose().scale(2,2,2);g.renderItem(new ItemStack(item),0,0);g.pose().popPose();g.drawString(font,new ItemStack(item).getHoverName(),70,yy+8,0xFFFFFF);}
  }
 }
 static void audit(Minecraft m)throws Exception{
  var report=new StringBuilder();var manager=m.level.getRecipeManager();int recipes=0,crafted=0;var menu=new AbstractContainerMenu(null,0){public ItemStack quickMoveStack(net.minecraft.world.entity.player.Player p,int i){return ItemStack.EMPTY;}public boolean stillValid(net.minecraft.world.entity.player.Player p){return true;}};
  for(var r:manager.getRecipes())if(r.getId().getNamespace().equals("dynasty")){
   recipes++;
   if(r instanceof SmithingTransformRecipe st){
    var buf=new net.minecraft.network.FriendlyByteBuf(io.netty.buffer.Unpooled.buffer());
    ((net.minecraft.world.item.crafting.RecipeSerializer<SmithingTransformRecipe>)st.getSerializer()).toNetwork(buf,st);
    var grid=new net.minecraft.world.SimpleContainer(3);
    for(int i=0;i<3;i++){var opts=Ingredient.fromNetwork(buf).getItems();if(opts.length>0)grid.setItem(i,opts[0].copy());}
    buf.release();var chosen=manager.getRecipeFor(RecipeType.SMITHING,grid,m.level);
    if(!st.matches(grid,m.level)||chosen.isEmpty()||!ItemStack.isSameItemSameTags(chosen.get().assemble(grid,m.level.registryAccess()),st.assemble(grid,m.level.registryAccess())))report.append("SMITHING_SHADOWED "+r.getId()+"\n");
   }
   for(var ing:r.getIngredients())if(ing!=Ingredient.EMPTY&&ing.getItems().length==0)report.append("EMPTY_INGREDIENT "+r.getId()+"\n");
   if(r instanceof CraftingRecipe c && !c.isSpecial()){
    var grid=new TransientCraftingContainer(menu,3,3);var list=c.getIngredients();
    for(int i=0;i<list.size();i++){var opts=list.get(i).getItems();int slot=c instanceof ShapedRecipe sh?(i/sh.getWidth())*3+i%sh.getWidth():i;if(opts.length>0)grid.setItem(slot,opts[0].copy());}
    if(!c.matches(grid,m.level)){report.append("MATCH_FAIL "+r.getId()+"\n");continue;}
    crafted++;var chosen=manager.getRecipeFor(RecipeType.CRAFTING,grid,m.level);
    if(chosen.isEmpty()||!ItemStack.isSameItemSameTags(chosen.get().assemble(grid,m.level.registryAccess()),c.assemble(grid,m.level.registryAccess())))report.append("SHADOWED "+r.getId()+" BY "+chosen.map(x->x.getId().toString()).orElse("NONE")+"\n");
   }
  }
  int items=0,missing=0;
  for(var id:net.minecraftforge.registries.ForgeRegistries.ITEMS.getKeys())if(id.getNamespace().equals("dynasty")){
   items++;var stack=new ItemStack(net.minecraftforge.registries.ForgeRegistries.ITEMS.getValue(id));var model=m.getItemRenderer().getModel(stack,m.level,m.player,0);
   if(model==m.getModelManager().getMissingModel()||!model.isCustomRenderer()&&model.getParticleIcon().contents().name().toString().equals("minecraft:missingno")){missing++;report.append("MISSING_MODEL "+id+"\n");}
   if(stack.getHoverName().getString().startsWith("item.dynasty.")||stack.getHoverName().getString().startsWith("block.dynasty."))report.append("MISSING_NAME "+id+"\n");
  }
  report.append("RECIPES "+recipes+" CRAFTED "+crafted+" ITEMS "+items+" MISSING_MODELS "+missing+"\n");
  Files.writeString(OUT.resolve("audit.txt"),report);
 }
 }
}
