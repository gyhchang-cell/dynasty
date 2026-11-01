package software.bernie.geckolib3.geo.render.built;

import net.minecraft.class_1160;
import net.minecraft.class_1161;
import net.minecraft.class_2350;
import software.bernie.geckolib3.geo.raw.pojo.*;
import software.bernie.geckolib3.util.VectorUtils;

public class GeoCube {
	public GeoQuad[] quads = new GeoQuad[6];
	public class_1160 pivot;
	public class_1160 rotation;
	public class_1160 size = new class_1160();
	public double inflate;
	public Boolean mirror;

	private GeoCube(double[] size) {
		if (size.length >= 3) {
			this.size.method_4949((float) size[0], (float) size[1], (float) size[2]);
		}
	}

	public static GeoCube createFromPojoCube(Cube cubeIn, ModelProperties properties, Double boneInflate,
			Boolean mirror) {
		GeoCube cube = new GeoCube(cubeIn.getSize());

		UvUnion uvUnion = cubeIn.getUv();
		UvFaces faces = uvUnion.faceUV;
		boolean isBoxUV = uvUnion.isBoxUV;
		cube.mirror = cubeIn.getMirror();
		cube.inflate = cubeIn.getInflate() == null ? (boneInflate == null ? 0 : boneInflate) : cubeIn.getInflate() / 16;

		float textureHeight = properties.getTextureHeight().floatValue();
		float textureWidth = properties.getTextureWidth().floatValue();

		class_1161 size = VectorUtils.fromArray(cubeIn.getSize());
		class_1161 origin = VectorUtils.fromArray(cubeIn.getOrigin());
		origin.field_5661 = -(origin.field_5661 + size.field_5661) / 16;
		origin.field_5660 /= 16;
		origin.field_5659 /= 16;

		size.field_5661 /= 16;
		size.field_5660 /= 16;
		size.field_5659 /= 16;

		if (size.field_5661 == 0) {
			size.field_5661 = 0f;
		}
		if (size.field_5660 == 0) {
			size.field_5660 = 0f;
		}
		if (size.field_5659 == 0) {
			size.field_5659 = 0f;
		}
		class_1160 rotation = VectorUtils.convertDoubleToFloat(VectorUtils.fromArray(cubeIn.getRotation()));
		rotation.method_23849(-1, -1, 1);

		rotation.method_4949((float) Math.toRadians(rotation.method_4943()), (float) Math.toRadians(rotation.method_4945()),
				(float) Math.toRadians(rotation.method_4947()));

		class_1160 pivot = VectorUtils.convertDoubleToFloat(VectorUtils.fromArray(cubeIn.getPivot()));
		pivot.method_23849(-1, 1, 1);

		cube.pivot = pivot;
		cube.rotation = rotation;

		//
		//
		// P7 P8
		// - - - - - - - - - - - - -
		// | \ | \
		// | \ | \
		// | \ | \
		// | \ | \
		// Y | \ | \
		// | \ | \
		// | \ P3 | \ P4
		// | - - - - - - - - - - - - -
		// | | | |
		// | | | |
		// | | | |
		// P5 - - - - - - - - | - - - - P6 |
		// \ | \ |
		// \ | \ |
		// \ | \ |
		// X \ | \ |
		// \ | \ |
		// \ | \ |
		// \ | \ |
		// - - - - - - - - - - - - -
		// P1 P2
		// Z
		// this drawing corresponds to the points declared below
		//

		// Making all 8 points of the cube using the origin (where the Z, X, and Y
		// values are smallest) and offseting each point by the right size values
		GeoVertex P1 = new GeoVertex(origin.field_5661 - cube.inflate, origin.field_5660 - cube.inflate, origin.field_5659 - cube.inflate);
		GeoVertex P2 = new GeoVertex(origin.field_5661 - cube.inflate, origin.field_5660 - cube.inflate,
				origin.field_5659 + size.field_5659 + cube.inflate);
		GeoVertex P3 = new GeoVertex(origin.field_5661 - cube.inflate, origin.field_5660 + size.field_5660 + cube.inflate,
				origin.field_5659 - cube.inflate);
		GeoVertex P4 = new GeoVertex(origin.field_5661 - cube.inflate, origin.field_5660 + size.field_5660 + cube.inflate,
				origin.field_5659 + size.field_5659 + cube.inflate);
		GeoVertex P5 = new GeoVertex(origin.field_5661 + size.field_5661 + cube.inflate, origin.field_5660 - cube.inflate,
				origin.field_5659 - cube.inflate);
		GeoVertex P6 = new GeoVertex(origin.field_5661 + size.field_5661 + cube.inflate, origin.field_5660 - cube.inflate,
				origin.field_5659 + size.field_5659 + cube.inflate);
		GeoVertex P7 = new GeoVertex(origin.field_5661 + size.field_5661 + cube.inflate, origin.field_5660 + size.field_5660 + cube.inflate,
				origin.field_5659 - cube.inflate);
		GeoVertex P8 = new GeoVertex(origin.field_5661 + size.field_5661 + cube.inflate, origin.field_5660 + size.field_5660 + cube.inflate,
				origin.field_5659 + size.field_5659 + cube.inflate);

		GeoQuad quadWest;
		GeoQuad quadEast;
		GeoQuad quadNorth;
		GeoQuad quadSouth;
		GeoQuad quadUp;
		GeoQuad quadDown;

		if (!isBoxUV) {
			FaceUv west = faces.getWest();
			FaceUv east = faces.getEast();
			FaceUv north = faces.getNorth();
			FaceUv south = faces.getSouth();
			FaceUv up = faces.getUp();
			FaceUv down = faces.getDown();
			// Pass in vertices starting from the top right corner, then going
			// counter-clockwise
			quadWest = west == null ? null
					: new GeoQuad(new GeoVertex[] { P4, P3, P1, P2 }, west.getUv(), west.getUvSize(), textureWidth,
							textureHeight, cubeIn.getMirror(), class_2350.field_11039);
			quadEast = east == null ? null
					: new GeoQuad(new GeoVertex[] { P7, P8, P6, P5 }, east.getUv(), east.getUvSize(), textureWidth,
							textureHeight, cubeIn.getMirror(), class_2350.field_11034);
			quadNorth = north == null ? null
					: new GeoQuad(new GeoVertex[] { P3, P7, P5, P1 }, north.getUv(), north.getUvSize(), textureWidth,
							textureHeight, cubeIn.getMirror(), class_2350.field_11043);
			quadSouth = south == null ? null
					: new GeoQuad(new GeoVertex[] { P8, P4, P2, P6 }, south.getUv(), south.getUvSize(), textureWidth,
							textureHeight, cubeIn.getMirror(), class_2350.field_11035);
			quadUp = up == null ? null
					: new GeoQuad(new GeoVertex[] { P4, P8, P7, P3 }, up.getUv(), up.getUvSize(), textureWidth,
							textureHeight, cubeIn.getMirror(), class_2350.field_11036);
			quadDown = down == null ? null
					: new GeoQuad(new GeoVertex[] { P1, P5, P6, P2 }, down.getUv(), down.getUvSize(), textureWidth,
							textureHeight, cubeIn.getMirror(), class_2350.field_11033);

			if (cubeIn.getMirror() == Boolean.TRUE || mirror == Boolean.TRUE) {
				quadWest = west == null ? null
						: new GeoQuad(new GeoVertex[] { P7, P8, P6, P5 }, west.getUv(), west.getUvSize(), textureWidth,
								textureHeight, cubeIn.getMirror(), class_2350.field_11039);
				quadEast = east == null ? null
						: new GeoQuad(new GeoVertex[] { P4, P3, P1, P2 }, east.getUv(), east.getUvSize(), textureWidth,
								textureHeight, cubeIn.getMirror(), class_2350.field_11034);
			}
		} else {
			double[] UV = cubeIn.getUv().boxUVCoords;
			class_1161 UVSize = VectorUtils.fromArray(cubeIn.getSize());
			UVSize = new class_1161(Math.floor(UVSize.field_5661), Math.floor(UVSize.field_5660), Math.floor(UVSize.field_5659));

			quadWest = new GeoQuad(new GeoVertex[] { P4, P3, P1, P2 },
					new double[] { UV[0] + UVSize.field_5659 + UVSize.field_5661, UV[1] + UVSize.field_5659 }, new double[] { UVSize.field_5659, UVSize.field_5660 },
					textureWidth, textureHeight, cubeIn.getMirror(), class_2350.field_11039);
			quadEast = new GeoQuad(new GeoVertex[] { P7, P8, P6, P5 }, new double[] { UV[0], UV[1] + UVSize.field_5659 },
					new double[] { UVSize.field_5659, UVSize.field_5660 }, textureWidth, textureHeight, cubeIn.getMirror(),
					class_2350.field_11034);
			quadNorth = new GeoQuad(new GeoVertex[] { P3, P7, P5, P1 },
					new double[] { UV[0] + UVSize.field_5659, UV[1] + UVSize.field_5659 }, new double[] { UVSize.field_5661, UVSize.field_5660 },
					textureWidth, textureHeight, cubeIn.getMirror(), class_2350.field_11043);
			quadSouth = new GeoQuad(new GeoVertex[] { P8, P4, P2, P6 },
					new double[] { UV[0] + UVSize.field_5659 + UVSize.field_5661 + UVSize.field_5659, UV[1] + UVSize.field_5659 },
					new double[] { UVSize.field_5661, UVSize.field_5660 }, textureWidth, textureHeight, cubeIn.getMirror(),
					class_2350.field_11035);
			quadUp = new GeoQuad(new GeoVertex[] { P4, P8, P7, P3 }, new double[] { UV[0] + UVSize.field_5659, UV[1] },
					new double[] { UVSize.field_5661, UVSize.field_5659 }, textureWidth, textureHeight, cubeIn.getMirror(), class_2350.field_11036);
			quadDown = new GeoQuad(new GeoVertex[] { P1, P5, P6, P2 },
					new double[] { UV[0] + UVSize.field_5659 + UVSize.field_5661, UV[1] + UVSize.field_5659 },
					new double[] { UVSize.field_5661, -UVSize.field_5659 }, textureWidth, textureHeight, cubeIn.getMirror(),
					class_2350.field_11033);

			if (cubeIn.getMirror() == Boolean.TRUE || mirror == Boolean.TRUE) {
				quadWest = new GeoQuad(new GeoVertex[] { P7, P8, P6, P5 },
						new double[] { UV[0] + UVSize.field_5659 + UVSize.field_5661, UV[1] + UVSize.field_5659 },
						new double[] { UVSize.field_5659, UVSize.field_5660 }, textureWidth, textureHeight, cubeIn.getMirror(),
						class_2350.field_11039);
				quadEast = new GeoQuad(new GeoVertex[] { P4, P3, P1, P2 }, new double[] { UV[0], UV[1] + UVSize.field_5659 },
						new double[] { UVSize.field_5659, UVSize.field_5660 }, textureWidth, textureHeight, cubeIn.getMirror(),
						class_2350.field_11034);
			}
		}

		cube.quads[0] = quadWest;
		cube.quads[1] = quadEast;
		cube.quads[2] = quadNorth;
		cube.quads[3] = quadSouth;
		cube.quads[4] = quadUp;
		cube.quads[5] = quadDown;
		return cube;
	}
}
