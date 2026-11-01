package software.bernie.geckolib3.model;

import java.util.Collections;
import net.minecraft.class_1297;
import net.minecraft.class_1309;
import net.minecraft.class_243;
import net.minecraft.class_2960;
import net.minecraft.class_310;
import net.minecraft.class_3532;
import com.eliotlash.molang.MolangParser;
import software.bernie.geckolib3.core.IAnimatable;
import software.bernie.geckolib3.core.IAnimatableModel;
import software.bernie.geckolib3.core.builder.Animation;
import software.bernie.geckolib3.core.event.predicate.AnimationEvent;
import software.bernie.geckolib3.core.manager.AnimationData;
import software.bernie.geckolib3.core.processor.AnimationProcessor;
import software.bernie.geckolib3.core.processor.IBone;
import software.bernie.geckolib3.file.AnimationFile;
import software.bernie.geckolib3.geo.exception.GeckoLibException;
import software.bernie.geckolib3.geo.render.built.GeoBone;
import software.bernie.geckolib3.geo.render.built.GeoModel;
import software.bernie.geckolib3.model.provider.GeoModelProvider;
import software.bernie.geckolib3.model.provider.IAnimatableModelProvider;
import software.bernie.geckolib3.resource.GeckoLibCache;
import software.bernie.geckolib3.util.AnimationTicker;
import software.bernie.geckolib3.util.MolangUtils;

public abstract class AnimatedGeoModel<T extends IAnimatable> extends GeoModelProvider<T>
		implements IAnimatableModel<T>, IAnimatableModelProvider<T> {
	@SuppressWarnings("rawtypes")
	private final AnimationProcessor animationProcessor;
	private GeoModel currentModel;

	@SuppressWarnings("rawtypes")
	protected AnimatedGeoModel() {
		this.animationProcessor = new AnimationProcessor(this);
	}

	public void registerBone(GeoBone bone) {
		registerModelRenderer(bone);

		for (GeoBone childBone : bone.childBones) {
			registerBone(childBone);
		}
	}

	@SuppressWarnings({ "rawtypes", "unchecked" })
	@Override
	public void setLivingAnimations(T entity, Integer uniqueID, AnimationEvent customPredicate) {
		// Each animation has it's own collection of animations (called the
		// EntityAnimationManager), which allows for multiple independent animations
		AnimationData manager = entity.getFactory().getOrCreateAnimationData(uniqueID);

		if (manager.ticker == null) {
			manager.ticker = new AnimationTicker(manager);
		}

		if (!class_310.method_1551().method_1493() || manager.shouldPlayWhilePaused) {
			seekTime = manager.tick + class_310.method_1551().method_1488();
		}

		AnimationEvent<T> predicate;
		if (customPredicate == null) {
			predicate = new AnimationEvent<T>(entity, 0, 0, (float) (manager.tick - lastGameTickTime), false,
					Collections.emptyList());
		} else {
			predicate = customPredicate;
		}

		predicate.animationTick = seekTime;

		animationProcessor.preAnimationSetup(predicate.getAnimatable(), seekTime);
		if (!this.animationProcessor.getModelRendererList().isEmpty()) {
			animationProcessor.tickAnimation(entity, uniqueID, seekTime, predicate, GeckoLibCache.getInstance().parser,
					shouldCrashOnMissing);
		}
	}

	@SuppressWarnings("rawtypes")
	@Override
	public AnimationProcessor getAnimationProcessor() {
		return this.animationProcessor;
	}

	public void registerModelRenderer(IBone modelRenderer) {
		animationProcessor.registerModelRenderer(modelRenderer);
	}

	@SuppressWarnings("unchecked")
	@Override
	public Animation getAnimation(String name, IAnimatable animatable) {
		AnimationFile animation = GeckoLibCache.getInstance().getAnimations()
				.get(this.getAnimationResource((T) animatable));
		if (animation == null) {
			throw new GeckoLibException(this.getAnimationResource((T) animatable),
					"Could not find animation file. Please double check name.");
		}
		return animation.getAnimation(name);
	}

	@Override
	public GeoModel getModel(class_2960 location) {
		GeoModel model = super.getModel(location);
		if (model == null) {
			throw new GeckoLibException(location,
					"Could not find model. If you are getting this with a built mod, please just restart your game.");
		}
		if (model != currentModel) {
			this.animationProcessor.clearModelRendererList();
			for (GeoBone bone : model.topLevelBones) {
				registerBone(bone);
			}
			this.currentModel = model;
		}
		return model;
	}

	@Override
	public void setMolangQueries(IAnimatable animatable, double currentTick) {
		MolangParser parser = GeckoLibCache.getInstance().parser;
		class_310 minecraftInstance = class_310.method_1551();

		parser.setValue("query.actor_count", minecraftInstance.field_1687.method_18120());
		parser.setValue("query.time_of_day", MolangUtils.normalizeTime(minecraftInstance.field_1687.method_8532()));
		parser.setValue("query.moon_phase", minecraftInstance.field_1687.method_30273());

		if (animatable instanceof class_1297) {
			parser.setValue("query.distance_from_camera",
					minecraftInstance.field_1773.method_19418().method_19326().method_1022(((class_1297) animatable).method_19538()));
			parser.setValue("query.is_on_ground", MolangUtils.booleanToFloat(((class_1297) animatable).method_24828()));
			parser.setValue("query.is_in_water", MolangUtils.booleanToFloat(((class_1297) animatable).method_5799()));
			// Should probably check specifically whether it's in rain?
			parser.setValue("query.is_in_water_or_rain", MolangUtils.booleanToFloat(((class_1297) animatable).method_5637()));

			if (animatable instanceof class_1309) {
				class_1309 livingEntity = (class_1309) animatable;
				parser.setValue("query.health", livingEntity.method_6032());
				parser.setValue("query.max_health", livingEntity.method_6063());

				parser.setValue("query.is_on_fire", MolangUtils.booleanToFloat(livingEntity.method_5809()));
				// Doesn't work for some reason?
				parser.setValue("query.on_fire_time", livingEntity.method_20802());

				class_243 velocity = livingEntity.method_18798();
				// Must be always positive to prevent NaNs
				float groundSpeed = class_3532.method_15355((float) (+velocity.field_1352 * +velocity.field_1350));
				parser.setValue("query.ground_speed", groundSpeed);

				float yawSpeed = livingEntity.method_5705((float) currentTick)
						- livingEntity.method_5705((float) (currentTick - 0.1));
				parser.setValue("query.yaw_speed", yawSpeed);
			}
		}
	}
}