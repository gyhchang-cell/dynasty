package artifacts.component.ability;

import artifacts.component.ComponentType;
import net.minecraft.ChatFormatting;
import net.minecraft.core.component.DataComponentGetter;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.world.item.Item;

import java.util.Objects;
import java.util.function.Consumer;

public interface EquipmentAbility {

    boolean isNonCosmetic();

    default void addToTooltip(TooltipWriter writer) {
        writer.addDefaultTooltipKey();
    }

    class TooltipWriter {

        private final Identifier id;
        private final Consumer<Component> tooltip;
        private final Item.TooltipContext context;
        private final DataComponentGetter componentGetter;

        public TooltipWriter(ComponentType<?, ? extends EquipmentAbility> type, Consumer<Component> tooltip, Item.TooltipContext context, DataComponentGetter componentGetter) {
            this.id = Objects.requireNonNull(BuiltInRegistries.DATA_COMPONENT_TYPE.getKey(type.get()));
            this.tooltip = tooltip;
            this.context = context;
            this.componentGetter = componentGetter;
        }

        public Item.TooltipContext context() {
            return context;
        }

        public DataComponentGetter components() {
            return componentGetter;
        }

        public TooltipWriter add(String lineId, Object... args) {
            return addRaw(Component.translatable("%s.tooltip.ability.%s.%s".formatted(id.getNamespace(), id.getPath(), lineId), args).withStyle(ChatFormatting.GRAY));
        }

        public TooltipWriter addDefaultTooltipKey(Object... args) {
            return addRaw(Component.translatable("%s.tooltip.ability.%s".formatted(id.getNamespace(), id.getPath()), args).withStyle(ChatFormatting.GRAY));
        }

        private TooltipWriter addRaw(Component component) {
            tooltip.accept(component);
            return this;
        }
    }
}
