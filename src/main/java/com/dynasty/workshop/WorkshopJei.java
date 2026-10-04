package com.dynasty.workshop;

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

/** Optional integration: JEI owns loading this annotated class, including on dedicated servers. */
@JeiPlugin
public final class WorkshopJei implements IModPlugin {
    private static final RecipeType<WorkshopRecipes.Recipe> TYPE=RecipeType.create("dynasty","workshop",WorkshopRecipes.Recipe.class);
    @Override public ResourceLocation getPluginUid(){return new ResourceLocation("dynasty","workshop");}
    @Override public void registerCategories(IRecipeCategoryRegistration r){r.addRecipeCategories(new Category(r.getJeiHelpers().getGuiHelper()));}
    @Override public void registerRecipes(IRecipeRegistration r){r.addRecipes(TYPE,WorkshopRecipes.ALL);}
    @Override public void registerRecipeCatalysts(IRecipeCatalystRegistration r){for(var recipe:WorkshopRecipes.ALL)r.addRecipeCatalyst(new WorkshopRecipes.Cost("dynasty:"+recipe.station(),1).stack(),TYPE);}
    private static final class Category implements IRecipeCategory<WorkshopRecipes.Recipe>{
        final IDrawable background,icon;
        Category(IGuiHelper h){background=h.createBlankDrawable(162,62);icon=h.createDrawableIngredient(VanillaTypes.ITEM_STACK,new WorkshopRecipes.Cost("dynasty:marrow_vat",1).stack());}
        @Override public RecipeType<WorkshopRecipes.Recipe> getRecipeType(){return TYPE;}
        @Override public Component getTitle(){return Component.translatable("jei.dynasty.workshop");}
        @Override public IDrawable getBackground(){return background;}
        @Override public IDrawable getIcon(){return icon;}
        @Override public void setRecipe(IRecipeLayoutBuilder b,WorkshopRecipes.Recipe r,IFocusGroup focus){
            int x=4;for(var cost:r.costs()){b.addSlot(RecipeIngredientRole.INPUT,x,7).addItemStack(cost.stack());x+=22;}
            b.addSlot(RecipeIngredientRole.CATALYST,91,7).addItemStack(new WorkshopRecipes.Cost("dynasty:"+r.station(),1).stack());
            b.addSlot(RecipeIngredientRole.OUTPUT,136,7).addItemStack(r.result());
        }
        @Override public void draw(WorkshopRecipes.Recipe r,mezz.jei.api.gui.ingredient.IRecipeSlotsView slots,net.minecraft.client.gui.GuiGraphics g,double x,double y){
            var font=net.minecraft.client.Minecraft.getInstance().font;
            g.drawString(font,"→",76,11,0x444444,false);g.drawString(font,"→",116,11,0x444444,false);
            g.drawWordWrap(font,Component.translatable("jei.dynasty.workshop.steps"),2,32,158,0x444444);
        }
    }
}
