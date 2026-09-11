package com.dynasty.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.CubeListBuilder;
import net.minecraft.client.model.geom.builders.LayerDefinition;
import net.minecraft.client.model.geom.builders.MeshDefinition;
import net.minecraft.client.model.geom.builders.PartDefinition;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;

/**
 * 通用四足神兽模型：麒麟、九尾狐共用。
 * Generic quadruped beast model used by the Qilin and the Nine-tailed Fox.
 */
public class DynastyBeastModel<T extends Entity> extends EntityModel<T> {

    private final ModelPart body;
    private final ModelPart head;
    private final ModelPart tail;
    private final ModelPart legFrontLeft;
    private final ModelPart legFrontRight;
    private final ModelPart legBackLeft;
    private final ModelPart legBackRight;

    public DynastyBeastModel(ModelPart root) {
        this.body = root.getChild("body");
        this.head = root.getChild("head");
        this.tail = root.getChild("tail");
        this.legFrontLeft = root.getChild("leg_front_left");
        this.legFrontRight = root.getChild("leg_front_right");
        this.legBackLeft = root.getChild("leg_back_left");
        this.legBackRight = root.getChild("leg_back_right");
    }

    public static LayerDefinition createBodyLayer() {
        MeshDefinition mesh = new MeshDefinition();
        PartDefinition root = mesh.getRoot();
        root.addOrReplaceChild("body", CubeListBuilder.create().texOffs(0, 0)
                        .addBox(-6.0F, -6.0F, -8.0F, 12.0F, 10.0F, 18.0F),
                PartPose.offset(0.0F, 12.0F, 0.0F));
        root.addOrReplaceChild("head", CubeListBuilder.create().texOffs(0, 30)
                        .addBox(-4.0F, -4.0F, -8.0F, 8.0F, 8.0F, 8.0F)
                        .texOffs(32, 30).addBox(-3.0F, -8.0F, -5.0F, 2.0F, 5.0F, 2.0F)
                        .texOffs(32, 30).addBox(1.0F, -8.0F, -5.0F, 2.0F, 5.0F, 2.0F),
                PartPose.offset(0.0F, 8.0F, -9.0F));
        root.addOrReplaceChild("tail", CubeListBuilder.create().texOffs(44, 30)
                        .addBox(-2.0F, -2.0F, 0.0F, 4.0F, 4.0F, 12.0F),
                PartPose.offset(0.0F, 8.0F, 10.0F));
        root.addOrReplaceChild("leg_front_left", CubeListBuilder.create().texOffs(0, 48)
                        .addBox(-2.0F, 0.0F, -2.0F, 4.0F, 9.0F, 4.0F),
                PartPose.offset(4.0F, 15.0F, -6.0F));
        root.addOrReplaceChild("leg_front_right", CubeListBuilder.create().texOffs(0, 48)
                        .addBox(-2.0F, 0.0F, -2.0F, 4.0F, 9.0F, 4.0F),
                PartPose.offset(-4.0F, 15.0F, -6.0F));
        root.addOrReplaceChild("leg_back_left", CubeListBuilder.create().texOffs(0, 48)
                        .addBox(-2.0F, 0.0F, -2.0F, 4.0F, 9.0F, 4.0F),
                PartPose.offset(4.0F, 15.0F, 7.0F));
        root.addOrReplaceChild("leg_back_right", CubeListBuilder.create().texOffs(0, 48)
                        .addBox(-2.0F, 0.0F, -2.0F, 4.0F, 9.0F, 4.0F),
                PartPose.offset(-4.0F, 15.0F, 7.0F));
        return LayerDefinition.create(mesh, 128, 128);
    }

    @Override
    public void setupAnim(T entity, float limbSwing, float limbSwingAmount, float ageInTicks,
                          float netHeadYaw, float headPitch) {
        this.head.yRot = netHeadYaw * ((float) Math.PI / 180.0F);
        this.head.xRot = headPitch * ((float) Math.PI / 180.0F);
        this.legFrontLeft.xRot = Mth.cos(limbSwing * 0.6662F) * 1.4F * limbSwingAmount;
        this.legFrontRight.xRot = Mth.cos(limbSwing * 0.6662F + (float) Math.PI) * 1.4F * limbSwingAmount;
        this.legBackLeft.xRot = Mth.cos(limbSwing * 0.6662F + (float) Math.PI) * 1.4F * limbSwingAmount;
        this.legBackRight.xRot = Mth.cos(limbSwing * 0.6662F) * 1.4F * limbSwingAmount;
        this.tail.yRot = Mth.cos(ageInTicks * 0.12F) * 0.5F;
        this.tail.xRot = -0.2F + Mth.cos(ageInTicks * 0.08F) * 0.15F;
    }

    @Override
    public void renderToBuffer(PoseStack pose, VertexConsumer buffer, int packedLight, int packedOverlay,
                               float red, float green, float blue, float alpha) {
        this.body.render(pose, buffer, packedLight, packedOverlay, red, green, blue, alpha);
        this.head.render(pose, buffer, packedLight, packedOverlay, red, green, blue, alpha);
        this.tail.render(pose, buffer, packedLight, packedOverlay, red, green, blue, alpha);
        this.legFrontLeft.render(pose, buffer, packedLight, packedOverlay, red, green, blue, alpha);
        this.legFrontRight.render(pose, buffer, packedLight, packedOverlay, red, green, blue, alpha);
        this.legBackLeft.render(pose, buffer, packedLight, packedOverlay, red, green, blue, alpha);
        this.legBackRight.render(pose, buffer, packedLight, packedOverlay, red, green, blue, alpha);
    }
}
