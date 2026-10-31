package artifacts.component;

import com.mojang.serialization.Codec;
import io.netty.buffer.ByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.util.ByIdMap;
import net.minecraft.util.StringRepresentable;

import java.util.function.IntFunction;

public enum ToggleIdentifier implements StringRepresentable {
    CHARM_OF_SHRINKING(0, "charm_of_shrinking"),
    CHARM_OF_SINKING(1, "charm_of_sinking"),
    NIGHT_VISION_GOGGLES(2, "night_vision_goggles"),
    SCARF_OF_INVISIBILITY(3, "scarf_of_invisibility"),
    UNIVERSAL_ATTRACTOR(4, "universal_attractor");

    private final int id;
    private final String name;

    ToggleIdentifier(int id, String name) {
        this.id = id;
        this.name = name;
    }

    public static final Codec<ToggleIdentifier> CODEC = StringRepresentable.fromValues(ToggleIdentifier::values);
    public static final IntFunction<ToggleIdentifier> BY_ID = ByIdMap.continuous(toggleIdentifier -> toggleIdentifier.id, values(), ByIdMap.OutOfBoundsStrategy.ZERO);
    public static final StreamCodec<ByteBuf, ToggleIdentifier> STREAM_CODEC = ByteBufCodecs.idMapper(BY_ID, rarity -> rarity.id);

    @Override
    public String getSerializedName() {
        return toString();
    }

    @Override
    public String toString() {
        return name;
    }
}
