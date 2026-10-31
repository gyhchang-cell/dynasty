package com.yellowbrossproductions.illageandspillage.client.model;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.yellowbrossproductions.illageandspillage.entities.ImpEntity;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;

public class ImpModel<T extends Entity> extends EntityModel<T> {
    public static final ModelLayerLocation LAYER_LOCATION = new ModelLayerLocation(new ResourceLocation("illageandspillage", "imp"), "main");
    private final ModelPart body;
    private final ModelPart block;

    public ImpModel(ModelPart root) {
        this.body = root.getChild("body");
        this.block = root.getChild("block");
    }

    public static LayerDefinition createBodyLayer() {
        MeshDefinition meshdefinition = new MeshDefinition();
        PartDefinition partdefinition = meshdefinition.getRoot();
        PartDefinition body = partdefinition.addOrReplaceChild("body", CubeListBuilder.create().texOffs(16, 20).addBox(-4.0F, 0.0F, -3.0F, 8.0F, 12.0F, 6.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 0.0F, 0.0F));
        PartDefinition head = body.addOrReplaceChild("head", CubeListBuilder.create().texOffs(0, 0).addBox(-4.0F, -10.0F, -4.0F, 8.0F, 10.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 0.0F, 0.0F));
        head.addOrReplaceChild("nose", CubeListBuilder.create().texOffs(24, 0).addBox(-1.0F, -1.0F, -6.0F, 2.0F, 4.0F, 2.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, -2.0F, 0.0F));
        head.addOrReplaceChild("horns", CubeListBuilder.create().texOffs(28, 42).addBox(-10.0F, -6.0F, 0.0F, 18.0F, 6.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offset(1.0F, -7.0F, 0.0F));
        body.addOrReplaceChild("left_arm", CubeListBuilder.create().texOffs(0, 38).mirror().addBox(-1.0F, -2.0F, -2.0F, 4.0F, 12.0F, 4.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offsetAndRotation(5.0F, 2.0F, 0.0F, 0.0F, 0.0F, -0.6109F));
        PartDefinition right_arm = body.addOrReplaceChild("right_arm", CubeListBuilder.create().texOffs(0, 38).addBox(-3.0F, -2.0F, -2.0F, 4.0F, 12.0F, 4.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(-5.0F, 2.0F, 0.0F, -2.3562F, 0.0F, 0.0F));
        right_arm.addOrReplaceChild("pitchfork", CubeListBuilder.create().texOffs(42, 0).addBox(-0.5F, -15.0F, -0.5F, 1.0F, 24.0F, 1.0F, new CubeDeformation(0.0F)).texOffs(46, 0).addBox(-2.5F, -16.0F, -0.5F, 5.0F, 1.0F, 1.0F, new CubeDeformation(0.0F)).texOffs(46, 2).addBox(1.5F, -20.0F, -0.5F, 1.0F, 4.0F, 1.0F, new CubeDeformation(0.0F)).texOffs(50, 2).addBox(-0.5F, -21.0F, -0.5F, 1.0F, 5.0F, 1.0F, new CubeDeformation(0.0F)).texOffs(46, 2).addBox(-2.5F, -20.0F, -0.5F, 1.0F, 4.0F, 1.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(-1.0F, 8.0F, 0.0F, 1.5708F, 0.0F, 0.0F));
        body.addOrReplaceChild("left_leg", CubeListBuilder.create().texOffs(0, 22).mirror().addBox(-2.0F, 0.0F, -2.0F, 4.0F, 12.0F, 4.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offsetAndRotation(2.0F, 12.0F, 0.0F, 0.0F, 0.0F, -0.0873F));
        body.addOrReplaceChild("right_leg", CubeListBuilder.create().texOffs(0, 22).addBox(-2.0F, 0.0F, -2.0F, 4.0F, 12.0F, 4.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(-2.0F, 12.0F, 0.0F, 0.0F, 0.0F, 0.0873F));
        body.addOrReplaceChild("wing1", CubeListBuilder.create().texOffs(32, 48).mirror().addBox(0.0F, -16.0F, 0.0F, 16.0F, 16.0F, 0.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offset(4.0F, 6.0F, 3.0F));
        body.addOrReplaceChild("wing2", CubeListBuilder.create().texOffs(32, 48).addBox(-16.0F, -16.0F, 0.0F, 16.0F, 16.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offset(-4.0F, 6.0F, 3.0F));
        PartDefinition tail1 = body.addOrReplaceChild("tail1", CubeListBuilder.create().texOffs(32, 9).addBox(-0.5F, -8.0F, 0.0F, 1.0F, 8.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 9.0F, 3.0F, -1.1345F, 0.0F, 0.0F));
        PartDefinition tail2 = tail1.addOrReplaceChild("tail2", CubeListBuilder.create().texOffs(32, 9).addBox(-0.5F, -8.0F, 0.0F, 1.0F, 8.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, -8.0F, 0.0F, 0.5236F, 0.0F, -0.5236F));
        PartDefinition tail3 = tail2.addOrReplaceChild("tail3", CubeListBuilder.create().texOffs(32, 9).addBox(-0.5F, -8.0F, 0.0F, 1.0F, 8.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, -8.0F, 0.0F, 0.5236F, 0.0F, -0.4363F));
        tail3.addOrReplaceChild("tail4", CubeListBuilder.create().texOffs(34, 9).addBox(-2.0F, -6.0F, 0.0F, 4.0F, 6.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, -8.0F, 0.0F, 0.0F, 0.0F, -0.3491F));
        partdefinition.addOrReplaceChild("block", CubeListBuilder.create().texOffs(64, 0).addBox(-8.0F, -8.0F, -8.0F, 16.0F, 16.0F, 16.0F, new CubeDeformation(0.25F)), PartPose.offset(0.0F, 32.0F, 0.0F));
        return LayerDefinition.create(meshdefinition, 128, 64);
    }

    public void setupAnim(T entity, float limbSwing, float limbSwingAmount, float ageInTicks, float netHeadYaw, float headPitch) {
        float f3 = ageInTicks / 60.0F;
        this.body.getChild("head").yRot = netHeadYaw * 0.017453292F;
        this.body.getChild("head").xRot = headPitch * 0.017453292F;
        if (entity instanceof ImpEntity) {
            this.block.x = -0.5F + ((ImpEntity) entity).getRandom().nextFloat();
            this.block.z = -0.5F + ((ImpEntity) entity).getRandom().nextFloat();
        }
        if (entity instanceof ImpEntity imp) {
            if (imp.getStage() == 1) {
                this.body.visible = false;
                this.block.visible = true;
            } else {
                this.body.visible = true;
                this.block.visible = false;
            }

            if (imp.getStage() == 3) {
                this.body.getChild("left_arm").xRot = -2.0944F;
                this.body.getChild("left_arm").zRot = -1.7453F;
                this.body.getChild("head").y = Mth.sin(f3 * 40.0F) * 0.5F;
            } else {
                this.body.getChild("left_arm").xRot = 0.0F;
                this.body.getChild("left_arm").zRot = -0.6109F;
                this.body.getChild("head").y = 0.0F;
            }

            if (imp.getStage() == 2) {
                this.body.yRot = ageInTicks * 25.0F * 0.017453292F;
            } else {
                this.body.yRot = 0.0F;
            }

            if (imp.getStage() == 4) {
                this.body.xRot = 3.14159F;
            } else {
                this.body.xRot = 0.0F;
            }
        }

    }

    public void renderToBuffer(PoseStack poseStack, VertexConsumer vertexConsumer, int packedLight, int packedOverlay, float red, float green, float blue, float alpha) {
        this.body.render(poseStack, vertexConsumer, packedLight, packedOverlay, red, green, blue, alpha);
        this.block.render(poseStack, vertexConsumer, packedLight, packedOverlay, red, green, blue, alpha);
    }
}
