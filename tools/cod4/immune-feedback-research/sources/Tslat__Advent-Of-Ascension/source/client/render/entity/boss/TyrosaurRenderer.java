package net.tslat.aoa3.client.render.entity.boss;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.tslat.aoa3.advent.AdventOfAscension;
import net.tslat.aoa3.client.render.entity.AnimatedMobRenderer;
import net.tslat.aoa3.common.registration.entity.AoAMonsters;
import net.tslat.aoa3.content.entity.boss.tyrosaur.TyrosaurEntity;
import org.jetbrains.annotations.Nullable;
import software.bernie.geckolib.cache.object.BakedGeoModel;
import software.bernie.geckolib.model.DefaultedEntityGeoModel;

public class TyrosaurRenderer extends AnimatedMobRenderer<TyrosaurEntity> {
	public TyrosaurRenderer(EntityRendererProvider.Context renderManager) {
		super(renderManager, new DefaultedEntityGeoModel<>(AdventOfAscension.id("boss/tyrosaur/tyrosaur"), true), AoAMonsters.TYROSAUR.get().getWidth() / (AoAMonsters.TYROSAUR.get().getWidth() > 1 ? 2.5f : 3f));
	}

	@Override
	public void preRender(PoseStack poseStack, TyrosaurEntity animatable, BakedGeoModel model, @Nullable MultiBufferSource bufferSource, @Nullable VertexConsumer buffer, boolean isReRender, float partialTick, int packedLight, int packedOverlay, int colour) {
		super.preRender(poseStack, animatable, model, bufferSource, buffer, isReRender, partialTick, packedLight, packedOverlay, colour);

		float armour = animatable.getArmourPercent();

		model.getBone("head_plates").ifPresent(bone -> bone.setHidden(armour <= 0.75f));
		model.getBone("backplate_1").ifPresent(bone -> bone.setHidden(armour <= 0.5f));
		model.getBone("backplate_2").ifPresent(bone -> bone.setHidden(armour <= 0.25f));
		model.getBone("bone4").ifPresent(bone -> bone.setHidden(armour <= 0));
	}
}
