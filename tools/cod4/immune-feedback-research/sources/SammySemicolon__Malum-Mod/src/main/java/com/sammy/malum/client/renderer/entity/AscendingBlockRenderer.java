package com.sammy.malum.client.renderer.entity;

import com.mojang.blaze3d.vertex.*;
import com.sammy.malum.common.entity.*;
import net.minecraft.client.renderer.*;
import net.minecraft.client.renderer.block.*;
import net.minecraft.client.renderer.entity.*;
import net.minecraft.client.renderer.texture.*;
import net.minecraft.core.*;
import net.minecraft.resources.*;
import net.minecraft.util.*;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.state.*;

public class AscendingBlockRenderer extends EntityRenderer<AscendingBlock> {
    private final BlockRenderDispatcher dispatcher;

    public AscendingBlockRenderer(EntityRendererProvider.Context context) {
        super(context);
        this.shadowRadius = 0.5F;
        this.dispatcher = context.getBlockRenderDispatcher();
    }

    public void render(AscendingBlock entity, float entityYaw, float partialTicks, PoseStack poseStack, MultiBufferSource buffer, int packedLight) {
        BlockState blockstate = entity.getBlockState();
        if (blockstate.getRenderShape() == RenderShape.MODEL) {
            Level level = entity.level();
            if (blockstate != level.getBlockState(entity.blockPosition()) && blockstate.getRenderShape() != RenderShape.INVISIBLE) {
                poseStack.pushPose();
                BlockPos blockpos = BlockPos.containing(entity.getX(), entity.getBoundingBox().maxY, entity.getZ());
                poseStack.translate(-0.5, 0.0, -0.5);
                var model = this.dispatcher.getBlockModel(blockstate);
                for (var renderType : model.getRenderTypes(blockstate, RandomSource.create(blockstate.getSeed(entity.getStartPos())), net.neoforged.neoforge.client.model.data.ModelData.EMPTY))
                    this.dispatcher
                            .getModelRenderer()
                            .tesselateBlock(
                                    level,
                                    this.dispatcher.getBlockModel(blockstate),
                                    blockstate,
                                    blockpos,
                                    poseStack,
                                    buffer.getBuffer(net.neoforged.neoforge.client.RenderTypeHelper.getMovingBlockRenderType(renderType)),
                                    false,
                                    RandomSource.create(),
                                    blockstate.getSeed(entity.getStartPos()),
                                    OverlayTexture.NO_OVERLAY,
                                    net.neoforged.neoforge.client.model.data.ModelData.EMPTY,
                                    renderType
                            );
                poseStack.popPose();
                super.render(entity, entityYaw, partialTicks, poseStack, buffer, packedLight);
            }
        }
    }

    /**
     * Returns the location of an entity's texture.
     */
    public ResourceLocation getTextureLocation(AscendingBlock entity) {
        return TextureAtlas.LOCATION_BLOCKS;
    }
}