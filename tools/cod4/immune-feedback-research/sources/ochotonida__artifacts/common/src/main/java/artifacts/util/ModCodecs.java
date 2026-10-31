package artifacts.util;

import com.mojang.datafixers.util.Function7;
import com.mojang.datafixers.util.Pair;
import com.mojang.serialization.Codec;
import com.mojang.serialization.DataResult;
import com.mojang.serialization.DynamicOps;
import io.netty.buffer.ByteBuf;
import net.minecraft.core.Registry;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.tags.TagKey;

import java.util.function.Function;

public class ModCodecs {

    public static <T> StreamCodec<ByteBuf, TagKey<T>> tagKeyStreamCodec(ResourceKey<? extends Registry<T>> registry) {
        return Identifier.STREAM_CODEC.map(
                id -> TagKey.create(registry, id),
                TagKey::location
        );
    }

    public static <T> Codec<T> xorAlternative(final Codec<T> codec, final Codec<T> alternative) {
        return new XorAlternativeCodec<>(codec, alternative);
    }

    // see NeoForgeExtraCodecs
    private record XorAlternativeCodec<T>(Codec<T> codec, Codec<T> alternative) implements Codec<T> {
        @Override
        public <T1> DataResult<Pair<T, T1>> decode(final DynamicOps<T1> ops, final T1 input) {
            final DataResult<Pair<T, T1>> result = codec.decode(ops, input);
            if (result.error().isEmpty()) {
                return result;
            } else {
                return alternative.decode(ops, input);
            }
        }

        @Override
        public <T1> DataResult<T1> encode(final T input, final DynamicOps<T1> ops, final T1 prefix) {
            final DataResult<T1> result = codec.encode(input, ops, prefix);
            if (result.error().isEmpty()) {
                return result;
            } else {
                return alternative.encode(input, ops, prefix);
            }
        }

        @Override
        public String toString() {
            return "Alternative[" + codec + ", " + alternative + "]";
        }
    }

    public static <B, C, T1, T2, T3, T4, T5, T6, T7> StreamCodec<B, C> composite(
            final StreamCodec<? super B, T1> codec1,
            final Function<C, T1> getter1,
            final StreamCodec<? super B, T2> codec2,
            final Function<C, T2> getter2,
            final StreamCodec<? super B, T3> codec3,
            final Function<C, T3> getter3,
            final StreamCodec<? super B, T4> codec4,
            final Function<C, T4> getter4,
            final StreamCodec<? super B, T5> codec5,
            final Function<C, T5> getter5,
            final StreamCodec<? super B, T6> codec6,
            final Function<C, T6> getter6,
            final StreamCodec<? super B, T7> codec7,
            final Function<C, T7> getter7,
            final Function7<T1, T2, T3, T4, T5, T6, T7, C> f) {
        return new StreamCodec<>() {
            @Override
            public C decode(B b) {
                T1 t1 = codec1.decode(b);
                T2 t2 = codec2.decode(b);
                T3 t3 = codec3.decode(b);
                T4 t4 = codec4.decode(b);
                T5 t5 = codec5.decode(b);
                T6 t6 = codec6.decode(b);
                T7 t7 = codec7.decode(b);
                return f.apply(t1, t2, t3, t4, t5, t6, t7);
            }

            @Override
            public void encode(B b, C c) {
                codec1.encode(b, getter1.apply(c));
                codec2.encode(b, getter2.apply(c));
                codec3.encode(b, getter3.apply(c));
                codec4.encode(b, getter4.apply(c));
                codec5.encode(b, getter5.apply(c));
                codec6.encode(b, getter6.apply(c));
                codec7.encode(b, getter7.apply(c));
            }
        };
    }
}
