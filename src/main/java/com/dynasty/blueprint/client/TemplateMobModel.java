package com.dynasty.blueprint.client;

import com.dynasty.blueprint.TemplateMob;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.model.GeoModel;
import software.bernie.geckolib.core.animation.AnimationState;

/** The four prototypes share loading, but each owns an independently authored articulated rig. */
public final class TemplateMobModel extends GeoModel<TemplateMob> {
    @Override public void setCustomAnimations(TemplateMob mob, long instanceId, AnimationState<TemplateMob> state) {
        super.setCustomAnimations(mob, instanceId, state);
        TemplateSecondaryMotion.apply(this, mob, state.getPartialTick());
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
            case "zuwu_daoshou", "ludun_jiashi" -> "royal_guard";
            case "shanjing_shanxiao" -> "nian_beast";
            default -> "imperial_soldier";
        };
        return new ResourceLocation("dynasty", "textures/entity/" + atlas + ".png");
    }
}
