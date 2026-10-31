package com.yellowbrossproductions.illageandspillage.client.model;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.yellowbrossproductions.illageandspillage.entities.PreserverEntity;
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

public class PreserverModel<T extends Entity> extends EntityModel<T> implements HeadedModel {
    public static final ModelLayerLocation LAYER_LOCATION = new ModelLayerLocation(new ResourceLocation("illageandspillage", "preserver"), "main");
    private final ModelPart body;

    public PreserverModel(ModelPart root) {
        this.body = root.getChild("body");
    }

    public static LayerDefinition createBodyLayer() {
        MeshDefinition meshdefinition = new MeshDefinition();
        PartDefinition partdefinition = meshdefinition.getRoot();

        PartDefinition body = partdefinition.addOrReplaceChild("body", CubeListBuilder.create(), PartPose.offset(0.0F, 6.0F, 0.0F));

        PartDefinition hay = body.addOrReplaceChild("hay", CubeListBuilder.create().texOffs(32, 0).addBox(-7.0F, -6.0F, -7.0F, 14.0F, 5.0F, 14.0F, new CubeDeformation(0.0F))
                .texOffs(0, 58).addBox(-7.5F, -8.0F, -7.5F, 15.0F, 3.0F, 15.0F, new CubeDeformation(0.0F))
                .texOffs(0, 58).addBox(-7.5F, 5.0F, -7.5F, 15.0F, 3.0F, 15.0F, new CubeDeformation(0.0F))
                .texOffs(0, 38).addBox(-7.0F, 6.0F, -7.0F, 14.0F, 6.0F, 14.0F, new CubeDeformation(0.0F))
                .texOffs(56, 38).addBox(-7.0F, -12.0F, -7.0F, 14.0F, 6.0F, 14.0F, new CubeDeformation(0.0F))
                .texOffs(32, 0).addBox(-7.0F, 1.0F, -7.0F, 14.0F, 5.0F, 14.0F, new CubeDeformation(0.0F))
                .texOffs(44, 19).addBox(-6.5F, -1.0F, -6.5F, 13.0F, 2.0F, 13.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 0.0F, 0.0F));

        hay.addOrReplaceChild("hay4", CubeListBuilder.create().texOffs(16, 19).mirror().addBox(-7.0F, 0.0F, 0.0F, 14.0F, 6.0F, 0.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offsetAndRotation(-7.0F, 6.0F, 0.0F, 0.0F, -1.5708F, 0.3491F));

        hay.addOrReplaceChild("hay3", CubeListBuilder.create().texOffs(16, 19).mirror().addBox(-7.0F, 0.0F, 0.0F, 14.0F, 6.0F, 0.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offsetAndRotation(7.0F, 6.0F, 0.0F, 0.0F, -1.5708F, -0.3491F));

        hay.addOrReplaceChild("hay2", CubeListBuilder.create().texOffs(16, 19).addBox(-7.0F, 0.0F, 0.0F, 14.0F, 6.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 6.0F, 7.0F, 2.7925F, 0.0F, 3.1416F));

        hay.addOrReplaceChild("hay1", CubeListBuilder.create().texOffs(16, 19).addBox(-7.0F, 0.0F, 0.0F, 14.0F, 6.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 6.0F, -7.0F, -0.3491F, 0.0F, 0.0F));

        hay.addOrReplaceChild("hay8", CubeListBuilder.create().texOffs(16, 19).mirror().addBox(-7.0F, 0.0F, 0.0F, 14.0F, 6.0F, 0.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offsetAndRotation(-7.0F, -6.0F, 0.0F, 0.0F, 1.5708F, 2.7925F));

        hay.addOrReplaceChild("hay7", CubeListBuilder.create().texOffs(16, 19).mirror().addBox(-7.0F, 0.0F, 0.0F, 14.0F, 6.0F, 0.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offsetAndRotation(7.0F, -6.0F, 0.0F, 0.0F, 1.5708F, -2.7925F));

        hay.addOrReplaceChild("hay6", CubeListBuilder.create().texOffs(16, 25).addBox(-7.0F, 0.0F, 0.0F, 14.0F, 6.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, -6.0F, -7.0F, -2.7925F, 0.0F, 0.0F));

        hay.addOrReplaceChild("hay5", CubeListBuilder.create().texOffs(16, 19).addBox(-7.0F, 0.0F, 0.0F, 14.0F, 6.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, -6.0F, 7.0F, 2.7925F, 0.0F, 0.0F));

        PartDefinition head = body.addOrReplaceChild("head", CubeListBuilder.create().texOffs(0, 0).addBox(-4.0F, -10.0F, -4.0F, 8.0F, 10.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, -6.0F, 0.0F));

        head.addOrReplaceChild("nose", CubeListBuilder.create().texOffs(24, 0).addBox(-1.0F, -1.0F, -6.0F, 2.0F, 4.0F, 2.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, -2.0F, 0.0F));

        head.addOrReplaceChild("eyebrow1", CubeListBuilder.create().texOffs(0, 0).addBox(0.0F, -2.0F, 0.0F, 3.0F, 2.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(-3.75F, -3.5F, -4.1F, 0.0F, 0.0F, 0.1309F));

        head.addOrReplaceChild("eyebrow2", CubeListBuilder.create().texOffs(0, 0).mirror().addBox(-3.0F, -2.0F, 0.0F, 3.0F, 2.0F, 0.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offsetAndRotation(3.75F, -3.5F, -4.1F, 0.0F, 0.0F, -0.1309F));

        PartDefinition birthday = head.addOrReplaceChild("birthday", CubeListBuilder.create().texOffs(82, 68).addBox(-2.0F, 2.0F, -1.0F, 4.0F, 3.0F, 4.0F, new CubeDeformation(0.0F))
                .texOffs(70, 68).addBox(-1.5F, -1.0F, -0.5F, 3.0F, 3.0F, 3.0F, new CubeDeformation(0.0F))
                .texOffs(98, 68).addBox(-1.5F, -4.0F, 1.0F, 3.0F, 3.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, -15.0F, 0.0F));

        birthday.addOrReplaceChild("thingy", CubeListBuilder.create().texOffs(98, 68).addBox(-0.5F, 2.0F, 0.0F, 3.0F, 3.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, -6.0F, 0.0F, 0.0F, -1.5708F, 0.0F));

        body.addOrReplaceChild("left_leg", CubeListBuilder.create().texOffs(0, 22).mirror().addBox(-2.0F, 0.0F, -2.0F, 4.0F, 12.0F, 4.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offset(2.0F, 6.0F, 0.0F));

        body.addOrReplaceChild("right_leg", CubeListBuilder.create().texOffs(0, 22).addBox(-2.0F, 0.0F, -2.0F, 4.0F, 12.0F, 4.0F, new CubeDeformation(0.0F)), PartPose.offset(-2.0F, 6.0F, 0.0F));

        return LayerDefinition.create(meshdefinition, 128, 128);
    }

    public void setupAnim(T entity, float limbSwing, float limbSwingAmount, float ageInTicks, float netHeadYaw, float headPitch) {
        this.body.getAllParts().forEach(ModelPart::resetPose);
        if (entity instanceof PreserverEntity preserver) {
            Calendar calendar = Calendar.getInstance();
            this.body.getChild("head").getChild("birthday").visible = calendar.get(Calendar.MONTH) == Calendar.FEBRUARY && calendar.get(Calendar.DAY_OF_MONTH) < 8;

            if (!preserver.isTryingToProtect()) {
                this.body.getChild("head").yRot = netHeadYaw * 0.017453292F;
                this.body.getChild("head").xRot = headPitch * 0.017453292F;
                this.body.y = -Math.abs(Mth.cos(limbSwing * 0.6662F) * 1.4F * limbSwingAmount * 0.5F) * 4.0F + 6.0F;
                this.body.xRot = -Math.abs(Mth.cos(limbSwing * 0.6662F) * 1.4F * limbSwingAmount * 0.5F) * 0.1F;
                this.body.getChild("left_leg").xRot = Mth.cos(limbSwing * 1.6F) * 1.4F * limbSwingAmount * 0.2F;
                this.body.getChild("right_leg").xRot = Mth.cos(limbSwing * 1.6F + 3.1415927F) * 1.4F * limbSwingAmount * 0.2F;
            } else {
                float multiplier = 0.1F * (float) Math.min(preserver.getJumpAnimationTick(), 10);
                this.body.yRot = netHeadYaw * 0.017453292F * multiplier;
                this.body.xRot = (headPitch * 0.017453292F + 1.5707F) * multiplier;
            }
        }

    }

    public void renderToBuffer(PoseStack poseStack, VertexConsumer vertexConsumer, int packedLight, int packedOverlay, float red, float green, float blue, float alpha) {
        this.body.render(poseStack, vertexConsumer, packedLight, packedOverlay, red, green, blue, alpha);
    }

    public ModelPart getHead() {
        return this.body.getChild("head");
    }
}
