package com.yellowbrossproductions.illageandspillage.client.model;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.yellowbrossproductions.illageandspillage.IllageAndSpillage;
import com.yellowbrossproductions.illageandspillage.client.model.animation.RagnoAnimation;
import com.yellowbrossproductions.illageandspillage.client.model.animation.RagnoAnimation2;
import com.yellowbrossproductions.illageandspillage.entities.RagnoEntity;
import net.minecraft.client.model.HierarchicalModel;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.Entity;

import java.util.Calendar;

public class RagnoModel<T extends Entity> extends HierarchicalModel<T> {
    public static final ModelLayerLocation LAYER_LOCATION = new ModelLayerLocation(new ResourceLocation(IllageAndSpillage.MOD_ID, "ragno"), "main");
    private final ModelPart root;
    private final ModelPart all;

    public RagnoModel(ModelPart root) {
        this.root = root;
        this.all = root.getChild("all");
    }

    public static LayerDefinition createBodyLayer() {
        MeshDefinition meshdefinition = new MeshDefinition();
        PartDefinition partdefinition = meshdefinition.getRoot();

        PartDefinition all = partdefinition.addOrReplaceChild("all", CubeListBuilder.create(), PartPose.offset(0.0F, -2.0F, 0.0F));

        PartDefinition neck = all.addOrReplaceChild("neck", CubeListBuilder.create().texOffs(68, 0).addBox(-5.0F, -5.0F, -16.0F, 10.0F, 10.0F, 16.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 3.0F, -6.0F, -0.1745F, 0.0F, 0.0F));

        PartDefinition ragno_head = neck.addOrReplaceChild("ragno_head", CubeListBuilder.create().texOffs(0, 0).addBox(-8.0F, -20.0F, -14.0F, 16.0F, 20.0F, 16.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 8.0F, -11.0F, 0.2618F, 0.0F, 0.0F));

        ragno_head.addOrReplaceChild("nose", CubeListBuilder.create().texOffs(0, 0).addBox(-2.0F, -1.0F, -3.0F, 4.0F, 8.0F, 4.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, -5.0F, -15.0F, -0.0873F, 0.0F, 0.0F));

        PartDefinition birthday = ragno_head.addOrReplaceChild("birthday", CubeListBuilder.create().texOffs(125, 85).addBox(-2.0F, -9.3333F, 6.0833F, 4.0F, 3.0F, 4.0F, new CubeDeformation(0.0F))
                .texOffs(113, 85).addBox(-1.5F, -12.3333F, 6.5833F, 3.0F, 3.0F, 3.0F, new CubeDeformation(0.0F))
                .texOffs(138, 82).addBox(0.0F, -15.3333F, 6.5833F, 0.0F, 3.0F, 3.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, -12.6667F, -13.0833F, 0.0F, 0.0F, 0.1309F));

        birthday.addOrReplaceChild("thingy", CubeListBuilder.create().texOffs(138, 85).addBox(-1.5F, -15.3333F, 8.0F, 3.0F, 3.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 0.0F, 0.0F));

        PartDefinition ragno_body = all.addOrReplaceChild("ragno_body", CubeListBuilder.create().texOffs(120, 0).addBox(-8.0F, -7.0F, -10.5F, 16.0F, 14.0F, 22.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 0.0F, 0.0F, 0.1745F, 0.0F, 0.0F));

        ragno_body.addOrReplaceChild("abdomen", CubeListBuilder.create().texOffs(0, 36).addBox(-13.0F, -13.0F, 0.0F, 26.0F, 26.0F, 30.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 0.0F, 8.5F, 0.2618F, 0.0F, 0.0F));

        PartDefinition leg4 = all.addOrReplaceChild("leg4", CubeListBuilder.create(), PartPose.offset(5.0F, 2.0F, 2.5F));

        PartDefinition legrotation4 = leg4.addOrReplaceChild("legrotation4", CubeListBuilder.create().texOffs(154, 36).addBox(0.0F, -2.5F, -1.5F, 16.0F, 5.0F, 5.0F, new CubeDeformation(0.5F)), PartPose.offsetAndRotation(0.0F, 0.0F, 0.0F, 0.4363F, -0.2618F, -0.7854F));

        legrotation4.addOrReplaceChild("knee4", CubeListBuilder.create().texOffs(92, 46).addBox(-1.0F, -2.0F, -1.0F, 48.0F, 4.0F, 4.0F, new CubeDeformation(0.0F))
                .texOffs(124, 54).addBox(15.0F, -2.0F, -1.0F, 32.0F, 4.0F, 4.0F, new CubeDeformation(1.0F)), PartPose.offsetAndRotation(16.0F, 0.0F, 0.0F, 0.0F, 0.0F, 1.5708F));

        PartDefinition leg8 = all.addOrReplaceChild("leg8", CubeListBuilder.create(), PartPose.offset(-5.0F, 2.0F, 4.5F));

        PartDefinition legrotation8 = leg8.addOrReplaceChild("legrotation8", CubeListBuilder.create().texOffs(154, 36).addBox(0.0F, -2.5F, -1.5F, 16.0F, 5.0F, 5.0F, new CubeDeformation(0.5F)), PartPose.offsetAndRotation(0.0F, 0.0F, 0.0F, 2.7053F, -0.2618F, -2.3562F));

        legrotation8.addOrReplaceChild("knee8", CubeListBuilder.create().texOffs(92, 46).addBox(-1.0F, -2.0F, -1.0F, 48.0F, 4.0F, 4.0F, new CubeDeformation(0.0F))
                .texOffs(124, 54).addBox(15.0F, -2.0F, -1.0F, 32.0F, 4.0F, 4.0F, new CubeDeformation(1.0F)), PartPose.offsetAndRotation(16.0F, 0.0F, 0.0F, 0.0F, 0.0F, 1.5708F));

        PartDefinition leg3 = all.addOrReplaceChild("leg3", CubeListBuilder.create(), PartPose.offset(5.0F, 2.0F, -1.5F));

        PartDefinition legrotation3 = leg3.addOrReplaceChild("legrotation3", CubeListBuilder.create().texOffs(154, 36).addBox(0.0F, -2.5F, -1.5F, 16.0F, 5.0F, 5.0F, new CubeDeformation(0.5F)), PartPose.offsetAndRotation(0.0F, 0.0F, 0.0F, 0.2618F, -0.1745F, -0.2618F));

        legrotation3.addOrReplaceChild("knee3", CubeListBuilder.create().texOffs(92, 46).addBox(-1.0F, -2.0F, -1.0F, 48.0F, 4.0F, 4.0F, new CubeDeformation(0.0F))
                .texOffs(124, 54).addBox(15.0F, -2.0F, -1.0F, 32.0F, 4.0F, 4.0F, new CubeDeformation(1.0F)), PartPose.offsetAndRotation(16.0F, 0.0F, 0.0F, 0.0F, 0.0F, 0.8727F));

        PartDefinition leg7 = all.addOrReplaceChild("leg7", CubeListBuilder.create(), PartPose.offset(-6.0F, 2.0F, -0.5F));

        PartDefinition legrotation7 = leg7.addOrReplaceChild("legrotation7", CubeListBuilder.create().texOffs(154, 36).addBox(0.0F, -2.5F, -1.5F, 16.0F, 5.0F, 5.0F, new CubeDeformation(0.5F)), PartPose.offsetAndRotation(0.0F, 0.0F, 1.0F, 2.8798F, -0.1745F, -2.8798F));

        legrotation7.addOrReplaceChild("knee7", CubeListBuilder.create().texOffs(92, 46).addBox(-1.0F, -2.0F, -1.0F, 48.0F, 4.0F, 4.0F, new CubeDeformation(0.0F))
                .texOffs(124, 54).addBox(15.0F, -2.0F, -1.0F, 32.0F, 4.0F, 4.0F, new CubeDeformation(1.0F)), PartPose.offsetAndRotation(16.0F, 0.0F, 0.0F, 0.0F, 0.0F, 0.8727F));

        PartDefinition leg2 = all.addOrReplaceChild("leg2", CubeListBuilder.create(), PartPose.offset(5.0F, 2.0F, -5.5F));

        PartDefinition legrotation2 = leg2.addOrReplaceChild("legrotation2", CubeListBuilder.create().texOffs(154, 36).addBox(0.0F, -2.5F, -1.5F, 16.0F, 5.0F, 5.0F, new CubeDeformation(0.5F)), PartPose.offsetAndRotation(0.0F, 0.0F, 0.0F, -0.2618F, 0.0873F, -0.3491F));

        legrotation2.addOrReplaceChild("knee2", CubeListBuilder.create().texOffs(92, 46).addBox(-1.0F, -2.0F, -1.0F, 48.0F, 4.0F, 4.0F, new CubeDeformation(0.0F))
                .texOffs(124, 54).addBox(15.0F, -2.0F, -1.0F, 32.0F, 4.0F, 4.0F, new CubeDeformation(1.0F)), PartPose.offsetAndRotation(16.0F, 0.0F, 0.0F, 0.0F, 0.0F, 1.0472F));

        PartDefinition leg6 = all.addOrReplaceChild("leg6", CubeListBuilder.create(), PartPose.offset(-6.0F, 2.0F, -3.5F));

        PartDefinition legrotation6 = leg6.addOrReplaceChild("legrotation6", CubeListBuilder.create().texOffs(154, 36).addBox(0.0F, -2.5F, -1.5F, 16.0F, 5.0F, 5.0F, new CubeDeformation(0.5F)), PartPose.offsetAndRotation(0.0F, 0.0F, 0.0F, -2.8798F, 0.0873F, -2.7925F));

        legrotation6.addOrReplaceChild("knee6", CubeListBuilder.create().texOffs(92, 46).addBox(-1.0F, -2.0F, -1.0F, 48.0F, 4.0F, 4.0F, new CubeDeformation(0.0F))
                .texOffs(124, 54).addBox(15.0F, -2.0F, -1.0F, 32.0F, 4.0F, 4.0F, new CubeDeformation(1.0F)), PartPose.offsetAndRotation(16.0F, 0.0F, 0.0F, 0.0F, 0.0F, 1.0472F));

        PartDefinition leg1 = all.addOrReplaceChild("leg1", CubeListBuilder.create(), PartPose.offset(5.0F, 2.0F, -9.5F));

        PartDefinition legrotation1 = leg1.addOrReplaceChild("legrotation1", CubeListBuilder.create().texOffs(154, 36).addBox(0.0F, -2.5F, -1.5F, 16.0F, 5.0F, 5.0F, new CubeDeformation(0.5F)), PartPose.offsetAndRotation(0.0F, 0.0F, 0.0F, -0.4363F, 0.6109F, -0.7854F));

        legrotation1.addOrReplaceChild("knee1", CubeListBuilder.create().texOffs(92, 46).addBox(-1.0F, -2.0F, -1.0F, 48.0F, 4.0F, 4.0F, new CubeDeformation(0.0F))
                .texOffs(124, 54).addBox(15.0F, -2.0F, -1.0F, 32.0F, 4.0F, 4.0F, new CubeDeformation(1.0F)), PartPose.offsetAndRotation(16.0F, 0.0F, 0.0F, 0.0F, 0.0F, 1.4835F));

        PartDefinition leg5 = all.addOrReplaceChild("leg5", CubeListBuilder.create(), PartPose.offset(-8.0F, 2.0F, -9.5F));

        PartDefinition legrotation5 = leg5.addOrReplaceChild("legrotation5", CubeListBuilder.create().texOffs(154, 36).addBox(0.0F, -2.5F, -1.5F, 16.0F, 5.0F, 5.0F, new CubeDeformation(0.5F)), PartPose.offsetAndRotation(0.0F, 0.0F, 0.0F, -2.7053F, 0.6109F, -2.3562F));

        legrotation5.addOrReplaceChild("knee5", CubeListBuilder.create().texOffs(92, 46).addBox(-1.0F, -2.0F, -1.0F, 48.0F, 4.0F, 4.0F, new CubeDeformation(0.0F))
                .texOffs(124, 54).addBox(15.0F, -2.0F, -1.0F, 32.0F, 4.0F, 4.0F, new CubeDeformation(1.0F)), PartPose.offsetAndRotation(16.0F, 0.0F, 0.0F, 0.0F, 0.0F, 1.4835F));

        return LayerDefinition.create(meshdefinition, 196, 128);
    }

    @Override
    public void setupAnim(T entity, float limbSwing, float limbSwingAmount, float ageInTicks, float netHeadYaw, float headPitch) {
        this.root().getAllParts().forEach(ModelPart::resetPose);
        ModelPart head = this.all.getChild("neck").getChild("ragno_head");
        ModelPart neck = this.all.getChild("neck");
        ModelPart abdomen = this.all.getChild("ragno_body").getChild("abdomen");
        ModelPart leg1 = this.all.getChild("leg1");
        ModelPart leg2 = this.all.getChild("leg2");
        ModelPart leg3 = this.all.getChild("leg3");
        ModelPart leg4 = this.all.getChild("leg4");
        ModelPart leg5 = this.all.getChild("leg5");
        ModelPart leg6 = this.all.getChild("leg6");
        ModelPart leg7 = this.all.getChild("leg7");
        ModelPart leg8 = this.all.getChild("leg8");

        if (entity instanceof RagnoEntity ragno) {
            float craziness = ragno.getShakeMultiplier() * 4.0F;

            this.animate(ragno.getAnimationState("intro1"), RagnoAnimation.INTRO1, ageInTicks, ragno.getAnimationSpeed());
            this.animate(ragno.getAnimationState("intro2"), RagnoAnimation.INTRO2, ageInTicks, ragno.getAnimationSpeed());
            this.animate(ragno.getAnimationState("phase"), RagnoAnimation.PHASE, ageInTicks, ragno.getAnimationSpeed());
            this.animate(ragno.getAnimationState("block"), RagnoAnimation.BLOCK, ageInTicks, ragno.getAnimationSpeed());
            this.animate(ragno.getAnimationState("attack"), RagnoAnimation.ATTACK, ageInTicks, ragno.getAnimationSpeed());
            this.animate(ragno.getAnimationState("web"), RagnoAnimation.WEB, ageInTicks, ragno.getAnimationSpeed());
            this.animate(ragno.getAnimationState("webNet"), RagnoAnimation2.WEB_NET, ageInTicks, ragno.getAnimationSpeed());
            this.animate(ragno.getAnimationState("pullIn"), RagnoAnimation2.PULL_IN, ageInTicks, ragno.getAnimationSpeed());
            this.animate(ragno.getAnimationState("netSlam"), RagnoAnimation.PULL_SLAM, ageInTicks, ragno.getAnimationSpeed());
            this.animate(ragno.getAnimationState("jump"), RagnoAnimation.JUMP, ageInTicks, ragno.getAnimationSpeed());
            this.animate(ragno.getAnimationState("land"), RagnoAnimation.LAND, ageInTicks, ragno.getAnimationSpeed());
            this.animate(ragno.getAnimationState("leap"), RagnoAnimation.LEAP, ageInTicks, ragno.getAnimationSpeed());
            this.animate(ragno.getAnimationState("burrow"), RagnoAnimation.BURROW, ageInTicks, ragno.getAnimationSpeed());
            this.animate(ragno.getAnimationState("popup"), RagnoAnimation.POPUP, ageInTicks, ragno.getAnimationSpeed());
            this.animate(ragno.getAnimationState("charge"), RagnoAnimation.CHARGE, ageInTicks, ragno.getAnimationSpeed());
            this.animate(ragno.getAnimationState("cough"), RagnoAnimation.COUGH, ageInTicks, ragno.getAnimationSpeed());
            this.animate(ragno.getAnimationState("stun"), RagnoAnimation.STUN, ageInTicks, ragno.getAnimationSpeed());
            this.animate(ragno.getAnimationState("fall"), RagnoAnimation.FALL, ageInTicks, ragno.getAnimationSpeed());
            this.animate(ragno.getAnimationState("grab"), RagnoAnimation2.GRAB, ageInTicks, ragno.getAnimationSpeed());
            this.animate(ragno.getAnimationState("breath"), RagnoAnimation2.BREATH, ageInTicks, ragno.getAnimationSpeed());
            this.animate(ragno.getAnimationState("death"), RagnoAnimation2.DEATH, ageInTicks, ragno.getAnimationSpeed());

            Calendar calendar = Calendar.getInstance();
            head.getChild("birthday").visible = calendar.get(Calendar.MONTH) == Calendar.FEBRUARY && calendar.get(Calendar.DAY_OF_MONTH) < 8;

            if (!ragno.isAlive()) {
                this.all.yRot = (float) Math.toRadians(180);
            } else {
                this.all.yRot = 0;
            }

            head.yRot += netHeadYaw * ((float) Math.PI / 180F);
            head.xRot += headPitch * ((float) Math.PI / 180F);

            RandomSource random = ragno.getRandom();

            head.yRot += (((-0.5F + random.nextFloat()) * 0.08F) * craziness) * ((float) Math.PI / 180F);
            head.xRot += (((-0.5F + random.nextFloat()) * 0.08F) * craziness) * ((float) Math.PI / 180F);
            head.zRot += (((-0.5F + random.nextFloat()) * 0.08F) * craziness) * ((float) Math.PI / 180F);

            neck.yRot += (((-0.5F + random.nextFloat()) * 0.04F) * craziness) * ((float) Math.PI / 180F);
            neck.xRot += (((-0.5F + random.nextFloat()) * 0.04F) * craziness) * ((float) Math.PI / 180F);

            abdomen.yRot += (((-0.5F + random.nextFloat()) * 0.16F) * craziness) * ((float) Math.PI / 180F);
            abdomen.xRot += (((-0.5F + random.nextFloat()) * 0.08F) * craziness) * ((float) Math.PI / 180F);
            abdomen.zRot += (((-0.5F + random.nextFloat()) * 0.08F) * craziness) * ((float) Math.PI / 180F);

            if (ragno.getFrame() >= 10 && ragno.getFrame() <= 12) {
                float f3 = ageInTicks / 60.0F;
                float mult1 = 15.0F;
                float mult2 = 20.0F;

                head.yRot += (Mth.cos(f3 * 40 * mult1) * mult2) * ((float) Math.PI / 180F);
                head.xRot += ((Mth.cos(f3 * 20 * mult1) * mult2) / 8.0F) * ((float) Math.PI / 180F);
                head.zRot += (Mth.cos(f3 * 60 * mult1) * mult2) * ((float) Math.PI / 180F);

                neck.yRot += (Mth.cos(f3 * 30 * mult1) * mult2) * ((float) Math.PI / 180F);
                neck.xRot += ((Mth.cos(f3 * 50 * mult1) * mult2) / 8.0F) * ((float) Math.PI / 180F);
            }

            if (ragno.getAttackType() != 7) {
                float $$9 = -(Mth.cos(limbSwing * 0.6662F * 2.0F + 0.0F) * 0.4F) * limbSwingAmount;
                float $$10 = -(Mth.cos(limbSwing * 0.6662F * 2.0F + 3.1415927F) * 0.4F) * limbSwingAmount;
                float $$11 = -(Mth.cos(limbSwing * 0.6662F * 2.0F + 1.5707964F) * 0.4F) * limbSwingAmount;
                float $$12 = -(Mth.cos(limbSwing * 0.6662F * 2.0F + 4.712389F) * 0.4F) * limbSwingAmount;
                float $$13 = Math.abs(Mth.sin(limbSwing * 0.6662F + 0.0F) * 0.4F) * limbSwingAmount;
                float $$14 = Math.abs(Mth.sin(limbSwing * 0.6662F + 3.1415927F) * 0.4F) * limbSwingAmount;
                float $$15 = Math.abs(Mth.sin(limbSwing * 0.6662F + 1.5707964F) * 0.4F) * limbSwingAmount;
                float $$16 = Math.abs(Mth.sin(limbSwing * 0.6662F + 4.712389F) * 0.4F) * limbSwingAmount;
                ModelPart var10000 = leg8;
                var10000.yRot += $$9;
                var10000 = leg4;
                var10000.yRot -= $$9;
                var10000 = leg7;
                var10000.yRot += $$10;
                var10000 = leg3;
                var10000.yRot -= $$10;
                var10000 = leg6;
                var10000.yRot += $$11;
                var10000 = leg2;
                var10000.yRot -= $$11;
                var10000 = leg5;
                var10000.yRot += $$12;
                var10000 = leg1;
                var10000.yRot -= $$12;
                var10000 = leg8;
                var10000.zRot += $$13;
                var10000 = leg4;
                var10000.zRot -= $$13;
                var10000 = leg7;
                var10000.zRot += $$14;
                var10000 = leg3;
                var10000.zRot -= $$14;
                var10000 = leg6;
                var10000.zRot += $$15;
                var10000 = leg2;
                var10000.zRot -= $$15;
                var10000 = leg5;
                var10000.zRot += $$16;
                var10000 = leg1;
                var10000.zRot -= $$16;
            } else {
                ModelPart var10000 = leg8;
                var10000.yRot = 0;
                var10000 = leg4;
                var10000.yRot = 0;
                var10000 = leg7;
                var10000.yRot = 0;
                var10000 = leg3;
                var10000.yRot = 0;
                var10000 = leg6;
                var10000.yRot = 0;
                var10000 = leg2;
                var10000.yRot = 0;
                var10000 = leg5;
                var10000.yRot = 0;
                var10000 = leg1;
                var10000.yRot = 0;
                var10000 = leg8;
                var10000.zRot = 0;
                var10000 = leg4;
                var10000.zRot = 0;
                var10000 = leg7;
                var10000.zRot = 0;
                var10000 = leg3;
                var10000.zRot = 0;
                var10000 = leg6;
                var10000.zRot = 0;
                var10000 = leg2;
                var10000.zRot = 0;
                var10000 = leg5;
                var10000.zRot = 0;
                var10000 = leg1;
                var10000.zRot = 0;
            }
        }
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