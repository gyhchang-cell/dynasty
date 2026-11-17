package com.yellowbrossproductions.illageandspillage.client.model;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.yellowbrossproductions.illageandspillage.client.model.animation.FactoryAnimation;
import com.yellowbrossproductions.illageandspillage.entities.FactoryEntity;
import net.minecraft.client.model.HierarchicalModel;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.Entity;

import java.util.Calendar;

public class FactoryModel<T extends Entity> extends HierarchicalModel<T> {
    public static final ModelLayerLocation LAYER_LOCATION = new ModelLayerLocation(new ResourceLocation("illageandspillage", "factory"), "main");
    private final ModelPart root;
    private final ModelPart all;
    private final ModelPart fold2;
    private final ModelPart head;
    private final ModelPart chute2;
    private final ModelPart chute3;
    private final ModelPart fold1;
    private final ModelPart chute1;

    public FactoryModel(ModelPart root) {
        this.root = root;
        this.all = this.root.getChild("all");
        this.fold2 = all.getChild("fold2");
        this.head = fold2.getChild("head");
        this.chute2 = fold2.getChild("chute2");
        this.chute3 = fold2.getChild("chute3");
        this.fold1 = all.getChild("fold1");
        this.chute1 = fold1.getChild("chute1");
    }

    public static LayerDefinition createBodyLayer() {
        MeshDefinition meshdefinition = new MeshDefinition();
        PartDefinition partdefinition = meshdefinition.getRoot();

        PartDefinition all = partdefinition.addOrReplaceChild("all", CubeListBuilder.create(), PartPose.offset(0.0F, 14.0F, 0.0F));

        PartDefinition fold2 = all.addOrReplaceChild("fold2", CubeListBuilder.create().texOffs(10, 10).addBox(12.0F, -2.0F, -1.0F, 1.0F, 4.0F, 2.0F, new CubeDeformation(0.0F))
                .texOffs(0, 0).mirror().addBox(0.0F, 0.0F, -8.0F, 12.0F, 4.0F, 16.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offset(0.0F, 6.0F, 0.0F));

        PartDefinition head = fold2.addOrReplaceChild("head", CubeListBuilder.create().texOffs(0, 40).addBox(-6.0F, -8.5F, -3.5F, 12.0F, 8.0F, 7.0F, new CubeDeformation(0.0F)), PartPose.offset(6.0F, 0.5F, -4.5F));

        PartDefinition birthday = head.addOrReplaceChild("birthday", CubeListBuilder.create().texOffs(45, 22).addBox(-2.0F, -9.3333F, 6.0833F, 4.0F, 3.0F, 4.0F, new CubeDeformation(0.0F))
                .texOffs(33, 22).addBox(-1.5F, -12.3333F, 6.5833F, 3.0F, 3.0F, 3.0F, new CubeDeformation(0.0F))
                .texOffs(58, 19).addBox(0.0F, -15.3333F, 6.5833F, 0.0F, 3.0F, 3.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, -2.1667F, -8.5833F, -0.0873F, 0.0F, 0.0F));

        birthday.addOrReplaceChild("thingy", CubeListBuilder.create().texOffs(58, 19).addBox(-1.5F, -15.3333F, 8.0F, 3.0F, 3.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 0.0F, 0.0F));

        fold2.addOrReplaceChild("chute2", CubeListBuilder.create().texOffs(40, 0).addBox(-3.0F, -14.75F, -3.0F, 6.0F, 6.0F, 6.0F, new CubeDeformation(0.0F))
                .texOffs(0, 0).addBox(-1.5F, -8.75F, -1.5F, 3.0F, 9.0F, 3.0F, new CubeDeformation(0.0F)), PartPose.offset(-0.5F, -0.25F, 1.5F));

        fold2.addOrReplaceChild("chute3", CubeListBuilder.create().texOffs(40, 0).addBox(-3.0F, -14.75F, -3.0F, 6.0F, 6.0F, 6.0F, new CubeDeformation(0.0F))
                .texOffs(0, 0).addBox(-1.5F, -8.75F, -1.5F, 3.0F, 9.0F, 3.0F, new CubeDeformation(0.0F)), PartPose.offset(7.5F, -0.25F, 3.3F));

        PartDefinition fold1 = all.addOrReplaceChild("fold1", CubeListBuilder.create().texOffs(0, 0).addBox(-12.0F, 0.0F, -8.0F, 12.0F, 4.0F, 16.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 6.0F, 0.0F));

        fold1.addOrReplaceChild("chute1", CubeListBuilder.create().texOffs(40, 0).addBox(-3.0F, -14.75F, -3.0F, 6.0F, 6.0F, 6.0F, new CubeDeformation(0.0F))
                .texOffs(0, 0).addBox(-1.5F, -8.75F, -1.5F, 3.0F, 9.0F, 3.0F, new CubeDeformation(0.0F)), PartPose.offset(-8.5F, -0.25F, -0.5F));

        return LayerDefinition.create(meshdefinition, 64, 64);
    }

    @Override
    public void setupAnim(Entity entity, float limbSwing, float limbSwingAmount, float ageInTicks, float netHeadYaw, float headPitch) {
        this.root().getAllParts().forEach(ModelPart::resetPose);
        if (entity instanceof FactoryEntity factory) {
            this.animate(factory.getAnimationState("intro"), FactoryAnimation.INTRO, ageInTicks, factory.getAnimationSpeed());
            this.animate(factory.getAnimationState("spin"), FactoryAnimation.SPIN, ageInTicks, factory.getAnimationSpeed());

            Calendar calendar = Calendar.getInstance();
            this.head.getChild("birthday").visible = calendar.get(Calendar.MONTH) == Calendar.FEBRUARY && calendar.get(Calendar.DAY_OF_MONTH) < 8;
        }
    }

    @Override
    public void renderToBuffer(PoseStack poseStack, VertexConsumer vertexConsumer, int packedLight, int packedOverlay, float red, float green, float blue, float alpha) {
        this.root.render(poseStack, vertexConsumer, packedLight, packedOverlay, red, green, blue, alpha);
    }

    @Override
    public ModelPart root() {
        return this.root;
    }
}