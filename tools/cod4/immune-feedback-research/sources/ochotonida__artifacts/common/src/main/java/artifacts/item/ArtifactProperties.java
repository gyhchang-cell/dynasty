package artifacts.item;

import artifacts.Artifacts;
import artifacts.component.CompositeComponent;
import artifacts.component.Equipable;
import artifacts.component.ToggleIdentifier;
import artifacts.component.ability.*;
import artifacts.component.ability.mobeffect.EquipmentMobEffect;
import artifacts.component.ability.mobeffect.MobEffectProvider;
import artifacts.component.itemdamage.*;
import artifacts.config.value.ConfigValue;
import artifacts.config.value.Value;
import artifacts.item.consumeeffects.DamageItemConsumeEffect;
import artifacts.registry.ModDataComponents;
import artifacts.registry.ModTags;
import net.minecraft.ChatFormatting;
import net.minecraft.core.Holder;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.HolderSet;
import net.minecraft.core.component.DataComponentInitializers;
import net.minecraft.core.component.DataComponentType;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.resources.ResourceKey;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.tags.TagKey;
import net.minecraft.util.Unit;
import net.minecraft.world.damagesource.DamageType;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.Rarity;
import net.minecraft.world.item.component.Consumables;
import net.minecraft.world.item.component.ItemLore;
import net.minecraft.world.item.component.UseCooldown;
import net.minecraft.world.item.enchantment.Enchantment;
import net.minecraft.world.item.enchantment.Repairable;
import org.jetbrains.annotations.Nullable;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;
import java.util.function.Consumer;
import java.util.function.Function;
import java.util.function.Supplier;

public final class ArtifactProperties {

    private final String itemName;
    private final Item.Properties properties;
    private final List<CompositeComponentInitializer<?>> compositeComponents;

    private boolean isEquipable = false;

    public ArtifactProperties(String itemName) {
        this.itemName = itemName;
        this.properties = new Item.Properties();
        this.compositeComponents = new ArrayList<>();
    }

    public ArtifactProperties abilityLore(MutableComponent component) {
        return component(
                ModDataComponents.ABILITY_LORE.get(),
                new ItemLore(List.of(component.withStyle(ChatFormatting.GRAY)))
        );
    }

    public ArtifactProperties equipable() {
        return equipable(SoundEvents.ARMOR_EQUIP_GENERIC);
    }

    public ArtifactProperties equipable(SoundEvent equipSound) {
        return equipable(BuiltInRegistries.SOUND_EVENT.wrapAsHolder(equipSound));
    }

    public ArtifactProperties equipable(Holder<SoundEvent> equipSound) {
        this.isEquipable = true;
        component(ModDataComponents.EQUIPABLE.get(), new Equipable(equipSound, true));
        return this;
    }

    public ArtifactProperties toggleKey(ToggleIdentifier identifier) {
        return component(ModDataComponents.TOGGLE_KEY.get(), identifier);
    }

    public ArtifactProperties piglinLoved() {
        return component(ModDataComponents.PIGLIN_LOVED.get());
    }

    public ArtifactProperties increasesAttribute(Holder<Attribute> attribute, Value<Double> amount) {
        return addAttributeModifier(attribute, amount, AttributeModifier.Operation.ADD_VALUE);
    }

    public ArtifactProperties modifiesAttributeBase(Holder<Attribute> attribute, Value<Double> amount) {
        return addAttributeModifier(attribute, amount, AttributeModifier.Operation.ADD_MULTIPLIED_BASE);
    }

    public ArtifactProperties modifiesAttributeTotal(Holder<Attribute> attribute, Value<Double> amount) {
        return addAttributeModifier(attribute, amount, AttributeModifier.Operation.ADD_MULTIPLIED_TOTAL);
    }

    public ArtifactProperties addAttributeModifier(Holder<Attribute> attribute, Value<Double> amount, AttributeModifier.Operation operation) {
        return addAttributeModifier(attribute, amount, operation, () -> true, true);
    }

    public ArtifactProperties addAttributeModifier(Holder<Attribute> attribute, Value<Double> amount, AttributeModifier.Operation operation, Supplier<Boolean> condition, boolean ignoreCooldown) {
        return compositeComponent(ModDataComponents.ATTRIBUTE_MODIFIERS.get(), condition, _ -> new EquipmentAttributeModifier(
                attribute, amount, operation,
                Artifacts.id(itemName + '/' + attribute.unwrapKey().orElseThrow().identifier().getPath()),
                ignoreCooldown
        ));
    }

    public ArtifactProperties mobEffect(Holder<MobEffect> effect, Value<Integer> level, Value<Integer> duration, Supplier<EntityCondition> condition) {
        return delayedComponent(ModDataComponents.MOB_EFFECTS.get(), _ -> new CompositeComponent<>(List.of(
                new EquipmentMobEffect(new MobEffectProvider(effect, level, duration, Value.of(false), Value.of(true), condition.get()))
        )));
    }

    public ArtifactProperties increasesEnchantment(ResourceKey<Enchantment> enchantment, Value<Integer> amount) {
        return compositeComponent(ModDataComponents.ENCHANTMENT_LEVEL_MODIFIERS.get(), _ -> new EnchantmentLevelModifier(enchantment, amount));
    }

    public ArtifactProperties useCooldown(Value<Integer> cooldown) {
        return delayedComponent(DataComponents.USE_COOLDOWN, _ -> new UseCooldown(cooldown.get()));
    }

    public ArtifactProperties cooldownOnHurt(Value<Integer> cooldown) {
        return component(ModDataComponents.POST_DAMAGE_COOLDOWN.get(), new PostDamageCooldown(cooldown, Optional.empty()));
    }

    public ArtifactProperties cooldownOnHurt(Value<Integer> cooldown, TagKey<DamageType> filter) {
        return component(ModDataComponents.POST_DAMAGE_COOLDOWN.get(), new PostDamageCooldown(cooldown, Optional.of(filter)));
    }

    public ArtifactProperties durability(ItemDamageProperties durability) {
        // Vanilla also sets max stack size to 1, but we already do this by default in ArtifactProperties#build()
        delayedComponent(DataComponents.DAMAGE, durability::canBeDamaged, _ -> 0);
        delayedComponent(DataComponents.MAX_DAMAGE, durability::canBeDamaged, _ -> durability.getMaxDamage());
        delayedComponent(ModDataComponents.INDESTRUCTIBLE.get(), durability::canBeDamaged, _ -> durability.indestructible());
        delayedComponent(DataComponents.REPAIRABLE, () -> durability.canBeDamaged() && durability.canBeRepaired(), registries -> new Repairable(
                registries.getOrThrow(durability.getRepairMaterials())
        ));
        return this;
    }

    public ArtifactProperties breakSound(Holder<SoundEvent> breakSound) {
        return component(DataComponents.BREAK_SOUND, breakSound);
    }

    public ArtifactProperties damageOverTime(Value<Double> damagePerSecond, EntityCondition condition) {
        return component(ModDataComponents.DAMAGE_OVER_TIME.get(), new DamageOverTime(damagePerSecond, condition));
    }

    public ArtifactProperties damageWhenConsumed(Value<Boolean> enabled, Value<Integer> itemDamage) {
        return delayedComponent(
                DataComponents.CONSUMABLE,
                enabled,
                _ -> Consumables.defaultFood().onConsume(new DamageItemConsumeEffect(itemDamage)).build()
        );
    }

    public ArtifactProperties damageOnHurt(Value<Integer> itemDamage) {
        return component(ModDataComponents.DAMAGE_ON_HURT.get(), new DamageOnHurt(itemDamage, Optional.empty()));
    }

    public ArtifactProperties damageOnHurt(Value<Integer> itemDamage, TagKey<DamageType> filter) {
        return component(ModDataComponents.DAMAGE_ON_HURT.get(), new DamageOnHurt(itemDamage, Optional.of(filter)));
    }

    public ArtifactProperties damageOnMeleeAttack(Value<Integer> itemDamage) {
        return compositeComponent(ModDataComponents.DAMAGE_ON_ATTACK.get(), _ -> new DamageOnAttack(itemDamage, true, false, Optional.empty()));
    }

    public ArtifactProperties damageOnKill(Value<Integer> itemDamage) {
        return compositeComponent(ModDataComponents.DAMAGE_ON_ATTACK.get(), _ -> new DamageOnAttack(itemDamage, false, true, Optional.empty()));
    }

    public ArtifactProperties damageOnKill(Value<Integer> itemDamage, Function<HolderLookup.Provider, HolderSet<EntityType<?>>> entity) {
        return compositeComponent(
                ModDataComponents.DAMAGE_ON_ATTACK.get(),
                registries -> new DamageOnAttack(itemDamage, false, true, Optional.of(entity.apply(registries)))
        );
    }

    public ArtifactProperties damageOnBlockMined(Value<Integer> itemDamage) {
        return component(ModDataComponents.DAMAGE_ON_BLOCK_MINED.get(), new DamageOnBlockMined(itemDamage, Optional.empty()));
    }

    public ArtifactProperties damageOnOreMined(Value<Integer> itemDamage) {
        return component(ModDataComponents.DAMAGE_ON_BLOCK_MINED.get(), new DamageOnBlockMined(itemDamage, Optional.of(ModTags.ORES)));
    }

    public ArtifactProperties damageOnItemConsumed(Value<Integer> damageOnEat, Value<Integer> damageOnDrink) {
        return component(ModDataComponents.DAMAGE_ON_ITEM_CONSUMED.get(), new DamageOnItemConsumed(damageOnEat, damageOnDrink));
    }

    public ArtifactProperties component(DataComponentType<Unit> type) {
        return component(type, Unit.INSTANCE);
    }

    public ArtifactProperties component(DataComponentType<SimpleAbility> type, Value<Boolean> enabled) {
        return component(type, new SimpleAbility(enabled));
    }

    public <T> ArtifactProperties delayedComponent(DataComponentType<T> type, DataComponentInitializers.SingleComponentInitializer<@Nullable T> initializer) {
        return delayedComponent(type, () -> true, initializer);
    }

    @SuppressWarnings("DataFlowIssue")
    public <T> ArtifactProperties delayedComponent(DataComponentType<T> type, Supplier<Boolean> condition, DataComponentInitializers.SingleComponentInitializer<@Nullable T> initializer) {
        assertRequiresWorldRestart(condition);
        properties.delayedComponent(type, context -> condition.get() ? initializer.create(context) : null);
        return this;
    }

    public <T> ArtifactProperties compositeComponent(DataComponentType<CompositeComponent<T>> type, Supplier<Boolean> condition, EntryInitializer<T> initializer) {
        assertRequiresWorldRestart(condition);
        return compositeComponent(type, registries -> condition.get() ? initializer.create(registries) : null);
    }

    @SafeVarargs
    public final <T> ArtifactProperties compositeComponent(DataComponentType<CompositeComponent<T>> type, EntryInitializer<T>... entries) {
        CompositeComponentInitializer<T> initializer = null;
        for (CompositeComponentInitializer<?> compositeComponent : compositeComponents) {
            if (type.equals(compositeComponent.type)) {
                // noinspection unchecked
                initializer = ((CompositeComponentInitializer<T>) compositeComponent);
            }
        }
        if (initializer == null) {
            initializer = new CompositeComponentInitializer<>(type);
            compositeComponents.add(initializer);
        }
        initializer.entries.addAll(Arrays.asList(entries));
        return this;
    }

    public <T> ArtifactProperties component(DataComponentType<T> type, T component) {
        properties.component(type, component);
        return this;
    }

    public ArtifactProperties properties(Consumer<Item.Properties> consumer) {
        consumer.accept(this.properties);
        return this;
    }

    public Item.Properties build() {
        if (isEquipable) {
            component(ModDataComponents.DEPENDENCY_CHECK_TOOLTIP.get());
        }
        component(ModDataComponents.COSMETIC_TOOLTIP.get());
        properties.stacksTo(1);
        properties.rarity(Rarity.RARE);
        properties.fireResistant();
        for (CompositeComponentInitializer<?> initializer : compositeComponents) {
            initializer.addTo(properties);
        }
        return properties;
    }

    private static void assertRequiresWorldRestart(Supplier<Boolean> condition) {
        if (condition instanceof ConfigValue<Boolean> configValue && !configValue.requiresRestart()) {
            throw new IllegalArgumentException(
                    "Config value '%s' used as a component condition should require world restart".formatted(configValue.getKey())
            );
        }
    }

    private static class CompositeComponentInitializer<T> {

        private final DataComponentType<CompositeComponent<T>> type;
        private final List<EntryInitializer<T>> entries;

        private CompositeComponentInitializer(DataComponentType<CompositeComponent<T>> type) {
            this.type = type;
            this.entries = new ArrayList<>();
        }

        private void addTo(Item.Properties properties) {
            properties.delayedComponent(type, registries -> new CompositeComponent<>(
                    entries.stream().map(entry -> entry.create(registries)).toList()
            ));
        }
    }

    @FunctionalInterface
    public interface EntryInitializer<T> {

        @Nullable
        T create(HolderLookup.Provider registries);
    }
}
