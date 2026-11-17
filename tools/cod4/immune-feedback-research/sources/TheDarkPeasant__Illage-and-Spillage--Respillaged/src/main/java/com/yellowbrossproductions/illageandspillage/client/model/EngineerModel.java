package com.yellowbrossproductions.illageandspillage.client.model;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.yellowbrossproductions.illageandspillage.client.model.animation.EngineerAnimation;
import com.yellowbrossproductions.illageandspillage.entities.EngineerEntity;
import net.minecraft.client.model.HierarchicalModel;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;

import java.util.Calendar;

public class EngineerModel<T extends Entity> extends HierarchicalModel<T> implements CustomHeadedModel {
    public static final ModelLayerLocation LAYER_LOCATION = new ModelLayerLocation(new ResourceLocation("illageandspillage", "engineer"), "main");
    private final ModelPart root;
    private final ModelPart all;
    private final ModelPart body;
    private final ModelPart left_arm;
    private final ModelPart right_arm;
    private final ModelPart left_leg;
    private final ModelPart right_leg;
    private final ModelPart head;

    public EngineerModel(ModelPart root) {
        this.root = root;
        this.all = this.root.getChild("all");
        this.body = this.all.getChild("body");
        this.left_arm = this.body.getChild("left_arm");
        this.right_arm = this.body.getChild("right_arm");
        this.left_leg = this.all.getChild("left_leg");
        this.right_leg = this.all.getChild("right_leg");
        this.head = this.body.getChild("head");
    }

    public static LayerDefinition createBodyLayer() {
        MeshDefinition meshdefinition = new MeshDefinition();
        PartDefinition partdefinition = meshdefinition.getRoot();

        PartDefinition all = partdefinition.addOrReplaceChild("all", CubeListBuilder.create(), PartPose.offset(0.0F, 24.0F, 0.0F));

        PartDefinition body = all.addOrReplaceChild("body", CubeListBuilder.create().texOffs(0, 18).addBox(-4.0F, -12.0F, -3.0F, 8.0F, 12.0F, 6.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, -12.0F, 0.0F));

        body.addOrReplaceChild("left_arm", CubeListBuilder.create().texOffs(16, 36).mirror().addBox(-2.0F, -2.0F, -2.0F, 4.0F, 12.0F, 4.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offset(6.0F, -10.0F, 0.0F));

        PartDefinition right_arm = body.addOrReplaceChild("right_arm", CubeListBuilder.create().texOffs(16, 36).addBox(-2.0F, -2.0F, -2.0F, 4.0F, 12.0F, 4.0F, new CubeDeformation(0.0F)), PartPose.offset(-6.0F, -10.0F, 0.0F));

        right_arm.addOrReplaceChild("hammer", CubeListBuilder.create().texOffs(0, 52).addBox(-1.0F, -10.0F, -1.0F, 2.0F, 14.0F, 2.0F, new CubeDeformation(0.0F))
                .texOffs(8, 52).addBox(-2.0F, -9.0F, -4.0F, 4.0F, 4.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 8.0F, 0.0F, 1.5708F, 0.0F, 0.0F));

        PartDefinition head = body.addOrReplaceChild("head", CubeListBuilder.create().texOffs(0, 0).addBox(-4.0F, -10.0F, -4.0F, 8.0F, 10.0F, 8.0F, new CubeDeformation(0.0F))
                .texOffs(0, 0).addBox(-1.0F, -3.0F, -6.0F, 2.0F, 4.0F, 2.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, -12.0F, 0.0F));

        PartDefinition hat = head.addOrReplaceChild("hat", CubeListBuilder.create().texOffs(32, 0).addBox(-4.0F, -10.0F, -4.0F, 8.0F, 10.0F, 8.0F, new CubeDeformation(0.25F))
                .texOffs(64, 0).addBox(-5.0F, -7.0F, -5.0F, 10.0F, 1.0F, 10.0F, new CubeDeformation(0.0F))
                .texOffs(28, 18).addBox(-1.0F, -11.0F, -5.0F, 2.0F, 4.0F, 10.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 0.0F, 0.0F));

        PartDefinition birthday = hat.addOrReplaceChild("birthday", CubeListBuilder.create().texOffs(45, 46).addBox(-2.0F, -9.3333F, 6.0833F, 4.0F, 3.0F, 4.0F, new CubeDeformation(0.0F))
                .texOffs(33, 46).addBox(-1.5F, -12.3333F, 6.5833F, 3.0F, 3.0F, 3.0F, new CubeDeformation(0.0F))
                .texOffs(58, 43).addBox(0.0F, -15.3333F, 6.5833F, 0.0F, 3.0F, 3.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, -3.6667F, -8.0833F, 0.0F, 0.0F, 0.0873F));

        birthday.addOrReplaceChild("thingy", CubeListBuilder.create().texOffs(58, 46).addBox(-1.5F, -15.3333F, 8.0F, 3.0F, 3.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 0.0F, 0.0F));

        all.addOrReplaceChild("left_leg", CubeListBuilder.create().texOffs(0, 36).mirror().addBox(-2.0F, 0.0F, -2.0F, 4.0F, 12.0F, 4.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offset(2.0F, -12.0F, 0.0F));

        all.addOrReplaceChild("right_leg", CubeListBuilder.create().texOffs(0, 36).addBox(-2.0F, 0.0F, -2.0F, 4.0F, 12.0F, 4.0F, new CubeDeformation(0.0F)), PartPose.offset(-2.0F, -12.0F, 0.0F));

        return LayerDefinition.create(meshdefinition, 128, 128);
    }

    @Override
    public void setupAnim(Entity entity, float limbSwing, float limbSwingAmount, float ageInTicks, float netHeadYaw, float headPitch) {
        this.root().getAllParts().forEach(ModelPart::resetPose);
        if (entity instanceof EngineerEntity engineer) {
            this.animate(engineer.getAnimationState("throw"), EngineerAnimation.THROW, ageInTicks, engineer.getAnimationSpeed());
            this.animate(engineer.getAnimationState("repair"), EngineerAnimation.REPAIR, ageInTicks, engineer.getAnimationSpeed());

            Calendar calendar = Calendar.getInstance();
            this.body.getChild("head").getChild("hat").getChild("birthday").visible = calendar.get(Calendar.MONTH) == Calendar.FEBRUARY && calendar.get(Calendar.DAY_OF_MONTH) < 8;

            this.head.yRot = netHeadYaw * ((float) Math.PI / 180F);
            this.head.xRot = headPitch * ((float) Math.PI / 180F);
            if (this.riding) {
                if (engineer.getAnimationState() == 0) {
                    this.right_arm.xRot = (-(float) Math.PI / 5F);
                    this.left_arm.xRot = (-(float) Math.PI / 5F);
                    this.right_arm.yRot = 0.0F;
                    this.right_arm.zRot = 0.0F;
                    this.left_arm.yRot = 0.0F;
                    this.left_arm.zRot = 0.0F;
                }
                this.right_leg.xRot = -1.4137167F;
                this.right_leg.yRot = ((float) Math.PI / 10F);
                this.right_leg.zRot = 0.07853982F;
                this.left_leg.xRot = -1.4137167F;
                this.left_leg.yRot = (-(float) Math.PI / 10F);
                this.left_leg.zRot = -0.07853982F;
            } else {
                if (engineer.getAnimationState() == 0) {
                    this.right_arm.xRot = Mth.cos(limbSwing * 0.6662F + (float) Math.PI) * 2.0F * limbSwingAmount * 0.5F;
                    this.left_arm.xRot = Mth.cos(limbSwing * 0.6662F) * 2.0F * limbSwingAmount * 0.5F;
                    this.right_arm.yRot = 0.0F;
                    this.right_arm.zRot = 0.0F;
                    this.left_arm.yRot = 0.0F;
                    this.left_arm.zRot = 0.0F;
                }
                this.right_leg.xRot = Mth.cos(limbSwing * 0.6662F) * 1.4F * limbSwingAmount * 0.5F;
                this.right_leg.yRot = 0.0F;
                this.right_leg.zRot = 0.0F;
                this.left_leg.xRot = Mth.cos(limbSwing * 0.6662F + (float) Math.PI) * 1.4F * limbSwingAmount * 0.5F;
                this.left_leg.yRot = 0.0F;
                this.left_leg.zRot = 0.0F;
            }
        }
    }

    @Override
    public void renderToBuffer(PoseStack poseStack, VertexConsumer vertexConsumer, int packedLight, int packedOverlay, float red, float green, float blue, float alpha) {
        all.render(poseStack, vertexConsumer, packedLight, packedOverlay, red, green, blue, alpha);
    }

    @Override
    public ModelPart root() {
        return this.root;
    }

    @Override
    public void translateToHead(PoseStack stack) {
        this.root().translateAndRotate(stack);
        this.all.translateAndRotate(stack);
        this.body.translateAndRotate(stack);
        this.head.translateAndRotate(stack);
    }
}