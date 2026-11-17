package com.sammy.malum.client.extensions;

import com.sammy.malum.client.renderer.item.*;
import net.minecraft.client.model.geom.EntityModelSet;
import net.minecraft.client.renderer.BlockEntityWithoutLevelRenderer;
import net.minecraft.client.renderer.blockentity.BlockEntityRenderDispatcher;

import java.util.function.BiFunction;

public class SpiritJarItemExtension extends RendererItemExtension {

	@Override
	public BiFunction<BlockEntityRenderDispatcher, EntityModelSet, BlockEntityWithoutLevelRenderer> makeRenderer() {
		return SpiritJarItemRenderer::new;
	}
}
