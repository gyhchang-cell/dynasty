package com.yellowbrossproductions.illageandspillage.client.model;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.yellowbrossproductions.illageandspillage.client.model.animation.OldRagnoAnimation;
import com.yellowbrossproductions.illageandspillage.entities.OldRagnoEntity;
import net.minecraft.client.model.HierarchicalModel;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;

public class OldRagnoModel<T extends Entity> extends HierarchicalModel<T> {
    public static final ModelLayerLocation LAYER_LOCATION = new ModelLayerLocation(new ResourceLocation("illageandspillage", "old_ragno"), "main");
    private final ModelPart root;
    private final ModelPart ragno_body;

    public OldRagnoModel(ModelPart root) {
        this.root = root;
        this.ragno_body = root.getChild("ragno_body");
    }

    public static LayerDefinition createBodyLayer() {
        MeshDefinition meshdefinition = new MeshDefinition();
        PartDefinition partdefinition = meshdefinition.getRoot();
        PartDefinition ragno_body = partdefinition.addOrReplaceChild("ragno_body", CubeListBuilder.create().texOffs(56, 62).addBox(-6.0F, -7.0F, -7.0F, 12.0F, 13.0F, 18.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, -5.0F, 3.5F, 0.0873F, 0.0F, 0.0F));
        PartDefinition neck = ragno_body.addOrReplaceChild("neck", CubeListBuilder.create().texOffs(0, 58).addBox(-5.0F, -5.0F, -12.0F, 10.0F, 10.0F, 12.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 0.0F, -3.5F));
        neck.addOrReplaceChild("ragno_head", CubeListBuilder.create().texOffs(64, 26).addBox(-8.0F, -20.0F, -14.0F, 16.0F, 20.0F, 16.0F, new CubeDeformation(0.0F)).texOffs(64, 26).addBox(-2.0F, -6.0F, -18.0F, 4.0F, 8.0F, 4.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 9.0F, -12.0F, -0.0873F, 0.0F, 0.0F));
        ragno_body.addOrReplaceChild("abdomen", CubeListBuilder.create().texOffs(0, 93).addBox(-12.0F, -12.0F, 0.0F, 24.0F, 24.0F, 24.0F, new CubeDeformation(0.0F)).texOffs(0, 141).addBox(-11.0F, -11.0F, 24.0F, 22.0F, 22.0F, 4.0F, new CubeDeformation(0.0F)).texOffs(84, 93).addBox(-10.0F, -10.0F, 28.0F, 20.0F, 20.0F, 2.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, -1.0F, 7.0F, -0.3491F, 0.0F, 0.0F));
        PartDefinition leg1 = ragno_body.addOrReplaceChild("leg1", CubeListBuilder.create().texOffs(0, 184).addBox(0.0F, -3.0F, -3.0F, 12.0F, 6.0F, 6.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(3.0F, 1.0F, -4.0F, 0.0F, 0.4363F, -0.2618F));
        PartDefinition knee1 = leg1.addOrReplaceChild("knee1", CubeListBuilder.create().texOffs(0, 167).addBox(0.0F, -1.5F, -1.5F, 16.0F, 3.0F, 3.0F, new CubeDeformation(0.0F)), PartPose.offset(12.0F, 0.0F, 0.0F));
        knee1.addOrReplaceChild("kneeee1", CubeListBuilder.create().texOffs(0, 173).addBox(0.0F, -1.0F, -1.0F, 48.0F, 2.0F, 2.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(16.0F, 0.0F, 0.0F, 0.0F, 0.0F, 1.1345F));
        PartDefinition leg2 = ragno_body.addOrReplaceChild("leg2", CubeListBuilder.create().texOffs(0, 184).addBox(0.0F, -3.0F, -3.0F, 12.0F, 6.0F, 6.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(3.0F, 1.0F, -4.0F, 0.0F, -0.4363F, -0.2618F));
        PartDefinition knee2 = leg2.addOrReplaceChild("knee2", CubeListBuilder.create().texOffs(0, 167).addBox(0.0F, -1.5F, -1.5F, 16.0F, 3.0F, 3.0F, new CubeDeformation(0.0F)), PartPose.offset(12.0F, 0.0F, 0.0F));
        knee2.addOrReplaceChild("kneeee2", CubeListBuilder.create().texOffs(0, 173).addBox(0.0F, -1.0F, -1.0F, 48.0F, 2.0F, 2.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(16.0F, 0.0F, 0.0F, 0.0F, 0.0F, 1.1345F));
        PartDefinition leg3 = ragno_body.addOrReplaceChild("leg3", CubeListBuilder.create().texOffs(0, 184).addBox(0.0F, -3.0F, -3.0F, 12.0F, 6.0F, 6.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(3.0F, 3.0F, 5.0F, 0.0F, 0.4363F, -0.0873F));
        PartDefinition knee3 = leg3.addOrReplaceChild("knee3", CubeListBuilder.create().texOffs(0, 167).addBox(0.0F, -1.5F, -1.5F, 16.0F, 3.0F, 3.0F, new CubeDeformation(0.0F)), PartPose.offset(12.0F, 0.0F, 0.0F));
        knee3.addOrReplaceChild("kneeee3", CubeListBuilder.create().texOffs(0, 177).addBox(0.0F, -1.0F, -1.0F, 40.0F, 2.0F, 2.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(16.0F, 0.0F, 0.0F, 0.0F, 0.0F, 1.0472F));
        PartDefinition leg4 = ragno_body.addOrReplaceChild("leg4", CubeListBuilder.create().texOffs(0, 184).addBox(0.0F, -3.0F, -3.0F, 12.0F, 6.0F, 6.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(3.0F, 3.0F, 5.0F, 0.0F, -0.4363F, -0.0873F));
        PartDefinition knee4 = leg4.addOrReplaceChild("knee4", CubeListBuilder.create().texOffs(0, 167).addBox(0.0F, -1.5F, -1.5F, 16.0F, 3.0F, 3.0F, new CubeDeformation(0.0F)), PartPose.offset(12.0F, 0.0F, 0.0F));
        knee4.addOrReplaceChild("kneeee4", CubeListBuilder.create().texOffs(0, 177).addBox(0.0F, -1.0F, -1.0F, 40.0F, 2.0F, 2.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(16.0F, 0.0F, 0.0F, 0.0F, 0.0F, 1.0472F));
        PartDefinition leg5 = ragno_body.addOrReplaceChild("leg5", CubeListBuilder.create().texOffs(0, 184).addBox(-12.0F, -3.0F, -3.0F, 12.0F, 6.0F, 6.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(-4.0F, 1.0F, -4.0F, 0.0F, -0.4363F, 0.2618F));
        PartDefinition knee5 = leg5.addOrReplaceChild("knee5", CubeListBuilder.create().texOffs(0, 167).addBox(-16.0F, -1.5F, -1.5F, 16.0F, 3.0F, 3.0F, new CubeDeformation(0.0F)), PartPose.offset(-12.0F, 0.0F, 0.0F));
        knee5.addOrReplaceChild("kneeee5", CubeListBuilder.create().texOffs(0, 173).addBox(-48.0F, -1.0F, -1.0F, 48.0F, 2.0F, 2.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(-16.0F, 0.0F, 0.0F, 0.0F, 0.0F, -1.1345F));
        PartDefinition leg6 = ragno_body.addOrReplaceChild("leg6", CubeListBuilder.create().texOffs(0, 184).addBox(-12.0F, -3.0F, -3.0F, 12.0F, 6.0F, 6.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(-4.0F, 1.0F, -4.0F, 0.0F, 0.4363F, 0.2618F));
        PartDefinition knee6 = leg6.addOrReplaceChild("knee6", CubeListBuilder.create().texOffs(0, 167).addBox(-16.0F, -1.5F, -1.5F, 16.0F, 3.0F, 3.0F, new CubeDeformation(0.0F)), PartPose.offset(-12.0F, 0.0F, 0.0F));
        knee6.addOrReplaceChild("kneeee6", CubeListBuilder.create().texOffs(0, 173).addBox(-48.0F, -1.0F, -1.0F, 48.0F, 2.0F, 2.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(-16.0F, 0.0F, 0.0F, 0.0F, 0.0F, -1.1345F));
        PartDefinition leg7 = ragno_body.addOrReplaceChild("leg7", CubeListBuilder.create().texOffs(0, 184).addBox(-12.0F, -3.0F, -3.0F, 12.0F, 6.0F, 6.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(-4.0F, 3.0F, 5.0F, 0.0F, -0.4363F, 0.0873F));
        PartDefinition knee7 = leg7.addOrReplaceChild("knee7", CubeListBuilder.create().texOffs(0, 167).addBox(-16.0F, -1.5F, -1.5F, 16.0F, 3.0F, 3.0F, new CubeDeformation(0.0F)), PartPose.offset(-12.0F, 0.0F, 0.0F));
        knee7.addOrReplaceChild("kneeee7", CubeListBuilder.create().texOffs(0, 177).addBox(-40.0F, -1.0F, -1.0F, 40.0F, 2.0F, 2.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(-16.0F, 0.0F, 0.0F, 0.0F, 0.0F, -1.0472F));
        PartDefinition leg8 = ragno_body.addOrReplaceChild("leg8", CubeListBuilder.create().texOffs(0, 184).addBox(-12.0F, -3.0F, -3.0F, 12.0F, 6.0F, 6.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(-4.0F, 3.0F, 5.0F, 0.0F, 0.4363F, 0.0873F));
        PartDefinition knee8 = leg8.addOrReplaceChild("knee8", CubeListBuilder.create().texOffs(0, 167).addBox(-16.0F, -1.5F, -1.5F, 16.0F, 3.0F, 3.0F, new CubeDeformation(0.0F)), PartPose.offset(-12.0F, 0.0F, 0.0F));
        knee8.addOrReplaceChild("kneeee8", CubeListBuilder.create().texOffs(0, 177).addBox(-40.0F, -1.0F, -1.0F, 40.0F, 2.0F, 2.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(-16.0F, 0.0F, 0.0F, 0.0F, 0.0F, -1.0472F));
        return LayerDefinition.create(meshdefinition, 192, 196);
    }

    public void setupAnim(T entity, float limbSwing, float limbSwingAmount, float ageInTicks, float netHeadYaw, float headPitch) {
        this.ragno_body.getAllParts().forEach(ModelPart::resetPose);
        ModelPart head = this.ragno_body.getChild("neck").getChild("ragno_head");
        ModelPart neck = this.ragno_body.getChild("neck");
        ModelPart abdomen = this.ragno_body.getChild("abdomen");
        ModelPart leg1 = this.ragno_body.getChild("leg1");
        ModelPart leg2 = this.ragno_body.getChild("leg2");
        ModelPart leg3 = this.ragno_body.getChild("leg3");
        ModelPart leg4 = this.ragno_body.getChild("leg4");
        ModelPart leg5 = this.ragno_body.getChild("leg5");
        ModelPart leg6 = this.ragno_body.getChild("leg6");
        ModelPart leg7 = this.ragno_body.getChild("leg7");
        ModelPart leg8 = this.ragno_body.getChild("leg8");
        if (entity instanceof OldRagnoEntity ragno) {
            float craziness = ragno.isCrazy() ? 2.0F : 1.0F;
            head.yRot = netHeadYaw * 0.017453292F + (-0.5F + ragno.getRandom().nextFloat()) * 0.08F * craziness;
            head.xRot = -0.0873F + headPitch * 0.017453292F + (-0.5F + ragno.getRandom().nextFloat()) * 0.08F * craziness;
            head.zRot = (-0.5F + ragno.getRandom().nextFloat()) * 0.08F * craziness;
            neck.yRot = (-0.5F + ragno.getRandom().nextFloat()) * 0.04F * craziness;
            neck.xRot = (-0.5F + ragno.getRandom().nextFloat()) * 0.04F * craziness;
            abdomen.yRot = (-0.5F + ragno.getRandom().nextFloat()) * 0.16F * craziness;
            abdomen.xRot = -0.3491F + (-0.5F + ragno.getRandom().nextFloat()) * 0.08F * craziness;
            abdomen.zRot = (-0.5F + ragno.getRandom().nextFloat()) * 0.08F * craziness;
        }

        float $$9 = -(Mth.cos(limbSwing * 0.6662F * 2.0F + 0.0F) * 0.4F) * limbSwingAmount;
        float $$10 = -(Mth.cos(limbSwing * 0.6662F * 2.0F + 3.1415927F) * 0.4F) * limbSwingAmount;
        float $$11 = -(Mth.cos(limbSwing * 0.6662F * 2.0F + 1.5707964F) * 0.4F) * limbSwingAmount;
        float $$12 = -(Mth.cos(limbSwing * 0.6662F * 2.0F + 4.712389F) * 0.4F) * limbSwingAmount;
        float $$13 = Math.abs(Mth.sin(limbSwing * 0.6662F + 0.0F) * 0.4F) * limbSwingAmount;
        float $$14 = Math.abs(Mth.sin(limbSwing * 0.6662F + 3.1415927F) * 0.4F) * limbSwingAmount;
        float $$15 = Math.abs(Mth.sin(limbSwing * 0.6662F + 1.5707964F) * 0.4F) * limbSwingAmount;
        float $$16 = Math.abs(Mth.sin(limbSwing * 0.6662F + 4.712389F) * 0.4F) * limbSwingAmount;
        leg8.yRot += $$9;
        leg4.yRot -= $$9;
        leg7.yRot += $$10;
        leg3.yRot -= $$10;
        leg6.yRot += $$11;
        leg2.yRot -= $$11;
        leg5.yRot += $$12;
        leg1.yRot -= $$12;
        leg8.zRot += $$13;
        leg4.zRot -= $$13;
        leg7.zRot += $$14;
        leg3.zRot -= $$14;
        leg6.zRot += $$15;
        leg2.zRot -= $$15;
        leg5.zRot += $$16;
        leg1.zRot -= $$16;
        if (entity instanceof OldRagnoEntity ragno) {
            this.animate(ragno.getAnimationState("intro"), OldRagnoAnimation.INTRO, ageInTicks, ragno.getAnimationSpeed());
            this.animate(ragno.getAnimationState("phase"), OldRagnoAnimation.PHASE, ageInTicks, ragno.getAnimationSpeed());
            this.animate(ragno.getAnimationState("block"), OldRagnoAnimation.BLOCK, ageInTicks, ragno.getAnimationSpeed());
            this.animate(ragno.getAnimationState("web"), OldRagnoAnimation.WEB, ageInTicks, ragno.getAnimationSpeed());
            this.animate(ragno.getAnimationState("leap"), OldRagnoAnimation.LEAP, ageInTicks, ragno.getAnimationSpeed());
            this.animate(ragno.getAnimationState("burrow"), OldRagnoAnimation.BURROW, ageInTicks, ragno.getAnimationSpeed());
            this.animate(ragno.getAnimationState("popup"), OldRagnoAnimation.POPUP, ageInTicks, ragno.getAnimationSpeed());
            this.animate(ragno.getAnimationState("charge"), OldRagnoAnimation.CHARGE, ageInTicks, ragno.getAnimationSpeed());
            this.animate(ragno.getAnimationState("cough"), OldRagnoAnimation.COUGH, ageInTicks, ragno.getAnimationSpeed());
            this.animate(ragno.getAnimationState("stun"), OldRagnoAnimation.STUN, ageInTicks, ragno.getAnimationSpeed());
        }

    }

    public void renderToBuffer(PoseStack poseStack, VertexConsumer vertexConsumer, int packedLight, int packedOverlay, float red, float green, float blue, float alpha) {
        this.ragno_body.render(poseStack, vertexConsumer, packedLight, packedOverlay, red, green, blue, alpha);
    }

    public ModelPart root() {
        return this.root;
    }
}
