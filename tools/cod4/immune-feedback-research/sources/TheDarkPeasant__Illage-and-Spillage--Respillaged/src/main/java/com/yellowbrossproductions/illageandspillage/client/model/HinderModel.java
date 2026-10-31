package com.yellowbrossproductions.illageandspillage.client.model;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.yellowbrossproductions.illageandspillage.client.model.animation.HinderAnimation;
import com.yellowbrossproductions.illageandspillage.entities.HinderEntity;
import net.minecraft.client.model.HierarchicalModel;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.Entity;

import java.util.Calendar;

public class HinderModel<T extends Entity> extends HierarchicalModel<T> {
    public static final ModelLayerLocation LAYER_LOCATION = new ModelLayerLocation(new ResourceLocation("illageandspillage", "hinder"), "main");
    private final ModelPart root;
    private final ModelPart thingy2;
    private final ModelPart thingy;
    private final ModelPart head;
    private final ModelPart stick;
    private final ModelPart propeler;
    private final ModelPart base;

    public HinderModel(ModelPart root) {
        this.root = root;
        this.thingy2 = this.root.getChild("thingy2");
        this.thingy = this.root.getChild("thingy");
        this.head = root.getChild("head");
        this.base = this.root.getChild("base");
        this.stick = head.getChild("stick");
        this.propeler = stick.getChild("propeler");
    }

    public static LayerDefinition createBodyLayer() {
        MeshDefinition meshdefinition = new MeshDefinition();
        PartDefinition partdefinition = meshdefinition.getRoot();

        partdefinition.addOrReplaceChild("thingy2", CubeListBuilder.create().texOffs(28, 0).mirror().addBox(-5.0F, -7.5F, -5.0F, 10.0F, 0.0F, 10.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offset(0.0F, 24.0F, 0.0F));

        partdefinition.addOrReplaceChild("thingy", CubeListBuilder.create().texOffs(28, 0).addBox(-5.0F, -9.5F, -5.0F, 10.0F, 0.0F, 10.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 24.0F, 0.0F));

        PartDefinition head = partdefinition.addOrReplaceChild("head", CubeListBuilder.create().texOffs(0, 32).addBox(-4.0F, -4.75F, -4.0F, 8.0F, 8.0F, 8.0F, new CubeDeformation(0.0F))
                .texOffs(32, 48).addBox(-4.0F, -6.75F, -4.0F, 8.0F, 2.0F, 8.0F, new CubeDeformation(0.0F))
                .texOffs(0, 62).addBox(-6.0F, 4.25F, -1.0F, 12.0F, 2.0F, 2.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 7.75F, 0.0F));

        head.addOrReplaceChild("cube_r1", CubeListBuilder.create().texOffs(0, 62).addBox(-6.0F, -1.0F, -1.0F, 12.0F, 2.0F, 2.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 5.25F, 0.0F, 0.0F, -1.5708F, 0.0F));

        head.addOrReplaceChild("cube_r2", CubeListBuilder.create().texOffs(32, 48).addBox(-4.0F, -1.0F, -4.0F, 8.0F, 2.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 4.25F, 0.0F, 3.1416F, 0.0F, 0.0F));

        PartDefinition stick = head.addOrReplaceChild("stick", CubeListBuilder.create().texOffs(0, 19).addBox(-1.0F, -6.0F, -1.0F, 2.0F, 6.0F, 2.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, -6.75F, 0.0F));

        PartDefinition propeler = stick.addOrReplaceChild("propeler", CubeListBuilder.create().texOffs(-18, 0).addBox(-9.0F, 0.0F, -9.0F, 18.0F, 0.0F, 18.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, -6.1F, 0.0F));

        PartDefinition birthday = propeler.addOrReplaceChild("birthday", CubeListBuilder.create().texOffs(72, 26).addBox(-2.0F, -9.3333F, 6.0833F, 4.0F, 3.0F, 4.0F, new CubeDeformation(0.0F))
                .texOffs(60, 26).addBox(-1.5F, -12.3333F, 6.5833F, 3.0F, 3.0F, 3.0F, new CubeDeformation(0.0F))
                .texOffs(85, 23).addBox(0.0F, -15.3333F, 6.5833F, 0.0F, 3.0F, 3.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 6.4333F, -8.0833F));

        birthday.addOrReplaceChild("thingy3", CubeListBuilder.create().texOffs(85, 26).addBox(-1.5F, -15.3333F, 8.0F, 3.0F, 3.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 0.0F, 0.0F));

        partdefinition.addOrReplaceChild("base", CubeListBuilder.create().texOffs(0, 18).addBox(-5.0F, -4.0F, -5.0F, 10.0F, 4.0F, 10.0F, new CubeDeformation(0.0F))
                .texOffs(32, 48).addBox(-4.0F, -6.0F, -4.0F, 8.0F, 2.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 24.0F, 0.0F));

        return LayerDefinition.create(meshdefinition, 128, 128);
    }

    @Override
    public void setupAnim(Entity entity, float limbSwing, float limbSwingAmount, float ageInTicks, float netHeadYaw, float headPitch) {
        this.root().getAllParts().forEach(ModelPart::resetPose);
        if (entity instanceof HinderEntity hinder) {
            this.animate(hinder.getAnimationState("intro"), HinderAnimation.SPAWN, ageInTicks, hinder.getAnimationSpeed());
            this.animate(hinder.getAnimationState("idle"), HinderAnimation.IDLE, ageInTicks, hinder.getAnimationSpeed());

            Calendar calendar = Calendar.getInstance();
            this.propeler.getChild("birthday").visible = calendar.get(Calendar.MONTH) == Calendar.FEBRUARY && calendar.get(Calendar.DAY_OF_MONTH) < 8;

            if (hinder.isInMotion()) {
                this.base.xRot = ageInTicks * 25.0F * 0.017453292F;
                this.base.yRot = ageInTicks * 15.0F * 0.017453292F;
                this.base.zRot = ageInTicks * 20.0F * 0.017453292F;
                this.head.visible = false;
                this.thingy.visible = false;
                this.thingy2.visible = false;
            } else {
                this.base.xRot = 0.0F;
                this.base.yRot = 0.0F;
                this.base.zRot = 0.0F;
                this.head.visible = true;
                this.thingy.visible = true;
                this.thingy2.visible = true;
            }
        }
    }

    @Override
    public void renderToBuffer(PoseStack poseStack, VertexConsumer vertexConsumer, int packedLight, int packedOverlay, float red, float green, float blue, float alpha) {
        thingy2.render(poseStack, vertexConsumer, packedLight, packedOverlay, red, green, blue, alpha);
        thingy.render(poseStack, vertexConsumer, packedLight, packedOverlay, red, green, blue, alpha);
        head.render(poseStack, vertexConsumer, packedLight, packedOverlay, red, green, blue, alpha);
        base.render(poseStack, vertexConsumer, packedLight, packedOverlay, red, green, blue, alpha);
    }

    @Override
    public ModelPart root() {
        return this.root;
    }
}