package artifacts.component.itemdamage;

import artifacts.component.ability.EntityCondition;
import artifacts.config.value.Value;
import artifacts.config.value.ValueTypes;
import artifacts.registry.ModDataComponents;
import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import io.netty.buffer.ByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.world.entity.LivingEntity;

public record DamageOverTime(Value<Double> damagePerSecond, EntityCondition condition) {

    public static final Codec<DamageOverTime> CODEC = RecordCodecBuilder.create(instance -> instance.group(
            ValueTypes.NON_NEGATIVE_DOUBLE.codec().fieldOf("damage_per_second").forGetter(DamageOverTime::damagePerSecond),
            EntityCondition.CODEC.optionalFieldOf("condition", EntityCondition.ALWAYS).forGetter(DamageOverTime::condition)
    ).apply(instance, DamageOverTime::new));

    public static final StreamCodec<ByteBuf, DamageOverTime> STREAM_CODEC = StreamCodec.composite(
            ValueTypes.NON_NEGATIVE_DOUBLE.streamCodec(),
            DamageOverTime::damagePerSecond,
            EntityCondition.STREAM_CODEC,
            DamageOverTime::condition,
            DamageOverTime::new
    );

    public static void onLivingUpdate(LivingEntity entity) {
        ModDataComponents.DAMAGE_OVER_TIME.on(entity).iterate((component, slot) -> {
            if (component.condition.test(entity)) {
                double damagePerTick = component.damagePerSecond.get() / 20;
                if (damagePerTick >= 1) {
                    slot.hurtAndBreak(damagePerTick);
                } else if (entity.tickCount % (int) Math.round(1 / damagePerTick) == 0) {
                    slot.hurtAndBreak(1);
                }
            }
        });
    }
}
