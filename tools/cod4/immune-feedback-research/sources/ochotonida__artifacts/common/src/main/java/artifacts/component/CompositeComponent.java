package artifacts.component;

import com.mojang.serialization.Codec;
import io.netty.buffer.ByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;

import java.util.List;

public record CompositeComponent<ENTRY>(List<ENTRY> entries) {

    public static <ENTRY> Codec<CompositeComponent<ENTRY>> codec(Codec<ENTRY> entryCodec) {
        return entryCodec.listOf().xmap(CompositeComponent::new, CompositeComponent::entries);
    }

    public static <ENTRY, B extends ByteBuf> StreamCodec<B, CompositeComponent<ENTRY>> streamCodec(StreamCodec<B, ENTRY> entryCodec) {
        return ByteBufCodecs.<B, ENTRY>list().apply(entryCodec).map(CompositeComponent::new, CompositeComponent::entries);
    }

    @SafeVarargs
    public static <ENTRY> CompositeComponent<ENTRY> of(ENTRY... entries) {
        return new CompositeComponent<>(List.of(entries));
    }
}
