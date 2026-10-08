package com.dynasty.client;
import com.dynasty.entity.DynastyBosses;
import net.minecraft.client.renderer.entity.*;
import net.minecraft.resources.ResourceLocation;
public final class DragonEmperorRenderer extends MobRenderer<DynastyBosses.DragonEmperor,DragonEmperorModel> {
    private static final ResourceLocation TEXTURE=new ResourceLocation("dynasty","textures/entity/dragon_emperor.png");
    public DragonEmperorRenderer(EntityRendererProvider.Context c){super(c,new DragonEmperorModel(),1.8f);}
    @Override public ResourceLocation getTextureLocation(DynastyBosses.DragonEmperor e){return TEXTURE;}
}
