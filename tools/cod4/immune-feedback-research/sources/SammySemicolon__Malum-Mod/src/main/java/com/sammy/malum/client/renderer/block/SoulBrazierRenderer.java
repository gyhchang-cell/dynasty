package com.sammy.malum.client.renderer.block;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import com.sammy.malum.client.renderer.entity.FloatingItemRenderer;
import com.sammy.malum.common.block.curiosities.sorcery.soul_brazier.SoulBrazierBlockEntity;
import com.sammy.malum.common.item.spirit.SpiritShardItem;
import com.sammy.malum.core.systems.spirit.SpiritLike;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.blockentity.BlockEntityRenderer;
import net.minecraft.client.renderer.blockentity.BlockEntityRendererProvider;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import org.joml.Vector3f;
import team.lodestar.lodestone.modules.rendering.LodestoneRenderingSystem;
import team.lodestar.lodestone.registry.client.LodestoneRenderTypes;
import team.lodestar.lodestone.systems.rendering.builder.VFXBuilders;
import team.lodestar.lodestone.systems.rendering.rendeertype.RenderTypeToken;

import java.awt.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.*;

import static net.minecraft.client.renderer.texture.OverlayTexture.NO_OVERLAY;

public class SoulBrazierRenderer implements BlockEntityRenderer<SoulBrazierBlockEntity> {
    public SoulBrazierRenderer(BlockEntityRendererProvider.Context context) {
    }

    @Override
    public void render(SoulBrazierBlockEntity blockEntityIn, float partialTicks, PoseStack poseStack, MultiBufferSource bufferIn, int combinedLightIn, int combinedOverlayIn) {
        var level = Minecraft.getInstance().level;
        var itemRenderer = Minecraft.getInstance().getItemRenderer();
        var inventory = blockEntityIn.inventory;
        var spiritInventory = blockEntityIn.spiritInventory;
        int spiritsRendered = 0;
        if (!spiritInventory.isEmpty()) {
            for (int i = 0; i < spiritInventory.getSlotCount(); i++) {
                ItemStack item = spiritInventory.getStackInSlot(i);
                if (item.getItem() instanceof SpiritShardItem shardItem) {
                    poseStack.pushPose();
                    Vector3f offset = blockEntityIn.getSpiritOffset(spiritsRendered++, partialTicks).toVector3f();
                    poseStack.translate(offset.x(), offset.y(), offset.z());
                    FloatingItemRenderer.renderSpiritGlimmer(poseStack, shardItem.getSpiritHolder(), partialTicks);
                    poseStack.mulPose(Axis.YP.rotationDegrees(((level.getGameTime() % 360) + partialTicks) * 3));
                    poseStack.scale(0.5f, 0.5f, 0.5f);
                    itemRenderer.renderStatic(item, ItemDisplayContext.FIXED, combinedLightIn, NO_OVERLAY, poseStack, bufferIn, level, 0);
                    poseStack.popPose();
                }
            }
        }
        int extrasRendered = 0;
        if (!inventory.isEmpty()) {
            for (int i = 0; i < inventory.getSlotCount()-1; i++) {
                ItemStack item = inventory.getStackInSlot(i+1);
                poseStack.pushPose();
                Vector3f offset = blockEntityIn.getExtrasOffset(extrasRendered++, partialTicks).toVector3f();
                poseStack.translate(offset.x(), offset.y(), offset.z());
                poseStack.mulPose(Axis.YN.rotationDegrees(((level.getGameTime() % 360) + partialTicks) * 3));
                poseStack.scale(0.5f, 0.5f, 0.5f);
                itemRenderer.renderStatic(item, ItemDisplayContext.FIXED, combinedLightIn, NO_OVERLAY, poseStack, bufferIn, level, 0);
                poseStack.popPose();
            }
        }
        ItemStack stack = inventory.getStackInSlot(0);
        if (!stack.isEmpty()) {
            poseStack.pushPose();
            Vec3 offset = SoulBrazierBlockEntity.BRAZIER_ITEM_OFFSET;
            poseStack.translate(offset.x, offset.y, offset.z);
            poseStack.mulPose(Axis.YP.rotationDegrees((((level.getGameTime() + partialTicks) * 3) % 360)));
            poseStack.scale(0.55f, 0.55f, 0.55f);
            itemRenderer.renderStatic(stack, ItemDisplayContext.FIXED, combinedLightIn, NO_OVERLAY, poseStack, bufferIn, level, 0);
            poseStack.popPose();
        }

        if (blockEntityIn.isActive()) {
            var recipe = blockEntityIn.recipe;
            var spirits = recipe.spirits;
            var geas = recipe.result;
            var texture = geas.getIcon();
            var additive = LodestoneRenderTypes.ADDITIVE_DISTORTED_TEXTURE.apply(RenderTypeToken.createToken(texture));
            var transparent = LodestoneRenderTypes.TRANSPARENT_DISTORTED_TEXTURE.apply(RenderTypeToken.createToken(texture));
            var offset = SoulBrazierBlockEntity.BRAZIER_GEAS_ICON_OFFSET;
            float progress = blockEntityIn.progress + partialTicks;
            float alpha = 0.9f * Math.clamp(progress / 5f, 0, 1);
            float scale = 0.4f * Math.min(1 + progress / 10f, 2);
            var worldVFXBuilder = VFXBuilders.createWorld();
            var cycle = new AtomicInteger();
            Function<Function<SpiritLike, Color>, Color> colorSupplier = (b) -> b.apply(spirits.get(cycle.getAndIncrement() % spirits.size())); //TODO: this kinda smells...
            var mainColor = colorSupplier.apply(SpiritLike::getPrimaryColor);

            poseStack.pushPose();
            poseStack.translate(offset.x, offset.y, offset.z);
            poseStack.mulPose(Minecraft.getInstance().getEntityRenderDispatcher().cameraOrientation());

            int interval = 160;
            float gameTime = level.getGameTime() + partialTicks;
            float distance = scale * 0.08f;

            worldVFXBuilder
                    .setColor(colorSupplier.apply(SpiritLike::getPrimaryColor)).multiplyColor(0.32f)
                    .setRenderType(transparent)
                    .setAlpha(alpha*0.4f)
                    .renderQuad(poseStack, scale);
            for (int i = 0; i < 4; i++) {
                double angle = i * 1.57f;
                angle += ((gameTime % interval) / interval) * 6.28f;
                double xOffset = (distance * Math.cos(angle));
                double yOffset = (distance * Math.sin(angle));
                poseStack.translate(xOffset, yOffset, -0.02*i);
                worldVFXBuilder
                        .setColor(colorSupplier.apply(SpiritLike::getPrimaryColor)).multiplyColor(0.32f)
                        .renderQuad(poseStack, scale);
                poseStack.translate(-xOffset, -yOffset, 0.02*i);
            }

            worldVFXBuilder
                    .replaceBufferSource(LodestoneRenderingSystem.LATE_DEFERRED_RENDER)
                    .setColor(mainColor)
                    .setRenderType(additive)
                    .setAlpha(alpha*0.8f)
                    .renderQuad(poseStack, scale);
            for (int i = 0; i < 4; i++) {
                double angle = i * 1.57f;
                angle += ((gameTime % interval) / interval) * 6.28f;
                double xOffset = (distance * Math.cos(angle));
                double yOffset = (distance * Math.sin(angle));
                poseStack.translate(xOffset, yOffset, 0);
                worldVFXBuilder
                        .setAlpha(alpha*0.4f)
                        .setColor(colorSupplier.apply(SpiritLike::getSecondaryColor))
                        .renderQuad(poseStack, scale);
                poseStack.translate(-xOffset, -yOffset, 0);
            }
            poseStack.popPose();
        }
    }

    @Override
    public AABB getRenderBoundingBox(SoulBrazierBlockEntity altar) {
        var pos = altar.getBlockPos();
        return new AABB(pos.getX() - 1, pos.getY(), pos.getZ() - 1, pos.getX() + 2, pos.getY() + 2, pos.getZ() + 2);
    }
}
