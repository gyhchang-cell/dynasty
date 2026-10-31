package com.sammy.malum.client.model.armor;


import com.google.common.collect.ImmutableList;
import com.sammy.malum.MalumMod;
import com.sammy.malum.client.model.CachedModelPart;
import net.minecraft.client.Minecraft;
import net.minecraft.client.model.HumanoidModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.client.player.AbstractClientPlayer;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import team.lodestar.lodestone.modules.rendering.model.entity.EntityModelHolder;
import team.lodestar.lodestone.modules.rendering.model.entity.armor.*;

public class SoulHunterArmorModel extends LodestoneArmorModel {

    public static EntityModelHolder<SoulHunterArmorModel> MODEL = new EntityModelHolder<>(MalumMod.malumPath("soul_hunter_armor"), SoulHunterArmorModel::new, SoulHunterArmorModel::createBodyLayer);

    public ModelPart cape;
    public ModelPart hood;

    public SoulHunterArmorModel(ModelPart root) {
        super(root);
        this.cape = root.getChild("cape");
        this.hood = root.getChild("hood");
    }

    @Override
    protected Iterable<ModelPart> bodyParts() {
        if (this.slot == EquipmentSlot.CHEST) {
            return ImmutableList.of(body, leftArmArmor, rightArmArmor, cape, hood);
        }
        return super.bodyParts();
    }

    @Override
    public void copyFromDefault(HumanoidModel model) {
        super.copyFromDefault(model);
        cape.copyFrom(model.body);
        hood.copyFrom(model.body);
        model.hat.visible = false;
    }

    @Override
    public void setupAnim(LivingEntity pEntity, float pLimbSwing, float pLimbSwingAmount, float pAgeInTicks, float pNetHeadYaw, float pHeadPitch) {
        float pPartialTicks = Minecraft.getInstance().getTimer().getGameTimeDeltaTicks();
        hood.visible = pEntity.getItemBySlot(EquipmentSlot.HEAD).isEmpty();
        if (pEntity instanceof AbstractClientPlayer clientPlayer) {
            double d0 = Mth.lerp(pPartialTicks, clientPlayer.xCloakO, clientPlayer.xCloak) - Mth.lerp(pPartialTicks, pEntity.xo, pEntity.getX());
            double d1 = Mth.lerp(pPartialTicks, clientPlayer.yCloakO, clientPlayer.yCloak) - Mth.lerp(pPartialTicks, pEntity.yo, pEntity.getY());
            double d2 = Mth.lerp(pPartialTicks, clientPlayer.zCloakO, clientPlayer.zCloak) - Mth.lerp(pPartialTicks, pEntity.zo, pEntity.getZ());
            float f = pEntity.yBodyRotO + (pEntity.yBodyRot - pEntity.yBodyRotO);
            double d3 = Mth.sin(f * ((float) Math.PI / 180F));
            double d4 = (-Mth.cos(f * ((float) Math.PI / 180F)));
            float f1 = (float) d1 * 10.0F;
            f1 = Mth.clamp(f1, -6.0F, 16.0F);
            float f2 = (float) (d0 * d3 + d2 * d4) * 65.0F;
            f2 = Mth.clamp(f2, 0.0F, 75.0F);
            float f3 = (float) (d0 * d4 - d2 * d3) * 100.0F;
            f3 = Mth.clamp(f3, -20.0F, 20.0F);
            if (f2 < 0.0F) {
                f2 = 0.0F;
            }
            float f4 = Mth.lerp(pPartialTicks, clientPlayer.oBob, clientPlayer.bob);
            f1 += Mth.sin(Mth.lerp(pPartialTicks, pEntity.walkDistO, pEntity.walkDist) * 6.0F) * 32.0F * f4;
            if (pEntity.isCrouching()) {
                f1 += 25.0F;
            }
            float x = (float) Math.toRadians(6.0F + f2 / 2.0F + f1);
            float y = (float) Math.toRadians(f3 / 2.0F);
            float z = (float) Math.toRadians(f3 / 2.0F);
            cape.setRotation(x, y, z);
            hood.setRotation(x / 3f, y / 3f, z / 3f);
        } else {
            cape.setRotation(0, 0, 0);
            hood.setRotation(0, 0, 0);
        }
        super.setupAnim(pEntity, pLimbSwing, pLimbSwingAmount, pAgeInTicks, pNetHeadYaw, pHeadPitch);
    }

    public static LayerDefinition createBodyLayer() {
        return createArmorModel((mesh, root, head, body, waist, right_arm, left_arm, right_leg, left_leg, right_foot, left_foot) -> {
            PartDefinition cape = root.addOrReplaceChild("cape", new CubeListBuilder(), PartPose.ZERO);
            PartDefinition hood = root.addOrReplaceChild("hood", CubeListBuilder.create(), PartPose.ZERO);

            PartDefinition head_armor = head.addOrReplaceChild("head_armor", CubeListBuilder.create().texOffs(0, 0).addBox(-4.5F, -8.5F, -4.0F, 9.0F, 9.0F, 9.0F, new CubeDeformation(0.0F))
                    .texOffs(36, 0).addBox(-4.5F, -8.5F, -4.0F, 9.0F, 9.0F, 9.0F, new CubeDeformation(0.25F)), PartPose.offset(0.0F, 0.0F, 0.0F));

            PartDefinition left_hood_part = head_armor.addOrReplaceChild("left_hood_part", CubeListBuilder.create().texOffs(0, 18).addBox(0.0F, -4.0F, -3.0F, 2.0F, 5.0F, 7.0F, new CubeDeformation(0.0F))
                    .texOffs(42, 18).addBox(0.0F, -4.0F, -3.0F, 2.0F, 5.0F, 7.0F, new CubeDeformation(0.25F)), PartPose.offsetAndRotation(4.5F, -0.5F, 0.0F, 0.0F, 0.0F, -0.3927F));

            PartDefinition right_hood_part = head_armor.addOrReplaceChild("right_hood_part", CubeListBuilder.create().texOffs(42, 18).mirror().addBox(-2.0F, -4.0F, -3.0F, 2.0F, 5.0F, 7.0F, new CubeDeformation(0.25F)).mirror(false)
                    .texOffs(0, 18).mirror().addBox(-2.0F, -4.0F, -3.0F, 2.0F, 5.0F, 7.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offsetAndRotation(-4.5F, -0.5F, 0.0F, 0.0F, 0.0F, 0.3927F));

            PartDefinition back_hood_part = head_armor.addOrReplaceChild("back_hood_part", CubeListBuilder.create().texOffs(18, 20).addBox(-3.5F, 0.0F, 0.0F, 7.0F, 5.0F, 5.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, -8.5F, 5.0F, -0.7854F, 0.0F, 0.0F));

            PartDefinition lowered_hood = hood.addOrReplaceChild("lowered_hood", CubeListBuilder.create().texOffs(28, 30).addBox(-3.98F, -0.5028F, -2.1359F, 8.0F, 2.0F, 5.0F, new CubeDeformation(0.0F))
                    .texOffs(54, 30).addBox(-3.98F, -0.5028F, -2.1359F, 8.0F, 2.0F, 5.0F, new CubeDeformation(0.25F)), PartPose.offsetAndRotation(0.0F, 0.0F, 0.0F, -0.6109F, 0.0F, 0.0F));

            PartDefinition body_armor = body.addOrReplaceChild("body_armor", CubeListBuilder.create().texOffs(0, 30).addBox(-4.5F, -0.5F, -2.5F, 9.0F, 10.0F, 5.0F, new CubeDeformation(0.0F))
                    .texOffs(0, 45).addBox(-4.5F, -0.5F, -2.5F, 9.0F, 10.0F, 5.0F, new CubeDeformation(0.25F)), PartPose.offset(0.0F, 0.0F, 0.0F));

            PartDefinition left_robe = body_armor.addOrReplaceChild("left_robe", CubeListBuilder.create().texOffs(28, 37).mirror().addBox(-1.0926F, -0.5F, -0.6014F, 3.0F, 10.0F, 1.0F, new CubeDeformation(0.01F)).mirror(false), PartPose.offsetAndRotation(2.5F, 0.0F, -2.5F, -0.0873F, -0.3491F, 0.0087F));

            PartDefinition right_robe = body_armor.addOrReplaceChild("right_robe", CubeListBuilder.create().texOffs(28, 37).addBox(-1.9074F, -0.5F, -0.6014F, 3.0F, 10.0F, 1.0F, new CubeDeformation(0.01F)), PartPose.offsetAndRotation(-2.5F, 0.0F, -2.5F, -0.0873F, 0.3491F, 0.0087F));

            PartDefinition cape_top = cape.addOrReplaceChild("cape_top", CubeListBuilder.create().texOffs(36, 37).addBox(-5.5213F, 0.3975F, -0.5395F, 11.0F, 8.0F, 1.0F, new CubeDeformation(0.0F))
                    .texOffs(60, 37).addBox(-5.5213F, 0.3975F, -0.5395F, 11.0F, 8.0F, 1.0F, new CubeDeformation(0.25F)), PartPose.offsetAndRotation(0.0F, 0.0F, 3.0F, 0.0873F, 0.0F, 0.0F));

            PartDefinition cape_middle = cape_top.addOrReplaceChild("cape_middle", CubeListBuilder.create().texOffs(60, 45).addBox(-5.5213F, -0.2225F, -0.5569F, 11.0F, 7.0F, 1.0F, new CubeDeformation(0.25F))
                    .texOffs(36, 45).addBox(-5.5213F, -0.2225F, -0.5569F, 11.0F, 7.0F, 1.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 8.5455F, 0.0417F, 0.1309F, 0.0F, 0.0F));

            PartDefinition cape_bottom = cape_middle.addOrReplaceChild("cape_bottom", CubeListBuilder.create().texOffs(28, 48).addBox(-5.5213F, -1.3642F, -0.3206F, 3.0F, 4.0F, 1.0F, new CubeDeformation(0.0F))
                    .texOffs(36, 53).addBox(-2.5213F, -1.3642F, -0.3206F, 5.0F, 6.0F, 1.0F, new CubeDeformation(0.0F))
                    .texOffs(28, 48).mirror().addBox(2.4787F, -1.3642F, -0.3206F, 3.0F, 4.0F, 1.0F, new CubeDeformation(0.0F)).mirror(false)
                    .texOffs(28, 53).mirror().addBox(2.4787F, -1.3642F, -0.3206F, 3.0F, 4.0F, 1.0F, new CubeDeformation(0.25F)).mirror(false)
                    .texOffs(48, 53).addBox(-2.5213F, -1.3642F, -0.3206F, 5.0F, 6.0F, 1.0F, new CubeDeformation(0.25F))
                    .texOffs(28, 53).addBox(-5.5213F, -1.3642F, -0.3206F, 3.0F, 4.0F, 1.0F, new CubeDeformation(0.25F)), PartPose.offsetAndRotation(0.0F, 8.0653F, -0.0043F, 0.1745F, 0.0F, 0.0F));

            PartDefinition waist_armor = waist.addOrReplaceChild("waist_armor", CubeListBuilder.create().texOffs(0, 71).addBox(-5.0F, 9.5F, -3.5F, 10.0F, 3.0F, 7.0F, new CubeDeformation(0.01F))
                    .texOffs(34, 71).addBox(-5.0F, 9.5F, -3.5F, 10.0F, 3.0F, 7.0F, new CubeDeformation(0.26F)), PartPose.offset(0.0F, 0.0F, 0.0F));

            PartDefinition left_arm_armor = left_arm.addOrReplaceChild("left_arm_armor", CubeListBuilder.create().texOffs(0, 60).addBox(-1.5F, -2.5F, -2.5F, 5.0F, 6.0F, 5.0F, new CubeDeformation(0.01F))
                    .texOffs(20, 60).addBox(-1.5F, -2.5F, -2.5F, 5.0F, 6.0F, 5.0F, new CubeDeformation(0.26F)), PartPose.offset(0.0F, 0.0F, 0.0F));

            PartDefinition left_glove = left_arm_armor.addOrReplaceChild("left_glove", CubeListBuilder.create().texOffs(90, 62).addBox(7.5F, -17.5F, -2.5F, 2.0F, 5.0F, 3.0F, new CubeDeformation(0.25F))
                    .texOffs(40, 60).addBox(3.5F, -16.5F, -3.5F, 5.0F, 5.0F, 5.0F, new CubeDeformation(0.01F))
                    .texOffs(60, 60).addBox(3.5F, -16.5F, -3.5F, 5.0F, 5.0F, 5.0F, new CubeDeformation(0.26F))
                    .texOffs(80, 62).addBox(7.5F, -17.5F, -2.5F, 2.0F, 5.0F, 3.0F, new CubeDeformation(0.0F)), PartPose.offset(-5.0F, 22.0F, 1.0F));

            PartDefinition right_arm_armor = right_arm.addOrReplaceChild("right_arm_armor", CubeListBuilder.create().texOffs(0, 60).mirror().addBox(-3.5F, -2.5F, -2.5F, 5.0F, 6.0F, 5.0F, new CubeDeformation(0.01F)).mirror(false)
                    .texOffs(20, 60).mirror().addBox(-3.5F, -2.5F, -2.5F, 5.0F, 6.0F, 5.0F, new CubeDeformation(0.26F)).mirror(false), PartPose.offset(0.0F, 0.0F, 0.0F));

            PartDefinition right_glove = right_arm_armor.addOrReplaceChild("right_glove", CubeListBuilder.create().texOffs(90, 62).mirror().addBox(-9.5F, -17.5F, -2.5F, 2.0F, 5.0F, 3.0F, new CubeDeformation(0.25F)).mirror(false)
                    .texOffs(40, 60).mirror().addBox(-8.5F, -16.5F, -3.5F, 5.0F, 5.0F, 5.0F, new CubeDeformation(0.01F)).mirror(false)
                    .texOffs(60, 60).mirror().addBox(-8.5F, -16.5F, -3.5F, 5.0F, 5.0F, 5.0F, new CubeDeformation(0.26F)).mirror(false)
                    .texOffs(80, 62).mirror().addBox(-9.5F, -17.5F, -2.5F, 2.0F, 5.0F, 3.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offset(5.0F, 22.0F, 1.0F));

            PartDefinition left_leg_armor = left_leg.addOrReplaceChild("left_leg_armor", CubeListBuilder.create().texOffs(0, 82).mirror().addBox(-2.4F, -0.5F, -2.5F, 5.0F, 8.0F, 5.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offset(0.0F, 0.0F, 0.0F));

            PartDefinition left_lower_robe = left_leg_armor.addOrReplaceChild("left_lower_robe", CubeListBuilder.create().texOffs(20, 81).mirror().addBox(-4.0F, -1.0F, -5.0F, 4.0F, 7.0F, 7.0F, new CubeDeformation(0.0F)).mirror(false)
                    .texOffs(42, 81).mirror().addBox(-4.0F, -1.0F, -5.0F, 4.0F, 7.0F, 7.0F, new CubeDeformation(0.25F)).mirror(false)
                    .texOffs(0, 95).mirror().addBox(0.0F, 3.0F, -5.0F, 1.0F, 3.0F, 7.0F, new CubeDeformation(0.0F)).mirror(false)
                    .texOffs(16, 95).mirror().addBox(0.0F, 3.0F, -5.0F, 1.0F, 3.0F, 7.0F, new CubeDeformation(0.25F)).mirror(false), PartPose.offsetAndRotation(3.1F, -0.5F, 1.5F, 0.0F, 0.0F, -0.3491F));

            PartDefinition right_leg_armor = right_leg.addOrReplaceChild("right_leg_armor", CubeListBuilder.create().texOffs(0, 82).addBox(-2.6F, -0.5F, -2.5F, 5.0F, 8.0F, 5.0F, new CubeDeformation(0.01F)), PartPose.offset(0.0F, 0.0F, 0.0F));

            PartDefinition right_lower_robe = right_leg_armor.addOrReplaceChild("right_lower_robe", CubeListBuilder.create().texOffs(20, 81).addBox(0.0F, -1.0F, -5.0F, 4.0F, 7.0F, 7.0F, new CubeDeformation(0.0F))
                    .texOffs(42, 81).addBox(0.0F, -1.0F, -5.0F, 4.0F, 7.0F, 7.0F, new CubeDeformation(0.25F))
                    .texOffs(0, 95).addBox(-1.0F, 3.0F, -5.0F, 1.0F, 3.0F, 7.0F, new CubeDeformation(0.0F))
                    .texOffs(16, 95).addBox(-1.0F, 3.0F, -5.0F, 1.0F, 3.0F, 7.0F, new CubeDeformation(0.25F)), PartPose.offsetAndRotation(-3.1F, -0.5F, 1.5F, 0.0F, 0.0F, 0.3491F));

            PartDefinition left_foot_armor = left_foot.addOrReplaceChild("left_foot_armor", CubeListBuilder.create().texOffs(0, 105).mirror().addBox(-2.9F, 7.0F, -3.0F, 6.0F, 6.0F, 6.0F, new CubeDeformation(0.01F)).mirror(false)
                    .texOffs(24, 105).mirror().addBox(-2.9F, 7.0F, -3.0F, 6.0F, 6.0F, 6.0F, new CubeDeformation(0.25F)).mirror(false), PartPose.offset(0.0F, 0.0F, 0.0F));

            PartDefinition right_foot_armor = right_foot.addOrReplaceChild("right_foot_armor", CubeListBuilder.create().texOffs(0, 105).addBox(-3.1F, 7.0F, -3.0F, 6.0F, 6.0F, 6.0F, new CubeDeformation(0.0F))
                    .texOffs(24, 105).addBox(-3.1F, 7.0F, -3.0F, 6.0F, 6.0F, 6.0F, new CubeDeformation(0.25F)), PartPose.offset(0.0F, 0.0F, 0.0F));
            return LayerDefinition.create(mesh, 128, 128);
        });
    }
}