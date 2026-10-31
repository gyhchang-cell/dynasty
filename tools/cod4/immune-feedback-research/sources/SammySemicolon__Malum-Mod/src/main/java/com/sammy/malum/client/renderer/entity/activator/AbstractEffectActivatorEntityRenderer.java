package com.sammy.malum.client.renderer.entity.activator;

import com.mojang.blaze3d.vertex.*;
import com.sammy.malum.client.*;
import com.sammy.malum.core.systems.spirit.SpiritArcanaType;
import com.sammy.malum.registry.client.*;
import net.minecraft.client.renderer.*;
import net.minecraft.client.renderer.entity.*;
import net.minecraft.client.renderer.texture.*;
import net.minecraft.resources.*;
import net.minecraft.world.entity.*;
import team.lodestar.lodestone.registry.client.*;
import team.lodestar.lodestone.systems.rendering.*;
import team.lodestar.lodestone.systems.rendering.builder.VFXBuilders;
import team.lodestar.lodestone.systems.rendering.trail.*;

public abstract class AbstractEffectActivatorEntityRenderer<T extends Entity> extends EntityRenderer<T> {

    public AbstractEffectActivatorEntityRenderer(EntityRendererProvider.Context context) {
        super(context);
        this.shadowRadius = 0;
        this.shadowStrength = 0;
    }


    @Override
    public void render(T entity, float entityYaw, float partialTicks, PoseStack poseStack, MultiBufferSource bufferIn, int packedLightIn) {
        var renderType = LodestoneRenderTypes.ADDITIVE_ROUNDED_TEXTURE_TRIANGLE.apply(MalumRenderTypeTokens.CONCENTRATED_TRAIL);
        var builder = VFXBuilders.createWorld().setRenderType(renderType);
        var primaryColor = getSpiritType(entity).getPrimaryColor();
        var secondaryColor = getSpiritType(entity).getSecondaryColor();
        RenderUtils.renderEntityTrail(poseStack, builder, getTrail(entity), entity, primaryColor, secondaryColor, getScale(entity, false), getAlpha(entity, false), partialTicks);
        RenderUtils.renderEntityTrail(poseStack, builder, getLongTrail(entity), entity, primaryColor, secondaryColor, getScale(entity, true), getAlpha(entity, true), partialTicks);
        super.render(entity, entityYaw, partialTicks, poseStack, bufferIn, packedLightIn);
    }

    public abstract SpiritArcanaType getSpiritType(T entity);

    public abstract float getScale(T entity, boolean longTrail);

    public abstract float getAlpha(T entity, boolean longTrail);

    public abstract TrailPointBuilder getTrail(T entity);

    public abstract TrailPointBuilder getLongTrail(T entity);

    @Override
    public ResourceLocation getTextureLocation(T entity) {
        return TextureAtlas.LOCATION_BLOCKS;
    }
}