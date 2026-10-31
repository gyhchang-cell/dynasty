package com.sammy.malum.visual_effects.block;

import com.sammy.malum.client.*;
import com.sammy.malum.common.block.curiosities.sorcery.runic_workbench.*;
import com.sammy.malum.registry.common.*;
import com.sammy.malum.registry.common.magic.*;
import com.sammy.malum.visual_effects.SpiritLightSpecs;
import com.sammy.malum.visual_effects.networked.*;
import com.sammy.malum.visual_effects.networked.runic_workbench.*;
import net.minecraft.util.*;
import net.minecraft.world.level.*;
import net.minecraft.world.phys.*;
import team.lodestar.lodestone.helpers.*;
import team.lodestar.lodestone.modules.core.easing.Easing;
import team.lodestar.lodestone.modules.rendering.particle.standard.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.data.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.world.behaviors.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.world.options.*;

import static com.sammy.malum.visual_effects.SpiritLightSpecs.*;

public class RunicWorkbenchParticleEffects {

    public static void craftRuneParticles(Level level, RunicWorkbenchBlockEntity workbench, MalumNetworkedParticleEffectColorData colorData, RunicWorkbenchEffectData extraData) {
        long gameTime = level.getGameTime();
        var rand = level.random;
        Vec3 targetPos = workbench.getItemPos();
        for (int i = 0; i < 2; i++) {
            var spirit = colorData.getSpirit();
            SpiritLightSpecs.coolLookingShinyThing(level, targetPos, spirit);
        }
        for (int i = 0; i < 6; i++) {
            int lifeDelay = 2 + i;
            var scaleData = GenericParticleData.create(0.1f, Easing.SINE_IN_OUT.asWeighedRandom(rand, 0.5f, 0.6f) + i * 0.05f, 0.5f)
                    .setEasing(Easing.SINE_OUT, Easing.SINE_IN)
                    .setCoefficient(Easing.SINE_IN_OUT.asWeighedRandom(rand, 1.5f, 2f)).build();
            var builder = SpiritBasedParticleBuilder.createSpirit(MalumParticles.SQUARE.get())
                    .setSpirit(colorData.getSpirit())
                    .setBehavior(DirectionalParticleBehavior.directional(new Vec3(0, 1, 0)))
                    .setTransparencyData(GenericParticleData.create(0.7f, 0f).setEasing(Easing.SINE_IN_OUT).build())
                    .setSpritePicker(SimpleParticleOptions.ParticleSpritePicker.WITH_AGE)
                    .setScaleData(scaleData)
                    .setLifetime(15)
                    .setLifeDelay(lifeDelay)
                    .enableNoClip();
            if (i % 2 == 0) {
                builder.act(b -> b.setColorData(b.getColorData().invert().build()));
            }
            builder
                    .spawn(level, targetPos.x, targetPos.y, targetPos.z)
                    .setBehavior(BillboardParticleBehavior.INSTANCE)
                    .setLifetime(8)
                    .setLifeDelay((int) (lifeDelay * 1.5f))
                    .modifyScaleData(d -> d.multiplyValue(1.25f).multiplyCoefficient(0.9f))
                    .modifyTransparencyData(d -> d.multiplyValue(0.6f))
                    .spawn(level, targetPos.x, targetPos.y, targetPos.z);
        }

        for (int i = 0; i < 4; i++) {
            int lifeDelay = 18;
            var scaleData = GenericParticleData.create(0.2f, Easing.SINE_IN_OUT.asWeighedRandom(rand, 0.3f, 0.4f) + i * 0.1f, 0.3f)
                    .setEasing(Easing.SINE_OUT, Easing.SINE_IN)
                    .setCoefficient(Easing.SINE_IN_OUT.asWeighedRandom(rand, 1.5f, 2f)).build();
            var builder = SpiritBasedParticleBuilder.createSpirit(MalumParticles.SQUARE.get())
                    .setSpirit(colorData.getSpirit())
                    .setBehavior(DirectionalParticleBehavior.directional(new Vec3(0, 1, 0)))
                    .setTransparencyData(GenericParticleData.create(0.9f, 0f).setEasing(Easing.EXPO_IN).build())
                    .setSpritePicker(SimpleParticleOptions.ParticleSpritePicker.WITH_AGE)
                    .setScaleData(scaleData)
                    .setLifetime(15)
                    .setLifeDelay(lifeDelay)
                    .enableNoClip();
            if (i % 2 == 0) {
                builder.act(b -> b.setColorData(b.getColorData().invert().build()));
            }
            builder
                    .spawn(level, targetPos.x, targetPos.y, targetPos.z)
                    .setBehavior(BillboardParticleBehavior.INSTANCE)
                    .setLifetime(10)
                    .modifyScaleData(d -> d.multiplyValue(1.25f).multiplyCoefficient(0.9f))
                    .modifyTransparencyData(d -> d.multiplyValue(0.6f))
                    .spawn(level, targetPos.x, targetPos.y, targetPos.z);
        }

        for (int i = 0; i < 32; i++) {
            var spirit = colorData.getSpirit();
            Vec3 offsetPosition = VecHelper.rotatingRadialOffset(targetPos, 0.6f, i, 16, gameTime, 160);
            var lightSpecs = spiritLightSpecs(level, offsetPosition, spirit);
            int lifeDelay = i / 2;
            if (i % 2 == 0) {
                lightSpecs.getBuilder().act(b -> b.setColorData(b.getColorData().invert().build()));
                lightSpecs.getBloomBuilder().act(b -> b.setColorData(b.getColorData().invert().build()));
            }

            lightSpecs.getBuilder()
                    .setMotion(0, 0.1f, 0)
                    .modifyColorData(d -> d.multiplyCoefficient(0.35f))
                    .modifyScaleData(d -> d.multiplyValue(2f).multiplyCoefficient(0.9f))
                    .modifyTransparencyData(d -> d.multiplyCoefficient(0.9f))
                    .setLifetime(10)
                    .setLifeDelay(4+ lifeDelay);
            lightSpecs.getBloomBuilder()
                    .setMotion(0, 0.1f, 0)
                    .modifyColorData(d -> d.multiplyCoefficient(0.35f))
                    .modifyScaleData(d -> d.multiplyValue(1.6f).multiplyCoefficient(0.9f))
                    .modifyTransparencyData(d -> d.multiplyCoefficient(0.9f))
                    .setLifetime(10)
                    .setLifeDelay(4+ lifeDelay);
            lightSpecs.spawnParticles();
        }
    }

    public static void craftItemParticles(Level level, RunicWorkbenchBlockEntity workbench, RunicWorkbenchEffectData extraData) {
        var colorData = new MalumNetworkedParticleEffectColorData(MalumSpiritTypes.ARCANE_SPIRIT);
        long gameTime = level.getGameTime();
        Vec3 targetPos = workbench.getItemPos();

        for (int i = 0; i < 2; i++) {
            var spirit = colorData.getSpirit();
            var lightSpecs = spiritLightSpecs(level, targetPos, spirit, new WorldParticleOptions(MalumParticles.LIGHT_SPEC.get()));
            lightSpecs.getBuilder()
                    .multiplyLifetime(0.6f)
                    .modifyColorData(d -> d.multiplyCoefficient(0.5f))
                    .modifyScaleData(d -> d.multiplyValue(6f))
                    .modifyTransparencyData(d -> d.multiplyValue(3f))
                    .setLifeDelay(20);
            lightSpecs.getBloomBuilder()
                    .multiplyLifetime(0.6f)
                    .modifyColorData(d -> d.multiplyCoefficient(0.5f))
                    .modifyScaleData(d -> d.multiplyValue(4f))
                    .modifyTransparencyData(d -> d.multiplyValue(3f))
                    .setLifeDelay(20);
            lightSpecs.spawnParticles();
        }
        for (int i = 0; i < 32; i++) {
            var spirit = colorData.getSpirit();
            float delta = i / 32f;
            int lifeDelay = Mth.floor(delta*20);
            Vec3 offsetPosition = VecHelper.rotatingRadialOffset(targetPos, Mth.lerp(delta, 0.7f, 0.35f), i, 16, gameTime, 160);
            var lightSpecs = spiritLightSpecs(level, offsetPosition, spirit);
            if (i % 2 == 0) {
                lightSpecs.getBuilder().act(b -> b.setColorData(b.getColorData().invert().build()));
                lightSpecs.getBloomBuilder().act(b -> b.setColorData(b.getColorData().invert().build()));
            }

            lightSpecs.getBuilder()
                    .modifyColorData(d -> d.multiplyCoefficient(0.35f))
                    .modifyScaleData(d -> d.multiplyValue(2f).multiplyCoefficient(0.9f))
                    .modifyTransparencyData(d -> d.multiplyCoefficient(0.9f))
                    .setLifeDelay(lifeDelay);
            lightSpecs.getBloomBuilder()
                    .modifyColorData(d -> d.multiplyCoefficient(0.35f))
                    .modifyScaleData(d -> d.multiplyValue(1.2f).multiplyCoefficient(0.9f))
                    .modifyTransparencyData(d -> d.multiplyCoefficient(0.4f))
                    .setLifeDelay(lifeDelay);
            lightSpecs.spawnParticles();
        }
    }
}