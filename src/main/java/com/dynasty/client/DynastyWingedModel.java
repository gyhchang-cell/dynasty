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
 * 飞行神兽模型（凤凰）：身体 + 头 + 双翼 + 尾羽。
 * Winged beast model (Phoenix): body, head, wings and tail feathers.
 */
public class DynastyWingedModel<T extends Entity> extends EntityModel<T> {

    private final ModelPart body;
    private final ModelPart head;
    private final ModelPart leftWing;
    private final ModelPart rightWing;
    private final ModelPart tail;

    public DynastyWingedModel(ModelPart root) {
        this.body = root.getChild("body");
        this.head = root.getChild("head");
        this.leftWing = root.getChild("left_wing");
        this.rightWing = root.getChild("right_wing");
        this.tail = root.getChild("tail");
    }

    public static LayerDefinition createBodyLayer() {
        MeshDefinition mesh = new MeshDefinition();
        PartDefinition root = mesh.getRoot();
        root.addOrReplaceChild("body", CubeListBuilder.create().texOffs(0, 0)
                        .addBox(-4.0F, -4.0F, -6.0F, 8.0F, 8.0F, 14.0F),
                PartPose.offset(0.0F, 14.0F, 0.0F));
        root.addOrReplaceChild("head", CubeListBuilder.create().texOffs(0, 24)
                        .addBox(-3.0F, -3.0F, -6.0F, 6.0F, 6.0F, 6.0F)
                        .texOffs(24, 24).addBox(-1.0F, -6.0F, -6.0F, 2.0F, 4.0F, 2.0F),
                PartPose.offset(0.0F, 11.0F, -6.0F));
        root.addOrReplaceChild("left_wing", CubeListBuilder.create().texOffs(32, 0)
                        .addBox(0.0F, -1.0F, -4.0F, 18.0F, 2.0F, 12.0F),
                PartPose.offset(4.0F, 13.0F, 0.0F));
        root.addOrReplaceChild("right_wing", CubeListBuilder.create().texOffs(32, 0)
                        .addBox(-18.0F, -1.0F, -4.0F, 18.0F, 2.0F, 12.0F),
                PartPose.offset(-4.0F, 13.0F, 0.0F));
        root.addOrReplaceChild("tail", CubeListBuilder.create().texOffs(0, 40)
                        .addBox(-3.0F, -1.0F, 0.0F, 6.0F, 2.0F, 16.0F),
                PartPose.offset(0.0F, 13.0F, 8.0F));
        return LayerDefinition.create(mesh, 128, 128);
    }

    @Override
    public void setupAnim(T entity, float limbSwing, float limbSwingAmount, float ageInTicks,
                          float netHeadYaw, float headPitch) {
        this.head.yRot = netHeadYaw * ((float) Math.PI / 180.0F);
        this.head.xRot = headPitch * ((float) Math.PI / 180.0F);
        float flap = Mth.cos(ageInTicks * 0.6F) * 0.9F;
        this.leftWing.zRot = -flap;
        this.rightWing.zRot = flap;
        this.tail.xRot = 0.15F + Mth.cos(ageInTicks * 0.2F) * 0.12F;
    }

    @Override
    public void renderToBuffer(PoseStack pose, VertexConsumer buffer, int packedLight, int packedOverlay,
                               float red, float green, float blue, float alpha) {
        this.body.render(pose, buffer, packedLight, packedOverlay, red, green, blue, alpha);
        this.head.render(pose, buffer, packedLight, packedOverlay, red, green, blue, alpha);
        this.leftWing.render(pose, buffer, packedLight, packedOverlay, red, green, blue, alpha);
        this.rightWing.render(pose, buffer, packedLight, packedOverlay, red, green, blue, alpha);
        this.tail.render(pose, buffer, packedLight, packedOverlay, red, green, blue, alpha);
    }
}
