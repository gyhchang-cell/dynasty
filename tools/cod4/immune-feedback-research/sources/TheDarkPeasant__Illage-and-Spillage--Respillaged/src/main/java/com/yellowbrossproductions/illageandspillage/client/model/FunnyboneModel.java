package com.yellowbrossproductions.illageandspillage.client.model;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.yellowbrossproductions.illageandspillage.client.model.animation.FunnyboneAnimation;
import com.yellowbrossproductions.illageandspillage.entities.FunnyboneEntity;
import net.minecraft.client.model.HierarchicalModel;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;

import java.util.Calendar;

public class FunnyboneModel<T extends Entity> extends HierarchicalModel<T> {
    public static final ModelLayerLocation LAYER_LOCATION = new ModelLayerLocation(new ResourceLocation("illageandspillage", "funnybone"), "main");
    private final ModelPart root;
    private final ModelPart all;
    private final ModelPart leg1;
    private final ModelPart leg2;
    private final ModelPart leg3;
    private final ModelPart leg4;
    private final ModelPart spine;
    private final ModelPart ribs;
    private final ModelPart head;
    private final ModelPart arm3;
    private final ModelPart arm4;
    private final ModelPart finger3;
    private final ModelPart finger4;
    private final ModelPart arm1;
    private final ModelPart arm2;
    private final ModelPart finger1;
    private final ModelPart finger2;
    private final ModelPart bone_weapon;

    public FunnyboneModel(ModelPart root) {
        this.root = root;
        this.all = this.root.getChild("all");
        this.leg1 = all.getChild("leg1");
        this.leg2 = leg1.getChild("leg2");
        this.leg3 = all.getChild("leg3");
        this.leg4 = leg3.getChild("leg4");
        this.spine = all.getChild("spine");
        this.ribs = spine.getChild("ribs");
        this.head = ribs.getChild("head");
        this.arm3 = ribs.getChild("arm3");
        this.arm4 = arm3.getChild("arm4");
        this.finger3 = arm4.getChild("finger3");
        this.finger4 = arm4.getChild("finger4");
        this.arm1 = ribs.getChild("arm1");
        this.arm2 = arm1.getChild("arm2");
        this.finger1 = arm2.getChild("finger1");
        this.finger2 = arm2.getChild("finger2");
        this.bone_weapon = arm2.getChild("bone_weapon");
    }

    public static LayerDefinition createBodyLayer() {
        MeshDefinition meshdefinition = new MeshDefinition();
        PartDefinition partdefinition = meshdefinition.getRoot();

        PartDefinition all = partdefinition.addOrReplaceChild("all", CubeListBuilder.create(), PartPose.offset(0.0F, 27.0F, 3.0F));

        PartDefinition leg1 = all.addOrReplaceChild("leg1", CubeListBuilder.create().texOffs(24, 0).addBox(-1.0F, 0.0F, -1.0F, 2.0F, 6.0F, 2.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(1.8F, -12.0F, 0.0F, -1.0335F, -0.3391F, 0.0066F));

        leg1.addOrReplaceChild("leg2", CubeListBuilder.create().texOffs(0, 33).addBox(-1.0F, 0.0F, -1.0F, 2.0F, 6.0F, 2.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 6.0F, 0.0F, 1.2654F, 0.0F, 0.0F));

        PartDefinition leg3 = all.addOrReplaceChild("leg3", CubeListBuilder.create().texOffs(24, 0).mirror().addBox(-1.0F, 0.0F, -1.0F, 2.0F, 6.0F, 2.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offsetAndRotation(-1.8F, -12.0F, 0.0F, -0.4516F, 0.3783F, 0.1318F));

        leg3.addOrReplaceChild("leg4", CubeListBuilder.create().texOffs(0, 33).mirror().addBox(-1.0F, 0.0F, -1.0F, 2.0F, 6.0F, 2.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offsetAndRotation(0.0F, 6.0F, 0.0F, 1.5272F, 0.0F, 0.0F));

        PartDefinition spine = all.addOrReplaceChild("spine", CubeListBuilder.create().texOffs(20, 14).addBox(-3.0F, -5.0F, -1.5F, 6.0F, 5.0F, 3.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, -12.0F, 0.0F, 0.2182F, 0.0F, 0.0F));

        PartDefinition ribs = spine.addOrReplaceChild("ribs", CubeListBuilder.create().texOffs(0, 24).addBox(-3.0F, -5.0F, -4.0F, 6.0F, 5.0F, 4.0F, new CubeDeformation(0.0F))
                .texOffs(0, 25).addBox(-1.0F, -7.0F, 0.0F, 2.0F, 2.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, -5.0F, 1.5F, 0.6545F, 0.0F, 0.0F));

        PartDefinition head2 = ribs.addOrReplaceChild("head", CubeListBuilder.create().texOffs(0, 0).addBox(-4.0F, -8.0F, -5.0F, 8.0F, 6.0F, 8.0F, new CubeDeformation(0.0F))
                .texOffs(0, 14).addBox(-3.0F, -2.0F, -5.0F, 6.0F, 2.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, -7.0F, -0.5F, -0.8727F, 0.0F, 0.0F));

        PartDefinition birthday = head2.addOrReplaceChild("birthday", CubeListBuilder.create().texOffs(40, 45).addBox(-2.0F, -9.3333F, 6.0833F, 4.0F, 3.0F, 4.0F, new CubeDeformation(0.0F))
                .texOffs(28, 45).addBox(-1.5F, -12.3333F, 6.5833F, 3.0F, 3.0F, 3.0F, new CubeDeformation(0.0F))
                .texOffs(53, 42).addBox(0.0F, -15.3333F, 6.5833F, 0.0F, 3.0F, 3.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, -1.6667F, -9.0833F));

        birthday.addOrReplaceChild("thingy", CubeListBuilder.create().texOffs(53, 45).addBox(-1.5F, -15.3333F, 8.0F, 3.0F, 3.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 0.0F, 0.0F));

        PartDefinition arm3 = ribs.addOrReplaceChild("arm3", CubeListBuilder.create().texOffs(26, 32).mirror().addBox(-1.0F, -1.0F, -1.0F, 2.0F, 8.0F, 2.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offsetAndRotation(-4.0F, -5.0F, -1.5F, 0.121F, -0.05F, 0.3897F));

        PartDefinition arm4 = arm3.addOrReplaceChild("arm4", CubeListBuilder.create().texOffs(32, 0).mirror().addBox(-1.0F, 0.0F, -1.0F, 2.0F, 8.0F, 2.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offsetAndRotation(0.0F, 7.0F, 0.0F, -1.2952F, -0.1063F, 0.795F));

        arm4.addOrReplaceChild("finger3", CubeListBuilder.create().texOffs(20, 34).mirror().addBox(-1.5F, -0.5F, 0.0F, 3.0F, 3.0F, 0.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offsetAndRotation(-0.5F, 8.5F, -0.9F, -0.3414F, 0.0741F, 0.2054F));

        arm4.addOrReplaceChild("finger4", CubeListBuilder.create().texOffs(14, 33).mirror().addBox(-1.5F, -0.5F, 0.0F, 3.0F, 3.0F, 0.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offsetAndRotation(0.0F, 8.5F, 0.9F, 0.1309F, 0.0F, 0.2182F));

        PartDefinition arm1 = ribs.addOrReplaceChild("arm1", CubeListBuilder.create().texOffs(26, 32).addBox(-1.0F, -1.0F, -1.0F, 2.0F, 8.0F, 2.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(4.0F, -5.0F, -1.5F, 0.0832F, 0.0262F, -0.3043F));

        PartDefinition arm2 = arm1.addOrReplaceChild("arm2", CubeListBuilder.create().texOffs(32, 0).addBox(-1.0F, 0.0F, -1.0F, 2.0F, 8.0F, 2.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 7.0F, 0.0F, -1.4634F, 0.0387F, -1.0904F));

        arm2.addOrReplaceChild("finger1", CubeListBuilder.create().texOffs(20, 34).addBox(-1.5F, -0.5F, 0.0F, 3.0F, 3.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.5F, 8.5F, -0.9F, -0.2182F, 0.0F, -0.5672F));

        arm2.addOrReplaceChild("finger2", CubeListBuilder.create().texOffs(14, 33).addBox(-1.5F, -0.5F, 0.0F, 3.0F, 3.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 8.5F, 0.9F, 0.2618F, 0.0F, 0.0F));

        arm2.addOrReplaceChild("bone_weapon", CubeListBuilder.create().texOffs(0, 42).addBox(-2.0F, -0.5F, -1.0F, 5.0F, 1.0F, 4.0F, new CubeDeformation(0.0F))
                .texOffs(0, 47).addBox(-10.0F, -0.5F, -9.0F, 5.0F, 1.0F, 4.0F, new CubeDeformation(0.0F))
                .texOffs(10, 56).addBox(-1.0F, -0.5F, 3.0F, 3.0F, 1.0F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(1, 58).addBox(-8.0F, -0.5F, -10.0F, 2.0F, 1.0F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(8, 58).addBox(3.0F, -0.5F, 0.0F, 1.0F, 1.0F, 2.0F, new CubeDeformation(0.0F))
                .texOffs(0, 54).addBox(-4.0F, -0.5F, -2.0F, 4.0F, 1.0F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(10, 54).addBox(-5.0F, -0.5F, -3.0F, 4.0F, 1.0F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(12, 52).addBox(-6.0F, -0.5F, -4.0F, 4.0F, 1.0F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(0, 52).addBox(-8.0F, -0.5F, -5.0F, 5.0F, 1.0F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(0, 44).addBox(-5.0F, -0.5F, -6.0F, 1.0F, 1.0F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(0, 42).addBox(-3.0F, -0.5F, -1.0F, 1.0F, 1.0F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(2, 60).addBox(-11.0F, -0.5F, -8.0F, 1.0F, 1.0F, 2.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(6.5F, 6.0F, 0.0F, -1.5943F, -0.0368F, -1.0031F));

        return LayerDefinition.create(meshdefinition, 64, 64);
    }

    @Override
    public void setupAnim(Entity entity, float limbSwing, float limbSwingAmount, float ageInTicks, float netHeadYaw, float headPitch) {
        this.root().getAllParts().forEach(ModelPart::resetPose);
        if (entity instanceof FunnyboneEntity funnybone) {
            this.animate(funnybone.getAnimationState("idle"), FunnyboneAnimation.IDLE, ageInTicks, funnybone.getAnimationSpeed());
            this.animate(funnybone.getAnimationState("run"), FunnyboneAnimation.RUN, ageInTicks, funnybone.getAnimationSpeed());
            this.animate(funnybone.getAnimationState("fly"), FunnyboneAnimation.FLY, ageInTicks, funnybone.getAnimationSpeed());
            this.animate(funnybone.getAnimationState("spawn"), FunnyboneAnimation.SPAWN, ageInTicks, funnybone.getAnimationSpeed());
            this.animate(funnybone.getAnimationState("throw"), FunnyboneAnimation.THROW, ageInTicks, funnybone.getAnimationSpeed());

            Calendar calendar = Calendar.getInstance();
            this.head.getChild("birthday").visible = calendar.get(Calendar.MONTH) == Calendar.FEBRUARY && calendar.get(Calendar.DAY_OF_MONTH) < 8;

            this.bone_weapon.visible = funnybone.shouldShowBone();

            if (!funnybone.isFlying()) {
                this.head.yRot = netHeadYaw * ((float) Math.PI / 180F);
                this.head.xRot = headPitch * ((float) Math.PI / 180F) - 0.7F;
            } else {
                this.head.xRot = -70.0F;
                this.head.yRot = 0.0F;
            }
            this.head.xScale = 1.25F;
            this.head.yScale = 1.25F;
            this.head.zScale = 1.25F;

            this.spine.xScale = 0.75F;
            this.spine.yScale = 0.75F;
            this.spine.zScale = 0.75F;

            this.leg1.xScale = 0.75F;
            this.leg1.yScale = 0.75F;
            this.leg1.zScale = 0.75F;

            this.leg3.xScale = 0.75F;
            this.leg3.yScale = 0.75F;
            this.leg3.zScale = 0.75F;

            if (funnybone.idleAnimationState.isStarted()) {
                this.arm3.xRot = Mth.cos(limbSwing * 0.6662F + (float) Math.PI) * 2.0F * limbSwingAmount * 0.5F;
                this.arm1.xRot = Mth.cos(limbSwing * 0.6662F) * 2.0F * limbSwingAmount * 0.5F;
                this.leg3.xRot = (Mth.cos(limbSwing * 0.6662F) * 1.4F * limbSwingAmount * 1.0F) - 0.5F;
                this.leg1.xRot = (Mth.cos(limbSwing * 0.6662F + (float) Math.PI) * 1.4F * limbSwingAmount * 1.0F) - 1.0f;
            }

            if (!funnybone.isThrowing) {
                float moveX = (float) (funnybone.getX() - funnybone.xo);
                float moveZ = (float) (funnybone.getZ() - funnybone.zo);
                float speed = Mth.sqrt(moveX * moveX + moveZ * moveZ);
                if (speed > 0.2) {
                    if (!funnybone.runAnimationState.isStarted() && this.isNotAnimating(funnybone)) {
                        funnybone.idleAnimationState.stop();
                        funnybone.runAnimationState.start(funnybone.tickCount);
                    }
                } else if (!funnybone.idleAnimationState.isStarted() && this.isNotAnimating(funnybone)) {
                    funnybone.runAnimationState.stop();
                    funnybone.idleAnimationState.start(funnybone.tickCount);
                } else if (!this.isNotAnimating(funnybone)) {
                    funnybone.idleAnimationState.stop();
                    funnybone.runAnimationState.stop();
                }
            }
        }
    }

    private boolean isNotAnimating(FunnyboneEntity funnybone) {
        return !funnybone.flyAnimationState.isStarted() && !funnybone.spawnAnimationState.isStarted() && !funnybone.throwAnimationState.isStarted();
    }

    @Override
    public void renderToBuffer(PoseStack poseStack, VertexConsumer vertexConsumer, int packedLight, int packedOverlay, float red, float green, float blue, float alpha) {
        this.root().render(poseStack, vertexConsumer, packedLight, packedOverlay, red, green, blue, alpha);
    }

    @Override
    public ModelPart root() {
        return this.root;
    }
}