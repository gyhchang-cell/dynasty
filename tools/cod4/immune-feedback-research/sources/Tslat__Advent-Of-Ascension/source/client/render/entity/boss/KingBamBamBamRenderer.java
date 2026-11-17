package net.tslat.aoa3.client.render.entity.boss;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.tslat.aoa3.advent.AdventOfAscension;
import net.tslat.aoa3.client.render.entity.AnimatedMobRenderer;
import net.tslat.aoa3.common.registration.entity.AoAMonsters;
import net.tslat.aoa3.content.entity.boss.king_bambambam.KingBamBamBamEntity;
import org.jetbrains.annotations.Nullable;
import software.bernie.geckolib.cache.object.BakedGeoModel;
import software.bernie.geckolib.model.DefaultedEntityGeoModel;
import software.bernie.geckolib.renderer.layer.AutoGlowingGeoLayer;

public class KingBamBamBamRenderer extends AnimatedMobRenderer<KingBamBamBamEntity> {
	public KingBamBamBamRenderer(EntityRendererProvider.Context renderManager) {
		super(renderManager, new DefaultedEntityGeoModel<>(AdventOfAscension.id("boss/king_bambambam/king_bambambam"), true), AoAMonsters.KING_BAMBAMBAM.get().getWidth() / (AoAMonsters.KING_BAMBAMBAM.get().getWidth() > 1 ? 2.5f : 3f));

		addRenderLayer(new AutoGlowingGeoLayer<>(this));
	}

	@Override
	public void preRender(PoseStack poseStack, KingBamBamBamEntity animatable, BakedGeoModel model, @Nullable MultiBufferSource bufferSource, @Nullable VertexConsumer buffer, boolean isReRender, float partialTick, int packedLight, int packedOverlay, int colour) {
		model.getBone("sphere").filter(bone -> bone.getScaleX() == 1).ifPresent(bone -> animatable.orbPos = bone.getWorldPosition());
	}
}
