package com.sammy.malum.visual_effects.networked;

import com.mojang.serialization.*;
import com.mojang.serialization.codecs.*;
import com.sammy.malum.core.systems.spirit.SpiritArcanaType;
import com.sammy.malum.core.systems.spirit.SpiritLike;
import io.netty.buffer.*;
import net.minecraft.network.codec.*;
import team.lodestar.lodestone.systems.network.particle.NetworkedParticleEffectColorData;
import team.lodestar.lodestone.modules.rendering.particle.standard.data.color.*;

import java.util.*;
import java.util.List;
import java.util.stream.Collectors;

public class MalumNetworkedParticleEffectColorData extends NetworkedParticleEffectColorData {

    public static final Codec<MalumNetworkedParticleEffectColorData> CODEC = RecordCodecBuilder.create(instance -> instance.group(
            ColorParticleData.CODEC.listOf().fieldOf("colors").forGetter(data -> data.colors),
            SpiritArcanaType.CODEC.listOf().fieldOf("spirits").forGetter(data -> data.spirits)
    ).apply(instance, MalumNetworkedParticleEffectColorData::new));

    public static final StreamCodec<ByteBuf, MalumNetworkedParticleEffectColorData> STREAM_CODEC = ByteBufCodecs.fromCodec(CODEC);

    private final List<SpiritArcanaType> spirits;
    public int colorCycleCounter;

    public static MalumNetworkedParticleEffectColorData fromSpirits(Collection<? extends SpiritLike> spirits) {
        return new MalumNetworkedParticleEffectColorData(Collections.emptyList(), spirits.stream().map(SpiritLike::getSpirit).collect(Collectors.toList()));
    }

    public static MalumNetworkedParticleEffectColorData fromColors(List<? extends ColorParticleDataWrapper> colors) {
        return new MalumNetworkedParticleEffectColorData(colors, Collections.emptyList());
    }

    public static MalumNetworkedParticleEffectColorData fromColor(ColorParticleDataWrapper color) {
        return fromColors(List.of(color));
    }

    public MalumNetworkedParticleEffectColorData(List<? extends ColorParticleDataWrapper> colors, List<? extends SpiritLike> spirits) {
        super(colors);
        this.spirits = spirits.isEmpty() ? Collections.emptyList() : spirits.stream().map(SpiritLike::getSpirit).toList();
    }

    public MalumNetworkedParticleEffectColorData(ColorParticleDataWrapper... colors) {
        this(List.of(colors), Collections.emptyList());
    }

    public MalumNetworkedParticleEffectColorData(SpiritLike... spirits) {
        this(Collections.emptyList(), List.of(spirits));
    }

    public boolean isSpiritBased() {
        return colors.isEmpty();
    }

    @Override
    public ColorParticleData getColor() {
        if (!spirits.isEmpty()) {
            return getSpirit().createColorData().build();
        }
        if (colors.size() == 1) {
            return colors.getFirst();
        }
        return colors.get(colorCycleCounter++ % colors.size());
    }

    public SpiritArcanaType getSpirit() {
        if (!colors.isEmpty()) {
            throw new IllegalArgumentException("Networked Particle Effect expected Spirit Color Data. Raw Color Data was passed instead, which is not supported.");
        }
        if (spirits.size() == 1) {
            return spirits.getFirst();
        }
        return spirits.get(colorCycleCounter++ % spirits.size());
    }
}