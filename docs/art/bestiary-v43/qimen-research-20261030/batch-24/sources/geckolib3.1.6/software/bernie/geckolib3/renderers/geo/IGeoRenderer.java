package software.bernie.geckolib3.renderers.geo;

import net.minecraft.class_1159;
import net.minecraft.class_1160;
import net.minecraft.class_1162;
import net.minecraft.class_1921;
import net.minecraft.class_2960;
import net.minecraft.class_4581;
import net.minecraft.class_4587;
import net.minecraft.class_4588;
import net.minecraft.class_4597;
import software.bernie.geckolib3.core.util.Color;
import software.bernie.geckolib3.geo.render.built.GeoBone;
import software.bernie.geckolib3.geo.render.built.GeoCube;
import software.bernie.geckolib3.geo.render.built.GeoModel;
import software.bernie.geckolib3.geo.render.built.GeoQuad;
import software.bernie.geckolib3.geo.render.built.GeoVertex;
import software.bernie.geckolib3.model.provider.GeoModelProvider;
import software.bernie.geckolib3.util.RenderUtils;

public interface IGeoRenderer<T> {
	default void render(GeoModel model, T animatable, float partialTicks, class_1921 type, class_4587 matrixStackIn,
			class_4597 renderTypeBuffer, class_4588 vertexBuilder, int packedLightIn,
			int packedOverlayIn, float red, float green, float blue, float alpha) {
		renderEarly(animatable, matrixStackIn, partialTicks, renderTypeBuffer, vertexBuilder, packedLightIn,
				packedOverlayIn, red, green, blue, alpha);

		if (renderTypeBuffer != null) {
			vertexBuilder = renderTypeBuffer.getBuffer(type);
		}
		renderLate(animatable, matrixStackIn, partialTicks, renderTypeBuffer, vertexBuilder, packedLightIn,
				packedOverlayIn, red, green, blue, alpha);
		// Render all top level bones
		for (GeoBone group : model.topLevelBones) {
			renderRecursively(group, matrixStackIn, vertexBuilder, packedLightIn, packedOverlayIn, red, green, blue,
					alpha);
		}
	}

	default void renderRecursively(GeoBone bone, class_4587 stack, class_4588 bufferIn, int packedLightIn,
			int packedOverlayIn, float red, float green, float blue, float alpha) {
		stack.method_22903();
		RenderUtils.translate(bone, stack);
		RenderUtils.moveToPivot(bone, stack);
		RenderUtils.rotate(bone, stack);
		RenderUtils.scale(bone, stack);
		RenderUtils.moveBackFromPivot(bone, stack);

		if (!bone.isHidden()) {
			for (GeoCube cube : bone.childCubes) {
				stack.method_22903();
				if (!bone.cubesAreHidden()) {
					renderCube(cube, stack, bufferIn, packedLightIn, packedOverlayIn, red, green, blue, alpha);
				}
				stack.method_22909();
			}
		}
		if (!bone.childBonesAreHiddenToo()) {
			for (GeoBone childBone : bone.childBones) {
				renderRecursively(childBone, stack, bufferIn, packedLightIn, packedOverlayIn, red, green, blue, alpha);
			}
		}

		stack.method_22909();
	}

	default void renderCube(GeoCube cube, class_4587 stack, class_4588 bufferIn, int packedLightIn,
			int packedOverlayIn, float red, float green, float blue, float alpha) {
		RenderUtils.moveToPivot(cube, stack);
		RenderUtils.rotate(cube, stack);
		RenderUtils.moveBackFromPivot(cube, stack);
		class_4581 matrix3f = stack.method_23760().method_23762();
		class_1159 matrix4f = stack.method_23760().method_23761();

		for (GeoQuad quad : cube.quads) {
			if (quad == null) {
				continue;
			}
			class_1160 normal = quad.normal.method_23850();
			normal.method_23215(matrix3f);

			if ((cube.size.method_4945() == 0 || cube.size.method_4947() == 0) && normal.method_4943() < 0) {
				normal.method_23849(-1, 1, 1);
			}
			if ((cube.size.method_4943() == 0 || cube.size.method_4947() == 0) && normal.method_4945() < 0) {
				normal.method_23849(1, -1, 1);
			}
			if ((cube.size.method_4943() == 0 || cube.size.method_4945() == 0) && normal.method_4947() < 0) {
				normal.method_23849(1, 1, -1);
			}

			for (GeoVertex vertex : quad.vertices) {
				class_1162 vector4f = new class_1162(vertex.position.method_4943(), vertex.position.method_4945(), vertex.position.method_4947(),
						1.0F);
				vector4f.method_22674(matrix4f);
				bufferIn.method_23919(vector4f.method_4953(), vector4f.method_4956(), vector4f.method_4957(), red, green, blue, alpha,
						vertex.textureU, vertex.textureV, packedOverlayIn, packedLightIn, normal.method_4943(), normal.method_4945(),
						normal.method_4947());
			}
		}
	}

	@SuppressWarnings("rawtypes")
	GeoModelProvider getGeoModelProvider();

	class_2960 getTextureResource(T instance);

	default void renderEarly(T animatable, class_4587 stackIn, float partialTicks,
			class_4597 renderTypeBuffer, class_4588 vertexBuilder, int packedLightIn,
			int packedOverlayIn, float red, float green, float blue, float alpha) {
	}

	default void renderLate(T animatable, class_4587 stackIn, float partialTicks, class_4597 renderTypeBuffer,
			class_4588 bufferIn, int packedLightIn, int packedOverlayIn, float red, float green, float blue,
			float alpha) {
	}

	default class_1921 getRenderType(T animatable, float partialTicks, class_4587 stack,
			class_4597 renderTypeBuffer, class_4588 vertexBuilder, int packedLightIn,
			class_2960 textureLocation) {
		return class_1921.method_23576(textureLocation);
	}

	default Color getRenderColor(T animatable, float partialTicks, class_4587 stack,
			class_4597 renderTypeBuffer, class_4588 vertexBuilder, int packedLightIn) {
		return Color.ofRGBA(255, 255, 255, 255);
	}

	default Integer getUniqueID(T animatable) {
		return animatable.hashCode();
	}
}
