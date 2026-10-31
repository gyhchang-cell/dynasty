package com.sammy.malum.client.renderer.entity.cultist.evangelist;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import com.sammy.malum.client.model.mob.evangelist.EvangelistModel;
import com.sammy.malum.common.entity.mob.cultist.evangelist.EvangelistCultist;
import net.minecraft.client.renderer.ItemInHandRenderer;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.entity.layers.ItemInHandLayer;
import net.minecraft.world.entity.HumanoidArm;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;

public class EvangelistItemInHandLayer extends ItemInHandLayer<EvangelistCultist, EvangelistModel> {
    public EvangelistItemInHandLayer(RenderLayerParent<EvangelistCultist, EvangelistModel> renderer, ItemInHandRenderer itemInHandRenderer) {
        super(renderer, itemInHandRenderer);
    }

    @Override
    protected void renderArmWithItem(
            LivingEntity livingEntity,
            ItemStack itemStack,
            ItemDisplayContext displayContext,
            HumanoidArm arm,
            PoseStack poseStack,
            MultiBufferSource buffer,
            int packedLight
    ) {
        if (!itemStack.isEmpty()) {
            poseStack.pushPose();
            this.getParentModel().translateToHand(arm, poseStack);
            poseStack.mulPose(Axis.XP.rotationDegrees(-90.0F));
            poseStack.translate(0f, 0.35F, 0f);
            poseStack.mulPose(Axis.YP.rotationDegrees(180.0F));
            boolean flag = arm == HumanoidArm.LEFT;
            itemInHandRenderer.renderItem(livingEntity, itemStack, displayContext, flag, poseStack, buffer, packedLight);
            poseStack.popPose();
        }
    }
}
