package com.sammy.malum.client.renderer.entity.cultist.cardinal;

import com.mojang.blaze3d.vertex.PoseStack;
import com.sammy.malum.MalumMod;
import com.sammy.malum.client.renderer.entity.cultist.CultistEmpowermentLayer;
import com.sammy.malum.client.model.mob.cardinal.CardinalModel;
import com.sammy.malum.common.entity.mob.cultist.cardinal.CardinalCultist;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.resources.ResourceLocation;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.api.distmarker.OnlyIn;
import org.jetbrains.annotations.NotNull;

@OnlyIn(Dist.CLIENT)
public class CardinalRenderer extends MobRenderer<CardinalCultist, CardinalModel> {
    private static final ResourceLocation CARDINAL_LOCATION = MalumMod.malumPath("textures/entity/cultist/cardinal.png");

    public CardinalRenderer(EntityRendererProvider.Context context) {
        super(context, new CardinalModel(context.bakeLayer(CardinalModel.LAYER)), 0.8F);
        this.addLayer(new CultistEmpowermentLayer<>(this, CultistEmpowermentLayer.LARGE));
    }

    @Override
    protected void scale(CardinalCultist cardinal, PoseStack poseStack, float partialTicks) {
        float scale = cardinal.getCultistScaleMultiplier();
        poseStack.scale(scale, scale, scale);
    }

    @Override
    public @NotNull ResourceLocation getTextureLocation(@NotNull CardinalCultist cardinal) {
        return CARDINAL_LOCATION;
    }
}