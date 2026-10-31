package com.yellowbrossproductions.illageandspillage.client.model;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.yellowbrossproductions.illageandspillage.entities.DispenserEntity;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.Entity;

public class DispenserModel<T extends Entity> extends EntityModel<T> {
    public static final ModelLayerLocation LAYER_LOCATION = new ModelLayerLocation(new ResourceLocation("illageandspillage", "dispenser"), "main");
    private final ModelPart chest;

    public DispenserModel(ModelPart root) {
        this.chest = root.getChild("chest");
    }

    public static LayerDefinition createBodyLayer() {
        MeshDefinition meshdefinition = new MeshDefinition();
        PartDefinition partdefinition = meshdefinition.getRoot();
        PartDefinition chest = partdefinition.addOrReplaceChild("chest", CubeListBuilder.create().texOffs(0, 0).addBox(-7.0F, 1.0F, -7.0F, 14.0F, 2.0F, 14.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 21.0F, 0.0F));
        chest.addOrReplaceChild("chest_lid", CubeListBuilder.create().texOffs(0, 16).addBox(-7.0F, -4.0F, -14.0F, 14.0F, 4.0F, 14.0F, new CubeDeformation(0.0F)).texOffs(0, 16).addBox(-1.0F, -3.0F, -15.0F, 2.0F, 4.0F, 1.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 1.0F, 7.0F, -2.1817F, 0.0F, 0.0F));
        chest.addOrReplaceChild("machine", CubeListBuilder.create().texOffs(0, 34).addBox(-1.0F, -1.0F, -6.0F, 2.0F, 1.0F, 12.0F, new CubeDeformation(0.0F)).texOffs(16, 34).addBox(-6.0F, -1.0F, -1.0F, 12.0F, 1.0F, 2.0F, new CubeDeformation(0.0F)).texOffs(0, 47).addBox(-3.0F, -2.0F, -3.0F, 6.0F, 2.0F, 6.0F, new CubeDeformation(0.0F)).texOffs(56, 50).addBox(-1.0F, -14.0F, -1.0F, 2.0F, 12.0F, 2.0F, new CubeDeformation(0.0F)).texOffs(32, 52).addBox(-3.0F, -20.0F, -3.0F, 6.0F, 6.0F, 6.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 2.0F, 0.0F));
        return LayerDefinition.create(meshdefinition, 64, 64);
    }

    public void setupAnim(T entity, float limbSwing, float limbSwingAmount, float ageInTicks, float netHeadYaw, float headPitch) {
        if (entity instanceof DispenserEntity dispenser) {
            if (dispenser.isInMotion()) {
                this.chest.xRot = ageInTicks * 25.0F * 0.017453292F;
                this.chest.yRot = ageInTicks * 15.0F * 0.017453292F;
                this.chest.zRot = ageInTicks * 20.0F * 0.017453292F;
                this.chest.getChild("chest_lid").xRot = 0.0F;
                this.chest.getChild("machine").visible = false;
            } else {
                this.chest.xRot = 0.0F;
                this.chest.yRot = 0.0F;
                this.chest.zRot = 0.0F;
                this.chest.getChild("chest_lid").xRot = -2.1817F;
                this.chest.getChild("machine").visible = true;
            }
        }

    }

    public void renderToBuffer(PoseStack poseStack, VertexConsumer buffer, int packedLight, int packedOverlay, float red, float green, float blue, float alpha) {
        this.chest.render(poseStack, buffer, packedLight, packedOverlay);
    }
}
