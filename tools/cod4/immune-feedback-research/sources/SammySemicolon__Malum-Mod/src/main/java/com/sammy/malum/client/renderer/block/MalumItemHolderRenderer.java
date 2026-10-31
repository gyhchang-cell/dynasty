package com.sammy.malum.client.renderer.block;

import com.mojang.blaze3d.vertex.PoseStack;
import com.sammy.malum.common.block.storage.MalumItemHolderBlockEntity;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.blockentity.BlockEntityRenderer;
import net.minecraft.client.renderer.blockentity.BlockEntityRendererProvider;
import net.minecraft.world.phys.*;
import team.lodestar.lodestone.modules.toolkit.inventory.display.ItemStackDisplayDataRenderer;


@SuppressWarnings("NullableProblems")
public class MalumItemHolderRenderer implements BlockEntityRenderer<MalumItemHolderBlockEntity> {
    public MalumItemHolderRenderer(BlockEntityRendererProvider.Context context) {
    }

    @Override
    public void render(MalumItemHolderBlockEntity blockEntityIn, float partialTicks, PoseStack poseStack, MultiBufferSource bufferIn, int combinedLightIn, int combinedOverlayIn) {
        var renderer = new ItemStackDisplayDataRenderer();
        renderer.render(blockEntityIn.inventory, poseStack, bufferIn, combinedLightIn, partialTicks);
    }

    @Override
    public AABB getRenderBoundingBox(MalumItemHolderBlockEntity blockEntity) {
        var pos = blockEntity.getBlockPos();
        return new AABB(pos.getX() - 1, pos.getY() - 1, pos.getZ() - 1, pos.getX() + 2, pos.getY() + 2, pos.getZ() + 2);
    }
}