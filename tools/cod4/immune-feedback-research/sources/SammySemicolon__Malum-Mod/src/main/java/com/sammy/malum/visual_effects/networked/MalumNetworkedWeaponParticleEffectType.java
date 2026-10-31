package com.sammy.malum.visual_effects.networked;

import com.sammy.malum.common.item.spirit.*;
import com.sammy.malum.core.systems.spirit.SpiritLike;
import io.netty.buffer.*;
import net.minecraft.core.*;
import net.minecraft.network.codec.*;
import net.minecraft.server.level.*;
import net.minecraft.util.*;
import net.minecraft.world.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.item.*;
import net.minecraft.world.level.*;
import net.minecraft.world.phys.*;
import team.lodestar.lodestone.systems.network.*;
import team.lodestar.lodestone.systems.network.WeaponParticleEffectType.*;
import team.lodestar.lodestone.systems.network.particle.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.data.color.*;

import java.awt.*;
import java.util.List;
import java.util.*;
import java.util.function.*;

public abstract class MalumNetworkedWeaponParticleEffectType<T extends WeaponParticleEffectData> extends WeaponParticleEffectType<T> {
    public MalumNetworkedWeaponParticleEffectType(String id) {
        super(id);
    }

    @Override
    public Optional<StreamCodec<ByteBuf, ? extends NetworkedParticleEffectColorData>> getColorCodec() {
        return Optional.of(MalumNetworkedParticleEffectColorData.STREAM_CODEC);
    }

    @Override
    protected void castAndAct(Level level, RandomSource random, NetworkedParticleEffectPositionData positionData, NetworkedParticleEffectColorData colorData, NetworkedParticleEffectExtraData extraData) {
        act(level, random, positionData, (MalumNetworkedParticleEffectColorData) colorData, (T) extraData);
    }

    public abstract void act(Level level, RandomSource random, NetworkedParticleEffectPositionData positionData, MalumNetworkedParticleEffectColorData colorData, T extraData);

    @Override
    public final void act(Level level, RandomSource random, NetworkedParticleEffectPositionData positionData, NetworkedParticleEffectColorData colorData, T extraData) {
    }

    @Override
    public MalumWeaponParticleEffectBuilder<T> createEffect(BlockPos position) {
        return createEffect().at(position);
    }

    @Override
    public MalumWeaponParticleEffectBuilder<T> createEffect(Vec3 position) {
        return createEffect().at(position);
    }

    @Override
    public MalumWeaponParticleEffectBuilder<T> createEffect(Entity target) {
        return createEffect().at(target);
    }

    @Override
    public MalumWeaponParticleEffectBuilder<T> createEffect() {
        return new MalumWeaponParticleEffectBuilder<>(this);
    }

    public static class MalumWeaponParticleEffectBuilder<T extends WeaponParticleEffectData> extends WeaponParticleEffectType.WeaponParticleEffectBuilder<T> {
        public MalumWeaponParticleEffectBuilder(WeaponParticleEffectType<T> type) {
            super(type);
        }

        public MalumWeaponParticleEffectBuilder<T> color(ItemStack stack) {
            if (stack.getItem() instanceof ISpiritAffiliatedItem spiritAffiliatedItem) {
                var definingSpiritType = spiritAffiliatedItem.getDefiningSpiritType(stack);
                if (definingSpiritType == null) {
                    return this;
                }
                return color(new MalumNetworkedParticleEffectColorData(definingSpiritType));
            }
            return this;
        }

        public final MalumWeaponParticleEffectBuilder<T> color(SpiritLike... spiritTypes) {
            return color(new MalumNetworkedParticleEffectColorData(spiritTypes));
        }

        @Override
        public MalumWeaponParticleEffectBuilder<T> color(NetworkedParticleEffectColorData color) {
            if (color instanceof MalumNetworkedParticleEffectColorData malumColor) {
                return (MalumWeaponParticleEffectBuilder<T>) super.color(malumColor);
            }
            return (MalumWeaponParticleEffectBuilder<T>)super.color(MalumNetworkedParticleEffectColorData.fromColors(color.getColors()));
        }

        @Override
        public MalumWeaponParticleEffectBuilder<T> originatesFrom(Entity source) {
            return (MalumWeaponParticleEffectBuilder<T>)super.originatesFrom(source);
        }

        @Override
        public MalumWeaponParticleEffectBuilder<T> targets(Entity target) {
            return (MalumWeaponParticleEffectBuilder<T>)super.targets(target);
        }

        @Override
        public MalumWeaponParticleEffectBuilder<T> aimedAt(Vec3 direction) {
            return (MalumWeaponParticleEffectBuilder<T>)super.aimedAt(direction);
        }

        @Override
        public MalumWeaponParticleEffectBuilder<T> tiedToTarget() {
            return (MalumWeaponParticleEffectBuilder<T>)super.tiedToTarget();
        }

        @Override
        public MalumWeaponParticleEffectBuilder<T> mirroredRandomly(RandomSource random) {
            return (MalumWeaponParticleEffectBuilder<T>)super.mirroredRandomly(random);
        }

        @Override
        public MalumWeaponParticleEffectBuilder<T> mirrored() {
            return (MalumWeaponParticleEffectBuilder<T>)super.mirrored();
        }

        @Override
        public MalumWeaponParticleEffectBuilder<T> mirrored(boolean isMirrored) {
            return (MalumWeaponParticleEffectBuilder<T>)super.mirrored(isMirrored);
        }

        @Override
        public MalumWeaponParticleEffectBuilder<T> randomSlashRotation(RandomSource random) {
            return (MalumWeaponParticleEffectBuilder<T>)super.randomSlashRotation(random);
        }

        @Override
        public MalumWeaponParticleEffectBuilder<T> verticalSlashRotation() {
            return (MalumWeaponParticleEffectBuilder<T>)super.verticalSlashRotation();
        }

        @Override
        public MalumWeaponParticleEffectBuilder<T> slashRotation(float slashRotation) {
            return (MalumWeaponParticleEffectBuilder<T>)super.slashRotation(slashRotation);
        }

        @Override
        public MalumWeaponParticleEffectBuilder<T> setOffsetsFromHand(InteractionHand hand) {
            return (MalumWeaponParticleEffectBuilder<T>)super.setOffsetsFromHand(hand);
        }

        @Override
        public MalumWeaponParticleEffectBuilder<T> horizontalOffset(float horizontalOffset) {
            return (MalumWeaponParticleEffectBuilder<T>)super.horizontalOffset(horizontalOffset);
        }

        @Override
        public MalumWeaponParticleEffectBuilder<T> forwardOffset(float forwardOffset) {
            return (MalumWeaponParticleEffectBuilder<T>)super.forwardOffset(forwardOffset);
        }

        @Override
        public MalumWeaponParticleEffectBuilder<T> upwardOffset(float upwardOffset) {
            return (MalumWeaponParticleEffectBuilder<T>)super.upwardOffset(upwardOffset);
        }

        @Override
        public MalumWeaponParticleEffectBuilder<T> randomOffset(RandomSource random, float min, float max) {
            return (MalumWeaponParticleEffectBuilder<T>) super.randomOffset(random, min, max);
        }

        @Override
        public MalumWeaponParticleEffectBuilder<T> absoluteOffset(Vec3 absoluteOffset) {
            return (MalumWeaponParticleEffectBuilder<T>)super.absoluteOffset(absoluteOffset);
        }

        @Override
        public MalumWeaponParticleEffectBuilder<T> deviation(float horizontalDeviation, float verticalDeviation, float deviationAngle) {
            return (MalumWeaponParticleEffectBuilder<T>) super.deviation(horizontalDeviation, verticalDeviation, deviationAngle);
        }

        @Override
        public MalumWeaponParticleEffectBuilder<T> deviation(float horizontalDeviation, float verticalDeviation) {
            return (MalumWeaponParticleEffectBuilder<T>) super.deviation(horizontalDeviation, verticalDeviation);
        }

        @Override
        public MalumWeaponParticleEffectBuilder<T> deviation(float deviation) {
            return (MalumWeaponParticleEffectBuilder<T>) super.deviation(deviation);
        }

        @Override
        public MalumWeaponParticleEffectBuilder<T> horizontalDeviation(float horizontalDeviation) {
            return (MalumWeaponParticleEffectBuilder<T>)super.horizontalDeviation(horizontalDeviation);
        }

        @Override
        public MalumWeaponParticleEffectBuilder<T> verticalDeviation(float verticalDeviation) {
            return (MalumWeaponParticleEffectBuilder<T>)super.verticalDeviation(verticalDeviation);
        }

        @Override
        public MalumWeaponParticleEffectBuilder<T> randomDeviationAngle(RandomSource random) {
            return (MalumWeaponParticleEffectBuilder<T>) super.randomDeviationAngle(random);
        }

        @Override
        public MalumWeaponParticleEffectBuilder<T> deviationAngle(float deviationAngle) {
            return (MalumWeaponParticleEffectBuilder<T>)super.deviationAngle(deviationAngle);
        }

        @Override
        public MalumWeaponParticleEffectBuilder<T> spawn(ServerLevel level) {
            return (MalumWeaponParticleEffectBuilder<T>)super.spawn(level);
        }

        @Override
        public MalumWeaponParticleEffectBuilder<T> at(BlockPos position) {
            return (MalumWeaponParticleEffectBuilder<T>)super.at(position);
        }

        @Override
        public MalumWeaponParticleEffectBuilder<T> at(Vec3 position) {
            return (MalumWeaponParticleEffectBuilder<T>)super.at(position);
        }

        @Override
        public MalumWeaponParticleEffectBuilder<T> at(Entity target) {
            return (MalumWeaponParticleEffectBuilder<T>)super.at(target);
        }

        @Override
        public MalumWeaponParticleEffectBuilder<T> at(NetworkedParticleEffectPositionData position) {
            return (MalumWeaponParticleEffectBuilder<T>)super.at(position);
        }

        @Override
        public MalumWeaponParticleEffectBuilder<T> color(Color color) {
            return (MalumWeaponParticleEffectBuilder<T>)super.color(color);
        }

        @Override
        public MalumWeaponParticleEffectBuilder<T> color(ColorParticleDataWrapper color) {
            return (MalumWeaponParticleEffectBuilder<T>)super.color(color);
        }

        @Override
        public MalumWeaponParticleEffectBuilder<T> color(List<? extends ColorParticleDataWrapper> colors) {
            return (MalumWeaponParticleEffectBuilder<T>)super.color(colors);
        }

        @Override
        public MalumWeaponParticleEffectBuilder<T> customData(T extra) {
            return (MalumWeaponParticleEffectBuilder<T>) super.customData(extra);
        }

        @Override
        public MalumWeaponParticleEffectBuilder<T> spawn(Consumer<NetworkedParticleEffectPayload> sender) {
            return (MalumWeaponParticleEffectBuilder<T>) super.spawn(sender);
        }
    }
}
