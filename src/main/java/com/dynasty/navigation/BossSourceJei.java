package com.dynasty.navigation;

import com.dynasty.DynastyItems;
import mezz.jei.api.*;
import mezz.jei.api.constants.VanillaTypes;
import mezz.jei.api.gui.builder.IRecipeLayoutBuilder;
import mezz.jei.api.gui.drawable.IDrawable;
import mezz.jei.api.recipe.*;
import mezz.jei.api.recipe.category.IRecipeCategory;
import mezz.jei.api.registration.*;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.SpawnEggItem;
import net.minecraftforge.registries.ForgeRegistries;

/** A searchable OUTPUT recipe, so R on a token actually opens its mob source. */
@JeiPlugin
public final class BossSourceJei implements IModPlugin {
    public record Source(String mob,ItemStack drop,String location){}
    public static final RecipeType<Source> TYPE=RecipeType.create("dynasty","boss_drops",Source.class);
    @Override public ResourceLocation getPluginUid(){return new ResourceLocation("dynasty","boss_drops");}
    @Override public void registerCategories(IRecipeCategoryRegistration r){r.addRecipeCategories(new Category(r.getJeiHelpers().getGuiHelper()));}
    @Override public void registerRecipes(IRecipeRegistration r){r.addRecipes(TYPE,java.util.List.of(
        new Source("nine_heaven_general",new ItemStack(DynastyItems.SKY_TOKEN.get()),"进入九霄天界，在九霄仙岛寻找九霄天将。击败后必掉1枚；首次不需要令牌。"),
        new Source("dragon_king",new ItemStack(DynastyItems.SEA_TOKEN.get()),"进入东海龙宫，寻找东海龙王。击败后必掉1枚。")));}
    public static final class Category implements IRecipeCategory<Source>{
        private final IDrawable bg,icon;
        Category(mezz.jei.api.helpers.IGuiHelper h){bg=h.createBlankDrawable(160,100);icon=h.createDrawableIngredient(VanillaTypes.ITEM_STACK,new ItemStack(DynastyItems.SKY_TOKEN.get()));}
        public RecipeType<Source> getRecipeType(){return TYPE;}public Component getTitle(){return Component.literal("生物掉落");}
        public IDrawable getBackground(){return bg;}public IDrawable getIcon(){return icon;}
        public void setRecipe(IRecipeLayoutBuilder b,Source s,IFocusGroup f){
            var type=ForgeRegistries.ENTITY_TYPES.getValue(new ResourceLocation("dynasty",s.mob()));var egg=SpawnEggItem.byId(type);
            if(egg!=null)b.addSlot(RecipeIngredientRole.INPUT,8,5).addItemStack(new ItemStack(egg));
            b.addSlot(RecipeIngredientRole.OUTPUT,132,5).addItemStack(s.drop());
        }
        public void draw(Source s,mezz.jei.api.gui.ingredient.IRecipeSlotsView slots,net.minecraft.client.gui.GuiGraphics g,double x,double y){
            var font=net.minecraft.client.Minecraft.getInstance().font;int line=29;
            var title=Component.translatable("entity.dynasty."+s.mob());g.drawString(font,title,3,line,0x333333,false);line+=14;
            for(var t:font.split(Component.literal(s.location()),154)){g.drawString(font,t,3,line,0x333333,false);line+=10;}
        }
    }
}
