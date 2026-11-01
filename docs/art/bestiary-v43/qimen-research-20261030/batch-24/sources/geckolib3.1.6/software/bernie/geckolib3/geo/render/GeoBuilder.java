package software.bernie.geckolib3.geo.render;

import java.util.HashMap;
import java.util.Map;
import net.minecraft.class_1160;
import org.apache.commons.lang3.ArrayUtils;
import software.bernie.geckolib3.geo.raw.pojo.Bone;
import software.bernie.geckolib3.geo.raw.pojo.Cube;
import software.bernie.geckolib3.geo.raw.pojo.ModelProperties;
import software.bernie.geckolib3.geo.raw.tree.RawBoneGroup;
import software.bernie.geckolib3.geo.raw.tree.RawGeometryTree;
import software.bernie.geckolib3.geo.render.built.GeoBone;
import software.bernie.geckolib3.geo.render.built.GeoCube;
import software.bernie.geckolib3.geo.render.built.GeoModel;
import software.bernie.geckolib3.util.VectorUtils;

public class GeoBuilder implements IGeoBuilder {

	private static Map<String, IGeoBuilder> moddedGeoBuilders = new HashMap<>();
	private static IGeoBuilder defaultBuilder = new GeoBuilder();

	public static void registerGeoBuilder(String modID, IGeoBuilder builder) {
		moddedGeoBuilders.put(modID, builder);
	}

	public static IGeoBuilder getGeoBuilder(String modID) {
		IGeoBuilder builder = moddedGeoBuilders.get(modID);
		return builder == null ? defaultBuilder : builder;
	}

	@Override
	public GeoModel constructGeoModel(RawGeometryTree geometryTree) {
		GeoModel model = new GeoModel();
		model.properties = geometryTree.properties;
		for (RawBoneGroup rawBone : geometryTree.topLevelBones.values()) {
			model.topLevelBones.add(this.constructBone(rawBone, geometryTree.properties, null));
		}
		return model;
	}

	@Override
	public GeoBone constructBone(RawBoneGroup bone, ModelProperties properties, GeoBone parent) {
		GeoBone geoBone = new GeoBone();

		Bone rawBone = bone.selfBone;
		class_1160 rotation = VectorUtils.convertDoubleToFloat(VectorUtils.fromArray(rawBone.getRotation()));
		class_1160 pivot = VectorUtils.convertDoubleToFloat(VectorUtils.fromArray(rawBone.getPivot()));
		rotation.method_23849(-1, -1, 1);

		geoBone.mirror = rawBone.getMirror();
		geoBone.dontRender = rawBone.getNeverRender();
		geoBone.reset = rawBone.getReset();
		geoBone.inflate = rawBone.getInflate();
		geoBone.parent = parent;
		geoBone.setModelRendererName(rawBone.getName());

		geoBone.setRotationX((float) Math.toRadians(rotation.method_4943()));
		geoBone.setRotationY((float) Math.toRadians(rotation.method_4945()));
		geoBone.setRotationZ((float) Math.toRadians(rotation.method_4947()));

		geoBone.pivotX = -pivot.method_4943();
		geoBone.pivotY = pivot.method_4945();
		geoBone.pivotZ = pivot.method_4947();

		if (!ArrayUtils.isEmpty(rawBone.getCubes())) {
			for (Cube cube : rawBone.getCubes()) {
				geoBone.childCubes.add(GeoCube.createFromPojoCube(cube, properties,
						geoBone.inflate == null ? null : geoBone.inflate / 16, geoBone.mirror));
			}
		}

		for (RawBoneGroup child : bone.children.values()) {
			geoBone.childBones.add(constructBone(child, properties, geoBone));
		}

		return geoBone;
	}
}
