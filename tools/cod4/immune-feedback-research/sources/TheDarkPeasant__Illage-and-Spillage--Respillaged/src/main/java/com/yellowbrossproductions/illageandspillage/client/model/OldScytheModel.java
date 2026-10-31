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

public class OldScytheModel<T extends Entity> extends EntityModel<T> {
    public static final ModelLayerLocation LAYER_LOCATION = new ModelLayerLocation(new ResourceLocation("illageandspillage", "old_scythe"), "main");
    private final ModelPart scythe;

    public OldScytheModel(ModelPart root) {
        this.scythe = root.getChild("scythe");
    }

    public static LayerDefinition createBodyLayer() {
        MeshDefinition meshdefinition = new MeshDefinition();
        PartDefinition partdefinition = meshdefinition.getRoot();
        partdefinition.addOrReplaceChild("scythe", CubeListBuilder.create().texOffs(0, 0).addBox(0.0F, -12.0F, -12.0F, 0.0F, 24.0F, 24.0F, new CubeDeformation(0.0F)).texOffs(0, 0).addBox(-0.1F, -12.0F, -12.0F, 0.0F, 24.0F, 24.0F, new CubeDeformation(0.0F)).texOffs(0, 0).addBox(-0.2F, -12.0F, -12.0F, 0.0F, 24.0F, 24.0F, new CubeDeformation(0.0F)).texOffs(0, 0).addBox(-0.3F, -12.0F, -12.0F, 0.0F, 24.0F, 24.0F, new CubeDeformation(0.0F)).texOffs(0, 0).addBox(-0.4F, -12.0F, -12.0F, 0.0F, 24.0F, 24.0F, new CubeDeformation(0.0F)).texOffs(0, 0).addBox(-0.5F, -12.0F, -12.0F, 0.0F, 24.0F, 24.0F, new CubeDeformation(0.0F)).texOffs(0, 0).addBox(0.1F, -12.0F, -12.0F, 0.0F, 24.0F, 24.0F, new CubeDeformation(0.0F)).texOffs(0, 0).addBox(0.2F, -12.0F, -12.0F, 0.0F, 24.0F, 24.0F, new CubeDeformation(0.0F)).texOffs(0, 0).addBox(0.3F, -12.0F, -12.0F, 0.0F, 24.0F, 24.0F, new CubeDeformation(0.0F)).texOffs(0, 0).addBox(0.4F, -12.0F, -12.0F, 0.0F, 24.0F, 24.0F, new CubeDeformation(0.0F)).texOffs(0, 0).addBox(0.5F, -12.0F, -12.0F, 0.0F, 24.0F, 24.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 21.0F, 0.0F, 0.0F, 0.0F, -1.5708F));
        return LayerDefinition.create(meshdefinition, 48, 48);
    }

    public void setupAnim(T entity, float limbSwing, float limbSwingAmount, float ageInTicks, float netHeadYaw, float headPitch) {
        this.scythe.xRot = ageInTicks * 45.0F * 0.017453292F;
    }

    public void renderToBuffer(PoseStack poseStack, VertexConsumer vertexConsumer, int packedLight, int packedOverlay, float red, float green, float blue, float alpha) {
        this.scythe.render(poseStack, vertexConsumer, packedLight, packedOverlay, red, green, blue, alpha);
    }
}
