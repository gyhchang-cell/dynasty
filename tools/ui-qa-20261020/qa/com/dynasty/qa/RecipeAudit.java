package com.dynasty.qa;
import net.minecraft.client.*;
import net.minecraft.world.item.*;
import net.minecraft.world.item.crafting.*;
import net.minecraft.world.inventory.*;
import java.nio.file.*;
class RecipeAudit {static final Path OUT=UiAudit.OUT;
 static void audit(Minecraft m)throws Exception{
  var report=new StringBuilder();var manager=m.level.getRecipeManager();int recipes=0,crafted=0,woodVariants=0;var menu=new AbstractContainerMenu(null,0){public ItemStack quickMoveStack(net.minecraft.world.entity.player.Player p,int i){return ItemStack.EMPTY;}public boolean stillValid(net.minecraft.world.entity.player.Player p){return true;}};
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
    crafted++;
    var planks=Ingredient.of(net.minecraft.tags.ItemTags.PLANKS).getItems();
    var woodSlots=new java.util.ArrayList<Integer>();for(int i=0;i<list.size();i++)if(java.util.Arrays.stream(list.get(i).getItems()).anyMatch(x->x.is(net.minecraft.tags.ItemTags.PLANKS)))woodSlots.add(c instanceof ShapedRecipe sh?(i/sh.getWidth())*3+i%sh.getWidth():i);
    for(var plank:planks)if(!woodSlots.isEmpty()){for(int slot:woodSlots)grid.setItem(slot,plank.copy());if(!c.matches(grid,m.level))report.append("WOOD_VARIANT_FAIL "+r.getId()+" "+plank+"\n");else woodVariants++;}
    var chosen=manager.getRecipeFor(RecipeType.CRAFTING,grid,m.level);
    if(chosen.isEmpty()||!ItemStack.isSameItemSameTags(chosen.get().assemble(grid,m.level.registryAccess()),c.assemble(grid,m.level.registryAccess())))report.append("SHADOWED "+r.getId()+" BY "+chosen.map(x->x.getId().toString()).orElse("NONE")+"\n");
   }
  }
  int items=0,missing=0;
  for(var id:net.minecraftforge.registries.ForgeRegistries.ITEMS.getKeys())if(id.getNamespace().equals("dynasty")){
   items++;var stack=new ItemStack(net.minecraftforge.registries.ForgeRegistries.ITEMS.getValue(id));var model=m.getItemRenderer().getModel(stack,m.level,m.player,0);
   if(model==m.getModelManager().getMissingModel()||!model.isCustomRenderer()&&model.getParticleIcon().contents().name().toString().equals("minecraft:missingno")){missing++;report.append("MISSING_MODEL "+id+"\n");}
   if(stack.getHoverName().getString().startsWith("item.dynasty.")||stack.getHoverName().getString().startsWith("block.dynasty."))report.append("MISSING_NAME "+id+"\n");
  }
  int packNames=0;for(var id:net.minecraftforge.registries.ForgeRegistries.ITEMS.getKeys()){var stack=new ItemStack(net.minecraftforge.registries.ForgeRegistries.ITEMS.getValue(id));if(!stack.isEmpty()){packNames++;if(!net.minecraft.locale.Language.getInstance().has(stack.getDescriptionId()))report.append("PACK_MISSING_NAME "+id+" "+stack.getDescriptionId()+"\n");}}
  String errors=report.toString();
  report.append("RECIPES "+recipes+" CRAFTED "+crafted+" ITEMS "+items+" MISSING_MODELS "+missing+" WOOD_VARIANTS "+woodVariants+" PACK_ITEM_NAMES "+packNames+"\n");
  Files.writeString(OUT.resolve("audit.txt"),report);
  UiAudit.check(errors.isBlank(),"No native recipe, wood variant, model or pack item translation failures: "+errors);
 }
}
