/*
 * Copyright (c) MoriyaShiine. All Rights Reserved.
 */
package moriyashiine.anthropophagy.client.render.entity;

import moriyashiine.anthropophagy.client.render.entity.model.PigluttonEntityModel;
import moriyashiine.anthropophagy.common.Anthropophagy;
import moriyashiine.anthropophagy.common.entity.PigluttonEntity;
import net.fabricmc.api.EnvType;
import net.fabricmc.api.Environment;
import net.minecraft.client.render.entity.EntityRendererFactory;
import net.minecraft.client.render.entity.MobEntityRenderer;
import net.minecraft.client.util.math.MatrixStack;
import net.minecraft.util.Identifier;

@Environment(EnvType.CLIENT)
public class PigluttonEntityRenderer extends MobEntityRenderer<PigluttonEntity, PigluttonEntityModel<PigluttonEntity>> {
	private static final Identifier TEXTURE = Anthropophagy.id("textures/entity/living/piglutton.png");

	public PigluttonEntityRenderer(EntityRendererFactory.Context context) {
		super(context, new PigluttonEntityModel<>(context.getPart(PigluttonEntityModel.MODEL_LAYER)), 1.1F);
	}

	@Override
	public Identifier getTexture(PigluttonEntity entity) {
		return TEXTURE;
	}

	@Override
	protected void scale(PigluttonEntity entity, MatrixStack matrices, float amount) {
		matrices.scale(2, 1.5F, 2);
	}
}
