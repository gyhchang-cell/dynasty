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

public class HayArmorModel<T extends Entity> extends EntityModel<T> {
    public static final ModelLayerLocation LAYER_LOCATION = new ModelLayerLocation(new ResourceLocation("illageandspillage", "hay_armor"), "main");
    private final ModelPart body;

    public HayArmorModel(ModelPart root) {
        this.body = root.getChild("body");
    }

    public static LayerDefinition createBodyLayer() {
        MeshDefinition meshdefinition = new MeshDefinition();
        PartDefinition partdefinition = meshdefinition.getRoot();
        PartDefinition body = partdefinition.addOrReplaceChild("body", CubeListBuilder.create(), PartPose.offset(0.0F, 6.0F, 0.0F));
        PartDefinition hay = body.addOrReplaceChild("hay", CubeListBuilder.create().texOffs(32, 0).addBox(-7.0F, -6.0F, -7.0F, 14.0F, 5.0F, 14.0F, new CubeDeformation(0.0F)).texOffs(0, 58).addBox(-7.5F, -8.0F, -7.5F, 15.0F, 3.0F, 15.0F, new CubeDeformation(0.0F)).texOffs(0, 58).addBox(-7.5F, 5.0F, -7.5F, 15.0F, 3.0F, 15.0F, new CubeDeformation(0.0F)).texOffs(0, 38).addBox(-7.0F, 6.0F, -7.0F, 14.0F, 6.0F, 14.0F, new CubeDeformation(0.0F)).texOffs(56, 38).addBox(-7.0F, -12.0F, -7.0F, 14.0F, 6.0F, 14.0F, new CubeDeformation(0.0F)).texOffs(32, 0).addBox(-7.0F, 1.0F, -7.0F, 14.0F, 5.0F, 14.0F, new CubeDeformation(0.0F)).texOffs(44, 19).addBox(-6.5F, -1.0F, -6.5F, 13.0F, 2.0F, 13.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 0.0F, 0.0F));
        hay.addOrReplaceChild("hay4", CubeListBuilder.create().texOffs(16, 19).mirror().addBox(-7.0F, 0.0F, 0.0F, 14.0F, 6.0F, 0.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offsetAndRotation(-7.0F, 6.0F, 0.0F, 0.0F, -1.5708F, 0.3491F));
        hay.addOrReplaceChild("hay3", CubeListBuilder.create().texOffs(16, 19).mirror().addBox(-7.0F, 0.0F, 0.0F, 14.0F, 6.0F, 0.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offsetAndRotation(7.0F, 6.0F, 0.0F, 0.0F, -1.5708F, -0.3491F));
        hay.addOrReplaceChild("hay2", CubeListBuilder.create().texOffs(16, 19).addBox(-7.0F, 0.0F, 0.0F, 14.0F, 6.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 6.0F, 7.0F, 2.7925F, 0.0F, 3.1416F));
        hay.addOrReplaceChild("hay1", CubeListBuilder.create().texOffs(16, 19).addBox(-7.0F, 0.0F, 0.0F, 14.0F, 6.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 6.0F, -7.0F, -0.3491F, 0.0F, 0.0F));
        hay.addOrReplaceChild("hay8", CubeListBuilder.create().texOffs(16, 19).mirror().addBox(-7.0F, 0.0F, 0.0F, 14.0F, 6.0F, 0.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offsetAndRotation(-7.0F, -6.0F, 0.0F, 0.0F, 1.5708F, 2.7925F));
        hay.addOrReplaceChild("hay7", CubeListBuilder.create().texOffs(16, 19).mirror().addBox(-7.0F, 0.0F, 0.0F, 14.0F, 6.0F, 0.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offsetAndRotation(7.0F, -6.0F, 0.0F, 0.0F, 1.5708F, -2.7925F));
        hay.addOrReplaceChild("hay6", CubeListBuilder.create().texOffs(16, 25).addBox(-7.0F, 0.0F, 0.0F, 14.0F, 6.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, -6.0F, -7.0F, -2.7925F, 0.0F, 0.0F));
        hay.addOrReplaceChild("hay5", CubeListBuilder.create().texOffs(16, 19).addBox(-7.0F, 0.0F, 0.0F, 14.0F, 6.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, -6.0F, 7.0F, 2.7925F, 0.0F, 0.0F));
        return LayerDefinition.create(meshdefinition, 128, 128);
    }

    public void setupAnim(T entity, float limbSwing, float limbSwingAmount, float ageInTicks, float netHeadYaw, float headPitch) {
    }

    public void renderToBuffer(PoseStack poseStack, VertexConsumer vertexConsumer, int packedLight, int packedOverlay, float red, float green, float blue, float alpha) {
        this.body.render(poseStack, vertexConsumer, packedLight, packedOverlay, red, green, blue, alpha);
    }
}
