package com.yellowbrossproductions.illageandspillage.client.model;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;

public class MobSpiritModel<T extends Entity> extends EntityModel<T> {
    public static final ModelLayerLocation LAYER_LOCATION = new ModelLayerLocation(new ResourceLocation("illageandspillage", "mob_spirit"), "main");
    private final ModelPart soul;

    public MobSpiritModel(ModelPart root) {
        this.soul = root.getChild("soul");
    }

    public static LayerDefinition createBodyLayer() {
        MeshDefinition meshdefinition = new MeshDefinition();
        PartDefinition partdefinition = meshdefinition.getRoot();
        PartDefinition soul = partdefinition.addOrReplaceChild("soul", CubeListBuilder.create().texOffs(0, 0).addBox(-4.0F, -4.0F, -4.0F, 8.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 16.0F, 0.0F));
        soul.addOrReplaceChild("ring1", CubeListBuilder.create().texOffs(0, 24).addBox(-16.0F, -2.0F, -2.0F, 4.0F, 4.0F, 4.0F, new CubeDeformation(0.0F)).texOffs(0, 24).addBox(12.0F, -2.0F, -2.0F, 4.0F, 4.0F, 4.0F, new CubeDeformation(0.0F)).texOffs(16, 24).addBox(-2.0F, -2.0F, -16.0F, 4.0F, 4.0F, 4.0F, new CubeDeformation(0.0F)).texOffs(16, 24).addBox(-2.0F, -2.0F, 12.0F, 4.0F, 4.0F, 4.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 0.0F, 0.0F));
        soul.addOrReplaceChild("ring2", CubeListBuilder.create().texOffs(0, 24).addBox(-16.0F, -2.0F, -2.0F, 4.0F, 4.0F, 4.0F, new CubeDeformation(0.0F)).texOffs(0, 24).addBox(12.0F, -2.0F, -2.0F, 4.0F, 4.0F, 4.0F, new CubeDeformation(0.0F)).texOffs(16, 24).addBox(-2.0F, -2.0F, -16.0F, 4.0F, 4.0F, 4.0F, new CubeDeformation(0.0F)).texOffs(16, 24).addBox(-2.0F, -2.0F, 12.0F, 4.0F, 4.0F, 4.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 0.0F, 0.0F, 0.0F, -0.7854F, -1.5708F));
        return LayerDefinition.create(meshdefinition, 32, 32);
    }

    public void setupAnim(T entity, float limbSwing, float limbSwingAmount, float ageInTicks, float netHeadYaw, float headPitch) {
        float f3 = ageInTicks / 60.0F;
        this.soul.xRot = ageInTicks * 10.0F * 0.017453292F;
        this.soul.yRot = ageInTicks * 10.0F * 0.017453292F;
        this.soul.zRot = ageInTicks * 10.0F * 0.017453292F;
        this.soul.getChild("ring1").yRot = ageInTicks * 15.0F * 0.017453292F;
        this.soul.getChild("ring2").yRot = -0.7854F + ageInTicks * 15.0F * 0.017453292F;
        this.soul.y = 16.0F + Mth.sin(f3 * 7.0F) * 0.2F;
    }

    public void renderToBuffer(PoseStack poseStack, VertexConsumer vertexConsumer, int packedLight, int packedOverlay, float red, float green, float blue, float alpha) {
        this.soul.render(poseStack, vertexConsumer, packedLight, packedOverlay, red, green, blue, alpha);
    }
}
