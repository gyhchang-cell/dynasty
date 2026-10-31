package com.yellowbrossproductions.illageandspillage.client.model;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.yellowbrossproductions.illageandspillage.client.model.animation.EyesoreAnimation;
import com.yellowbrossproductions.illageandspillage.entities.EyesoreEntity;
import net.minecraft.client.model.HierarchicalModel;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.Entity;

import java.util.Calendar;

public class EyesoreModel<T extends Entity> extends HierarchicalModel<T> {
    public static final ModelLayerLocation LAYER_LOCATION = new ModelLayerLocation(new ResourceLocation("illageandspillage", "eyesore"), "main");
    private final ModelPart root;
    private final ModelPart eye;
    private final ModelPart tendon;
    private final ModelPart tendon2;
    private final ModelPart tendon3;
    private final ModelPart tendon4;

    public EyesoreModel(ModelPart root) {
        this.root = root;
        this.eye = this.root.getChild("eye");
        this.tendon = eye.getChild("tendon");
        this.tendon2 = tendon.getChild("tendon2");
        this.tendon3 = tendon2.getChild("tendon3");
        this.tendon4 = tendon3.getChild("tendon4");
    }

    public static LayerDefinition createBodyLayer() {
        MeshDefinition meshdefinition = new MeshDefinition();
        PartDefinition partdefinition = meshdefinition.getRoot();

        PartDefinition eye = partdefinition.addOrReplaceChild("eye", CubeListBuilder.create().texOffs(0, 0).addBox(-6.0F, -7.0F, -7.0F, 12.0F, 12.0F, 12.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 19.0F, 1.0F));

        PartDefinition tendon = eye.addOrReplaceChild("tendon", CubeListBuilder.create().texOffs(12, 60).addBox(-6.0F, 2.0F, 0.0F, 12.0F, 0.0F, 12.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, -3.0F, 5.0F, -0.2182F, 0.0F, 0.0F));

        tendon.addOrReplaceChild("cube_r1", CubeListBuilder.create().texOffs(24, 48).addBox(0.0F, -6.0F, -6.0F, 0.0F, 12.0F, 12.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 2.0F, 6.0F, -1.5708F, 0.0F, 0.0F));

        PartDefinition tendon2 = tendon.addOrReplaceChild("tendon2", CubeListBuilder.create().texOffs(0, 36).addBox(-6.0F, -0.5F, 0.0F, 12.0F, 0.0F, 12.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 2.5F, 12.0F, 0.1309F, 0.0F, 0.0F));

        tendon2.addOrReplaceChild("cube_r2", CubeListBuilder.create().texOffs(13, 24).addBox(0.0F, -6.0F, -6.0F, 0.0F, 12.0F, 12.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, -1.5F, 6.0F, -1.5708F, 0.0F, 0.0F));

        PartDefinition tendon3 = tendon2.addOrReplaceChild("tendon3", CubeListBuilder.create().texOffs(24, 24).addBox(-6.0F, 0.0F, 0.0F, 12.0F, 0.0F, 12.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, -0.5F, 12.0F, 0.0873F, 0.0F, 0.0F));

        tendon3.addOrReplaceChild("cube_r3", CubeListBuilder.create().texOffs(36, 12).addBox(0.0F, -6.0F, -6.0F, 0.0F, 12.0F, 12.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 0.0F, 6.0F, -1.5708F, 0.0F, 0.0F));

        PartDefinition tendon4 = tendon3.addOrReplaceChild("tendon4", CubeListBuilder.create().texOffs(26, 0).mirror().addBox(-6.5F, -0.25F, 0.5F, 12.0F, 0.0F, 11.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offsetAndRotation(-0.5F, 0.25F, 11.2F, -0.1298F, 0.0169F, 0.0011F));

        tendon4.addOrReplaceChild("cube_r4", CubeListBuilder.create().texOffs(37, -11).addBox(0.0F, -5.5F, -5.5F, 0.0F, 11.0F, 11.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.5F, 0.25F, 6.0F, -1.5708F, 0.0F, -3.1416F));

        PartDefinition birthday = eye.addOrReplaceChild("birthday", CubeListBuilder.create().texOffs(80, 21).addBox(-2.0F, -9.3333F, 6.0833F, 4.0F, 3.0F, 4.0F, new CubeDeformation(0.0F))
                .texOffs(68, 21).addBox(-1.5F, -12.3333F, 6.5833F, 3.0F, 3.0F, 3.0F, new CubeDeformation(0.0F))
                .texOffs(93, 18).addBox(0.0F, -15.3333F, 6.5833F, 0.0F, 3.0F, 3.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, -0.6667F, -10.0833F, -0.0873F, 0.0F, 0.0F));

        birthday.addOrReplaceChild("thingy", CubeListBuilder.create().texOffs(93, 21).addBox(-1.5F, -15.3333F, 8.0F, 3.0F, 3.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 0.0F, 0.0F));

        return LayerDefinition.create(meshdefinition, 128, 128);
    }

    @Override
    public void setupAnim(Entity entity, float limbSwing, float limbSwingAmount, float ageInTicks, float netHeadYaw, float headPitch) {
        this.root().getAllParts().forEach(ModelPart::resetPose);
        if (entity instanceof EyesoreEntity eyesore) {
            Calendar calendar = Calendar.getInstance();
            this.eye.getChild("birthday").visible = calendar.get(Calendar.MONTH) == Calendar.FEBRUARY && calendar.get(Calendar.DAY_OF_MONTH) < 8;
            this.animate(eyesore.getAnimationState("slither"), EyesoreAnimation.SLITHER, ageInTicks, eyesore.getAnimationSpeed());
            this.animate(eyesore.getAnimationState("fly"), EyesoreAnimation.FLY, ageInTicks, eyesore.getAnimationSpeed());
        }
    }

    @Override
    public void renderToBuffer(PoseStack poseStack, VertexConsumer vertexConsumer, int packedLight, int packedOverlay, float red, float green, float blue, float alpha) {
        eye.render(poseStack, vertexConsumer, packedLight, packedOverlay, red, green, blue, alpha);
    }

    @Override
    public ModelPart root() {
        return this.root;
    }
}