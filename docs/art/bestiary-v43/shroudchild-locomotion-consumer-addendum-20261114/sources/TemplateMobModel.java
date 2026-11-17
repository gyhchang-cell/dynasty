package com.dynasty.blueprint.client;

import com.dynasty.blueprint.TemplateMob;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.model.GeoModel;
import software.bernie.geckolib.core.animation.AnimationState;

/** Shared loading; each profession owns an independently authored articulated rig. */
public final class TemplateMobModel extends GeoModel<TemplateMob> {
    @Override public void setCustomAnimations(TemplateMob mob, long instanceId, AnimationState<TemplateMob> state) {
        super.setCustomAnimations(mob, instanceId, state);
        TemplateSecondaryMotion.apply(this, mob, state.getPartialTick());
        if(mob.kind()==TemplateMob.Kind.DROWNER&&mob.isAlive()){
            boolean pool=mob.waterPool();
            getBone("body").ifPresent(b->{b.setScaleY(pool?.12F:1);b.setScaleX(pool?2.5F:1);b.setScaleZ(pool?2.5F:1);});
        }
        if(mob.kind()==TemplateMob.Kind.TOAD)
            // Independent identity wrapper: never multiply a shared animated bone across draws.
            getBone("tongue_reach").ifPresent(b->b.setScaleZ(mob.skillId()==com.dynasty.blueprint.ArmySkills.TOAD_TONGUE?mob.tongueReach()/5:1));
    }
    @Override public ResourceLocation getModelResource(TemplateMob mob) {
        return new ResourceLocation("dynasty", "geo/" + artDirectory(mob) + mob.blueprintId() + ".geo.json");
    }

    @Override public ResourceLocation getAnimationResource(TemplateMob mob) {
        return new ResourceLocation("dynasty", "animations/" + artDirectory(mob) + mob.blueprintId() + ".animation.json");
    }

    // Preserve the concurrent legacy UV files; these two rigs have separate authored resources.
    private static String artDirectory(TemplateMob mob) {
        return mob.kind()==TemplateMob.Kind.CHILD||mob.kind()==TemplateMob.Kind.PAPER
            ? "blueprint/cod2_voxel/" : "blueprint/";
    }

    @Override public ResourceLocation getTextureResource(TemplateMob mob) {
        if(mob.kind()==TemplateMob.Kind.CHILD||mob.kind()==TemplateMob.Kind.PAPER)
            return new ResourceLocation("dynasty", "textures/entity/" + artDirectory(mob) + mob.blueprintId() + ".png");
        if (switch (mob.kind()) {
            case STONE_GUARD, BIXI, YECHA, LANTERN_BAT, BLIND_FISH, DROWNER,
                 BRONZE_SNAKE, CLOCKWORK_DOG, MINING_SPIDER, SCORPION,
                 CENTIPEDE, SERPENT, TOAD, PRIEST,
                 SPEAR, POWDER, TREE, CROSSBOW, SHIELD, SKULL, AXE_GUARD, SCOUT,
                 CORPSE, GHOST, PALANQUIN, FLAG, BEAST, SWORD -> true;
            default -> false;
        }) return new ResourceLocation("dynasty", "textures/entity/blueprint/" + mob.blueprintId() + ".png");
        // Continuous opaque native swatches preserve pixel grain without replacing legacy artwork.
        String atlas = switch (mob.blueprintId()) {
            case "juli_bixi_kuilei", "xueju_mangguyu", "jubi_shigandang", "zuwu_daoshou", "ludun_jiashi", "zhenwang_zhangqiguan", "pijia_panjiang_huwei", "yinbing_guizu" -> "royal_guard";
            case "juma_changqiangbing" -> "archer";
            case "bazu_digongzhu", "qingtong_shuangtoushekui", "xunshan_mujiaquan", "liannu_zhenzu", "kuijun_sishi" -> "rebel_soldier";
            case "tiesuo_chihou" -> "assassin";
            case "fuhun_baibu_tongzi" -> "imperial_soldier";
            case "bishui_xuanjiao_youzi", "shibian_lishi", "chimu_zhuha", "kumu_shujing", "mingsha_shixie" -> "nian_beast";
            case "tongbi_feitian_yecha", "baimu_mowu", "youdeng_guimianfu", "shanjing_shanxiao" -> "nian_beast";
            default -> "imperial_soldier";
        };
        return new ResourceLocation("dynasty", "textures/entity/" + atlas + ".png");
    }
}
