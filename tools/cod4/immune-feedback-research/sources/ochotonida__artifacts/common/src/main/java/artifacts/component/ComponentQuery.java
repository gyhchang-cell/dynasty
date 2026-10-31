package artifacts.component;

import artifacts.component.ability.EquipmentAbility;
import artifacts.equipment.EquipmentSlotManager;
import net.minecraft.util.Unit;
import net.minecraft.world.entity.LivingEntity;
import org.jetbrains.annotations.Nullable;

import java.util.function.Function;
import java.util.function.Predicate;

public record ComponentQuery<C, E>(
        ComponentType<C, E> type,
        @Nullable LivingEntity entity,
        Predicate<E> filter,
        boolean skipCooldown,
        boolean skipDisabled,
        boolean skipCosmetic
) {

    public ComponentQuery(ComponentType<C, E> type, @Nullable LivingEntity entity) {
        this(type, entity, _ -> true, true, true, true);
    }

    /**
     * Include all components of this type in this query, regardless of cooldowns/disabled state
     */
    public ComponentQuery<C, E> includeInactive() {
        return this.includeDisabledItems().includeItemsOnCooldown();
    }

    /**
     * Include items that are currently on cooldown in this query
     */
    public ComponentQuery<C, E> includeItemsOnCooldown() {
        return new ComponentQuery<>(type, entity, filter, false, skipDisabled, skipCosmetic);
    }

    /**
     * Include items that are broken or have been toggled off in this query
     */
    public ComponentQuery<C, E> includeDisabledItems() {
        return new ComponentQuery<>(type, entity, filter, skipCooldown, false, skipCosmetic);
    }

    public ComponentQuery<C, E> filter(Predicate<E> filter) {
        return new ComponentQuery<>(type, entity, this.filter.and(filter), skipCooldown, skipDisabled, skipCosmetic);
    }

    /**
     * Returns true if the entity has an item equipped with a component matching this query
     */
    public boolean findAny() {
        return reduce(false, (_, _) -> true);
    }

    public int sumInt(Function<E, Integer> f) {
        return reduce(0, (current, component) -> current + f.apply(component));
    }

    public double maxDouble(Function<E, Double> f) {
        return reduce(0D, (current, component) -> Math.max(current, f.apply(component)));
    }

    public double minDouble(double init, Function<E, Double> f) {
        return reduce(init, (current, component) -> Math.min(current, f.apply(component)));
    }

    public int maxInt(Function<E, Integer> f) {
        return reduce(0, (current, component) -> Math.max(current, f.apply(component)));
    }

    public int minInt(int init, Function<E, Integer> f) {
        return reduce(init, (current, component) -> Math.min(current, f.apply(component)));
    }

    /**
     * Iterate over all components matching this query
     */
    public void iterate(ComponentVisitor<E> visitor) {
        EquipmentSlotManager.reduceEquipment(entity, skipCooldown, skipDisabled, Unit.INSTANCE, (acc, slotAccess) -> {
            for (E entry : type.getEntries(slotAccess.get())) {
                if ((!skipCosmetic || !(entry instanceof EquipmentAbility ability) || ability.isNonCosmetic())
                        && filter.test(entry)
                ) {
                    visitor.visit(entry, slotAccess);
                }
            }
            return acc;
        });
    }

    /**
     * Collect all components matching this query into a single value
     */
    public <ACC> ACC reduce(ACC init, ComponentAccumulator<ACC, E> accumulator) {
        return EquipmentSlotManager.reduceEquipment(entity, skipCooldown, skipDisabled, init, (acc, slotAccess) -> {
            for (E entry : type.getEntries(slotAccess.get())) {
                if ((!skipCosmetic || !(entry instanceof EquipmentAbility ability) || ability.isNonCosmetic())
                        && filter.test(entry)
                ) {
                    acc = accumulator.accumulate(acc, entry);
                }
            }
            return acc;
        });
    }
}
