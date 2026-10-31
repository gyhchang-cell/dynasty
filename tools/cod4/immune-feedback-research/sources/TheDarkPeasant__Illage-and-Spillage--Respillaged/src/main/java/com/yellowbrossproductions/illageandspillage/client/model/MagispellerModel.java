package com.yellowbrossproductions.illageandspillage.client.model;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.yellowbrossproductions.illageandspillage.client.model.animation.MagispellerAnimation;
import com.yellowbrossproductions.illageandspillage.entities.MagispellerEntity;
import net.minecraft.client.model.AnimationUtils;
import net.minecraft.client.model.ArmedModel;
import net.minecraft.client.model.HierarchicalModel;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.HumanoidArm;

import java.util.Calendar;
import java.util.Random;

public class MagispellerModel<T extends Entity> extends HierarchicalModel<T> implements CustomHeadedModel, ArmedModel {
    public static final ModelLayerLocation LAYER_LOCATION = new ModelLayerLocation(new ResourceLocation("illageandspillage", "magispeller"), "main");
    private final ModelPart root;
    private final ModelPart body;
    private final ModelPart left_leg;
    private final ModelPart right_leg;
    private final Random random = new Random();

    public MagispellerModel(ModelPart root) {
        this.root = root;
        this.body = root.getChild("body");
        this.left_leg = root.getChild("left_leg");
        this.right_leg = root.getChild("right_leg");
    }

    public static LayerDefinition createBodyLayer() {
        MeshDefinition meshdefinition = new MeshDefinition();
        PartDefinition partdefinition = meshdefinition.getRoot();

        PartDefinition body = partdefinition.addOrReplaceChild("body", CubeListBuilder.create().texOffs(16, 20).addBox(-4.0F, 0.0F, -3.0F, 8.0F, 12.0F, 6.0F, new CubeDeformation(0.0F))
                .texOffs(0, 38).addBox(-4.0F, 0.0F, -3.0F, 8.0F, 18.0F, 6.0F, new CubeDeformation(0.5F)), PartPose.offset(0.0F, 0.0F, 0.0F));

        PartDefinition arms = body.addOrReplaceChild("arms", CubeListBuilder.create(), PartPose.offset(0.0F, 3.5F, 0.3F));

        PartDefinition arms_rotation = arms.addOrReplaceChild("arms_rotation", CubeListBuilder.create().texOffs(44, 22).addBox(-8.0F, 0.0F, -2.0F, 4.0F, 8.0F, 4.0F, new CubeDeformation(0.0F))
                .texOffs(40, 38).addBox(-4.0F, 4.0F, -2.0F, 8.0F, 4.0F, 4.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, -2.0F, 0.05F, -0.7505F, 0.0F, 0.0F));

        arms_rotation.addOrReplaceChild("arms_flipped", CubeListBuilder.create().texOffs(44, 22).mirror().addBox(4.0F, -24.0F, -2.0F, 4.0F, 8.0F, 4.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offset(0.0F, 24.0F, 0.0F));

        body.addOrReplaceChild("left_arm", CubeListBuilder.create().texOffs(40, 46).mirror().addBox(-1.0F, -2.0F, -2.0F, 4.0F, 12.0F, 4.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offset(5.0F, 2.0F, 0.0F));

        body.addOrReplaceChild("right_arm", CubeListBuilder.create().texOffs(40, 46).addBox(-3.0F, -2.0F, -2.0F, 4.0F, 12.0F, 4.0F, new CubeDeformation(0.0F)), PartPose.offset(-5.0F, 2.0F, 0.0F));

        PartDefinition head = body.addOrReplaceChild("head", CubeListBuilder.create().texOffs(0, 0).addBox(-4.0F, -10.0F, -4.0F, 8.0F, 10.0F, 8.0F, new CubeDeformation(0.0F))
                .texOffs(32, 0).addBox(-4.0F, -14.0F, -4.0F, 8.0F, 6.0F, 8.0F, new CubeDeformation(0.25F)), PartPose.offset(0.0F, 0.0F, 0.0F));

        head.addOrReplaceChild("nose", CubeListBuilder.create().texOffs(24, 0).addBox(-1.0F, 0.0F, -2.0F, 2.0F, 4.0F, 2.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, -3.0F, -4.0F));

        head.addOrReplaceChild("eyebrow1", CubeListBuilder.create().texOffs(0, 0).addBox(-2.0F, -2.0F, 0.0F, 2.0F, 2.0F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(0, 3).addBox(-3.0F, -1.0F, 0.0F, 1.0F, 1.0F, 1.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(4.0F, -4.0F, -5.0F, 0.0F, 0.0F, -0.1745F));

        head.addOrReplaceChild("eyebrow2", CubeListBuilder.create().texOffs(0, 0).mirror().addBox(0.0F, -2.0F, 0.0F, 2.0F, 2.0F, 1.0F, new CubeDeformation(0.0F)).mirror(false)
                .texOffs(0, 3).addBox(2.0F, -1.0F, 0.0F, 1.0F, 1.0F, 1.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(-4.0F, -4.0F, -5.0F, 0.0F, 0.0F, 0.1745F));

        PartDefinition santahat1 = head.addOrReplaceChild("santahat1", CubeListBuilder.create().texOffs(56, 56).addBox(-1.0F, -6.0F, -1.0F, 2.0F, 6.0F, 2.0F, new CubeDeformation(1.0F)), PartPose.offsetAndRotation(0.0F, -13.0F, 0.0F, -0.6981F, 0.6109F, 0.0F));

        PartDefinition santahat2 = santahat1.addOrReplaceChild("santahat2", CubeListBuilder.create().texOffs(56, 56).mirror().addBox(-1.0F, -6.0F, -1.0F, 2.0F, 6.0F, 2.0F, new CubeDeformation(0.5F)).mirror(false), PartPose.offsetAndRotation(0.0F, -6.0F, 0.0F, -1.0472F, 0.0F, 0.0F));

        PartDefinition santahat3 = santahat2.addOrReplaceChild("santahat3", CubeListBuilder.create().texOffs(56, 56).addBox(-1.0F, -6.0F, -1.0F, 2.0F, 6.0F, 2.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, -6.0F, 0.0F, -0.8727F, 0.0F, 0.0F));

        santahat3.addOrReplaceChild("santahat4", CubeListBuilder.create().texOffs(28, 58).addBox(-1.5F, -3.0F, -1.5F, 3.0F, 3.0F, 3.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, -6.0F, 0.0F));

        PartDefinition birthday = head.addOrReplaceChild("birthday", CubeListBuilder.create().texOffs(48, 14).addBox(-2.0F, -3.0F, -2.0F, 4.0F, 3.0F, 4.0F, new CubeDeformation(0.0F))
                .texOffs(36, 14).addBox(-1.5F, -6.0F, -1.5F, 3.0F, 3.0F, 3.0F, new CubeDeformation(0.0F))
                .texOffs(58, 21).addBox(-1.5F, -9.0F, 0.0F, 3.0F, 3.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, -14.0F, 0.0F));

        birthday.addOrReplaceChild("thingy", CubeListBuilder.create().texOffs(58, 21).addBox(-1.5F, -3.0F, 0.0F, 3.0F, 3.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, -6.0F, 0.0F, 0.0F, -1.5708F, 0.0F));

        partdefinition.addOrReplaceChild("left_leg", CubeListBuilder.create().texOffs(0, 22).mirror().addBox(2.0F, 0.0F, -2.0F, 4.0F, 12.0F, 4.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offset(-2.0F, 12.0F, 0.0F));

        partdefinition.addOrReplaceChild("right_leg", CubeListBuilder.create().texOffs(0, 22).addBox(-6.0F, 0.0F, -2.0F, 4.0F, 12.0F, 4.0F, new CubeDeformation(0.0F)), PartPose.offset(2.0F, 12.0F, 0.0F));

        return LayerDefinition.create(meshdefinition, 64, 64);
    }

    public void setupAnim(T entity, float limbSwing, float limbSwingAmount, float ageInTicks, float netHeadYaw, float headPitch) {
        this.root().getAllParts().forEach(ModelPart::resetPose);
        ModelPart left_arm = this.body.getChild("left_arm");
        ModelPart right_arm = this.body.getChild("right_arm");
        ModelPart arms = this.body.getChild("arms");
        ModelPart var10000;
        if (entity instanceof MagispellerEntity magispeller) {
            this.animate(magispeller.getAnimationState("fireball"), MagispellerAnimation.FIREBALL, ageInTicks, magispeller.getAnimationSpeed());
            this.animate(magispeller.getAnimationState("lifesteal"), MagispellerAnimation.LIFESTEAL, ageInTicks, magispeller.getAnimationSpeed());
            this.animate(magispeller.getAnimationState("fakers"), MagispellerAnimation.FAKERS, ageInTicks, magispeller.getAnimationSpeed());
            this.animate(magispeller.getAnimationState("vexes"), MagispellerAnimation.VEXES, ageInTicks, magispeller.getAnimationSpeed());
            this.animate(magispeller.getAnimationState("fangrun"), MagispellerAnimation.FANGRUN, ageInTicks, magispeller.getAnimationSpeed());
            this.animate(magispeller.getAnimationState("potions"), MagispellerAnimation.POTIONS, ageInTicks, magispeller.getAnimationSpeed());
            this.animate(magispeller.getAnimationState("crossbowspin"), MagispellerAnimation.CROSSBOWSPIN, ageInTicks, magispeller.getAnimationSpeed());
            this.animate(magispeller.getAnimationState("crashager"), MagispellerAnimation.CRASHAGER, ageInTicks, magispeller.getAnimationSpeed());
            this.animate(magispeller.getAnimationState("dispenser"), MagispellerAnimation.DISPENSER, ageInTicks, magispeller.getAnimationSpeed());
            this.animate(magispeller.getAnimationState("knockback"), MagispellerAnimation.KNOCKBACK, ageInTicks, magispeller.getAnimationSpeed());
            this.animate(magispeller.getAnimationState("kaboomer"), MagispellerAnimation.KABOOMER, ageInTicks, magispeller.getAnimationSpeed());
            this.animate(magispeller.getAnimationState("death"), MagispellerAnimation.DEATH, ageInTicks, magispeller.getAnimationSpeed());

            Calendar calendar = Calendar.getInstance();
            this.body.getChild("head").getChild("birthday").visible = calendar.get(Calendar.MONTH) == Calendar.FEBRUARY && calendar.get(Calendar.DAY_OF_MONTH) < 8 && magispeller.getGlowState() != 5;

            left_arm.visible = magispeller.shouldShowArms() || magispeller.isFaking();
            right_arm.visible = magispeller.shouldShowArms() || magispeller.isFaking();
            arms.visible = !magispeller.shouldShowArms() && !magispeller.isFaking();
            var10000 = this.body;
            var10000.x += (-0.5F + this.random.nextFloat()) / 20.0F * (float) magispeller.getShakeAmount();
            var10000.y += (-0.5F + this.random.nextFloat()) / 20.0F * (float) magispeller.getShakeAmount();
            var10000.z += (-0.5F + this.random.nextFloat()) / 20.0F * (float) magispeller.getShakeAmount();
            right_arm.xRot += (-0.5F + this.random.nextFloat()) / 2.0F * (float) magispeller.getShakeAmount() * 0.017453292F;
            right_arm.yRot += (-0.5F + this.random.nextFloat()) / 2.0F * (float) magispeller.getShakeAmount() * 0.017453292F;
            right_arm.zRot += (-0.5F + this.random.nextFloat()) / 2.0F * (float) magispeller.getShakeAmount() * 0.017453292F;
            left_arm.xRot += (-0.5F + this.random.nextFloat()) / 2.0F * (float) magispeller.getShakeAmount() * 0.017453292F;
            left_arm.yRot += (-0.5F + this.random.nextFloat()) / 2.0F * (float) magispeller.getShakeAmount() * 0.017453292F;
            left_arm.zRot += (-0.5F + this.random.nextFloat()) / 2.0F * (float) magispeller.getShakeAmount() * 0.017453292F;
            var10000 = this.body.getChild("head");
            var10000.xRot += (-0.5F + this.random.nextFloat()) / 2.0F * (float) magispeller.getShakeAmount() * 0.017453292F;
            var10000 = this.body.getChild("head");
            var10000.yRot += (-0.5F + this.random.nextFloat()) / 2.0F * (float) magispeller.getShakeAmount() * 0.017453292F;
            var10000 = this.body.getChild("head");
            var10000.zRot += (-0.5F + this.random.nextFloat()) / 2.0F * (float) magispeller.getShakeAmount() * 0.017453292F;
            if (magispeller.isFaking()) {
                AnimationUtils.swingWeaponDown(this.body.getChild("right_arm"), this.body.getChild("left_arm"), magispeller, this.attackTime, ageInTicks);
            }

            if (magispeller.getArrowState() == 1) {
                this.body.getChild("right_arm").zRot = 1.5708F;
                this.body.getChild("left_arm").zRot = -1.5708F;
            }

            if (magispeller.getArrowState() == 2) {
                AnimationUtils.animateCrossbowHold(this.body.getChild("left_arm"), this.body.getChild("right_arm"), this.body.getChild("head"), true);
            }

            if (magispeller.isWavingArms()) {
                this.body.getChild("right_arm").z = 0.0F;
                this.body.getChild("right_arm").x = -5.0F;
                this.body.getChild("left_arm").z = 0.0F;
                this.body.getChild("left_arm").x = 5.0F;
                this.body.getChild("right_arm").xRot = Mth.cos(ageInTicks * 0.6662F) * 0.25F;
                this.body.getChild("left_arm").xRot = Mth.cos(ageInTicks * 0.6662F) * 0.25F;
                this.body.getChild("right_arm").zRot = 2.3561945F;
                this.body.getChild("left_arm").zRot = -2.3561945F;
                this.body.getChild("right_arm").yRot = 0.0F;
                this.body.getChild("left_arm").yRot = 0.0F;
            }

            if (magispeller.isBalloon()) {
                this.body.getChild("right_arm").y = -9.0F;
                this.body.getChild("left_arm").y = -9.0F;
                this.body.getChild("right_arm").xRot = 3.1416F;
                this.body.getChild("left_arm").xRot = 3.1416F;
                this.body.getChild("right_arm").zRot = 0.4363F;
                this.body.getChild("left_arm").zRot = -0.4363F;
                this.right_leg.z = -4.0F;
                this.right_leg.y = 8.0F;
            }
        }

        var10000 = this.body.getChild("head");
        var10000.yRot += netHeadYaw * 0.017453292F;
        var10000 = this.body.getChild("head");
        var10000.xRot += headPitch * 0.017453292F;
        if (this.riding) {
            this.left_leg.xRot = -1.4137167F;
            this.left_leg.yRot = -0.31415927F;
            this.left_leg.zRot = -0.07853982F;
            this.right_leg.xRot = -1.4137167F;
            this.right_leg.yRot = 0.31415927F;
            this.right_leg.zRot = 0.07853982F;
        } else {
            var10000 = this.right_leg;
            var10000.xRot += Mth.cos(limbSwing * 0.6662F) * 1.4F * limbSwingAmount * 0.5F;
            var10000 = this.left_leg;
            var10000.xRot += Mth.cos(limbSwing * 0.6662F + 3.1415927F) * 1.4F * limbSwingAmount * 0.5F;
        }

    }

    public void renderToBuffer(PoseStack poseStack, VertexConsumer buffer, int packedLight, int packedOverlay, float red, float green, float blue, float alpha) {
        this.body.render(poseStack, buffer, packedLight, packedOverlay);
        this.left_leg.render(poseStack, buffer, packedLight, packedOverlay);
        this.right_leg.render(poseStack, buffer, packedLight, packedOverlay);
    }

    public ModelPart root() {
        return this.root;
    }

    public void translateToHand(HumanoidArm p_102108_, PoseStack p_102109_) {
        this.root().translateAndRotate(p_102109_);
        this.body.translateAndRotate(p_102109_);
        this.getArm(p_102108_).translateAndRotate(p_102109_);
    }

    private ModelPart getArm(HumanoidArm p_191216_1_) {
        return p_191216_1_ == HumanoidArm.LEFT ? this.body.getChild("left_arm") : this.body.getChild("right_arm");
    }

    @Override
    public void translateToHead(PoseStack stack) {
        this.root().translateAndRotate(stack);
        this.body.translateAndRotate(stack);
        this.body.getChild("head").translateAndRotate(stack);
    }
}
