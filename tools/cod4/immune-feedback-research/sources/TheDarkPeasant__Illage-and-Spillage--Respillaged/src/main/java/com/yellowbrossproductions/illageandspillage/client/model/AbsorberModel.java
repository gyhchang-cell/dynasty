package com.yellowbrossproductions.illageandspillage.client.model;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.yellowbrossproductions.illageandspillage.client.model.animation.AbsorberAnimation;
import com.yellowbrossproductions.illageandspillage.entities.AbsorberEntity;
import net.minecraft.client.model.HierarchicalModel;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;

import java.util.Calendar;
import java.util.Random;

public class AbsorberModel<T extends Entity> extends HierarchicalModel<T> implements CustomHeadedModel {
    public static final ModelLayerLocation LAYER_LOCATION = new ModelLayerLocation(new ResourceLocation("illageandspillage", "absorber"), "main");
    private final ModelPart root;
    private final ModelPart waist;
    private final ModelPart leg2;
    private final ModelPart leg1;
    private final Random random = new Random();

    public AbsorberModel(ModelPart root) {
        this.root = root;
        this.waist = root.getChild("waist");
        this.leg2 = root.getChild("leg2");
        this.leg1 = root.getChild("leg1");
    }

    public static LayerDefinition createBodyLayer() {
        MeshDefinition meshdefinition = new MeshDefinition();
        PartDefinition partdefinition = meshdefinition.getRoot();

        PartDefinition waist = partdefinition.addOrReplaceChild("waist", CubeListBuilder.create().texOffs(48, 0).addBox(-8.0F, -12.0F, -6.0F, 16.0F, 12.0F, 12.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 8.0F, 0.0F, -0.1745F, 0.0F, 0.0F));

        PartDefinition chest = waist.addOrReplaceChild("chest", CubeListBuilder.create().texOffs(28, 24).addBox(-11.0F, -16.0F, -8.0F, 22.0F, 16.0F, 16.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, -9.0F, 0.0F, 0.3491F, 0.0F, 0.0F));

        PartDefinition arm1 = chest.addOrReplaceChild("arm1", CubeListBuilder.create().texOffs(0, 18).addBox(-3.0F, -3.0F, -3.0F, 6.0F, 18.0F, 6.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(-14.0F, -11.0F, 0.0F, -0.8727F, 0.1745F, 0.0873F));

        PartDefinition glove1 = arm1.addOrReplaceChild("glove1", CubeListBuilder.create().texOffs(0, 42).addBox(-3.0F, -2.0F, -3.0F, 6.0F, 16.0F, 6.0F, new CubeDeformation(0.25F)), PartPose.offsetAndRotation(0.0F, 15.0F, 0.0F, -2.0944F, 0.1745F, 0.0873F));

        PartDefinition fist1 = glove1.addOrReplaceChild("fist1", CubeListBuilder.create().texOffs(72, 56).addBox(-4.0F, -4.0F, -4.0F, 8.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 12.0F, 0.0F));

        fist1.addOrReplaceChild("hammer", CubeListBuilder.create().texOffs(0, 94).addBox(-1.0F, -28.0F, -1.0F, 2.0F, 32.0F, 2.0F, new CubeDeformation(0.0F))
                .texOffs(8, 116).addBox(-3.0F, 4.0F, -3.0F, 6.0F, 6.0F, 6.0F, new CubeDeformation(0.0F))
                .texOffs(32, 102).addBox(-5.0F, -38.0F, -8.0F, 10.0F, 10.0F, 16.0F, new CubeDeformation(0.0F))
                .texOffs(8, 98).addBox(-7.0F, -40.0F, -12.0F, 14.0F, 14.0F, 4.0F, new CubeDeformation(0.0F))
                .texOffs(8, 98).addBox(-7.0F, -40.0F, 8.0F, 14.0F, 14.0F, 4.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 0.0F, 0.0F, 1.5708F, 0.0F, 0.0F));

        PartDefinition arm2 = chest.addOrReplaceChild("arm2", CubeListBuilder.create().texOffs(0, 18).mirror().addBox(-3.0F, -3.0F, -3.0F, 6.0F, 18.0F, 6.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offsetAndRotation(14.0F, -11.0F, 0.0F, -0.0873F, 0.0F, -0.0873F));

        PartDefinition glove2 = arm2.addOrReplaceChild("glove2", CubeListBuilder.create().texOffs(0, 42).mirror().addBox(-3.0F, -2.0F, -3.0F, 6.0F, 16.0F, 6.0F, new CubeDeformation(0.25F)).mirror(false), PartPose.offsetAndRotation(0.0F, 15.0F, 0.0F, -0.2618F, 0.0F, 0.3491F));

        glove2.addOrReplaceChild("fist2", CubeListBuilder.create().texOffs(72, 56).mirror().addBox(-4.0F, -4.0F, -4.0F, 8.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offsetAndRotation(0.0F, 12.0F, 0.0F, -0.1745F, 0.0F, 0.0F));

        PartDefinition head = chest.addOrReplaceChild("head", CubeListBuilder.create().texOffs(0, 0).addBox(-4.0F, -10.0F, -4.0F, 8.0F, 10.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, -14.0F, -6.0F, -0.1745F, 0.0F, 0.0F));

        head.addOrReplaceChild("nose", CubeListBuilder.create().texOffs(24, 0).addBox(-1.0F, -1.0F, -1.0F, 2.0F, 4.0F, 2.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, -2.0F, -5.0F));

        head.addOrReplaceChild("eyebrow1", CubeListBuilder.create().texOffs(0, 0).addBox(-3.0F, -2.0F, 0.0F, 3.0F, 2.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(-1.0F, -3.5F, -4.1F, 0.0F, 0.0F, 0.0873F));

        head.addOrReplaceChild("eyebrow2", CubeListBuilder.create().texOffs(0, 0).mirror().addBox(0.0F, -2.0F, 0.0F, 3.0F, 2.0F, 0.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offsetAndRotation(1.0F, -3.5F, -4.1F, 0.0F, 0.0F, -0.0873F));

        PartDefinition birthday = head.addOrReplaceChild("birthday", CubeListBuilder.create().texOffs(12, 64).addBox(-2.0F, -9.3333F, 6.0833F, 4.0F, 3.0F, 4.0F, new CubeDeformation(0.0F))
                .texOffs(0, 64).addBox(-1.5F, -12.3333F, 6.5833F, 3.0F, 3.0F, 3.0F, new CubeDeformation(0.0F))
                .texOffs(25, 61).addBox(0.0F, -15.3333F, 6.5833F, 0.0F, 3.0F, 3.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, -3.6667F, -8.0833F));

        birthday.addOrReplaceChild("thingy", CubeListBuilder.create().texOffs(25, 64).addBox(-1.5F, -15.3333F, 8.0F, 3.0F, 3.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 0.0F, 0.0F));

        PartDefinition leg2 = partdefinition.addOrReplaceChild("leg2", CubeListBuilder.create().texOffs(104, 0).mirror().addBox(-3.0F, 0.0F, -3.0F, 6.0F, 20.0F, 6.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offset(4.0F, 4.0F, 0.0F));

        leg2.addOrReplaceChild("boot2", CubeListBuilder.create().texOffs(104, 26).mirror().addBox(-3.0F, 0.0F, -3.0F, 6.0F, 12.0F, 6.0F, new CubeDeformation(0.25F)).mirror(false), PartPose.offset(0.0F, 8.0F, 0.0F));

        PartDefinition leg1 = partdefinition.addOrReplaceChild("leg1", CubeListBuilder.create().texOffs(104, 0).addBox(-3.0F, 0.0F, -3.0F, 6.0F, 20.0F, 6.0F, new CubeDeformation(0.0F)), PartPose.offset(-4.0F, 4.0F, 0.0F));

        leg1.addOrReplaceChild("boot1", CubeListBuilder.create().texOffs(104, 26).addBox(-3.0F, 0.0F, -3.0F, 6.0F, 12.0F, 6.0F, new CubeDeformation(0.25F)), PartPose.offset(0.0F, 8.0F, 0.0F));

        return LayerDefinition.create(meshdefinition, 128, 128);
    }

    public void setupAnim(T entity, float limbSwing, float limbSwingAmount, float ageInTicks, float netHeadYaw, float headPitch) {
        this.root().getAllParts().forEach(ModelPart::resetPose);
        ModelPart head = this.waist.getChild("chest").getChild("head");
        ModelPart chest = this.waist.getChild("chest");

        Calendar calendar = Calendar.getInstance();
        head.getChild("birthday").visible = calendar.get(Calendar.MONTH) == Calendar.FEBRUARY && calendar.get(Calendar.DAY_OF_MONTH) < 8;

        this.leg1.xRot = -1.5F * Mth.triangleWave(limbSwing, 13.0F) * limbSwingAmount;
        this.leg2.xRot = 1.5F * Mth.triangleWave(limbSwing, 13.0F) * limbSwingAmount;
        if (entity instanceof AbsorberEntity absorber) {
            this.animate(absorber.getAnimationState("attack"), AbsorberAnimation.ATTACK, ageInTicks, absorber.getAnimationSpeed());
            this.animate(absorber.getAnimationState("death"), AbsorberAnimation.DEATH, ageInTicks, absorber.getAnimationSpeed());
            if (absorber.deathTime >= 30 && absorber.deathTime < 44) {
                chest.x += (-0.5F + this.random.nextFloat()) * 0.8F;
                chest.y += (-0.5F + this.random.nextFloat()) * 0.8F;
                chest.z += (-0.5F + this.random.nextFloat()) * 0.8F;
            }
        }

        head.yRot += netHeadYaw * 0.017453292F;
        head.xRot += headPitch * 0.017453292F;
    }

    public void renderToBuffer(PoseStack poseStack, VertexConsumer vertexConsumer, int packedLight, int packedOverlay, float red, float green, float blue, float alpha) {
        this.waist.render(poseStack, vertexConsumer, packedLight, packedOverlay, red, green, blue, alpha);
        this.leg2.render(poseStack, vertexConsumer, packedLight, packedOverlay, red, green, blue, alpha);
        this.leg1.render(poseStack, vertexConsumer, packedLight, packedOverlay, red, green, blue, alpha);
    }

    public ModelPart root() {
        return this.root;
    }

    @Override
    public void translateToHead(PoseStack stack) {
        this.root().translateAndRotate(stack);
        this.waist.translateAndRotate(stack);
        this.leg2.translateAndRotate(stack);
        this.leg1.translateAndRotate(stack);
        this.waist.getChild("chest").getChild("head").translateAndRotate(stack);
    }
}
