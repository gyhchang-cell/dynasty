package com.sammy.malum.visual_effects.block;

import com.sammy.malum.common.block.curiosities.artifice.repair_pylon.*;
import com.sammy.malum.common.block.storage.*;
import com.sammy.malum.common.item.spirit.*;
import com.sammy.malum.core.systems.spirit.SpiritArcanaType;
import com.sammy.malum.core.systems.spirit.SpiritLike;
import com.sammy.malum.visual_effects.SparkParticleEffects;
import com.sammy.malum.visual_effects.SpiritLightSpecs;
import com.sammy.malum.visual_effects.networked.MalumNetworkedParticleEffectColorData;
import net.minecraft.core.*;
import net.minecraft.util.*;
import net.minecraft.world.item.*;
import net.minecraft.world.level.*;
import net.minecraft.world.phys.*;
import team.lodestar.lodestone.helpers.*;
import team.lodestar.lodestone.modules.core.easing.Easing;
import team.lodestar.lodestone.modules.toolkit.inventory.LodestoneItemStackHandler;
import team.lodestar.lodestone.modules.rendering.particle.standard.builder.*;

import javax.annotation.*;
import java.util.function.*;

import static com.sammy.malum.visual_effects.SpiritLightSpecs.*;

public class RepairPylonParticleEffects {

    public static SpiritLike getCentralSpiritType(RepairPylonCoreBlockEntity pylon) {
        final LodestoneItemStackHandler spiritInventory = pylon.spiritInventory;
        int spiritCount = spiritInventory.getFilledSlotCount();
        Item currentItem = spiritInventory.getStackInSlot(0).getItem();
        if (spiritCount > 1) {
            float duration = 60f * spiritCount;
            float gameTime = (pylon.getLevel().getGameTime() % duration) / 60f;
            currentItem = spiritInventory.getStackInSlot(Mth.floor(gameTime)).getItem();
        }
        if (!(currentItem instanceof SpiritShardItem spiritItem)) {
            return null;
        }
        return spiritItem;
    }

    public static void passiveRepairPylonParticles(RepairPylonCoreBlockEntity pylon, @Nullable IMalumSpecialItemAccessPoint holder) {
        var activeSpiritType = getCentralSpiritType(pylon);
        if (activeSpiritType == null) {
            return;
        }
        var level = pylon.getLevel();
        var random = level.random;
        var itemPos = pylon.getItemPos();
        var recipe = pylon.recipe;
        boolean isCharging = pylon.state.equals(RepairPylonCoreBlockEntity.RepairPylonState.CHARGING);
        if (recipe != null) {
                SpiritLightSpecs.rotatingLightSpecs(level, itemPos, activeSpiritType, 0.5f, 3,
                        b -> b.multiplyLifetime(1.2f).modifyScaleData(d -> d.multiplyValue(1.2f)));

            if (isCharging && holder != null) {
                Vec3 targetItemPos = holder.getItemPos();
                SpiritLightSpecs.rotatingLightSpecs(level, targetItemPos, activeSpiritType, 0.5f, 4, b -> b.multiplyLifetime(0.6f).modifyScaleData(d -> d.multiplyValue(0.95f)));
                SpiritLightSpecs.rotatingLightSpecs(level, targetItemPos, activeSpiritType, 0.75f, 5, b -> b.multiplyLifetime(1.2f).modifyScaleData(d -> d.multiplyValue(1.15f)));
            }
        }

        var spiritInventory = pylon.spiritInventory;
        int spiritsRendered = 0;
        for (int i = 0; i < spiritInventory.getSlotCount(); i++) {
            ItemStack item = spiritInventory.getStackInSlot(i);
            if (item.getItem() instanceof SpiritShardItem spiritSplinterItem) {
                Vec3 offset = pylon.getSpiritItemOffset(spiritsRendered++, 0);
                activeSpiritType = spiritSplinterItem;
                BlockPos blockPos = pylon.getBlockPos();
                Vec3 spiritPosition = new Vec3(blockPos.getX() + offset.x, blockPos.getY() + offset.y, blockPos.getZ() + offset.z);
                spiritLightSpecs(level, spiritPosition, activeSpiritType).spawnParticles();
                if (recipe != null && isCharging) {
                    Vec3 velocity = itemPos.subtract(spiritPosition).normalize().scale(Easing.SINE_IN_OUT.asWeighedRandom(random, 0.03f, 0.06f));
                    if (random.nextFloat() < 0.85f) {
                        var sparkParticles = SparkParticleEffects.spiritMotionSparks(level, spiritPosition, activeSpiritType);
                        sparkParticles.getBuilder().setMotion(velocity).modifyScaleData(d -> d.multiplyValue(1.2f));
                        sparkParticles.getBloomBuilder().setMotion(velocity);
                        sparkParticles.spawnParticles();
                    }
                    if (random.nextFloat() < 0.85f) {
                        var lightSpecs = SpiritLightSpecs.spiritLightSpecs(level, spiritPosition, activeSpiritType);
                        lightSpecs.getBuilder().multiplyLifetime(0.8f).setMotion(velocity.scale(1.5f)).modifyScaleData(d -> d.multiplyValue(1.6f));
                        lightSpecs.getBloomBuilder().setMotion(velocity);
                        lightSpecs.spawnParticles();
                    }
                }
            }
        }
    }

    public static void prepareRepairParticles(RepairPylonCoreBlockEntity pylon, IMalumSpecialItemAccessPoint holder, MalumNetworkedParticleEffectColorData colorData) {
        SpiritLike activeSpiritType = getCentralSpiritType(pylon);
        if (activeSpiritType == null) {
            return;
        }
        Level level = pylon.getLevel();
        var random = level.random;
        long gameTime = level.getGameTime();
        Vec3 pylonItemPos = pylon.getItemPos();
        Vec3 holderItemPos = holder.getItemPos();

        for (int i = 0; i < 2; i++) {
            SpiritLightSpecs.coolLookingShinyThing(level, pylonItemPos, activeSpiritType);
        }
        for (int i = 0; i < 4; i++) {
            SpiritArcanaType cyclingSpiritType = colorData.getSpirit();
            for (int j = 0; j < 60; j++) {
                float distance = 0.8f * (1 - j / 90f);
                long time = gameTime+j*4;
                Vec3 offsetPosition = VecHelper.rotatingRadialOffset(holderItemPos, distance, i, 4, time, 160);
                if (random.nextFloat() < 0.85f) {
                    var sparkParticles = SparkParticleEffects.spiritMotionSparks(level, offsetPosition, cyclingSpiritType);
                    sparkParticles.getBuilder()
                            .disableNoClip()
                            .setLifeDelay(j)
                            .multiplyLifetime(0.75f)
                            .modifyScaleData(d -> d.multiplyValue(1f));
                    sparkParticles.getBloomBuilder()
                            .disableNoClip()
                            .setLifeDelay(j)
                            .multiplyLifetime(0.75f)
                            .modifyTransparencyData(d -> d.multiplyValue(1.25f));
                    sparkParticles.spawnParticles();
                }
                if (random.nextFloat() < 0.85f) {
                    var lightSpecs = SpiritLightSpecs.spiritLightSpecs(level, offsetPosition, cyclingSpiritType);
                    lightSpecs.getBuilder()
                            .disableNoClip()
                            .setLifeDelay(j)
                            .modifyScaleData(d -> d.multiplyValue(1.5f));
                    lightSpecs.getBloomBuilder()
                            .disableNoClip()
                            .setLifeDelay(j)
                            .modifyTransparencyData(d -> d.multiplyValue(1.25f));
                    lightSpecs.spawnParticles();
                }
            }
            for (int j = 0; j < 32; j++) {
                float distance = 0.8f * (j / 32f);
                long time = gameTime+j*3;
                int lifeDelay = 32 - j;
                Vec3 offsetPosition = VecHelper.rotatingRadialOffset(pylonItemPos, distance, i, 4, time, 160);
                if (random.nextFloat() < 0.85f) {
                    var sparkParticles = SparkParticleEffects.spiritMotionSparks(level, offsetPosition, cyclingSpiritType);
                    sparkParticles.getBuilder()
                            .disableNoClip()
                            .setLifeDelay(lifeDelay)
                            .multiplyLifetime(0.75f)
                            .modifyScaleData(d -> d.multiplyValue(1f));
                    sparkParticles.getBloomBuilder()
                            .disableNoClip()
                            .setLifeDelay(lifeDelay)
                            .multiplyLifetime(0.75f)
                            .modifyTransparencyData(d -> d.multiplyValue(1.25f));
                    sparkParticles.spawnParticles();
                }
                if (random.nextFloat() < 0.85f) {
                    var lightSpecs = SpiritLightSpecs.spiritLightSpecs(level, offsetPosition, cyclingSpiritType);
                    lightSpecs.getBuilder()
                            .disableNoClip()
                            .setLifeDelay(lifeDelay)
                            .modifyScaleData(d -> d.multiplyValue(1.5f));
                    lightSpecs.getBloomBuilder()
                            .disableNoClip()
                            .setLifeDelay(lifeDelay)
                            .modifyTransparencyData(d -> d.multiplyValue(1.25f));
                    lightSpecs.spawnParticles();
                }
            }
        }
    }

    public static void repairItemParticles(RepairPylonCoreBlockEntity pylon, IMalumSpecialItemAccessPoint holder, MalumNetworkedParticleEffectColorData colorData) {
        SpiritLike activeSpiritType = getCentralSpiritType(pylon);
        if (activeSpiritType == null) {
            return;
        }
        var level = pylon.getLevel();
//        repairItemParticles(level, activeSpiritType, pylon.getItemPos(), colorData);
        repairItemParticles(level, activeSpiritType, holder.getItemPos(), colorData);
    }
    public static void repairItemParticles(Level level, SpiritLike activeSpiritType, Vec3 itemPos, MalumNetworkedParticleEffectColorData colorData) {
        long gameTime = level.getGameTime();
        var random = level.random;
        for (int i = 0; i < 2; i++) {
            SpiritLightSpecs.coolLookingShinyThing(level, itemPos, activeSpiritType);
        }
        for (int i = 0; i < 24; i++) {
            int lifeDelay = i / 8;
            SpiritArcanaType cyclingSpiritType = colorData.getSpirit();
            float xVelocity = Easing.CUBIC_OUT.asWeighedRandom(random, -0.075f, 0.075f);
            float yVelocity = Easing.SINE_IN_OUT.asWeighedRandom(random, 0.2f, 0.5f);
            float zVelocity = Easing.CUBIC_OUT.asWeighedRandom(random, -0.075f, 0.075f);
            float gravityStrength = Easing.SINE_IN_OUT.asWeighedRandom(random, 0.75f, 1f);
            if (random.nextFloat() < 0.85f) {
                var sparkParticles = SparkParticleEffects.spiritMotionSparks(level, itemPos, cyclingSpiritType);
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
                var lightSpecs = SpiritLightSpecs.spiritLightSpecs(level, itemPos, cyclingSpiritType);
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
        for (int i = 0; i < 8; i++) {
            int finalI = i;
            Vec3 offsetPosition = VecHelper.rotatingRadialOffset(itemPos, 0.6f, i, 8, gameTime, 160);
            Consumer<WorldParticleBuilder> behavior = b -> b.addTickActor(p -> {
                if (level.getGameTime() > gameTime + finalI * 4 && level.getGameTime() < gameTime + (finalI + 4) * 4) {
                    p.setParticleSpeed(p.getParticleSpeed().add(0, 0.015f, 0));
                }
            });

            var lightSpecs = spiritLightSpecs(level, offsetPosition, activeSpiritType);
            lightSpecs.getBuilder()
                    .act(behavior)
                    .modifyColorData(d -> d.multiplyCoefficient(0.35f))
                    .modifyScaleData(d -> d.multiplyValue(2f).multiplyCoefficient(0.9f))
                    .modifyTransparencyData(d -> d.multiplyCoefficient(0.9f))
                    .multiplyLifetime(1.5f)
                    .setLifetimeModifier(l -> l + finalI * 2);
            lightSpecs.getBloomBuilder()
                    .act(behavior)
                    .modifyColorData(d -> d.multiplyCoefficient(0.35f))
                    .modifyScaleData(d -> d.multiplyValue(2f).multiplyCoefficient(0.9f))
                    .modifyTransparencyData(d -> d.multiplyCoefficient(0.9f))
                    .multiplyLifetime(1.5f)
                    .setLifetimeModifier(l -> (int)(l + finalI * 2.5f));
            lightSpecs.spawnParticles();
        }
    }
}
