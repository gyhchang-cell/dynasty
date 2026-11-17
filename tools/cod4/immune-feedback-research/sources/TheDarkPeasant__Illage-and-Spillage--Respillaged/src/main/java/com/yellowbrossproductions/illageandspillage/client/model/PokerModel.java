package com.yellowbrossproductions.illageandspillage.client.model;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.model.ArmedModel;
import net.minecraft.client.model.HierarchicalModel;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.HumanoidArm;

import java.util.Calendar;

public class PokerModel<T extends Entity> extends HierarchicalModel<T> implements ArmedModel {
    public static final ModelLayerLocation LAYER_LOCATION = new ModelLayerLocation(new ResourceLocation("illageandspillage", "poker"), "main");
    private final ModelPart root;
    private final ModelPart all;
    private final ModelPart body;
    private final ModelPart head;
    private final ModelPart arm2;
    private final ModelPart arm1;
    private final ModelPart leg2;
    private final ModelPart leg1;

    public PokerModel(ModelPart root) {
        this.root = root;
        this.all = this.root.getChild("all");
        this.body = all.getChild("body");
        this.head = body.getChild("head");
        this.arm2 = body.getChild("arm2");
        this.arm1 = body.getChild("arm1");
        this.leg2 = all.getChild("leg2");
        this.leg1 = all.getChild("leg1");
    }

    public static LayerDefinition createBodyLayer() {
        MeshDefinition meshdefinition = new MeshDefinition();
        PartDefinition partdefinition = meshdefinition.getRoot();

        PartDefinition all = partdefinition.addOrReplaceChild("all", CubeListBuilder.create(), PartPose.offset(0.0F, 24.0F, 0.0F));

        PartDefinition body = all.addOrReplaceChild("body", CubeListBuilder.create().texOffs(14, 12).addBox(-2.0F, -5.0F, -1.0F, 4.0F, 5.0F, 2.0F, new CubeDeformation(0.0F)), PartPose.offset(-0.5F, -6.0F, 0.0F));

        PartDefinition head = body.addOrReplaceChild("head", CubeListBuilder.create().texOffs(0, 0).addBox(-2.5F, -7.0F, -2.5F, 5.0F, 7.0F, 5.0F, new CubeDeformation(0.0F))
                .texOffs(24, 8).addBox(-1.0F, -3.0F, -4.0F, 2.0F, 4.0F, 2.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, -5.0F, 0.0F));

        head.addOrReplaceChild("cube_r1", CubeListBuilder.create().texOffs(0, 5).addBox(0.0F, -7.3F, -9.7F, 0.0F, 7.0F, 7.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, -8.5F, 7.0F, 0.7854F, 0.0F, 0.0F));

        PartDefinition birthday = head.addOrReplaceChild("birthday", CubeListBuilder.create().texOffs(12, 32).addBox(-1.5F, -9.3333F, 6.0833F, 4.0F, 3.0F, 4.0F, new CubeDeformation(0.0F))
                .texOffs(0, 32).addBox(-1.0F, -12.3333F, 6.5833F, 3.0F, 3.0F, 3.0F, new CubeDeformation(0.0F))
                .texOffs(25, 29).addBox(0.5F, -15.3333F, 6.5833F, 0.0F, 3.0F, 3.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(-0.5F, -0.6667F, -8.0833F, -0.0873F, 0.0F, 0.0F));

        birthday.addOrReplaceChild("thingy", CubeListBuilder.create().texOffs(25, 32).addBox(-1.0F, -15.3333F, 8.0F, 3.0F, 3.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 0.0F, 0.0F));

        body.addOrReplaceChild("arm2", CubeListBuilder.create().texOffs(20, 0).addBox(-1.0F, -1.0F, -1.0F, 2.0F, 6.0F, 2.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(3.0F, -4.0F, 0.0F, -0.01F, 0.0082F, 0.0182F));

        body.addOrReplaceChild("arm1", CubeListBuilder.create().texOffs(8, 19).addBox(-1.0F, -1.0F, -1.0F, 2.0F, 6.0F, 2.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(-3.0F, -4.0F, 0.0F, 0.0143F, 0.0271F, 0.0074F));

        all.addOrReplaceChild("leg2", CubeListBuilder.create().texOffs(0, 19).addBox(-1.0F, 0.0F, -1.0F, 2.0F, 6.0F, 2.0F, new CubeDeformation(0.0F)), PartPose.offset(0.5F, -6.0F, 0.0F));

        all.addOrReplaceChild("leg1", CubeListBuilder.create().texOffs(0, 19).mirror().addBox(-1.0F, 0.0F, -1.0F, 2.0F, 6.0F, 2.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offset(-1.5F, -6.0F, 0.0F));

        return LayerDefinition.create(meshdefinition, 32, 40);
    }

    @Override
    public void setupAnim(Entity entity, float limbSwing, float limbSwingAmount, float ageInTicks, float netHeadYaw, float headPitch) {
        Calendar calendar = Calendar.getInstance();
        this.head.getChild("birthday").visible = calendar.get(Calendar.MONTH) == Calendar.FEBRUARY && calendar.get(Calendar.DAY_OF_MONTH) < 8;

        this.head.yRot = netHeadYaw * 0.017453292F;
        this.head.xRot = headPitch * 0.017453292F;
        this.leg1.xRot = Mth.cos(limbSwing * 0.6662F) * 1.4F * limbSwingAmount * 0.5F;
        this.leg2.xRot = Mth.cos(limbSwing * 0.6662F + 3.1415927F) * 1.4F * limbSwingAmount * 0.5F;
        animatePokerArms(this.arm1, this.arm2, this.head, this.attackTime);
    }

    public static void animatePokerArms(ModelPart rightArm, ModelPart leftArm, ModelPart head, float attackTime) {
        float f = Mth.sin(attackTime * -(float) Math.PI);
        float f1 = Mth.sin((1.0F - (1.0F - attackTime) * (1.0F - attackTime)) * (float) Math.PI);

        rightArm.yRot = (-0.45F + head.yRot) + (0.1F - f);
        leftArm.yRot = (0.45F + head.yRot) - (0.1F - f);
        rightArm.xRot = ((-(float) Math.PI / 2F) + head.xRot + 0.1F) + (f * 1.2F - f1 * 0.4F);
        leftArm.xRot = (-1.5F + head.xRot) + (f * 1.2F - f1 * 0.4F);
    }

    @Override
    public void renderToBuffer(PoseStack poseStack, VertexConsumer vertexConsumer, int packedLight, int packedOverlay, float red, float green, float blue, float alpha) {
        this.root.render(poseStack, vertexConsumer, packedLight, packedOverlay, red, green, blue, alpha);
    }

    @Override
    public ModelPart root() {
        return this.root;
    }

    private ModelPart getArm(HumanoidArm p_191216_1_) {
        return p_191216_1_ == HumanoidArm.LEFT ? this.arm2 : this.arm1;
    }

    @Override
    public void translateToHand(HumanoidArm p_102108_, PoseStack p_102109_) {
        this.root().translateAndRotate(p_102109_);
        this.all.translateAndRotate(p_102109_);
        this.body.translateAndRotate(p_102109_);
        this.getArm(p_102108_).translateAndRotate(p_102109_);
        p_102109_.scale(0.55F, 0.55F, 0.55F);
    }
}