package com.yellowbrossproductions.illageandspillage.client.model;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.yellowbrossproductions.illageandspillage.entities.TwittollagerEntity;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.HeadedModel;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;

import java.util.Calendar;

public class TwittollagerModel<T extends Entity> extends EntityModel<T> implements HeadedModel {
    public static final ModelLayerLocation LAYER_LOCATION = new ModelLayerLocation(new ResourceLocation("illageandspillage", "twittollager"), "main");
    private final ModelPart body;
    private final ModelPart right_leg;
    private final ModelPart left_leg;

    public TwittollagerModel(ModelPart root) {
        this.body = root.getChild("body");
        this.right_leg = root.getChild("right_leg");
        this.left_leg = root.getChild("left_leg");
    }

    public static LayerDefinition createBodyLayer() {
        MeshDefinition meshdefinition = new MeshDefinition();
        PartDefinition partdefinition = meshdefinition.getRoot();

        PartDefinition body = partdefinition.addOrReplaceChild("body", CubeListBuilder.create().texOffs(16, 20).addBox(-4.0F, -12.0F, -3.0F, 8.0F, 12.0F, 6.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 12.0F, 0.0F, 0.0873F, 0.0F, 0.0F));

        PartDefinition head = body.addOrReplaceChild("head", CubeListBuilder.create().texOffs(0, 0).addBox(-4.0F, -10.0F, -4.0F, 8.0F, 10.0F, 8.0F, new CubeDeformation(0.0F))
                .texOffs(24, 0).addBox(-1.0F, -3.0F, -6.0F, 2.0F, 4.0F, 2.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, -12.0F, 0.0F, -0.0873F, 0.0F, 0.0F));

        head.addOrReplaceChild("eyebrow1", CubeListBuilder.create().texOffs(0, 0).addBox(-0.5F, -2.0F, 0.0F, 3.0F, 2.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(-3.5F, -4.0F, -4.1F, 0.0F, 0.0F, 0.3927F));

        head.addOrReplaceChild("eyebrow2", CubeListBuilder.create().texOffs(0, 0).mirror().addBox(-2.5F, -2.0F, 0.0F, 3.0F, 2.0F, 0.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offsetAndRotation(3.5F, -4.0F, -4.1F, 0.0F, 0.0F, -0.4363F));

        PartDefinition birthday = head.addOrReplaceChild("birthday", CubeListBuilder.create().texOffs(74, 15).addBox(-2.0F, 2.0F, -1.0F, 4.0F, 3.0F, 4.0F, new CubeDeformation(0.0F))
                .texOffs(62, 15).addBox(-1.5F, -1.0F, -0.5F, 3.0F, 3.0F, 3.0F, new CubeDeformation(0.0F))
                .texOffs(90, 15).addBox(-1.5F, -4.0F, 1.0F, 3.0F, 3.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, -15.0F, 0.0F));

        birthday.addOrReplaceChild("thingy", CubeListBuilder.create().texOffs(90, 15).addBox(-0.5F, 2.0F, 0.0F, 3.0F, 3.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, -6.0F, 0.0F, 0.0F, -1.5708F, 0.0F));

        PartDefinition maskhead = body.addOrReplaceChild("maskhead", CubeListBuilder.create(), PartPose.offsetAndRotation(0.0F, -12.0F, 0.0F, -0.0873F, 0.0F, 0.0F));

        maskhead.addOrReplaceChild("mask", CubeListBuilder.create().texOffs(32, 0).addBox(-4.0F, -10.0F, -4.0F, 8.0F, 10.0F, 8.0F, new CubeDeformation(0.25F)), PartPose.offsetAndRotation(0.0F, -3.0F, -0.5F, -0.0873F, 0.0F, 0.0F));

        PartDefinition right_arm = body.addOrReplaceChild("right_arm", CubeListBuilder.create().texOffs(40, 46).mirror().addBox(-2.0F, -2.0F, -2.0F, 4.0F, 12.0F, 4.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offsetAndRotation(6.0F, -10.0F, 0.0F, -0.0873F, 0.0F, -0.0873F));

        right_arm.addOrReplaceChild("phone", CubeListBuilder.create().texOffs(76, 0).addBox(-2.0F, -0.5F, -6.0F, 4.0F, 1.0F, 6.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 8.5F, -1.0F, 0.1745F, 0.0F, -0.1745F));

        PartDefinition left_arm = body.addOrReplaceChild("left_arm", CubeListBuilder.create().texOffs(40, 46).addBox(-2.0F, -2.0F, -2.0F, 4.0F, 12.0F, 4.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(-6.0F, -10.0F, 0.0F, -0.0873F, 0.0F, 0.3491F));

        PartDefinition dispenser = left_arm.addOrReplaceChild("dispenser", CubeListBuilder.create().texOffs(64, 32).addBox(-8.0F, -8.0F, -8.0F, 16.0F, 16.0F, 16.0F, new CubeDeformation(-4.0F))
                .texOffs(0, 50).addBox(4.0F, -4.0F, -3.0F, 3.0F, 8.0F, 6.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(-3.0F, 10.0F, 0.0F, 0.8727F, 0.0F, 0.5236F));

        dispenser.addOrReplaceChild("torch_lit", CubeListBuilder.create().texOffs(120, 20).addBox(-1.0F, -9.0F, -1.0F, 2.0F, 10.0F, 2.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 2.0F, 0.0F, 1.8326F, 0.0F, 0.0F));

        body.addOrReplaceChild("burners", CubeListBuilder.create().texOffs(96, 0).addBox(-4.5F, 0.0F, -1.0F, 4.0F, 10.0F, 4.0F, new CubeDeformation(0.0F))
                .texOffs(112, 0).addBox(0.5F, 0.0F, -1.0F, 4.0F, 10.0F, 4.0F, new CubeDeformation(0.0F))
                .texOffs(120, 14).addBox(1.5F, -1.0F, 0.0F, 2.0F, 1.0F, 2.0F, new CubeDeformation(0.0F))
                .texOffs(120, 14).addBox(-1.0F, 5.5F, 0.0F, 2.0F, 1.0F, 2.0F, new CubeDeformation(0.0F))
                .texOffs(120, 14).addBox(-1.0F, 4.5F, 0.0F, 2.0F, 1.0F, 2.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, -12.0F, 4.0F, 0.1745F, 0.0F, -0.0873F));

        PartDefinition right_leg = partdefinition.addOrReplaceChild("right_leg", CubeListBuilder.create(), PartPose.offset(-2.0F, 12.0F, 0.0F));

        right_leg.addOrReplaceChild("right_leg_sub_0", CubeListBuilder.create().texOffs(0, 22).mirror().addBox(0.0F, -12.0F, -2.0F, 4.0F, 12.0F, 4.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offset(2.0F, 12.0F, 0.0F));

        partdefinition.addOrReplaceChild("left_leg", CubeListBuilder.create().texOffs(0, 22).addBox(-6.0F, 0.0F, -2.0F, 4.0F, 12.0F, 4.0F, new CubeDeformation(0.0F)), PartPose.offset(2.0F, 12.0F, 0.0F));

        return LayerDefinition.create(meshdefinition, 128, 64);
    }

    public void setupAnim(T entity, float limbSwing, float limbSwingAmount, float ageInTicks, float netHeadYaw, float headPitch) {
        Calendar calendar = Calendar.getInstance();
        this.body.getChild("head").getChild("birthday").visible = calendar.get(Calendar.MONTH) == Calendar.FEBRUARY && calendar.get(Calendar.DAY_OF_MONTH) < 8;

        this.body.getChild("head").yRot = netHeadYaw * 0.017453292F;
        this.body.getChild("head").xRot = -0.0873F + headPitch * 0.017453292F;
        this.body.getChild("maskhead").yRot = netHeadYaw * 0.017453292F;
        this.body.getChild("maskhead").xRot = -0.0873F + headPitch * 0.017453292F;
        if (this.riding) {
            this.right_leg.xRot = -1.4137167F;
            this.right_leg.yRot = -0.31415927F;
            this.right_leg.zRot = -0.07853982F;
            this.left_leg.xRot = -1.4137167F;
            this.left_leg.yRot = 0.31415927F;
            this.left_leg.zRot = 0.07853982F;
        } else {
            this.right_leg.xRot = Mth.cos(limbSwing * 0.6662F) * 1.4F * limbSwingAmount * 0.5F;
            this.left_leg.xRot = Mth.cos(limbSwing * 0.6662F + 3.1415927F) * 1.4F * limbSwingAmount * 0.5F;
            this.right_leg.zRot = 0.0F;
            this.left_leg.zRot = 0.0F;
            this.right_leg.yRot = 0.0F;
            this.left_leg.yRot = 0.0F;
        }

        if (entity instanceof TwittollagerEntity twittollager) {
            this.resetRotations();
            if (twittollager.isHmm()) {
                this.body.getChild("head").getChild("eyebrow1").zRot = 0.0F;
                this.body.getChild("head").getChild("eyebrow2").zRot = 0.0F;
            }

            if (twittollager.isCheckingPhone()) {
                this.body.getChild("head").getChild("eyebrow1").zRot = 0.0F;
                this.body.getChild("head").getChild("eyebrow2").zRot = 0.0F;
                this.body.getChild("head").getChild("eyebrow1").y = -3.5F;
                this.body.getChild("head").getChild("eyebrow2").y = -3.5F;
                this.body.getChild("right_arm").xRot = -1.0472F;
                this.body.getChild("right_arm").yRot = 0.6981F;
            }

            if (twittollager.getGRRRRRRRRRR() > 0) {
                this.body.getChild("head").getChild("eyebrow1").zRot = 0.010181666F * (float) twittollager.getGRRRRRRRRRR();
                this.body.getChild("head").getChild("eyebrow2").zRot = -0.010181666F * (float) twittollager.getGRRRRRRRRRR();
                this.body.getChild("head").getChild("eyebrow1").y = -3.5F - 0.025F * (float) twittollager.getGRRRRRRRRRR();
                this.body.getChild("head").getChild("eyebrow2").y = -3.5F - 0.025F * (float) twittollager.getGRRRRRRRRRR();
            }
        }

    }

    public void resetRotations() {
        this.body.getChild("head").getChild("eyebrow1").zRot = 0.3927F;
        this.body.getChild("head").getChild("eyebrow2").zRot = -0.4363F;
        this.body.getChild("head").getChild("eyebrow1").y = -4.0F;
        this.body.getChild("head").getChild("eyebrow2").y = -4.0F;
        this.body.getChild("right_arm").xRot = -0.0873F;
        this.body.getChild("right_arm").yRot = 0.0F;
    }

    public void renderToBuffer(PoseStack poseStack, VertexConsumer vertexConsumer, int packedLight, int packedOverlay, float red, float green, float blue, float alpha) {
        this.body.render(poseStack, vertexConsumer, packedLight, packedOverlay, red, green, blue, alpha);
        this.right_leg.render(poseStack, vertexConsumer, packedLight, packedOverlay, red, green, blue, alpha);
        this.left_leg.render(poseStack, vertexConsumer, packedLight, packedOverlay, red, green, blue, alpha);
    }

    public ModelPart getHead() {
        return this.body.getChild("head");
    }
}
