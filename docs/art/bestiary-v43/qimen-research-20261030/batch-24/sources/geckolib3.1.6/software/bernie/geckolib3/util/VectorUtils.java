package software.bernie.geckolib3.util;

import net.minecraft.class_1160;
import net.minecraft.class_1161;
import org.apache.commons.lang3.ArrayUtils;
import org.apache.commons.lang3.Validate;

public class VectorUtils {
	public static class_1161 fromArray(double[] array) {
		Validate.validIndex(ArrayUtils.toObject(array), 2);
		return new class_1161(array[0], array[1], array[2]);
	}

	public static class_1160 fromArray(float[] array) {
		Validate.validIndex(ArrayUtils.toObject(array), 2);
		return new class_1160(array[0], array[1], array[2]);
	}

	public static class_1160 convertDoubleToFloat(class_1161 vector) {
		return new class_1160((float) vector.field_5661, (float) vector.field_5660, (float) vector.field_5659);
	}

	public static class_1161 convertFloatToDouble(class_1160 vector) {
		return new class_1161(vector.method_4943(), vector.method_4945(), vector.method_4947());
	}
}
