package net.tslat.aoa3.client.render.entity.boss;

import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.tslat.aoa3.advent.AdventOfAscension;
import net.tslat.aoa3.client.render.entity.AnimatedMobRenderer;
import net.tslat.aoa3.common.registration.entity.AoAMonsters;
import net.tslat.aoa3.content.entity.boss.tyrosaur.WoundedTyrosaurEntity;
import software.bernie.geckolib.model.DefaultedEntityGeoModel;

public class WoundedTyrosaurRenderer extends AnimatedMobRenderer<WoundedTyrosaurEntity> {
	public WoundedTyrosaurRenderer(EntityRendererProvider.Context renderManager) {
		super(renderManager, new DefaultedEntityGeoModel<>(AdventOfAscension.id("boss/tyrosaur/wounded_tyrosaur"), true), AoAMonsters.WOUNDED_TYROSAUR.get().getWidth() / (AoAMonsters.WOUNDED_TYROSAUR.get().getWidth() > 1 ? 2.5f : 3f));
	}

	@Override
	public float getMotionAnimThreshold(WoundedTyrosaurEntity animatable) {
		return super.getMotionAnimThreshold(animatable) * 0.9f;
	}
}
