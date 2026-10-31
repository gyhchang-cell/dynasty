/*
 * Copyright (c) MoriyaShiine. All Rights Reserved.
 */
package moriyashiine.anthropophagy.client.render.entity.model;

import moriyashiine.anthropophagy.common.Anthropophagy;
import net.fabricmc.api.EnvType;
import net.fabricmc.api.Environment;
import net.minecraft.client.model.*;
import net.minecraft.client.render.VertexConsumer;
import net.minecraft.client.render.entity.model.EntityModel;
import net.minecraft.client.render.entity.model.EntityModelLayer;
import net.minecraft.client.util.math.MatrixStack;
import net.minecraft.entity.LivingEntity;
import net.minecraft.util.math.MathHelper;

@Environment(EnvType.CLIENT)
public class PigluttonEntityModel<T extends LivingEntity> extends EntityModel<T> {
	public static final EntityModelLayer MODEL_LAYER = new EntityModelLayer(Anthropophagy.id("piglutton"), "main");

	private final ModelPart body;
	private final ModelPart neck;
	private final ModelPart bipedLeftArm;
	private final ModelPart bipedRightArm;
	private final ModelPart bipedLeftLeg;
	private final ModelPart bipedRightLeg;

	public PigluttonEntityModel(ModelPart root) {
		body = root.getChild("body");
		neck = body.getChild("chest").getChild("neck");
		bipedLeftArm = body.getChild("chest").getChild("bipedLeftArm");
		bipedRightArm = body.getChild("chest").getChild("bipedRightArm");
		bipedLeftLeg = body.getChild("bipedLeftLeg");
		bipedRightLeg = body.getChild("bipedRightLeg");
	}

	public static TexturedModelData getTexturedModelData() {
		ModelData data = new ModelData();
		ModelPartData root = data.getRoot();
		ModelPartData body = root.addChild("body", ModelPartBuilder.create().uv(0, 18).cuboid(-5.0F, -7.2F, -3.2F, 10.0F, 11.0F, 7.0F).uv(0, 37).cuboid(-5.5F, -8.5F, -7.5F, 11.0F, 11.0F, 5.0F), ModelTransform.of(0.0F, 7.0F, 4.0F, 0.9163F, 0.0F, 0.0F));
		body.addChild("tail_r1", ModelPartBuilder.create().uv(71, 40).cuboid(-2.0F, -4.0F, -1.3F, 4.0F, 4.0F, 5.0F), ModelTransform.of(0.0F, 1.0F, 4.0F, -1.0472F, 0.0F, 0.0F));
		ModelPartData chest = body.addChild("chest", ModelPartBuilder.create().cuboid(-6.0F, -8.6F, -4.0F, 12.0F, 9.0F, 8.0F), ModelTransform.of(0.0F, -5.5979F, -0.1846F, 0.48F, 0.0F, 0.0F));
		chest.addChild("rightPec_r1", ModelPartBuilder.create().uv(41, 38).mirrored(true).cuboid(-4.5F, -7.0F, -2.0F, 7.0F, 7.0F, 4.0F), ModelTransform.of(-2.0F, -2.4021F, -4.8154F, -0.2182F, 0.1047F, -0.0873F));
		chest.addChild("leftPec_r1", ModelPartBuilder.create().uv(41, 38).cuboid(-2.5F, -7.0F, -2.0F, 7.0F, 7.0F, 4.0F), ModelTransform.of(2.0F, -2.4021F, -4.8154F, -0.2182F, -0.1047F, 0.0873F));
		ModelPartData neck = chest.addChild("neck", ModelPartBuilder.create().uv(32, 50).cuboid(-3.5F, -2.5F, -6.0F, 7.0F, 5.0F, 6.0F), ModelTransform.of(0.0F, -6.6F, 1.3F, -1.9635F, 0.0F, 0.0F));
		ModelPartData head = neck.addChild("head", ModelPartBuilder.create().uv(36, 19).cuboid(-4.0F, -3.0F, -6.0F, 8.0F, 6.0F, 6.0F), ModelTransform.of(0.0F, -2.5746F, -3.3132F, 0.6545F, 0.0F, 0.0F));
		ModelPartData upperJaw = head.addChild("upperJaw", ModelPartBuilder.create().uv(42, 1).cuboid(-1.99F, -0.5F, -4.0F, 4.0F, 1.0F, 5.0F), ModelTransform.of(0.0F, 1.3F, -6.0F, 0.0F, 0.0F, 0.0F));
		ModelPartData snout = upperJaw.addChild("snout", ModelPartBuilder.create().uv(41, 0).cuboid(-2.0F, -1.5F, -6.1F, 4.0F, 3.0F, 6.0F), ModelTransform.of(0.0F, -2.1F, 1.5F, 0.1745F, 0.0F, 0.0F));
		snout.addChild("nose", ModelPartBuilder.create().uv(58, 0).cuboid(-2.5F, -1.5F, -1.0F, 5.0F, 3.0F, 1.0F), ModelTransform.of(0.0F, -0.1F, -5.5F, -0.0873F, 0.0F, 0.0F));
		ModelPartData lowerJaw = head.addChild("lowerJaw", ModelPartBuilder.create().uv(41, 11).cuboid(-2.0F, -0.0275F, -4.4022F, 4.0F, 1.0F, 5.0F), ModelTransform.of(0.0F, 1.8F, -5.4F, 0.0F, 0.0F, 0.0F));
		ModelPartData rTusk = lowerJaw.addChild("rTusk", ModelPartBuilder.create().cuboid(-0.5F, -2.5F, -0.5F, 1.0F, 3.0F, 1.0F), ModelTransform.of(-1.9F, 0.1F, -3.4F, 0.0F, 0.0F, -0.3491F));
		rTusk.addChild("rTuskTip", ModelPartBuilder.create().cuboid(-0.5F, -2.0F, -0.5F, 1.0F, 2.0F, 1.0F), ModelTransform.of(0.0F, -2.3F, 0.0F, 0.0F, 0.0F, 0.3491F));
		ModelPartData lTusk = lowerJaw.addChild("lTusk", ModelPartBuilder.create().cuboid(-0.5F, -2.5F, -0.5F, 1.0F, 3.0F, 1.0F), ModelTransform.of(1.9F, 0.1F, -3.4F, 0.0F, 0.0F, 0.3491F));
		lTusk.addChild("lTuskTip", ModelPartBuilder.create().cuboid(-0.5F, -2.0F, -0.5F, 1.0F, 2.0F, 1.0F), ModelTransform.of(0.0F, -2.3F, 0.0F, 0.0F, 0.0F, -0.3491F));
		head.addChild("rEar", ModelPartBuilder.create().uv(35, 32).cuboid(-5.0F, -0.5F, -2.0F, 5.0F, 1.0F, 4.0F), ModelTransform.of(-3.4F, -2.0F, -2.6F, 0.0F, 0.0F, -1.0472F));
		head.addChild("lEar", ModelPartBuilder.create().uv(35, 32).cuboid(0.0F, -0.5F, -2.0F, 5.0F, 1.0F, 4.0F), ModelTransform.of(3.4F, -2.0F, -2.6F, 0.0F, 0.0F, 1.0472F));
		chest.addChild("bipedLeftArm", ModelPartBuilder.create().uv(70, 0).cuboid(-1.0F, -2.0F, -2.0F, 4.0F, 20.0F, 5.0F).uv(69, 26).cuboid(-0.5F, -3.0F, -2.5F, 4.0F, 7.0F, 6.0F), ModelTransform.of(6.0F, -3.4021F, -1.8154F, -1.7017F, 0.0F, -0.0524F));
		chest.addChild("bipedRightArm", ModelPartBuilder.create().uv(70, 0).mirrored(true).cuboid(-3.0F, -3.0F, -1.0F, 4.0F, 20.0F, 5.0F).uv(69, 26).cuboid(-3.5F, -4.0F, -1.5F, 4.0F, 7.0F, 6.0F), ModelTransform.of(-6.0F, -3.4021F, -2.8154F, -1.7017F, 0.0F, 0.0524F));
		ModelPartData bipedRightLeg = body.addChild("bipedRightLeg", ModelPartBuilder.create().uv(89, 0).mirrored(true).cuboid(-3.0F, 1.1F, -2.0F, 6.0F, 12.0F, 6.0F), ModelTransform.of(-2.6F, -0.0263F, 2.3801F, -1.2217F, 0.1222F, 0.0698F));
		ModelPartData rightLeg02 = bipedRightLeg.addChild("rightLeg02", ModelPartBuilder.create().uv(95, 19).mirrored(true).cuboid(-2.0F, -0.5F, -0.1F, 4.0F, 9.0F, 4.0F), ModelTransform.of(-0.1388F, 8.7572F, 3.6969F, 0.0F, 0.0F, 0.0F));
		ModelPartData rightTrotter = rightLeg02.addChild("rightTrotter", ModelPartBuilder.create().uv(112, 15).cuboid(-1.9F, -0.1F, -1.6F, 4.0F, 3.0F, 3.0F), ModelTransform.of(0.0F, 8.1F, 1.3F, 0.3142F, 0.0F, -0.0873F));
		rightTrotter.addChild("rTrotterClaw01", ModelPartBuilder.create().uv(115, 0).mirrored(true).cuboid(-1.0F, -1.3F, -2.0F, 2.0F, 2.0F, 3.0F), ModelTransform.of(-1.1F, 1.5F, -1.1F, 0.6981F, 0.1047F, 0.0349F));
		rightTrotter.addChild("rTrotterClaw02", ModelPartBuilder.create().uv(115, 0).cuboid(-1.0F, -1.3F, -2.0F, 2.0F, 2.0F, 3.0F), ModelTransform.of(1.0F, 1.5F, -1.1F, 0.6981F, -0.1047F, -0.0349F));
		ModelPartData bipedLeftLeg = body.addChild("bipedLeftLeg", ModelPartBuilder.create().uv(89, 0).cuboid(-3.0F, 1.1F, -2.0F, 6.0F, 10.0F, 6.0F), ModelTransform.of(2.6F, -0.0263F, 2.3801F, -1.2217F, -0.1222F, -0.0698F));
		ModelPartData leftLeg02 = bipedLeftLeg.addChild("leftLeg02", ModelPartBuilder.create().uv(95, 19).cuboid(-2.0F, -0.5F, -0.1F, 4.0F, 9.0F, 4.0F), ModelTransform.of(0.1388F, 8.7572F, 3.6969F, 0.0F, 0.0F, 0.0F));
		ModelPartData leftTrotter = leftLeg02.addChild("leftTrotter", ModelPartBuilder.create().uv(112, 15).cuboid(-1.9F, -0.1F, -1.6F, 4.0F, 3.0F, 3.0F), ModelTransform.of(0.0F, 8.1F, 1.3F, 0.3142F, 0.0F, 0.0873F));
		leftTrotter.addChild("lTrotterClaw01", ModelPartBuilder.create().uv(115, 0).cuboid(-1.0F, -1.3F, -2.0F, 2.0F, 2.0F, 3.0F), ModelTransform.of(1.1F, 1.5F, -1.1F, 0.6981F, -0.1047F, -0.0349F));
		leftTrotter.addChild("lTrotterClaw02", ModelPartBuilder.create().uv(115, 0).mirrored(true).cuboid(-1.0F, -1.3F, -2.0F, 2.0F, 2.0F, 3.0F), ModelTransform.of(-1.0F, 1.5F, -1.1F, 0.6981F, 0.1047F, 0.0349F));
		return TexturedModelData.of(data, 128, 64);
	}

	@Override
	public void render(MatrixStack matrixStack, VertexConsumer buffer, int packedLight, int packedOverlay, float red, float green, float blue, float alpha) {
		body.render(matrixStack, buffer, packedLight, packedOverlay);
	}

	@Override
	public void setAngles(T entity, float limbAngle, float limbDistance, float animationProgress, float headYaw, float headPitch) {
		neck.yaw = headYaw * 0.01F;
		neck.pitch = headPitch * 0.01F - 1.5F;
		bipedLeftArm.pitch = (MathHelper.cos(limbAngle * 2 / 3F) * limbDistance * 0.5F) - 5 / 3F;
		bipedRightArm.pitch = (MathHelper.cos(limbAngle * 2 / 3F + (float) Math.PI) * limbDistance * 0.5F) - 5 / 3F - MathHelper.sin((float) (handSwingProgress * Math.PI));
		bipedRightArm.yaw = MathHelper.sin((float) (handSwingProgress * Math.PI));
		bipedRightArm.roll = MathHelper.sin((float) (handSwingProgress * Math.PI));
		bipedLeftLeg.pitch = (MathHelper.cos(limbAngle * 2 / 3F + (float) Math.PI) * limbDistance) - 4 / 5F;
		bipedRightLeg.pitch = (MathHelper.cos(limbAngle * 2 / 3F) * limbDistance) - 4 / 5F;
	}
}
