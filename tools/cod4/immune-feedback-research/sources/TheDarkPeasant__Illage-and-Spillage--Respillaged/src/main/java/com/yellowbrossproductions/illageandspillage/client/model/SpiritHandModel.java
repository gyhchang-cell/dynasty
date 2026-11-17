package com.yellowbrossproductions.illageandspillage.client.model;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.yellowbrossproductions.illageandspillage.entities.SpiritHandEntity;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.Entity;

public class SpiritHandModel<T extends Entity> extends EntityModel<T> {
    public static final ModelLayerLocation LAYER_LOCATION = new ModelLayerLocation(new ResourceLocation("illageandspillage", "spirit_hand"), "main");
    private final ModelPart hand1;
    private final ModelPart hand2;

    public SpiritHandModel(ModelPart root) {
        this.hand1 = root.getChild("hand1");
        this.hand2 = root.getChild("hand2");
    }

    public static LayerDefinition createBodyLayer() {
        MeshDefinition meshdefinition = new MeshDefinition();
        PartDefinition partdefinition = meshdefinition.getRoot();
        PartDefinition hand1 = partdefinition.addOrReplaceChild("hand1", CubeListBuilder.create().texOffs(0, 16).addBox(-11.0F, -12.0F, -4.0F, 22.0F, 24.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 12.0F, 0.0F, 0.0F, 0.0F, -3.1416F));
        PartDefinition finger1 = hand1.addOrReplaceChild("finger1", CubeListBuilder.create().texOffs(0, 0).addBox(-3.0F, 0.0F, -4.0F, 6.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(-9.0F, 12.0F, 0.0F, 0.0F, 0.0F, 0.0873F));
        PartDefinition fingersmaller1 = finger1.addOrReplaceChild("fingersmaller1", CubeListBuilder.create().texOffs(0, 0).addBox(-3.0F, 0.0F, -4.0F, 6.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 8.0F, 0.0F, -0.4363F, 0.0F, 0.0F));
        fingersmaller1.addOrReplaceChild("fingersmallest1", CubeListBuilder.create().texOffs(0, 0).addBox(-3.0F, 0.0F, -4.0F, 6.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 8.0F, 0.0F, -0.4363F, 0.0F, 0.0F));
        PartDefinition finger2 = hand1.addOrReplaceChild("finger2", CubeListBuilder.create().texOffs(0, 0).addBox(-3.0F, 0.0F, -4.0F, 6.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offset(-3.0F, 12.0F, 0.0F));
        PartDefinition fingersmaller2 = finger2.addOrReplaceChild("fingersmaller2", CubeListBuilder.create().texOffs(0, 0).addBox(-3.0F, 0.0F, -4.0F, 6.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 8.0F, 0.0F, -0.2618F, 0.0F, 0.0F));
        fingersmaller2.addOrReplaceChild("fingersmallest2", CubeListBuilder.create().texOffs(0, 0).addBox(-3.0F, 0.0F, -4.0F, 6.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 8.0F, 0.0F, -0.2618F, 0.0F, 0.0F));
        PartDefinition finger3 = hand1.addOrReplaceChild("finger3", CubeListBuilder.create().texOffs(0, 0).addBox(-3.0F, 0.0F, -4.0F, 6.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(3.0F, 12.0F, 0.0F, 0.0F, 0.0F, -0.0873F));
        PartDefinition fingersmaller3 = finger3.addOrReplaceChild("fingersmaller3", CubeListBuilder.create().texOffs(0, 0).addBox(-3.0F, 0.0F, -4.0F, 6.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 8.0F, 0.0F, -0.4363F, 0.0F, 0.0F));
        fingersmaller3.addOrReplaceChild("fingersmallest3", CubeListBuilder.create().texOffs(0, 0).addBox(-3.0F, 0.0F, -4.0F, 6.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 8.0F, 0.0F, -0.6109F, 0.0F, 0.0F));
        PartDefinition finger4 = hand1.addOrReplaceChild("finger4", CubeListBuilder.create().texOffs(0, 0).addBox(-3.0F, 0.0F, -4.0F, 6.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(9.0F, 12.0F, 0.0F, 0.0F, 0.0F, -0.2618F));
        PartDefinition fingersmaller4 = finger4.addOrReplaceChild("fingersmaller4", CubeListBuilder.create().texOffs(0, 0).addBox(-3.0F, 0.0F, -4.0F, 6.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 8.0F, 0.0F, -0.4363F, 0.0F, 0.0F));
        fingersmaller4.addOrReplaceChild("fingersmallest4", CubeListBuilder.create().texOffs(0, 0).addBox(-3.0F, 0.0F, -4.0F, 6.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 8.0F, 0.0F, -0.7854F, 0.0F, 0.0F));
        PartDefinition finger5 = hand1.addOrReplaceChild("finger5", CubeListBuilder.create().texOffs(0, 0).addBox(-3.0F, 0.0F, -4.0F, 6.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(-11.0F, 1.0F, -4.0F, 0.0F, 0.0F, 0.6981F));
        PartDefinition fingersmaller5 = finger5.addOrReplaceChild("fingersmaller5", CubeListBuilder.create().texOffs(0, 0).addBox(-3.0F, 0.0F, -4.0F, 6.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 8.0F, 0.0F, -0.7854F, 0.0F, 0.0F));
        fingersmaller5.addOrReplaceChild("fingersmallest5", CubeListBuilder.create().texOffs(0, 0).addBox(-3.0F, 0.0F, -4.0F, 6.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 8.0F, 0.0F, -0.7854F, 0.0F, 0.0F));
        PartDefinition hand2 = partdefinition.addOrReplaceChild("hand2", CubeListBuilder.create().texOffs(0, 48).addBox(-11.0F, -3.0F, -4.0F, 22.0F, 24.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 21.0F, 0.0F, 0.0F, 0.0F, -3.1416F));
        PartDefinition finger6 = hand2.addOrReplaceChild("finger6", CubeListBuilder.create().texOffs(28, 0).addBox(-3.0F, 0.0F, -4.0F, 6.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(-9.0F, 21.0F, 0.0F, 0.0F, 0.0F, 0.2618F));
        PartDefinition fingersmaller6 = finger6.addOrReplaceChild("fingersmaller6", CubeListBuilder.create().texOffs(28, 0).addBox(-3.0F, 0.0F, -4.0F, 6.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 8.0F, 0.0F, -0.2618F, 0.0F, 0.0F));
        fingersmaller6.addOrReplaceChild("fingersmallest6", CubeListBuilder.create().texOffs(28, 0).addBox(-3.0F, 0.0F, -4.0F, 6.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 8.0F, 0.0F, -0.2618F, 0.0F, 0.0F));
        PartDefinition finger7 = hand2.addOrReplaceChild("finger7", CubeListBuilder.create().texOffs(28, 0).addBox(-3.0F, 0.0F, -4.0F, 6.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(11.0F, 10.0F, -4.0F, 0.0F, 0.0F, -0.6981F));
        PartDefinition fingersmaller7 = finger7.addOrReplaceChild("fingersmaller7", CubeListBuilder.create().texOffs(28, 0).addBox(-3.0F, 0.0F, -4.0F, 6.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 8.0F, 0.0F, -0.7854F, 0.0F, 0.0F));
        fingersmaller7.addOrReplaceChild("fingersmallest7", CubeListBuilder.create().texOffs(28, 0).addBox(-3.0F, 0.0F, -4.0F, 6.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 8.0F, 0.0F, -0.7854F, 0.0F, 0.0F));
        PartDefinition finger8 = hand2.addOrReplaceChild("finger8", CubeListBuilder.create().texOffs(28, 0).addBox(-3.0F, 0.0F, -4.0F, 6.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(-3.0F, 21.0F, 0.0F, 0.1745F, 0.0F, 0.0873F));
        PartDefinition fingersmaller8 = finger8.addOrReplaceChild("fingersmaller8", CubeListBuilder.create().texOffs(28, 0).addBox(-3.0F, 0.0F, -4.0F, 6.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 8.0F, 0.0F, -0.4363F, 0.0F, 0.0F));
        fingersmaller8.addOrReplaceChild("fingersmallest8", CubeListBuilder.create().texOffs(28, 0).addBox(-3.0F, 0.0F, -4.0F, 6.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 8.0F, 0.0F, -0.4363F, 0.0F, 0.0F));
        PartDefinition finger9 = hand2.addOrReplaceChild("finger9", CubeListBuilder.create().texOffs(28, 0).addBox(-3.0F, 0.0F, -4.0F, 6.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offset(3.0F, 21.0F, 0.0F));
        PartDefinition fingersmaller9 = finger9.addOrReplaceChild("fingersmaller9", CubeListBuilder.create().texOffs(28, 0).addBox(-3.0F, 0.0F, -4.0F, 6.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 8.0F, 0.0F, -0.2618F, 0.0F, 0.0F));
        fingersmaller9.addOrReplaceChild("fingersmallest9", CubeListBuilder.create().texOffs(28, 0).addBox(-3.0F, 0.0F, -4.0F, 6.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 8.0F, 0.0F, -0.2618F, 0.0F, 0.0F));
        PartDefinition finger10 = hand2.addOrReplaceChild("finger10", CubeListBuilder.create().texOffs(28, 0).addBox(-3.0F, 0.0F, -4.0F, 6.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(9.0F, 21.0F, 0.0F, 0.0F, 0.0F, -0.0873F));
        PartDefinition fingersmaller10 = finger10.addOrReplaceChild("fingersmaller10", CubeListBuilder.create().texOffs(28, 0).addBox(-3.0F, 0.0F, -4.0F, 6.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 8.0F, 0.0F, -0.2618F, 0.0F, 0.0F));
        fingersmaller10.addOrReplaceChild("fingersmallest10", CubeListBuilder.create().texOffs(28, 0).addBox(-3.0F, 0.0F, -4.0F, 6.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 8.0F, 0.0F, -0.4363F, 0.0F, 0.0F));
        return LayerDefinition.create(meshdefinition, 64, 96);
    }

    public void setupAnim(T entity, float limbSwing, float limbSwingAmount, float ageInTicks, float netHeadYaw, float headPitch) {
        if (entity instanceof SpiritHandEntity hand) {
            this.hand1.xRot = headPitch * 0.017453292F * -1.0F;
            this.hand2.xRot = headPitch * 0.017453292F * -1.0F;
            if (((SpiritHandEntity) entity).getAttackType() == 1) {
                this.hand2.xRot = 1.5708F;
                this.hand2.zRot = -3.1416F;
                this.hand2.z = -9.0F;
                this.hand1.zRot = 1.5708F;
                this.hand1.xRot = -1.5708F;
                this.hand1.getChild("finger1").xRot = -1.5708F;
                this.hand1.getChild("finger1").zRot = 0.0F;
                this.hand1.getChild("finger2").xRot = -1.5708F;
                this.hand1.getChild("finger2").zRot = 0.0F;
                this.hand1.getChild("finger3").xRot = -1.5708F;
                this.hand1.getChild("finger3").zRot = 0.0F;
                this.hand1.getChild("finger4").xRot = -1.5708F;
                this.hand1.getChild("finger4").zRot = 0.0F;
                this.hand1.getChild("finger5").xRot = -1.5708F;
                this.hand1.getChild("finger5").zRot = 1.5708F;
                this.hand1.getChild("finger1").getChild("fingersmaller1").xRot = -1.5708F;
                this.hand1.getChild("finger2").getChild("fingersmaller2").xRot = -1.5708F;
                this.hand1.getChild("finger3").getChild("fingersmaller3").xRot = -1.5708F;
                this.hand1.getChild("finger4").getChild("fingersmaller4").xRot = -1.5708F;
                this.hand1.getChild("finger5").getChild("fingersmaller5").xRot = -1.5708F;
                this.hand1.getChild("finger1").getChild("fingersmaller1").getChild("fingersmallest1").xRot = 0.0F;
                this.hand1.getChild("finger2").getChild("fingersmaller2").getChild("fingersmallest2").xRot = 0.0F;
                this.hand1.getChild("finger3").getChild("fingersmaller3").getChild("fingersmallest3").xRot = 0.0F;
                this.hand1.getChild("finger4").getChild("fingersmaller4").getChild("fingersmallest4").xRot = 0.0F;
                this.hand1.getChild("finger5").getChild("fingersmaller5").getChild("fingersmallest5").xRot = 0.0F;
            } else if (((SpiritHandEntity) entity).getAttackType() == 2) {
                this.hand2.xRot = -1.5708F + headPitch * 0.017453292F * -1.0F;
                this.hand2.zRot = -3.1416F;
                this.hand2.z = -4.0F;
                this.hand1.zRot = -3.1416F;
                this.hand1.xRot = -1.5708F + headPitch * 0.017453292F * -1.0F;
                this.hand1.getChild("finger1").xRot = -1.5708F;
                this.hand1.getChild("finger1").zRot = 0.0F;
                this.hand1.getChild("finger2").xRot = -1.5708F;
                this.hand1.getChild("finger2").zRot = 0.0F;
                this.hand1.getChild("finger3").xRot = -1.5708F;
                this.hand1.getChild("finger3").zRot = 0.0F;
                this.hand1.getChild("finger4").xRot = -1.5708F;
                this.hand1.getChild("finger4").zRot = 0.0F;
                this.hand1.getChild("finger5").xRot = -1.5708F;
                this.hand1.getChild("finger5").zRot = 1.5708F;
                this.hand1.getChild("finger1").getChild("fingersmaller1").xRot = -1.5708F;
                this.hand1.getChild("finger2").getChild("fingersmaller2").xRot = -1.5708F;
                this.hand1.getChild("finger3").getChild("fingersmaller3").xRot = -1.5708F;
                this.hand1.getChild("finger4").getChild("fingersmaller4").xRot = -1.5708F;
                this.hand1.getChild("finger5").getChild("fingersmaller5").xRot = -1.5708F;
                this.hand1.getChild("finger1").getChild("fingersmaller1").getChild("fingersmallest1").xRot = 0.0F;
                this.hand1.getChild("finger2").getChild("fingersmaller2").getChild("fingersmallest2").xRot = 0.0F;
                this.hand1.getChild("finger3").getChild("fingersmaller3").getChild("fingersmallest3").xRot = 0.0F;
                this.hand1.getChild("finger4").getChild("fingersmaller4").getChild("fingersmallest4").xRot = 0.0F;
                this.hand1.getChild("finger5").getChild("fingersmaller5").getChild("fingersmallest5").xRot = 0.0F;
            } else {
                this.hand2.xRot = headPitch * 0.017453292F * -1.0F;
                this.hand2.zRot = -3.1416F;
                this.hand2.z = -4.0F;
                this.hand1.xRot = headPitch * 0.017453292F * -1.0F;
                this.hand1.zRot = -3.1416F;
                this.hand1.getChild("finger1").xRot = 0.0F;
                this.hand1.getChild("finger1").zRot = 0.0873F;
                this.hand1.getChild("finger2").xRot = 0.0F;
                this.hand1.getChild("finger2").zRot = 0.0F;
                this.hand1.getChild("finger3").xRot = 0.0F;
                this.hand1.getChild("finger3").zRot = -0.0873F;
                this.hand1.getChild("finger4").xRot = 0.0F;
                this.hand1.getChild("finger4").zRot = -0.2618F;
                this.hand1.getChild("finger5").xRot = 0.0F;
                this.hand1.getChild("finger5").zRot = 0.6981F;
                this.hand1.getChild("finger1").getChild("fingersmaller1").xRot = -0.4363F;
                this.hand1.getChild("finger2").getChild("fingersmaller2").xRot = -0.2618F;
                this.hand1.getChild("finger3").getChild("fingersmaller3").xRot = -0.4363F;
                this.hand1.getChild("finger4").getChild("fingersmaller4").xRot = -0.4363F;
                this.hand1.getChild("finger5").getChild("fingersmaller5").xRot = -0.7854F;
                this.hand1.getChild("finger1").getChild("fingersmaller1").getChild("fingersmallest1").xRot = -0.4363F;
                this.hand1.getChild("finger2").getChild("fingersmaller2").getChild("fingersmallest2").xRot = -0.2618F;
                this.hand1.getChild("finger3").getChild("fingersmaller3").getChild("fingersmallest3").xRot = -0.6109F;
                this.hand1.getChild("finger4").getChild("fingersmaller4").getChild("fingersmallest4").xRot = -0.7854F;
                this.hand1.getChild("finger5").getChild("fingersmaller5").getChild("fingersmallest5").xRot = -0.7854F;
            }

            this.hand1.visible = !hand.isGoodOrEvil();
            this.hand2.visible = hand.isGoodOrEvil();
        }

    }

    public void renderToBuffer(PoseStack poseStack, VertexConsumer vertexConsumer, int packedLight, int packedOverlay, float red, float green, float blue, float alpha) {
        this.hand1.render(poseStack, vertexConsumer, packedLight, packedOverlay, red, green, blue, alpha);
        this.hand2.render(poseStack, vertexConsumer, packedLight, packedOverlay, red, green, blue, alpha);
    }
}
