package artifacts.component.itemdamage;

import artifacts.config.value.Value;
import artifacts.config.value.ValueTypes;
import artifacts.registry.ModDataComponents;
import artifacts.util.ModCodecs;
import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import io.netty.buffer.ByteBuf;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.tags.TagKey;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;

import java.util.Optional;

// TODO:
//  - consider using holderSet instead of tag key here and elsewhere
public record DamageOnBlockMined(Value<Integer> itemDamage, Optional<TagKey<Block>> tag) {

    public static final Codec<DamageOnBlockMined> CODEC = RecordCodecBuilder.create(instance -> instance.group(
            ValueTypes.itemDamageField(1).forGetter(DamageOnBlockMined::itemDamage),
            TagKey.codec(Registries.BLOCK).optionalFieldOf("tag").forGetter(DamageOnBlockMined::tag)
    ).apply(instance, DamageOnBlockMined::new));

    public static final StreamCodec<ByteBuf, DamageOnBlockMined> STREAM_CODEC = StreamCodec.composite(
            ValueTypes.DURATION.streamCodec(),
            DamageOnBlockMined::itemDamage,
            ByteBufCodecs.optional(ModCodecs.tagKeyStreamCodec(Registries.BLOCK)),
            DamageOnBlockMined::tag,
            DamageOnBlockMined::new
    );

    public static void onBlockBroken(LivingEntity entity, BlockState state) {
        ModDataComponents.DAMAGE_ON_BLOCK_MINED.on(entity)
                .filter(component -> component.tag().isEmpty() || state.is(component.tag().get()))
                .iterate((component, slot) -> slot.hurtAndBreak(component.itemDamage().get()));
    }
}
