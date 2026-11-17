package software.bernie.geckolib3.geo.render.built;

import java.util.ArrayList;
import java.util.List;
import net.minecraft.class_1159;
import net.minecraft.class_1161;
import net.minecraft.class_1162;
import net.minecraft.class_4581;
import software.bernie.geckolib3.core.processor.IBone;
import software.bernie.geckolib3.core.snapshot.BoneSnapshot;

public class GeoBone implements IBone {
	public GeoBone parent;

	public List<GeoBone> childBones = new ArrayList<>();
	public List<GeoCube> childCubes = new ArrayList<>();

	public String name;
	public Boolean mirror;
	public Double inflate;
	public Boolean dontRender;
	public boolean isHidden;
	public boolean areCubesHidden = false;
	public boolean hideChildBonesToo;
	// I still have no idea what this field does, but its in the json file so
	// ¯\_(ツ)_/¯
	public Boolean reset;
	public float pivotX;
	public float pivotY;
	public float pivotZ;
	private BoneSnapshot initialSnapshot;
	private float scaleX = 1;
	private float scaleY = 1;
	private float scaleZ = 1;
	private float positionX;
	private float positionY;
	private float positionZ;
	private float rotateX;
	private float rotateY;
	private float rotateZ;

	public Object extraData;

	private class_1159 modelSpaceXform;
	private boolean trackXform;
	public class_1159 rotMat;

	private class_1159 worldSpaceXform;
	private class_4581 worldSpaceNormal;

	public GeoBone() {
		modelSpaceXform = new class_1159();
		modelSpaceXform.method_22668();
		trackXform = false;
		rotMat = null;

		worldSpaceXform = new class_1159();
		worldSpaceXform.method_22668();
		worldSpaceNormal = new class_4581();
		worldSpaceNormal.method_22856();
	}

	@Override
	public void setModelRendererName(String modelRendererName) {
		this.name = modelRendererName;
	}

	@Override
	public void saveInitialSnapshot() {
		if (this.initialSnapshot == null) {
			this.initialSnapshot = new BoneSnapshot(this, true);
		}
	}

	@Override
	public BoneSnapshot getInitialSnapshot() {
		return this.initialSnapshot;
	}

	@Override
	public String getName() {
		return this.name;
	}

	// Boilerplate code incoming

	@Override
	public float getRotationX() {
		return rotateX;
	}

	@Override
	public void setRotationX(float value) {
		this.rotateX = value;
	}

	@Override
	public float getRotationY() {
		return rotateY;
	}

	@Override
	public void setRotationY(float value) {
		this.rotateY = value;
	}

	@Override
	public float getRotationZ() {
		return rotateZ;
	}

	@Override
	public void setRotationZ(float value) {
		this.rotateZ = value;
	}

	@Override
	public float getPositionX() {
		return positionX;
	}

	@Override
	public void setPositionX(float value) {
		this.positionX = value;
	}

	@Override
	public float getPositionY() {
		return positionY;
	}

	@Override
	public void setPositionY(float value) {
		this.positionY = value;
	}

	@Override
	public float getPositionZ() {
		return positionZ;
	}

	@Override
	public void setPositionZ(float value) {
		this.positionZ = value;
	}

	@Override
	public float getScaleX() {
		return scaleX;
	}

	@Override
	public void setScaleX(float value) {
		this.scaleX = value;
	}

	@Override
	public float getScaleY() {
		return scaleY;
	}

	@Override
	public void setScaleY(float value) {
		this.scaleY = value;
	}

	@Override
	public float getScaleZ() {
		return scaleZ;
	}

	@Override
	public void setScaleZ(float value) {
		this.scaleZ = value;
	}

	@Override
	public void setPivotX(float value) {
		this.pivotX = value;
	}

	@Override
	public void setPivotY(float value) {
		this.pivotY = value;
	}

	@Override
	public void setPivotZ(float value) {
		this.pivotZ = value;
	}

	@Override
	public float getPivotX() {
		return this.pivotX;
	}

	@Override
	public float getPivotY() {
		return this.pivotY;
	}

	@Override
	public float getPivotZ() {
		return this.pivotZ;
	}

	@Override
	public boolean isHidden() {
		return this.isHidden;
	}

	@Override
	public void setHidden(boolean hidden) {
		this.setHidden(hidden, hidden);
	}

	@Override
	public boolean cubesAreHidden() {
		return areCubesHidden;
	}

	@Override
	public boolean childBonesAreHiddenToo() {
		return hideChildBonesToo;
	}

	@Override
	public void setCubesHidden(boolean hidden) {
		this.areCubesHidden = hidden;
	}

	@Override
	public void setHidden(boolean selfHidden, boolean skipChildRendering) {
		this.isHidden = selfHidden;
		this.hideChildBonesToo = skipChildRendering;
	}

	public GeoBone getParent() {
		return (GeoBone) parent;
	}

	public boolean isTrackingXform() {
		return trackXform;
	}

	public void setTrackXform(boolean trackXform) {
		this.trackXform = trackXform;
	}

	public class_1159 getModelSpaceXform() {
		setTrackXform(true);
		return modelSpaceXform;
	}

	public void setModelSpaceXform(class_1159 modelSpaceXform) {
		this.modelSpaceXform.method_22672(modelSpaceXform);
	}

	public class_1161 getModelPosition() {
		class_1159 matrix = getModelSpaceXform();
		class_1162 vec = new class_1162(0, 0, 0, 1);
		vec.method_22674(matrix);
		return new class_1161(-vec.method_4953() * 16f, vec.method_4956() * 16f, vec.method_4957() * 16f);
	}

	public class_1159 getWorldSpaceXform() {
		setTrackXform(true);
		return worldSpaceXform;
	}

	public void setWorldSpaceXform(class_1159 worldSpaceXform) {
		this.worldSpaceXform.method_22672(worldSpaceXform);
	}

	public class_1161 getWorldPosition() {
		class_1159 matrix = getWorldSpaceXform();
		class_1162 vec = new class_1162(0, 0, 0, 1);
		vec.method_22674(matrix);
		return new class_1161(vec.method_4953(), vec.method_4956(), vec.method_4957());
	}

	public void setModelPosition(class_1161 pos) {
		// TODO: Doesn't work on bones with parent transforms
		GeoBone parent = getParent();
		class_1159 identity = new class_1159();
		identity.method_22668();
		class_1159 matrix = parent == null ? identity : parent.getModelSpaceXform().method_22673();
		matrix.method_22870();
		class_1162 vec = new class_1162(-(float) pos.field_5661 / 16f, (float) pos.field_5660 / 16f, (float) pos.field_5659 / 16f, 1);
		vec.method_22674(matrix);
		setPosition(-vec.method_4953() * 16f, vec.method_4956() * 16f, vec.method_4957() * 16f);
	}

	public class_1159 getModelRotationMat() {
		class_1159 matrix = getModelSpaceXform().method_22673();
		removeMatrixTranslation(matrix);
		return matrix;
	}

	public static void removeMatrixTranslation(class_1159 matrix) {
		matrix.field_21655 = 0;
		matrix.field_21659 = 0;
		matrix.field_21663 = 0;
	}

	public void setModelRotationMat(class_1159 mat) {
		rotMat = mat;
	}

	public void setWorldSpaceNormal(class_4581 worldSpaceNormal) {
		this.worldSpaceNormal = worldSpaceNormal;
	}

	public class_4581 getWorldSpaceNormal() {
		return worldSpaceNormal;
	}

	// Position utils
	public void addPosition(class_1161 vec) {
		addPosition((float) vec.field_5661, (float) vec.field_5660, (float) vec.field_5659);
	}

	public void addPosition(float x, float y, float z) {
		addPositionX(x);
		addPositionY(y);
		addPositionZ(z);
	}

	public void addPositionX(float x) {
		setPositionX(getPositionX() + x);
	}

	public void addPositionY(float y) {
		setPositionY(getPositionY() + y);
	}

	public void addPositionZ(float z) {
		setPositionZ(getPositionZ() + z);
	}

	public void setPosition(class_1161 vec) {
		setPosition((float) vec.field_5661, (float) vec.field_5660, (float) vec.field_5659);
	}

	public void setPosition(float x, float y, float z) {
		setPositionX(x);
		setPositionY(y);
		setPositionZ(z);
	}

	public class_1161 getPosition() {
		return new class_1161(getPositionX(), getPositionY(), getPositionZ());
	}

	// Rotation utils
	public void addRotation(class_1161 vec) {
		addRotation((float) vec.field_5661, (float) vec.field_5660, (float) vec.field_5659);
	}

	public void addRotation(float x, float y, float z) {
		addRotationX(x);
		addRotationY(y);
		addRotationZ(z);
	}

	public void addRotationX(float x) {
		setRotationX(getRotationX() + x);
	}

	public void addRotationY(float y) {
		setRotationY(getRotationY() + y);
	}

	public void addRotationZ(float z) {
		setRotationZ(getRotationZ() + z);
	}

	public void setRotation(class_1161 vec) {
		setRotation((float) vec.field_5661, (float) vec.field_5660, (float) vec.field_5659);
	}

	public void setRotation(float x, float y, float z) {
		setRotationX(x);
		setRotationY(y);
		setRotationZ(z);
	}

	public class_1161 getRotation() {
		return new class_1161(getRotationX(), getRotationY(), getRotationZ());
	}

	// Scale utils
	public void multiplyScale(class_1161 vec) {
		multiplyScale((float) vec.field_5661, (float) vec.field_5660, (float) vec.field_5659);
	}

	public void multiplyScale(float x, float y, float z) {
		setScaleX(getScaleX() * x);
		setScaleY(getScaleY() * y);
		setScaleZ(getScaleZ() * z);
	}

	public void setScale(class_1161 vec) {
		setScale((float) vec.field_5661, (float) vec.field_5660, (float) vec.field_5659);
	}

	public void setScale(float x, float y, float z) {
		setScaleX(x);
		setScaleY(y);
		setScaleZ(z);
	}

	public class_1161 getScale() {
		return new class_1161(getScaleX(), getScaleY(), getScaleZ());
	}

	public void addRotationOffsetFromBone(GeoBone source) {
		setRotationX(getRotationX() + source.getRotationX() - source.getInitialSnapshot().rotationValueX);
		setRotationY(getRotationY() + source.getRotationY() - source.getInitialSnapshot().rotationValueY);
		setRotationZ(getRotationZ() + source.getRotationZ() - source.getInitialSnapshot().rotationValueZ);
	}

}
