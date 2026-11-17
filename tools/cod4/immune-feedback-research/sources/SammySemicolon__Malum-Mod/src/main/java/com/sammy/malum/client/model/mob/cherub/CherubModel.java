package com.sammy.malum.client.model.mob.cherub;

import com.sammy.malum.MalumMod;
import com.sammy.malum.client.model.mob.CultistHumanoidModel;
import com.sammy.malum.client.model.mob.MalumAnimationUtils;
import com.sammy.malum.common.entity.mob.cultist.cherub.CherubCultist;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.util.Mth;

@SuppressWarnings({"FieldCanBeLocal", "unused"})
public class CherubModel extends CultistHumanoidModel<CherubCultist> {

	public static ModelLayerLocation LAYER = new ModelLayerLocation(MalumMod.malumPath("cherub"), "main");

	private final ModelPart wings;
	private final ModelPart frontWings;
	private final ModelPart backWings;
	private final ModelPart frontRightWing;
	private final ModelPart frontLeftWing;
	private final ModelPart backRightWing;
	private final ModelPart backLeftWing;

	public CherubModel(ModelPart modelDefinition) {
        super(modelDefinition);
		wings = root.getChild("wings");
		frontWings = wings.getChild("front");
		backWings = wings.getChild("back");
		frontRightWing = frontWings.getChild("front_right_wing");
		frontLeftWing = frontWings.getChild("front_left_wing");
		backRightWing = backWings.getChild("back_right_wing");
		backLeftWing = backWings.getChild("back_left_wing");
	}

	public static LayerDefinition createBodyLayer() {
		MeshDefinition meshdefinition = new MeshDefinition();
		PartDefinition partdefinition = meshdefinition.getRoot();

		PartDefinition root = partdefinition.addOrReplaceChild("root", CubeListBuilder.create(), PartPose.offset(0.0F, 0.0F, 0.0F));

		PartDefinition head = root.addOrReplaceChild("head", CubeListBuilder.create().texOffs(0, 10).addBox(-3.5F, -6.0F, -3.5F, 7.0F, 6.0F, 7.0F, new CubeDeformation(0.0F))
				.texOffs(28, 10).addBox(-3.5F, -6.0F, -3.5F, 7.0F, 6.0F, 7.0F, new CubeDeformation(0.5F))
				.texOffs(0, 23).addBox(-3.5F, 0.0F, -3.5F, 7.0F, 2.0F, 2.0F, new CubeDeformation(0.0F))
				.texOffs(16, 23).addBox(-2.5F, 2.0F, -3.5F, 5.0F, 1.0F, 1.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 19.0F, 0.0F));

		PartDefinition crown = head.addOrReplaceChild("crown", CubeListBuilder.create().texOffs(0, 0).addBox(-6.5F, -16.0F, 0.0F, 13.0F, 9.0F, 1.0F, new CubeDeformation(0.0F))
				.texOffs(28, 0).addBox(-6.5F, -16.0F, 0.0F, 13.0F, 9.0F, 1.0F, new CubeDeformation(0.5F)), PartPose.offset(0.0F, 5.0F, 0.0F));

		PartDefinition body = root.addOrReplaceChild("body", CubeListBuilder.create().texOffs(0, 27).addBox(-1.5F, -4.0F, -1.0F, 3.0F, 4.0F, 2.0F, new CubeDeformation(0.0F))
				.texOffs(0, 33).addBox(-2.0F, -3.0F, -1.0F, 4.0F, 6.0F, 2.0F, new CubeDeformation(-0.2F))
				.texOffs(18, 27).addBox(-1.5F, -4.0F, -1.0F, 3.0F, 4.0F, 2.0F, new CubeDeformation(0.25F))
				.texOffs(18, 33).addBox(-2.0F, -3.0F, -1.0F, 4.0F, 6.0F, 2.0F, new CubeDeformation(0.05F)), PartPose.offset(0.0F, 24.0F, 0.0F));

		PartDefinition wings = root.addOrReplaceChild("wings", CubeListBuilder.create(), PartPose.offset(0.0F, 24.0F, 0.0F));

		PartDefinition front = wings.addOrReplaceChild("front", CubeListBuilder.create(), PartPose.offset(0.0F, -2.0F, 0.0F));

		PartDefinition front_right_wing = front.addOrReplaceChild("front_right_wing", CubeListBuilder.create().texOffs(0, 41).addBox(-11.5F, -2.0F, 0.0F, 11.0F, 7.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(-2.0F, -3.0F, 0.0F, 0.0F, 0.3927F, -0.3927F));

		PartDefinition front_left_wing = front.addOrReplaceChild("front_left_wing", CubeListBuilder.create().texOffs(0, 41).mirror().addBox(0.5F, -2.0F, 0.0F, 11.0F, 7.0F, 0.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offsetAndRotation(2.0F, -3.0F, 0.0F, 0.0F, -0.3927F, 0.3927F));

		PartDefinition back = wings.addOrReplaceChild("back", CubeListBuilder.create(), PartPose.offset(0.0F, -2.0F, 0.0F));

		PartDefinition back_right_wing = back.addOrReplaceChild("back_right_wing", CubeListBuilder.create().texOffs(0, 48).addBox(-13.0F, -7.9197F, 0.6213F, 14.0F, 9.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(-4.0F, -1.5F, 2.0F, 0.0F, 0.3927F, 0.3927F));

		PartDefinition back_left_wing = back.addOrReplaceChild("back_left_wing", CubeListBuilder.create().texOffs(0, 48).mirror().addBox(-1.0F, -7.9197F, 0.6213F, 14.0F, 9.0F, 0.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offsetAndRotation(4.0F, -1.5F, 2.0F, 0.0F, -0.3927F, -0.3927F));

		PartDefinition right_arm = root.addOrReplaceChild("right_arm", CubeListBuilder.create().texOffs(10, 27).addBox(-1.25F, -0.5F, -1.0F, 2.0F, 5.0F, 2.0F, new CubeDeformation(-0.1F)), PartPose.offset(-1.75F, 20.25F, 0.0F));

		PartDefinition left_arm = root.addOrReplaceChild("left_arm", CubeListBuilder.create().texOffs(10, 27).mirror().addBox(-0.75F, -0.5F, -1.0F, 2.0F, 5.0F, 2.0F, new CubeDeformation(-0.1F)).mirror(false), PartPose.offset(1.75F, 20.25F, 0.0F));

		return LayerDefinition.create(meshdefinition, 64, 64);
	}

	@SuppressWarnings("SuspiciousNameCombination")
    @Override
	public void setupAnim(CherubCultist cherub, MalumAnimationUtils<CherubCultist> utils, float limbSwing, float limbSwingAmount, float ageInTicks, float netHeadYaw, float headPitch) {
		float headYClamp = 0.7f;
		float headXClamp = 0.08f;
		float armClamp = 1.4F;
		float legClamp = 0.7F;

		float headYRot = netHeadYaw * Mth.DEG_TO_RAD;
		headYRot = Mth.clamp(headYRot, -headYClamp, headYClamp);
		float headXRot = headPitch * Mth.DEG_TO_RAD;
		headXRot = Mth.clamp(headXRot, -headXClamp, headXClamp);

		head.yRot = headYRot;
		head.xRot = headXRot;

		animate(cherub.idleAnimationState, CherubAnimations.IDLE, ageInTicks);
		animate(cherub.castAnimationState, CherubAnimations.CAST, ageInTicks);

	}
}