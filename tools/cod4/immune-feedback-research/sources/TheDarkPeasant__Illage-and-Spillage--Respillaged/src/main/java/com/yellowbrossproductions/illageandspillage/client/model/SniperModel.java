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

import java.util.Calendar;

public class SniperModel<T extends Entity> extends EntityModel<T> {
    public static final ModelLayerLocation LAYER_LOCATION = new ModelLayerLocation(new ResourceLocation("illageandspillage", "sniper"), "main");
    private final ModelPart all;
    private final ModelPart body;
    private final ModelPart arms;
    private final ModelPart gun;
    private final ModelPart propeller;
    private final ModelPart head;
    private final ModelPart legs;

    public SniperModel(ModelPart root) {
        this.all = root.getChild("all");
        this.body = all.getChild("body");
        this.arms = body.getChild("arms");
        this.gun = body.getChild("gun");
        this.propeller = body.getChild("propeller");
        this.head = body.getChild("head");
        this.legs = all.getChild("legs");
    }

    public static LayerDefinition createBodyLayer() {
        MeshDefinition meshdefinition = new MeshDefinition();
        PartDefinition partdefinition = meshdefinition.getRoot();

        PartDefinition all = partdefinition.addOrReplaceChild("all", CubeListBuilder.create(), PartPose.offset(0.0F, 18.0F, 0.0F));

        PartDefinition body = all.addOrReplaceChild("body", CubeListBuilder.create().texOffs(14, 12).addBox(-7.5F, 10.0F, 3.5F, 4.0F, 5.0F, 2.0F, new CubeDeformation(0.0F))
                .texOffs(6, 11).addBox(-6.0F, 1.0F, 8.0F, 1.0F, 11.0F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(0, 15).addBox(-6.0F, 11.0F, 5.0F, 1.0F, 1.0F, 3.0F, new CubeDeformation(0.0F)), PartPose.offset(5.5F, -15.0F, -4.5F));

        body.addOrReplaceChild("arms", CubeListBuilder.create().texOffs(18, 19).addBox(-2.0F, 2.0F, -1.0F, 4.0F, 2.0F, 2.0F, new CubeDeformation(0.0F))
                .texOffs(10, 19).addBox(-4.0F, -1.0F, -1.0F, 2.0F, 5.0F, 2.0F, new CubeDeformation(0.0F))
                .texOffs(10, 19).mirror().addBox(2.0F, -1.0F, -1.0F, 2.0F, 5.0F, 2.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offsetAndRotation(-5.5F, 11.0F, 4.5F, -0.7854F, 0.0F, 0.0F));

        body.addOrReplaceChild("gun", CubeListBuilder.create().texOffs(14, 25).addBox(-1.5F, -1.5F, -3.0F, 3.0F, 3.0F, 4.0F, new CubeDeformation(0.0F)), PartPose.offset(-5.5F, 13.0F, 3.5F));

        PartDefinition propeller = body.addOrReplaceChild("propeller", CubeListBuilder.create().texOffs(21, 23).addBox(-0.5F, 0.0F, -4.5F, 1.0F, 0.0F, 9.0F, new CubeDeformation(0.0F)), PartPose.offset(-5.5F, 1.0F, 8.5F));

        propeller.addOrReplaceChild("cube_r1", CubeListBuilder.create().texOffs(21, 23).addBox(-0.5F, 0.0F, -5.0F, 1.0F, 0.0F, 9.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(-0.5F, 0.0F, 0.0F, 0.0F, -1.5708F, 0.0F));

        PartDefinition head = body.addOrReplaceChild("head", CubeListBuilder.create().texOffs(0, 0).addBox(-2.5F, -7.0F, -2.5F, 5.0F, 7.0F, 5.0F, new CubeDeformation(0.0F))
                .texOffs(24, 8).addBox(-1.0F, -3.0F, -4.0F, 2.0F, 4.0F, 2.0F, new CubeDeformation(0.0F)), PartPose.offset(-5.5F, 10.0F, 4.5F));

        PartDefinition birthday = head.addOrReplaceChild("birthday", CubeListBuilder.create().texOffs(12, 32).addBox(-2.0F, -9.3333F, 6.0833F, 4.0F, 3.0F, 4.0F, new CubeDeformation(0.0F))
                .texOffs(0, 32).addBox(-1.5F, -12.3333F, 6.5833F, 3.0F, 3.0F, 3.0F, new CubeDeformation(0.0F))
                .texOffs(25, 29).addBox(0.0F, -15.3333F, 6.5833F, 0.0F, 3.0F, 3.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, -0.6667F, -8.0833F, -0.0436F, 0.0F, 0.0F));

        birthday.addOrReplaceChild("thingy", CubeListBuilder.create().texOffs(25, 32).addBox(-1.5F, -15.3333F, 8.0F, 3.0F, 3.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 0.0F, 0.0F));

        all.addOrReplaceChild("legs", CubeListBuilder.create().texOffs(0, 19).addBox(0.0F, 0.0F, -1.0F, 2.0F, 6.0F, 2.0F, new CubeDeformation(0.0F))
                .texOffs(0, 19).mirror().addBox(-2.0F, 0.0F, -1.0F, 2.0F, 6.0F, 2.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offset(0.0F, 0.0F, 0.0F));

        return LayerDefinition.create(meshdefinition, 32, 40);
    }

    @Override
    public void setupAnim(Entity entity, float limbSwing, float limbSwingAmount, float ageInTicks, float netHeadYaw, float headPitch) {
        Calendar calendar = Calendar.getInstance();
        this.head.getChild("birthday").visible = calendar.get(Calendar.MONTH) == Calendar.FEBRUARY && calendar.get(Calendar.DAY_OF_MONTH) < 8;

        this.head.yRot = netHeadYaw * 0.017453292F;
        this.head.xRot = headPitch * 0.017453292F;
        this.gun.xRot = headPitch * 0.017453292F;

        this.legs.xRot = limbSwingAmount * 0.4F;

        this.propeller.yRot = ageInTicks * 60.0F * 0.017453292F;
    }

    @Override
    public void renderToBuffer(PoseStack poseStack, VertexConsumer vertexConsumer, int packedLight, int packedOverlay, float red, float green, float blue, float alpha) {
        this.all.render(poseStack, vertexConsumer, packedLight, packedOverlay, red, green, blue, alpha);
    }
}