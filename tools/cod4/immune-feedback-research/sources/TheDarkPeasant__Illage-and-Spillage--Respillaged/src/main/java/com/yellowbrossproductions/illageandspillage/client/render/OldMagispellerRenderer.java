package com.yellowbrossproductions.illageandspillage.client.render;

import com.mojang.blaze3d.vertex.PoseStack;
import com.yellowbrossproductions.illageandspillage.client.model.OldMagispellerModel;
import com.yellowbrossproductions.illageandspillage.client.render.layer.old_magispeller.OldMagispellerArmorLayer;
import com.yellowbrossproductions.illageandspillage.client.render.layer.old_magispeller.OldMagispellerFakerLayer;
import com.yellowbrossproductions.illageandspillage.entities.OldMagispellerEntity;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.client.renderer.entity.layers.CustomHeadLayer;
import net.minecraft.client.renderer.entity.layers.ItemInHandLayer;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

import java.util.Calendar;

@OnlyIn(Dist.CLIENT)
public class OldMagispellerRenderer extends MobRenderer<OldMagispellerEntity, OldMagispellerModel<OldMagispellerEntity>> {
    private static final ResourceLocation TEXTURE = new ResourceLocation("illageandspillage", "textures/entity/magispeller/magispeller.png");
    private static final ResourceLocation NOTHING = new ResourceLocation("illageandspillage", "textures/entity/magispeller/magispeller_nothing.png");
    private static final ResourceLocation CHRISTMAS = new ResourceLocation("illageandspillage", "textures/entity/magispeller/christmas/magispeller_christmas.png");

    public OldMagispellerRenderer(EntityRendererProvider.Context renderManagerIn) {
        super(renderManagerIn, new OldMagispellerModel<>(renderManagerIn.bakeLayer(OldMagispellerModel.LAYER_LOCATION)), 0.5F);
        this.addLayer(new OldMagispellerFakerLayer<>(this));
        this.addLayer(new OldMagispellerArmorLayer<>(this));
        this.addLayer(new CustomHeadLayer<>(this, renderManagerIn.getModelSet(), renderManagerIn.getItemInHandRenderer()));
        this.addLayer(new ItemInHandLayer<>(this, renderManagerIn.getItemInHandRenderer()) {
            public void render(PoseStack p_116352_, MultiBufferSource p_116353_, int p_116354_, OldMagispellerEntity p_116355_, float p_116356_, float p_116357_, float p_116358_, float p_116359_, float p_116360_, float p_116361_) {
                if (p_116355_.isWavingArms() || p_116355_.isSpinning() || p_116355_.isVindicatorAttacking() || p_116355_.isCrossbowAttacking() || p_116355_.isGoingWEEEEEEEEEEE()) {
                    super.render(p_116352_, p_116353_, p_116354_, p_116355_, p_116356_, p_116357_, p_116358_, p_116359_, p_116360_, p_116361_);
                }

            }
        });
    }

    public ResourceLocation getTextureLocation(OldMagispellerEntity p_110775_1_) {
        if (p_110775_1_.isFaking()) {
            return NOTHING;
        } else {
            Calendar calendar = Calendar.getInstance();
            return calendar.get(Calendar.MONTH) + 1 == 12 ? CHRISTMAS : TEXTURE;
        }
    }
}
