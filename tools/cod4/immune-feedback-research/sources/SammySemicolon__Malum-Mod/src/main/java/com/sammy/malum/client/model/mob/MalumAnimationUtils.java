package com.sammy.malum.client.model.mob;

import net.minecraft.client.model.AnimationUtils;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Mob;
import team.lodestar.lodestone.modules.core.easing.Easing;

import java.util.function.Consumer;

public class MalumAnimationUtils<T extends Mob> {

    public final HierarchicalHumanoidModel<T> model;
    public final T mob;
    public final float limbSwing, limbSwingAmount;
    public final float motionDelta;

    public MalumAnimationUtils(HierarchicalHumanoidModel<T> model, T mob, float limbSwing, float limbSwingAmount) {
        this.model = model;
        this.mob = mob;
        this.limbSwing = limbSwing;
        this.limbSwingAmount = limbSwingAmount;
        boolean isFalling = mob.getFallFlyingTicks() > 4;
        float motionDelta = 1.0F;
        if (isFalling) {
            motionDelta = (float) mob.getDeltaMovement().lengthSqr();
            motionDelta /= 0.2F;
            motionDelta *= motionDelta * motionDelta;
        }
        this.motionDelta = Math.max(motionDelta, 1.0F);
    }

    public static<T extends Mob> MalumAnimationUtils<T> create(HierarchicalHumanoidModel<T> model, T mob, float limbSwing, float limbSwingAmount) {
        return new MalumAnimationUtils<>(model, mob, limbSwing, limbSwingAmount);
    }
    public float getLeftArmRotation(Consumer<LimbRotationData> properties) {
        LimbRotationData data = new LimbRotationData();
        properties.accept(data);
        return getArmRotation(data, false);
    }

    public float getRightArmRotation(Consumer<LimbRotationData> properties) {
        LimbRotationData data = new LimbRotationData();
        properties.accept(data);
        return getArmRotation(data, true);
    }

    public float getArmRotation(LimbRotationData data, boolean isRightArm) {
        float rate = data.rate;
        float delta = Mth.cos(limbSwing * rate + (isRightArm ? 3.14f : 0f));
        return getLimbRotation(data, delta);
    }

    public float getLeftLegRotation(Consumer<LimbRotationData> properties) {
        LimbRotationData data = new LimbRotationData();
        properties.accept(data);
        return getLegRotation(data, false);
    }

    public float getRightLegRotation(Consumer<LimbRotationData> properties) {
        LimbRotationData data = new LimbRotationData();
        properties.accept(data);
        return getLegRotation(data, true);
    }

    public float getLegRotation(LimbRotationData data, boolean isRightLeg) {
        float rate = data.rate;
        float delta = Mth.cos(limbSwing * rate + (isRightLeg ? 0f : 3.14f));
        return getLimbRotation(data, delta);
    }

    public float getLimbRotation(LimbRotationData data, float delta) {
        float clamp = data.clamp;
        var easing = data.easing;
        float sign = delta >= 0 ? 1 : -1;
        float eased = easing.ease(Mth.abs(delta));
        float rotation = sign * eased * data.amount * limbSwingAmount / motionDelta;
        if (clamp != -1) {
            rotation = Mth.clamp(rotation, -clamp, clamp);
        }
        return rotation;
    }

    public void reset() {
        reset(model);
    }

    public void applyRidingRotations(HierarchicalHumanoidModel<?> model) {
        float armX = 0.628f;
        float legX = -1.413F;
        float legY = 0.314f;
        float legZ = 0.078F;
        model.rightArm.xRot -= armX;
        model.leftArm.xRot += armX;
        model.rightLeg.setRotation(legX, legY, legZ);
        model.leftLeg.setRotation(legX, -legY, -legZ);
    }

    public void applyGenericArmAnimations(float ageInTicks) {
        model.setupAttackAnimation(mob, ageInTicks);
        AnimationUtils.bobModelPart(model.rightArm, ageInTicks, 1.0F);
        AnimationUtils.bobModelPart(model.leftArm, ageInTicks, -1.0F);
    }

    public static void reset(HierarchicalHumanoidModel<?> model) {
        model.modelDefinition.getAllParts().forEach(ModelPart::resetPose);
    }

    public static class LimbRotationData {
        float rate = 1, amount = 1;
        float clamp = -1;
        Easing easing = Easing.LINEAR;

        public LimbRotationData setRate(float rate) {
            this.rate = rate;
            return this;
        }

        public LimbRotationData setAmount(float amount) {
            this.amount = amount;
            return this;
        }

        public LimbRotationData addClamp(float clamp) {
            this.clamp = clamp;
            return this;
        }

        public LimbRotationData setEasing(Easing easing) {
            this.easing = easing;
            return this;
        }
    }
}