package com.dynasty.infusion;
import mezz.jei.api.*;
import mezz.jei.api.runtime.IJeiRuntime;
import mezz.jei.api.registration.IRecipeCategoryRegistration;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
@JeiPlugin
public final class InfusionJeiQa implements IModPlugin {
    static IJeiRuntime runtime;
    static InfusionJei.Category category;
    @Override public ResourceLocation getPluginUid(){return new ResourceLocation("dynasty","infusion_qa");}
    @Override public void registerCategories(IRecipeCategoryRegistration r){category=new InfusionJei.Category(r.getJeiHelpers().getGuiHelper());}
    @Override public void onRuntimeAvailable(IJeiRuntime r){runtime=r;}
    static void verify(Minecraft mc,String language)throws Exception{
        InfusionClientQa.check(runtime!=null&&runtime.getRecipeManager().createRecipeLookup(InfusionJei.TYPE).get().count()==95,"JEI runtime registered 95 recipes: "+language);
        int max=0;InfusionTraits.Trait longest=null;
        for(var t:InfusionTraits.ALL){int y=26;for(var line:InfusionJei.Category.details(t))y+=mc.font.split(line,164).size()*10+2;if(y>max){max=y;longest=t;}InfusionClientQa.check(y<=category.getHeight(),"JEI text within layout: "+t.material()+"="+y);}
        final var selected=longest;
        InfusionClientQa.capture(mc,new Screen(Component.literal("JEI")){
            @Override public void render(GuiGraphics g,int x,int y,float partial){g.fill(0,0,width,height,0xffddd5b9);g.pose().pushPose();g.pose().translate((width-170)/2f,(height-category.getHeight())/2f,0);category.draw(selected,null,g,0,0);g.pose().popPose();}
        },language+"-jei-longest",640,480,2,false);
    }
}
