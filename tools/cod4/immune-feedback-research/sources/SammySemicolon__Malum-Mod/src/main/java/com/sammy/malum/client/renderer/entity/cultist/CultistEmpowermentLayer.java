package com.sammy.malum.client.renderer.entity.cultist;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.sammy.malum.MalumMod;
import com.sammy.malum.client.model.mob.CultistHumanoidModel;
import com.sammy.malum.common.entity.mob.cultist.CultistMonster;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.entity.layers.RenderLayer;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.ResourceLocation;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public class CultistEmpowermentLayer<T extends CultistMonster, M extends CultistHumanoidModel<T>> extends RenderLayer<T, M> {

    public static final ResourceLocation SMALL = MalumMod.malumPath("textures/entity/cultist/empowerment_small.png");
    public static final ResourceLocation MEDIUM = MalumMod.malumPath("textures/entity/cultist/empowerment_medium.png");
    public static final ResourceLocation LARGE = MalumMod.malumPath("textures/entity/cultist/empowerment_large.png");

    private final ResourceLocation empowermentTexture;

    public CultistEmpowermentLayer(RenderLayerParent<T, M> renderer, ResourceLocation empowermentTexture) {
        super(renderer);
        this.empowermentTexture = empowermentTexture;
    }

    @Override
    public void render(PoseStack poseStack, MultiBufferSource buffer, int packedLight, T cultist, float limbSwing, float limbSwingAmount, float partialTicks, float ageInTicks, float netHeadYaw, float headPitch) {
        float visibility = cultist.empowermentVisibility;
        if (visibility > 0) {
            float delta = (float) cultist.tickCount + partialTicks;
            M model = getParentModel();
            float u = (delta * 0.02f) % 1.0F;
            float v = (delta * 0.01F) % 1.0F;
            VertexConsumer vertexconsumer = buffer.getBuffer(RenderType.energySwirl(empowermentTexture, u, v));
            model.grow(0.25f);
            model.renderToBuffer(poseStack, vertexconsumer, packedLight, OverlayTexture.NO_OVERLAY, -8355712);
            model.grow(-0.25f);
        }
    }
}