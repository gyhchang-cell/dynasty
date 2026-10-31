package com.sammy.malum.client.model.armor;


import com.google.common.collect.*;
import com.sammy.malum.*;
import com.sammy.malum.client.model.CachedModelPart;
import net.minecraft.client.*;
import net.minecraft.client.model.*;
import net.minecraft.client.model.geom.*;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.client.player.*;
import net.minecraft.util.*;
import net.minecraft.world.entity.*;
import team.lodestar.lodestone.modules.rendering.model.entity.EntityModelHolder;
import team.lodestar.lodestone.modules.rendering.model.entity.armor.*;

public class MalignantStrongholdArmorModel extends LodestoneArmorModel {

    public static EntityModelHolder<MalignantStrongholdArmorModel> MODEL = new EntityModelHolder<>(MalumMod.malumPath("malignant_stronghold"), MalignantStrongholdArmorModel::new, MalignantStrongholdArmorModel::createBodyLayer);


    public ModelPart scarf;
    public CachedModelPart lowerScarf;
    public CachedModelPart middleScarf;
    public CachedModelPart upperScarf;

    public MalignantStrongholdArmorModel(ModelPart root) {
        super(root);
        this.scarf = root.getChild("scarf");
        this.lowerScarf = CachedModelPart.of(scarf.getChild("lower_scarf"));
        this.middleScarf = CachedModelPart.of(scarf.getChild("middle_scarf"));
        this.upperScarf = CachedModelPart.of(scarf.getChild("upper_scarf"));
    }


    @Override
    protected Iterable<ModelPart> bodyParts() {
        if (slot.equals(EquipmentSlot.CHEST)) {
            return ImmutableList.of(bodyArmor, leftArmArmor, rightArmArmor, scarf);
        }
        return super.bodyParts();
    }

    @Override
    public void copyFromDefault(HumanoidModel model) {
        super.copyFromDefault(model);
        scarf.copyFrom(model.body);
        model.hat.visible = false;
    }

    @Override
    public void setupAnim(LivingEntity pEntity, float pLimbSwing, float pLimbSwingAmount, float pAgeInTicks, float pNetHeadYaw, float pHeadPitch) {
        float pPartialTicks = Minecraft.getInstance().getTimer().getGameTimeDeltaTicks();
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
            lowerScarf.applyRotation(x / 2f, y / 2f, z / 2f);
            middleScarf.applyRotation(x, y, z);
            upperScarf.applyRotation(x, y, z);
        } else {
            lowerScarf.applyRotation(0, 0, 0);
            middleScarf.applyRotation(0, 0, 0);
            upperScarf.applyRotation(0, 0, 0);
        }
        super.setupAnim(pEntity, pLimbSwing, pLimbSwingAmount, pAgeInTicks, pNetHeadYaw, pHeadPitch);
    }

    public static LayerDefinition createBodyLayer() {
        return createArmorModel((mesh, root, head, body, waist, right_arm, left_arm, right_leg, left_leg, right_foot, left_foot) -> {
            PartDefinition head_armor = head.addOrReplaceChild("head_armor", CubeListBuilder.create().texOffs(0, 29).addBox(-4.0F, -9.5F, -5.0F, 3.0F, 4.0F, 9.0F, new CubeDeformation(0.01F))
                    .texOffs(0, 17).addBox(-4.5F, -6.5F, -1.5F, 9.0F, 6.0F, 6.0F, new CubeDeformation(0.0F))
                    .texOffs(0, 29).mirror().addBox(1.0F, -9.5F, -5.0F, 3.0F, 4.0F, 9.0F, new CubeDeformation(0.01F)).mirror(false)
                    .texOffs(0, 0).addBox(-1.5F, -10.5F, -5.5F, 3.0F, 6.0F, 11.0F, new CubeDeformation(0.0F))
                    .texOffs(28, 1).addBox(-5.5F, -11.5F, -4.5F, 2.0F, 6.0F, 10.0F, new CubeDeformation(0.0F))
                    .texOffs(28, 1).mirror().addBox(3.5F, -11.5F, -4.5F, 2.0F, 6.0F, 10.0F, new CubeDeformation(0.0F)).mirror(false)
                    .texOffs(42, 4).addBox(-6.5F, -8.0F, -5.5F, 4.0F, 3.0F, 4.0F, new CubeDeformation(0.0F))
                    .texOffs(42, 4).mirror().addBox(2.5F, -8.0F, -5.5F, 4.0F, 3.0F, 4.0F, new CubeDeformation(0.0F)).mirror(false)
                    .texOffs(62, 29).addBox(-4.0F, -9.5F, -5.0F, 3.0F, 4.0F, 9.0F, new CubeDeformation(0.3F))
                    .texOffs(62, 17).addBox(-4.5F, -6.5F, -1.5F, 9.0F, 6.0F, 6.0F, new CubeDeformation(0.3F))
                    .texOffs(62, 29).mirror().addBox(1.0F, -9.5F, -5.0F, 3.0F, 4.0F, 9.0F, new CubeDeformation(0.3F)).mirror(false)
                    .texOffs(62, 0).addBox(-1.5F, -10.5F, -5.5F, 3.0F, 6.0F, 11.0F, new CubeDeformation(0.3F))
                    .texOffs(90, 1).addBox(-5.5F, -11.5F, -4.5F, 2.0F, 6.0F, 10.0F, new CubeDeformation(0.3F))
                    .texOffs(90, 1).mirror().addBox(3.5F, -11.5F, -4.5F, 2.0F, 6.0F, 10.0F, new CubeDeformation(0.3F)).mirror(false)
                    .texOffs(104, 4).addBox(-6.5F, -8.0F, -5.5F, 4.0F, 3.0F, 4.0F, new CubeDeformation(0.3F))
                    .texOffs(104, 4).mirror().addBox(2.5F, -8.0F, -5.5F, 4.0F, 3.0F, 4.0F, new CubeDeformation(0.3F)).mirror(false), PartPose.offset(0.0F, 0.0F, 0.0F));

            PartDefinition cover = head_armor.addOrReplaceChild("cover", CubeListBuilder.create().texOffs(27, 29).mirror().addBox(2.5F, -5.222F, -4.8053F, 3.0F, 5.0F, 2.0F, new CubeDeformation(0.0F)).mirror(false)
                    .texOffs(27, 29).addBox(-5.5F, -5.222F, -4.8053F, 3.0F, 5.0F, 2.0F, new CubeDeformation(0.0F))
                    .texOffs(15, 29).addBox(-2.5F, -5.222F, -4.8053F, 5.0F, 6.0F, 1.0F, new CubeDeformation(0.0F))
                    .texOffs(77, 29).addBox(-2.5F, -5.222F, -4.8053F, 5.0F, 6.0F, 1.0F, new CubeDeformation(0.25F))
                    .texOffs(89, 29).mirror().addBox(2.5F, -5.222F, -4.8053F, 3.0F, 5.0F, 2.0F, new CubeDeformation(0.25F)).mirror(false)
                    .texOffs(89, 29).addBox(-5.5F, -5.222F, -4.8053F, 3.0F, 5.0F, 2.0F, new CubeDeformation(0.25F)), PartPose.offsetAndRotation(0.0F, 0.5F, 0.0F, -0.1309F, 0.0F, 0.0F));

            PartDefinition left_guard = head_armor.addOrReplaceChild("left_guard", CubeListBuilder.create().texOffs(17, 0).mirror().addBox(-1.5F, -1.0F, -2.5F, 3.0F, 6.0F, 5.0F, new CubeDeformation(0.0F)).mirror(false)
                    .texOffs(79, 0).mirror().addBox(-1.5F, -1.0F, -2.5F, 3.0F, 6.0F, 5.0F, new CubeDeformation(0.3F)).mirror(false), PartPose.offsetAndRotation(4.0F, -5.5F, -2.35F, 0.0F, 0.0F, -0.2618F));

            PartDefinition right_guard = head_armor.addOrReplaceChild("right_guard", CubeListBuilder.create().texOffs(17, 0).addBox(-1.5F, -1.0F, -2.5F, 3.0F, 6.0F, 5.0F, new CubeDeformation(0.0F))
                    .texOffs(79, 0).addBox(-1.5F, -1.0F, -2.5F, 3.0F, 6.0F, 5.0F, new CubeDeformation(0.3F)), PartPose.offsetAndRotation(-4.0F, -5.5F, -2.35F, 0.0F, 0.0F, 0.2618F));

            PartDefinition body_armor = body.addOrReplaceChild("body_armor", CubeListBuilder.create().texOffs(0, 49).addBox(-5.0F, 2.0F, -3.0F, 10.0F, 5.0F, 6.0F, new CubeDeformation(0.025F))
                    .texOffs(0, 60).addBox(-4.5F, 6.5F, -2.5F, 9.0F, 4.0F, 5.0F, new CubeDeformation(0.0F))
                    .texOffs(62, 49).addBox(-5.0F, 2.0F, -3.0F, 10.0F, 5.0F, 6.0F, new CubeDeformation(0.275F))
                    .texOffs(62, 60).addBox(-4.5F, 6.5F, -2.5F, 9.0F, 4.0F, 5.0F, new CubeDeformation(0.25F)), PartPose.offset(0.0F, 0.0F, 0.0F));

            PartDefinition cuirass = body_armor.addOrReplaceChild("cuirass", CubeListBuilder.create().texOffs(15, 36).addBox(-6.0F, -0.95F, -4.925F, 12.0F, 4.0F, 9.0F, new CubeDeformation(0.0F))
                    .texOffs(77, 36).addBox(-6.0F, -0.95F, -4.925F, 12.0F, 4.0F, 9.0F, new CubeDeformation(0.25F)), PartPose.offsetAndRotation(0.0F, 0.0F, 0.0F, 0.2618F, 0.0F, 0.0F));

            PartDefinition scarf = root.addOrReplaceChild("scarf", new CubeListBuilder(), PartPose.ZERO);

            PartDefinition lower_scarf = scarf.addOrReplaceChild("lower_scarf", CubeListBuilder.create().texOffs(0, 112).addBox(-5.5F, 2.05F, 4.075F, 11.0F, 10.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 0.0F, 0.0F, 0.0873F, 0.0F, 0.0F));

            PartDefinition middle_scarf = scarf.addOrReplaceChild("middle_scarf", CubeListBuilder.create().texOffs(40, 101).addBox(-3.5F, -0.95F, 4.325F, 7.0F, 21.0F, 0.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 0.0F, 0.0F, 0.2182F, 0.0F, 0.0F));

            PartDefinition upper_scarf = scarf.addOrReplaceChild("upper_scarf", CubeListBuilder.create().texOffs(41, 92).addBox(-4.5F, -0.95F, 1.575F, 9.0F, 6.0F, 3.0F, new CubeDeformation(0.0F)), PartPose.offsetAndRotation(0.0F, 0.0F, 0.0F, 0.5236F, 0.0F, 0.0F));

            PartDefinition waist_armor = waist.addOrReplaceChild("waist_armor", CubeListBuilder.create().texOffs(36, 76).addBox(-4.5F, 9.5F, -3.0F, 9.0F, 2.0F, 6.0F, new CubeDeformation(0.06F))
                    .texOffs(98, 76).addBox(-4.5F, 9.5F, -3.0F, 9.0F, 2.0F, 6.0F, new CubeDeformation(0.31F)), PartPose.offset(0.0F, 0.0F, 0.0F));

            PartDefinition codpiece_cloth = waist_armor.addOrReplaceChild("codpiece_cloth", CubeListBuilder.create().texOffs(0, 95).addBox(-2.5F, 6.5F, -3.0F, 5.0F, 11.0F, 6.0F, new CubeDeformation(0.15F))
                    .texOffs(62, 95).addBox(-2.5F, 6.5F, -3.0F, 5.0F, 11.0F, 6.0F, new CubeDeformation(0.4F)), PartPose.offset(0.0F, 0.0F, 0.0F));

            PartDefinition left_arm_armor = left_arm.addOrReplaceChild("left_arm_armor", CubeListBuilder.create().texOffs(33, 49).addBox(3.0F, -4.5F, -3.0F, 2.0F, 5.0F, 6.0F, new CubeDeformation(0.01F))
                    .texOffs(22, 109).addBox(2.0F, 2.0F, -3.0F, 3.0F, 5.0F, 6.0F, new CubeDeformation(0.01F))
                    .texOffs(0, 69).addBox(0.0F, -5.5F, -3.0F, 3.0F, 6.0F, 6.0F, new CubeDeformation(0.01F))
                    .texOffs(95, 49).addBox(3.0F, -4.5F, -3.0F, 2.0F, 5.0F, 6.0F, new CubeDeformation(0.26F))
                    .texOffs(62, 69).addBox(0.0F, -5.5F, -3.0F, 3.0F, 6.0F, 6.0F, new CubeDeformation(0.26F)), PartPose.offset(0.0F, 0.0F, 0.0F));

            PartDefinition left_shoulder_pad = left_arm_armor.addOrReplaceChild("left_shoulder_pad", CubeListBuilder.create().texOffs(20, 61).addBox(1.8918F, -1.4882F, -4.0F, 6.0F, 3.0F, 8.0F, new CubeDeformation(0.01F))
                    .texOffs(82, 61).addBox(1.8918F, -1.4882F, -4.0F, 6.0F, 3.0F, 8.0F, new CubeDeformation(0.26F)), PartPose.offsetAndRotation(-2.0F, 0.0F, 0.0F, 0.0F, 0.0F, 0.2182F));

            PartDefinition right_arm_armor = right_arm.addOrReplaceChild("right_arm_armor", CubeListBuilder.create().texOffs(33, 49).mirror().addBox(-5.0F, -4.5F, -3.0F, 2.0F, 5.0F, 6.0F, new CubeDeformation(0.01F)).mirror(false)
                    .texOffs(0, 69).mirror().addBox(-3.0F, -5.5F, -3.0F, 3.0F, 6.0F, 6.0F, new CubeDeformation(0.01F)).mirror(false)
                    .texOffs(22, 109).mirror().addBox(-5.0F, 2.0F, -3.0F, 3.0F, 5.0F, 6.0F, new CubeDeformation(0.01F)).mirror(false)
                    .texOffs(95, 49).mirror().addBox(-5.0F, -4.5F, -3.0F, 2.0F, 5.0F, 6.0F, new CubeDeformation(0.26F)).mirror(false)
                    .texOffs(62, 69).mirror().addBox(-3.0F, -5.5F, -3.0F, 3.0F, 6.0F, 6.0F, new CubeDeformation(0.26F)).mirror(false), PartPose.offset(0.0F, 0.0F, 0.0F));

            PartDefinition right_shoulder_pad = right_arm_armor.addOrReplaceChild("right_shoulder_pad", CubeListBuilder.create().texOffs(20, 61).mirror().addBox(-7.6753F, -1.4644F, -4.0F, 6.0F, 3.0F, 8.0F, new CubeDeformation(0.01F)).mirror(false)
                    .texOffs(82, 61).mirror().addBox(-7.6753F, -1.4644F, -4.0F, 6.0F, 3.0F, 8.0F, new CubeDeformation(0.26F)).mirror(false), PartPose.offsetAndRotation(2.0F, 0.0F, 0.0F, 0.0F, 0.0F, -0.2182F));

            PartDefinition left_leg_armor = left_leg.addOrReplaceChild("left_leg_armor", CubeListBuilder.create().texOffs(0, 81).mirror().addBox(-2.4F, -0.5F, -2.5F, 5.0F, 9.0F, 5.0F, new CubeDeformation(0.0F)).mirror(false)
                    .texOffs(62, 81).mirror().addBox(-2.4F, -0.5F, -2.5F, 5.0F, 9.0F, 5.0F, new CubeDeformation(0.0F)).mirror(false), PartPose.offset(0.0F, 0.0F, 0.0F));

            PartDefinition left_thigh_guard_right = left_leg_armor.addOrReplaceChild("left_thigh_guard_right", CubeListBuilder.create().texOffs(18, 72).mirror().addBox(1.3934F, -2.3778F, -3.0F, 3.0F, 6.0F, 6.0F, new CubeDeformation(0.05F)).mirror(false)
                    .texOffs(80, 72).mirror().addBox(1.3934F, -2.3778F, -3.0F, 3.0F, 6.0F, 6.0F, new CubeDeformation(0.3F)).mirror(false), PartPose.offsetAndRotation(0.1F, 2.0F, 0.0F, 0.0F, 0.0F, -1.1345F));

            PartDefinition left_thigh_guard_bottom = left_leg_armor.addOrReplaceChild("left_thigh_guard_bottom", CubeListBuilder.create().texOffs(18, 72).mirror().addBox(-0.2266F, -2.1443F, -3.0F, 3.0F, 6.0F, 6.0F, new CubeDeformation(0.02F)).mirror(false)
                    .texOffs(80, 72).mirror().addBox(-0.2266F, -2.1443F, -3.0F, 3.0F, 6.0F, 6.0F, new CubeDeformation(0.27F)).mirror(false), PartPose.offsetAndRotation(1.1F, 4.0F, 0.0F, 0.0F, 0.0F, -1.1345F));

            PartDefinition left_leg_cloth_l = left_leg_armor.addOrReplaceChild("left_leg_cloth_l", CubeListBuilder.create().texOffs(22, 95).mirror().addBox(-0.5F, -2.0F, -3.0F, 3.0F, 8.0F, 6.0F, new CubeDeformation(0.13F)).mirror(false)
                    .texOffs(84, 95).mirror().addBox(-0.5F, -2.0F, -3.0F, 3.0F, 8.0F, 6.0F, new CubeDeformation(0.38F)).mirror(false), PartPose.offsetAndRotation(-0.9F, 1.0F, 0.0F, 0.0F, 0.0F, -0.3054F));

            PartDefinition right_leg_armor = right_leg.addOrReplaceChild("right_leg_armor", CubeListBuilder.create().texOffs(0, 81).addBox(-2.6F, -0.5F, -2.5F, 5.0F, 9.0F, 5.0F, new CubeDeformation(0.0F))
                    .texOffs(62, 81).addBox(-2.6F, -0.5F, -2.5F, 5.0F, 9.0F, 5.0F, new CubeDeformation(0.0F)), PartPose.offset(0.0F, 0.0F, 0.0F));

            PartDefinition right_thigh_guard_top = right_leg_armor.addOrReplaceChild("right_thigh_guard_top", CubeListBuilder.create().texOffs(18, 72).addBox(-4.3934F, -2.3778F, -3.0F, 3.0F, 6.0F, 6.0F, new CubeDeformation(0.05F))
                    .texOffs(80, 72).addBox(-4.3934F, -2.3778F, -3.0F, 3.0F, 6.0F, 6.0F, new CubeDeformation(0.3F)), PartPose.offsetAndRotation(-0.1F, 2.0F, 0.0F, 0.0F, 0.0F, 1.1345F));

            PartDefinition right_thigh_guard_bottom = right_leg_armor.addOrReplaceChild("right_thigh_guard_bottom", CubeListBuilder.create().texOffs(18, 72).addBox(-2.7734F, -2.1443F, -3.0F, 3.0F, 6.0F, 6.0F, new CubeDeformation(0.02F))
                    .texOffs(80, 72).addBox(-2.7734F, -2.1443F, -3.0F, 3.0F, 6.0F, 6.0F, new CubeDeformation(0.27F)), PartPose.offsetAndRotation(-1.1F, 4.0F, 0.0F, 0.0F, 0.0F, 1.1345F));

            PartDefinition right_leg_cloth_r = right_leg_armor.addOrReplaceChild("right_leg_cloth_r", CubeListBuilder.create().texOffs(22, 95).addBox(-2.5F, -2.0F, -3.0F, 3.0F, 8.0F, 6.0F, new CubeDeformation(0.13F))
                    .texOffs(84, 95).addBox(-2.5F, -2.0F, -3.0F, 3.0F, 8.0F, 6.0F, new CubeDeformation(0.38F)), PartPose.offsetAndRotation(0.9F, 1.0F, 0.0F, 0.0F, 0.0F, 0.3054F));

            PartDefinition left_foot_armor = left_foot.addOrReplaceChild("left_foot_armor", CubeListBuilder.create().texOffs(20, 84).addBox(-2.9F, 8.0F, -3.0F, 6.0F, 5.0F, 6.0F, new CubeDeformation(0.01F))
                    .texOffs(82, 84).addBox(-2.9F, 8.0F, -3.0F, 6.0F, 5.0F, 6.0F, new CubeDeformation(0.26F)), PartPose.offset(0.0F, 0.0F, 0.0F));

            PartDefinition right_foot_armor = right_foot.addOrReplaceChild("right_foot_armor", CubeListBuilder.create().texOffs(20, 84).mirror().addBox(-3.1F, 8.0F, -3.0F, 6.0F, 5.0F, 6.0F, new CubeDeformation(0.0F)).mirror(false)
                    .texOffs(82, 84).mirror().addBox(-3.1F, 8.0F, -3.0F, 6.0F, 5.0F, 6.0F, new CubeDeformation(0.25F)).mirror(false), PartPose.offset(0.0F, 0.0F, 0.0F));

            return LayerDefinition.create(mesh, 128, 128);
        });
    }
}