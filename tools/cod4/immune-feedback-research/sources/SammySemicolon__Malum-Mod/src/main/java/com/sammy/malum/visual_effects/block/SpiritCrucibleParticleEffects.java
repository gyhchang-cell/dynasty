package com.sammy.malum.visual_effects.block;

import com.sammy.malum.common.block.curiosities.artifice.spirit_crucible.*;
import com.sammy.malum.common.item.augment.core.CoreAugmentItem;
import com.sammy.malum.core.systems.artifice.ArtificeInfluenceData;
import com.sammy.malum.core.systems.artifice.ArtificeModifierSourceInstance;
import com.sammy.malum.core.systems.artifice.IArtificeAcceptor;
import com.sammy.malum.common.block.curiosities.artifice.spirit_catalyzer.*;
import com.sammy.malum.common.item.augment.*;
import com.sammy.malum.common.item.spirit.*;
import com.sammy.malum.core.systems.spirit.SpiritArcanaType;
import com.sammy.malum.registry.common.*;
import com.sammy.malum.visual_effects.SparkParticleEffects;
import com.sammy.malum.visual_effects.SpiritLightSpecs;
import com.sammy.malum.visual_effects.networked.MalumNetworkedParticleEffectColorData;
import net.minecraft.client.*;
import net.minecraft.client.multiplayer.*;
import net.minecraft.core.*;
import net.minecraft.util.*;
import net.minecraft.world.item.*;
import net.minecraft.world.level.*;
import net.minecraft.world.phys.*;
import team.lodestar.lodestone.modules.core.easing.Easing;
import team.lodestar.lodestone.systems.network.particle.NetworkedParticleEffectPositionData;
import team.lodestar.lodestone.modules.rendering.particle.standard.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.builder.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.data.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.data.spin.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.world.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.world.behaviors.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.world.options.*;

import java.util.Optional;
import java.util.function.*;

import static com.sammy.malum.visual_effects.SpiritLightSpecs.*;

public class SpiritCrucibleParticleEffects {

    public static void suspiciousDevicePrimer(NetworkedParticleEffectPositionData positionData, MalumNetworkedParticleEffectColorData colorData) {
        ClientLevel level = Minecraft.getInstance().level;
        var random = level.random;

        for (int i = 0; i < 4; i++) {
            final GenericParticleData scaleData = GenericParticleData.create(Easing.SINE_IN_OUT.asWeighedRandom(random, 1.2f, 0.8f), 0f)
                    .setEasing(Easing.BOUNCE_IN_OUT)
                    .setCoefficient(Easing.SINE_IN_OUT.asWeighedRandom(random, 1f, 1.25f)).build();
            WorldParticleBuilder.create(MalumParticles.CIRCLE.get())
                    .setTransparencyData(GenericParticleData.create(0.7f, 0.3f).setEasing(Easing.SINE_IN_OUT).build())
                    .setSpinData(SpinParticleData.createRandomDirection(random, Easing.SINE_IN_OUT.asWeighedRandom(random, 0.4f, 0.8f)).build())
                    .setColorData(colorData.getColor())
                    .setScaleData(scaleData)
                    .setFriction(0.99f)
                    .setRandomOffset(0.25f)
                    .setLifetime(20)
                    .setLifeDelay(i)
                    .enableNoClip()
                    .repeat(level, positionData.getPosX(), positionData.getPosY(), positionData.getPosZ(), 2);
        }
        for (int i = 0; i < 4; i++) {
            final GenericParticleData scaleData = GenericParticleData.create(0.1f, Easing.SINE_IN_OUT.asWeighedRandom(random, 0.8f, 0.4f), 0f)
                    .setEasing(Easing.BOUNCE_IN_OUT)
                    .setCoefficient(Easing.SINE_IN_OUT.asWeighedRandom(random, 1f, 1.25f)).build();
            final Consumer<LodestoneWorldParticle> behavior = p -> p.setParticleSpeed(p.getParticleSpeed().scale(0.99f));
            WorldParticleBuilder.create(MalumParticles.SHINE.get())
                    .setTransparencyData(GenericParticleData.create(0.7f, 0.3f).setEasing(Easing.SINE_IN_OUT).build())
                    .setSpinData(SpinParticleData.createRandomDirection(random, Easing.SINE_IN_OUT.asWeighedRandom(random, 0.1f, 0.3f)).build())
                    .setColorData(colorData.getColor())
                    .setScaleData(scaleData)
                    .addTickActor(behavior)
                    .setRandomOffset(0.25f)
                    .setLifetime(10)
                    .setLifeDelay(10+i)
                    .enableNoClip()
                    .repeat(level, positionData.getPosX(), positionData.getPosY(), positionData.getPosZ(), 2);
        }
    }

    public static void passiveCrucibleParticles(SpiritCrucibleCoreBlockEntity crucible) {
        var activeSpiritType = crucible.getActiveSpiritType();
        var level = crucible.getLevel();
        var random = level.random;
        if (level.getGameTime() % 16L == 0) {
            var item = crucible.coreAugmentInventory.getStackInSlot(0);
            if (item.getItem() instanceof CoreAugmentItem augmentItem) {
                var blockPos = crucible.getBlockPos();
                for (var augmentSpiritType : augmentItem.spiritTypes) {
                    Vec3 offset = SpiritCrucibleCoreBlockEntity.CRUCIBLE_CORE_AUGMENT_OFFSET.add(
                            Mth.nextFloat(random, -0.1f, 0.1f),
                            Mth.nextFloat(random, -0.1f, 0.1f),
                            Mth.nextFloat(random, -0.1f, 0.1f));
                    var particlePosition = blockPos.getCenter().add(offset);
                    var lightSpecs = SpiritLightSpecs.spiritLightSpecs(level, particlePosition, augmentSpiritType);
                    lightSpecs.getBuilder().multiplyLifetime(2.5f).modifyScaleData(d -> d.multiplyValue(1.3f));
                    lightSpecs.getBloomBuilder().multiplyLifetime(1.5f);
                    lightSpecs.spawnParticles();
                }
            }
        }

        if (activeSpiritType == null) {
            return;
        }
        var itemPos = crucible.getItemPos();
        var spiritInventory = crucible.spiritInventory;
        var augmentInventory = crucible.augmentInventory;
        var recipe = crucible.recipe;
        if (recipe != null) {
            Optional<ArtificeInfluenceData> influenceData = crucible.attributes.getInfluenceData(level);
            influenceData.ifPresent(d -> {
                for (ArtificeModifierSourceInstance modifier : d.modifiers()) {
                    modifier.addParticles(crucible, activeSpiritType);
                }
            });
        }
        if (recipe != null) {
            var lightSpecs = spiritLightSpecs(level, itemPos, activeSpiritType, new WorldParticleOptions(MalumParticles.STAR.get()));
            lightSpecs.getBuilder()
                    .setSpinData(SpinParticleData.create(0).setSpinOffset((level.getGameTime() * 0.05f) % 6.28f).build())
                    .modifyScaleData(d -> d.multiplyValue(2f))
                    .modifyTransparencyData(d -> d.multiplyValue(0.25f));
            lightSpecs.getBloomBuilder()
                    .modifyScaleData(d -> d.multiplyValue(2f))
                    .modifyTransparencyData(d -> d.multiplyValue(0.5f));
            lightSpecs.spawnParticles();
        }

        if (recipe != null) {
            int spiritsRendered = 0;
            for (int i = 0; i < spiritInventory.getSlotCount(); i++) {
                var item = spiritInventory.getStackInSlot(i);
                if (item.getItem() instanceof SpiritShardItem shardItem) {
                    var offset = crucible.getSpiritItemOffset(spiritsRendered++, 0);
                    var blockPos = crucible.getBlockPos();
                    var spiritPosition = new Vec3(blockPos.getX() + offset.x, blockPos.getY() + offset.y, blockPos.getZ() + offset.z);
                    Vec3 velocity = itemPos.subtract(spiritPosition).normalize().scale(Easing.SINE_IN_OUT.asWeighedRandom(random, 0.03f, 0.06f));
                    if (random.nextFloat() < 0.85f) {
                        var sparkParticles = SparkParticleEffects.spiritMotionSparks(level, spiritPosition, shardItem);
                        sparkParticles.getBuilder().setMotion(velocity).modifyScaleData(d -> d.multiplyValue(1.2f));
                        sparkParticles.getBloomBuilder().setMotion(velocity);
                        sparkParticles.spawnParticles();
                    }
                    if (random.nextFloat() < 0.85f) {
                        var lightSpecs = SpiritLightSpecs.spiritLightSpecs(level, spiritPosition, shardItem);
                        lightSpecs.getBuilder().multiplyLifetime(0.8f).setMotion(velocity.scale(1.5f)).modifyScaleData(d -> d.multiplyValue(1.6f));
                        lightSpecs.getBloomBuilder().setMotion(velocity);
                        lightSpecs.spawnParticles();
                    }
                }
            }
        }
        if (level.getGameTime() % 4L == 0) {
            int augmentsRendered = 0;
            for (int i = 0; i < augmentInventory.getSlotCount(); i++) {
                var item = augmentInventory.getStackInSlot(i);
                if (item.getItem() instanceof AugmentItem augmentItem) {
                    var offset = crucible.getAugmentItemOffset(augmentsRendered++, 0);
                    var blockPos = crucible.getBlockPos();
                    var particlePosition = new Vec3(blockPos.getX() + offset.x, blockPos.getY() + offset.y, blockPos.getZ() + offset.z);
                    for (var spiritType : augmentItem.spiritTypes) {
                        if (recipe != null) {
                            Vec3 velocity = itemPos.subtract(particlePosition).normalize().scale(Easing.SINE_IN_OUT.asWeighedRandom(random, 0.01f, 0.02f));
                            if (random.nextFloat() < 0.15f) {
                                var sparkParticles = SparkParticleEffects.spiritMotionSparks(level, particlePosition, spiritType);
                                sparkParticles.getBuilder().multiplyLifetime(2.5f).setMotion(velocity).modifyScaleData(d -> d.multiplyValue(1.2f));
                                sparkParticles.getBloomBuilder().multiplyLifetime(1.5f).setMotion(velocity);
                                sparkParticles.spawnParticles();
                            }
                            if (random.nextFloat() < 0.15f) {
                                var lightSpecs = SpiritLightSpecs.spiritLightSpecs(level, particlePosition, spiritType);
                                lightSpecs.getBuilder().multiplyLifetime(2.5f).setMotion(velocity.scale(1.5f)).modifyScaleData(d -> d.multiplyValue(1.6f));
                                lightSpecs.getBloomBuilder().multiplyLifetime(1.5f).setMotion(velocity);
                                lightSpecs.spawnParticles();
                            }
                        }
                        var lightSpecs = SpiritLightSpecs.spiritLightSpecs(level, particlePosition, spiritType);
                        lightSpecs.getBuilder().multiplyLifetime(2.5f).modifyScaleData(d -> d.multiplyValue(1.3f));
                        lightSpecs.getBloomBuilder().multiplyLifetime(1.5f);
                        lightSpecs.spawnParticles();
                    }
                }
            }
        }
    }

    public static void craftItemParticles(SpiritCrucibleCoreBlockEntity crucible, MalumNetworkedParticleEffectColorData colorData) {
        SpiritArcanaType activeSpiritType = crucible.getActiveSpiritType();
        if (activeSpiritType == null) {
            return;
        }
        Level level = crucible.getLevel();
        var random = level.random;
        var cruciblePos = crucible.getBlockPos();
        Vec3 crucibleItemPos = cruciblePos.getCenter().add(SpiritCrucibleCoreBlockEntity.CRUCIBLE_ITEM_OFFSET);

        for (int i = 0; i < 2; i++) {
            SpiritLightSpecs.coolLookingShinyThing(level, crucibleItemPos, activeSpiritType);
        }
        for (int i = 0; i < 24; i++) {
            int lifeDelay = i / 8;
            SpiritArcanaType cyclingSpiritType = colorData.getSpirit();
            float xVelocity = Easing.CUBIC_OUT.asWeighedRandom(random, -0.075f, 0.075f);
            float yVelocity = Easing.SINE_IN_OUT.asWeighedRandom(random, 0.2f, 0.5f);
            float zVelocity = Easing.CUBIC_OUT.asWeighedRandom(random, -0.075f, 0.075f);
            float gravityStrength = Easing.SINE_IN_OUT.asWeighedRandom(random, 0.75f, 1f);
            if (random.nextFloat() < 0.85f) {
                var sparkParticles = SparkParticleEffects.spiritMotionSparks(level, crucibleItemPos, cyclingSpiritType);
                sparkParticles.getBuilder()
                        .disableNoClip()
                        .setLifeDelay(lifeDelay)
                        .multiplyLifetime(2)
                        .setGravity(gravityStrength)
                        .setMotion(xVelocity, yVelocity, zVelocity)
                        .modifyScaleData(d -> d.multiplyValue(2f));
                sparkParticles.getBloomBuilder()
                        .disableNoClip()
                        .setLifeDelay(lifeDelay)
                        .multiplyLifetime(2)
                        .setGravity(gravityStrength)
                        .setMotion(xVelocity, yVelocity, zVelocity)
                        .modifyTransparencyData(d -> d.multiplyValue(1.25f));
                sparkParticles.spawnParticles();
            }
            if (random.nextFloat() < 0.85f) {
                xVelocity *= 1.25f;
                yVelocity *= 0.75f;
                zVelocity *= 1.25f;
                var lightSpecs = SpiritLightSpecs.spiritLightSpecs(level, crucibleItemPos, cyclingSpiritType);
                lightSpecs.getBuilder()
                        .disableNoClip()
                        .setLifeDelay(lifeDelay)
                        .multiplyLifetime(4)
                        .setGravity(gravityStrength)
                        .setMotion(xVelocity, yVelocity, zVelocity)
                        .modifyScaleData(d -> d.multiplyValue(2.5f));
                lightSpecs.getBloomBuilder()
                        .disableNoClip()
                        .setLifeDelay(lifeDelay)
                        .multiplyLifetime(4)
                        .setGravity(gravityStrength)
                        .setMotion(xVelocity, yVelocity, zVelocity)
                        .modifyTransparencyData(d -> d.multiplyValue(1.25f));
                lightSpecs.spawnParticles();
            }
        }

        var smokePos = crucibleItemPos.subtract(0, 0.5f, 0);
        for (int i = 0; i < 8; i++) {
            SpiritArcanaType cyclingSpiritType = colorData.getSpirit();
            float xVelocity = Easing.CUBIC_OUT.asWeighedRandom(random, -0.025f, 0.025f);
            float yVelocity = Easing.SINE_IN_OUT.asWeighedRandom(random, 0.015f, 0.035f);
            float zVelocity = Easing.CUBIC_OUT.asWeighedRandom(random, -0.025f, 0.025f);
            if (random.nextFloat() < 0.85f) {
                var lightSpecs = SpiritLightSpecs.spiritLightSpecs(level, smokePos, cyclingSpiritType, new WorldParticleOptions(MalumParticles.STRANGE_SMOKE.get()));
                lightSpecs.getBuilder()
                        .disableNoClip()
                        .setLifeDelay(i)
                        .multiplyLifetime(5)
                        .setMotion(xVelocity, yVelocity, zVelocity)
                        .setSpritePicker(SimpleParticleOptions.ParticleSpritePicker.WITH_AGE)
                        .modifyColorData(c -> c.multiplyCoefficient(0.5f))
                        .modifyScaleData(d -> d.multiplyValue(1.5f))
                        .modifyTransparencyData(d -> d.multiplyValue(0.1f));
                lightSpecs.getBloomBuilder()
                        .disableNoClip()
                        .setLifeDelay(i)
                        .multiplyLifetime(5)
                        .setMotion(xVelocity, yVelocity, zVelocity)
                        .setSpritePicker(SimpleParticleOptions.ParticleSpritePicker.WITH_AGE)
                        .modifyColorData(c -> c.multiplyCoefficient(0.5f))
                        .modifyScaleData(d -> d.multiplyValue(2.5f))
                        .modifyTransparencyData(d -> d.multiplyValue(0.25f));
                lightSpecs.spawnParticles();
            }
        }
    }

    public static void activeSpiritCatalyzerParticles(SpiritCatalyzerCoreBlockEntity catalyzer, IArtificeAcceptor target, SpiritArcanaType spiritType) {
        Level level = catalyzer.getLevel();
        BlockPos catalyzerPos = catalyzer.getBlockPos();
        Vec3 startPos = SpiritCatalyzerCoreBlockEntity.CATALYZER_ITEM_OFFSET.add(catalyzerPos.getX(), catalyzerPos.getY(), catalyzerPos.getZ());
        RandomSource random = level.random;
        Vec3 targetPos = target.getVisualAccelerationPoint();
        if (level.getGameTime() % 2L == 0) {
            Vec3 velocity = targetPos.subtract(startPos).normalize().scale(Easing.SINE_IN_OUT.asWeighedRandom(random, 0.06f, 0.12f));
            Vec3 sparkPos = startPos.add(0.05f - random.nextFloat() * 0.1f, 0.05f - random.nextFloat() * 0.1f, 0.05f - random.nextFloat() * 0.1f);
            var sparkParticles = SparkParticleEffects.spiritMotionSparks(level, sparkPos, spiritType);
            sparkParticles.getBuilder().setMotion(velocity)
                    .modifyScaleData(d -> d.multiplyValue(1.5f))
                    .modifyLengthData(d -> d.multiplyValue(2f).multiplyCoefficient(0.75f))
                    .modifyColorData(c -> c.multiplyCoefficient(0.8f));
            sparkParticles.getBloomBuilder().setMotion(velocity);
            sparkParticles.spawnParticlesRaw();
        }
        if (level.getGameTime() % 10L == 0) {
            Vec3 velocity = targetPos.subtract(startPos).normalize().scale(0.02f * targetPos.distanceTo(startPos));
            final Consumer<LodestoneWorldParticle> behavior = p -> p.setParticleSpeed(p.getParticleSpeed().scale(0.98f));
            final SpinParticleData spinData = SpinParticleData.createRandomDirection(random, Easing.SINE_IN_OUT.asWeighedRandom(random, 0.1f, 0.2f)).randomSpinOffset(random).build();
            WorldParticleBuilder.create(MalumParticles.HEXAGON.get())
                    .setBehavior(DirectionalParticleBehavior.directional(velocity.normalize()))
                    .setTransparencyData(GenericParticleData.create(0.6f, 0.4f, 0f).setEasing(Easing.SINE_IN_OUT, Easing.SINE_IN).build())
                    .setSpinData(spinData)
                    .setScaleData(GenericParticleData.create(0.15f, 0).setEasing(Easing.SINE_IN_OUT).build())
                    .setColorData(spiritType.createColorData().build())
                    .setLifetime(60)
                    .setMotion(velocity)
                    .enableNoClip()
                    .setSpritePicker(SimpleParticleOptions.ParticleSpritePicker.RANDOM_SPRITE)
                    .addTickActor(behavior)
                    .spawn(level, startPos.x, startPos.y, startPos.z);
        }

        if (level.getGameTime() % 4L == 0) {
            ItemStack item = catalyzer.augmentInventory.getStackInSlot(0);
            if (item.getItem() instanceof AugmentItem augmentItem) {
                Vec3 offset = SpiritCatalyzerCoreBlockEntity.CATALYZER_AUGMENT_OFFSET;
                BlockPos blockPos = catalyzer.getBlockPos();
                Vec3 particlePosition = new Vec3(blockPos.getX() + offset.x, blockPos.getY() + offset.y, blockPos.getZ() + offset.z);
                for (var augmentSpiritType : augmentItem.spiritTypes) {
                    Vec3 velocity = targetPos.subtract(particlePosition).normalize().scale(Easing.SINE_IN_OUT.asWeighedRandom(random, 0.03f, 0.06f));
                    if (random.nextFloat() < 0.15f) {
                        var sparkParticles = SparkParticleEffects.spiritMotionSparks(level, particlePosition, augmentSpiritType);
                        sparkParticles.getBuilder().multiplyLifetime(2.5f).setMotion(velocity).modifyScaleData(d -> d.multiplyValue(1.2f));
                        sparkParticles.getBloomBuilder().multiplyLifetime(1.5f).setMotion(velocity);
                        sparkParticles.spawnParticles();
                    }
                    if (random.nextFloat() < 0.15f) {
                        var lightSpecs = SpiritLightSpecs.spiritLightSpecs(level, particlePosition, augmentSpiritType);
                        lightSpecs.getBuilder().multiplyLifetime(2.5f).setMotion(velocity.scale(1.5f)).modifyScaleData(d -> d.multiplyValue(1.6f));
                        lightSpecs.getBloomBuilder().multiplyLifetime(1.5f).setMotion(velocity);
                        lightSpecs.spawnParticles();
                    }
                }
            }
        }
    }


    public static void passiveSpiritCatalyzerParticles(SpiritCatalyzerCoreBlockEntity catalyzer) {
        Level level = catalyzer.getLevel();
        RandomSource random = level.random;
        if (level.getGameTime() % 16L == 0) {
            ItemStack item = catalyzer.augmentInventory.getStackInSlot(0);
            if (item.getItem() instanceof AugmentItem augmentItem) {
                BlockPos blockPos = catalyzer.getBlockPos();
                for (var augmentSpiritType : augmentItem.spiritTypes) {
                    Vec3 offset = SpiritCatalyzerCoreBlockEntity.CATALYZER_AUGMENT_OFFSET.add(
                            Mth.nextFloat(random, -0.1f, 0.1f),
                            Mth.nextFloat(random, -0.1f, 0.1f),
                            Mth.nextFloat(random, -0.1f, 0.1f));
                    Vec3 particlePosition = new Vec3(blockPos.getX() + offset.x, blockPos.getY() + offset.y, blockPos.getZ() + offset.z);
                    var lightSpecs = SpiritLightSpecs.spiritLightSpecs(level, particlePosition, augmentSpiritType);
                    lightSpecs.getBuilder().multiplyLifetime(2.5f).modifyScaleData(d -> d.multiplyValue(1.3f));
                    lightSpecs.getBloomBuilder().multiplyLifetime(1.5f);
                    lightSpecs.spawnParticles();
                }
            }
        }
    }
}