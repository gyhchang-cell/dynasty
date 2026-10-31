package artifacts.component;

import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.minecraft.core.Holder;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;

public record Equipable(
        Holder<SoundEvent> equipSound,
        boolean swappable
) {

    public static final Codec<Equipable> CODEC = RecordCodecBuilder.create(
            instance -> instance.group(
                            SoundEvent.CODEC.optionalFieldOf("equip_sound", SoundEvents.ARMOR_EQUIP_GENERIC).forGetter(Equipable::equipSound),
                            Codec.BOOL.optionalFieldOf("swappable", true).forGetter(Equipable::swappable)
                    )
                    .apply(instance, Equipable::new)
    );

    public static final StreamCodec<RegistryFriendlyByteBuf, Equipable> STREAM_CODEC = StreamCodec.composite(
            SoundEvent.STREAM_CODEC,
            Equipable::equipSound,
            ByteBufCodecs.BOOL,
            Equipable::swappable,
            Equipable::new
    );
}
