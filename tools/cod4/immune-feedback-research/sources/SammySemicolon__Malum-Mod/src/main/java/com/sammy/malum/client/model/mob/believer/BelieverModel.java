package com.sammy.malum.client.model.mob.believer;

import com.sammy.malum.MalumMod;
import com.sammy.malum.client.model.mob.CultistHumanoidModel;
import com.sammy.malum.client.model.mob.HierarchicalHumanoidModel;
import com.sammy.malum.client.model.mob.MalumAnimationUtils;
import com.sammy.malum.common.entity.mob.cultist.believer.BelieverCultist;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.util.Mth;
import team.lodestar.lodestone.modules.core.easing.Easing;

@SuppressWarnings({"FieldCanBeLocal", "unused"})
public class BelieverModel extends CultistHumanoidModel<BelieverCultist> {

	public static ModelLayerLocation LAYER = new ModelLayerLocation(MalumMod.malumPath("believer"), "main");

	private final ModelPart mask;
	private final ModelPart teeth;
	private final ModelPart leftTooth;
	private final ModelPart rightTooth;

	public BelieverModel(ModelPart modelDefinition) {
        super(modelDefinition);
		mask = head.getChild("mask");
		teeth = mask.getChild("teeth");
		leftTooth = teeth.getChild("left_tooth");
		rightTooth = teeth.getChild("right_tooth");
	}

	public static LayerDefinition createBodyLayer() {
		MeshDefinition meshdefinition = new MeshDefinition();
		PartDefinition partdefinition = meshdefinition.getRoot();

		PartDefinition root = partdefinition.addOrReplaceChild("root", CubeListBuilder.create(), PartPose.offset(0.0F, 0.0F, 0.0F));

		PartDefinition head = root.addOrReplaceChild("head", CubeListBuilder.create().texOffs(0, 8).addBox(-5.0F, -5.0F, -3.0F, 10.0F, 5.0F, 6.0F, new CubeDeformation(0.25F))
				.texOffs(32, 8).addBox(-5.0F, -5.0F, -3.0F, 10.0F, 5.0F, 6.0F, new CubeDeformation(0.75F)), PartPose.offset(0.0F, -4.0F, 0.0F));

		PartDefinition crown = head.addOrReplaceChild("crown", CubeListBuilder.create().texOffs(32, 0).addBox(-8.0F, -30.0F, 0.0F, 15.0F, 7.0F, 1.0F, new CubeDeformation(0.5F))
				.texOffs(0, 0).addBox(-8.0F, -30.0F, 0.0F, 15.0F, 7.0F, 1.0F, new CubeDeformation(0.0F)), PartPose.offset(0.5F, 20.0F, 0.0F));

		PartDefinition mask = head.addOrReplaceChild("mask", CubeListBuilder.create().texOffs(0, 19).addBox(-4.0F, -30.0F, -4.0F, 7.0F, 10.0F, 4.0F, new CubeDeformation(0.0F))
				.texOffs(30, 19).addBox(-4.0F, -30.0F, -4.0F, 7.0F, 10.0F, 4.0F, new CubeDeformation(0.5F)), PartPose.offset(0.5F, 23.0F, 0.0F));

		PartDefinition teeth = mask.addOrReplaceChild("teeth", CubeListBuilder.create(), PartPose.offset(-0.5F, -21.0F, -4.0F));

		PartDefinition right_tooth = teeth.addOrReplaceChild("right_tooth", CubeListBuilder.create().texOffs(0, 10).addBox(-1.0F, -0.5F, 0.0F, 2.0F, 3.0F, 1.0F, new CubeDeformation(0.0F)), PartPose.offset(-2.0F, 1.0F, 0.0F));

		PartDefinition left_tooth = teeth.addOrReplaceChild("left_tooth", CubeListBuilder.create().texOffs(0, 10).mirror().addBox(-1.0F, -0.5F, 0.0F, 2.0F, 3.0F, 1.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offset(2.0F, 1.0F, 0.0F));

		PartDefinition body = root.addOrReplaceChild("body", CubeListBuilder.create().texOffs(0, 33).addBox(-4.0F, -4.0F, -2.0F, 8.0F, 16.0F, 4.0F, new CubeDeformation(0.0F))
				.texOffs(32, 33).addBox(-4.0F, -4.0F, -2.0F, 8.0F, 16.0F, 4.0F, new CubeDeformation(0.5F)), PartPose.offset(0.0F, 0.0F, 0.0F));

		PartDefinition right_arm = root.addOrReplaceChild("right_arm", CubeListBuilder.create().texOffs(22, 19).mirror().addBox(-1.0F, -5.0F, -1.0F, 2.0F, 15.0F, 2.0F, new CubeDeformation(0.0F)).mirror(false)
				.texOffs(52, 19).mirror().addBox(-1.0F, -5.0F, -1.0F, 2.0F, 15.0F, 2.0F, new CubeDeformation(0.25F)).mirror(false), PartPose.offset(-5.0F, 2.0F, 0.0F));

		PartDefinition left_arm = root.addOrReplaceChild("left_arm", CubeListBuilder.create().texOffs(22, 19).addBox(-1.0F, -5.0F, -1.0F, 2.0F, 15.0F, 2.0F, new CubeDeformation(0.0F))
				.texOffs(52, 19).addBox(-1.0F, -5.0F, -1.0F, 2.0F, 15.0F, 2.0F, new CubeDeformation(0.25F)), PartPose.offset(5.0F, 2.0F, 0.0F));

		PartDefinition right_leg = root.addOrReplaceChild("right_leg", CubeListBuilder.create().texOffs(24, 36).mirror().addBox(-1.0F, 0.0F, -1.0F, 2.0F, 12.0F, 2.0F, new CubeDeformation(0.0F)).mirror(false)
				.texOffs(56, 36).mirror().addBox(-1.0F, 0.0F, -1.0F, 2.0F, 12.0F, 2.0F, new CubeDeformation(0.25F)).mirror(false), PartPose.offset(-2.0F, 12.0F, 0.0F));

		PartDefinition left_leg = root.addOrReplaceChild("left_leg", CubeListBuilder.create().texOffs(24, 36).addBox(-1.0F, 0.0F, -1.0F, 2.0F, 12.0F, 2.0F, new CubeDeformation(0.0F))
				.texOffs(56, 36).addBox(-1.0F, 0.0F, -1.0F, 2.0F, 12.0F, 2.0F, new CubeDeformation(0.25F)), PartPose.offset(2.0F, 12.0F, 0.0F));

		return LayerDefinition.create(meshdefinition, 64, 64);
	}

	@Override
	public void setupAnim(BelieverCultist believer, MalumAnimationUtils<BelieverCultist> utils, float limbSwing, float limbSwingAmount, float ageInTicks, float netHeadYaw, float headPitch) {
		float headYClamp = 0.7f;
		float headXClamp = 0.08f;
		float armClamp = 1.4F;
		float legClamp = 0.7F;

		float headYRot = netHeadYaw * Mth.DEG_TO_RAD;
		headYRot = Mth.clamp(headYRot, -headYClamp, headYClamp);
		float headXRot = headPitch * Mth.DEG_TO_RAD;
		headXRot = Mth.clamp(headXRot, -headXClamp, headXClamp);

		float rightArmRotation = utils.getRightArmRotation(d -> d
				.setRate(0.65F).setAmount(0.9F).setEasing(Easing.SINE_IN).addClamp(armClamp));
		float leftArmRotation = utils.getLeftArmRotation(d -> d
				.setRate(0.65F).setAmount(0.9F).setEasing(Easing.SINE_IN).addClamp(armClamp));

		float rightLegRotation = utils.getRightLegRotation(d -> d
				.setRate(0.8F).setAmount(0.9f).setEasing(Easing.SINE_IN_OUT).addClamp(legClamp));
		float leftLegRotation = utils.getLeftLegRotation(d -> d
				.setRate(0.8F).setAmount(0.9f).setEasing(Easing.SINE_IN_OUT).addClamp(legClamp));

		head.yRot = headYRot;
		head.xRot = headXRot;

		rightArm.xRot = rightArmRotation;
		leftArm.xRot = leftArmRotation;

		rightLeg.xRot = rightLegRotation;
		leftLeg.xRot = leftLegRotation;
	}
}