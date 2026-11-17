package com.sammy.malum.visual_effects;

import com.sammy.malum.client.*;
import com.sammy.malum.common.entity.scythe.*;
import com.sammy.malum.common.item.spirit.*;
import com.sammy.malum.core.systems.spirit.SpiritArcanaType;
import com.sammy.malum.core.systems.spirit.SpiritLike;
import com.sammy.malum.registry.common.*;
import com.sammy.malum.visual_effects.networked.MalumNetworkedParticleEffectColorData;
import net.minecraft.world.item.*;
import net.minecraft.world.level.*;
import net.minecraft.world.phys.*;
import team.lodestar.lodestone.modules.core.easing.Easing;
import team.lodestar.lodestone.modules.rendering.particle.standard.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.builder.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.data.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.data.color.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.data.spin.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.render_types.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.world.behaviors.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.world.options.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.world.type.*;

import java.util.function.*;

public class WeaponParticleEffects {

    public static final PointyDirectionalParticleBehavior MAELSTROM_DIRECTION = PointyDirectionalParticleBehavior.pointyDirectional(new Vec3(0, 0, 0));

    public static void spawnMaelstromParticles(AbstractScytheProjectileEntity entity) {
        var level = entity.level();
        if (level.getGameTime() % 2L == 0) {
            var random = level.getRandom();
            var stack = entity.getItem();
            var spirit = stack.getItem() instanceof ISpiritAffiliatedItem spiritItem ? spiritItem.getDefiningSpiritType(stack) : null;
            var slash = WeaponParticleEffects.spawnSlashParticle(level, entity.position(), MalumParticles.ROUNDABOUT_SLASH, spirit);
            float spinOffset = Easing.SINE_IN_OUT.asWeighedRandom(random, -0.8f, 0.8f);
            int age = Easing.SINE_IN_OUT.asWeighedRandom(random, 8, 18);
            slash.getBuilder()
                    .setBehavior(MAELSTROM_DIRECTION)
                    .setSpinData(SpinParticleData.create(0).setSpinOffset(spinOffset).build())
                    .setScaleData(GenericParticleData.create(Easing.SINE_IN_OUT.asWeighedRandom(random, 1.5f, 3f)).build())
                    .setTransparencyData(GenericParticleData.create(0.9f, 0.6f).build())
                    .addTickActor(p -> p.setParticlePosition(entity.position()))
                    .setLifetime(age);
            slash.spawnParticles();
            slash.getBuilder()
                    .setTransparencyData(GenericParticleData.create(0.6f, 0.3f).build())
                    .setLifeDelay(6);
            slash.spawnParticles();
            slash.getBuilder()
                    .setTransparencyData(GenericParticleData.create(0.3f, 0f).build())
                    .setLifeDelay(12);
            slash.spawnParticles();
        }
    }


    public static ParticleEffectSpawner spawnSlashParticle(Level level, Vec3 pos, Supplier<LodestoneWorldParticleType> particleType, MalumNetworkedParticleEffectColorData color) {
        if (color == null) {
            return spawnSlashParticle(level, pos, particleType);
        }
        if (color.isSpiritBased()) {
            return spawnSlashParticle(level, pos, particleType, color.getSpirit());
        }
        return spawnSlashParticle(level, pos, particleType, color.getColor());
    }

    public static ParticleEffectSpawner spawnSlashParticle(Level level, Vec3 pos, Supplier<LodestoneWorldParticleType> particleType, SpiritLike spirit) {
        if (spirit == null) {
            return spawnSlashParticle(level, pos, particleType);
        }
        return spawnSlashParticle(level, pos, SpiritBasedParticleBuilder.createSpirit(particleType.get()).setSpirit(spirit));
    }

    public static ParticleEffectSpawner spawnSlashParticle(Level level, Vec3 pos, Supplier<LodestoneWorldParticleType> particleType, ColorParticleData colorData) {
        return spawnSlashParticle(level, pos, WorldParticleBuilder.create(particleType.get()).setColorData(colorData));
    }

    public static ParticleEffectSpawner spawnSlashParticle(Level level, Vec3 pos, Supplier<LodestoneWorldParticleType> particleType) {
        return spawnSlashParticle(level, pos, WorldParticleBuilder.create(particleType).setRenderType(LodestoneWorldParticleRenderType.TRANSPARENT).setColorData(ColorParticleData.createGrayParticleColor(level.random)));
    }

    public static ParticleEffectSpawner spawnSlashParticle(Level level, Vec3 pos, WorldParticleBuilder builder) {
        var rand = level.getRandom();
        final WorldParticleBuilder worldParticleBuilder = builder
                .setScaleData(GenericParticleData.create(Easing.SINE_IN_OUT.asWeighedRandom(rand, 1.5f, 2f)).build())
                .setTransparencyData(GenericParticleData.create(1f, 0.9f).build())
                .enableForcedSpawn()
                .setLifetime(5)
                .enableNoClip();
        return new ParticleEffectSpawner(level, pos, worldParticleBuilder);
    }

    public static ParticleEffectSpawner spawnSlamParticle(Level level, Vec3 pos, Supplier<LodestoneWorldParticleType> particleType, MalumNetworkedParticleEffectColorData color) {
        if (color == null) {
            return spawnSlamParticle(level, pos, particleType);
        }
        if (color.isSpiritBased()) {
            return spawnSlamParticle(level, pos, particleType, color.getSpirit());
        }
        return spawnSlamParticle(level, pos, particleType, color.getColor());
    }
    public static ParticleEffectSpawner spawnSlamParticle(Level level, Vec3 pos, Supplier<LodestoneWorldParticleType> particleType, SpiritArcanaType spiritType) {
        if (spiritType == null) {
            return spawnSlamParticle(level, pos, particleType);
        }
        return spawnSlamParticle(level, pos, particleType, o -> SpiritBasedParticleBuilder.createSpirit(o).setSpirit(spiritType));
    }

    public static ParticleEffectSpawner spawnSlamParticle(Level level, Vec3 pos, Supplier<LodestoneWorldParticleType> particleType) {
        return spawnSlamParticle(level, pos, particleType, o -> WorldParticleBuilder.create(o).setRenderType(LodestoneWorldParticleRenderType.TRANSPARENT).setColorData(ColorParticleData.createGrayParticleColor(level.random)));
    }

    public static ParticleEffectSpawner spawnSlamParticle(Level level, Vec3 pos, Supplier<LodestoneWorldParticleType> particleType, ColorParticleData colorData) {
        return spawnSlamParticle(level, pos, particleType, o -> WorldParticleBuilder.create(o).setColorData(colorData));
    }

    public static ParticleEffectSpawner spawnSlamParticle(Level level, Vec3 pos, Supplier<LodestoneWorldParticleType> particleType, Function<WorldParticleOptions, WorldParticleBuilder> builderSupplier) {
        var builder = builderSupplier.apply(new WorldParticleOptions(particleType));
        return spawnSlamParticle(level, pos, builder);
    }

    public static ParticleEffectSpawner spawnSlamParticle(Level level, Vec3 pos, WorldParticleBuilder builder) {
        var rand = level.getRandom();
        final WorldParticleBuilder worldParticleBuilder = builder
                .setScaleData(GenericParticleData.create(Easing.SINE_IN_OUT.asWeighedRandom(rand, 1.5f, 2f)).build())
                .setTransparencyData(GenericParticleData.create(1f, 0.9f).build())
                .enableForcedSpawn()
                .setLifetime(5)
                .enableNoClip();
        return new ParticleEffectSpawner(level, pos, worldParticleBuilder);
    }
}