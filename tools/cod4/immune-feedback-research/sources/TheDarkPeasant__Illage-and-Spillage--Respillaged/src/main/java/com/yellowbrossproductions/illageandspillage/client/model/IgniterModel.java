package com.yellowbrossproductions.illageandspillage.client.model;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.yellowbrossproductions.illageandspillage.entities.IgniterEntity;
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

public class IgniterModel<T extends Entity> extends EntityModel<T> implements HeadedModel {
    public static final ModelLayerLocation LAYER_LOCATION = new ModelLayerLocation(new ResourceLocation("illageandspillage", "igniter"), "main");
    private final ModelPart head;
    private final ModelPart body;
    private final ModelPart right_leg;
    private final ModelPart left_leg;
    private final ModelPart right_arm;
    private final ModelPart left_arm;
    private final ModelPart dispenser;

    public IgniterModel(ModelPart root) {
        this.head = root.getChild("head");
        this.body = root.getChild("body");
        this.right_leg = root.getChild("right_leg");
        this.left_leg = root.getChild("left_leg");
        this.right_arm = root.getChild("right_arm");
        this.left_arm = root.getChild("left_arm");
        this.dispenser = root.getChild("dispenser");
    }

    public static LayerDefinition createBodyLayer() {
        MeshDefinition meshdefinition = new MeshDefinition();
        PartDefinition partdefinition = meshdefinition.getRoot();

        PartDefinition head = partdefinition.addOrReplaceChild("head", CubeListBuilder.create().texOffs(0, 0).addBox(-4.0F, -10.0F, -4.0F, 8.0F, 10.0F, 8.0F, new CubeDeformation(0.0F))
                .texOffs(24, 0).addBox(-1.0F, -3.0F, -6.0F, 2.0F, 4.0F, 2.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 0.0F, 0.0F));

        head.addOrReplaceChild("mask_on", CubeListBuilder.create().texOffs(32, 0).addBox(-4.0F, -10.0F, -4.0F, 8.0F, 10.0F, 8.0F, new CubeDeformation(0.25F)), PartPose.offset(0.0F, 0.0F, 0.0F));

        head.addOrReplaceChild("mask_off", CubeListBuilder.create().texOffs(32, 0).addBox(-4.0F, -10.0F, -4.0F, 8.0F, 10.0F, 8.0F, new CubeDeformation(0.25F)), PartPose.offsetAndRotation(0.0F, -5.5F, -2.25F, -0.6109F, 0.0F, 0.0F));

        PartDefinition birthday = head.addOrReplaceChild("birthday", CubeListBuilder.create().texOffs(76, 0).addBox(-2.0F, -3.0F, -2.0F, 4.0F, 3.0F, 4.0F, new CubeDeformation(0.0F))
                .texOffs(64, 0).addBox(-1.5F, -6.0F, -1.5F, 3.0F, 3.0F, 3.0F, new CubeDeformation(0.0F))
                .texOffs(92, 0).addBox(-1.5F, -9.0F, 0.0F, 3.0F, 3.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, -9.0F, 1.0F, -0.3491F, 0.0F, 0.0F));

        birthday.addOrReplaceChild("thingy", CubeListBuilder.create().texOffs(92, 0).addBox(-1.5F, -3.0F, 0.0F, 3.0F, 3.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, -6.0F, 0.0F, 0.0F, -1.5708F, 0.0F));

        partdefinition.addOrReplaceChild("body", CubeListBuilder.create().texOffs(16, 20).addBox(-4.0F, 0.0F, -3.0F, 8.0F, 12.0F, 6.0F, new CubeDeformation(0.0F))
                .texOffs(112, 0).addBox(0.5F, 0.0F, 3.0F, 4.0F, 10.0F, 4.0F, new CubeDeformation(0.0F))
                .texOffs(120, 14).addBox(1.5F, -1.0F, 4.0F, 2.0F, 1.0F, 2.0F, new CubeDeformation(0.0F))
                .texOffs(120, 14).addBox(-3.5F, -1.0F, 4.0F, 2.0F, 1.0F, 2.0F, new CubeDeformation(0.0F))
                .texOffs(120, 14).addBox(-1.0F, 5.5F, 4.0F, 2.0F, 1.0F, 2.0F, new CubeDeformation(0.0F))
                .texOffs(120, 14).addBox(-1.0F, 4.5F, 4.0F, 2.0F, 1.0F, 2.0F, new CubeDeformation(0.0F))
                .texOffs(112, 0).addBox(-4.5F, 0.0F, 3.0F, 4.0F, 10.0F, 4.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 0.0F, 0.0F));

        PartDefinition right_leg = partdefinition.addOrReplaceChild("right_leg", CubeListBuilder.create(), PartPose.offset(-2.0F, 12.0F, 0.0F));

        right_leg.addOrReplaceChild("right_leg_sub_0", CubeListBuilder.create().texOffs(0, 22).mirror().addBox(0.0F, -12.0F, -2.0F, 4.0F, 12.0F, 4.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offset(2.0F, 12.0F, 0.0F));

        partdefinition.addOrReplaceChild("left_leg", CubeListBuilder.create().texOffs(0, 22).addBox(-6.0F, 0.0F, -2.0F, 4.0F, 12.0F, 4.0F, new CubeDeformation(0.0F)), PartPose.offset(2.0F, 12.0F, 0.0F));

        PartDefinition right_arm = partdefinition.addOrReplaceChild("right_arm", CubeListBuilder.create(), PartPose.offsetAndRotation(6.0F, 2.0F, 0.0F, -2.1817F, -0.5236F, 0.0F));

        right_arm.addOrReplaceChild("right_arm_sub_0", CubeListBuilder.create().texOffs(40, 46).mirror().addBox(4.0F, -24.0F, -2.0F, 4.0F, 12.0F, 4.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offset(-6.0F, 22.0F, 0.0F));

        partdefinition.addOrReplaceChild("left_arm", CubeListBuilder.create().texOffs(40, 46).addBox(-2.0F, -2.0F, -2.0F, 4.0F, 12.0F, 4.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(-6.0F, 2.0F, 0.0F, -0.9599F, -0.2618F, 0.0F));

        PartDefinition dispenser = partdefinition.addOrReplaceChild("dispenser", CubeListBuilder.create().texOffs(64, 32).addBox(-8.0F, -8.0F, -8.0F, 16.0F, 16.0F, 16.0F, new CubeDeformation(-4.0F))
                .texOffs(0, 50).addBox(4.0F, -4.0F, -3.0F, 3.0F, 8.0F, 6.0F, new CubeDeformation(0.0F)), PartPose.offset(-1.0F, 5.0F, -7.0F));

        dispenser.addOrReplaceChild("lever_handle", CubeListBuilder.create().texOffs(120, 36).addBox(-1.0F, -9.0F, -1.0F, 2.0F, 10.0F, 2.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(6.0F, -1.0F, 0.0F, 0.0F, 0.0F, 0.7854F));

        dispenser.addOrReplaceChild("torch_lit", CubeListBuilder.create().texOffs(120, 20).addBox(-1.0F, -9.0F, -1.0F, 2.0F, 10.0F, 2.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 2.0F, 0.0F, 1.8326F, 0.0F, 0.0F));

        dispenser.addOrReplaceChild("torch_burnt", CubeListBuilder.create().texOffs(112, 20).addBox(-1.0F, -9.0F, -1.0F, 2.0F, 10.0F, 2.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 2.0F, 0.0F, 1.8326F, 0.0F, 0.0F));

        return LayerDefinition.create(meshdefinition, 128, 64);
    }

    public void setupAnim(T entity, float limbSwing, float limbSwingAmount, float ageInTicks, float netHeadYaw, float headPitch) {
        Calendar calendar = Calendar.getInstance();
        this.head.getChild("birthday").visible = calendar.get(Calendar.MONTH) == Calendar.FEBRUARY && calendar.get(Calendar.DAY_OF_MONTH) < 8;

        this.head.yRot = netHeadYaw * 0.017453292F;
        this.head.xRot = headPitch * 0.017453292F;
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

        if (entity instanceof IgniterEntity igniter) {
            this.head.getChild("mask_on").visible = igniter.isAttacking();
            this.head.getChild("mask_off").visible = !igniter.isAttacking();
            this.dispenser.getChild("torch_lit").visible = !igniter.isTorchBurntOut();
            this.dispenser.getChild("torch_burnt").visible = igniter.isTorchBurntOut();
            if (igniter.isAttacking()) {
                this.right_arm.xRot = -0.6981F;
                this.dispenser.getChild("lever_handle").zRot = 2.3562F;
                this.head.getChild("birthday").xRot = 0;
            } else {
                this.right_arm.xRot = -2.1817F;
                this.dispenser.getChild("lever_handle").zRot = 0.7854F;
                this.head.getChild("birthday").xRot = (float) Math.toRadians(-20);
            }
        }

    }

    public void renderToBuffer(PoseStack poseStack, VertexConsumer buffer, int packedLight, int packedOverlay, float red, float green, float blue, float alpha) {
        this.head.render(poseStack, buffer, packedLight, packedOverlay);
        this.body.render(poseStack, buffer, packedLight, packedOverlay);
        this.right_leg.render(poseStack, buffer, packedLight, packedOverlay);
        this.left_leg.render(poseStack, buffer, packedLight, packedOverlay);
        this.right_arm.render(poseStack, buffer, packedLight, packedOverlay);
        this.left_arm.render(poseStack, buffer, packedLight, packedOverlay);
        this.dispenser.render(poseStack, buffer, packedLight, packedOverlay);
    }

    public ModelPart getHead() {
        return this.head;
    }
}
