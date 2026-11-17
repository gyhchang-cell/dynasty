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
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;

import java.util.Optional;

public record DamageOnHurt(Value<Integer> itemDamage, Optional<TagKey<DamageType>> tag) {

    public static final Codec<DamageOnHurt> CODEC = RecordCodecBuilder.create(instance -> instance.group(
            ValueTypes.itemDamageField(1).forGetter(DamageOnHurt::itemDamage),
            TagKey.codec(Registries.DAMAGE_TYPE).optionalFieldOf("tag").forGetter(DamageOnHurt::tag)
    ).apply(instance, DamageOnHurt::new));

    public static final StreamCodec<ByteBuf, DamageOnHurt> STREAM_CODEC = StreamCodec.composite(
            ValueTypes.DURATION.streamCodec(),
            DamageOnHurt::itemDamage,
            ByteBufCodecs.optional(ModCodecs.tagKeyStreamCodec(Registries.DAMAGE_TYPE)),
            DamageOnHurt::tag,
            DamageOnHurt::new
    );

    public static void onLivingDamaged(LivingEntity entity, DamageSource damageSource) {
        // TODO: artifacts not worn by players aren't damaged, is this consistent with other damage rules?
        // I think I did it this way because the cross necklace only affects players, but this may not be the case with other items that use this rule
        if (entity instanceof Player player && !player.level().isClientSide()) {
            ModDataComponents.DAMAGE_ON_HURT.on(entity)
                    .filter(component -> component.tag().isEmpty() || damageSource.is(component.tag().get()))
                    .iterate((component, slot) -> slot.hurtAndBreak(component.itemDamage().get()));
        }
    }
}
