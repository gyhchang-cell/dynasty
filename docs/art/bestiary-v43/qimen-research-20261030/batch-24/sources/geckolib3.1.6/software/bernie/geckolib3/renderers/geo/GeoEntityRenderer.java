package software.bernie.geckolib3.renderers.geo;

import java.util.Collections;
import java.util.Iterator;
import java.util.List;

import com.google.common.collect.Lists;

import net.fabricmc.loader.api.FabricLoader;
import net.minecraft.class_1159;
import net.minecraft.class_1160;
import net.minecraft.class_124;
import net.minecraft.class_1297;
import net.minecraft.class_1304;
import net.minecraft.class_1308;
import net.minecraft.class_1309;
import net.minecraft.class_1657;
import net.minecraft.class_1664;
import net.minecraft.class_1799;
import net.minecraft.class_1921;
import net.minecraft.class_1944;
import net.minecraft.class_2338;
import net.minecraft.class_2350;
import net.minecraft.class_243;
import net.minecraft.class_2960;
import net.minecraft.class_310;
import net.minecraft.class_3532;
import net.minecraft.class_4050;
import net.minecraft.class_4581;
import net.minecraft.class_4587;
import net.minecraft.class_4588;
import net.minecraft.class_4597;
import net.minecraft.class_4608;
import net.minecraft.class_4720;
import net.minecraft.class_5617;
import net.minecraft.class_765;
import net.minecraft.class_897;
import software.bernie.geckolib3.compat.PatchouliCompat;
import software.bernie.geckolib3.core.IAnimatable;
import software.bernie.geckolib3.core.IAnimatableModel;
import software.bernie.geckolib3.core.controller.AnimationController;
import software.bernie.geckolib3.core.event.predicate.AnimationEvent;
import software.bernie.geckolib3.core.util.Color;
import software.bernie.geckolib3.geo.render.built.GeoBone;
import software.bernie.geckolib3.geo.render.built.GeoCube;
import software.bernie.geckolib3.geo.render.built.GeoModel;
import software.bernie.geckolib3.model.AnimatedGeoModel;
import software.bernie.geckolib3.model.provider.GeoModelProvider;
import software.bernie.geckolib3.model.provider.data.EntityModelData;
import software.bernie.geckolib3.util.AnimationUtils;
import software.bernie.geckolib3.util.RenderUtils;

@SuppressWarnings("unchecked")
public abstract class GeoEntityRenderer<T extends class_1309 & IAnimatable> extends class_897<T>
		implements IGeoRenderer<T> {
	static {
		AnimationController.addModelFetcher((IAnimatable object) -> {
			if (object instanceof class_1297) {
				return (IAnimatableModel<Object>) AnimationUtils.getGeoModelForEntity((class_1297) object);
			}
			return null;
		});
	}

	protected final List<GeoLayerRenderer<T>> layerRenderers = Lists.newArrayList();
	protected final AnimatedGeoModel<T> modelProvider;
	private class_1159 renderEarlyMat = new class_1159();

	public class_1799 mainHand;
	public class_1799 offHand;
	public class_1799 helmet;
	public class_1799 chestplate;
	public class_1799 leggings;
	public class_1799 boots;
	public class_4597 rtb;
	public class_2960 whTexture;

	public GeoEntityRenderer(class_5617.class_5618 ctx, AnimatedGeoModel<T> modelProvider) {
		super(ctx);
		this.modelProvider = modelProvider;
	}

	public static int getPackedOverlay(class_1309 livingEntityIn, float uIn) {
		return class_4608.method_23624(class_4608.method_23210(uIn),
				livingEntityIn.field_6235 > 0 || livingEntityIn.field_6213 > 0);
	}

	private static float getFacingAngle(class_2350 facingIn) {
		switch (facingIn) {
		case field_11035:
			return 90.0F;
		case field_11043:
			return 270.0F;
		case field_11034:
			return 180.0F;
		case field_11039:
		default:
			return 0.0F;
		}
	}

	@SuppressWarnings("resource")
	@Override
	public void render(T entity, float entityYaw, float partialTicks, class_4587 stack,
			class_4597 bufferIn, int packedLightIn) {
		stack.method_22903();
		boolean shouldSit = entity.method_5765() && (entity.method_5854() != null);
		EntityModelData entityModelData = new EntityModelData();
		entityModelData.isSitting = shouldSit;
		entityModelData.isChild = entity.method_6109();

		float f = class_3532.method_17821(partialTicks, entity.field_6220, entity.field_6283);
		float f1 = class_3532.method_17821(partialTicks, entity.field_6259, entity.field_6241);
		float netHeadYaw = f1 - f;
		if (shouldSit && entity.method_5854() instanceof class_1309) {
			class_1309 livingentity = (class_1309) entity.method_5854();
			f = class_3532.method_17821(partialTicks, livingentity.field_6220, livingentity.field_6283);
			netHeadYaw = f1 - f;
			float f3 = class_3532.method_15393(netHeadYaw);
			if (f3 < -85.0F) {
				f3 = -85.0F;
			}

			if (f3 >= 85.0F) {
				f3 = 85.0F;
			}

			f = f1 - f3;
			if (f3 * f3 > 2500.0F) {
				f += f3 * 0.2F;
			}

			netHeadYaw = f1 - f;
		}

		float headPitch = class_3532.method_16439(partialTicks, entity.method_36455(), entity.method_36455());
		if (entity.method_18376() == class_4050.field_18078) {
			class_2350 direction = entity.method_18401();
			if (direction != null) {
				float f4 = entity.method_18381(class_4050.field_18076) - 0.1F;
				stack.method_22904((float) (-direction.method_10148()) * f4, 0.0D, (float) (-direction.method_10165()) * f4);
			}
		}
		float f7 = this.handleRotationFloat(entity, partialTicks);
		this.applyRotations(entity, stack, f7, f, partialTicks);

		float lastLimbDistance = 0.0F;
		float limbSwing = 0.0F;
		if (!shouldSit && entity.method_5805()) {
			lastLimbDistance = class_3532.method_16439(partialTicks, entity.field_6211, entity.field_6225);
			limbSwing = entity.field_6249 - entity.field_6225 * (1.0F - partialTicks);
			if (entity.method_6109()) {
				limbSwing *= 3.0F;
			}

			if (lastLimbDistance > 1.0F) {
				lastLimbDistance = 1.0F;
			}
		}
		entityModelData.headPitch = -headPitch;
		entityModelData.netHeadYaw = -netHeadYaw;

		AnimationEvent<T> predicate = new AnimationEvent<T>(entity, limbSwing, lastLimbDistance, partialTicks,
				!(lastLimbDistance > -0.15F && lastLimbDistance < 0.15F), Collections.singletonList(entityModelData));
		GeoModel model = modelProvider.getModel(modelProvider.getModelResource(entity));
		if (modelProvider instanceof IAnimatableModel) {
			((IAnimatableModel<T>) modelProvider).setLivingAnimations(entity, this.getUniqueID(entity), predicate);
		}

		stack.method_22904(0, 0.01f, 0);
		class_310.method_1551().method_1531().method_22813(getTexture(entity));
		Color renderColor = getRenderColor(entity, partialTicks, stack, bufferIn, null, packedLightIn);
		class_1921 renderType = getRenderType(entity, partialTicks, stack, bufferIn, null, packedLightIn,
				getTexture(entity));
		if (!entity.method_5756(class_310.method_1551().field_1724))
			render(model, entity, partialTicks, renderType, stack, bufferIn,
					class_4720.method_24037(bufferIn.getBuffer(class_1921.method_29707()),
							bufferIn.getBuffer(class_1921.method_23689(getTextureResource(entity)))),
					packedLightIn, getPackedOverlay(entity, 0), (float) renderColor.getRed() / 255f,
					(float) renderColor.getGreen() / 255f, (float) renderColor.getBlue() / 255f,
					(float) renderColor.getAlpha() / 255);

		if (!entity.method_7325()) {
			for (GeoLayerRenderer<T> layerRenderer : this.layerRenderers) {
				this.renderLayer(stack, bufferIn, packedLightIn, entity, limbSwing, lastLimbDistance, partialTicks, f7,
						netHeadYaw, headPitch, bufferIn, layerRenderer);
			}
		}
		if (entity instanceof class_1308) {
			class_1297 leashHolder = ((class_1308) entity).method_5933();
			if (leashHolder != null) {
				this.renderLeash(entity, partialTicks, stack, bufferIn, leashHolder);
			}
		}
		if (FabricLoader.getInstance().isModLoaded("patchouli")) {
			PatchouliCompat.patchouliLoaded(stack);
		}
		stack.method_22909();
		super.method_3936(entity, entityYaw, partialTicks, stack, bufferIn, packedLightIn);
	}

	protected void renderLayer(class_4587 stack, class_4597 bufferIn, int packedLightIn, T entity,
			float limbSwing, float limbSwingAmount, float partialTicks, float rotFloat, float netHeadYaw,
			float headPitch, class_4597 bufferIn2, GeoLayerRenderer<T> layerRenderer) {
		layerRenderer.render(stack, bufferIn, packedLightIn, entity, limbSwing, limbSwingAmount, partialTicks, rotFloat,
				netHeadYaw, headPitch);
	}

	@Override
	public Integer getUniqueID(T animatable) {
		return animatable.method_5667().hashCode();
	}

	@Override
	public void renderEarly(T animatable, class_4587 stackIn, float ticks, class_4597 renderTypeBuffer,
			class_4588 vertexBuilder, int packedLightIn, int packedOverlayIn, float red, float green, float blue,
			float partialTicks) {
		renderEarlyMat = stackIn.method_23760().method_23761().method_22673();
		this.mainHand = animatable.method_6118(class_1304.field_6173);
		this.offHand = animatable.method_6118(class_1304.field_6171);
		this.helmet = animatable.method_6118(class_1304.field_6169);
		this.chestplate = animatable.method_6118(class_1304.field_6174);
		this.leggings = animatable.method_6118(class_1304.field_6172);
		this.boots = animatable.method_6118(class_1304.field_6166);
		this.rtb = renderTypeBuffer;
		this.whTexture = this.getTextureResource(animatable);
		IGeoRenderer.super.renderEarly(animatable, stackIn, ticks, renderTypeBuffer, vertexBuilder, packedLightIn,
				packedOverlayIn, red, green, blue, partialTicks);
	}

	@Override
	public void renderRecursively(GeoBone bone, class_4587 stack, class_4588 bufferIn, int packedLightIn,
			int packedOverlayIn, float red, float green, float blue, float alpha) {
		stack.method_22903();
		boolean rotOverride = bone.rotMat != null;
		RenderUtils.translate(bone, stack);
		RenderUtils.moveToPivot(bone, stack);
		if (rotOverride) {
			stack.method_23760().method_23761().method_22672(bone.rotMat);
			stack.method_23760().method_23762().method_22855(new class_4581(bone.rotMat));
		} else {
			RenderUtils.rotate(bone, stack);
		}
		RenderUtils.scale(bone, stack);
		if (bone.isTrackingXform()) {
			class_4587.class_4665 entry = stack.method_23760();
			class_1159 matBone = entry.method_23761().method_22673();
			bone.setWorldSpaceXform(matBone.method_22673());

			class_1159 renderEarlyMatInvert = renderEarlyMat.method_22673();
			renderEarlyMatInvert.method_22870();
			matBone.method_22672(renderEarlyMatInvert);
			bone.setModelSpaceXform(matBone);
		}
		RenderUtils.moveBackFromPivot(bone, stack);

		if (!bone.isHidden) {
			Iterator<?> var10 = bone.childCubes.iterator();

			while (var10.hasNext()) {
				GeoCube cube = (GeoCube) var10.next();
				stack.method_22903();
				this.renderCube(cube, stack, bufferIn, packedLightIn, packedOverlayIn, red, green, blue, alpha);
				stack.method_22909();
			}

			var10 = bone.childBones.iterator();

			while (var10.hasNext()) {
				GeoBone childBone = (GeoBone) var10.next();
				this.renderRecursively(childBone, stack, bufferIn, packedLightIn, packedOverlayIn, red, green, blue,
						alpha);
			}
		}

		stack.method_22909();
	}

	@Override
	public class_2960 getTexture(T entity) {
		return getTextureResource(entity);
	}

	@Override
	public GeoModelProvider<T> getGeoModelProvider() {
		return this.modelProvider;
	}

	protected void applyRotations(T entityLiving, class_4587 matrixStackIn, float ageInTicks, float rotationYaw,
			float partialTicks) {
		class_4050 pose = entityLiving.method_18376();
		if (pose != class_4050.field_18078) {
			matrixStackIn.method_22907(class_1160.field_20705.method_23214(180.0F - rotationYaw));
		}

		if (entityLiving.field_6213 > 0) {
			float f = ((float) entityLiving.field_6213 + partialTicks - 1.0F) / 20.0F * 1.6F;
			f = class_3532.method_15355(f);
			if (f > 1.0F) {
				f = 1.0F;
			}

			matrixStackIn.method_22907(class_1160.field_20707.method_23214(f * this.getDeathMaxRotation(entityLiving)));
		} else if (entityLiving.method_6123()) {
			matrixStackIn.method_22907(class_1160.field_20703.method_23214(-90.0F - entityLiving.method_36455()));
			matrixStackIn.method_22907(
					class_1160.field_20705.method_23214(((float) entityLiving.field_6012 + partialTicks) * -75.0F));
		} else if (pose == class_4050.field_18078) {
			class_2350 direction = entityLiving.method_18401();
			float f1 = direction != null ? getFacingAngle(direction) : rotationYaw;
			matrixStackIn.method_22907(class_1160.field_20705.method_23214(f1));
			matrixStackIn.method_22907(class_1160.field_20707.method_23214(this.getDeathMaxRotation(entityLiving)));
			matrixStackIn.method_22907(class_1160.field_20705.method_23214(270.0F));
		} else if (entityLiving.method_16914() || entityLiving instanceof class_1657) {
			String s = class_124.method_539(entityLiving.method_5477().getString());
			if (("Dinnerbone".equals(s) || "Grumm".equals(s)) && (!(entityLiving instanceof class_1657)
					|| ((class_1657) entityLiving).method_7348(class_1664.field_7559))) {
				matrixStackIn.method_22904(0.0D, entityLiving.method_17682() + 0.1F, 0.0D);
				matrixStackIn.method_22907(class_1160.field_20707.method_23214(180.0F));
			}
		}

	}

	@Override
	protected boolean hasLabel(T entity) {
		double d0 = this.field_4676.method_23168(entity);
		float f = entity.method_5715() ? 32.0F : 64.0F;
		if (d0 >= (double) (f * f)) {
			return false;
		} else {
			return entity == this.field_4676.field_4678 && entity.method_16914();
		}
	}

	protected boolean isVisible(T livingEntityIn) {
		return !livingEntityIn.method_5767();
	}

	protected float getDeathMaxRotation(T entityLivingBaseIn) {
		return 90.0F;
	}

	/**
	 * Returns where in the swing animation the living entity is (from 0 to 1). Args
	 * : entity, partialTickTime
	 */
	protected float getHandSwingProgress(T livingBase, float partialTickTime) {
		return livingBase.method_6055(partialTickTime);
	}

	/**
	 * Defines what float the third param in setRotationAngles of ModelBase is
	 */
	protected float handleRotationFloat(T livingBase, float partialTicks) {
		return (float) livingBase.field_6012 + partialTicks;
	}

	@Override
	public class_2960 getTextureResource(T instance) {
		return this.modelProvider.getTextureResource(instance);
	}

	public final boolean addLayer(GeoLayerRenderer<T> layer) {
		return this.layerRenderers.add(layer);
	}

	private <E extends class_1297> void renderLeash(T entity, float partialTicks, class_4587 poseStack,
			class_4597 buffer, E leashHolder) {
		int u;
		poseStack.method_22903();
		class_243 vec3d = leashHolder.method_30951(partialTicks);
		double d = (double) (class_3532.method_16439(partialTicks, entity.field_6283, entity.field_6220)
				* ((float) Math.PI / 180)) + 1.5707963267948966;
		class_243 vec3d2 = ((class_1297) entity).method_29919();
		double e = Math.cos(d) * vec3d2.field_1350 + Math.sin(d) * vec3d2.field_1352;
		double f = Math.sin(d) * vec3d2.field_1350 - Math.cos(d) * vec3d2.field_1352;
		double g = class_3532.method_16436(partialTicks, entity.field_6014, entity.method_23317()) + e;
		double h = class_3532.method_16436(partialTicks, entity.field_6036, entity.method_23318()) + vec3d2.field_1351;
		double i = class_3532.method_16436(partialTicks, entity.field_5969, entity.method_23321()) + f;
		poseStack.method_22904(e, vec3d2.field_1351, f);
		float j = (float) (vec3d.field_1352 - g);
		float k = (float) (vec3d.field_1351 - h);
		float l = (float) (vec3d.field_1350 - i);
		class_4588 vertexConsumer = buffer.getBuffer(class_1921.method_23587());
		class_1159 matrix4f = poseStack.method_23760().method_23761();
		float n = class_3532.method_22858(j * j + l * l) * 0.025f / 2.0f;
		float o = l * n;
		float p = j * n;
		class_2338 blockPos = new class_2338(entity.method_5836(partialTicks));
		class_2338 blockPos2 = new class_2338(leashHolder.method_5836(partialTicks));
		int q = this.method_24087(entity, blockPos);
		int r = leashHolder.method_5809() ? 15 : leashHolder.field_6002.method_8314(class_1944.field_9282, blockPos2);
		int s = entity.field_6002.method_8314(class_1944.field_9284, blockPos);
		int t = entity.field_6002.method_8314(class_1944.field_9284, blockPos2);
		for (u = 0; u <= 24; ++u) {
			GeoEntityRenderer.renderLeashPiece(vertexConsumer, matrix4f, j, k, l, q, r, s, t, 0.025f, 0.025f, o, p, u,
					false);
		}
		for (u = 24; u >= 0; --u) {
			GeoEntityRenderer.renderLeashPiece(vertexConsumer, matrix4f, j, k, l, q, r, s, t, 0.025f, 0.0f, o, p, u,
					true);
		}
		poseStack.method_22909();
	}

	private static void renderLeashPiece(class_4588 vertexConsumer, class_1159 positionMatrix, float f, float g,
			float h, int leashedEntityBlockLight, int holdingEntityBlockLight, int leashedEntitySkyLight,
			int holdingEntitySkyLight, float i, float j, float k, float l, int pieceIndex, boolean isLeashKnot) {
		float m = (float) pieceIndex / 24.0f;
		int n = (int) class_3532.method_16439(m, leashedEntityBlockLight, holdingEntityBlockLight);
		int o = (int) class_3532.method_16439(m, leashedEntitySkyLight, holdingEntitySkyLight);
		int p = class_765.method_23687(n, o);
		float q = pieceIndex % 2 == (isLeashKnot ? 1 : 0) ? 0.7f : 1.0f;
		float r = 0.5f * q;
		float s = 0.4f * q;
		float t = 0.3f * q;
		float u = f * m;
		float v = g > 0.0f ? g * m * m : g - g * (1.0f - m) * (1.0f - m);
		float w = h * m;
		vertexConsumer.method_22918(positionMatrix, u - k, v + j, w + l).method_22915(r, s, t, 1.0f).method_22916(p).method_1344();
		vertexConsumer.method_22918(positionMatrix, u + k, v + i - j, w - l).method_22915(r, s, t, 1.0f).method_22916(p).method_1344();
	}
}
