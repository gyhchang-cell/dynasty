package com.yellowbrossproductions.illageandspillage.client.model;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.Entity;

public class AxeModel<T extends Entity> extends EntityModel<T> {
    public static final ModelLayerLocation LAYER_LOCATION = new ModelLayerLocation(new ResourceLocation("illageandspillage", "axe"), "main");
    private final ModelPart axe;

    public AxeModel(ModelPart root) {
        this.axe = root.getChild("axe");
    }

    public static LayerDefinition createBodyLayer() {
        MeshDefinition meshdefinition = new MeshDefinition();
        PartDefinition partdefinition = meshdefinition.getRoot();

        partdefinition.addOrReplaceChild("axe", CubeListBuilder.create().texOffs(18, 22).addBox(2.8787F, -0.5F, -4.8787F, 2.0F, 1.0F, 2.0F, new CubeDeformation(0.0F))
                .texOffs(18, 25).addBox(0.8787F, -0.5F, -2.8787F, 2.0F, 1.0F, 2.0F, new CubeDeformation(0.0F))
                .texOffs(18, 19).addBox(-1.1213F, -0.5F, -0.8787F, 2.0F, 1.0F, 2.0F, new CubeDeformation(0.0F))
                .texOffs(18, 28).addBox(-3.1213F, -0.5F, 1.1213F, 2.0F, 1.0F, 2.0F, new CubeDeformation(0.0F))
                .texOffs(0, 14).addBox(-5.1213F, -0.5F, 3.1213F, 4.0F, 1.0F, 5.0F, new CubeDeformation(0.0F))
                .texOffs(0, 23).addBox(-5.1213F, -0.5F, 1.1213F, 1.0F, 1.0F, 2.0F, new CubeDeformation(0.0F))
                .texOffs(24, 15).addBox(-7.1213F, -0.5F, 2.1213F, 1.0F, 1.0F, 2.0F, new CubeDeformation(0.0F))
                .texOffs(4, 25).addBox(-6.1213F, -0.5F, 1.1213F, 1.0F, 1.0F, 5.0F, new CubeDeformation(0.0F))
                .texOffs(6, 20).addBox(-4.1213F, -0.5F, 8.1213F, 2.0F, 1.0F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(18, 14).addBox(-1.1213F, -0.5F, 3.1213F, 1.0F, 1.0F, 4.0F, new CubeDeformation(0.0F))
                .texOffs(0, 20).addBox(-0.1213F, -0.5F, 4.1213F, 1.0F, 1.0F, 2.0F, new CubeDeformation(0.0F))
                .texOffs(12, 20).addBox(-2.1213F, -0.5F, 0.1213F, 1.0F, 1.0F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(12, 20).addBox(-0.1213F, -0.5F, -1.8787F, 1.0F, 1.0F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(12, 20).addBox(1.8787F, -0.5F, -3.8787F, 1.0F, 1.0F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(12, 22).addBox(2.8787F, -0.5F, -2.8787F, 1.0F, 1.0F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(12, 22).addBox(0.8787F, -0.5F, -0.8787F, 1.0F, 1.0F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(12, 22).addBox(-1.1213F, -0.5F, 1.1213F, 1.0F, 1.0F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(12, 20).addBox(-4.1213F, -0.5F, 2.1213F, 1.0F, 1.0F, 1.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 24.0F, 0.0F, 3.1332F, 0.7476F, 1.5603F));

        return LayerDefinition.create(meshdefinition, 32, 32);
    }

    public void setupAnim(T entity, float limbSwing, float limbSwingAmount, float ageInTicks, float netHeadYaw, float headPitch) {
        this.axe.yRot = ageInTicks * 25.0F * -0.017453292F;
    }

    public void renderToBuffer(PoseStack poseStack, VertexConsumer vertexConsumer, int packedLight, int packedOverlay, float red, float green, float blue, float alpha) {
        this.axe.render(poseStack, vertexConsumer, packedLight, packedOverlay, red, green, blue, alpha);
    }
}