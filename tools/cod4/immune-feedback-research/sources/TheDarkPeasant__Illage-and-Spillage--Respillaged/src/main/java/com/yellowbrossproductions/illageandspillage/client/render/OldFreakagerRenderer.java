package com.yellowbrossproductions.illageandspillage.client.render;

import com.mojang.blaze3d.vertex.PoseStack;
import com.yellowbrossproductions.illageandspillage.client.model.OldFreakagerModel;
import com.yellowbrossproductions.illageandspillage.client.render.layer.old_freakager.*;
import com.yellowbrossproductions.illageandspillage.entities.OldFreakagerEntity;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.client.renderer.entity.layers.CustomHeadLayer;
import net.minecraft.client.renderer.entity.layers.ItemInHandLayer;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public class OldFreakagerRenderer extends MobRenderer<OldFreakagerEntity, OldFreakagerModel<OldFreakagerEntity>> {
    private static final ResourceLocation TEXTURE = new ResourceLocation("illageandspillage", "textures/entity/freakager/old/freakager.png");

    public OldFreakagerRenderer(EntityRendererProvider.Context renderManagerIn) {
        super(renderManagerIn, new OldFreakagerModel<>(renderManagerIn.bakeLayer(OldFreakagerModel.LAYER_LOCATION)), 0.5F);
        this.addLayer(new OldFreakagerArmorLayer<>(this));
        this.addLayer(new OldFreakagerVillaFace1Layer<>(this, renderManagerIn.getModelSet()));
        this.addLayer(new OldFreakagerVillaFace2Layer<>(this, renderManagerIn.getModelSet()));
        this.addLayer(new OldFreakagerVillaFace3Layer<>(this, renderManagerIn.getModelSet()));
        this.addLayer(new OldFreakagerVillaFace4Layer<>(this, renderManagerIn.getModelSet()));
        this.addLayer(new CustomHeadLayer<>(this, renderManagerIn.getModelSet(), renderManagerIn.getItemInHandRenderer()));
        this.addLayer(new ItemInHandLayer<>(this, renderManagerIn.getItemInHandRenderer()) {
            public void render(PoseStack p_116352_, MultiBufferSource p_116353_, int p_116354_, OldFreakagerEntity p_116355_, float p_116356_, float p_116357_, float p_116358_, float p_116359_, float p_116360_, float p_116361_) {
                if (p_116355_.shouldShowArms()) {
                    super.render(p_116352_, p_116353_, p_116354_, p_116355_, p_116356_, p_116357_, p_116358_, p_116359_, p_116360_, p_116361_);
                }

            }
        });
    }

    public ResourceLocation getTextureLocation(OldFreakagerEntity p_110775_1_) {
        return TEXTURE;
    }
}
