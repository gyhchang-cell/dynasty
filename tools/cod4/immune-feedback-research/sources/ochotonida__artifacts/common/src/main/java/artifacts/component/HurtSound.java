package artifacts.component;

import artifacts.config.value.Value;
import artifacts.config.value.ValueTypes;
import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.minecraft.core.Holder;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.sounds.SoundEvent;

public record HurtSound(Holder<SoundEvent> soundEvent, Value<Boolean> enabled) {

    public static final Codec<HurtSound> CODEC = RecordCodecBuilder.create(instance -> instance.group(
            BuiltInRegistries.SOUND_EVENT.holderByNameCodec().fieldOf("sound").forGetter(HurtSound::soundEvent),
            ValueTypes.BOOLEAN.codec().optionalFieldOf("enabled", Value.of(true)).forGetter(HurtSound::enabled)
    ).apply(instance, HurtSound::new));

    public static final StreamCodec<RegistryFriendlyByteBuf, HurtSound> STREAM_CODEC = StreamCodec.composite(
            ByteBufCodecs.holderRegistry(Registries.SOUND_EVENT),
            HurtSound::soundEvent,
            ValueTypes.BOOLEAN.streamCodec(),
            HurtSound::enabled,
            HurtSound::new
    );
}
