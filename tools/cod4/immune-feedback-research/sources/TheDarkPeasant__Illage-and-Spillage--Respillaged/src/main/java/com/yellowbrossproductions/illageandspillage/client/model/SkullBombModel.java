package com.yellowbrossproductions.illageandspillage.client.model;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.yellowbrossproductions.illageandspillage.entities.projectile.SkullBombEntity;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;

public class SkullBombModel<T extends Entity> extends EntityModel<T> {
    public static final ModelLayerLocation LAYER_LOCATION = new ModelLayerLocation(new ResourceLocation("illageandspillage", "skull_bomb"), "main");
    private final ModelPart skull;
    private final ModelPart smallerskull;

    public SkullBombModel(ModelPart root) {
        this.skull = root.getChild("skull");
        this.smallerskull = root.getChild("smallerskull");
    }

    public static LayerDefinition createBodyLayer() {
        MeshDefinition meshdefinition = new MeshDefinition();
        PartDefinition partdefinition = meshdefinition.getRoot();
        PartDefinition skull = partdefinition.addOrReplaceChild("skull", CubeListBuilder.create(), PartPose.offset(0.0F, 20.0F, 0.0F));
        PartDefinition skull_top = skull.addOrReplaceChild("skull_top", CubeListBuilder.create().texOffs(0, 0).addBox(-4.0F, -6.0F, -8.0F, 8.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 2.0F, 4.0F));
        skull_top.addOrReplaceChild("horn1", CubeListBuilder.create().texOffs(0, 0).addBox(-1.0F, -5.0F, -1.0F, 1.0F, 6.0F, 2.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(-4.0F, -5.0F, -4.0F, 0.7854F, 0.0F, 0.0F));
        skull_top.addOrReplaceChild("horn2", CubeListBuilder.create().texOffs(0, 0).addBox(0.0F, -5.0F, -1.0F, 1.0F, 6.0F, 2.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(4.0F, -5.0F, -4.0F, 0.7854F, 0.0F, 0.0F));
        skull.addOrReplaceChild("jaw", CubeListBuilder.create().texOffs(32, 0).addBox(-4.0F, -1.0F, -8.0F, 8.0F, 3.0F, 8.0F, new CubeDeformation(0.25F)), PartPose.offset(0.0F, 2.0F, 3.75F));
        PartDefinition smallerskull = partdefinition.addOrReplaceChild("smallerskull", CubeListBuilder.create(), PartPose.offset(0.0F, 22.0F, 0.0F));
        smallerskull.addOrReplaceChild("skull_top2", CubeListBuilder.create().texOffs(32, 11).addBox(-2.0F, -3.0F, -4.0F, 4.0F, 4.0F, 4.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 1.0F, 2.0F));
        smallerskull.addOrReplaceChild("jaw2", CubeListBuilder.create().texOffs(48, 11).addBox(-2.0F, 0.0F, -4.0F, 4.0F, 1.0F, 4.0F, new CubeDeformation(0.1F)), PartPose.offset(0.0F, 1.0F, 2.0F));
        return LayerDefinition.create(meshdefinition, 64, 24);
    }

    public void setupAnim(T entity, float limbSwing, float limbSwingAmount, float ageInTicks, float netHeadYaw, float headPitch) {
        if (entity instanceof SkullBombEntity skull) {
            this.skull.visible = !skull.isSmall();
            this.smallerskull.visible = skull.isSmall();
        }

        float f3 = ageInTicks / 60.0F;
        this.skull.xRot = ageInTicks * 10.0F * 0.017453292F;
        this.skull.yRot = ageInTicks * 8.0F * 0.017453292F;
        this.smallerskull.xRot = ageInTicks * 10.0F * 0.017453292F;
        this.smallerskull.yRot = ageInTicks * 8.0F * 0.017453292F;
        this.skull.getChild("skull_top").xRot = -Math.abs(0.55F * Mth.sin(f3 * 100.0F));
        this.skull.getChild("jaw").xRot = this.skull.getChild("skull_top").xRot * -1.0F;
        this.smallerskull.getChild("skull_top2").xRot = -Math.abs(0.55F * Mth.sin(f3 * 100.0F));
        this.smallerskull.getChild("jaw2").xRot = this.smallerskull.getChild("skull_top2").xRot * -1.0F;
    }

    public void renderToBuffer(PoseStack poseStack, VertexConsumer vertexConsumer, int packedLight, int packedOverlay, float red, float green, float blue, float alpha) {
        this.skull.render(poseStack, vertexConsumer, packedLight, packedOverlay, red, green, blue, alpha);
        this.smallerskull.render(poseStack, vertexConsumer, packedLight, packedOverlay, red, green, blue, alpha);
    }
}
