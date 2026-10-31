package artifacts.component.ability;

import artifacts.config.value.Value;
import artifacts.config.value.ValueTypes;
import artifacts.equipment.EquipmentSlotAccess;
import artifacts.registry.ModAttributes;
import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.minecraft.core.Holder;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.resources.Identifier;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;

import java.util.HashSet;
import java.util.List;
import java.util.Set;

public record EquipmentAttributeModifier(
        Holder<Attribute> attribute,
        Value<Double> amount,
        AttributeModifier.Operation operation,
        Identifier id,
        boolean ignoreCooldown
) implements EquipmentAbility {

    private static final Set<Holder<Attribute>> POSITIVE_ATTRIBUTES_WITH_TOOLTIP;
    private static final Set<Holder<Attribute>> NEGATIVE_ATTRIBUTES_WITH_TOOLTIP = Set.of(
            Attributes.SCALE,
            Attributes.FALL_DAMAGE_MULTIPLIER
    );

    static {
        POSITIVE_ATTRIBUTES_WITH_TOOLTIP = new HashSet<>();
        POSITIVE_ATTRIBUTES_WITH_TOOLTIP.addAll(ModAttributes.PLAYER_ATTRIBUTES);
        POSITIVE_ATTRIBUTES_WITH_TOOLTIP.addAll(ModAttributes.GENERIC_ATTRIBUTES);
        POSITIVE_ATTRIBUTES_WITH_TOOLTIP.add(ModAttributes.SWIM_SPEED);
        POSITIVE_ATTRIBUTES_WITH_TOOLTIP.addAll(List.of(
                Attributes.ATTACK_DAMAGE,
                Attributes.ATTACK_KNOCKBACK,
                Attributes.ATTACK_SPEED,
                Attributes.BLOCK_BREAK_SPEED,
                Attributes.JUMP_STRENGTH,
                Attributes.KNOCKBACK_RESISTANCE,
                Attributes.MAX_HEALTH,
                Attributes.SAFE_FALL_DISTANCE,
                Attributes.OXYGEN_BONUS
        ));
    }

    public static final Codec<EquipmentAttributeModifier> CODEC = RecordCodecBuilder.create(instance -> instance.group(
            BuiltInRegistries.ATTRIBUTE.holderByNameCodec().fieldOf("attribute").forGetter(EquipmentAttributeModifier::attribute),
            ValueTypes.ATTRIBUTE_MODIFIER.codec().fieldOf("amount").forGetter(EquipmentAttributeModifier::amount),
            AttributeModifier.Operation.CODEC.fieldOf("operation").forGetter(EquipmentAttributeModifier::operation),
            Identifier.CODEC.fieldOf("id").forGetter(EquipmentAttributeModifier::id),
            Codec.BOOL.optionalFieldOf("ignore_cooldown", true).forGetter(EquipmentAttributeModifier::ignoreCooldown)
    ).apply(instance, EquipmentAttributeModifier::new));

    public static final StreamCodec<RegistryFriendlyByteBuf, EquipmentAttributeModifier> STREAM_CODEC = StreamCodec.composite(
            ByteBufCodecs.holderRegistry(Registries.ATTRIBUTE),
            EquipmentAttributeModifier::attribute,
            ValueTypes.ATTRIBUTE_MODIFIER.streamCodec(),
            EquipmentAttributeModifier::amount,
            AttributeModifier.Operation.STREAM_CODEC,
            EquipmentAttributeModifier::operation,
            Identifier.STREAM_CODEC,
            EquipmentAttributeModifier::id,
            ByteBufCodecs.BOOL,
            EquipmentAttributeModifier::ignoreCooldown,
            EquipmentAttributeModifier::new
    );

    public AttributeModifier createModifier() {
        return new AttributeModifier(id(), amount().get(), operation());
    }

    private void onAttributeUpdated(LivingEntity entity) {
        if (attribute() == Attributes.MAX_HEALTH && entity.getHealth() > entity.getMaxHealth()) {
            entity.setHealth(entity.getMaxHealth());
        }
    }

    @Override
    public boolean isNonCosmetic() {
        return !Mth.equal(amount().get(), 0);
    }

    @Override
    public void addToTooltip(TooltipWriter writer) {
        String attributeName = attribute().unwrapKey().orElseThrow().identifier().getPath();

        if (amount().get() > 0) {
            for (Holder<Attribute> attribute : POSITIVE_ATTRIBUTES_WITH_TOOLTIP) {
                if (attribute.isBound() && attribute.value() == attribute().value()) {
                    writer.add(attributeName);
                }
            }
        } else {
            for (Holder<Attribute> attribute : NEGATIVE_ATTRIBUTES_WITH_TOOLTIP) {
                if (attribute.isBound() && attribute.value() == attribute().value()) {
                    writer.add(attributeName);
                }
            }
        }
    }

    public record Ticker() implements AbilityTicker<EquipmentAttributeModifier> {

        @Override
        public void onUnequip(EquipmentAttributeModifier ability, LivingEntity entity) {
            AttributeInstance attributeInstance = entity.getAttribute(ability.attribute());
            if (attributeInstance != null && attributeInstance.hasModifier(ability.id())) {
                attributeInstance.removeModifier(ability.id());
                ability.onAttributeUpdated(entity);
            }
        }

        @Override
        public void wornTick(EquipmentAttributeModifier ability, EquipmentSlotAccess slotAccess, LivingEntity entity, boolean isOnCooldown, boolean isDisabled) {
            AttributeInstance attributeInstance = entity.getAttribute(ability.attribute());
            if (attributeInstance == null) {
                return;
            }
            AttributeModifier existingModifier = attributeInstance.getModifier(ability.id());
            if (!ability.ignoreCooldown() && isOnCooldown) {
                if (!isDisabled && ability.isNonCosmetic()) {
                    onUnequip(ability, entity);
                }
            } else if (!isDisabled) {
                if (existingModifier == null || !Mth.equal(ability.amount().get(), existingModifier.amount())) {
                    attributeInstance.removeModifier(ability.id());
                    attributeInstance.addPermanentModifier(ability.createModifier());
                    ability.onAttributeUpdated(entity);
                }
            }
        }
    }
}
