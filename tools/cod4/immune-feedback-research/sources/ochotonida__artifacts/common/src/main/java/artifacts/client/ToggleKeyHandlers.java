package artifacts.client;

import artifacts.Artifacts;
import artifacts.component.ToggleIdentifier;
import artifacts.network.NetworkHandler;
import artifacts.network.payload.ToggleKeyPressedPacket;
import artifacts.registry.ModKeyMappings;
import net.minecraft.ChatFormatting;
import net.minecraft.client.KeyMapping;
import net.minecraft.network.chat.Component;

import java.util.LinkedHashSet;
import java.util.Set;
import java.util.function.Consumer;

public class ToggleKeyHandlers {

    private static final Set<ToggleInputListener> INPUT_HANDLERS = new LinkedHashSet<>();

    public static void init() {
        INPUT_HANDLERS.add(new ToggleInputListener(ToggleIdentifier.CHARM_OF_SHRINKING, ModKeyMappings.TOGGLE_CHARM_OF_SHRINKING));
        INPUT_HANDLERS.add(new ToggleInputListener(ToggleIdentifier.CHARM_OF_SINKING, ModKeyMappings.TOGGLE_CHARM_OF_SINKING));
        INPUT_HANDLERS.add(new ToggleInputListener(ToggleIdentifier.NIGHT_VISION_GOGGLES, ModKeyMappings.TOGGLE_NIGHT_VISION_GOGGLES));
        INPUT_HANDLERS.add(new ToggleInputListener(ToggleIdentifier.UNIVERSAL_ATTRACTOR, ModKeyMappings.TOGGLE_UNIVERSAL_ATTRACTOR));
        INPUT_HANDLERS.add(new ToggleInputListener(ToggleIdentifier.SCARF_OF_INVISIBILITY, ModKeyMappings.TOGGLE_SCARF_OF_INVISIBILITY));
    }

    public static void onClientTick() {
        for (ToggleInputListener inputHandler : INPUT_HANDLERS) {
            inputHandler.onClientTick();
        }
    }

    public static KeyMapping getKeyMapping(ToggleIdentifier identifier) {
        for (ToggleInputListener inputHandler : INPUT_HANDLERS) {
            if (inputHandler.identifier == identifier) {
                return inputHandler.key;
            }
        }
        throw new IllegalArgumentException();
    }

    public static void addTooltip(ToggleIdentifier identifier, boolean addWhenUnbound, Consumer<Component> consumer) {
        KeyMapping key = ToggleKeyHandlers.getKeyMapping(identifier);
        if (key != null && (!key.isUnbound() || addWhenUnbound)) {
            consumer.accept(Component.translatable("%s.tooltip.toggle_keymapping".formatted(Artifacts.MOD_ID), key.getTranslatedKeyMessage())
                    .withStyle(ChatFormatting.GRAY));
        }
    }

    private static class ToggleInputListener {

        private final KeyMapping key;
        private final ToggleIdentifier identifier;

        private boolean wasToggleKeyDown;

        public ToggleInputListener(ToggleIdentifier identifier, KeyMapping key) {
            this.key = key;
            this.identifier = identifier;
        }

        public void onClientTick() {
            boolean isToggleKeyDown = key.isDown();
            if (isToggleKeyDown && !wasToggleKeyDown) {
                NetworkHandler.sendToServer(new ToggleKeyPressedPacket(identifier));
            }
            wasToggleKeyDown = isToggleKeyDown;
        }
    }
}
