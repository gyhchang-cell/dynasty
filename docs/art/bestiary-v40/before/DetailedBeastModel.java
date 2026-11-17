package com.dynasty.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.CubeListBuilder;
import net.minecraft.client.model.geom.builders.LayerDefinition;
import net.minecraft.client.model.geom.builders.MeshDefinition;
import net.minecraft.client.model.geom.builders.PartDefinition;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;

import java.util.ArrayList;
import java.util.List;

/**
 * 神兽精细模型（128×128，三种形态）：麒麟 / 九尾狐 / 凤凰。
 * Detailed beast model (128x128) in three forms: Qilin, Nine-tailed Fox and Phoenix.
 * 部件：胸腔、后躯、脖颈、头、口鼻、耳、角/冠、鬃毛、分段四肢、尾巴（九尾）、羽翼。
 */
public class DetailedBeastModel<T extends Entity> extends EntityModel<T> {

    public enum Kind { QILIN, FOX, PHOENIX, NIAN }

    private final List<ModelPart> all = new ArrayList<>();
    private final List<ModelPart> upperLegs = new ArrayList<>();
    private final List<ModelPart> lowerLegs = new ArrayList<>();
    private final List<ModelPart> tails = new ArrayList<>();
    private final List<ModelPart> wings = new ArrayList<>();
    private final ModelPart head;
    private final ModelPart neck;
    private final ModelPart snout;

    private static final String[] UPPER_NAMES = {
            "leg_front_left_upper", "leg_front_right_upper", "leg_back_left_upper", "leg_back_right_upper",
            "leg_left_upper", "leg_right_upper"};
    private static final String[] LOWER_NAMES = {
            "leg_front_left_lower", "leg_front_right_lower", "leg_back_left_lower", "leg_back_right_lower",
            "leg_left_lower", "leg_right_lower", "talon_left", "talon_right"};

    private static final String[] PARTS = {
            "chest", "hind", "body", "neck", "head", "snout", "ear_left", "ear_right", "antler_left",
            "antler_right", "mane", "ruff", "crest",
            "leg_front_left_upper", "leg_front_left_lower", "leg_front_right_upper", "leg_front_right_lower",
            "leg_back_left_upper", "leg_back_left_lower", "leg_back_right_upper", "leg_back_right_lower",
            "leg_left_upper", "leg_left_lower", "leg_right_upper", "leg_right_lower", "talon_left", "talon_right",
            "wing_left_upper", "wing_left_lower", "wing_left_tip", "wing_right_upper", "wing_right_lower",
            "wing_right_tip", "tail", "tail_tuft", "tail0", "tail1", "tail2", "tail3", "tail4", "tail5",
            "tail6", "tail7", "tail8",
    };

    public DetailedBeastModel(ModelPart root, Kind kind) {
        this.head = root.getChild("head");
        this.neck = root.hasChild("neck") ? root.getChild("neck") : this.head;
        this.snout = root.hasChild("snout") ? root.getChild("snout") : this.head;
        for (String name : PARTS) {
            if (!root.hasChild(name)) {
                continue;
            }
            ModelPart part = root.getChild(name);
            this.all.add(part);
            if (name.endsWith("upper")) {
                this.upperLegs.add(part);
            } else if (name.endsWith("lower")) {
                this.lowerLegs.add(part);
            } else if (name.startsWith("tail")) {
                this.tails.add(part);
            } else if (name.startsWith("wing")) {
                this.wings.add(part);
            }
        }
    }

    private static void box(PartDefinition root, String name, int u, int v, int w, int h, int d,
                            float x, float y, float z) {
        root.addOrReplaceChild(name, CubeListBuilder.create().texOffs(u, v)
                .addBox(-w / 2.0F, -h / 2.0F, -d / 2.0F, w, h, d), PartPose.offset(x, y, z));
    }

    public static LayerDefinition createLayer(Kind kind) {
        MeshDefinition mesh = new MeshDefinition();
        PartDefinition root = mesh.getRoot();
        switch (kind) {
            case QILIN, NIAN -> buildQilin(root);
            case FOX -> buildFox(root);
            default -> buildPhoenix(root);
        }
        return LayerDefinition.create(mesh, 128, 128);
    }

    private static void buildQilin(PartDefinition root) {
        box(root, "chest", 0, 0, 14, 12, 16, 0.0F, 14.0F, -5.0F);
        box(root, "hind", 0, 32, 13, 11, 14, 0.0F, 14.0F, 12.0F);
        box(root, "neck", 48, 0, 8, 12, 8, 0.0F, 9.0F, -14.0F);
        box(root, "head", 48, 24, 10, 10, 10, 0.0F, 3.0F, -20.0F);
        box(root, "snout", 48, 48, 6, 6, 8, 0.0F, 1.0F, -27.0F);
        box(root, "ear_left", 80, 0, 3, 4, 2, 4.0F, -3.0F, -19.0F);
        box(root, "ear_right", 80, 0, 3, 4, 2, -4.0F, -3.0F, -19.0F);
        box(root, "antler_left", 80, 8, 3, 12, 3, 4.0F, -10.0F, -18.0F);
        box(root, "antler_right", 80, 8, 3, 12, 3, -4.0F, -10.0F, -18.0F);
        box(root, "mane", 0, 64, 12, 8, 4, 0.0F, 7.0F, -10.0F);
        box(root, "leg_front_left_upper", 80, 24, 5, 10, 5, 6.0F, 17.0F, -9.0F);
        box(root, "leg_front_left_lower", 80, 40, 4, 10, 4, 6.0F, 25.0F, -9.0F);
        box(root, "leg_front_right_upper", 80, 24, 5, 10, 5, -6.0F, 17.0F, -9.0F);
        box(root, "leg_front_right_lower", 80, 40, 4, 10, 4, -6.0F, 25.0F, -9.0F);
        box(root, "leg_back_left_upper", 80, 24, 5, 10, 5, 5.0F, 17.0F, 11.0F);
        box(root, "leg_back_left_lower", 80, 40, 4, 10, 4, 5.0F, 25.0F, 11.0F);
        box(root, "leg_back_right_upper", 80, 24, 5, 10, 5, -5.0F, 17.0F, 11.0F);
        box(root, "leg_back_right_lower", 80, 40, 4, 10, 4, -5.0F, 25.0F, 11.0F);
        box(root, "tail", 32, 64, 5, 5, 10, 0.0F, 10.0F, 21.0F);
        box(root, "tail_tuft", 32, 80, 6, 6, 6, 0.0F, 8.0F, 27.0F);
    }

    private static void buildFox(PartDefinition root) {
        box(root, "body", 0, 0, 12, 10, 16, 0.0F, 14.0F, 0.0F);
        box(root, "head", 48, 24, 9, 9, 9, 0.0F, 6.0F, -13.0F);
        box(root, "snout", 48, 48, 5, 5, 7, 0.0F, 4.0F, -19.0F);
        box(root, "ear_left", 80, 0, 3, 4, 2, 3.0F, 1.0F, -12.0F);
        box(root, "ear_right", 80, 0, 3, 4, 2, -3.0F, 1.0F, -12.0F);
        box(root, "ruff", 0, 64, 10, 8, 3, 0.0F, 12.0F, -6.0F);
        box(root, "leg_front_left_upper", 80, 24, 4, 9, 4, 5.0F, 17.0F, -5.0F);
        box(root, "leg_front_left_lower", 80, 40, 3, 9, 3, 5.0F, 25.0F, -5.0F);
        box(root, "leg_front_right_upper", 80, 24, 4, 9, 4, -5.0F, 17.0F, -5.0F);
        box(root, "leg_front_right_lower", 80, 40, 3, 9, 3, -5.0F, 25.0F, -5.0F);
        box(root, "leg_back_left_upper", 80, 24, 4, 9, 4, 5.0F, 17.0F, 7.0F);
        box(root, "leg_back_left_lower", 80, 40, 3, 9, 3, 5.0F, 25.0F, 7.0F);
        box(root, "leg_back_right_upper", 80, 24, 4, 9, 4, -5.0F, 17.0F, 7.0F);
        box(root, "leg_back_right_lower", 80, 40, 3, 9, 3, -5.0F, 25.0F, 7.0F);
        int[][] spots = {{0, 96}, {24, 96}, {48, 96}, {72, 96}, {96, 96}, {0, 108}, {24, 108}, {48, 108}, {72, 108}};
        for (int i = 0; i < 9; i++) {
            root.addOrReplaceChild("tail" + i, CubeListBuilder.create().texOffs(spots[i][0], spots[i][1])
                            .addBox(-2.0F, -2.0F, 0.0F, 4, 4, 8),
                    PartPose.offsetAndRotation((i - 4) * 1.4F, 10.0F + (i % 3) * 1.5F, 8.0F,
                            0.35F, (float) Math.toRadians((i - 4) * 9.0F), 0.0F));
        }
    }

    private static void buildPhoenix(PartDefinition root) {
        box(root, "chest", 0, 0, 10, 9, 16, 0.0F, 14.0F, 0.0F);
        box(root, "neck", 48, 0, 6, 10, 6, 0.0F, 8.0F, -9.0F);
        box(root, "head", 48, 16, 8, 7, 8, 0.0F, 3.0F, -14.0F);
        box(root, "snout", 48, 36, 4, 3, 6, 0.0F, 2.0F, -19.0F);
        box(root, "crest", 48, 48, 2, 8, 2, 0.0F, -4.0F, -12.0F);
        box(root, "wing_left_upper", 80, 0, 4, 2, 18, 6.0F, 12.0F, 0.0F);
        box(root, "wing_left_lower", 80, 24, 4, 2, 16, 6.0F, 14.0F, 1.0F);
        box(root, "wing_left_tip", 80, 48, 4, 2, 12, 6.0F, 16.0F, 3.0F);
        box(root, "wing_right_upper", 80, 0, 4, 2, 18, -6.0F, 12.0F, 0.0F);
        box(root, "wing_right_lower", 80, 24, 4, 2, 16, -6.0F, 14.0F, 1.0F);
        box(root, "wing_right_tip", 80, 48, 4, 2, 12, -6.0F, 16.0F, 3.0F);
        box(root, "tail0", 0, 40, 3, 2, 20, -3.0F, 13.0F, 14.0F);
        box(root, "tail1", 0, 40, 3, 2, 20, 0.0F, 13.0F, 15.0F);
        box(root, "tail2", 0, 40, 3, 2, 20, 3.0F, 13.0F, 14.0F);
        box(root, "leg_left_upper", 0, 64, 3, 8, 3, 3.0F, 19.0F, 3.0F);
        box(root, "leg_left_lower", 0, 80, 4, 3, 5, 3.0F, 24.0F, 2.0F);
        box(root, "leg_right_upper", 0, 64, 3, 8, 3, -3.0F, 19.0F, 3.0F);
        box(root, "leg_right_lower", 0, 80, 4, 3, 5, -3.0F, 24.0F, 2.0F);
    }

    @Override
    public void setupAnim(T entity, float limbSwing, float limbSwingAmount, float ageInTicks,
                          float netHeadYaw, float headPitch) {
        this.head.yRot = netHeadYaw * ((float) Math.PI / 180.0F);
        this.head.xRot = headPitch * ((float) Math.PI / 180.0F);
        if (this.neck != this.head) {
            this.neck.xRot = headPitch * ((float) Math.PI / 360.0F);
        }
        if (this.snout != this.head) {
            this.snout.xRot = this.head.xRot;
        }
        float swing = Mth.cos(limbSwing * 0.65F) * 1.25F * limbSwingAmount;
        float swingAlt = Mth.cos(limbSwing * 0.65F + (float) Math.PI) * 1.25F * limbSwingAmount;
        for (int i = 0; i < this.upperLegs.size(); i++) {
            this.upperLegs.get(i).xRot = (i % 2 == 0) ? swing : swingAlt;
        }
        for (int i = 0; i < this.lowerLegs.size(); i++) {
            float base = (i % 2 == 0) ? swing : swingAlt;
            this.lowerLegs.get(i).xRot = Math.max(0.0F, -base);
        }
        for (int i = 0; i < this.tails.size(); i++) {
            ModelPart tail = this.tails.get(i);
            tail.yRot = Mth.cos(ageInTicks * 0.11F + i * 0.35F) * 0.38F;
            tail.xRot = 0.3F + Mth.cos(ageInTicks * 0.08F + i * 0.45F) * 0.12F;
        }
        for (int i = 0; i < this.wings.size(); i++) {
            ModelPart wing = this.wings.get(i);
            float flap = Mth.cos(ageInTicks * 0.55F + i * 0.2F) * 0.75F;
            wing.zRot = (i < this.wings.size() / 2) ? -flap : flap;
        }
    }

    @Override
    public void renderToBuffer(PoseStack pose, VertexConsumer buffer, int packedLight, int packedOverlay,
                               float r, float g, float b, float a) {
        for (ModelPart part : this.all) {
            part.render(pose, buffer, packedLight, packedOverlay, r, g, b, a);
        }
    }
}

