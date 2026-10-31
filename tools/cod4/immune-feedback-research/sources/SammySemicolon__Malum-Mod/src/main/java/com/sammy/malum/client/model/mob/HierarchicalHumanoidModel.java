package com.sammy.malum.client.model.mob;

import com.google.common.collect.ImmutableList;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.animation.AnimationChannel;
import net.minecraft.client.animation.AnimationDefinition;
import net.minecraft.client.animation.Keyframe;
import net.minecraft.client.model.AgeableListModel;
import net.minecraft.client.model.ArmedModel;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.HeadedModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.AnimationState;
import net.minecraft.world.entity.HumanoidArm;
import net.minecraft.world.entity.LivingEntity;
import org.jetbrains.annotations.NotNull;
import org.joml.Vector3f;

import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.function.Function;

public abstract class HierarchicalHumanoidModel<T extends LivingEntity> extends EntityModel<T> implements ArmedModel, HeadedModel {

    private static final Vector3f ANIMATION_VECTOR_CACHE = new Vector3f();

    protected final ModelPart modelDefinition;

    public final ModelPart root;
    public final ModelPart head;
    public final ModelPart body;
    public final ModelPart rightArm;
    public final ModelPart leftArm;
    public final ModelPart rightLeg;
    public final ModelPart leftLeg;

    public HierarchicalHumanoidModel(ModelPart modelDefinition) {
        this(modelDefinition, RenderType::entityCutoutNoCull);
    }

    public HierarchicalHumanoidModel(ModelPart modelDefinition, Function<ResourceLocation, RenderType> renderType) {
        super(renderType);
        this.modelDefinition = modelDefinition;
        this.root = modelDefinition.getChild("root");
        this.head = getHead("head");
        this.body = getPart("body");
        this.rightArm = getPart("right_arm");
        this.leftArm = getPart("left_arm");
        this.rightLeg = getPart("right_leg");
        this.leftLeg = getPart("left_leg");
    }

    public ModelPart getHead(String name) {
        try {
            return root.getChild(name);
        } catch (Exception ignored) {
            var body = root.getChild("body");
            if (body.hasChild(name)) {
                return body.getChild(name);
            }
            return new ModelPart(Collections.emptyList(), Collections.emptyMap());
        }
    }
    public ModelPart getPart(String name) {
        try {
            return root.getChild(name);
        } catch (Exception ignored) {
            return new ModelPart(Collections.emptyList(), Collections.emptyMap());
        }
    }

    @Override
    public void renderToBuffer(PoseStack poseStack, VertexConsumer buffer, int packedLight, int packedOverlay, int color) {
        root.render(poseStack, buffer, packedLight, packedOverlay);
    }

    @Override
    public void translateToHand(@NotNull HumanoidArm side, @NotNull PoseStack poseStack) {
        this.getArm(side).translateAndRotate(poseStack);
    }

    @Override
    public @NotNull ModelPart getHead() {
        return head;
    }

    public void grow(float size) {
        root.xScale += size;
        root.yScale += size;
        root.zScale += size;
    }

    protected ModelPart getArm(HumanoidArm side) {
        return side == HumanoidArm.LEFT ? leftArm : rightArm;
    }

    public Optional<ModelPart> getAnyDescendantWithName(String name) {
        return name.equals("root")
                ? Optional.of(modelDefinition)
                : modelDefinition.getAllParts().filter(p_233400_ -> p_233400_.hasChild(name)).findFirst().map(p_233397_ -> p_233397_.getChild(name));
    }

    public void setupAttackAnimation(T livingEntity, float ageInTicks) {
        if (!(this.attackTime <= 0.0F)) {
            HumanoidArm humanoidarm = this.getAttackArm(livingEntity);
            ModelPart modelpart = this.getArm(humanoidarm);
            float f = this.attackTime;
            this.body.yRot = Mth.sin(Mth.sqrt(f) * (float) (Math.PI * 2)) * 0.2F;
            if (humanoidarm == HumanoidArm.LEFT) {
                this.body.yRot *= -1.0F;
            }

            this.rightArm.z = Mth.sin(this.body.yRot) * 5.0F;
            this.rightArm.x = -Mth.cos(this.body.yRot) * 5.0F;
            this.leftArm.z = -Mth.sin(this.body.yRot) * 5.0F;
            this.leftArm.x = Mth.cos(this.body.yRot) * 5.0F;
            this.rightArm.yRot = this.rightArm.yRot + this.body.yRot;
            this.leftArm.yRot = this.leftArm.yRot + this.body.yRot;
            this.leftArm.xRot = this.leftArm.xRot + this.body.yRot;
            f = 1.0F - this.attackTime;
            f *= f;
            f *= f;
            f = 1.0F - f;
            float f1 = Mth.sin(f * (float) Math.PI);
            float f2 = Mth.sin(this.attackTime * (float) Math.PI) * -(this.head.xRot - 0.7F) * 0.75F;
            modelpart.xRot -= f1 * 1.2F + f2;
            modelpart.yRot = modelpart.yRot + this.body.yRot * 2.0F;
            modelpart.zRot = modelpart.zRot + Mth.sin(this.attackTime * (float) Math.PI) * -0.4F;
        }
    }

    private HumanoidArm getAttackArm(T entity) {
        HumanoidArm humanoidarm = entity.getMainArm();
        return entity.swingingArm == InteractionHand.MAIN_HAND ? humanoidarm : humanoidarm.getOpposite();
    }

    protected boolean animateWalk(net.neoforged.neoforge.client.entity.animation.json.AnimationHolder animation, float limbSwing, float limbSwingAmount, float maxAnimationSpeed, float animationScaleFactor) {
        return animateWalk(animation.get(), limbSwing, limbSwingAmount, maxAnimationSpeed, animationScaleFactor);
    }

    protected boolean animateWalk(AnimationDefinition animationDefinition, float limbSwing, float limbSwingAmount, float maxAnimationSpeed, float animationScaleFactor) {
        long i = (long) (limbSwing * 50.0F * maxAnimationSpeed);
        float f = Math.min(limbSwingAmount * animationScaleFactor, 1.0F);
        return animate(this, animationDefinition, i, f, ANIMATION_VECTOR_CACHE);
    }

    protected boolean animate(AnimationState animationState, AnimationDefinition animationDefinition, float ageInTicks) {
        return animate(animationState, animationDefinition, ageInTicks, 1.0F);
    }

    protected boolean animate(AnimationState animationState, AnimationDefinition animationDefinition, float ageInTicks, float speed) {
        animationState.updateTime(ageInTicks, speed);
        if (animationState.isStarted()) {
            return animate(this, animationDefinition, animationState.getAccumulatedTime(), 1.0F, ANIMATION_VECTOR_CACHE);
        }
        return false;
    }

    protected boolean applyStatic(AnimationDefinition animationDefinition) {
        return animate(this, animationDefinition, 0L, 1.0F, ANIMATION_VECTOR_CACHE);
    }

    public static boolean animate(HierarchicalHumanoidModel<?> model, AnimationDefinition animationDefinition, long accumulatedTime, float scale, Vector3f animationVecCache) {
        float delta = getElapsedSeconds(animationDefinition, accumulatedTime);
        if (delta < animationDefinition.lengthInSeconds()) {
            for (Map.Entry<String, List<AnimationChannel>> entry : animationDefinition.boneAnimations().entrySet()) {
                Optional<ModelPart> optional = model.getAnyDescendantWithName(entry.getKey());
                List<AnimationChannel> list = entry.getValue();
                optional.ifPresent(p_232330_ -> list.forEach(p_288241_ -> {
                    Keyframe[] akeyframe = p_288241_.keyframes();
                    int i = Math.max(0, Mth.binarySearch(0, akeyframe.length, p_232315_ -> delta <= akeyframe[p_232315_].timestamp()) - 1);
                    int j = Math.min(akeyframe.length - 1, i + 1);
                    Keyframe keyframe = akeyframe[i];
                    Keyframe keyframe1 = akeyframe[j];
                    float f1 = delta - keyframe.timestamp();
                    float f2;
                    if (j != i) {
                        f2 = Mth.clamp(f1 / (keyframe1.timestamp() - keyframe.timestamp()), 0.0F, 1.0F);
                    } else {
                        f2 = 0.0F;
                    }

                    keyframe1.interpolation().apply(animationVecCache, f2, akeyframe, i, j, scale);
                    p_288241_.target().apply(p_232330_, animationVecCache);
                }));
            }
            return true;
        }
        return false;
    }

    public static float getElapsedSeconds(AnimationDefinition animationDefinition, long accumulatedTime) {
        float f = (float) accumulatedTime / 1000.0F;
        return animationDefinition.looping() ? f % animationDefinition.lengthInSeconds() : f;
    }

    public static Vector3f posVec(float x, float y, float z) {
        return new Vector3f(x, -y, z);
    }

    public static Vector3f degreeVec(float xDegrees, float yDegrees, float zDegrees) {
        return new Vector3f(xDegrees * Mth.DEG_TO_RAD, yDegrees * Mth.DEG_TO_RAD, zDegrees * Mth.DEG_TO_RAD);
    }

    public static Vector3f scaleVec(double xScale, double yScale, double zScale) {
        return new Vector3f((float) (xScale - 1.0), (float) (yScale - 1.0), (float) (zScale - 1.0));
    }
}