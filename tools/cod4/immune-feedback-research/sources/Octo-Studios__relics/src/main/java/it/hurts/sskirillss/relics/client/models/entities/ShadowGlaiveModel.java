package it.hurts.sskirillss.relics.client.models.entities;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.world.entity.Entity;

public class ShadowGlaiveModel<T extends Entity> extends EntityModel<T> {
    private final ModelPart bone;

    public ShadowGlaiveModel() {
        MeshDefinition meshdefinition = new MeshDefinition();
        PartDefinition partdefinition = meshdefinition.getRoot();

        PartDefinition bone = partdefinition.addOrReplaceChild("bone", CubeListBuilder.create().texOffs(10, 6).addBox(-1.0F, -5.0F, -0.5F, 2.0F, 4.0F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(12, 16).addBox(-1.0F, -6.0F, 0.0F, 2.0F, 1.0F, 0.0F, new CubeDeformation(0.0F))
                .texOffs(0, 6).addBox(-5.0F, -1.0F, -0.5F, 4.0F, 2.0F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(6, 12).addBox(-6.0F, -1.0F, 0.0F, 1.0F, 2.0F, 0.0F, new CubeDeformation(0.0F))
                .texOffs(0, 9).addBox(1.0F, -1.0F, -0.5F, 4.0F, 2.0F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(18, 2).addBox(5.0F, -1.0F, 0.0F, 1.0F, 2.0F, 0.0F, new CubeDeformation(0.0F))
                .texOffs(0, 12).addBox(-1.0F, 1.0F, -0.5F, 2.0F, 4.0F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(16, 12).addBox(-1.0F, 5.0F, 0.0F, 2.0F, 1.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 16.0F, 0.5F));

        bone.addOrReplaceChild("cube_r1", CubeListBuilder.create().texOffs(0, 0).addBox(-2.0F, -2.0F, -1.0F, 4.0F, 4.0F, 2.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 0.0F, 0.0F, 0.0F, 0.0F, 0.7854F));

        bone.addOrReplaceChild("cube_r2", CubeListBuilder.create().texOffs(0, 17).addBox(-1.0F, -3.0F, 0.0F, 2.0F, 1.0F, 0.0F, new CubeDeformation(0.0F))
                .texOffs(16, 5).addBox(-1.0F, -2.0F, -0.5F, 2.0F, 4.0F, 1.0F, new CubeDeformation(0.005F)), PartPose.offsetAndRotation(-2.6892F, -2.4651F, 0.0F, 0.0F, 0.0F, -0.7854F));

        bone.addOrReplaceChild("cube_r3", CubeListBuilder.create().texOffs(18, 0).addBox(-1.0F, 2.0F, 0.0F, 2.0F, 1.0F, 0.0F, new CubeDeformation(0.0F))
                .texOffs(6, 16).addBox(-1.0F, -2.0F, -0.5F, 2.0F, 4.0F, 1.0F, new CubeDeformation(0.005F)), PartPose.offsetAndRotation(-2.6892F, 2.4651F, 0.0F, 0.0F, 0.0F, 0.7854F));

        bone.addOrReplaceChild("cube_r4", CubeListBuilder.create().texOffs(16, 14).addBox(-1.0F, 2.0F, 0.0F, 2.0F, 1.0F, 0.0F, new CubeDeformation(0.0F))
                .texOffs(12, 0).addBox(-1.0F, -2.0F, -0.5F, 2.0F, 4.0F, 1.0F, new CubeDeformation(0.005F)), PartPose.offsetAndRotation(2.6892F, 2.4651F, 0.0F, 0.0F, 0.0F, -0.7854F));

        bone.addOrReplaceChild("cube_r5", CubeListBuilder.create().texOffs(16, 10).addBox(-1.0F, -3.0F, 0.0F, 2.0F, 1.0F, 0.0F, new CubeDeformation(0.0F))
                .texOffs(10, 11).addBox(-1.0F, -2.0F, -0.5F, 2.0F, 4.0F, 1.0F, new CubeDeformation(0.005F)), PartPose.offsetAndRotation(2.6892F, -2.4651F, 0.0F, 0.0F, 0.0F, 0.7854F));

        this.bone = LayerDefinition.create(meshdefinition, 32, 32).bakeRoot().getChild("bone");
    }

    @Override
    public void setupAnim(T entity, float limbSwing, float limbSwingAmount, float ageInTicks, float netHeadYaw, float headPitch) {

    }

    @Override
    public void renderToBuffer(PoseStack poseStack, VertexConsumer buffer, int packedLight, int packedOverlay, int seed) {
        bone.render(poseStack, buffer, packedLight, packedOverlay, seed);
    }
}