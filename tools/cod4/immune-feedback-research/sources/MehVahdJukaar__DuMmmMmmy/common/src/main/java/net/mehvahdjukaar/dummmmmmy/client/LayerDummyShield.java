package net.mehvahdjukaar.dummmmmmy.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import net.mehvahdjukaar.dummmmmmy.common.TargetDummyEntity;
import net.minecraft.client.model.geom.ModelLayers;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.renderer.ItemInHandRenderer;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.entity.layers.ItemInHandLayer;
import net.minecraft.world.entity.HumanoidArm;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;

public class LayerDummyShield extends ItemInHandLayer<TargetDummyEntity, TargetDummyModel<TargetDummyEntity>> {

    private final ItemInHandRenderer itemInHandRenderer;

    public LayerDummyShield(RenderLayerParent<TargetDummyEntity, TargetDummyModel<TargetDummyEntity>> renderer,

                            ItemInHandRenderer itemInHandRenderer) {
        super(renderer, itemInHandRenderer);
        this.itemInHandRenderer = itemInHandRenderer;
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
            boolean left = arm == HumanoidArm.LEFT;
            if(left)return;

            boolean isBlocking = livingEntity.isBlocking();

            poseStack.pushPose();

            this.getParentModel().translateToHand(arm, poseStack);
            poseStack.mulPose(Axis.XP.rotationDegrees(-90.0F));
            float angle = 90 + (isBlocking ? 0 : -30);
            poseStack.mulPose(Axis.ZP.rotationDegrees((left ? -angle : angle)));


            poseStack.translate(isBlocking ? 0 :-1/32f, 3 / 16f, 4 / 16f);
            this.itemInHandRenderer.renderItem(livingEntity, itemStack, displayContext, left, poseStack, buffer, packedLight);
            poseStack.popPose();
        }

    }

}

