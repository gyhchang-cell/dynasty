package com.dynasty.client;

import net.minecraft.client.model.HumanoidModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.CubeDeformation;
import net.minecraft.client.model.geom.builders.LayerDefinition;
import net.minecraft.world.entity.Mob;

/**
 * 王朝人形模型（兵马俑/士兵/Boss 共用）。
 * Shared humanoid model for Dynasty mobs.
 */
@SuppressWarnings("null")
public class DynastyHumanoidModel<T extends Mob> extends HumanoidModel<T> {

    public DynastyHumanoidModel(ModelPart root) {
        super(root);
    }

    public static LayerDefinition createBodyLayer(float inflation) {
        return LayerDefinition.create(
                HumanoidModel.createMesh(new CubeDeformation(inflation), 0.0F), 64, 64);
    }

    public static LayerDefinition createBodyLayer() {
        return createBodyLayer(0.0F);
    }

    /** 让模型保持默认站姿 / keep the default pose */
    public static PartPose pose() {
        return PartPose.ZERO;
    }
}
