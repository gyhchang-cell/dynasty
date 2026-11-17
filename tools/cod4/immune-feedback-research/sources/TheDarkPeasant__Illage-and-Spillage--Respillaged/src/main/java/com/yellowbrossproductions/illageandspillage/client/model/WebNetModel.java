package com.yellowbrossproductions.illageandspillage.client.model;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.yellowbrossproductions.illageandspillage.entities.projectile.WebNetEntity;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.Entity;

public class WebNetModel<T extends Entity> extends EntityModel<T> {
    public static final ModelLayerLocation LAYER_LOCATION = new ModelLayerLocation(new ResourceLocation("illageandspillage", "web_net"), "main");
    private final ModelPart all;
    private final ModelPart web3;
    private final ModelPart web1;
    private final ModelPart web2;
    private final ModelPart web4;

    public WebNetModel(ModelPart root) {
        this.all = root.getChild("all");
        this.web3 = all.getChild("web3");
        this.web1 = all.getChild("web1");
        this.web2 = all.getChild("web2");
        this.web4 = all.getChild("web4");
    }

    public static LayerDefinition createBodyLayer() {
        MeshDefinition meshdefinition = new MeshDefinition();
        PartDefinition partdefinition = meshdefinition.getRoot();

        PartDefinition all = partdefinition.addOrReplaceChild("all", CubeListBuilder.create(), PartPose.offset(0.0F, 24.0F, 1.0F));

        PartDefinition web3 = all.addOrReplaceChild("web3", CubeListBuilder.create(), PartPose.offset(0.0F, -14.0F, 0.0F));

        web3.addOrReplaceChild("cube_r1", CubeListBuilder.create().texOffs(0, 28).addBox(-14.0F, -14.0F, -1.0F, 14.0F, 14.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 0.0F, 0.0F, 0.3491F, -0.2618F, 0.0F));

        PartDefinition web1 = all.addOrReplaceChild("web1", CubeListBuilder.create(), PartPose.offset(0.0F, -14.0F, 0.0F));

        web1.addOrReplaceChild("cube_r2", CubeListBuilder.create().texOffs(0, 14).addBox(-14.0F, 0.0F, -1.0F, 14.0F, 14.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 0.0F, 0.0F, -0.3491F, -0.2618F, 0.0F));

        PartDefinition web2 = all.addOrReplaceChild("web2", CubeListBuilder.create(), PartPose.offset(0.0F, -14.0F, 0.0F));

        web2.addOrReplaceChild("cube_r3", CubeListBuilder.create().texOffs(0, 0).addBox(0.0F, 0.0F, -1.0F, 14.0F, 14.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 0.0F, 0.0F, -0.3491F, 0.2618F, 0.0F));

        PartDefinition web4 = all.addOrReplaceChild("web4", CubeListBuilder.create(), PartPose.offset(0.0F, -14.0F, 0.0F));

        web4.addOrReplaceChild("cube_r4", CubeListBuilder.create().texOffs(28, 0).addBox(0.0F, -14.0F, -1.0F, 14.0F, 14.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 0.0F, 0.0F, 0.3491F, 0.2618F, 0.0F));

        return LayerDefinition.create(meshdefinition, 64, 64);
    }

    @Override
    public void setupAnim(Entity entity, float limbSwing, float limbSwingAmount, float ageInTicks, float netHeadYaw, float headPitch) {
        if (entity instanceof WebNetEntity webNet && webNet.isCaught()) {
            float rotationAmount = (float) Math.toRadians(35);

            this.web1.xRot = -rotationAmount;
            this.web1.yRot = -rotationAmount;
            this.web2.xRot = -rotationAmount;
            this.web2.yRot = rotationAmount;
            this.web3.xRot = rotationAmount;
            this.web3.yRot = -rotationAmount;
            this.web4.xRot = rotationAmount;
            this.web4.yRot = rotationAmount;
        } else {
            this.web1.xRot = 0;
            this.web1.yRot = 0;
            this.web2.xRot = 0;
            this.web2.yRot = 0;
            this.web3.xRot = 0;
            this.web3.yRot = 0;
            this.web4.xRot = 0;
            this.web4.yRot = 0;
        }
    }

    @Override
    public void renderToBuffer(PoseStack poseStack, VertexConsumer vertexConsumer, int packedLight, int packedOverlay, float red, float green, float blue, float alpha) {
        this.all.render(poseStack, vertexConsumer, packedLight, packedOverlay, red, green, blue, alpha);
    }
}