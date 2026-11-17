package com.yellowbrossproductions.illageandspillage.client.model;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.yellowbrossproductions.illageandspillage.entities.CrashagerEntity;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;

public class CrashagerModel<T extends Entity> extends EntityModel<T> {
    public static final ModelLayerLocation LAYER_LOCATION = new ModelLayerLocation(new ResourceLocation("illageandspillage", "crashager"), "main");
    private final ModelPart body;

    public CrashagerModel(ModelPart root) {
        this.body = root.getChild("body");
    }

    public static LayerDefinition createBodyLayer() {
        MeshDefinition meshdefinition = new MeshDefinition();
        PartDefinition partdefinition = meshdefinition.getRoot();
        PartDefinition body = partdefinition.addOrReplaceChild("body", CubeListBuilder.create(), PartPose.offset(0.0F, 1.0F, 3.5F));
        body.addOrReplaceChild("rotation", CubeListBuilder.create().texOffs(0, 55).addBox(-7.0F, -10.0F, -7.0F, 14.0F, 16.0F, 20.0F, new CubeDeformation(0.0F)).texOffs(0, 91).addBox(-6.0F, 6.0F, -7.0F, 12.0F, 13.0F, 18.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 0.0F, 0.0F, 1.5708F, 0.0F, 0.0F));
        PartDefinition neck = body.addOrReplaceChild("neck", CubeListBuilder.create().texOffs(68, 73).addBox(-5.0F, -1.0F, -18.0F, 10.0F, 10.0F, 18.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, -7.0F, 4.5F));
        PartDefinition head = neck.addOrReplaceChild("head", CubeListBuilder.create().texOffs(0, 0).addBox(-8.0F, -20.0F, -14.0F, 16.0F, 20.0F, 16.0F, new CubeDeformation(0.0F)).texOffs(0, 0).addBox(-2.0F, -6.0F, -18.0F, 4.0F, 8.0F, 4.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 16.0F, -18.0F));
        PartDefinition horns = head.addOrReplaceChild("horns", CubeListBuilder.create().texOffs(74, 55).addBox(-5.0F, -14.0F, -1.0F, 2.0F, 14.0F, 4.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(-5.0F, -13.0F, -9.0F, 1.0472F, 0.0F, 0.0F));
        horns.addOrReplaceChild("left_horn", CubeListBuilder.create().texOffs(74, 55).mirror().addBox(8.0F, -41.0F, -20.0F, 2.0F, 14.0F, 4.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offset(5.0F, 27.0F, 19.0F));
        head.addOrReplaceChild("jaw", CubeListBuilder.create().texOffs(0, 36).addBox(-8.0F, 0.0F, -16.0F, 16.0F, 3.0F, 16.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, -2.0F, 2.0F));
        body.addOrReplaceChild("leg1", CubeListBuilder.create().texOffs(96, 0).addBox(-20.0F, 0.0F, -4.0F, 8.0F, 37.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offset(8.0F, -14.0F, 17.5F));
        body.addOrReplaceChild("leg2", CubeListBuilder.create().texOffs(96, 0).mirror().addBox(12.0F, 0.0F, -4.0F, 8.0F, 37.0F, 8.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offset(-8.0F, -14.0F, 17.5F));
        body.addOrReplaceChild("leg3", CubeListBuilder.create().texOffs(64, 0).addBox(-20.0F, 0.0F, -4.0F, 8.0F, 37.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offset(8.0F, -14.0F, -7.0F));
        body.addOrReplaceChild("leg4", CubeListBuilder.create().texOffs(64, 0).mirror().addBox(12.0F, 0.0F, -4.0F, 8.0F, 37.0F, 8.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offset(-8.0F, -14.0F, -7.0F));
        return LayerDefinition.create(meshdefinition, 128, 128);
    }

    public void setupAnim(T entity, float limbSwing, float limbSwingAmount, float ageInTicks, float netHeadYaw, float headPitch) {
        if (entity instanceof CrashagerEntity) {
            if (((CrashagerEntity) entity).getAttackStage() == 1) {
                this.resetAngles(limbSwing, limbSwingAmount, netHeadYaw, headPitch);
                this.body.xRot = 0.2618F;
                this.body.getChild("neck").getChild("head").xRot = headPitch * 0.017453292F - 0.2618F;
                this.body.getChild("leg1").y = -8.0F;
                this.body.getChild("leg2").y = -8.0F;
                this.body.getChild("leg1").xRot = 0.0F;
                this.body.getChild("leg2").xRot = 0.0F;
                this.body.getChild("leg3").xRot = -0.4363F;
                this.body.getChild("leg4").xRot = -0.4363F;
            }

            if (((CrashagerEntity) entity).getAttackStage() == 2) {
                this.resetAngles(limbSwing, limbSwingAmount, netHeadYaw, headPitch);
                this.body.xRot = 0.2618F;
                this.body.z = -2.5F;
                this.body.getChild("neck").z = -5.5F;
                this.body.getChild("neck").xRot = -0.3491F;
                this.body.getChild("neck").getChild("head").xRot = -0.6981F;
                this.body.getChild("neck").getChild("head").getChild("jaw").xRot = 0.8727F;
                this.body.getChild("leg1").y = -8.0F;
                this.body.getChild("leg2").y = -8.0F;
                this.body.getChild("leg1").xRot = 0.0873F;
                this.body.getChild("leg2").xRot = 0.0873F;
                this.body.getChild("leg3").xRot = -0.1745F;
                this.body.getChild("leg4").xRot = -0.1745F;
            } else {
                this.resetAngles(limbSwing, limbSwingAmount, netHeadYaw, headPitch);
            }
        }

    }

    public void resetAngles(float limbSwing, float limbSwingAmount, float netHeadYaw, float headPitch) {
        this.body.getChild("neck").getChild("head").yRot = netHeadYaw * 0.017453292F;
        this.body.getChild("neck").getChild("head").xRot = headPitch * 0.017453292F;
        this.body.xRot = 0.0F;
        this.body.getChild("leg1").y = -14.0F;
        this.body.getChild("leg2").y = -14.0F;
        this.body.getChild("leg1").xRot = Mth.cos(limbSwing * 0.6662F) * 1.4F * limbSwingAmount * 0.5F;
        this.body.getChild("leg2").xRot = Mth.cos(limbSwing * 0.6662F + 3.1415927F) * 1.4F * limbSwingAmount * 0.5F;
        this.body.getChild("leg3").xRot = Mth.cos(limbSwing * 0.6662F + 3.1415927F) * 1.4F * limbSwingAmount * 0.5F;
        this.body.getChild("leg4").xRot = Mth.cos(limbSwing * 0.6662F) * 1.4F * limbSwingAmount * 0.5F;
        this.body.getChild("neck").z = 4.5F;
        this.body.z = 3.5F;
        this.body.getChild("neck").xRot = 0.0F;
        this.body.getChild("neck").getChild("head").getChild("jaw").xRot = 0.0F;
    }

    public void renderToBuffer(PoseStack poseStack, VertexConsumer buffer, int packedLight, int packedOverlay, float red, float green, float blue, float alpha) {
        this.body.render(poseStack, buffer, packedLight, packedOverlay);
    }
}
