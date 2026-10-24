package com.dynasty.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Mob;

/** Connected native anatomy for the base fox and phoenix; no combat changes. */
public final class BestiarySpiritModel<T extends Mob> extends EntityModel<T> {
    private final ModelPart root, body, head;
    private final boolean phoenix;

    public BestiarySpiritModel(ModelPart root, boolean phoenix) {
        this.root = root;
        this.phoenix = phoenix;
        this.body = root.getChild("body");
        this.head = body.getChild("neck").getChild("head");
    }

    @Override
    public void setupAnim(T entity, float limbSwing, float limbSwingAmount,
                          float age, float yaw, float pitch) {
        applyPose(!entity.onGround(), entity.getAttackAnim(0.0F), limbSwing,
                limbSwingAmount, age, yaw, pitch);
    }

    // Kept independent of world state so the native mesh can be replayed without a game window.
    void applyPose(boolean flying, float attackProgress, float limbSwing, float limbSwingAmount,
                   float age, float yaw, float pitch) {
        root.getAllParts().forEach(ModelPart::resetPose);
        head.yRot += Mth.clamp(yaw, -45.0F, 45.0F) * Mth.DEG_TO_RAD;
        head.xRot += Mth.clamp(pitch, -25.0F, 30.0F) * Mth.DEG_TO_RAD * 0.6F;
        float amount = Math.min(limbSwingAmount, 1.0F);
        if (phoenix) {
            body.xRot += flying ? -0.10F : Mth.sin(age * 0.07F) * 0.018F;
            for (String side : new String[]{"left", "right"}) {
                float sign = side.equals("left") ? 1.0F : -1.0F;
                ModelPart wing = body.getChild("wing_" + side);
                ModelPart fore = wing.getChild("wing_" + side + "_fore");
                ModelPart tip = fore.getChild("wing_" + side + "_tip");
                float flap = Mth.cos(age * 0.52F);
                wing.zRot += sign * (flying ? flap * 0.55F : 0.12F + Mth.sin(age * 0.09F) * 0.025F);
                if (!flying) wing.yRot -= sign * 1.25F;
                // The elbow follows the shoulder; the tip lags instead of flapping separately.
                fore.zRot += sign * (flying ? Mth.cos(age * 0.52F - 0.45F) * 0.19F : 0.05F);
                if (!flying) fore.yRot -= sign * 0.18F;
                tip.zRot += sign * Mth.sin(age * 0.52F - 0.70F) * (flying ? 0.10F : 0.01F);
                ModelPart leg = body.getChild("leg_" + side);
                leg.xRot += flying ? -0.70F : Mth.cos(limbSwing * 0.8F + (sign < 0 ? Mth.PI : 0)) * amount * 0.45F;
                leg.getChild("foot_" + side).xRot += flying ? 0.55F : 0.0F;
            }
            for (int i = 0; i < 3; i++) {
                ModelPart tail = body.getChild("rump").getChild("tail" + i);
                tail.xRot += Mth.sin(age * 0.12F + i * 0.4F) * 0.07F;
                tail.getChild("tail" + i + "_tip").xRot += Mth.sin(age * 0.12F + i * 0.4F - 0.5F) * 0.07F;
            }
        } else {
            body.y += Mth.sin(age * 0.08F) * 0.045F;
            String[] legs = {"front_left", "front_right", "back_left", "back_right"};
            for (int i = 0; i < legs.length; i++) {
                float phase = (i == 0 || i == 3) ? 0 : Mth.PI;
                float step = Mth.cos(limbSwing * 0.8F + phase) * amount * 0.52F;
                ModelPart leg = body.getChild("leg_" + legs[i]);
                leg.xRot += step;
                leg.getChild("ankle_" + legs[i]).xRot += Math.max(0, -step) * 0.45F;
            }
            for (int i = 0; i < 9; i++) {
                ModelPart tail = body.getChild("tail" + i);
                tail.yRot += Mth.sin(age * 0.065F + i * 0.36F) * 0.045F;
                tail.xRot += Mth.sin(age * 0.08F + i * 0.4F) * 0.035F;
                tail.getChild("tail" + i + "_tip").yRot += Mth.sin(age * 0.065F + i * 0.36F - 0.55F) * 0.08F;
            }
            float attack = Mth.sin(attackProgress * Mth.PI);
            body.getChild("neck").xRot += attack * 0.13F;
            head.xRot -= attack * 0.22F;
        }
    }

    @Override
    public void renderToBuffer(PoseStack pose, VertexConsumer buffer, int light,
                               int overlay, float r, float g, float b, float a) {
        root.render(pose, buffer, light, overlay, r, g, b, a);
    }
}
