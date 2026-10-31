package com.sammy.malum.visual_effects.block;

import com.sammy.malum.common.block.curiosities.obelisk.rite_pylon.*;
import com.sammy.malum.common.block.curiosities.obelisk.runewood.*;
import com.sammy.malum.common.block.curiosities.sorcery.spirit_altar.*;
import com.sammy.malum.common.block.storage.*;
import com.sammy.malum.common.item.spirit.*;
import com.sammy.malum.core.systems.spirit.SpiritArcanaType;
import com.sammy.malum.core.systems.spirit.SpiritLike;
import com.sammy.malum.registry.common.MalumParticles;
import com.sammy.malum.visual_effects.ItemCrumbleParticleEffects;
import com.sammy.malum.visual_effects.SparkParticleEffects;
import com.sammy.malum.visual_effects.SpiritLightSpecs;
import com.sammy.malum.visual_effects.networked.MalumNetworkedParticleEffectColorData;
import net.minecraft.util.*;
import net.minecraft.world.item.*;
import net.minecraft.world.level.*;
import net.minecraft.world.phys.*;
import team.lodestar.lodestone.helpers.*;
import team.lodestar.lodestone.modules.core.easing.Easing;
import team.lodestar.lodestone.modules.toolkit.inventory.ItemStackHandlerItemDisplayData;
import team.lodestar.lodestone.modules.toolkit.inventory.LodestoneItemStackHandler;
import team.lodestar.lodestone.modules.rendering.particle.standard.SimpleParticleOptions;
import team.lodestar.lodestone.modules.rendering.particle.standard.builder.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.data.GenericParticleData;
import team.lodestar.lodestone.modules.rendering.particle.standard.data.spin.SpinParticleData;
import team.lodestar.lodestone.modules.rendering.particle.standard.world.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.world.options.WorldParticleOptions;
import team.lodestar.lodestone.modules.toolkit.inventory.display.ItemDisplayDataEntry;

import java.util.function.*;

import static com.sammy.malum.visual_effects.SpiritLightSpecs.*;

public class SpiritAltarParticleEffects {

    public static SpiritLike getCentralSpiritType(SpiritAltarBlockEntity altar) {
        final LodestoneItemStackHandler spiritInventory = altar.spiritInventory;
        int spiritCount = spiritInventory.getFilledSlotCount();
        Item currentItem = spiritInventory.getStackInSlot(0).getItem();
        if (spiritCount > 1) {
            float duration = 30f * spiritCount;
            float gameTime = (altar.getLevel().getGameTime() % duration) / 30f;
            currentItem = spiritInventory.getStackInSlot(Mth.floor(gameTime)).getItem();
        }
        if (!(currentItem instanceof SpiritShardItem spiritItem)) {
            return null;
        }
        return spiritItem;
    }

    public static void passiveSpiritAltarParticles(SpiritAltarBlockEntity altar) {
        SpiritLike activeSpiritType = getCentralSpiritType(altar);
        if (activeSpiritType == null) {
            return;
        }
        var level = altar.getLevel();
        var random = level.random;
        var itemPos = altar.inventory.getDisplayData().getDisplayCenter(0);
        var recipe = altar.recipe;
        if (recipe != null) {
            for (IAltarAccelerator accelerator : altar.accelerators) {
                if (accelerator != null) {
                    if (accelerator.canAccelerate(altar)) {
                        accelerator.addParticles(altar, activeSpiritType.getSpirit());
                    }
                }
            }
            SpiritLightSpecs.rotatingLightSpecs(level, itemPos, activeSpiritType, 0.5f, 3,
                    b -> b.multiplyLifetime(1.2f).modifyScaleData(d -> d.multiplyValue(1.2f)));
        }

        var spiritDisplayData = altar.spiritInventory.getDisplayData();
        for (ItemDisplayDataEntry dataEntry : spiritDisplayData.getDataEntries()) {
            var stack = dataEntry.getStack();
            if (stack.getItem() instanceof SpiritShardItem shard) {
                Vec3 spiritPosition = spiritDisplayData.getItemPosition(dataEntry);
                spiritLightSpecs(level, spiritPosition, shard).spawnParticles();
                if (recipe != null) {
                    Vec3 velocity = itemPos.subtract(spiritPosition).normalize().scale(Easing.SINE_IN_OUT.asWeighedRandom(random, 0.03f, 0.06f));
                    if (random.nextFloat() < 0.85f) {
                        var sparkParticles = SparkParticleEffects.spiritMotionSparks(level, spiritPosition, shard);
                        sparkParticles.getBuilder().setMotion(velocity).modifyScaleData(d -> d.multiplyValue(1.2f));
                        sparkParticles.getBloomBuilder().setMotion(velocity);
                        sparkParticles.spawnParticles();
                    }
                    if (random.nextFloat() < 0.85f) {
                        var lightSpecs = SpiritLightSpecs.spiritLightSpecs(level, spiritPosition, shard);
                        lightSpecs.getBuilder().multiplyLifetime(0.8f).setMotion(velocity.scale(1.5f)).modifyScaleData(d -> d.multiplyValue(1.6f));
                        lightSpecs.getBloomBuilder().setMotion(velocity);
                        lightSpecs.spawnParticles();
                    }
                }
            }
        }
    }

    public static void eatItemParticles(Level level, SpiritAltarBlockEntity altar, IMalumSpecialItemAccessPoint holder, MalumNetworkedParticleEffectColorData colorData, ItemStack stack) {
        SpiritLike activeSpiritType = getCentralSpiritType(altar);
        if (activeSpiritType == null) {
            return;
        }
        long gameTime = level.getGameTime();
        var random = level.random;
        var altarTargetPos = getItemPos(altar);
        var holderTargetPos = holder.getItemPos();
        for (int i = 0; i < 2; i++) {
            SpiritLightSpecs.coolLookingShinyThing(level, holderTargetPos, activeSpiritType);
        }
        for (int i = 0; i < 16; i++) {
            int finalI = i;
            SpiritArcanaType cyclingSpiritType = colorData.getSpirit();
            Vec3 velocity = altarTargetPos.subtract(holderTargetPos).normalize().scale(0.025f);
            Vec3 offsetPosition = VecHelper.rotatingRadialOffset(holderTargetPos, 0.5f, i, 16, gameTime, 160);
            final Consumer<LodestoneWorldParticle> behavior = p -> {
                if (level.getGameTime() > gameTime + finalI * 2 && level.getGameTime() < gameTime + (finalI + 4) * 2) {
                    p.setParticleSpeed(p.getParticleSpeed().add(velocity));
                }
            };
            var lightSpecs = spiritLightSpecs(level, offsetPosition, cyclingSpiritType);
            lightSpecs.getBuilder()
                    .addTickActor(behavior)
                    .multiplyLifetime(2.5f)
                    .modifyScaleData(d -> d.multiplyValue(Easing.SINE_IN_OUT.asWeighedRandom(random, 1f, 2f)));
            lightSpecs.getBloomBuilder()
                    .addTickActor(behavior)
                    .multiplyLifetime(2f)
                    .modifyScaleData(d -> d.multiplyValue(Easing.SINE_IN_OUT.asWeighedRandom(random, 0.6f, 1.5f)));
            lightSpecs.spawnParticles();

            var crumbles = ItemCrumbleParticleEffects.spawnItemCrumbs(level, holderTargetPos, stack);
            crumbles.getBuilder()
                    .setLifeDelay(i)
                    .addTickActor(behavior);
            crumbles.spawnParticles();
            crumbles.getBuilder().setRandomOffset(0.2f);
            crumbles.spawnParticles();
        }
    }

    public static void craftItemParticles(Level level, SpiritAltarBlockEntity altar, MalumNetworkedParticleEffectColorData colorData) {
        SpiritLike activeSpiritType = getCentralSpiritType(altar);
        if (activeSpiritType == null) {
            return;
        }
        long gameTime = level.getGameTime();
        var random = level.random;
        var targetPos = getItemPos(altar);

        for (int i = 0; i < 2; i++) {
            SpiritLightSpecs.coolLookingShinyThing(level, targetPos, activeSpiritType);
        }
        for (int i = 0; i < 8; i++) {
            SpiritArcanaType cyclingSpiritType = colorData.getSpirit();
            float xOffset = Easing.CUBIC_OUT.asWeighedRandom(random, 0.1f, 0.5f) * (random.nextBoolean() ? -1 : 1);
            float yOffset = i * 0.08f;
            float zOffset = Easing.CUBIC_OUT.asWeighedRandom(random, 0.1f, 0.5f) * (random.nextBoolean() ? -1 : 1);

            var offsetPos = targetPos.add(xOffset, yOffset, zOffset);
            int lifeDelay = 5 + i * 3;
            var lightSpecs = SpiritLightSpecs.spiritLightSpecs(level, offsetPos, cyclingSpiritType, new WorldParticleOptions(MalumParticles.SHINE));
            lightSpecs.getBuilder()
                    .modifyTransparencyData(d -> d.multiplyValue(1.25f))
                    .setSpinData(SpinParticleData.create(0).randomSpinOffset(random).build())
                    .setSpritePicker(SimpleParticleOptions.ParticleSpritePicker.WITH_AGE)
                    .setScaleData(GenericParticleData.create(0.3f).build())
                    .multiplyLifetime(1.25f)
                    .setLifeDelay(lifeDelay)
                    .disableNoClip();
            lightSpecs.getBloomBuilder()
                    .modifyScaleData(d -> d.multiplyValue(3f))
                    .modifyTransparencyData(d -> d.multiplyValue(1.25f))
                    .multiplyLifetime(0.85f)
                    .setLifeDelay(lifeDelay)
                    .disableNoClip();
            lightSpecs.spawnParticles();
        }

        for (int i = 0; i < 12; i++) {
            int lifeDelay = i / 4;
            SpiritArcanaType cyclingSpiritType = colorData.getSpirit();
            float xVelocity = Easing.CUBIC_OUT.asWeighedRandom(random, -0.075f, 0.075f);
            float yVelocity = Easing.SINE_IN_OUT.asWeighedRandom(random, 0.2f, 0.5f);
            float zVelocity = Easing.CUBIC_OUT.asWeighedRandom(random, -0.075f, 0.075f);
            float gravityStrength = Easing.SINE_IN_OUT.asWeighedRandom(random, 0.75f, 1f);
            if (random.nextFloat() < 0.85f) {
                var sparkParticles = SparkParticleEffects.spiritMotionSparks(level, targetPos, cyclingSpiritType);
                sparkParticles.getBuilder()
                        .disableNoClip()
                        .setLifeDelay(lifeDelay)
                        .multiplyLifetime(1.5f)
                        .setGravity(gravityStrength)
                        .setMotion(xVelocity, yVelocity, zVelocity)
                        .modifyScaleData(d -> d.multiplyValue(2f));
                sparkParticles.getBloomBuilder()
                        .disableNoClip()
                        .setLifeDelay(lifeDelay)
                        .multiplyLifetime(1.5f)
                        .setGravity(gravityStrength)
                        .setMotion(xVelocity, yVelocity, zVelocity)
                        .modifyTransparencyData(d -> d.multiplyValue(1.25f));
                sparkParticles.spawnParticles();
            }
            if (random.nextFloat() < 0.85f) {
                xVelocity *= 1.25f;
                yVelocity *= 0.75f;
                zVelocity *= 1.25f;
                var lightSpecs = SpiritLightSpecs.spiritLightSpecs(level, targetPos, cyclingSpiritType);
                lightSpecs.getBuilder()
                        .disableNoClip()
                        .setLifeDelay(lifeDelay)
                        .multiplyLifetime(2)
                        .setGravity(gravityStrength)
                        .setMotion(xVelocity, yVelocity, zVelocity)
                        .modifyScaleData(d -> d.multiplyValue(2.5f));
                lightSpecs.getBloomBuilder()
                        .disableNoClip()
                        .setLifeDelay(lifeDelay)
                        .multiplyLifetime(1.5f)
                        .setGravity(gravityStrength)
                        .setMotion(xVelocity, yVelocity, zVelocity)
                        .modifyTransparencyData(d -> d.multiplyValue(1.25f));
                lightSpecs.spawnParticles();
            }
        }
        for (int i = 0; i < 8; i++) {
            int finalI = i;
            Vec3 offsetPosition = VecHelper.rotatingRadialOffset(targetPos, 0.6f, i, 8, gameTime, 160);
            Consumer<WorldParticleBuilder> behavior = b -> b.addTickActor(p -> {
                if (level.getGameTime() > gameTime + finalI * 4 && level.getGameTime() < gameTime + (finalI + 4) * 4) {
                    p.setParticleSpeed(p.getParticleSpeed().add(0, 0.015f, 0));
                }
            });
            int lifetime = Easing.SINE_IN_OUT.asWeighedRandom(random, 10, 20) + finalI * 2;
            var lightSpecs = spiritLightSpecs(level, offsetPosition, activeSpiritType);
            lightSpecs.getBuilder()
                    .act(behavior)
                    .modifyColorData(d -> d.multiplyCoefficient(0.35f))
                    .modifyScaleData(d -> d.multiplyValue(2f).multiplyCoefficient(0.9f))
                    .modifyTransparencyData(d -> d.multiplyCoefficient(0.9f))
                    .setLifetime(lifetime);
            lightSpecs.getBloomBuilder()
                    .act(behavior)
                    .modifyColorData(d -> d.multiplyCoefficient(0.35f))
                    .modifyScaleData(d -> d.multiplyValue(1.6f).multiplyCoefficient(0.9f))
                    .modifyTransparencyData(d -> d.multiplyCoefficient(0.9f))
                    .setLifetime(lifetime);
            lightSpecs.spawnParticles();
        }
    }

    public static void runewoodObeliskParticles(RunewoodObeliskBlockEntity obelisk, SpiritAltarBlockEntity altar, SpiritArcanaType spiritType) {
        var level = obelisk.getLevel();
        var obeliskPos = obelisk.getBlockPos();
        var startPos = obelisk.getParticleOffset().add(obeliskPos.getX(), obeliskPos.getY(), obeliskPos.getZ());
        spiritLightSpecs(level, startPos, spiritType).spawnParticles();
        if (level.getGameTime() % 2L == 0) {
            var random = level.random;
            long gameTime = level.getGameTime();
            var targetPos = getItemPos(altar);
            var direction = targetPos.subtract(startPos).normalize();
            var velocity = direction.scale(Easing.SINE_IN_OUT.asWeighedRandom(random, 0.01f, 0.02f));
            double yOffset = Math.sin((gameTime*0.2f) % 6.28f) * 0.1f;
            var offsetPosition = VecHelper.rotatingRadialOffset(startPos.add(0, yOffset, 0), 0.45f, 0, 1, gameTime, 30);
            Consumer<WorldParticleBuilder> behavior = b -> b.addTickActor(p -> {
                if (gameTime % 6L == 0) {
                    p.setParticleSpeed(p.getParticleSpeed().scale(1.05f));
                }
            });
            var lightSpecs = spiritLightSpecs(level, offsetPosition, spiritType);
            lightSpecs.getBuilder()
                    .act(behavior)
                    .setMotion(velocity)
                    .multiplyLifetime(2f)
                    .modifyScaleData(d -> d.multiplyValue(Easing.SINE_IN_OUT.asWeighedRandom(random, 1f, 2f)));
            lightSpecs.getBloomBuilder()
                    .act(behavior)
                    .setMotion(velocity)
                    .multiplyLifetime(1.5f)
                    .modifyScaleData(d -> d.multiplyValue(Easing.SINE_IN_OUT.asWeighedRandom(random, 0.6f, 1.5f)));
            lightSpecs.spawnParticles();
        }
    }

    public static void arcanaPylonParticles(ArcanaPylonBlockEntity arcanaPylon, SpiritAltarBlockEntity altar, SpiritArcanaType spiritType) {
        var level = arcanaPylon.getLevel();
        var startPos = arcanaPylon.getItemPos();
        spiritLightSpecs(level, startPos, spiritType).spawnParticles();
        if (level.getGameTime() % 2L == 0) {
            var random = level.random;
            long gameTime = level.getGameTime();
            var targetPos = getItemPos(altar);
            var direction = targetPos.subtract(startPos).normalize();
            var velocity = direction.scale(Easing.SINE_IN_OUT.asWeighedRandom(random, 0.025f, 0.04f));
            double yOffset = Math.sin((gameTime*0.4f) % 6.28f) * 0.1f;
            var offsetPosition = VecHelper.rotatingRadialOffset(startPos.add(0, yOffset, 0), 0.45f, 0, 1, gameTime, 40);
            Consumer<WorldParticleBuilder> behavior = b -> b.addTickActor(p -> {
                if (gameTime % 6L == 0) {
                    p.setParticleSpeed(p.getParticleSpeed().scale(1.1f));
                }
            });
            var sparks = SparkParticleEffects.spiritMotionSparks(level, offsetPosition, spiritType);
            sparks.getBuilder()
                    .act(behavior)
                    .setMotion(velocity)
                    .multiplyLifetime(3f)
                    .modifyScaleData(d -> d.multiplyValue(Easing.SINE_IN_OUT.asWeighedRandom(random, 1f, 2f)));
            sparks.getBloomBuilder()
                    .act(behavior)
                    .setMotion(velocity)
                    .multiplyLifetime(2.5f)
                    .modifyScaleData(d -> d.multiplyValue(Easing.SINE_IN_OUT.asWeighedRandom(random, 0.6f, 1.5f)));
            sparks.spawnParticles();
        }
    }

    public static Vec3 getItemPos(SpiritAltarBlockEntity altar) {
        return altar.inventory.getDisplayData().getDisplayCenter(0);
    }
}