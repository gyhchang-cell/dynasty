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

public class ScytheModel<T extends Entity> extends EntityModel<T> {
    public static final ModelLayerLocation LAYER_LOCATION = new ModelLayerLocation(new ResourceLocation("illageandspillage", "scythe"), "main");
    private final ModelPart scythe;

    public ScytheModel(ModelPart root) {
        this.scythe = root.getChild("scythe");
    }

    public static LayerDefinition createBodyLayer() {
        MeshDefinition meshdefinition = new MeshDefinition();
        PartDefinition partdefinition = meshdefinition.getRoot();

        partdefinition.addOrReplaceChild("scythe", CubeListBuilder.create().texOffs(0, 13).addBox(-4.0F, -0.5F, -1.0F, 6.0F, 1.0F, 2.0F, new CubeDeformation(0.0F))
                .texOffs(10, 21).addBox(7.0F, -0.5F, -12.0F, 1.0F, 1.0F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(10, 23).addBox(6.0F, -0.5F, -11.0F, 3.0F, 1.0F, 2.0F, new CubeDeformation(0.0F))
                .texOffs(0, 16).addBox(4.0F, -0.5F, -9.0F, 3.0F, 1.0F, 4.0F, new CubeDeformation(0.0F))
                .texOffs(20, 23).addBox(2.0F, -0.5F, -5.0F, 3.0F, 1.0F, 2.0F, new CubeDeformation(0.0F))
                .texOffs(16, 13).addBox(0.0F, -0.5F, -3.0F, 4.0F, 1.0F, 2.0F, new CubeDeformation(0.0F))
                .texOffs(14, 16).addBox(-4.0F, -0.5F, 1.0F, 4.0F, 1.0F, 2.0F, new CubeDeformation(0.0F))
                .texOffs(0, 2).addBox(-6.0F, -0.5F, 3.0F, 3.0F, 1.0F, 6.0F, new CubeDeformation(0.0F))
                .texOffs(14, 19).addBox(-8.0F, -0.5F, 4.0F, 2.0F, 1.0F, 3.0F, new CubeDeformation(0.0F))
                .texOffs(20, 7).addBox(-10.0F, -0.5F, 3.0F, 2.0F, 1.0F, 3.0F, new CubeDeformation(0.0F))
                .texOffs(0, 25).addBox(-11.0F, -0.5F, 4.0F, 1.0F, 1.0F, 3.0F, new CubeDeformation(0.0F))
                .texOffs(0, 9).addBox(-4.0F, -0.5F, 9.0F, 7.0F, 1.0F, 3.0F, new CubeDeformation(0.0F))
                .texOffs(24, 19).addBox(3.0F, -0.5F, 9.0F, 3.0F, 1.0F, 2.0F, new CubeDeformation(0.0F))
                .texOffs(0, 0).addBox(-3.0F, -0.5F, 8.0F, 12.0F, 1.0F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(20, 11).addBox(6.0F, -0.5F, 7.0F, 4.0F, 1.0F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(26, 0).addBox(8.0F, -0.5F, 6.0F, 3.0F, 1.0F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(0, 21).addBox(-9.0F, -0.5F, 9.0F, 2.0F, 1.0F, 3.0F, new CubeDeformation(0.0F))
                .texOffs(18, 2).addBox(-7.0F, -0.5F, 7.0F, 1.0F, 1.0F, 4.0F, new CubeDeformation(0.0F))
                .texOffs(28, 26).addBox(-6.0F, -0.5F, 9.0F, 1.0F, 1.0F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(28, 26).addBox(0.0F, -0.5F, 1.0F, 1.0F, 1.0F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(28, 26).addBox(2.0F, -0.5F, -1.0F, 1.0F, 1.0F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(28, 26).addBox(5.0F, -0.5F, -5.0F, 1.0F, 1.0F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(28, 2).addBox(-3.0F, -0.5F, 7.0F, 1.0F, 1.0F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(28, 4).addBox(10.0F, -0.5F, 5.0F, 1.0F, 1.0F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(10, 21).addBox(-8.0F, -0.5F, 8.0F, 1.0F, 1.0F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(10, 21).addBox(1.0F, -0.5F, -4.0F, 1.0F, 1.0F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(24, 26).addBox(5.0F, -0.5F, -10.0F, 1.0F, 1.0F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(10, 21).addBox(3.0F, -0.5F, -6.0F, 1.0F, 1.0F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(28, 28).addBox(-3.0F, -0.5F, 3.0F, 1.0F, 1.0F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(28, 28).addBox(-5.0F, -0.5F, 2.0F, 1.0F, 1.0F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(8, 26).addBox(-6.0F, -0.5F, 0.0F, 1.0F, 1.0F, 3.0F, new CubeDeformation(0.0F))
                .texOffs(0, 29).addBox(-3.0F, -0.5F, -2.0F, 1.0F, 1.0F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(4, 29).addBox(-4.0F, -0.5F, -3.0F, 1.0F, 1.0F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(16, 27).addBox(7.0F, -0.5F, -9.0F, 1.0F, 1.0F, 2.0F, new CubeDeformation(0.0F))
                .texOffs(0, 5).addBox(6.0F, -0.5F, 9.0F, 2.0F, 1.0F, 1.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 24.0F, 0.0F));

        return LayerDefinition.create(meshdefinition, 36, 36);
    }

    public void setupAnim(T entity, float limbSwing, float limbSwingAmount, float ageInTicks, float netHeadYaw, float headPitch) {
        this.scythe.yRot = ageInTicks * 45.0F * 0.017453292F;
    }

    public void renderToBuffer(PoseStack poseStack, VertexConsumer vertexConsumer, int packedLight, int packedOverlay, float red, float green, float blue, float alpha) {
        this.scythe.render(poseStack, vertexConsumer, packedLight, packedOverlay, red, green, blue, alpha);
    }
}
