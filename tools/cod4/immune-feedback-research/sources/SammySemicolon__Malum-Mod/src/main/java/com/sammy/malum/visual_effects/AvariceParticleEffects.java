package com.sammy.malum.visual_effects;

import com.sammy.malum.MalumMod;
import com.sammy.malum.registry.common.magic.MalumSpiritTypes;
import com.sammy.malum.visual_effects.networked.MalumNetworkedParticleEffectColorData;
import net.minecraft.client.Minecraft;
import net.minecraft.core.BlockPos;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

import team.lodestar.lodestone.helpers.VecHelper;
import team.lodestar.lodestone.modules.core.easing.Easing;
import team.lodestar.lodestone.modules.rendering.particle.standard.data.GenericParticleData;
import team.lodestar.lodestone.modules.rendering.particle.standard.world.LodestoneWorldParticle;

import java.util.function.Consumer;

import static com.sammy.malum.visual_effects.SpiritLightSpecs.spiritLightSpecs;

public class AvariceParticleEffects {


    public static void avariceItemParticles(Level level, Entity entity) {
        if (level.getGameTime() % 8L == 0) {
            var center = entity.position().add(0, entity.getBbHeight() / 2f, 0);
            float width = entity.getBbWidth()*2f;
            float distance = width;
            if (entity instanceof ItemEntity item) {
                //Copied from ItemEntityRenderer
                var itemstack = item.getItem();
                var itemRenderer = Minecraft.getInstance().getItemRenderer();
                var bakedmodel = itemRenderer.getModel(itemstack, entity.level(), null, entity.getId());
                boolean shouldBob = net.neoforged.neoforge.client.extensions.common.IClientItemExtensions.of(itemstack).shouldBobAsEntity(itemstack);
                float f1 = shouldBob ? Mth.sin(((float)item.getAge()) / 10.0F + item.bobOffs) * 0.1F + 0.1F : 0;
                float f2 = bakedmodel.getTransforms().getTransform(ItemDisplayContext.GROUND).scale.y();
                center = center.add(0, f1 + 0.25f * f2, 0);
                distance = Mth.clampedLerp(0, width, item.age/20f);
            }

            for (int i = 0; i < 2; i++) {
                var angle = i + (level.getGameTime() % 80f) / 80f;
                int delay = Easing.SINE_IN_OUT.asWeighedRandom(MalumMod.RANDOM, 0, 4);
                var offsetCenter = VecHelper.radialOffset(center, distance, angle, 2);
                var lightSpecs = spiritLightSpecs(level, offsetCenter, MalumSpiritTypes.INFERNAL_SPIRIT);
                lightSpecs.getBuilder()
                        .setLifeDelay(delay)
                        .setRandomMotion(0.01f)
                        .multiplyLifetime(2.5f)
                        .setTransparencyData(GenericParticleData.create(0.4f, 0.9f, 0f).build());
                lightSpecs.getBloomBuilder()
                        .setLifeDelay(delay)
                        .setRandomMotion(0.01f)
                        .multiplyLifetime(1.5f)
                        .setTransparencyData(GenericParticleData.create(0.05f, 0.4f, 0f).build());
                lightSpecs.spawnParticles();
            }
        }
    }

    public static void avariceFortuneBlockEffect(Level level, MalumNetworkedParticleEffectColorData colorData, Vec3 position) {
        var random = level.random;
        var asBlockPos = new BlockPos((int) Math.round(position.x), (int) Math.round(position.y), (int) Math.round(position.z));
        for (int i = 0; i < 4; i++) {
            float xOffset = Mth.clamp(i%3, 0, 1) - 1f;
            float zOffset = Mth.clamp((i-1)%4, 0, 1) - 1f;
            float xMotion = (i%2) * (i > 1 ? 0.06f : -0.06f);
            float zMotion = ((i + 1) % 2) * (i > 1 ? -0.06f : 0.06f);
            var spirit = colorData.getSpirit();

            for (int j = 0; j < 2; j++) {
                var offsetPosition = new Vec3(asBlockPos.getX()+xOffset, asBlockPos.getY()+j-1f, asBlockPos.getZ()+zOffset);
                var toCenter = position.subtract(offsetPosition).normalize();

                var lightSpecs = spiritLightSpecs(level, offsetPosition, spirit);
                Consumer<LodestoneWorldParticle> tickBehavior = p -> {
                    var speed = p.getParticleSpeed();
                    p.setParticleSpeed(speed.lerp(toCenter, 0.2f).normalize().scale(speed.length()).scale(0.97f));
                };
                lightSpecs.getBuilder()
                        .multiplyLifetime(1.5f)
                        .addTickActor(tickBehavior)
                        .setMotion(xMotion, 0, zMotion)
                        .setTransparencyData(GenericParticleData.create(0.2f, 0.8f, 0f).build())
                        .modifyScaleData(d -> d.multiplyValue(Easing.SINE_IN_OUT.asWeighedRandom(random, 1f, 2f)));
                lightSpecs.getBloomBuilder()
                        .multiplyLifetime(0.75f)
                        .addTickActor(tickBehavior)
                        .setMotion(xMotion, 0, zMotion)
                        .setTransparencyData(GenericParticleData.create(0.05f, 0.35f, 0f).build())
                        .modifyScaleData(d -> d.multiplyValue(Easing.SINE_IN_OUT.asWeighedRandom(random, 0.5f, 1f)));
                lightSpecs.spawnParticles();
            }
        }
    }
}
