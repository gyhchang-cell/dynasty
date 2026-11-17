package com.sammy.malum.client.renderer.entity.cultist.evangelist;

import com.mojang.blaze3d.vertex.PoseStack;
import com.sammy.malum.MalumMod;
import com.sammy.malum.client.renderer.entity.cultist.CultistEmpowermentLayer;
import com.sammy.malum.client.model.mob.evangelist.EvangelistModel;
import com.sammy.malum.common.entity.mob.cultist.evangelist.EvangelistCultist;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.resources.ResourceLocation;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.api.distmarker.OnlyIn;
import org.jetbrains.annotations.NotNull;

@OnlyIn(Dist.CLIENT)
public class EvangelistRenderer extends MobRenderer<EvangelistCultist, EvangelistModel> {
    private static final ResourceLocation EVANGELIST_LOCATION = MalumMod.malumPath("textures/entity/cultist/evangelist.png");

    public EvangelistRenderer(EntityRendererProvider.Context context) {
        super(context, new EvangelistModel(context.bakeLayer(EvangelistModel.LAYER)), 0.4F);
        this.addLayer(new EvangelistItemInHandLayer(this, context.getItemInHandRenderer()));
        this.addLayer(new CultistEmpowermentLayer<>(this, CultistEmpowermentLayer.MEDIUM));
    }

    @Override
    protected void scale(EvangelistCultist evangelist, PoseStack poseStack, float partialTicks) {
        float scale = evangelist.getCultistScaleMultiplier();
        poseStack.scale(scale, scale, scale);
    }

    @Override
    public @NotNull ResourceLocation getTextureLocation(@NotNull EvangelistCultist evangelist) {
        return EVANGELIST_LOCATION;
    }
}