package com.yellowbrossproductions.illageandspillage.client.model;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.yellowbrossproductions.illageandspillage.client.model.animation.ChagrinSentryAnimation;
import com.yellowbrossproductions.illageandspillage.entities.ChagrinSentryEntity;
import net.minecraft.client.model.HierarchicalModel;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.Entity;

import java.util.Calendar;

public class ChagrinSentryModel<T extends Entity> extends HierarchicalModel<T> {
    public static final ModelLayerLocation LAYER_LOCATION = new ModelLayerLocation(new ResourceLocation("illageandspillage", "chagrinsentry"), "main");
    private final ModelPart root;
    private final ModelPart sentry;
    private final ModelPart locker;
    private final ModelPart locker_lid;
    private final ModelPart upperBody;
    private final ModelPart neck;
    private final ModelPart head;
    private final ModelPart glow;
    private final ModelPart chest;
    private final ModelPart arm1;
    private final ModelPart elbow1;
    private final ModelPart arm2;
    private final ModelPart elbow2;
    private final ModelPart joint;
    private final ModelPart slab;

    public ChagrinSentryModel(ModelPart root) {
        this.root = root;
        this.sentry = this.root.getChild("sentry");
        this.locker = sentry.getChild("locker");
        this.locker_lid = locker.getChild("locker_lid");
        this.upperBody = sentry.getChild("upper_body");
        this.neck = upperBody.getChild("neck");
        this.head = upperBody.getChild("head");
        this.glow = head.getChild("glow");
        this.chest = upperBody.getChild("chest");
        this.arm1 = upperBody.getChild("arm1");
        this.elbow1 = arm1.getChild("elbow1");
        this.arm2 = upperBody.getChild("arm2");
        this.elbow2 = arm2.getChild("elbow2");
        this.joint = upperBody.getChild("joint");
        this.slab = sentry.getChild("slab");
    }

    public static LayerDefinition createBodyLayer() {
        MeshDefinition meshdefinition = new MeshDefinition();
        PartDefinition partdefinition = meshdefinition.getRoot();

        PartDefinition sentry = partdefinition.addOrReplaceChild("sentry", CubeListBuilder.create(), PartPose.offset(0.0F, 24.0F, 0.0F));

        PartDefinition locker = sentry.addOrReplaceChild("locker", CubeListBuilder.create().texOffs(0, 0).addBox(-7.0F, -2.0F, -7.0F, 14.0F, 2.0F, 14.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 0.0F, 0.0F));

        locker.addOrReplaceChild("locker_lid", CubeListBuilder.create().texOffs(0, 16).addBox(-7.0F, -4.0F, -14.0F, 14.0F, 4.0F, 14.0F, new CubeDeformation(0.0F))
                .texOffs(0, 16).addBox(-1.0F, -3.0F, -15.0F, 2.0F, 4.0F, 1.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, -2.0F, 7.0F));

        PartDefinition upper_body = sentry.addOrReplaceChild("upper_body", CubeListBuilder.create(), PartPose.offset(0.0F, -4.0F, 0.0F));

        upper_body.addOrReplaceChild("neck", CubeListBuilder.create().texOffs(56, 0).addBox(-1.0F, -18.0F, -1.0F, 2.0F, 17.0F, 2.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 4.0F, 0.0F));

        PartDefinition head = upper_body.addOrReplaceChild("head", CubeListBuilder.create().texOffs(64, 0).addBox(-6.0F, -12.0F, -6.0F, 12.0F, 12.0F, 12.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, -12.0F, 0.0F));

        head.addOrReplaceChild("glow", CubeListBuilder.create().texOffs(64, 64).addBox(-6.0F, -12.0F, -6.0F, 12.0F, 12.0F, 12.0F, new CubeDeformation(0.1F)), PartPose.offset(0.0F, 0.0F, 0.0F));

        PartDefinition birthday = head.addOrReplaceChild("birthday", CubeListBuilder.create().texOffs(72, 27).addBox(-2.0F, -9.3333F, 6.0833F, 4.0F, 3.0F, 4.0F, new CubeDeformation(0.0F))
                .texOffs(60, 27).addBox(-1.5F, -12.3333F, 6.5833F, 3.0F, 3.0F, 3.0F, new CubeDeformation(0.0F))
                .texOffs(85, 21).addBox(0.0F, -15.3333F, 6.5833F, 0.0F, 3.0F, 3.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, -5.6667F, -8.0833F));

        birthday.addOrReplaceChild("thingy", CubeListBuilder.create().texOffs(85, 27).addBox(-1.5F, -15.3333F, 8.0F, 3.0F, 3.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 0.0F, 0.0F));

        upper_body.addOrReplaceChild("chest", CubeListBuilder.create().texOffs(104, 0).addBox(-3.0F, -3.0F, -3.0F, 6.0F, 6.0F, 6.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, -8.0F, 0.0F));

        PartDefinition arm1 = upper_body.addOrReplaceChild("arm1", CubeListBuilder.create().texOffs(104, 24).addBox(-2.0F, -1.0F, -1.0F, 10.0F, 2.0F, 2.0F, new CubeDeformation(0.0F)), PartPose.offset(3.0F, -9.0F, 0.0F));

        arm1.addOrReplaceChild("elbow1", CubeListBuilder.create().texOffs(92, 28).addBox(-2.0F, -2.0F, -11.0F, 4.0F, 4.0F, 14.0F, new CubeDeformation(0.0F)), PartPose.offset(8.0F, 0.0F, 0.0F));

        PartDefinition arm2 = upper_body.addOrReplaceChild("arm2", CubeListBuilder.create().texOffs(104, 24).mirror().addBox(-8.0F, -1.0F, -1.0F, 10.0F, 2.0F, 2.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offset(-3.0F, -9.0F, 0.0F));

        arm2.addOrReplaceChild("elbow2", CubeListBuilder.create().texOffs(92, 28).mirror().addBox(-2.0F, -2.0F, -11.0F, 4.0F, 4.0F, 14.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offset(-8.0F, 0.0F, 0.0F));

        upper_body.addOrReplaceChild("joint", CubeListBuilder.create().texOffs(0, 50).addBox(-2.0F, -2.0F, -2.0F, 4.0F, 4.0F, 4.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 0.0F, 0.0F));

        sentry.addOrReplaceChild("slab", CubeListBuilder.create().texOffs(0, 34).addBox(-6.0F, -4.0F, -6.0F, 12.0F, 4.0F, 12.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 0.0F, 0.0F));

        return LayerDefinition.create(meshdefinition, 128, 128);
    }

    @Override
    public void setupAnim(Entity entity, float limbSwing, float limbSwingAmount, float ageInTicks, float netHeadYaw, float headPitch) {
        this.root().getAllParts().forEach(ModelPart::resetPose);

        if (entity instanceof ChagrinSentryEntity sentry) {
            Calendar calendar = Calendar.getInstance();
            this.head.getChild("birthday").visible = calendar.get(Calendar.MONTH) == Calendar.FEBRUARY && calendar.get(Calendar.DAY_OF_MONTH) < 8;

            float deltaYaw = sentry.yBodyRot - sentry.yBodyRotO;
            while (deltaYaw < -180.0F) deltaYaw += 360.0F;
            while (deltaYaw >= 180.0F) deltaYaw -= 360.0F;

            this.upperBody.yRot = (sentry.yBodyRotO + deltaYaw * sentry.getPartialTicks()) * ((float) Math.PI / 180F);
            this.head.xRot = headPitch * 0.017453292F;
            arm1.xRot = headPitch * 0.017453292F;
            arm2.xRot = headPitch * 0.017453292F;
            slab.setRotation(0, 0, 0);

            this.animate(sentry.getAnimationState("intro"), ChagrinSentryAnimation.INTRO, ageInTicks, sentry.getAnimationSpeed());
            this.animate(sentry.getAnimationState("shooting"), ChagrinSentryAnimation.SHOOT, ageInTicks, sentry.getAnimationSpeed());
            this.animate(sentry.getAnimationState("stun"), ChagrinSentryAnimation.POWER_DOWN, ageInTicks, sentry.getAnimationSpeed());

            this.locker.visible = sentry.shouldShowLocker();

            if (sentry.isInMotion()) {
                this.locker.xRot = ageInTicks * 25.0F * 0.017453292F;
                this.locker.yRot = ageInTicks * 15.0F * 0.017453292F;
                this.locker.zRot = ageInTicks * 20.0F * 0.017453292F;
                this.upperBody.visible = false;
                this.slab.visible = false;
            } else {
                this.locker.xRot = 0.0F;
                this.locker.yRot = 0.0F;
                this.locker.zRot = 0.0F;
                this.upperBody.visible = true;
                this.slab.visible = true;
            }
        }
    }

    @Override
    public void renderToBuffer(PoseStack poseStack, VertexConsumer vertexConsumer, int packedLight, int packedOverlay, float red, float green, float blue, float alpha) {
        this.root.render(poseStack, vertexConsumer, packedLight, packedOverlay, red, green, blue, alpha);
    }

    @Override
    public ModelPart root() {
        return this.root;
    }
}