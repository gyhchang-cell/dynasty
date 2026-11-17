package com.yellowbrossproductions.illageandspillage.client.model;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.yellowbrossproductions.illageandspillage.IllageAndSpillage;
import com.yellowbrossproductions.illageandspillage.client.model.animation.FreakagerAnimation;
import com.yellowbrossproductions.illageandspillage.entities.FreakagerEntity;
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

public class FreakagerModel<T extends Entity> extends HierarchicalModel<T> implements CustomHeadedModel, ArmedModel {
    public static final ModelLayerLocation LAYER_LOCATION = new ModelLayerLocation(new ResourceLocation(IllageAndSpillage.MOD_ID, "freakager"), "main");
    private final ModelPart root;
    private final ModelPart villager;
    private final ModelPart all;

    public FreakagerModel(ModelPart root) {
        this.root = root;
        this.villager = root.getChild("villager");
        this.all = root.getChild("all");
    }

    public static LayerDefinition createBodyLayer() {
        MeshDefinition meshdefinition = new MeshDefinition();
        PartDefinition partdefinition = meshdefinition.getRoot();

        PartDefinition villager = partdefinition.addOrReplaceChild("villager", CubeListBuilder.create().texOffs(144, 20).addBox(-4.0F, -24.0F, -3.0F, 8.0F, 12.0F, 6.0F, new CubeDeformation(0.0F))
                .texOffs(128, 38).addBox(-4.0F, -24.0F, -3.0F, 8.0F, 18.0F, 6.0F, new CubeDeformation(0.25F)), PartPose.offset(0.0F, 24.0F, 0.0F));

        PartDefinition arms2 = villager.addOrReplaceChild("arms2", CubeListBuilder.create(), PartPose.offset(0.0F, -20.5F, 0.3F));

        PartDefinition arms_rotation2 = arms2.addOrReplaceChild("arms_rotation2", CubeListBuilder.create().texOffs(172, 22).addBox(-8.0F, 0.0F, -2.05F, 4.0F, 8.0F, 4.0F, new CubeDeformation(0.0F))
                .texOffs(168, 38).addBox(-4.0F, 4.0F, -2.05F, 8.0F, 4.0F, 4.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, -2.0F, 0.05F, -0.7505F, 0.0F, 0.0F));

        arms_rotation2.addOrReplaceChild("arms_flipped2", CubeListBuilder.create().texOffs(172, 22).mirror().addBox(4.0F, -24.0F, -2.05F, 4.0F, 8.0F, 4.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offset(0.0F, 24.0F, 0.0F));

        PartDefinition head2 = villager.addOrReplaceChild("head2", CubeListBuilder.create().texOffs(128, 0).addBox(-4.0F, -10.0F, -4.0F, 8.0F, 10.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, -24.0F, 0.0F));

        head2.addOrReplaceChild("nose2", CubeListBuilder.create().texOffs(152, 0).addBox(-1.0F, -1.0F, -6.0F, 2.0F, 4.0F, 2.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, -2.0F, 0.0F));

        PartDefinition birthday2 = head2.addOrReplaceChild("birthday2", CubeListBuilder.create().texOffs(77, 30).addBox(-2.0F, -9.3333F, 6.0833F, 4.0F, 3.0F, 4.0F, new CubeDeformation(0.0F))
                .texOffs(65, 30).addBox(-1.5F, -12.3333F, 6.5833F, 3.0F, 3.0F, 3.0F, new CubeDeformation(0.0F))
                .texOffs(90, 27).addBox(0.0F, -15.3333F, 6.5833F, 0.0F, 3.0F, 3.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, -3.6667F, -8.0833F));

        birthday2.addOrReplaceChild("thingy2", CubeListBuilder.create().texOffs(90, 30).addBox(-1.5F, -15.3333F, 8.0F, 3.0F, 3.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 0.0F, 0.0F));

        villager.addOrReplaceChild("left_leg3", CubeListBuilder.create().texOffs(128, 22).mirror().addBox(-2.0F, 0.0F, -2.0F, 4.0F, 12.0F, 4.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offset(2.0F, -12.0F, 0.0F));

        villager.addOrReplaceChild("right_leg3", CubeListBuilder.create().texOffs(128, 22).addBox(-2.0F, 0.0F, -2.0F, 4.0F, 12.0F, 4.0F, new CubeDeformation(0.0F)), PartPose.offset(-2.0F, -12.0F, 0.0F));

        PartDefinition all = partdefinition.addOrReplaceChild("all", CubeListBuilder.create(), PartPose.offset(0.0F, 24.0F, 0.0F));

        all.addOrReplaceChild("left_leg2", CubeListBuilder.create().texOffs(0, 22).mirror().addBox(-2.0F, 0.0F, -2.0F, 4.0F, 12.0F, 4.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offset(2.0F, -12.0F, 0.0F));

        all.addOrReplaceChild("right_leg2", CubeListBuilder.create().texOffs(0, 22).addBox(-2.0F, 0.0F, -2.0F, 4.0F, 12.0F, 4.0F, new CubeDeformation(0.0F)), PartPose.offset(-2.0F, -12.0F, 0.0F));

        PartDefinition body = all.addOrReplaceChild("body", CubeListBuilder.create().texOffs(16, 20).addBox(-4.0F, -11.0F, -3.0F, 8.0F, 12.0F, 6.0F, new CubeDeformation(0.0F))
                .texOffs(0, 38).addBox(-4.0F, -11.0F, -3.0F, 8.0F, 14.0F, 6.0F, new CubeDeformation(0.25F)), PartPose.offset(0.0F, -13.0F, 0.0F));

        PartDefinition arms = body.addOrReplaceChild("arms", CubeListBuilder.create(), PartPose.offset(0.0F, -7.5F, 0.3F));

        PartDefinition arms_rotation = arms.addOrReplaceChild("arms_rotation", CubeListBuilder.create().texOffs(44, 22).addBox(-8.0F, 0.0F, -2.05F, 4.0F, 8.0F, 4.0F, new CubeDeformation(0.0F))
                .texOffs(40, 38).addBox(-4.0F, 4.0F, -2.05F, 8.0F, 4.0F, 4.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, -2.0F, 0.05F, -0.7505F, 0.0F, 0.0F));

        arms_rotation.addOrReplaceChild("arms_flipped", CubeListBuilder.create().texOffs(44, 22).mirror().addBox(4.0F, -24.0F, -2.05F, 4.0F, 8.0F, 4.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offset(0.0F, 24.0F, 0.0F));

        body.addOrReplaceChild("left_arm", CubeListBuilder.create().texOffs(40, 46).mirror().addBox(-1.0F, -2.0F, -2.0F, 4.0F, 12.0F, 4.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offset(5.0F, -9.0F, 0.0F));

        PartDefinition right_arm = body.addOrReplaceChild("right_arm", CubeListBuilder.create().texOffs(40, 46).addBox(-3.0F, -2.0F, -2.0F, 4.0F, 12.0F, 4.0F, new CubeDeformation(0.0F)), PartPose.offset(-5.0F, -9.0F, 0.0F));

        right_arm.addOrReplaceChild("scythe", CubeListBuilder.create().texOffs(128, 76).addBox(-4.0F, -0.5F, -1.0F, 6.0F, 1.0F, 2.0F, new CubeDeformation(0.0F))
                .texOffs(138, 84).addBox(7.0F, -0.5F, -12.0F, 1.0F, 1.0F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(138, 86).addBox(6.0F, -0.5F, -11.0F, 3.0F, 1.0F, 2.0F, new CubeDeformation(0.0F))
                .texOffs(128, 79).addBox(4.0F, -0.5F, -9.0F, 3.0F, 1.0F, 4.0F, new CubeDeformation(0.0F))
                .texOffs(148, 86).addBox(2.0F, -0.5F, -5.0F, 3.0F, 1.0F, 2.0F, new CubeDeformation(0.0F))
                .texOffs(144, 76).addBox(0.0F, -0.5F, -3.0F, 4.0F, 1.0F, 2.0F, new CubeDeformation(0.0F))
                .texOffs(142, 79).addBox(-4.0F, -0.5F, 1.0F, 4.0F, 1.0F, 2.0F, new CubeDeformation(0.0F))
                .texOffs(128, 65).addBox(-6.0F, -0.5F, 3.0F, 3.0F, 1.0F, 6.0F, new CubeDeformation(0.0F))
                .texOffs(142, 82).addBox(-8.0F, -0.5F, 4.0F, 2.0F, 1.0F, 3.0F, new CubeDeformation(0.0F))
                .texOffs(148, 70).addBox(-10.0F, -0.5F, 3.0F, 2.0F, 1.0F, 3.0F, new CubeDeformation(0.0F))
                .texOffs(128, 88).addBox(-11.0F, -0.5F, 4.0F, 1.0F, 1.0F, 3.0F, new CubeDeformation(0.0F))
                .texOffs(128, 72).addBox(-4.0F, -0.5F, 9.0F, 7.0F, 1.0F, 3.0F, new CubeDeformation(0.0F))
                .texOffs(152, 82).addBox(3.0F, -0.5F, 9.0F, 3.0F, 1.0F, 2.0F, new CubeDeformation(0.0F))
                .texOffs(128, 63).addBox(-3.0F, -0.5F, 8.0F, 12.0F, 1.0F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(148, 74).addBox(6.0F, -0.5F, 7.0F, 4.0F, 1.0F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(154, 63).addBox(8.0F, -0.5F, 6.0F, 3.0F, 1.0F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(128, 84).addBox(-9.0F, -0.5F, 9.0F, 2.0F, 1.0F, 3.0F, new CubeDeformation(0.0F))
                .texOffs(146, 65).addBox(-7.0F, -0.5F, 7.0F, 1.0F, 1.0F, 4.0F, new CubeDeformation(0.0F))
                .texOffs(156, 89).addBox(-6.0F, -0.5F, 9.0F, 1.0F, 1.0F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(156, 89).addBox(0.0F, -0.5F, 1.0F, 1.0F, 1.0F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(156, 89).addBox(2.0F, -0.5F, -1.0F, 1.0F, 1.0F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(156, 89).addBox(5.0F, -0.5F, -5.0F, 1.0F, 1.0F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(156, 65).addBox(-3.0F, -0.5F, 7.0F, 1.0F, 1.0F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(156, 67).addBox(10.0F, -0.5F, 5.0F, 1.0F, 1.0F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(138, 84).addBox(-8.0F, -0.5F, 8.0F, 1.0F, 1.0F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(138, 84).addBox(1.0F, -0.5F, -4.0F, 1.0F, 1.0F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(152, 89).addBox(5.0F, -0.5F, -10.0F, 1.0F, 1.0F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(138, 84).addBox(3.0F, -0.5F, -6.0F, 1.0F, 1.0F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(156, 91).addBox(-3.0F, -0.5F, 3.0F, 1.0F, 1.0F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(156, 91).addBox(-5.0F, -0.5F, 2.0F, 1.0F, 1.0F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(136, 89).addBox(-6.0F, -0.5F, 0.0F, 1.0F, 1.0F, 3.0F, new CubeDeformation(0.0F))
                .texOffs(128, 92).addBox(-3.0F, -0.5F, -2.0F, 1.0F, 1.0F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(132, 92).addBox(-4.0F, -0.5F, -3.0F, 1.0F, 1.0F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(144, 90).addBox(7.0F, -0.5F, -9.0F, 1.0F, 1.0F, 2.0F, new CubeDeformation(0.0F))
                .texOffs(128, 68).addBox(6.0F, -0.5F, 9.0F, 2.0F, 1.0F, 1.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(-1.0F, 7.6F, -4.0F, -3.1416F, -0.7418F, 1.5708F));


        PartDefinition head = body.addOrReplaceChild("head", CubeListBuilder.create().texOffs(0, 0).addBox(-4.0F, -10.0F, -4.0F, 8.0F, 10.0F, 8.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, -11.0F, 0.0F));

        PartDefinition nose = head.addOrReplaceChild("nose", CubeListBuilder.create().texOffs(24, 0).addBox(-1.0F, -1.0F, -6.0F, 2.0F, 4.0F, 2.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, -2.0F, 0.0F));

        nose.addOrReplaceChild("mole", CubeListBuilder.create().texOffs(0, 0).addBox(0.0F, 3.0F, -6.75F, 1.0F, 1.0F, 1.0F, new CubeDeformation(-0.25F)), PartPose.offset(0.0F, -2.0F, 0.0F));

        PartDefinition hat = head.addOrReplaceChild("hat", CubeListBuilder.create().texOffs(64, 0).addBox(-8.0F, -1.0F, -8.0F, 16.0F, 1.0F, 16.0F, new CubeDeformation(0.0F))
                .texOffs(32, 0).addBox(-4.0F, -6.0F, -4.0F, 8.0F, 5.0F, 8.0F, new CubeDeformation(0.5F)), PartPose.offsetAndRotation(0.0F, -5.0F, 0.5F, 0.0873F, 0.0F, 0.0F));

        hat.addOrReplaceChild("hat_littlepiece", CubeListBuilder.create().texOffs(116, 0).addBox(-1.5F, -5.0F, -1.5F, 3.0F, 5.0F, 3.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, -5.0F, 0.0F, -0.5236F, 0.0F, 0.0F));

        hat.addOrReplaceChild("hat_littlepiece2", CubeListBuilder.create().texOffs(120, 4).addBox(1.5F, -7.0F, -1.5F, 0.0F, 7.0F, 4.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(3.0F, -0.5F, -1.0F, 0.0F, 0.1745F, 0.2618F));

        head.addOrReplaceChild("body_smaller", CubeListBuilder.create().texOffs(0, 58).addBox(-4.0F, -3.0F, -7.0F, 8.0F, 4.0F, 8.0F, new CubeDeformation(0.3F)), PartPose.offsetAndRotation(0.0F, -1.0F, 3.0F, 0.0873F, 0.0F, 0.0F));

        PartDefinition birthday = head.addOrReplaceChild("birthday", CubeListBuilder.create().texOffs(77, 21).addBox(-2.0F, -9.3333F, 6.0833F, 4.0F, 3.0F, 4.0F, new CubeDeformation(0.0F))
                .texOffs(65, 21).addBox(-1.5F, -12.3333F, 6.5833F, 3.0F, 3.0F, 3.0F, new CubeDeformation(0.0F))
                .texOffs(90, 18).addBox(0.0F, -15.3333F, 6.5833F, 0.0F, 3.0F, 3.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(1.0F, -4.6667F, -9.0833F, 0.0F, 0.0F, 0.1745F));

        birthday.addOrReplaceChild("thingy", CubeListBuilder.create().texOffs(90, 21).addBox(-1.5F, -15.3333F, 8.0F, 3.0F, 3.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 0.0F, 0.0F));

        body.addOrReplaceChild("left_leg", CubeListBuilder.create().texOffs(0, 22).mirror().addBox(-2.0F, 0.0F, -2.0F, 4.0F, 12.0F, 4.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offset(2.0F, 1.0F, 0.0F));

        body.addOrReplaceChild("right_leg", CubeListBuilder.create().texOffs(0, 22).addBox(-2.0F, 0.0F, -2.0F, 4.0F, 12.0F, 4.0F, new CubeDeformation(0.0F)), PartPose.offset(-2.0F, 1.0F, 0.0F));

        return LayerDefinition.create(meshdefinition, 196, 128);
    }

    @Override
    public void setupAnim(T entity, float limbSwing, float limbSwingAmount, float ageInTicks, float netHeadYaw, float headPitch) {
        this.root().getAllParts().forEach(ModelPart::resetPose);
        ModelPart head = this.all.getChild("body").getChild("head");
        ModelPart left_arm = this.all.getChild("body").getChild("left_arm");
        ModelPart right_arm = this.all.getChild("body").getChild("right_arm");
        ModelPart arms = this.all.getChild("body").getChild("arms");
        ModelPart scythe = this.all.getChild("body").getChild("right_arm").getChild("scythe");

        if (entity instanceof FreakagerEntity freakager) {
            this.all.getChild("right_leg2").xRot = Mth.cos(limbSwing * 0.6662F) * 1.4F * limbSwingAmount * 0.5F;
            this.all.getChild("left_leg2").xRot = Mth.cos(limbSwing * 0.6662F + (float) Math.PI) * 1.4F * limbSwingAmount * 0.5F;
            this.all.getChild("body").getChild("right_leg").visible = false;
            this.all.getChild("body").getChild("left_leg").visible = false;

            this.animate(freakager.getAnimationState("intro1"), FreakagerAnimation.INTRO1, ageInTicks, freakager.getAnimationSpeed());
            this.animate(freakager.getAnimationState("intro2"), FreakagerAnimation.INTRO2, ageInTicks, freakager.getAnimationSpeed());
            this.animate(freakager.getAnimationState("intro3"), FreakagerAnimation.INTRO3, ageInTicks, freakager.getAnimationSpeed());
            this.animate(freakager.getAnimationState("bombs"), FreakagerAnimation.BOMBS, ageInTicks, freakager.getAnimationSpeed());
            this.animate(freakager.getAnimationState("minions"), FreakagerAnimation.MINIONS, ageInTicks, freakager.getAnimationSpeed());
            this.animate(freakager.getAnimationState("axes_start"), FreakagerAnimation.AXES_START, ageInTicks, freakager.getAnimationSpeed());
            this.animate(freakager.getAnimationState("axes_normal"), FreakagerAnimation.AXES_NORMAL, ageInTicks, freakager.getAnimationSpeed());
            this.animate(freakager.getAnimationState("axes_angry"), FreakagerAnimation.AXES_ANGRY, ageInTicks, freakager.getAnimationSpeed());
            this.animate(freakager.getAnimationState("potions"), FreakagerAnimation.POTIONS, ageInTicks, freakager.getAnimationSpeed());
            this.animate(freakager.getAnimationState("scythe"), FreakagerAnimation.SCYTHE, ageInTicks, freakager.getAnimationSpeed());
            this.animate(freakager.getAnimationState("catch"), FreakagerAnimation.CATCH, ageInTicks, freakager.getAnimationSpeed());
            this.animate(freakager.getAnimationState("trickortreat"), FreakagerAnimation.TRICKORTREAT, ageInTicks, freakager.getAnimationSpeed());
            this.animate(freakager.getAnimationState("anticheese"), FreakagerAnimation.ANTICHEESE, ageInTicks, freakager.getAnimationSpeed());
            this.animate(freakager.getAnimationState("phase"), FreakagerAnimation.PHASE, ageInTicks, freakager.getAnimationSpeed());

            Calendar calendar = Calendar.getInstance();
            head.getChild("birthday").visible = calendar.get(Calendar.MONTH) == Calendar.FEBRUARY && calendar.get(Calendar.DAY_OF_MONTH) < 8;
            this.villager.getChild("head2").getChild("birthday2").visible = calendar.get(Calendar.MONTH) == Calendar.FEBRUARY && calendar.get(Calendar.DAY_OF_MONTH) < 8;

            head.yRot += netHeadYaw * ((float) Math.PI / 180F);
            head.xRot += headPitch * ((float) Math.PI / 180F);
            left_arm.visible = freakager.shouldShowArms();
            right_arm.visible = freakager.shouldShowArms();
            arms.visible = !freakager.shouldShowArms();
            scythe.visible = freakager.shouldShowScythe();
            this.villager.visible = freakager.shouldShowVillager();

            float f3 = ageInTicks / 6.0F;
            float f4 = ageInTicks / 60.0F;
            float multiplier = 0.1F;

            head.getChild("hat").getChild("hat_littlepiece2").zRot += (Mth.cos(f4 * 5)) * multiplier;

            this.villager.x += (((Mth.cos(f3 * 700))) * freakager.getVillagerShakeMultiplier()) * 0.04F;
            this.villager.z += (((Mth.cos(f3 * 550))) * freakager.getVillagerShakeMultiplier()) * 0.04F;
            this.villager.getChild("arms2").xRot += (((-0.5F + freakager.getRandom().nextFloat())) * freakager.getVillagerShakeMultiplier()) * ((float) Math.PI / 180F);
            this.villager.getChild("arms2").yRot += (((-0.5F + freakager.getRandom().nextFloat()) / 2.0F) * freakager.getVillagerShakeMultiplier()) * ((float) Math.PI / 180F);

            if (freakager.halfHealth() && freakager.isAlive()) {
                head.x += ((-0.5F + freakager.getRandom().nextFloat()) * 1.2F);
                head.y += ((-0.5F + freakager.getRandom().nextFloat()) * 1.2F);
                head.z += ((-0.5F + freakager.getRandom().nextFloat()) * 1.2F);
            }
        }
    }

    @Override
    public void renderToBuffer(PoseStack poseStack, VertexConsumer vertexConsumer, int packedLight, int packedOverlay, float red, float green, float blue, float alpha) {
        villager.render(poseStack, vertexConsumer, packedLight, packedOverlay, red, green, blue, alpha);
        all.render(poseStack, vertexConsumer, packedLight, packedOverlay, red, green, blue, alpha);
    }

    @Override
    public ModelPart root() {
        return this.root;
    }

    private ModelPart getArm(HumanoidArm p_191216_1_) {
        return p_191216_1_ == HumanoidArm.LEFT ? this.all.getChild("body").getChild("left_arm") : this.all.getChild("body").getChild("right_arm");
    }

    @Override
    public void translateToHand(HumanoidArm p_102108_, PoseStack p_102109_) {
        this.root().translateAndRotate(p_102109_);
        this.all.translateAndRotate(p_102109_);
        this.all.getChild("body").translateAndRotate(p_102109_);
        this.getArm(p_102108_).translateAndRotate(p_102109_);
    }

    @Override
    public void translateToHead(PoseStack stack) {
        this.root().translateAndRotate(stack);
        this.all.translateAndRotate(stack);
        this.all.getChild("body").translateAndRotate(stack);
        this.all.getChild("body").getChild("head").translateAndRotate(stack);
    }
}
