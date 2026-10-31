package com.yellowbrossproductions.illageandspillage.client.model;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.yellowbrossproductions.illageandspillage.entities.FakeMagispellerEntity;
import net.minecraft.client.model.AnimationUtils;
import net.minecraft.client.model.ArmedModel;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.HeadedModel;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.HumanoidArm;

public class FakerModel<T extends Entity> extends EntityModel<T> implements ArmedModel, HeadedModel {
    public static final ModelLayerLocation LAYER_LOCATION = new ModelLayerLocation(new ResourceLocation("illageandspillage", "faker"), "main");
    private final ModelPart body;
    private final ModelPart left_leg;
    private final ModelPart right_leg;

    public FakerModel(ModelPart root) {
        this.body = root.getChild("body");
        this.left_leg = root.getChild("left_leg");
        this.right_leg = root.getChild("right_leg");
    }

    public static LayerDefinition createBodyLayer() {
        MeshDefinition meshdefinition = new MeshDefinition();
        PartDefinition partdefinition = meshdefinition.getRoot();
        PartDefinition body = partdefinition.addOrReplaceChild("body", CubeListBuilder.create().texOffs(16, 20).addBox(-4.0F, 0.0F, -3.0F, 8.0F, 12.0F, 6.0F, new CubeDeformation(0.0F)).texOffs(0, 38).addBox(-4.0F, 0.0F, -3.0F, 8.0F, 18.0F, 6.0F, new CubeDeformation(0.5F)), PartPose.offset(0.0F, 0.0F, 0.0F));
        PartDefinition arms = body.addOrReplaceChild("arms", CubeListBuilder.create(), PartPose.offset(0.0F, 3.5F, 0.3F));
        PartDefinition arms_rotation = arms.addOrReplaceChild("arms_rotation", CubeListBuilder.create().texOffs(44, 22).addBox(-8.0F, 0.0F, -2.0F, 4.0F, 8.0F, 4.0F, new CubeDeformation(0.0F)).texOffs(40, 38).addBox(-4.0F, 4.0F, -2.0F, 8.0F, 4.0F, 4.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, -2.0F, 0.05F, -0.7505F, 0.0F, 0.0F));
        arms_rotation.addOrReplaceChild("arms_flipped", CubeListBuilder.create().texOffs(44, 22).mirror().addBox(4.0F, -24.0F, -2.0F, 4.0F, 8.0F, 4.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offset(0.0F, 24.0F, 0.0F));
        body.addOrReplaceChild("left_arm", CubeListBuilder.create().texOffs(40, 46).mirror().addBox(-1.0F, -2.0F, -2.0F, 4.0F, 12.0F, 4.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offset(5.0F, 2.0F, 0.0F));
        body.addOrReplaceChild("right_arm", CubeListBuilder.create().texOffs(40, 46).addBox(-3.0F, -2.0F, -2.0F, 4.0F, 12.0F, 4.0F, new CubeDeformation(0.0F)), PartPose.offset(-5.0F, 2.0F, 0.0F));
        PartDefinition head = body.addOrReplaceChild("head", CubeListBuilder.create().texOffs(0, 0).addBox(-4.0F, -10.0F, -4.0F, 8.0F, 10.0F, 8.0F, new CubeDeformation(0.0F)).texOffs(32, 0).addBox(-4.0F, -14.0F, -4.0F, 8.0F, 6.0F, 8.0F, new CubeDeformation(0.25F)), PartPose.offset(0.0F, 0.0F, 0.0F));
        head.addOrReplaceChild("nose", CubeListBuilder.create().texOffs(24, 0).addBox(-1.0F, 0.0F, -2.0F, 2.0F, 4.0F, 2.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, -3.0F, -4.0F));
        head.addOrReplaceChild("eyebrow1", CubeListBuilder.create().texOffs(0, 0).addBox(-2.0F, -2.0F, 0.0F, 2.0F, 2.0F, 1.0F, new CubeDeformation(0.0F)).texOffs(0, 3).addBox(-3.0F, -1.0F, 0.0F, 1.0F, 1.0F, 1.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(4.0F, -4.0F, -5.0F, 0.0F, 0.0F, -0.1745F));
        head.addOrReplaceChild("eyebrow2", CubeListBuilder.create().texOffs(0, 0).mirror().addBox(0.0F, -2.0F, 0.0F, 2.0F, 2.0F, 1.0F, new CubeDeformation(0.0F)).mirror(false).texOffs(0, 3).addBox(2.0F, -1.0F, 0.0F, 1.0F, 1.0F, 1.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(-4.0F, -4.0F, -5.0F, 0.0F, 0.0F, 0.1745F));
        PartDefinition santahat1 = head.addOrReplaceChild("santahat1", CubeListBuilder.create().texOffs(56, 56).addBox(-1.0F, -6.0F, -1.0F, 2.0F, 6.0F, 2.0F, new CubeDeformation(1.0F)), PartPose.offsetAndRotation(0.0F, -13.0F, 0.0F, -0.6981F, 0.6109F, 0.0F));
        PartDefinition santahat2 = santahat1.addOrReplaceChild("santahat2", CubeListBuilder.create().texOffs(56, 56).mirror().addBox(-1.0F, -6.0F, -1.0F, 2.0F, 6.0F, 2.0F, new CubeDeformation(0.5F)).mirror(false), PartPose.offsetAndRotation(0.0F, -6.0F, 0.0F, -1.0472F, 0.0F, 0.0F));
        PartDefinition santahat3 = santahat2.addOrReplaceChild("santahat3", CubeListBuilder.create().texOffs(56, 56).addBox(-1.0F, -6.0F, -1.0F, 2.0F, 6.0F, 2.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, -6.0F, 0.0F, -0.8727F, 0.0F, 0.0F));
        santahat3.addOrReplaceChild("santahat4", CubeListBuilder.create().texOffs(28, 58).addBox(-1.5F, -3.0F, -1.5F, 3.0F, 3.0F, 3.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, -6.0F, 0.0F));
        partdefinition.addOrReplaceChild("left_leg", CubeListBuilder.create().texOffs(0, 22).mirror().addBox(2.0F, 0.0F, -2.0F, 4.0F, 12.0F, 4.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offset(-2.0F, 12.0F, 0.0F));
        partdefinition.addOrReplaceChild("right_leg", CubeListBuilder.create().texOffs(0, 22).addBox(-6.0F, 0.0F, -2.0F, 4.0F, 12.0F, 4.0F, new CubeDeformation(0.0F)), PartPose.offset(2.0F, 12.0F, 0.0F));
        return LayerDefinition.create(meshdefinition, 64, 64);
    }

    public void setupAnim(T entity, float limbSwing, float limbSwingAmount, float ageInTicks, float netHeadYaw, float headPitch) {
        this.body.getChild("head").yRot = netHeadYaw * 0.017453292F;
        this.body.getChild("head").xRot = headPitch * 0.017453292F;
        if (this.riding) {
            this.left_leg.xRot = -1.4137167F;
            this.left_leg.yRot = -0.31415927F;
            this.left_leg.zRot = -0.07853982F;
            this.right_leg.xRot = -1.4137167F;
            this.right_leg.yRot = 0.31415927F;
            this.right_leg.zRot = 0.07853982F;
        } else {
            this.right_leg.xRot = Mth.cos(limbSwing * 0.6662F) * 1.4F * limbSwingAmount * 0.5F;
            this.left_leg.xRot = Mth.cos(limbSwing * 0.6662F + 3.1415927F) * 1.4F * limbSwingAmount * 0.5F;
            this.right_leg.zRot = 0.0F;
            this.left_leg.zRot = 0.0F;
            this.right_leg.yRot = 0.0F;
            this.left_leg.yRot = 0.0F;
        }

//        if (entity instanceof OldMagispellerEntity magispeller) {
//            boolean flag = magispeller.isWavingArms() || magispeller.isSpinning() || magispeller.isVindicatorAttacking() || magispeller.isCrossbowAttacking() || magispeller.isGoingWEEEEEEEEEEE();
//            this.body.getChild("arms").visible = !flag;
//            this.body.getChild("left_arm").visible = flag;
//            this.body.getChild("right_arm").visible = flag;
//            if (magispeller.isVindicatorAttacking()) {
//                AnimationUtils.swingWeaponDown(this.body.getChild("right_arm"), this.body.getChild("left_arm"), magispeller, this.attackTime, ageInTicks);
//            } else if (magispeller.isCrossbowAttacking()) {
//                AnimationUtils.animateCrossbowHold(this.body.getChild("left_arm"), this.body.getChild("right_arm"), this.body.getChild("head"), true);
//            } else if (magispeller.isWavingArms()) {
//                this.body.getChild("right_arm").z = 0.0F;
//                this.body.getChild("right_arm").x = -5.0F;
//                this.body.getChild("left_arm").z = 0.0F;
//                this.body.getChild("left_arm").x = 5.0F;
//                this.body.getChild("right_arm").xRot = Mth.cos(ageInTicks * 0.6662F) * 0.25F;
//                this.body.getChild("left_arm").xRot = Mth.cos(ageInTicks * 0.6662F) * 0.25F;
//                this.body.getChild("right_arm").zRot = 2.3561945F;
//                this.body.getChild("left_arm").zRot = -2.3561945F;
//                this.body.getChild("right_arm").yRot = 0.0F;
//                this.body.getChild("left_arm").yRot = 0.0F;
//            } else if (magispeller.isSpinning()) {
//                this.body.getChild("right_arm").z = 0.0F;
//                this.body.getChild("right_arm").x = -5.0F;
//                this.body.getChild("left_arm").z = 0.0F;
//                this.body.getChild("left_arm").x = 5.0F;
//                this.body.getChild("right_arm").xRot = 0.0F;
//                this.body.getChild("left_arm").xRot = 0.0F;
//                this.body.getChild("right_arm").zRot = 1.5708F;
//                this.body.getChild("left_arm").zRot = -1.5708F;
//                this.body.getChild("right_arm").yRot = 0.0F;
//                this.body.getChild("left_arm").yRot = 0.0F;
//            } else if (magispeller.isGoingWEEEEEEEEEEE()) {
//                this.body.getChild("right_arm").z = 0.0F;
//                this.body.getChild("right_arm").x = -5.0F;
//                this.body.getChild("left_arm").z = 0.0F;
//                this.body.getChild("left_arm").x = 5.0F;
//                this.body.getChild("right_arm").xRot = 0.0F;
//                this.body.getChild("left_arm").xRot = 0.0F;
//                this.body.getChild("right_arm").zRot = 2.5307F;
//                this.body.getChild("left_arm").zRot = -2.5307F;
//                this.body.getChild("right_arm").yRot = 0.0F;
//                this.body.getChild("left_arm").yRot = 0.0F;
//            }
//        }
        if (entity instanceof FakeMagispellerEntity magispeller) {
            AnimationUtils.swingWeaponDown(this.body.getChild("right_arm"), this.body.getChild("left_arm"), magispeller, this.attackTime, ageInTicks);
            this.body.getChild("arms").visible = false;
            this.body.getChild("left_arm").visible = true;
            this.body.getChild("right_arm").visible = true;
        }

    }

    public void renderToBuffer(PoseStack poseStack, VertexConsumer buffer, int packedLight, int packedOverlay, float red, float green, float blue, float alpha) {
        this.body.render(poseStack, buffer, packedLight, packedOverlay);
        this.left_leg.render(poseStack, buffer, packedLight, packedOverlay);
        this.right_leg.render(poseStack, buffer, packedLight, packedOverlay);
    }

    public void translateToHand(HumanoidArm p_102108_, PoseStack p_102109_) {
        this.getArm(p_102108_).translateAndRotate(p_102109_);
    }

    public ModelPart getHead() {
        return this.body.getChild("head");
    }

    private ModelPart getArm(HumanoidArm p_191216_1_) {
        return p_191216_1_ == HumanoidArm.LEFT ? this.body.getChild("left_arm") : this.body.getChild("right_arm");
    }
}
