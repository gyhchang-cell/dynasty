package com.sammy.malum.client.renderer.entity.cultist.altar;

import com.mojang.blaze3d.vertex.PoseStack;
import com.sammy.malum.MalumMod;
import com.sammy.malum.client.model.mob.altar.AltarModel;
import com.sammy.malum.common.entity.mob.cultist.altar.AltarCultist;
import earth.terrarium.athena.api.client.utils.AthenaUtils;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.resources.ResourceLocation;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.api.distmarker.OnlyIn;
import org.jetbrains.annotations.NotNull;

@OnlyIn(Dist.CLIENT)
public class AltarRenderer extends MobRenderer<AltarCultist, AltarModel> {
    private static final ResourceLocation ALTAR_LOCATION = MalumMod.malumPath("textures/entity/cultist/altar.png");

    public AltarRenderer(EntityRendererProvider.Context context) {
        super(context, new AltarModel(context.bakeLayer(AltarModel.LAYER)), 0.4F);
    }

    @Override
    protected void scale(AltarCultist altar, PoseStack poseStack, float partialTicks) {
        float scale = altar.getCultistScaleMultiplier();
        poseStack.scale(scale, scale, scale);
    }

    @Override
    public @NotNull ResourceLocation getTextureLocation(@NotNull AltarCultist altar) {
        return ALTAR_LOCATION;
    }
}