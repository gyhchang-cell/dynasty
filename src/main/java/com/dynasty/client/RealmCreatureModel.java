package com.dynasty.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Mob;

/** Realm creatures, with canonical Steve proportions for anatomical humanoids. */
public final class RealmCreatureModel<T extends Mob> extends EntityModel<T> {
    private final ModelPart root, body, head, rightArm, leftArm;
    private final String kind;

    public RealmCreatureModel(ModelPart root, String kind) {
        this.root = root;
        this.kind = kind;
        body = root.getChild("body");
        head = root.getChild("head");
        rightArm = root.getChild("right_arm");
        leftArm = root.getChild("left_arm");
    }

    @Override
    public void setupAnim(T entity, float limbSwing, float amount, float age, float yaw, float pitch) {
        // MeleeAttackGoal already calls swing(). No additional attack clock or server changes.
        applyPose(entity.getAttackAnim(0), limbSwing, amount, age, yaw, pitch);
    }

    void applyPose(float attack, float limbSwing, float amount, float age, float yaw, float pitch) {
        root.getAllParts().forEach(ModelPart::resetPose);
        head.yRot += Mth.clamp(yaw, -60, 60) * Mth.DEG_TO_RAD;
        head.xRot += Mth.clamp(pitch, -35, 35) * Mth.DEG_TO_RAD;
        float stride = Mth.cos(limbSwing * 0.6662F) * Math.min(amount, 1) * 1.15F;
        float strike = Mth.sin(Mth.sqrt(attack) * Mth.PI);
        if (kind.equals("soul_soldier")) {
            // Ground-nav wraith: small bob, reaching shell-arms, trailing cloth, no player walk.
            root.y += Mth.sin(age * 0.075F) * 0.22F;
            rightArm.xRot -= 0.24F + strike * 1.25F;
            leftArm.xRot -= 0.24F + strike * 0.45F;
            rightArm.yRot -= strike * 0.25F;
            head.xRot -= strike * 0.10F;
            for (String side : new String[]{"right", "left"}) {
                ModelPart strip = body.getChild("strip_" + side);
                float phase = side.equals("left") ? 0.8F : 0;
                strip.xRot += Mth.sin(age * 0.10F + phase) * 0.08F + amount * 0.17F;
                strip.getChild("strip_" + side + "_tip").xRot += Mth.sin(age * 0.10F + phase - 0.55F) * 0.10F;
            }
            body.getChild("backcloth").xRot += Mth.sin(age * 0.08F) * 0.035F + amount * 0.1F;
        } else {
            root.getChild("right_leg").xRot = stride;
            root.getChild("left_leg").xRot = -stride;
            rightArm.xRot = -stride * 0.65F;
            leftArm.xRot = stride * 0.65F;
            float breath = Mth.sin(age * 0.075F) * 0.025F;
            if (kind.equals("jade_guard")) {
                rightArm.xRot -= 0.13F;
                leftArm.xRot -= 0.13F;
                rightArm.zRot -= 0.045F;
                leftArm.zRot += 0.045F;
            } else if (kind.equals("thunder_envoy")) {
                rightArm.xRot -= 0.28F;
                leftArm.xRot -= 0.12F;
                head.getChild("knot").xRot += Mth.sin(age * 0.13F) * 0.07F;
            } else if (kind.equals("terracotta_warrior")) {
                // A clay body still walks on the original six-block humanoid skeleton.
                rightArm.xRot = -stride * 0.45F - 0.16F;
                leftArm.xRot = stride * 0.45F - 0.16F;
            } else if (kind.equals("minister")) {
                // Civilian idle, not a caster attack pose. No weapon/attack AI is added.
                rightArm.xRot = -stride * 0.5F - 0.18F;
                leftArm.xRot = stride * 0.5F - 0.18F;
                rightArm.zRot -= 0.04F;
                leftArm.zRot += 0.04F;
            } else {
                body.getChild("tail").yRot += Mth.sin(age * 0.12F) * 0.14F + stride * 0.12F;
                body.getChild("tail").getChild("tail_fin").yRot += Mth.sin(age * 0.12F - 0.6F) * 0.12F;
                for (String side : new String[]{"right", "left"}) {
                    head.getChild("gill_" + side).yRot += Mth.sin(age * 0.09F) * 0.035F;
                }
                rightArm.xRot -= 0.15F;
                leftArm.xRot -= 0.15F;
            }
            rightArm.zRot -= breath;
            leftArm.zRot += breath;
            rightArm.xRot -= strike * 1.65F;
            rightArm.yRot -= strike * 0.20F;
            leftArm.xRot -= strike * 0.22F;
            body.yRot -= strike * 0.08F;
        }
    }

    @Override
    public void renderToBuffer(PoseStack pose, VertexConsumer buffer, int light, int overlay,
                               float r, float g, float b, float a) {
        root.render(pose, buffer, light, overlay, r, g, b, a);
    }
}
