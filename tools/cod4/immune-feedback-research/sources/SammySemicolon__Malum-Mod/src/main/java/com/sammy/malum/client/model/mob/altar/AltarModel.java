package com.sammy.malum.client.model.mob.altar;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.sammy.malum.MalumMod;
import com.sammy.malum.client.model.CachedModelPart;
import com.sammy.malum.common.entity.mob.cultist.altar.AltarCultist;
import net.minecraft.client.Minecraft;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.util.Mth;
import org.jetbrains.annotations.NotNull;

@SuppressWarnings({"FieldCanBeLocal", "unused"})
public class AltarModel extends EntityModel<AltarCultist> {

	public static ModelLayerLocation LAYER = new ModelLayerLocation(MalumMod.malumPath("altar"), "main");

	private final ModelPart head;
	private final ModelPart body;
	private final ModelPart legs;

	private final CachedModelPart candles;
	private final CachedModelPart smallCandle;
	private final CachedModelPart medium_candle;
	private final CachedModelPart big_candle;

	private final CachedModelPart fleshHeart;

	private final CachedModelPart hindLeftLeg;
	private final CachedModelPart hindRightLeg;
	private final CachedModelPart leftLeg;
	private final CachedModelPart rightLeg;

	public AltarModel(ModelPart root) {
		head = root.getChild("head");
		body = root.getChild("body");
		legs = root.getChild("legs");
		candles = CachedModelPart.of(head.getChild("candles"));
		smallCandle = CachedModelPart.of(candles.getChild("small_candle"));
		medium_candle = CachedModelPart.of(candles.getChild("medium_candle"));
		big_candle = CachedModelPart.of(candles.getChild("big_candle"));

		fleshHeart = CachedModelPart.of(body.getChild("flesh_heart"));

		hindLeftLeg = CachedModelPart.of(legs.getChild("hind_left_leg"));
		hindRightLeg = CachedModelPart.of(legs.getChild("hind_right_leg"));
		leftLeg = CachedModelPart.of(legs.getChild("left_leg"));
		rightLeg = CachedModelPart.of(legs.getChild("right_leg"));
	}

	public static LayerDefinition createBodyLayer() {
		MeshDefinition meshdefinition = new MeshDefinition();
		PartDefinition partdefinition = meshdefinition.getRoot();

		PartDefinition head = partdefinition.addOrReplaceChild("head", CubeListBuilder.create().texOffs(0, 0).addBox(-8.0F, -2.0F, -8.0F, 16.0F, 5.0F, 16.0F, new CubeDeformation(0.0F))
				.texOffs(64, 0).addBox(-8.0F, -3.0F, -8.0F, 16.0F, 6.0F, 16.0F, new CubeDeformation(0.4F))
				.texOffs(0, 22).addBox(-6.5F, -5.0F, -6.5F, 13.0F, 3.0F, 13.0F, new CubeDeformation(0.0F))
				.texOffs(52, 22).addBox(-6.5F, -5.0F, -6.5F, 13.0F, 3.0F, 13.0F, new CubeDeformation(0.5F)), PartPose.offset(0.0F, 7.0F, 0.0F));

		PartDefinition candles = head.addOrReplaceChild("candles", CubeListBuilder.create(), PartPose.offset(0.0F, -2.0F, 0.0F));

		PartDefinition small_candle = candles.addOrReplaceChild("small_candle", CubeListBuilder.create().texOffs(68, 45).addBox(-1.5F, -8.0F, -1.5F, 3.0F, 8.0F, 3.0F, new CubeDeformation(0.25F))
				.texOffs(28, 45).addBox(-1.5F, -8.0F, -1.5F, 3.0F, 8.0F, 3.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(3.5F, 0.0F, 0.5F, 0.0F, 0.3927F, 0.0F));

		PartDefinition small_wick = small_candle.addOrReplaceChild("small_wick", CubeListBuilder.create().texOffs(26, 37).addBox(0.0F, -2.0F, -1.5F, 0.0F, 2.0F, 3.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, -8.0F, 0.0F, 0.0F, -0.7854F, 0.0F));

		PartDefinition medium_candle = candles.addOrReplaceChild("medium_candle", CubeListBuilder.create().texOffs(56, 42).addBox(-1.5F, -11.0F, -1.5F, 3.0F, 11.0F, 3.0F, new CubeDeformation(0.25F))
				.texOffs(16, 42).addBox(-1.5F, -11.0F, -1.5F, 3.0F, 11.0F, 3.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(-2.5F, 0.0F, -2.5F, 0.0F, -0.3927F, 0.0F));

		PartDefinition medium_wick = medium_candle.addOrReplaceChild("medium_wick", CubeListBuilder.create().texOffs(20, 39).addBox(-1.5F, -3.0F, 0.0F, 3.0F, 3.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, -11.0F, 0.0F, 0.0F, -0.7854F, 0.0F));

		PartDefinition big_candle = candles.addOrReplaceChild("big_candle", CubeListBuilder.create().texOffs(40, 38).addBox(-2.0F, -14.0F, -2.0F, 4.0F, 14.0F, 4.0F, new CubeDeformation(0.25F))
				.texOffs(0, 38).addBox(-2.0F, -14.0F, -2.0F, 4.0F, 14.0F, 4.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(-1.0F, 0.0F, 2.0F, 0.0F, 0.7854F, 0.0F));

		PartDefinition big_wick = big_candle.addOrReplaceChild("big_wick", CubeListBuilder.create().texOffs(12, 38).addBox(-2.0F, -4.0F, 0.0F, 4.0F, 4.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, -14.0F, 0.0F, 0.0F, -0.7854F, 0.0F));

		PartDefinition body = partdefinition.addOrReplaceChild("body", CubeListBuilder.create().texOffs(0, 56).addBox(-4.0F, -2.0F, -4.0F, 8.0F, 4.0F, 8.0F, new CubeDeformation(0.0F))
				.texOffs(32, 56).addBox(-4.0F, -2.0F, -10.0F, 8.0F, 4.0F, 6.0F, new CubeDeformation(0.0F))
				.texOffs(60, 56).addBox(-4.0F, -2.0F, -10.0F, 8.0F, 4.0F, 6.0F, new CubeDeformation(0.4F)), PartPose.offset(0.0F, 12.0F, 0.0F));

		PartDefinition cube_r1 = body.addOrReplaceChild("cube_r1", CubeListBuilder.create().texOffs(60, 56).addBox(-4.0F, -2.0F, -10.0F, 8.0F, 4.0F, 6.0F, new CubeDeformation(0.4F))
				.texOffs(32, 56).addBox(-4.0F, -2.0F, -10.0F, 8.0F, 4.0F, 6.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 0.0F, 0.0F, 0.0F, 1.5708F, 0.0F));

		PartDefinition cube_r2 = body.addOrReplaceChild("cube_r2", CubeListBuilder.create().texOffs(60, 56).addBox(-4.0F, -2.0F, -10.0F, 8.0F, 4.0F, 6.0F, new CubeDeformation(0.4F))
				.texOffs(32, 56).addBox(-4.0F, -2.0F, -10.0F, 8.0F, 4.0F, 6.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 0.0F, 0.0F, 0.0F, 3.1416F, 0.0F));

		PartDefinition cube_r3 = body.addOrReplaceChild("cube_r3", CubeListBuilder.create().texOffs(60, 56).addBox(-4.0F, -2.0F, -10.0F, 8.0F, 4.0F, 6.0F, new CubeDeformation(0.4F))
				.texOffs(32, 56).addBox(-4.0F, -2.0F, -10.0F, 8.0F, 4.0F, 6.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 0.0F, 0.0F, 0.0F, -1.5708F, 0.0F));

		PartDefinition flesh_heart = body.addOrReplaceChild("flesh_heart", CubeListBuilder.create().texOffs(48, 68).addBox(-6.0F, -2.0F, -6.0F, 12.0F, 8.0F, 12.0F, new CubeDeformation(0.4F))
				.texOffs(0, 68).addBox(-6.0F, -2.0F, -6.0F, 12.0F, 8.0F, 12.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 4.0F, 0.0F));

		PartDefinition cloth = body.addOrReplaceChild("cloth", CubeListBuilder.create().texOffs(36, 58).addBox(-10.0F, 2.0F, -4.0F, 0.0F, 5.0F, 8.0F, new CubeDeformation(0.0F))
				.texOffs(36, 58).addBox(10.0F, 2.0F, -4.0F, 0.0F, 5.0F, 8.0F, new CubeDeformation(0.0F))
				.texOffs(36, 66).addBox(-4.0F, 2.0F, -10.0F, 8.0F, 5.0F, 0.0F, new CubeDeformation(0.0F))
				.texOffs(36, 66).addBox(-4.0F, 2.0F, 10.0F, 8.0F, 5.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 0.0F, 0.0F));

		PartDefinition legs = partdefinition.addOrReplaceChild("legs", CubeListBuilder.create(), PartPose.offset(0.0F, 24.0F, 0.0F));

		PartDefinition hind_left_leg = legs.addOrReplaceChild("hind_left_leg", CubeListBuilder.create().texOffs(0, 88).addBox(-1.5F, -3.0F, -1.5F, 3.0F, 14.0F, 3.0F, new CubeDeformation(0.0F))
				.texOffs(0, 105).addBox(1.5F, 8.0F, -1.5F, 6.0F, 3.0F, 3.0F, new CubeDeformation(0.0F))
				.texOffs(18, 88).addBox(-1.5F, -3.0F, -1.5F, 3.0F, 14.0F, 3.0F, new CubeDeformation(0.4F))
				.texOffs(18, 105).addBox(1.5F, 8.0F, -1.5F, 6.0F, 3.0F, 3.0F, new CubeDeformation(0.4F)), PartPose.offsetAndRotation(7.6533F, -10.3827F, 7.6533F, 0.3655F, -0.7119F, -0.5299F));

		PartDefinition hind_right_leg = legs.addOrReplaceChild("hind_right_leg", CubeListBuilder.create().texOffs(0, 88).addBox(-1.5F, -3.0F, -1.5F, 3.0F, 14.0F, 3.0F, new CubeDeformation(0.0F))
				.texOffs(0, 105).addBox(1.5F, 8.0F, -1.5F, 6.0F, 3.0F, 3.0F, new CubeDeformation(0.0F))
				.texOffs(18, 88).addBox(-1.5F, -3.0F, -1.5F, 3.0F, 14.0F, 3.0F, new CubeDeformation(0.4F))
				.texOffs(18, 105).addBox(1.5F, 8.0F, -1.5F, 6.0F, 3.0F, 3.0F, new CubeDeformation(0.4F)), PartPose.offsetAndRotation(-7.0F, -10.0F, 7.0F, 2.7761F, -0.7119F, -2.6117F));

		PartDefinition right_leg = legs.addOrReplaceChild("right_leg", CubeListBuilder.create().texOffs(0, 88).addBox(-1.5F, -3.0F, -1.5F, 3.0F, 14.0F, 3.0F, new CubeDeformation(0.0F))
				.texOffs(0, 105).addBox(1.5F, 8.0F, -1.5F, 6.0F, 3.0F, 3.0F, new CubeDeformation(0.0F))
				.texOffs(18, 88).addBox(-1.5F, -3.0F, -1.5F, 3.0F, 14.0F, 3.0F, new CubeDeformation(0.4F))
				.texOffs(18, 105).addBox(1.5F, 8.0F, -1.5F, 6.0F, 3.0F, 3.0F, new CubeDeformation(0.4F)), PartPose.offsetAndRotation(-7.0F, -10.0F, -7.0F, -2.7761F, 0.7119F, -2.6117F));

		PartDefinition left_leg = legs.addOrReplaceChild("left_leg", CubeListBuilder.create().texOffs(0, 88).addBox(-1.5F, -3.0F, -1.5F, 3.0F, 14.0F, 3.0F, new CubeDeformation(0.0F))
				.texOffs(0, 105).addBox(1.5F, 8.0F, -1.5F, 6.0F, 3.0F, 3.0F, new CubeDeformation(0.0F))
				.texOffs(18, 88).addBox(-1.5F, -3.0F, -1.5F, 3.0F, 14.0F, 3.0F, new CubeDeformation(0.4F))
				.texOffs(18, 105).addBox(1.5F, 8.0F, -1.5F, 6.0F, 3.0F, 3.0F, new CubeDeformation(0.4F)), PartPose.offsetAndRotation(7.0F, -10.0F, -7.0F, -0.3655F, 0.7119F, -0.5299F));

		return LayerDefinition.create(meshdefinition, 128, 128);
	}

	@Override
	public void setupAnim(@NotNull AltarCultist altar, float limbSwing, float limbSwingAmount, float ageInTicks, float netHeadYaw, float headPitch) {
		float partialTicks = Minecraft.getInstance().getTimer().getGameTimeDeltaPartialTick(false);
		float headTilt = Mth.lerp(partialTicks, altar.oHeadTilt, altar.headTilt);

		head.yRot = (headTilt*90 + netHeadYaw) * Mth.DEG_TO_RAD;
		head.xRot = headPitch * Mth.DEG_TO_RAD;

		float bodyX = (Mth.sin(limbSwing * 1.2f + 0.0F) * 0.3F) * limbSwingAmount;
		float bodyZ = (Mth.cos(limbSwing * 1.2f + 0.0F) * 0.3F) * limbSwingAmount;

		body.setRotation(bodyX, 0, bodyZ);
		candles.applyRotation(0, altar.getCandleRotation(), 0);

		float hindLeft = (Mth.sin(limbSwing * 1.2f + 0.785f) * 0.6F) * limbSwingAmount;
		float hindRight = (Mth.sin(limbSwing * 1.2f + 1.57f) * 0.6F) * limbSwingAmount;
		float left = (Mth.sin(limbSwing * 1.2f + 2.355f) * 0.6F) * limbSwingAmount;
		float right = (Mth.sin(limbSwing * 1.2f + 3.14f) * 0.6F) * limbSwingAmount;

		hindLeftLeg.applyRotation(0, left, left);
		hindRightLeg.applyRotation(0, left, left);
		leftLeg.applyRotation(left, 0, left);
		rightLeg.applyRotation(left, 0, left);
	}

	@Override
	public void renderToBuffer(@NotNull PoseStack poseStack, @NotNull VertexConsumer buffer, int packedLight, int packedOverlay, int color) {
		head.render(poseStack, buffer, packedLight, packedOverlay);
		body.render(poseStack, buffer, packedLight, packedOverlay);
		legs.render(poseStack, buffer, packedLight, packedOverlay);
	}
}