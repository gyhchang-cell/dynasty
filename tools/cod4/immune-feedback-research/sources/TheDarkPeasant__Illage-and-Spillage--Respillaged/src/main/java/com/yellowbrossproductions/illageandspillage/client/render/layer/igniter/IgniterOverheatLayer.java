package com.yellowbrossproductions.illageandspillage.client.render.layer.igniter;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.yellowbrossproductions.illageandspillage.client.model.IgniterModel;
import com.yellowbrossproductions.illageandspillage.entities.IgniterEntity;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.LivingEntityRenderer;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.entity.layers.RenderLayer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.LivingEntity;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public class IgniterOverheatLayer<T extends LivingEntity> extends RenderLayer<T, IgniterModel<T>> {
    private static final RenderType LAYER1 = RenderType.eyes(new ResourceLocation("illageandspillage", "textures/entity/igniter/heat_layer1.png"));
    private static final RenderType LAYER2 = RenderType.eyes(new ResourceLocation("illageandspillage", "textures/entity/igniter/heat_layer2.png"));
    private static final RenderType LAYER3 = RenderType.eyes(new ResourceLocation("illageandspillage", "textures/entity/igniter/heat_layer3.png"));
    private static final RenderType LAYER4 = RenderType.eyes(new ResourceLocation("illageandspillage", "textures/entity/igniter/heat_layer4.png"));
    private static final RenderType LAYER5 = RenderType.eyes(new ResourceLocation("illageandspillage", "textures/entity/igniter/heat_layer5.png"));

    public IgniterOverheatLayer(RenderLayerParent<T, IgniterModel<T>> p_i226039_1_) {
        super(p_i226039_1_);
    }

    public RenderType getLayer(float percent, IgniterEntity igniter) {
        if (igniter.isOverheated()) {
            if (percent <= 0.2F) {
                return LAYER1;
            }
            if (percent > 0.2F && percent <= 0.4F) {
                return LAYER2;
            }
            if (percent > 0.4F && percent <= 0.6F) {
                return LAYER3;
            }
            if (percent > 0.6F && percent <= 0.8F) {
                return LAYER4;
            }
            if (percent > 0.8F) {
                return LAYER5;
            }
        } else {
            if (percent > 0.2F && percent <= 0.4F) {
                return LAYER1;
            }
            if (percent > 0.4F && percent <= 0.6F) {
                return LAYER2;
            }
            if (percent > 0.6F && percent <= 0.8F) {
                return LAYER3;
            }
            if (percent > 0.8F) {
                return LAYER4;
            }
        }

        return LAYER1;
    }

    @Override
    public void render(PoseStack poseStack, MultiBufferSource bufferSource, int packedLight, T entity, float limbSwing, float limbSwingAmount, float partialTicks, float ageInTicks, float netHeadYaw, float headPitch) {
        if (entity instanceof IgniterEntity igniter && !igniter.isInvisible()) {
            float percent = igniter.isOverheated() ? igniter.getCooldownTicks() / IgniterEntity.COOLDOWN_TIME : igniter.getFireballsShot() / IgniterEntity.FIREBALLS_TO_OVERHEAT;
            if (percent > 0.2F || igniter.isOverheated()) {
                VertexConsumer vertexConsumer = bufferSource.getBuffer(this.getLayer(percent, igniter));
                this.getParentModel().renderToBuffer(poseStack, vertexConsumer, packedLight, LivingEntityRenderer.getOverlayCoords(entity, 0.0F), 1.0F, 1.0F, 1.0F, 1.0F);
            }
        }
    }

}
