package com.sammy.malum.client.model.mob.cardinal;

import com.sammy.malum.MalumMod;
import com.sammy.malum.client.model.mob.CultistHumanoidModel;
import com.sammy.malum.client.model.mob.MalumAnimationUtils;
import com.sammy.malum.common.entity.mob.cultist.cardinal.CardinalCultist;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.util.Mth;
import team.lodestar.lodestone.modules.core.easing.Easing;

@SuppressWarnings({"FieldCanBeLocal", "unused"})
public class CardinalModel extends CultistHumanoidModel<CardinalCultist> {

	public static ModelLayerLocation LAYER = new ModelLayerLocation(MalumMod.malumPath("cardinal"), "main");

	public CardinalModel(ModelPart modelDefinition) {
        super(modelDefinition);
	}

	public static LayerDefinition createBodyLayer() {
		MeshDefinition meshdefinition = new MeshDefinition();
		PartDefinition partdefinition = meshdefinition.getRoot();

		PartDefinition root = partdefinition.addOrReplaceChild("root", CubeListBuilder.create(), PartPose.offset(0.0F, 0.0F, 0.0F));

		PartDefinition body = root.addOrReplaceChild("body", CubeListBuilder.create().texOffs(0, 46).addBox(-11.0F, -14.0F, -6.0F, 22.0F, 14.0F, 11.0F, new CubeDeformation(0.05F))
				.texOffs(74, 46).addBox(-11.0F, -14.0F, -6.0F, 22.0F, 14.0F, 11.0F, new CubeDeformation(0.55F))
				.texOffs(55, 60).addBox(7.0F, -18.0F, -6.0F, 4.0F, 4.0F, 11.0F, new CubeDeformation(0.05F))
				.texOffs(55, 60).mirror().addBox(-11.0F, -18.0F, -6.0F, 4.0F, 4.0F, 11.0F, new CubeDeformation(0.05F)).mirror(false)
				.texOffs(129, 60).addBox(7.0F, -18.0F, -6.0F, 4.0F, 4.0F, 11.0F, new CubeDeformation(0.55F))
				.texOffs(129, 60).mirror().addBox(-11.0F, -18.0F, -6.0F, 4.0F, 4.0F, 11.0F, new CubeDeformation(0.55F)).mirror(false)
				.texOffs(0, 71).addBox(-11.0F, 0.0F, -6.0F, 22.0F, 5.0F, 11.0F, new CubeDeformation(0.05F))
				.texOffs(74, 71).addBox(-11.0F, 0.0F, -6.0F, 22.0F, 5.0F, 11.0F, new CubeDeformation(0.55F))
				.texOffs(0, 87).addBox(-9.0F, -8.0F, -5.0F, 18.0F, 19.0F, 9.0F, new CubeDeformation(0.05F))
				.texOffs(84, 101).addBox(-9.0F, -8.0F, -5.0F, 18.0F, 19.0F, 9.0F, new CubeDeformation(0.55F))
				.texOffs(0, 116).addBox(-8.0F, 5.0F, -4.0F, 16.0F, 11.0F, 7.0F, new CubeDeformation(0.05F))
				.texOffs(54, 87).addBox(-11.0F, -14.0F, 5.0F, 22.0F, 12.0F, 2.0F, new CubeDeformation(0.0F))
				.texOffs(102, 87).addBox(-11.0F, -14.0F, 5.0F, 22.0F, 12.0F, 2.0F, new CubeDeformation(0.5F))
				.texOffs(54, 101).addBox(-4.5F, -6.0F, -3.0F, 9.0F, 13.0F, 6.0F, new CubeDeformation(0.5F)), PartPose.offset(0.0F, 1.0F, 0.0F));

		PartDefinition head = body.addOrReplaceChild("head", CubeListBuilder.create().texOffs(0, 14).addBox(-4.0F, -5.0F, -3.5F, 8.0F, 12.0F, 8.0F, new CubeDeformation(0.0F))
				.texOffs(64, 14).addBox(-4.0F, -5.0F, -3.5F, 8.0F, 12.0F, 8.0F, new CubeDeformation(0.5F))
				.texOffs(38, 42).addBox(-4.0F, 6.0F, -3.5F, 8.0F, 3.0F, 1.0F, new CubeDeformation(0.5F))
				.texOffs(0, 34).addBox(-10.0F, -7.0F, -3.5F, 8.0F, 6.0F, 6.0F, new CubeDeformation(0.0F))
				.texOffs(0, 34).mirror().addBox(2.0F, -7.0F, -3.5F, 8.0F, 6.0F, 6.0F, new CubeDeformation(0.0F)).mirror(false)
				.texOffs(64, 34).addBox(-10.0F, -7.0F, -3.5F, 8.0F, 6.0F, 6.0F, new CubeDeformation(0.5F))
				.texOffs(64, 34).mirror().addBox(2.0F, -7.0F, -3.5F, 8.0F, 6.0F, 6.0F, new CubeDeformation(0.5F)).mirror(false)
				.texOffs(30, 32).addBox(-6.0F, 2.0F, -3.5F, 2.0F, 12.0F, 2.0F, new CubeDeformation(0.0F))
				.texOffs(30, 32).mirror().addBox(4.0F, 2.0F, -3.5F, 2.0F, 12.0F, 2.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offset(0.0F, -19.0F, -4.0F));

		PartDefinition crown = head.addOrReplaceChild("crown", CubeListBuilder.create().texOffs(0, 0).addBox(-12.0F, -51.0F, -3.5F, 23.0F, 14.0F, 0.0F, new CubeDeformation(0.0F))
				.texOffs(64, 0).addBox(-12.0F, -51.0F, -3.5F, 23.0F, 14.0F, 0.0F, new CubeDeformation(0.5F)), PartPose.offset(0.5F, 36.0F, 4.0F));

		PartDefinition right_arm = root.addOrReplaceChild("right_arm", CubeListBuilder.create().texOffs(0, 134).mirror().addBox(-5.0F, -7.5F, -2.0F, 4.0F, 28.0F, 4.0F, new CubeDeformation(0.0F)).mirror(false)
				.texOffs(16, 134).mirror().addBox(-6.0F, -9.0F, -2.5F, 5.0F, 31.0F, 5.0F, new CubeDeformation(0.5F)).mirror(false)
				.texOffs(36, 133).mirror().addBox(-6.5F, 14.0F, -3.0F, 6.0F, 9.0F, 6.0F, new CubeDeformation(0.5F)).mirror(false), PartPose.offset(-10.0F, -10.0F, 0.0F));

		PartDefinition left_arm = root.addOrReplaceChild("left_arm", CubeListBuilder.create().texOffs(0, 170).addBox(1.0F, -7.5F, -4.0F, 6.0F, 23.0F, 8.0F, new CubeDeformation(0.0F))
				.texOffs(28, 170).addBox(1.0F, -9.0F, -4.5F, 7.0F, 26.0F, 9.0F, new CubeDeformation(0.5F))
				.texOffs(60, 170).addBox(0.5F, 13.0F, -5.0F, 8.0F, 7.0F, 10.0F, new CubeDeformation(0.5F)), PartPose.offset(10.0F, -10.0F, 0.0F));

		PartDefinition right_leg = root.addOrReplaceChild("right_leg", CubeListBuilder.create().texOffs(0, 201).mirror().addBox(-2.5F, -3.0F, -3.0F, 6.0F, 16.0F, 5.0F, new CubeDeformation(0.0F)).mirror(false)
				.texOffs(64, 201).mirror().addBox(-2.5F, -3.0F, -3.0F, 6.0F, 16.0F, 5.0F, new CubeDeformation(0.5F)).mirror(false), PartPose.offset(-5.0F, 11.0F, 0.0F));

		PartDefinition left_leg = root.addOrReplaceChild("left_leg", CubeListBuilder.create().texOffs(0, 201).addBox(-3.5F, -3.0F, -3.0F, 6.0F, 16.0F, 5.0F, new CubeDeformation(0.0F))
				.texOffs(64, 201).addBox(-3.5F, -3.0F, -3.0F, 6.0F, 16.0F, 5.0F, new CubeDeformation(0.5F)), PartPose.offset(5.0F, 11.0F, 0.0F));

		return LayerDefinition.create(meshdefinition, 256, 256);
	}

	@Override
	public void setupAnim(CardinalCultist cardinal, MalumAnimationUtils<CardinalCultist> utils, float limbSwing, float limbSwingAmount, float ageInTicks, float netHeadYaw, float headPitch) {
		float headYClamp = 0.7f;
		float headXClamp = 0.08f;
		float armClamp = 4.4F;
		float legClamp = 0.2F;

		float headYRot = netHeadYaw * Mth.DEG_TO_RAD;
		headYRot = Mth.clamp(headYRot, -headYClamp, headYClamp);
		float headXRot = headPitch * Mth.DEG_TO_RAD;
		headXRot = Mth.clamp(headXRot, -headXClamp, headXClamp);

		float rightArmRotation = utils.getRightArmRotation(d -> d
				.setRate(0.4f).setAmount(1.2f).setEasing(Easing.CUBIC_IN).addClamp(armClamp));
		float leftArmRotation = utils.getLeftArmRotation(d -> d
				.setRate(0.3f).setAmount(1.4f).setEasing(Easing.BOUNCE_OUT).addClamp(armClamp));

		float rightLegRotation = utils.getRightLegRotation(d -> d
				.setRate(0.7f).setAmount(0.6f).setEasing(Easing.EXPO_OUT).addClamp(legClamp));
		float leftLegRotation = utils.getLeftLegRotation(d -> d
				.setRate(0.7f).setAmount(0.6f).setEasing(Easing.EXPO_OUT).addClamp(legClamp));


		head.yRot = headYRot;
		head.xRot = headXRot;

		rightArm.xRot = rightArmRotation;
		leftArm.xRot = leftArmRotation;

		rightLeg.xRot = rightLegRotation;
		leftLeg.xRot = leftLegRotation;

		animate(cardinal.idleAnimationState, CardinalAnimations.IDLE, ageInTicks);
		animate(cardinal.lobAnimationState, CardinalAnimations.LOB_CHARGE, ageInTicks);
		animate(cardinal.detonateAnimationState, CardinalAnimations.DETONATE, ageInTicks);
		animate(cardinal.quickFireAnimationState, CardinalAnimations.QUICKFIRE, ageInTicks);
		animate(cardinal.immolationBlastAnimationState, CardinalAnimations.IMMOLATION, ageInTicks);
	}
}