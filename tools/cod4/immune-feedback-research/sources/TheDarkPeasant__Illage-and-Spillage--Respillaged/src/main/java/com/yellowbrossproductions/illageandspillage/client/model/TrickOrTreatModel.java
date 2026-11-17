package com.yellowbrossproductions.illageandspillage.client.model;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.yellowbrossproductions.illageandspillage.entities.TrickOrTreatEntity;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.Entity;

public class TrickOrTreatModel<T extends Entity> extends EntityModel<T> {
    public static final ModelLayerLocation LAYER_LOCATION = new ModelLayerLocation(new ResourceLocation("illageandspillage", "trickortreat"), "main");
    private final ModelPart treat1;
    private final ModelPart treat2;
    private final ModelPart treat3;
    private final ModelPart treat4;
    private final ModelPart treat5;
    private final ModelPart treat6;

    public TrickOrTreatModel(ModelPart root) {
        this.treat1 = root.getChild("treat1");
        this.treat2 = root.getChild("treat2");
        this.treat3 = root.getChild("treat3");
        this.treat4 = root.getChild("treat4");
        this.treat5 = root.getChild("treat5");
        this.treat6 = root.getChild("treat6");
    }

    public static LayerDefinition createBodyLayer() {
        MeshDefinition meshdefinition = new MeshDefinition();
        PartDefinition partdefinition = meshdefinition.getRoot();

        partdefinition.addOrReplaceChild("treat1", CubeListBuilder.create().texOffs(0, 0).addBox(-1.0F, -7.0F, -1.0F, 2.0F, 24.0F, 2.0F, new CubeDeformation(0.0F))
                .texOffs(8, 0).addBox(-5.0F, -17.0F, -5.0F, 10.0F, 10.0F, 10.0F, new CubeDeformation(0.0F))
                .texOffs(48, 0).addBox(-5.5F, -14.0F, -5.5F, 11.0F, 4.0F, 11.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 7.0F, 0.0F));

        partdefinition.addOrReplaceChild("treat2", CubeListBuilder.create().texOffs(0, 26).addBox(-5.0F, -11.0F, -3.0F, 10.0F, 24.0F, 6.0F, new CubeDeformation(0.0F))
                .texOffs(0, 56).addBox(-8.0F, -15.0F, 0.0F, 16.0F, 32.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 7.0F, 0.0F));

        partdefinition.addOrReplaceChild("treat3", CubeListBuilder.create().texOffs(32, 20).addBox(-7.0F, -7.0F, -3.0F, 14.0F, 14.0F, 6.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 7.0F, 0.0F));

        partdefinition.addOrReplaceChild("treat4", CubeListBuilder.create().texOffs(0, 0).addBox(-1.0F, -7.0F, -1.0F, 2.0F, 24.0F, 2.0F, new CubeDeformation(0.0F))
                .texOffs(32, 40).addBox(-8.0F, -23.0F, -2.0F, 16.0F, 16.0F, 4.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 7.0F, 0.0F));

        partdefinition.addOrReplaceChild("treat5", CubeListBuilder.create().texOffs(32, 60).mirror().addBox(-5.0F, 7.0F, -1.0F, 4.0F, 10.0F, 2.0F, new CubeDeformation(0.0F)).mirror(false)
                .texOffs(32, 60).addBox(1.0F, 7.0F, -1.0F, 4.0F, 10.0F, 2.0F, new CubeDeformation(0.0F))
                .texOffs(44, 60).addBox(-5.0F, -5.0F, -1.0F, 10.0F, 12.0F, 2.0F, new CubeDeformation(0.0F))
                .texOffs(32, 74).mirror().addBox(-11.0F, -5.0F, -1.0F, 6.0F, 4.0F, 2.0F, new CubeDeformation(0.0F)).mirror(false)
                .texOffs(32, 74).addBox(5.0F, -5.0F, -1.0F, 6.0F, 4.0F, 2.0F, new CubeDeformation(0.0F))
                .texOffs(32, 80).addBox(-6.0F, -17.0F, -2.0F, 12.0F, 12.0F, 4.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 7.0F, 0.0F));

        partdefinition.addOrReplaceChild("treat6", CubeListBuilder.create().texOffs(85, 8).addBox(0.0F, -7.0F, -8.0F, 12.0F, 7.0F, 7.0F, new CubeDeformation(0.0F))
                .texOffs(86, 28).addBox(1.0F, -17.0F, -8.0F, 10.0F, 10.0F, 7.0F, new CubeDeformation(0.0F))
                .texOffs(88, 46).addBox(2.0F, -23.0F, -8.0F, 8.0F, 6.0F, 7.0F, new CubeDeformation(0.0F)), PartPose.offset(-6.0F, 24.0F, 4.5F));

        return LayerDefinition.create(meshdefinition, 128, 128);
    }

    @Override
    public void setupAnim(Entity entity, float limbSwing, float limbSwingAmount, float ageInTicks, float netHeadYaw, float headPitch) {
        this.treat1.resetPose();
        this.treat2.resetPose();
        this.treat3.resetPose();
        this.treat4.resetPose();
        this.treat5.resetPose();
        this.treat6.resetPose();
        if (entity instanceof TrickOrTreatEntity treat) {
            this.treat1.visible = treat.getTreat() == 1;
            this.treat2.visible = treat.getTreat() == 2;
            this.treat3.visible = treat.getTreat() == 3;
            this.treat4.visible = treat.getTreat() == 4;
            this.treat5.visible = treat.getTreat() == 5;
            this.treat6.visible = treat.getTreat() == 6;
            if (treat.getBounce()) {
                this.treat1.yRot = netHeadYaw * 0.017453292F;
                this.treat1.xRot = 1.5707F + headPitch * 0.017453292F;
                this.treat2.yRot = netHeadYaw * 0.017453292F;
                this.treat2.xRot = 1.5707F + headPitch * 0.017453292F;
                this.treat3.yRot = netHeadYaw * 0.017453292F;
                this.treat3.xRot = 1.5707F + headPitch * 0.017453292F;
                this.treat4.yRot = netHeadYaw * 0.017453292F;
                this.treat4.xRot = 1.5707F + headPitch * 0.017453292F;
                this.treat5.yRot = netHeadYaw * 0.017453292F;
                this.treat5.xRot = 1.5707F + headPitch * 0.017453292F;
                this.treat6.yRot = netHeadYaw * 0.017453292F;
                this.treat6.xRot = 1.5707F + headPitch * 0.017453292F;
            }
        }
    }

    @Override
    public void renderToBuffer(PoseStack poseStack, VertexConsumer vertexConsumer, int packedLight, int packedOverlay, float red, float green, float blue, float alpha) {
        treat1.render(poseStack, vertexConsumer, packedLight, packedOverlay, red, green, blue, alpha);
        treat2.render(poseStack, vertexConsumer, packedLight, packedOverlay, red, green, blue, alpha);
        treat3.render(poseStack, vertexConsumer, packedLight, packedOverlay, red, green, blue, alpha);
        treat4.render(poseStack, vertexConsumer, packedLight, packedOverlay, red, green, blue, alpha);
        treat5.render(poseStack, vertexConsumer, packedLight, packedOverlay, red, green, blue, alpha);
        treat6.render(poseStack, vertexConsumer, packedLight, packedOverlay, red, green, blue, alpha);
    }
}