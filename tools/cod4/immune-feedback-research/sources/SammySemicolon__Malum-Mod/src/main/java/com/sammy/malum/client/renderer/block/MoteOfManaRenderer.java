//package com.sammy.malum.client.renderer.block;
//
//import com.mojang.blaze3d.vertex.*;
//import com.sammy.malum.MalumMod;
//import com.sammy.malum.client.*;
//import com.sammy.malum.common.block.curiosities.decor.mana_mote.*;
//import com.sammy.malum.core.systems.registry.*;
//import com.sammy.malum.core.systems.spirit.*;
//import com.sammy.malum.core.systems.spirit.type.*;
//import net.minecraft.client.renderer.*;
//import net.minecraft.client.renderer.blockentity.*;
//import net.minecraft.core.*;
//import team.lodestar.lodestone.registry.client.*;
//import team.lodestar.lodestone.systems.rendering.builder.data.CubeVertexData;

//import team.lodestar.lodestone.systems.rendering.rendeertype.*;
//
//import java.util.*;
//
//
//public class MoteOfManaRenderer implements BlockEntityRenderer<ManaMoteBlockEntity> {
//
//
//    public static final RenderTypeToken MOTE_OF_MANA = RenderTypeToken.createToken(MalumMod.malumPath("textures/block/spirit_mote.png"));
//
//    public MoteOfManaRenderer(BlockEntityRendererProvider.Context context) {
//    }
//
//    @Override
//    public void render(ManaMoteBlockEntity blockEntityIn, float partialTicks, PoseStack poseStack, MultiBufferSource bufferIn, int combinedLightIn, int combinedOverlayIn) {
//        var state = blockEntityIn.getBlockState();
//        SpiritHolder<SpiritArcanaType> spirit = SpiritTypeProperty.getSpiritType(state);
//
//        var additive = LodestoneRenderTypes.ADDITIVE_TEXTURE.apply(MOTE_OF_MANA);
//        var transparent = LodestoneRenderTypes.TRANSPARENT_TEXTURE.apply(MOTE_OF_MANA);
//        var builder = SpiritBasedWorldVFXBuilder.create(spirit);
//
//        var primaryColor = spirit.getPrimaryColor();
//        var secondaryColor = spirit.getSecondaryColor();
//
//        float wobble = 1f;
//        var directions = new ArrayList<Direction>();
//        var invertedDirections = new ArrayList<Direction>();
//        for (Direction direction : Direction.values()) {
//            if (!ManaMoteBlock.isOccluded(state, direction)) {
//                var usedDirection = direction;
//                if (usedDirection.getAxis().isVertical()) {
//                    usedDirection = usedDirection.getOpposite();
//                }
//                directions.add(usedDirection.getOpposite());
//                invertedDirections.add(usedDirection);
//            }
//            else {
//                wobble -= 0.2f;
//            }
//        }
//        var cube = CubeVertexData.makeCubePositions(1f).applyWobble(0, 0.5f, wobble * 0.02f);
//        var inverse = CubeVertexData.makeCubePositions(-1f).applyWobble(0, 0.5f, wobble * 0.02f);
//
//        poseStack.pushPose();
//        poseStack.translate(0.5f, 0.5f, 0.5f);
//
//        builder.setRenderType(transparent).setColor(primaryColor, 0.9f)
//                .renderCubeSides(poseStack, cube, directions);
//        builder.setRenderType(additive).setAlpha(0.25f)
//                .renderCubeSides(poseStack, cube.scale(1.05f), directions);
//        builder.setColor(secondaryColor, 0.4f)
//                .renderCubeSides(poseStack, inverse.scale(0.95f), invertedDirections);
//
//        poseStack.popPose();
//    }
//}