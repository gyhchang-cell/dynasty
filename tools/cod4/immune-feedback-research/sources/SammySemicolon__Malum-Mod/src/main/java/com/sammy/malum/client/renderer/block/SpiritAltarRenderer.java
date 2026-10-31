package com.sammy.malum.client.renderer.block;

import com.mojang.blaze3d.vertex.PoseStack;
import com.sammy.malum.common.block.curiosities.sorcery.spirit_altar.SpiritAltarBlockEntity;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.blockentity.BlockEntityRenderer;
import net.minecraft.client.renderer.blockentity.BlockEntityRendererProvider;
import net.minecraft.world.phys.AABB;
import org.jetbrains.annotations.NotNull;
import team.lodestar.lodestone.modules.toolkit.inventory.display.ItemStackDisplayDataRenderer;

public class SpiritAltarRenderer implements BlockEntityRenderer<SpiritAltarBlockEntity> {
    public SpiritAltarRenderer(BlockEntityRendererProvider.Context context) {
    }

    @Override
    public void render(SpiritAltarBlockEntity blockEntityIn, float partialTicks, PoseStack poseStack, MultiBufferSource bufferIn, int combinedLightIn, int combinedOverlayIn) {
        var renderer = new ItemStackDisplayDataRenderer();
        renderer.render(blockEntityIn.inventory, poseStack, bufferIn, combinedLightIn, partialTicks);
        renderer.render(blockEntityIn.spiritInventory, poseStack, bufferIn, combinedLightIn, partialTicks);
//      FloatingItemRenderer.renderSpiritGlimmer(poseStack, shardItem.getSpiritHolder(), partialTicks);
    }

    @Override
    public @NotNull AABB getRenderBoundingBox(SpiritAltarBlockEntity altar) {
        var pos = altar.getBlockPos();
        return new AABB(pos.getX() - 1, pos.getY(), pos.getZ() - 1, pos.getX() + 2, pos.getY() + 2, pos.getZ() + 2);
    }
}
