package artifacts.component.ability;

import artifacts.config.value.Value;
import artifacts.config.value.ValueTypes;
import artifacts.registry.ModDataComponents;
import artifacts.registry.ModKeyMappings;
import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import io.netty.buffer.ByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;

public record SwimInAir(Value<Integer> flightDuration, Value<Integer> rechargeDuration, Value<Integer> cooldown)
        implements EquipmentAbility {

    public static final Codec<SwimInAir> CODEC = RecordCodecBuilder.create(instance -> instance.group(
            ValueTypes.DURATION.codec().fieldOf("flight_duration").forGetter(SwimInAir::flightDuration),
            ValueTypes.DURATION.codec().fieldOf("recharge_duration").forGetter(SwimInAir::rechargeDuration),
            ValueTypes.DURATION.codec().fieldOf("cooldown").forGetter(SwimInAir::cooldown)
    ).apply(instance, SwimInAir::new));

    public static final StreamCodec<ByteBuf, SwimInAir> STREAM_CODEC = StreamCodec.composite(
            ValueTypes.DURATION.streamCodec(),
            SwimInAir::flightDuration,
            ValueTypes.DURATION.streamCodec(),
            SwimInAir::rechargeDuration,
            ValueTypes.DURATION.streamCodec(),
            SwimInAir::cooldown,
            SwimInAir::new
    );

    /**
     * @return The maximum amount of time the entity is allowed to fly, in ticks
     */
    public static int getMaxFlightDuration(LivingEntity entity) {
        return ModDataComponents.SWIM_IN_AIR.on(entity)
                .includeItemsOnCooldown()
                .maxInt(ability -> ability.flightDuration().get() * 20);
    }

    /**
     * @return The time it takes to fully recharge, in ticks
     */
    public static int getRechargeDuration(LivingEntity entity) {
        int rechargeDuration = ModDataComponents.SWIM_IN_AIR.on(entity)
                .includeItemsOnCooldown()
                .maxInt(ability -> ability.rechargeDuration().get() * 20);
        return Math.max(20, rechargeDuration);
    }

    public static boolean canSwim(LivingEntity entity) {
        return entity instanceof Player player
                && ModDataComponents.SWIM_IN_AIR.on(player).findAny()
                && !player.getAbilities().flying
                && !player.onGround()
                && !player.isFallFlying()
                && !player.isPassenger();
    }

    @Override
    public boolean isNonCosmetic() {
        return flightDuration().get() > 0;
    }

    @Override
    public void addToTooltip(TooltipWriter writer) {
        writer.add("swimming");
        writer.add("keymapping", ModKeyMappings.getHeliumFlamingoKey().getTranslatedKeyMessage());
    }
}
