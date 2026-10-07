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
        return new ResourceLocation("dynasty", "geo/blueprint/" + mob.blueprintId() + ".geo.json");
    }

    @Override public ResourceLocation getAnimationResource(TemplateMob mob) {
        return new ResourceLocation("dynasty", "animations/blueprint/" + mob.blueprintId() + ".animation.json");
    }

    @Override public ResourceLocation getTextureResource(TemplateMob mob) {
        // Continuous opaque native swatches preserve pixel grain without replacing legacy artwork.
        String atlas = switch (mob.blueprintId()) {
            case "xueju_mangguyu", "jubi_shigandang", "zuwu_daoshou", "ludun_jiashi", "zhenwang_zhangqiguan", "pijia_panjiang_huwei", "yinbing_guizu" -> "royal_guard";
            case "juma_changqiangbing" -> "archer";
            case "bazu_digongzhu", "qingtong_shuangtoushekui", "xunshan_mujiaquan", "liannu_zhenzu", "kuijun_sishi" -> "rebel_soldier";
            case "tiesuo_chihou" -> "assassin";
            case "fuhun_baibu_tongzi" -> "imperial_soldier";
            case "bishui_xuanjiao_youzi", "shibian_lishi", "chimu_zhuha", "kumu_shujing", "mingsha_shixie" -> "nian_beast";
            case "youdeng_guimianfu", "shanjing_shanxiao" -> "nian_beast";
            default -> "imperial_soldier";
        };
        return new ResourceLocation("dynasty", "textures/entity/" + atlas + ".png");
    }
}
