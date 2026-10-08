package com.dynasty.infusion;

import mezz.jei.api.*;
import mezz.jei.api.constants.VanillaTypes;
import mezz.jei.api.gui.builder.IRecipeLayoutBuilder;
import mezz.jei.api.gui.drawable.IDrawable;
import mezz.jei.api.helpers.IGuiHelper;
import mezz.jei.api.recipe.*;
import mezz.jei.api.recipe.category.IRecipeCategory;
import mezz.jei.api.registration.*;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.registries.ForgeRegistries;

/** One entry per existing material, without enumerating every equipment combination. */
@JeiPlugin
public final class InfusionJei implements IModPlugin {
    public static final RecipeType<InfusionTraits.Trait> TYPE=RecipeType.create("dynasty","infusion",InfusionTraits.Trait.class);
    @Override public ResourceLocation getPluginUid(){return new ResourceLocation("dynasty","infusion");}
    @Override public void registerCategories(IRecipeCategoryRegistration r){r.addRecipeCategories(new Category(r.getJeiHelpers().getGuiHelper()));}
    @Override public void registerRecipes(IRecipeRegistration r){r.addRecipes(TYPE,InfusionTraits.ALL);}
    @Override public void registerRecipeCatalysts(IRecipeCatalystRegistration r){r.addRecipeCatalyst(new ItemStack(InfusionContent.TABLE_ITEM.get()),TYPE);}
    public static final class Category implements IRecipeCategory<InfusionTraits.Trait>{
        private final IDrawable background,icon;
        Category(IGuiHelper h){background=h.createBlankDrawable(170,174);icon=h.createDrawableIngredient(VanillaTypes.ITEM_STACK,new ItemStack(InfusionContent.TABLE_ITEM.get()));}
        @Override public RecipeType<InfusionTraits.Trait> getRecipeType(){return TYPE;}
        @Override public Component getTitle(){return Component.translatable("infusion.dynasty.jei");}
        @Override public IDrawable getBackground(){return background;}
        @Override public IDrawable getIcon(){return icon;}
        @Override public void setRecipe(IRecipeLayoutBuilder b,InfusionTraits.Trait t,IFocusGroup focus){b.addSlot(RecipeIngredientRole.INPUT,3,3).addItemStack(new ItemStack(ForgeRegistries.ITEMS.getValue(new ResourceLocation("dynasty",t.material())),t.count()));b.addSlot(RecipeIngredientRole.CATALYST,149,3).addItemStack(new ItemStack(InfusionContent.TABLE_ITEM.get()));}
        @Override public void draw(InfusionTraits.Trait t,mezz.jei.api.gui.ingredient.IRecipeSlotsView slots,net.minecraft.client.gui.GuiGraphics g,double x,double y){
            int line=26;line=wrap(g,t.name(),line,0x27634c);line=wrap(g,Component.translatable("infusion.dynasty.jei_types",t.applicability()),line,0x444444);line=wrap(g,t.description(),line,0x444444);line=wrap(g,Component.translatable("infusion.dynasty.trait_cost",t.cost()),line,0x444444);line=wrap(g,Component.translatable("infusion.dynasty.apply_cost"),line,0x444444);line=wrap(g,Component.translatable("infusion.dynasty.jei_gate",Component.translatable("infusion.dynasty.gate.get_jade")),line,0x444444);
            if(!t.gate().isEmpty())wrap(g,Component.translatable("infusion.dynasty.jei_gate",Component.translatable("infusion.dynasty.gate."+t.gate())),line,0x444444);
        }
        private int wrap(net.minecraft.client.gui.GuiGraphics g,Component text,int y,int color){var f=net.minecraft.client.Minecraft.getInstance().font;for(var line:f.split(text,164)){g.drawString(f,line,3,y,color,false);y+=10;}return y+2;}
    }
}
