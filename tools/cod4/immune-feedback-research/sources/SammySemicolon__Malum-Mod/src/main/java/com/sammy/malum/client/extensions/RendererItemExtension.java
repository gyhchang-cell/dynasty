package com.sammy.malum.client.extensions;

import net.minecraft.client.Minecraft;
import net.minecraft.client.model.geom.EntityModelSet;
import net.minecraft.client.renderer.BlockEntityWithoutLevelRenderer;
import net.minecraft.client.renderer.blockentity.BlockEntityRenderDispatcher;
import net.neoforged.neoforge.client.extensions.common.IClientItemExtensions;
import org.jetbrains.annotations.NotNull;

import java.util.function.BiFunction;

public abstract class RendererItemExtension implements IClientItemExtensions {

	private BlockEntityWithoutLevelRenderer renderer;
	
	@Override
	public @NotNull BlockEntityWithoutLevelRenderer getCustomRenderer() {
		if (renderer == null) {
			var minecraft = Minecraft.getInstance();
			renderer = makeRenderer().apply(minecraft.getBlockEntityRenderDispatcher(), minecraft.getEntityModels());
		}
		return renderer;
	}

	public abstract BiFunction<BlockEntityRenderDispatcher, EntityModelSet, BlockEntityWithoutLevelRenderer> makeRenderer();
}
