package com.sammy.malum.client.renderer.entity.cultist.cherub;

import com.mojang.blaze3d.vertex.PoseStack;
import com.sammy.malum.MalumMod;
import com.sammy.malum.client.model.mob.cherub.CherubModel;
import com.sammy.malum.client.renderer.entity.cultist.CultistEmpowermentLayer;
import com.sammy.malum.common.entity.mob.cultist.cherub.CherubCultist;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.client.renderer.entity.layers.ItemInHandLayer;
import net.minecraft.resources.ResourceLocation;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.api.distmarker.OnlyIn;
import org.jetbrains.annotations.NotNull;

@OnlyIn(Dist.CLIENT)
public class CherubRenderer extends MobRenderer<CherubCultist, CherubModel> {
    private static final ResourceLocation CHERUB_LOCATION = MalumMod.malumPath("textures/entity/cultist/cherub.png");

    public CherubRenderer(EntityRendererProvider.Context context) {
        super(context, new CherubModel(context.bakeLayer(CherubModel.LAYER)), 0.3F);
        this.addLayer(new ItemInHandLayer<>(this, context.getItemInHandRenderer()));
        this.addLayer(new CultistEmpowermentLayer<>(this, CultistEmpowermentLayer.SMALL));
    }

    @Override
    protected void scale(CherubCultist cherub, PoseStack poseStack, float partialTicks) {
        float scale = cherub.getCultistScaleMultiplier();
        poseStack.scale(scale, scale, scale);
    }

    @Override
    public @NotNull ResourceLocation getTextureLocation(@NotNull CherubCultist cherub) {
        return CHERUB_LOCATION;
    }
}