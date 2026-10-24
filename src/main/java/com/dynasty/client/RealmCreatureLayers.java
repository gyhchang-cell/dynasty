package com.dynasty.client;

import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.*;

/** Generated original native models / UVs: tools/art/bestiary-v42/build_models.py. */
public final class RealmCreatureLayers {
    private RealmCreatureLayers() {}
    public static LayerDefinition jade_guard() {
        MeshDefinition mesh = new MeshDefinition();
        PartDefinition root = mesh.getRoot();
        PartDefinition body = root.addOrReplaceChild("body", CubeListBuilder.create().texOffs(1, 1).addBox(-4.00000F, 0.00000F, -2.00000F, 8.00000F, 12.00000F, 4.00000F), PartPose.offsetAndRotation(0.00000F, 0.00000F, 0.00000F, 0.00000F, 0.00000F, 0.00000F));
        PartDefinition head = root.addOrReplaceChild("head", CubeListBuilder.create().texOffs(26, 1).addBox(-4.00000F, -8.00000F, -4.00000F, 8.00000F, 8.00000F, 8.00000F), PartPose.offsetAndRotation(0.00000F, 0.00000F, 0.00000F, 0.00000F, 0.00000F, 0.00000F));
        PartDefinition right_arm = root.addOrReplaceChild("right_arm", CubeListBuilder.create().texOffs(59, 1).addBox(-3.00000F, -2.00000F, -2.00000F, 4.00000F, 12.00000F, 4.00000F), PartPose.offsetAndRotation(-5.00000F, 2.00000F, 0.00000F, 0.00000F, 0.00000F, 0.00000F));
        PartDefinition right_leg = root.addOrReplaceChild("right_leg", CubeListBuilder.create().texOffs(76, 1).addBox(-2.00000F, 0.00000F, -2.00000F, 4.00000F, 12.00000F, 4.00000F), PartPose.offsetAndRotation(-1.90000F, 12.00000F, 0.00000F, 0.00000F, 0.00000F, 0.00000F));
        PartDefinition left_arm = root.addOrReplaceChild("left_arm", CubeListBuilder.create().texOffs(93, 1).addBox(-1.00000F, -2.00000F, -2.00000F, 4.00000F, 12.00000F, 4.00000F), PartPose.offsetAndRotation(5.00000F, 2.00000F, 0.00000F, 0.00000F, 0.00000F, 0.00000F));
        PartDefinition left_leg = root.addOrReplaceChild("left_leg", CubeListBuilder.create().texOffs(110, 1).addBox(-2.00000F, 0.00000F, -2.00000F, 4.00000F, 12.00000F, 4.00000F), PartPose.offsetAndRotation(1.90000F, 12.00000F, 0.00000F, 0.00000F, 0.00000F, 0.00000F));
        PartDefinition helmet = head.addOrReplaceChild("helmet", CubeListBuilder.create().texOffs(1, 18).addBox(-4.20000F, -1.50000F, -4.20000F, 8.00000F, 2.00000F, 8.00000F), PartPose.offsetAndRotation(0.00000F, -6.70000F, 0.00000F, 0.00000F, 0.00000F, 0.00000F));
        PartDefinition brow = head.addOrReplaceChild("brow", CubeListBuilder.create().texOffs(34, 18).addBox(-4.00000F, -0.60000F, -0.40000F, 8.00000F, 1.00000F, 1.00000F), PartPose.offsetAndRotation(0.00000F, -4.80000F, -4.20000F, 0.00000F, 0.00000F, 0.00000F));
        PartDefinition mask = head.addOrReplaceChild("mask", CubeListBuilder.create().texOffs(53, 18).addBox(-3.00000F, -1.10000F, -0.40000F, 6.00000F, 3.00000F, 1.00000F), PartPose.offsetAndRotation(0.00000F, -1.40000F, -4.22000F, 0.00000F, 0.00000F, 0.00000F));
        PartDefinition shoulder_right = right_arm.addOrReplaceChild("shoulder_right", CubeListBuilder.create().texOffs(68, 18).addBox(-2.20000F, -0.40000F, -2.40000F, 4.00000F, 2.00000F, 5.00000F), PartPose.offsetAndRotation(-1.00000F, -1.80000F, 0.00000F, 0.00000F, 0.00000F, 0.00000F));
        PartDefinition shoulder_left = left_arm.addOrReplaceChild("shoulder_left", CubeListBuilder.create().texOffs(87, 18).addBox(-2.20000F, -0.40000F, -2.40000F, 4.00000F, 2.00000F, 5.00000F), PartPose.offsetAndRotation(1.00000F, -1.80000F, 0.00000F, 0.00000F, 0.00000F, 0.00000F));
        PartDefinition collar = body.addOrReplaceChild("collar", CubeListBuilder.create().texOffs(106, 18).addBox(-3.00000F, -0.40000F, -0.30000F, 6.00000F, 2.00000F, 1.00000F), PartPose.offsetAndRotation(0.00000F, 0.80000F, -2.10000F, 0.00000F, 0.00000F, 0.00000F));
        return LayerDefinition.create(mesh, 128, 128);
    }

    public static LayerDefinition soul_soldier() {
        MeshDefinition mesh = new MeshDefinition();
        PartDefinition root = mesh.getRoot();
        PartDefinition body = root.addOrReplaceChild("body", CubeListBuilder.create().texOffs(1, 1).addBox(-3.75000F, 0.00000F, -2.00000F, 2.00000F, 10.00000F, 4.00000F).texOffs(14, 1).addBox(2.25000F, 0.00000F, -2.00000F, 2.00000F, 10.00000F, 4.00000F).texOffs(27, 1).addBox(-3.50000F, 0.00000F, -2.00000F, 7.00000F, 2.00000F, 4.00000F).texOffs(50, 1).addBox(-3.50000F, 8.00000F, -2.00000F, 7.00000F, 2.00000F, 4.00000F), PartPose.offsetAndRotation(0.00000F, 1.00000F, 0.00000F, 0.00000F, 0.00000F, 0.00000F));
        PartDefinition head = root.addOrReplaceChild("head", CubeListBuilder.create().texOffs(73, 1).addBox(-3.50000F, -7.00000F, 0.00000F, 7.00000F, 7.00000F, 2.00000F).texOffs(92, 1).addBox(-3.50000F, -7.00000F, -3.00000F, 7.00000F, 1.00000F, 4.00000F).texOffs(115, 1).addBox(-3.50000F, -6.00000F, -3.00000F, 1.00000F, 6.00000F, 4.00000F).texOffs(1, 16).addBox(2.50000F, -6.00000F, -3.00000F, 1.00000F, 6.00000F, 4.00000F), PartPose.offsetAndRotation(0.00000F, -0.50000F, 0.00000F, 0.00000F, 0.00000F, 0.00000F));
        PartDefinition mask = head.addOrReplaceChild("mask", CubeListBuilder.create().texOffs(12, 16).addBox(-2.50000F, -2.50000F, -0.50000F, 5.00000F, 5.00000F, 1.00000F), PartPose.offsetAndRotation(0.00000F, -3.00000F, -2.20000F, 0.00000F, 0.00000F, 0.00000F));
        PartDefinition right_arm = root.addOrReplaceChild("right_arm", CubeListBuilder.create().texOffs(25, 16).addBox(-1.50000F, 0.00000F, -1.50000F, 3.00000F, 7.00000F, 3.00000F), PartPose.offsetAndRotation(-4.50000F, 3.00000F, 0.00000F, -0.18000F, 0.00000F, 0.08000F));
        PartDefinition hand_right = right_arm.addOrReplaceChild("hand_right", CubeListBuilder.create().texOffs(38, 16).addBox(-1.00000F, 0.00000F, -1.00000F, 2.00000F, 3.00000F, 2.00000F), PartPose.offsetAndRotation(0.00000F, 6.00000F, -0.10000F, 0.00000F, 0.00000F, 0.00000F));
        PartDefinition strip_right = body.addOrReplaceChild("strip_right", CubeListBuilder.create().texOffs(47, 16).addBox(-1.50000F, 0.00000F, -1.00000F, 3.00000F, 7.00000F, 1.00000F), PartPose.offsetAndRotation(-2.20000F, 9.00000F, 0.60000F, 0.10000F, -0.12000F, 0.16000F));
        PartDefinition strip_right_tip = strip_right.addOrReplaceChild("strip_right_tip", CubeListBuilder.create().texOffs(56, 16).addBox(-1.00000F, 0.00000F, -0.40000F, 2.00000F, 3.00000F, 1.00000F), PartPose.offsetAndRotation(0.00000F, 6.00000F, 0.00000F, 0.11000F, 0.00000F, 0.00000F));
        PartDefinition left_arm = root.addOrReplaceChild("left_arm", CubeListBuilder.create().texOffs(63, 16).addBox(-1.50000F, 0.00000F, -1.50000F, 3.00000F, 7.00000F, 3.00000F), PartPose.offsetAndRotation(4.50000F, 3.00000F, 0.00000F, -0.18000F, 0.00000F, -0.08000F));
        PartDefinition hand_left = left_arm.addOrReplaceChild("hand_left", CubeListBuilder.create().texOffs(76, 16).addBox(-1.00000F, 0.00000F, -1.00000F, 2.00000F, 3.00000F, 2.00000F), PartPose.offsetAndRotation(0.00000F, 6.00000F, -0.10000F, 0.00000F, 0.00000F, 0.00000F));
        PartDefinition strip_left = body.addOrReplaceChild("strip_left", CubeListBuilder.create().texOffs(85, 16).addBox(-1.50000F, 0.00000F, -1.00000F, 3.00000F, 9.00000F, 1.00000F), PartPose.offsetAndRotation(2.20000F, 9.00000F, 0.60000F, -0.06000F, 0.12000F, -0.16000F));
        PartDefinition strip_left_tip = strip_left.addOrReplaceChild("strip_left_tip", CubeListBuilder.create().texOffs(94, 16).addBox(-1.00000F, 0.00000F, -0.40000F, 2.00000F, 3.00000F, 1.00000F), PartPose.offsetAndRotation(0.00000F, 8.00000F, 0.00000F, 0.11000F, 0.00000F, 0.00000F));
        PartDefinition backcloth = body.addOrReplaceChild("backcloth", CubeListBuilder.create().texOffs(101, 16).addBox(-3.00000F, 0.00000F, 0.00000F, 6.00000F, 13.00000F, 1.00000F), PartPose.offsetAndRotation(0.00000F, 2.00000F, 2.00000F, 0.00000F, 0.00000F, 0.00000F));
        PartDefinition rear_strip = backcloth.addOrReplaceChild("rear_strip", CubeListBuilder.create().texOffs(116, 16).addBox(-1.50000F, 0.00000F, 0.00000F, 3.00000F, 6.00000F, 1.00000F), PartPose.offsetAndRotation(-0.70000F, 12.00000F, 0.10000F, 0.24000F, 0.05000F, 0.08000F));
        return LayerDefinition.create(mesh, 128, 128);
    }

    public static LayerDefinition thunder_envoy() {
        MeshDefinition mesh = new MeshDefinition();
        PartDefinition root = mesh.getRoot();
        PartDefinition body = root.addOrReplaceChild("body", CubeListBuilder.create().texOffs(1, 1).addBox(-4.00000F, 0.00000F, -2.00000F, 8.00000F, 12.00000F, 4.00000F), PartPose.offsetAndRotation(0.00000F, 0.00000F, 0.00000F, 0.00000F, 0.00000F, 0.00000F));
        PartDefinition head = root.addOrReplaceChild("head", CubeListBuilder.create().texOffs(26, 1).addBox(-4.00000F, -8.00000F, -4.00000F, 8.00000F, 8.00000F, 8.00000F), PartPose.offsetAndRotation(0.00000F, 0.00000F, 0.00000F, 0.00000F, 0.00000F, 0.00000F));
        PartDefinition right_arm = root.addOrReplaceChild("right_arm", CubeListBuilder.create().texOffs(59, 1).addBox(-3.00000F, -2.00000F, -2.00000F, 4.00000F, 12.00000F, 4.00000F), PartPose.offsetAndRotation(-5.00000F, 2.00000F, 0.00000F, 0.00000F, 0.00000F, 0.00000F));
        PartDefinition right_leg = root.addOrReplaceChild("right_leg", CubeListBuilder.create().texOffs(76, 1).addBox(-2.00000F, 0.00000F, -2.00000F, 4.00000F, 12.00000F, 4.00000F), PartPose.offsetAndRotation(-1.90000F, 12.00000F, 0.00000F, 0.00000F, 0.00000F, 0.00000F));
        PartDefinition left_arm = root.addOrReplaceChild("left_arm", CubeListBuilder.create().texOffs(93, 1).addBox(-1.00000F, -2.00000F, -2.00000F, 4.00000F, 12.00000F, 4.00000F), PartPose.offsetAndRotation(5.00000F, 2.00000F, 0.00000F, 0.00000F, 0.00000F, 0.00000F));
        PartDefinition left_leg = root.addOrReplaceChild("left_leg", CubeListBuilder.create().texOffs(110, 1).addBox(-2.00000F, 0.00000F, -2.00000F, 4.00000F, 12.00000F, 4.00000F), PartPose.offsetAndRotation(1.90000F, 12.00000F, 0.00000F, 0.00000F, 0.00000F, 0.00000F));
        PartDefinition headband = head.addOrReplaceChild("headband", CubeListBuilder.create().texOffs(1, 18).addBox(-4.15000F, -0.60000F, -4.15000F, 8.00000F, 1.00000F, 8.00000F), PartPose.offsetAndRotation(0.00000F, -6.70000F, 0.00000F, 0.00000F, 0.00000F, 0.00000F));
        PartDefinition knot = head.addOrReplaceChild("knot", CubeListBuilder.create().texOffs(34, 18).addBox(-0.50000F, 0.00000F, 0.00000F, 1.00000F, 5.00000F, 1.00000F), PartPose.offsetAndRotation(3.00000F, -5.80000F, 3.90000F, 0.00000F, 0.00000F, 0.00000F));
        PartDefinition collar = body.addOrReplaceChild("collar", CubeListBuilder.create().texOffs(39, 18).addBox(-3.00000F, -0.30000F, -0.30000F, 6.00000F, 2.00000F, 1.00000F), PartPose.offsetAndRotation(0.00000F, 0.00000F, -2.10000F, 0.00000F, 0.00000F, 0.00000F));
        PartDefinition cuff_right = right_arm.addOrReplaceChild("cuff_right", CubeListBuilder.create().texOffs(54, 18).addBox(-2.15000F, 0.00000F, -2.15000F, 4.00000F, 2.00000F, 4.00000F), PartPose.offsetAndRotation(-1.00000F, 6.30000F, 0.00000F, 0.00000F, 0.00000F, 0.00000F));
        PartDefinition cuff_left = left_arm.addOrReplaceChild("cuff_left", CubeListBuilder.create().texOffs(71, 18).addBox(-2.15000F, 0.00000F, -2.15000F, 4.00000F, 2.00000F, 4.00000F), PartPose.offsetAndRotation(1.00000F, 6.30000F, 0.00000F, 0.00000F, 0.00000F, 0.00000F));
        return LayerDefinition.create(mesh, 128, 128);
    }

    public static LayerDefinition merfolk() {
        MeshDefinition mesh = new MeshDefinition();
        PartDefinition root = mesh.getRoot();
        PartDefinition body = root.addOrReplaceChild("body", CubeListBuilder.create().texOffs(1, 1).addBox(-4.00000F, 0.00000F, -2.00000F, 8.00000F, 12.00000F, 4.00000F), PartPose.offsetAndRotation(0.00000F, 0.00000F, 0.00000F, 0.00000F, 0.00000F, 0.00000F));
        PartDefinition head = root.addOrReplaceChild("head", CubeListBuilder.create().texOffs(26, 1).addBox(-4.00000F, -8.00000F, -4.00000F, 8.00000F, 8.00000F, 8.00000F), PartPose.offsetAndRotation(0.00000F, 0.00000F, 0.00000F, 0.00000F, 0.00000F, 0.00000F));
        PartDefinition right_arm = root.addOrReplaceChild("right_arm", CubeListBuilder.create().texOffs(59, 1).addBox(-3.00000F, -2.00000F, -2.00000F, 4.00000F, 12.00000F, 4.00000F), PartPose.offsetAndRotation(-5.00000F, 2.00000F, 0.00000F, 0.00000F, 0.00000F, 0.00000F));
        PartDefinition right_leg = root.addOrReplaceChild("right_leg", CubeListBuilder.create().texOffs(76, 1).addBox(-2.00000F, 0.00000F, -2.00000F, 4.00000F, 12.00000F, 4.00000F), PartPose.offsetAndRotation(-1.90000F, 12.00000F, 0.00000F, 0.00000F, 0.00000F, 0.00000F));
        PartDefinition left_arm = root.addOrReplaceChild("left_arm", CubeListBuilder.create().texOffs(93, 1).addBox(-1.00000F, -2.00000F, -2.00000F, 4.00000F, 12.00000F, 4.00000F), PartPose.offsetAndRotation(5.00000F, 2.00000F, 0.00000F, 0.00000F, 0.00000F, 0.00000F));
        PartDefinition left_leg = root.addOrReplaceChild("left_leg", CubeListBuilder.create().texOffs(110, 1).addBox(-2.00000F, 0.00000F, -2.00000F, 4.00000F, 12.00000F, 4.00000F), PartPose.offsetAndRotation(1.90000F, 12.00000F, 0.00000F, 0.00000F, 0.00000F, 0.00000F));
        PartDefinition gill_right = head.addOrReplaceChild("gill_right", CubeListBuilder.create().texOffs(1, 18).addBox(-0.40000F, -2.00000F, 0.00000F, 1.00000F, 4.00000F, 3.00000F), PartPose.offsetAndRotation(-3.90000F, -3.00000F, 0.70000F, 0.00000F, -0.22000F, -0.14000F));
        PartDefinition gill_left = head.addOrReplaceChild("gill_left", CubeListBuilder.create().texOffs(10, 18).addBox(-0.40000F, -2.00000F, 0.00000F, 1.00000F, 4.00000F, 3.00000F), PartPose.offsetAndRotation(3.90000F, -3.00000F, 0.70000F, 0.00000F, 0.22000F, 0.14000F));
        PartDefinition dorsal = body.addOrReplaceChild("dorsal", CubeListBuilder.create().texOffs(19, 18).addBox(-0.40000F, 0.00000F, 0.00000F, 1.00000F, 7.00000F, 3.00000F), PartPose.offsetAndRotation(0.00000F, 2.00000F, 1.90000F, 0.00000F, 0.00000F, 0.00000F));
        PartDefinition tail = body.addOrReplaceChild("tail", CubeListBuilder.create().texOffs(28, 18).addBox(-1.00000F, 0.00000F, 0.00000F, 2.00000F, 3.00000F, 5.00000F), PartPose.offsetAndRotation(0.00000F, 10.00000F, 1.90000F, -0.42000F, 0.00000F, 0.00000F));
        PartDefinition tail_fin = tail.addOrReplaceChild("tail_fin", CubeListBuilder.create().texOffs(43, 18).addBox(-3.00000F, 0.00000F, 0.00000F, 6.00000F, 1.00000F, 3.00000F), PartPose.offsetAndRotation(0.00000F, 0.00000F, 4.00000F, 0.12000F, 0.00000F, 0.00000F));
        return LayerDefinition.create(mesh, 128, 128);
    }

    public static LayerDefinition terracotta_warrior() {
        MeshDefinition mesh = new MeshDefinition();
        PartDefinition root = mesh.getRoot();
        PartDefinition body = root.addOrReplaceChild("body", CubeListBuilder.create().texOffs(1, 1).addBox(-4.00000F, 0.00000F, -2.00000F, 8.00000F, 12.00000F, 4.00000F), PartPose.offsetAndRotation(0.00000F, 0.00000F, 0.00000F, 0.00000F, 0.00000F, 0.00000F));
        PartDefinition head = root.addOrReplaceChild("head", CubeListBuilder.create().texOffs(26, 1).addBox(-4.00000F, -8.00000F, -4.00000F, 8.00000F, 8.00000F, 8.00000F), PartPose.offsetAndRotation(0.00000F, 0.00000F, 0.00000F, 0.00000F, 0.00000F, 0.00000F));
        PartDefinition right_arm = root.addOrReplaceChild("right_arm", CubeListBuilder.create().texOffs(59, 1).addBox(-3.00000F, -2.00000F, -2.00000F, 4.00000F, 12.00000F, 4.00000F), PartPose.offsetAndRotation(-5.00000F, 2.00000F, 0.00000F, 0.00000F, 0.00000F, 0.00000F));
        PartDefinition right_leg = root.addOrReplaceChild("right_leg", CubeListBuilder.create().texOffs(76, 1).addBox(-2.00000F, 0.00000F, -2.00000F, 4.00000F, 12.00000F, 4.00000F), PartPose.offsetAndRotation(-1.90000F, 12.00000F, 0.00000F, 0.00000F, 0.00000F, 0.00000F));
        PartDefinition left_arm = root.addOrReplaceChild("left_arm", CubeListBuilder.create().texOffs(93, 1).addBox(-1.00000F, -2.00000F, -2.00000F, 4.00000F, 12.00000F, 4.00000F), PartPose.offsetAndRotation(5.00000F, 2.00000F, 0.00000F, 0.00000F, 0.00000F, 0.00000F));
        PartDefinition left_leg = root.addOrReplaceChild("left_leg", CubeListBuilder.create().texOffs(110, 1).addBox(-2.00000F, 0.00000F, -2.00000F, 4.00000F, 12.00000F, 4.00000F), PartPose.offsetAndRotation(1.90000F, 12.00000F, 0.00000F, 0.00000F, 0.00000F, 0.00000F));
        PartDefinition topknot = head.addOrReplaceChild("topknot", CubeListBuilder.create().texOffs(1, 18).addBox(-1.50000F, -2.00000F, -1.50000F, 3.00000F, 2.00000F, 3.00000F), PartPose.offsetAndRotation(1.00000F, -8.00000F, 1.00000F, 0.00000F, 0.00000F, 0.00000F));
        PartDefinition collar = body.addOrReplaceChild("collar", CubeListBuilder.create().texOffs(14, 18).addBox(-3.00000F, -0.30000F, -0.60000F, 6.00000F, 2.00000F, 1.00000F), PartPose.offsetAndRotation(0.00000F, 0.30000F, -2.00000F, 0.00000F, 0.00000F, 0.00000F));
        PartDefinition shoulder_right = right_arm.addOrReplaceChild("shoulder_right", CubeListBuilder.create().texOffs(29, 18).addBox(-2.00000F, -0.30000F, -2.30000F, 4.00000F, 2.00000F, 5.00000F), PartPose.offsetAndRotation(-1.00000F, -1.70000F, 0.00000F, 0.00000F, 0.00000F, 0.00000F));
        PartDefinition shoulder_left = left_arm.addOrReplaceChild("shoulder_left", CubeListBuilder.create().texOffs(48, 18).addBox(-2.00000F, -0.30000F, -2.30000F, 4.00000F, 2.00000F, 5.00000F), PartPose.offsetAndRotation(1.00000F, -1.70000F, 0.00000F, 0.00000F, 0.00000F, 0.00000F));
        return LayerDefinition.create(mesh, 128, 128);
    }

    public static LayerDefinition minister() {
        MeshDefinition mesh = new MeshDefinition();
        PartDefinition root = mesh.getRoot();
        PartDefinition body = root.addOrReplaceChild("body", CubeListBuilder.create().texOffs(1, 1).addBox(-4.00000F, 0.00000F, -2.00000F, 8.00000F, 12.00000F, 4.00000F), PartPose.offsetAndRotation(0.00000F, 0.00000F, 0.00000F, 0.00000F, 0.00000F, 0.00000F));
        PartDefinition head = root.addOrReplaceChild("head", CubeListBuilder.create().texOffs(26, 1).addBox(-4.00000F, -8.00000F, -4.00000F, 8.00000F, 8.00000F, 8.00000F), PartPose.offsetAndRotation(0.00000F, 0.00000F, 0.00000F, 0.00000F, 0.00000F, 0.00000F));
        PartDefinition right_arm = root.addOrReplaceChild("right_arm", CubeListBuilder.create().texOffs(59, 1).addBox(-3.00000F, -2.00000F, -2.00000F, 4.00000F, 12.00000F, 4.00000F), PartPose.offsetAndRotation(-5.00000F, 2.00000F, 0.00000F, 0.00000F, 0.00000F, 0.00000F));
        PartDefinition right_leg = root.addOrReplaceChild("right_leg", CubeListBuilder.create().texOffs(76, 1).addBox(-2.00000F, 0.00000F, -2.00000F, 4.00000F, 12.00000F, 4.00000F), PartPose.offsetAndRotation(-1.90000F, 12.00000F, 0.00000F, 0.00000F, 0.00000F, 0.00000F));
        PartDefinition left_arm = root.addOrReplaceChild("left_arm", CubeListBuilder.create().texOffs(93, 1).addBox(-1.00000F, -2.00000F, -2.00000F, 4.00000F, 12.00000F, 4.00000F), PartPose.offsetAndRotation(5.00000F, 2.00000F, 0.00000F, 0.00000F, 0.00000F, 0.00000F));
        PartDefinition left_leg = root.addOrReplaceChild("left_leg", CubeListBuilder.create().texOffs(110, 1).addBox(-2.00000F, 0.00000F, -2.00000F, 4.00000F, 12.00000F, 4.00000F), PartPose.offsetAndRotation(1.90000F, 12.00000F, 0.00000F, 0.00000F, 0.00000F, 0.00000F));
        PartDefinition hat = head.addOrReplaceChild("hat", CubeListBuilder.create().texOffs(1, 18).addBox(-4.00000F, -1.20000F, -4.00000F, 8.00000F, 2.00000F, 8.00000F, new CubeDeformation(0.15000F)), PartPose.offsetAndRotation(0.00000F, -7.80000F, 0.00000F, 0.00000F, 0.00000F, 0.00000F));
        PartDefinition hat_fold_right = hat.addOrReplaceChild("hat_fold_right", CubeListBuilder.create().texOffs(34, 18).addBox(-1.00000F, 0.00000F, 0.00000F, 1.00000F, 1.00000F, 3.00000F), PartPose.offsetAndRotation(-3.80000F, -0.30000F, 1.00000F, 0.00000F, 0.00000F, -0.10000F));
        PartDefinition hat_fold_left = hat.addOrReplaceChild("hat_fold_left", CubeListBuilder.create().texOffs(43, 18).addBox(0.00000F, 0.00000F, 0.00000F, 1.00000F, 1.00000F, 3.00000F), PartPose.offsetAndRotation(3.80000F, -0.30000F, 1.00000F, 0.00000F, 0.00000F, 0.10000F));
        PartDefinition collar = body.addOrReplaceChild("collar", CubeListBuilder.create().texOffs(52, 18).addBox(-3.00000F, -0.50000F, -0.30000F, 6.00000F, 2.00000F, 1.00000F), PartPose.offsetAndRotation(0.00000F, 0.70000F, -2.10000F, 0.00000F, 0.00000F, 0.00000F));
        return LayerDefinition.create(mesh, 128, 128);
    }
}
