package com.yellowbrossproductions.illageandspillage.client.model;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.yellowbrossproductions.illageandspillage.entities.SpiritcallerEntity;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.HeadedModel;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;

import java.util.Calendar;

public class SpiritcallerModel<T extends Entity> extends EntityModel<T> implements HeadedModel {
    public static final ModelLayerLocation LAYER_LOCATION = new ModelLayerLocation(new ResourceLocation("illageandspillage", "spiritcaller"), "main");
    private final ModelPart body;
    private final ModelPart book;
    private final ModelPart left_leg;
    private final ModelPart right_leg;

    public SpiritcallerModel(ModelPart root) {
        this.body = root.getChild("body");
        this.book = root.getChild("book");
        this.left_leg = root.getChild("left_leg");
        this.right_leg = root.getChild("right_leg");
    }

    public static LayerDefinition createBodyLayer() {
        MeshDefinition meshdefinition = new MeshDefinition();
        PartDefinition partdefinition = meshdefinition.getRoot();

        PartDefinition body = partdefinition.addOrReplaceChild("body", CubeListBuilder.create().texOffs(0, 20).addBox(-4.0F, 0.0F, -3.0F, 8.0F, 12.0F, 6.0F, new CubeDeformation(0.0F))
                .texOffs(0, 38).addBox(-4.0F, 0.0F, -3.0F, 8.0F, 20.0F, 6.0F, new CubeDeformation(0.25F)), PartPose.offset(0.0F, -4.0F, 0.0F));

        PartDefinition head = body.addOrReplaceChild("head", CubeListBuilder.create().texOffs(0, 0).addBox(-4.0F, -10.0F, -4.0F, 8.0F, 10.0F, 8.0F, new CubeDeformation(0.0F))
                .texOffs(24, 0).addBox(-1.0F, -3.0F, -6.0F, 2.0F, 4.0F, 2.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 0.0F, 0.0F));

        PartDefinition birthday = head.addOrReplaceChild("birthday", CubeListBuilder.create().texOffs(138, 120).addBox(-2.0F, -9.3333F, 6.0833F, 4.0F, 3.0F, 4.0F, new CubeDeformation(0.0F))
                .texOffs(126, 120).addBox(-1.5F, -12.3333F, 6.5833F, 3.0F, 3.0F, 3.0F, new CubeDeformation(0.0F))
                .texOffs(154, 117).addBox(0.0F, -15.3333F, 6.5833F, 0.0F, 3.0F, 3.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, -3.6667F, -8.0833F));

        birthday.addOrReplaceChild("thingy", CubeListBuilder.create().texOffs(154, 120).addBox(-1.5F, -15.3333F, 8.0F, 3.0F, 3.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 0.0F, 0.0F));

        PartDefinition halohead = body.addOrReplaceChild("halohead", CubeListBuilder.create(), PartPose.offset(0.0F, 0.0F, 0.0F));

        halohead.addOrReplaceChild("halo", CubeListBuilder.create().texOffs(80, 115).addBox(-6.0F, -1.0F, -6.0F, 12.0F, 1.0F, 12.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, -12.0F, 0.0F, 0.2618F, 0.0F, -0.1745F));

        PartDefinition right_arm = body.addOrReplaceChild("right_arm", CubeListBuilder.create().texOffs(56, 44).addBox(-3.0F, -2.0F, -2.0F, 4.0F, 16.0F, 4.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(-5.0F, 2.0F, 0.0F, 0.0F, -0.4363F, 0.7854F));

        right_arm.addOrReplaceChild("magic1", CubeListBuilder.create().texOffs(80, 0).addBox(-8.0F, 0.0F, -8.0F, 16.0F, 0.0F, 16.0F, new CubeDeformation(0.0F)), PartPose.offset(-3.0F, 16.0F, 0.0F));

        PartDefinition hand1 = right_arm.addOrReplaceChild("hand1", CubeListBuilder.create().texOffs(100, 51).addBox(-11.0F, -3.0F, -4.0F, 22.0F, 24.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offset(-1.0F, 12.0F, 0.0F));

        PartDefinition finger1 = hand1.addOrReplaceChild("finger1", CubeListBuilder.create().texOffs(132, 0).addBox(-3.0F, 0.0F, -4.0F, 6.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(-9.0F, 21.0F, 0.0F, -1.5708F, 0.0F, 0.0F));

        PartDefinition fingersmaller1 = finger1.addOrReplaceChild("fingersmaller1", CubeListBuilder.create().texOffs(132, 0).addBox(-3.0F, 0.0F, -4.0F, 6.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 8.0F, 0.0F, -1.5708F, 0.0F, 0.0F));

        fingersmaller1.addOrReplaceChild("fingersmallest1", CubeListBuilder.create().texOffs(132, 0).addBox(-3.0F, 0.0F, -4.0F, 6.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 8.0F, 0.0F));

        PartDefinition finger5 = hand1.addOrReplaceChild("finger5", CubeListBuilder.create().texOffs(132, 0).addBox(-3.0F, 0.0F, -4.0F, 6.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(-11.0F, 10.0F, -4.0F, -1.5708F, 0.0F, 1.5708F));

        PartDefinition fingersmaller5 = finger5.addOrReplaceChild("fingersmaller5", CubeListBuilder.create().texOffs(132, 0).addBox(-3.0F, 0.0F, -4.0F, 6.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 8.0F, 0.0F, -1.5708F, 0.0F, 0.0F));

        fingersmaller5.addOrReplaceChild("fingersmallest5", CubeListBuilder.create().texOffs(132, 0).addBox(-3.0F, 0.0F, -4.0F, 6.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 8.0F, 0.0F));

        PartDefinition finger2 = hand1.addOrReplaceChild("finger2", CubeListBuilder.create().texOffs(132, 0).addBox(-3.0F, 0.0F, -4.0F, 6.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(-3.0F, 21.0F, 0.0F, -1.5708F, 0.0F, 0.0F));

        PartDefinition fingersmaller2 = finger2.addOrReplaceChild("fingersmaller2", CubeListBuilder.create().texOffs(132, 0).addBox(-3.0F, 0.0F, -4.0F, 6.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 8.0F, 0.0F, -1.5708F, 0.0F, 0.0F));

        fingersmaller2.addOrReplaceChild("fingersmallest2", CubeListBuilder.create().texOffs(132, 0).addBox(-3.0F, 0.0F, -4.0F, 6.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 8.0F, 0.0F));

        PartDefinition finger3 = hand1.addOrReplaceChild("finger3", CubeListBuilder.create().texOffs(132, 0).addBox(-3.0F, 0.0F, -4.0F, 6.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(3.0F, 21.0F, 0.0F, -1.5708F, 0.0F, 0.0F));

        PartDefinition fingersmaller3 = finger3.addOrReplaceChild("fingersmaller3", CubeListBuilder.create().texOffs(132, 0).addBox(-3.0F, 0.0F, -4.0F, 6.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 8.0F, 0.0F, -1.5708F, 0.0F, 0.0F));

        fingersmaller3.addOrReplaceChild("fingersmallest3", CubeListBuilder.create().texOffs(132, 0).addBox(-3.0F, 0.0F, -4.0F, 6.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 8.0F, 0.0F));

        PartDefinition finger4 = hand1.addOrReplaceChild("finger4", CubeListBuilder.create().texOffs(132, 0).addBox(-3.0F, 0.0F, -4.0F, 6.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(9.0F, 21.0F, 0.0F, -1.5708F, 0.0F, 0.0F));

        PartDefinition fingersmaller4 = finger4.addOrReplaceChild("fingersmaller4", CubeListBuilder.create().texOffs(132, 0).addBox(-3.0F, 0.0F, -4.0F, 6.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 8.0F, 0.0F, -1.5708F, 0.0F, 0.0F));

        fingersmaller4.addOrReplaceChild("fingersmallest4", CubeListBuilder.create().texOffs(132, 0).addBox(-3.0F, 0.0F, -4.0F, 6.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 8.0F, 0.0F));

        PartDefinition left_arm = body.addOrReplaceChild("left_arm", CubeListBuilder.create().texOffs(40, 44).mirror().addBox(-1.0F, -2.0F, -2.0F, 4.0F, 16.0F, 4.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offsetAndRotation(5.0F, 2.0F, 0.0F, 0.0F, 0.4363F, -0.7854F));

        left_arm.addOrReplaceChild("magic2", CubeListBuilder.create().texOffs(80, 16).addBox(-8.0F, 0.0F, -8.0F, 16.0F, 0.0F, 16.0F, new CubeDeformation(0.0F)), PartPose.offset(1.0F, 16.0F, 0.0F));

        PartDefinition hand2 = left_arm.addOrReplaceChild("hand2", CubeListBuilder.create().texOffs(100, 83).addBox(-11.0F, -3.0F, -4.0F, 22.0F, 24.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offset(1.0F, 12.0F, 0.0F));

        PartDefinition finger6 = hand2.addOrReplaceChild("finger6", CubeListBuilder.create().texOffs(132, 32).addBox(-3.0F, 0.0F, -4.0F, 6.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(-9.0F, 21.0F, 0.0F, -1.5708F, 0.0F, 0.0F));

        PartDefinition fingersmaller6 = finger6.addOrReplaceChild("fingersmaller6", CubeListBuilder.create().texOffs(132, 32).addBox(-3.0F, 0.0F, -4.0F, 6.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 8.0F, 0.0F, -1.5708F, 0.0F, 0.0F));

        fingersmaller6.addOrReplaceChild("fingersmallest6", CubeListBuilder.create().texOffs(132, 32).addBox(-3.0F, 0.0F, -4.0F, 6.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 8.0F, 0.0F));

        PartDefinition finger7 = hand2.addOrReplaceChild("finger7", CubeListBuilder.create().texOffs(132, 32).addBox(-3.0F, 0.0F, -4.0F, 6.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(11.0F, 10.0F, -4.0F, -1.5708F, 0.0F, -1.5708F));

        PartDefinition fingersmaller7 = finger7.addOrReplaceChild("fingersmaller7", CubeListBuilder.create().texOffs(132, 32).addBox(-3.0F, 0.0F, -4.0F, 6.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 8.0F, 0.0F, -1.5708F, 0.0F, 0.0F));

        fingersmaller7.addOrReplaceChild("fingersmallest7", CubeListBuilder.create().texOffs(132, 32).addBox(-3.0F, 0.0F, -4.0F, 6.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 8.0F, 0.0F));

        PartDefinition finger8 = hand2.addOrReplaceChild("finger8", CubeListBuilder.create().texOffs(132, 32).addBox(-3.0F, 0.0F, -4.0F, 6.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(-3.0F, 21.0F, 0.0F, -1.5708F, 0.0F, 0.0F));

        PartDefinition fingersmaller8 = finger8.addOrReplaceChild("fingersmaller8", CubeListBuilder.create().texOffs(132, 32).addBox(-3.0F, 0.0F, -4.0F, 6.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 8.0F, 0.0F, -1.5708F, 0.0F, 0.0F));

        fingersmaller8.addOrReplaceChild("fingersmallest8", CubeListBuilder.create().texOffs(132, 32).addBox(-3.0F, 0.0F, -4.0F, 6.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 8.0F, 0.0F));

        PartDefinition finger9 = hand2.addOrReplaceChild("finger9", CubeListBuilder.create().texOffs(132, 32).addBox(-3.0F, 0.0F, -4.0F, 6.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(3.0F, 21.0F, 0.0F, -1.5708F, 0.0F, 0.0F));

        PartDefinition fingersmaller9 = finger9.addOrReplaceChild("fingersmaller9", CubeListBuilder.create().texOffs(132, 32).addBox(-3.0F, 0.0F, -4.0F, 6.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 8.0F, 0.0F, -1.5708F, 0.0F, 0.0F));

        fingersmaller9.addOrReplaceChild("fingersmallest9", CubeListBuilder.create().texOffs(132, 32).addBox(-3.0F, 0.0F, -4.0F, 6.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 8.0F, 0.0F));

        PartDefinition finger10 = hand2.addOrReplaceChild("finger10", CubeListBuilder.create().texOffs(132, 32).addBox(-3.0F, 0.0F, -4.0F, 6.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(9.0F, 21.0F, 0.0F, -1.5708F, 0.0F, 0.0F));

        PartDefinition fingersmaller10 = finger10.addOrReplaceChild("fingersmaller10", CubeListBuilder.create().texOffs(132, 32).addBox(-3.0F, 0.0F, -4.0F, 6.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 8.0F, 0.0F, -1.5708F, 0.0F, 0.0F));

        fingersmaller10.addOrReplaceChild("fingersmallest10", CubeListBuilder.create().texOffs(132, 32).addBox(-3.0F, 0.0F, -4.0F, 6.0F, 8.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 8.0F, 0.0F));

        PartDefinition wing1 = body.addOrReplaceChild("wing1", CubeListBuilder.create().texOffs(0, 96).addBox(0.0F, -24.0F, 0.0F, 10.0F, 32.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offset(4.0F, 0.0F, 3.0F));

        PartDefinition wing_small1 = wing1.addOrReplaceChild("wing_small1", CubeListBuilder.create().texOffs(20, 96).addBox(0.0F, -20.0F, 0.0F, 10.0F, 32.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offset(10.0F, -4.0F, 0.0F));

        PartDefinition wing_smaller1 = wing_small1.addOrReplaceChild("wing_smaller1", CubeListBuilder.create().texOffs(40, 96).addBox(0.0F, -20.0F, 0.0F, 10.0F, 32.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offset(10.0F, 0.0F, 0.0F));

        wing_smaller1.addOrReplaceChild("wing_smallest1", CubeListBuilder.create().texOffs(60, 96).addBox(0.0F, -20.0F, 0.0F, 10.0F, 32.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offset(10.0F, 0.0F, 0.0F));

        PartDefinition wing2 = body.addOrReplaceChild("wing2", CubeListBuilder.create().texOffs(0, 64).addBox(0.0F, -24.0F, 0.0F, 10.0F, 32.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(-4.0F, 0.0F, 3.0F, 0.0F, 3.1416F, 0.0F));

        PartDefinition wing_small2 = wing2.addOrReplaceChild("wing_small2", CubeListBuilder.create().texOffs(20, 64).addBox(0.0F, -20.0F, 0.0F, 10.0F, 32.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offset(10.0F, -4.0F, 0.0F));

        PartDefinition wing_smaller2 = wing_small2.addOrReplaceChild("wing_smaller2", CubeListBuilder.create().texOffs(40, 64).addBox(0.0F, -20.0F, 0.0F, 10.0F, 32.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offset(10.0F, 0.0F, 0.0F));

        wing_smaller2.addOrReplaceChild("wing_smallest2", CubeListBuilder.create().texOffs(60, 64).addBox(0.0F, -20.0F, 0.0F, 10.0F, 32.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offset(10.0F, 0.0F, 0.0F));

        PartDefinition arms = body.addOrReplaceChild("arms", CubeListBuilder.create(), PartPose.offset(0.0F, 2.5F, 0.3F));

        PartDefinition arms_rotation = arms.addOrReplaceChild("arms_rotation", CubeListBuilder.create().texOffs(56, 20).addBox(-8.0F, 0.0F, -2.05F, 4.0F, 12.0F, 4.0F, new CubeDeformation(0.0F))
                .texOffs(40, 36).mirror().addBox(-4.0F, 8.0F, -2.05F, 8.0F, 4.0F, 4.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offsetAndRotation(0.0F, -2.0F, 0.05F, -0.5236F, 0.0F, 0.0F));

        arms_rotation.addOrReplaceChild("arms_flipped", CubeListBuilder.create().texOffs(40, 20).addBox(4.0F, 0.0F, -2.05F, 4.0F, 12.0F, 4.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 0.0F, 0.0F));

        body.addOrReplaceChild("left_leg2", CubeListBuilder.create().texOffs(38, 0).mirror().addBox(-2.0F, 0.0F, -2.0F, 4.0F, 16.0F, 4.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offset(2.0F, 12.0F, 0.0F));

        body.addOrReplaceChild("right_leg2", CubeListBuilder.create().texOffs(54, 0).addBox(-2.0F, 0.0F, -2.0F, 4.0F, 16.0F, 4.0F, new CubeDeformation(0.0F)), PartPose.offset(-2.0F, 12.0F, 0.0F));

        PartDefinition book = partdefinition.addOrReplaceChild("book", CubeListBuilder.create(), PartPose.offsetAndRotation(0.0F, 4.0F, -12.0F, -2.618F, 0.0F, 0.0F));

        PartDefinition cover_left = book.addOrReplaceChild("cover_left", CubeListBuilder.create(), PartPose.offsetAndRotation(-1.0F, 0.0F, 0.0F, 0.0F, -0.2618F, 0.0F));

        cover_left.addOrReplaceChild("cover_left_rotation", CubeListBuilder.create().texOffs(110, 32).addBox(-3.0F, -5.0F, 0.0F, 6.0F, 10.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(-3.0F, 0.0F, 0.0F, 0.0F, 0.0F, -3.1416F));

        PartDefinition cover_right = book.addOrReplaceChild("cover_right", CubeListBuilder.create(), PartPose.offsetAndRotation(1.0F, 0.0F, 0.0F, 0.0F, 0.2618F, 0.0F));

        cover_right.addOrReplaceChild("cover_right_rotation", CubeListBuilder.create().texOffs(94, 32).addBox(-3.0F, -5.0F, 0.0F, 6.0F, 10.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(3.0F, 0.0F, 0.0F, 0.0F, 0.0F, -3.1416F));

        PartDefinition book_spine = book.addOrReplaceChild("book_spine", CubeListBuilder.create(), PartPose.offset(0.0F, 0.0F, 0.0F));

        book_spine.addOrReplaceChild("spine_rotation", CubeListBuilder.create().texOffs(106, 32).addBox(-1.0F, -5.0F, 0.0F, 2.0F, 10.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 0.0F, 0.0F, 3.1416F, 0.0F, 0.0F));

        PartDefinition pages_left = book.addOrReplaceChild("pages_left", CubeListBuilder.create(), PartPose.offsetAndRotation(0.0F, 0.0F, -1.075F, 0.0F, -0.2618F, 0.0F));

        pages_left.addOrReplaceChild("page_left_rotation", CubeListBuilder.create().texOffs(106, 42).addBox(-2.5F, -4.0F, -0.5F, 5.0F, 8.0F, 1.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(-2.5F, 0.0F, 0.475F, 0.0F, 0.0F, -3.1416F));

        PartDefinition pages_right = book.addOrReplaceChild("pages_right", CubeListBuilder.create(), PartPose.offsetAndRotation(0.0F, 0.0F, -0.125F, 0.0F, 0.2618F, 0.0F));

        pages_right.addOrReplaceChild("page_right_rotation", CubeListBuilder.create().texOffs(94, 42).addBox(-2.5F, -4.0F, -0.5F, 5.0F, 8.0F, 1.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(2.5F, 0.0F, -0.475F, 0.0F, 3.1416F, -3.1416F));

        PartDefinition flipping_page_left = book.addOrReplaceChild("flipping_page_left", CubeListBuilder.create(), PartPose.offsetAndRotation(0.0F, 0.0F, -1.075F, 0.0F, -0.2618F, 0.0F));

        flipping_page_left.addOrReplaceChild("flip_left_rotation", CubeListBuilder.create().texOffs(118, 42).addBox(-2.5F, -4.0F, 0.0F, 5.0F, 8.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(-2.5F, 0.0F, -0.025F, 0.0F, 0.0F, -3.1416F));

        PartDefinition flipping_page_right = book.addOrReplaceChild("flipping_page_right", CubeListBuilder.create(), PartPose.offsetAndRotation(0.0F, 0.0F, -1.125F, 0.0F, 0.2618F, 0.0F));

        flipping_page_right.addOrReplaceChild("flip_right_rotation", CubeListBuilder.create().texOffs(118, 42).addBox(-2.5F, -4.0F, 0.0F, 5.0F, 8.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(2.5F, 0.0F, 0.025F, 0.0F, 3.1416F, -3.1416F));

        partdefinition.addOrReplaceChild("left_leg", CubeListBuilder.create().texOffs(38, 0).mirror().addBox(-2.0F, 0.0F, -2.0F, 4.0F, 16.0F, 4.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offset(2.0F, 8.0F, 0.0F));

        partdefinition.addOrReplaceChild("right_leg", CubeListBuilder.create().texOffs(54, 0).addBox(-2.0F, 0.0F, -2.0F, 4.0F, 16.0F, 4.0F, new CubeDeformation(0.0F)), PartPose.offset(-2.0F, 8.0F, 0.0F));

        return LayerDefinition.create(meshdefinition, 160, 128);
    }

    public void setupAnim(T entity, float limbSwing, float limbSwingAmount, float ageInTicks, float netHeadYaw, float headPitch) {
        float f3 = ageInTicks / 60.0F;
        ModelPart wing1 = this.body.getChild("wing1");
        ModelPart wing_small1 = this.body.getChild("wing1").getChild("wing_small1");
        ModelPart wing_smaller1 = this.body.getChild("wing1").getChild("wing_small1").getChild("wing_smaller1");
        ModelPart wing_smallest1 = this.body.getChild("wing1").getChild("wing_small1").getChild("wing_smaller1").getChild("wing_smallest1");
        ModelPart wing2 = this.body.getChild("wing2");
        ModelPart wing_small2 = this.body.getChild("wing2").getChild("wing_small2");
        ModelPart wing_smaller2 = this.body.getChild("wing2").getChild("wing_small2").getChild("wing_smaller2");
        ModelPart wing_smallest2 = this.body.getChild("wing2").getChild("wing_small2").getChild("wing_smaller2").getChild("wing_smallest2");
        this.book.y = Mth.sin(f3 * 5.0F) * 0.5F;
        if (entity instanceof SpiritcallerEntity spiritcaller) {
            Calendar calendar = Calendar.getInstance();
            this.body.getChild("head").getChild("birthday").visible = calendar.get(Calendar.MONTH) == Calendar.FEBRUARY && calendar.get(Calendar.DAY_OF_MONTH) < 8;

            this.body.getChild("head").yRot = netHeadYaw * 0.017453292F;
            this.body.getChild("head").xRot = -0.0873F + headPitch * 0.017453292F;
            this.body.getChild("halohead").yRot = netHeadYaw * 0.017453292F;
            this.body.getChild("halohead").xRot = -0.0873F + headPitch * 0.017453292F;
            this.body.getChild("halohead").getChild("halo").yRot = ageInTicks * 10.0F * 0.017453292F;
            this.body.getChild("right_arm").getChild("magic1").yRot = ageInTicks * 15.0F * 0.017453292F;
            this.body.getChild("left_arm").getChild("magic2").yRot = ageInTicks * -15.0F * 0.017453292F;
            if (this.riding) {
                this.right_leg.xRot = -1.4137167F;
                this.right_leg.yRot = 0.31415927F;
                this.right_leg.zRot = 0.07853982F;
                this.left_leg.xRot = -1.4137167F;
                this.left_leg.yRot = -0.31415927F;
                this.left_leg.zRot = -0.07853982F;
            } else {
                if (spiritcaller.isActive()) {
                    this.right_leg.xRot = 0.0F;
                    this.left_leg.xRot = 0.0F;
                } else {
                    this.right_leg.xRot = Mth.cos(limbSwing * 0.6662F) * 1.4F * limbSwingAmount * 0.5F;
                    this.left_leg.xRot = Mth.cos(limbSwing * 0.6662F + 3.1415927F) * 1.4F * limbSwingAmount * 0.5F;
                }

                this.right_leg.yRot = 0.0F;
                this.right_leg.zRot = 0.0F;
                this.left_leg.yRot = 0.0F;
                this.left_leg.zRot = 0.0F;
            }

            this.body.y = -4.0F;
            this.body.x = 0.0F;
            this.right_leg.y = 8.0F;
            this.left_leg.y = 8.0F;
            this.left_leg.z = 0.0F;
            wing1.xRot = 0.0F;
            wing2.xRot = 0.0F;
            wing1.zRot = 0.0F;
            wing2.zRot = 0.0F;
            wing_small1.yRot = 0.0F;
            wing_smaller1.yRot = 0.0F;
            wing_smallest1.yRot = 0.0F;
            wing_small2.yRot = 0.0F;
            wing_smaller2.yRot = 0.0F;
            wing_smallest2.yRot = 0.0F;
            float f = ageInTicks - (float) spiritcaller.tickCount;
            float f1 = spiritcaller.getWingsAnimationScale(f);
            f1 *= f1;
            float f4 = -Mth.sin(f1 / 5.0F / 4.0F) * 2.0F;
            float f5 = Math.min(f4, 0.0F);
            this.book.visible = spiritcaller.isRitual();
            if (spiritcaller.isRitual()) {
                this.body.y = -4.0F + Mth.cos(f3 * 20.0F) * 2.0F;
                this.body.x = Mth.sin(f3 * 20.0F) * 0.6F;
                this.body.getChild("right_arm").zRot = 0.7854F + Mth.sin(f3 * 14.0F) * 0.3F;
                this.body.getChild("left_arm").zRot = -0.7854F + Mth.sin(f3 * 14.0F) * -0.3F;
            }

            this.body.getChild("right_leg2").visible = false;
            this.body.getChild("left_leg2").visible = false;
            this.body.getChild("right_arm").getChild("hand1").visible = false;
            this.body.getChild("left_arm").getChild("hand2").visible = false;
            if (spiritcaller.isActive()) {
                this.body.getChild("halohead").visible = true;
                this.body.getChild("right_arm").getChild("magic1").visible = true;
                this.body.getChild("left_arm").getChild("magic2").visible = true;
                this.body.getChild("wing1").visible = true;
                this.body.getChild("wing2").visible = true;
                int frame = spiritcaller.getWingsFrames();
                this.body.getChild("right_arm").zRot = 0.7854F + Mth.sin(f3 * 7.0F) * 0.1F;
                this.body.getChild("left_arm").zRot = -0.7854F + Mth.sin(f3 * 7.0F) * -0.1F;
                if (!spiritcaller.isDeadOrDying()) {
                    if (spiritcaller.getWingsFrames() <= 5) {
                        this.body.y = -4.0F - f5;
                        this.right_leg.y = 8.0F - f5;
                        this.left_leg.y = 5.0F - f5;
                        this.left_leg.z = -4.0F;
                        wing1.xRot = 0.31415927F * (float) (frame);
                        wing2.xRot = -0.31415927F * (float) (frame);
                        wing1.zRot = -0.15707964F * (float) (frame);
                        wing2.zRot = 0.15707964F * (float) (frame);
                        wing_small1.yRot = -0.08726646F * (float) (frame);
                        wing_smaller1.yRot = -0.08726646F * (float) (frame);
                        wing_smallest1.yRot = -0.08726646F * (float) (frame);
                        wing_small2.yRot = 0.08726646F * (float) (frame);
                        wing_smaller2.yRot = 0.08726646F * (float) (frame);
                        wing_smallest2.yRot = 0.08726646F * (float) (frame);
                    } else if (spiritcaller.getWingsFrames() <= 10) {
                        this.body.y = -4.0F - f5;
                        this.right_leg.y = 8.0F - f5;
                        this.left_leg.y = 5.0F - f5;
                        this.left_leg.z = -4.0F;
                        wing1.xRot = 1.5707964F;
                        wing2.xRot = -1.5707964F;
                        wing1.zRot = -0.7853982F;
                        wing2.zRot = 0.7853982F;
                        wing_small1.yRot = -0.43633232F;
                        wing_smaller1.yRot = -0.43633232F;
                        wing_smallest1.yRot = -0.43633232F;
                        wing_small2.yRot = 0.43633232F;
                        wing_smaller2.yRot = 0.43633232F;
                        wing_smallest2.yRot = 0.43633232F;
                    } else if (spiritcaller.getWingsFrames() <= 12) {
                        this.body.y = -4.0F - f5;
                        this.right_leg.y = 8.0F - f5;
                        this.left_leg.y = 5.0F - f5;
                        this.left_leg.z = -4.0F;
                        wing1.xRot = 1.5707964F;
                        wing2.xRot = -1.5707964F;
                        wing1.zRot = -0.7853982F - -0.61086524F * (float) (frame - 10);
                        wing2.zRot = 0.7853982F - 0.61086524F * (float) (frame - 10);
                        wing_small1.yRot = -0.43633232F;
                        wing_smaller1.yRot = -0.43633232F;
                        wing_smallest1.yRot = -0.43633232F;
                        wing_small2.yRot = 0.43633232F;
                        wing_smaller2.yRot = 0.43633232F;
                        wing_smallest2.yRot = 0.43633232F;
                    } else if (spiritcaller.getWingsFrames() <= 15) {
                        this.body.y = -4.0F - f5;
                        this.right_leg.y = 8.0F - f5;
                        this.left_leg.y = 5.0F - f5;
                        this.left_leg.z = -4.0F;
                        wing1.xRot = 1.5707964F;
                        wing2.xRot = -1.5707964F;
                        wing1.zRot = 0.43633232F - -0.05817764F * (float) (frame - 12);
                        wing2.zRot = -0.43633232F - 0.05817764F * (float) (frame - 12);
                        wing_small1.yRot = -0.43633232F - -0.29088822F * (float) (frame - 12);
                        wing_smaller1.yRot = -0.43633232F - -0.29088822F * (float) (frame - 12);
                        wing_smallest1.yRot = -0.43633232F - -0.29088822F * (float) (frame - 12);
                        wing_small2.yRot = 0.43633232F - 0.29088822F * (float) (frame - 12);
                        wing_smaller2.yRot = 0.43633232F - 0.29088822F * (float) (frame - 12);
                        wing_smallest2.yRot = 0.43633232F - 0.29088822F * (float) (frame - 12);
                    } else if (spiritcaller.getWingsFrames() <= 20) {
                        this.body.y = -4.0F - f5;
                        this.right_leg.y = 8.0F - f5;
                        this.left_leg.y = 5.0F - f5;
                        this.left_leg.z = -4.0F;
                        wing1.xRot = 1.5707964F;
                        wing2.xRot = -1.5707964F;
                        wing1.zRot = 0.61086524F;
                        wing2.zRot = -0.61086524F;
                        wing_small1.yRot = 0.43633232F;
                        wing_smaller1.yRot = 0.43633232F;
                        wing_smallest1.yRot = 0.43633232F;
                        wing_small2.yRot = -0.43633232F;
                        wing_smaller2.yRot = -0.43633232F;
                        wing_smallest2.yRot = -0.43633232F;
                    } else if (spiritcaller.getWingsFrames() <= 25) {
                        this.body.y = -4.0F - f5;
                        this.right_leg.y = 8.0F - f5;
                        this.left_leg.y = 5.0F - f5;
                        this.left_leg.z = -4.0F;
                        wing1.xRot = 1.5707964F - 0.31415927F * (float) (frame - 20);
                        wing2.xRot = -1.5707964F - -0.31415927F * (float) (frame - 20);
                        wing1.zRot = 0.61086524F - 0.12217305F * (float) (frame - 20);
                        wing2.zRot = -0.61086524F - -0.12217305F * (float) (frame - 20);
                        wing_small1.yRot = 0.43633232F - 0.08726646F * (float) (frame - 20);
                        wing_smaller1.yRot = 0.43633232F - 0.08726646F * (float) (frame - 20);
                        wing_smallest1.yRot = 0.43633232F - 0.08726646F * (float) (frame - 20);
                        wing_small2.yRot = -0.43633232F - -0.08726646F * (float) (frame - 20);
                        wing_smaller2.yRot = -0.43633232F - -0.08726646F * (float) (frame - 20);
                        wing_smallest2.yRot = -0.43633232F - -0.08726646F * (float) (frame - 20);
                    }
                } else {
                    wing1.xRot = -0.7854F;
                    wing1.zRot = 0.7854F;
                    wing2.xRot = 0.7854F;
                    wing2.zRot = -0.7854F;
                }
            } else {
                this.body.getChild("halohead").visible = false;
                this.body.getChild("right_arm").getChild("magic1").visible = false;
                this.body.getChild("left_arm").getChild("magic2").visible = false;
                this.body.getChild("wing1").visible = false;
                this.body.getChild("wing2").visible = false;
            }

            if (spiritcaller.isArmsUpward()) {
                this.body.getChild("right_arm").zRot = 1.9198F + Mth.sin(f3 * 14.0F) * 0.3F;
                this.body.getChild("left_arm").zRot = -1.9198F + Mth.sin(f3 * 14.0F) * -0.3F;
            }

            if (spiritcaller.isSpinning()) {
                this.body.getChild("right_arm").zRot = 1.5708F;
                this.body.getChild("left_arm").zRot = -1.5708F;
            }

            if (spiritcaller.isCharging()) {
                this.body.getChild("head").xRot = -1.5708F;
                this.body.getChild("halohead").xRot = -1.5708F;
                this.body.getChild("head").yRot = 0.0F;
                this.body.getChild("halohead").yRot = 0.0F;
                this.body.xRot = 1.5708F + headPitch * 0.017453292F;
                this.right_leg.visible = false;
                this.left_leg.visible = false;
                this.body.getChild("right_leg2").visible = true;
                this.body.getChild("left_leg2").visible = true;
                this.body.getChild("right_arm").xRot = 3.1416F;
                this.body.getChild("left_arm").xRot = 3.1416F;
                this.body.getChild("right_arm").yRot = 0.0F;
                this.body.getChild("left_arm").yRot = 0.0F;
                this.body.getChild("right_arm").zRot = 0.0F;
                this.body.getChild("left_arm").zRot = 0.0F;
            } else {
                this.body.xRot = 0.0F;
                this.right_leg.visible = true;
                this.left_leg.visible = true;
                this.body.getChild("right_arm").xRot = 0.0F;
                this.body.getChild("left_arm").xRot = 0.0F;
                this.body.getChild("right_arm").yRot = -0.4363F;
                this.body.getChild("left_arm").yRot = 0.4363F;
            }

            if (spiritcaller.isFaking() || spiritcaller.isClap() || spiritcaller.shouldShowSpiritHands() || spiritcaller.isShootingLaser()) {
                this.body.getChild("right_arm").getChild("magic1").visible = false;
                this.body.getChild("left_arm").getChild("magic2").visible = false;
            }

            if (!spiritcaller.isActive() && !spiritcaller.isRitual()) {
                this.body.getChild("right_arm").visible = false;
                this.body.getChild("left_arm").visible = false;
                this.body.getChild("arms").visible = true;
            } else {
                this.body.getChild("right_arm").visible = true;
                this.body.getChild("left_arm").visible = true;
                this.body.getChild("arms").visible = false;
            }

            if (spiritcaller.isClap()) {
                this.body.getChild("right_arm").xRot = -1.5707F;
                this.body.getChild("left_arm").xRot = -1.5707F;
            }

            if (spiritcaller.isDeadOrDying() && spiritcaller.isActive()) {
                this.body.getChild("right_arm").zRot = 1.2217F;
                this.body.getChild("left_arm").zRot = -1.2217F;
                this.right_leg.xRot = -0.3491F;
                this.left_leg.xRot = -0.3491F;
            }

            if (spiritcaller.isChargingLaser()) {
                this.body.getChild("right_arm").xRot = Mth.cos(ageInTicks * 0.6662F) * 0.25F;
                this.body.getChild("right_arm").yRot = 0.0F;
                this.body.getChild("right_arm").zRot = 2.3561945F;
            }

            if (spiritcaller.isShootingLaser()) {
                this.body.getChild("right_arm").xRot = -1.5707F;
                this.body.getChild("left_arm").xRot = -1.5707F;
            }

            this.body.getChild("right_arm").getChild("hand1").visible = spiritcaller.shouldShowSpiritHands();
            this.body.getChild("left_arm").getChild("hand2").visible = spiritcaller.shouldShowSpiritHands();
        }

    }

    public void renderToBuffer(PoseStack poseStack, VertexConsumer vertexConsumer, int packedLight, int packedOverlay, float red, float green, float blue, float alpha) {
        this.body.render(poseStack, vertexConsumer, packedLight, packedOverlay, red, green, blue, alpha);
        this.book.render(poseStack, vertexConsumer, packedLight, packedOverlay, red, green, blue, alpha);
        this.left_leg.render(poseStack, vertexConsumer, packedLight, packedOverlay, red, green, blue, alpha);
        this.right_leg.render(poseStack, vertexConsumer, packedLight, packedOverlay, red, green, blue, alpha);
    }

    public ModelPart getHead() {
        return this.body.getChild("head");
    }
}
