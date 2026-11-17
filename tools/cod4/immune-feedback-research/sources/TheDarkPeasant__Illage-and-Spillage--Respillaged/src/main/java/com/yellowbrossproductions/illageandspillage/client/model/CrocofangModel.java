package com.yellowbrossproductions.illageandspillage.client.model;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.yellowbrossproductions.illageandspillage.client.model.animation.CrocofangAnimation;
import com.yellowbrossproductions.illageandspillage.entities.CrocofangEntity;
import net.minecraft.client.model.HierarchicalModel;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;

import java.util.Calendar;

public class CrocofangModel<T extends Entity> extends HierarchicalModel<T> {
    public static final ModelLayerLocation LAYER_LOCATION = new ModelLayerLocation(new ResourceLocation("illageandspillage", "crocofang"), "main");
    private final ModelPart root;
    private final ModelPart bone;

    public CrocofangModel(ModelPart root) {
        this.root = root;
        this.bone = root.getChild("bone");
    }

    public static LayerDefinition createBodyLayer() {
        MeshDefinition meshdefinition = new MeshDefinition();
        PartDefinition partdefinition = meshdefinition.getRoot();

        PartDefinition bone = partdefinition.addOrReplaceChild("bone", CubeListBuilder.create(), PartPose.offsetAndRotation(0.0F, 24.0F, 0.0F, 0.0F, 3.1416F, 0.0F));

        PartDefinition body = bone.addOrReplaceChild("body", CubeListBuilder.create(), PartPose.offset(0.0F, -15.0F, -2.5F));

        body.addOrReplaceChild("torax", CubeListBuilder.create().texOffs(26, 52).addBox(-9.5F, -7.75F, -14.5F, 19.0F, 15.0F, 28.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, -0.25F, 1.0F));

        PartDefinition tail = body.addOrReplaceChild("tail", CubeListBuilder.create().texOffs(14, 129).addBox(-6.5F, -7.0F, -17.0F, 13.0F, 13.0F, 17.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 0.0F, -13.5F));

        PartDefinition tail2 = tail.addOrReplaceChild("tail2", CubeListBuilder.create().texOffs(196, 108).addBox(-4.0F, -5.25F, -16.0F, 8.0F, 11.0F, 16.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, -0.75F, -17.0F));

        tail2.addOrReplaceChild("tail3", CubeListBuilder.create().texOffs(16, 209).addBox(-4.0F, -5.75F, -16.0F, 8.0F, 11.0F, 16.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 0.5F, -16.0F));

        PartDefinition head = body.addOrReplaceChild("head", CubeListBuilder.create().texOffs(95, 212).addBox(-7.5F, -6.3333F, 0.0833F, 15.0F, 13.0F, 10.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, -0.6667F, 14.4167F));

        head.addOrReplaceChild("collar", CubeListBuilder.create().texOffs(181, 214).addBox(-8.5F, -7.5F, -2.5F, 17.0F, 15.0F, 5.0F, new CubeDeformation(0.0F))
                .texOffs(210, 149).addBox(-6.5F, -10.5F, -1.5F, 3.0F, 3.0F, 3.0F, new CubeDeformation(0.0F))
                .texOffs(229, 149).addBox(3.5F, -10.5F, -1.5F, 3.0F, 3.0F, 3.0F, new CubeDeformation(0.0F))
                .texOffs(191, 149).addBox(-11.5F, -5.5F, -1.5F, 3.0F, 3.0F, 3.0F, new CubeDeformation(0.0F))
                .texOffs(191, 163).addBox(-11.5F, 2.5F, -1.5F, 3.0F, 3.0F, 3.0F, new CubeDeformation(0.0F))
                .texOffs(210, 163).addBox(8.5F, -5.5F, -1.5F, 3.0F, 3.0F, 3.0F, new CubeDeformation(0.0F))
                .texOffs(229, 163).addBox(8.5F, 2.5F, -1.5F, 3.0F, 3.0F, 3.0F, new CubeDeformation(0.0F))
                .texOffs(192, 177).addBox(3.5F, 7.5F, -1.5F, 3.0F, 3.0F, 3.0F, new CubeDeformation(0.0F))
                .texOffs(211, 177).addBox(-6.5F, 7.5F, -1.5F, 3.0F, 3.0F, 3.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 0.1667F, 3.5833F));

        PartDefinition mounth = head.addOrReplaceChild("mounth", CubeListBuilder.create(), PartPose.offset(0.0F, 15.6667F, -11.9167F));

        mounth.addOrReplaceChild("mounth_part1", CubeListBuilder.create().texOffs(100, 152).addBox(-7.5F, -5.0F, 0.0F, 15.0F, 5.0F, 22.0F, new CubeDeformation(0.1F)), PartPose.offset(0.0F, -14.75F, 22.0F));

        mounth.addOrReplaceChild("mounth_part2", CubeListBuilder.create().texOffs(100, 113).addBox(-7.5F, 0.0F, 0.0F, 15.0F, 5.0F, 22.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, -15.75F, 22.0F));

        PartDefinition birthday = head.addOrReplaceChild("birthday", CubeListBuilder.create().texOffs(13, 15).addBox(-2.0F, -9.3333F, 6.0833F, 4.0F, 3.0F, 4.0F, new CubeDeformation(0.0F))
                .texOffs(1, 15).addBox(-1.5F, -12.3333F, 6.5833F, 3.0F, 3.0F, 3.0F, new CubeDeformation(0.0F))
                .texOffs(26, 12).addBox(0.0F, -15.3333F, 6.5833F, 0.0F, 3.0F, 3.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 0.0F, 0.0F));

        birthday.addOrReplaceChild("thingy", CubeListBuilder.create().texOffs(26, 15).addBox(-1.5F, -15.3333F, 8.0F, 3.0F, 3.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 0.0F, 0.0F));

        PartDefinition legs = body.addOrReplaceChild("legs", CubeListBuilder.create(), PartPose.offset(0.0F, -0.25F, 0.25F));

        PartDefinition leg1 = legs.addOrReplaceChild("leg1", CubeListBuilder.create(), PartPose.offset(-9.5F, 0.25F, 8.75F));

        leg1.addOrReplaceChild("cube_r1", CubeListBuilder.create().texOffs(168, 56).addBox(-3.0F, -9.0F, -3.5F, 6.0F, 18.0F, 7.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(-3.0F, 6.0F, 0.0F, 0.0F, 3.1416F, 0.0F));

        PartDefinition leg2 = legs.addOrReplaceChild("leg2", CubeListBuilder.create(), PartPose.offset(-9.5F, 0.25F, -8.25F));

        leg2.addOrReplaceChild("cube_r2", CubeListBuilder.create().texOffs(168, 18).addBox(-3.0F, -9.0F, -3.5F, 6.0F, 18.0F, 7.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(-3.0F, 6.0F, 0.0F, 0.0F, 3.1416F, 0.0F));

        PartDefinition leg3 = legs.addOrReplaceChild("leg3", CubeListBuilder.create(), PartPose.offset(9.5F, 0.25F, -8.25F));

        leg3.addOrReplaceChild("cube_r3", CubeListBuilder.create().texOffs(213, 56).addBox(-3.0F, -9.0F, -3.5F, 6.0F, 18.0F, 7.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(3.0F, 6.0F, 0.0F, 0.0F, 3.1416F, 0.0F));

        PartDefinition leg4 = legs.addOrReplaceChild("leg4", CubeListBuilder.create(), PartPose.offset(9.5F, 0.25F, 8.75F));

        leg4.addOrReplaceChild("cube_r4", CubeListBuilder.create().texOffs(214, 18).addBox(-3.0F, -9.0F, -3.5F, 6.0F, 18.0F, 7.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(3.0F, 6.0F, 0.0F, 0.0F, 3.1416F, 0.0F));

        return LayerDefinition.create(meshdefinition, 256, 256);
    }

    public void setupAnim(T entity, float limbSwing, float limbSwingAmount, float ageInTicks, float netHeadYaw, float headPitch) {
        this.root().getAllParts().forEach(ModelPart::resetPose);
        if (entity instanceof CrocofangEntity crocofang) {
            this.animate(crocofang.getAnimationState("attack"), CrocofangAnimation.BITE, ageInTicks, crocofang.getAnimationSpeed());
            this.animate(crocofang.getAnimationState("precharge"), CrocofangAnimation.PRECHARGE, ageInTicks, crocofang.getAnimationSpeed());
            this.animate(crocofang.getAnimationState("charge"), CrocofangAnimation.CHARGE, ageInTicks, crocofang.getAnimationSpeed());
            this.animate(crocofang.getAnimationState("stunned"), CrocofangAnimation.STUNNED, ageInTicks, crocofang.getAnimationSpeed());

            Calendar calendar = Calendar.getInstance();
            this.bone.getChild("body").getChild("head").getChild("birthday").visible = calendar.get(Calendar.MONTH) == Calendar.FEBRUARY && calendar.get(Calendar.DAY_OF_MONTH) < 8;

            ModelPart var10000 = this.bone.getChild("body").getChild("head");
            var10000.yRot += netHeadYaw * 0.017453292F;
            var10000 = this.bone.getChild("body").getChild("head");
            var10000.xRot += headPitch * 0.017453292F * -1.0F;
            if (!crocofang.isCharging()) {
                var10000 = this.bone.getChild("body").getChild("legs").getChild("leg1");
                var10000.xRot += Mth.cos(limbSwing * 0.6662F) * 1.4F * limbSwingAmount * 0.5F;
                var10000 = this.bone.getChild("body").getChild("legs").getChild("leg3");
                var10000.xRot += Mth.cos(limbSwing * 0.6662F) * 1.4F * limbSwingAmount * 0.5F;
                var10000 = this.bone.getChild("body").getChild("legs").getChild("leg2");
                var10000.xRot += Mth.cos(limbSwing * 0.6662F + 3.1415927F) * 1.4F * limbSwingAmount * 0.5F;
                var10000 = this.bone.getChild("body").getChild("legs").getChild("leg4");
                var10000.xRot += Mth.cos(limbSwing * 0.6662F + 3.1415927F) * 1.4F * limbSwingAmount * 0.5F;
            }
        }

    }

    public void renderToBuffer(PoseStack poseStack, VertexConsumer vertexConsumer, int packedLight, int packedOverlay, float red, float green, float blue, float alpha) {
        this.bone.render(poseStack, vertexConsumer, packedLight, packedOverlay, red, green, blue, alpha);
    }

    public ModelPart root() {
        return this.root;
    }
}
