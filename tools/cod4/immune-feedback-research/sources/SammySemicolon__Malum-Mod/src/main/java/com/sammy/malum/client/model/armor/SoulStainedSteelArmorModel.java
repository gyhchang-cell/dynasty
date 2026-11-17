package com.sammy.malum.client.model.armor;


import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.sammy.malum.MalumMod;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.tags.ItemTags;
import team.lodestar.lodestone.modules.rendering.model.entity.EntityModelHolder;
import team.lodestar.lodestone.modules.rendering.model.entity.armor.*;

public class SoulStainedSteelArmorModel extends MalumArmorModel {

    public static EntityModelHolder<SoulStainedSteelArmorModel> MODEL = new EntityModelHolder<>(MalumMod.malumPath("soul_stained_armor"), SoulStainedSteelArmorModel::new, SoulStainedSteelArmorModel::createBodyLayer);

    public SoulStainedSteelArmorModel(ModelPart root) {
        super(root);
    }

    public static LayerDefinition createBodyLayer() {
        return createArmorModel((mesh, root, head, body, waist, right_arm, left_arm, right_leg, left_leg, right_foot, left_foot) -> {

            PartDefinition head_armor = head.addOrReplaceChild("head_armor", CubeListBuilder.create().texOffs(0, 0).addBox(-4.0F, -8.0F, -4.0F, 8.0F, 8.0F, 8.0F, new CubeDeformation(0.75F))
                    .texOffs(32, 0).addBox(-4.0F, -8.0F, -4.0F, 8.0F, 8.0F, 8.0F, new CubeDeformation(1.0F)), PartPose.offset(0.0F, 0.0F, 0.0F));

            PartDefinition body_armor = body.addOrReplaceChild("body_armor", CubeListBuilder.create().texOffs(16, 16).addBox(-4.0F, 0.0F, -2.0F, 8.0F, 12.0F, 4.0F, new CubeDeformation(0.75F)), PartPose.offset(0.0F, 0.0F, 0.0F));

            PartDefinition waist_armor = waist.addOrReplaceChild("waist_armor", CubeListBuilder.create().texOffs(16, 32).addBox(-4.0F, 0.0F, -2.0F, 8.0F, 12.0F, 4.0F, new CubeDeformation(0.5F)), PartPose.offset(0.0F, 0.0F, 0.0F));

            PartDefinition left_arm_armor = left_arm.addOrReplaceChild("left_arm_armor", CubeListBuilder.create().texOffs(40, 16).mirror().addBox(-1.0F, -2.0F, -2.0F, 4.0F, 12.0F, 4.0F, new CubeDeformation(0.75F)).mirror(false), PartPose.offset(0.0F, 0.0F, 0.0F));

            PartDefinition right_arm_armor = right_arm.addOrReplaceChild("right_arm_armor", CubeListBuilder.create().texOffs(40, 16).addBox(-3.0F, -2.0F, -2.0F, 4.0F, 12.0F, 4.0F, new CubeDeformation(0.75F)), PartPose.offset(0.0F, 0.0F, 0.0F));

            PartDefinition right_leg_armor = right_leg.addOrReplaceChild("right_leg_armor", CubeListBuilder.create().texOffs(0, 32).addBox(-2.0F, 0.0F, -2.0F, 4.0F, 12.0F, 4.0F, new CubeDeformation(0.5F)), PartPose.offset(0.0F, 0.0F, 0.0F));

            PartDefinition left_leg_armor = left_leg.addOrReplaceChild("left_leg_armor", CubeListBuilder.create().texOffs(0, 32).mirror().addBox(-2.0F, 0.0F, -2.0F, 4.0F, 12.0F, 4.0F, new CubeDeformation(0.5F)).mirror(false), PartPose.offset(0.0F, 0.0F, 0.0F));

            PartDefinition right_foot_armor = right_foot.addOrReplaceChild("right_foot_armor", CubeListBuilder.create().texOffs(0, 16).addBox(-2.0F, 0.0F, -2.0F, 4.0F, 12.0F, 4.0F, new CubeDeformation(0.75F)), PartPose.offset(0.0F, 0.0F, 0.0F));

            PartDefinition left_foot_armor = left_foot.addOrReplaceChild("left_foot_armor", CubeListBuilder.create().texOffs(0, 16).mirror().addBox(-2.0F, 0.0F, -2.0F, 4.0F, 12.0F, 4.0F, new CubeDeformation(0.75F)).mirror(false), PartPose.offset(0.0F, 0.0F, 0.0F));
            return LayerDefinition.create(mesh, 64, 64);
        });
    }
}