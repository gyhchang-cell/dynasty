package software.bernie.geckolib3.util;

import net.minecraft.class_1158;
import net.minecraft.class_1160;
import net.minecraft.class_4587;
import software.bernie.geckolib3.geo.render.built.GeoBone;
import software.bernie.geckolib3.geo.render.built.GeoCube;

public class RenderUtils {
	public static void moveToPivot(GeoCube cube, class_4587 stack) {
		class_1160 pivot = cube.pivot;
		stack.method_22904(pivot.method_4943() / 16, pivot.method_4945() / 16, pivot.method_4947() / 16);
	}

	public static void moveBackFromPivot(GeoCube cube, class_4587 stack) {
		class_1160 pivot = cube.pivot;
		stack.method_22904(-pivot.method_4943() / 16, -pivot.method_4945() / 16, -pivot.method_4947() / 16);
	}

	public static void moveToPivot(GeoBone bone, class_4587 stack) {
		stack.method_22904(bone.pivotX / 16, bone.pivotY / 16, bone.pivotZ / 16);
	}

	public static void moveBackFromPivot(GeoBone bone, class_4587 stack) {
		stack.method_22904(-bone.pivotX / 16, -bone.pivotY / 16, -bone.pivotZ / 16);
	}

	public static void scale(GeoBone bone, class_4587 stack) {
		stack.method_22905(bone.getScaleX(), bone.getScaleY(), bone.getScaleZ());
	}

	public static void translate(GeoBone bone, class_4587 stack) {
		stack.method_22904(-bone.getPositionX() / 16, bone.getPositionY() / 16, bone.getPositionZ() / 16);
	}

	public static void rotate(GeoBone bone, class_4587 stack) {
		if (bone.getRotationZ() != 0.0F) {
			stack.method_22907(class_1160.field_20707.method_23626(bone.getRotationZ()));
		}

		if (bone.getRotationY() != 0.0F) {
			stack.method_22907(class_1160.field_20705.method_23626(bone.getRotationY()));
		}

		if (bone.getRotationX() != 0.0F) {
			stack.method_22907(class_1160.field_20703.method_23626(bone.getRotationX()));
		}
	}

	public static void rotate(GeoCube bone, class_4587 stack) {
		class_1160 rotation = bone.rotation;

		stack.method_22907(new class_1158(0, 0, rotation.method_4947(), false));
		stack.method_22907(new class_1158(0, rotation.method_4945(), 0, false));
		stack.method_22907(new class_1158(rotation.method_4943(), 0, 0, false));
	}
}
