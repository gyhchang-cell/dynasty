package com.yellowbrossproductions.illageandspillage.client.render.layer;

import com.mojang.blaze3d.vertex.PoseStack;
import com.yellowbrossproductions.illageandspillage.client.model.MobSpiritModel;
import com.yellowbrossproductions.illageandspillage.entities.MobSpiritEntity;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.entity.layers.EyesLayer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.LivingEntity;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public class MobSpiritEvilLayer<T extends LivingEntity> extends EyesLayer<T, MobSpiritModel<T>> {
    private static final RenderType LAYER = RenderType.eyes(new ResourceLocation("illageandspillage", "textures/entity/spiritcaller/mob_spirit_evil.png"));

    public MobSpiritEvilLayer(RenderLayerParent<T, MobSpiritModel<T>> p_i226039_1_) {
        super(p_i226039_1_);
    }

    public void render(PoseStack p_116983_, MultiBufferSource p_116984_, int p_116985_, T p_116986_, float p_116987_, float p_116988_, float p_116989_, float p_116990_, float p_116991_, float p_116992_) {
        if (p_116986_ instanceof MobSpiritEntity s) {
            if (!s.isGoodOrEvil() && !s.isSpiritcaller()) {
                super.render(p_116983_, p_116984_, p_116985_, p_116986_, p_116987_, p_116988_, p_116989_, p_116990_, p_116991_, p_116992_);
            }
        }

    }

    public RenderType renderType() {
        return LAYER;
    }
}
