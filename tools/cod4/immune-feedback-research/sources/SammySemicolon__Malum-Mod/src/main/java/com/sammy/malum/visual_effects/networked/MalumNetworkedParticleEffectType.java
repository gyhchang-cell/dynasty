package com.sammy.malum.visual_effects.networked;

import com.sammy.malum.common.item.spirit.*;
import com.sammy.malum.core.systems.spirit.SpiritLike;
import io.netty.buffer.ByteBuf;
import net.minecraft.core.BlockPos;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.item.*;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import team.lodestar.lodestone.systems.network.particle.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.data.color.*;

import java.awt.*;
import java.util.List;
import java.util.Optional;
import java.util.function.Consumer;

public abstract class MalumNetworkedParticleEffectType<T extends NetworkedParticleEffectExtraData> extends NetworkedParticleEffectType<T> {
    public MalumNetworkedParticleEffectType(String id) {
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
    public MalumParticleEffectBuilder<T> createEffect(BlockPos position) {
        return createEffect().at(position);
    }

    @Override
    public MalumParticleEffectBuilder<T> createEffect(Vec3 position) {
        return createEffect().at(position);
    }

    @Override
    public MalumParticleEffectBuilder<T> createEffect(Entity target) {
        return createEffect().at(target);
    }

    @Override
    public MalumParticleEffectBuilder<T> createEffect() {
        return new MalumParticleEffectBuilder<>(this);
    }

    public static class MalumParticleEffectBuilder<T extends NetworkedParticleEffectExtraData> extends ParticleEffectBuilder<T> {

        public MalumParticleEffectBuilder(NetworkedParticleEffectType<T> type) {
            super(type);
        }

        public MalumParticleEffectBuilder<T> color(ItemStack stack) {
            var item = stack.getItem();
            if (item instanceof SpiritLike spirit) {
                return color(spirit);
            }
            if (item instanceof ISpiritAffiliatedItem spiritAffiliatedItem) {
                return color(new MalumNetworkedParticleEffectColorData(spiritAffiliatedItem.getDefiningSpiritType(stack)));
            }
            return this;
        }

        public MalumParticleEffectBuilder<T> color(SpiritLike... spiritTypes) {
            return color(new MalumNetworkedParticleEffectColorData(spiritTypes));
        }

        @Override
        public MalumParticleEffectBuilder<T> at(BlockPos position) {
            return(MalumParticleEffectBuilder<T>)super.at(position);
        }

        @Override
        public MalumParticleEffectBuilder<T> at(Vec3 position) {
            return(MalumParticleEffectBuilder<T>)super.at(position);
        }

        @Override
        public MalumParticleEffectBuilder<T> at(Entity target) {
            return(MalumParticleEffectBuilder<T>)super.at(target);
        }

        @Override
        public MalumParticleEffectBuilder<T> at(NetworkedParticleEffectPositionData position) {
            return(MalumParticleEffectBuilder<T>)super.at(position);
        }

        @Override
        public MalumParticleEffectBuilder<T> color(Color color) {
            return color(ColorParticleData.create(color).build());
        }

        @Override
        public MalumParticleEffectBuilder<T> color(ColorParticleDataWrapper color) {
            return color(MalumNetworkedParticleEffectColorData.fromColor(color));
        }

        @Override
        public MalumParticleEffectBuilder<T> color(List<? extends ColorParticleDataWrapper> colors) {
            return color(MalumNetworkedParticleEffectColorData.fromColors(colors));
        }

        @Override
        public MalumParticleEffectBuilder<T> color(NetworkedParticleEffectColorData color) {
            return(MalumParticleEffectBuilder<T>)super.color(color);
        }

        @Override
        public MalumParticleEffectBuilder<T> customData(T extra) {
            return(MalumParticleEffectBuilder<T>)super.customData(extra);
        }

        @Override
        public MalumParticleEffectBuilder<T> spawn(ServerLevel level) {
            return(MalumParticleEffectBuilder<T>)super.spawn(level);
        }

        @Override
        public MalumParticleEffectBuilder<T> spawn(Consumer<NetworkedParticleEffectPayload> sender) {
            return(MalumParticleEffectBuilder<T>)super.spawn(sender);
        }
    }
}
