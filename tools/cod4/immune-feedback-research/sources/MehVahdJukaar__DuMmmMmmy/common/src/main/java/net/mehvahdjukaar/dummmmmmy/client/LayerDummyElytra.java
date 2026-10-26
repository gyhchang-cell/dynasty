package net.mehvahdjukaar.dummmmmmy.client;

import com.mojang.blaze3d.vertex.PoseStack;
import net.mehvahdjukaar.dummmmmmy.common.TargetDummyEntity;
import net.minecraft.client.model.geom.EntityModelSet;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.layers.ElytraLayer;

public class LayerDummyElytra extends ElytraLayer<TargetDummyEntity, TargetDummyModel<TargetDummyEntity>> {
    public LayerDummyElytra(TargetDummyRenderer renderer, EntityModelSet entityModelSet) {
        super(renderer, entityModelSet);
    }

    @Override
    public void render(PoseStack poseStack, MultiBufferSource buffer, int packedLight, TargetDummyEntity livingEntity, float limbSwing, float limbSwingAmount, float partialTicks, float ageInTicks, float netHeadYaw, float headPitch) {
       poseStack.pushPose();
       poseStack.translate(0,-12/16f,0);
       this.getParentModel().getBody().translateAndRotate(poseStack);
        super.render(poseStack, buffer, packedLight, livingEntity, limbSwing, limbSwingAmount, partialTicks, ageInTicks, netHeadYaw, headPitch);


        poseStack.popPose();
    }
}
