package artifacts.registry;

import artifacts.Artifacts;
import com.mojang.blaze3d.platform.InputConstants;
import net.minecraft.client.KeyMapping;
import net.minecraft.client.Minecraft;
import net.minecraft.core.Holder;
import net.minecraft.world.item.Item;

import java.util.function.Consumer;

public class ModKeyMappings {

    private static final KeyMapping.Category CATEGORY = KeyMapping.Category.register(Artifacts.id("artifacts"));

    private static final KeyMapping ACTIVATE_HELIUM_FLAMINGO = createUnboundKeyMapping(ModItems.HELIUM_FLAMINGO, "activate");
    public static final KeyMapping TOGGLE_CHARM_OF_SHRINKING = createToggleKeyMapping(ModItems.CHARM_OF_SHRINKING);
    public static final KeyMapping TOGGLE_CHARM_OF_SINKING = createToggleKeyMapping(ModItems.CHARM_OF_SINKING);
    public static final KeyMapping TOGGLE_NIGHT_VISION_GOGGLES = createToggleKeyMapping(ModItems.NIGHT_VISION_GOGGLES);
    public static final KeyMapping TOGGLE_SCARF_OF_INVISIBILITY = createToggleKeyMapping(ModItems.SCARF_OF_INVISIBILITY);
    public static final KeyMapping TOGGLE_UNIVERSAL_ATTRACTOR = createToggleKeyMapping(ModItems.UNIVERSAL_ATTRACTOR);

    private static KeyMapping createToggleKeyMapping(Holder<Item> item) {
        return createUnboundKeyMapping(item, "toggle");
    }

    private static KeyMapping createUnboundKeyMapping(Holder<Item> item, String action) {
        String id = "artifacts.key.%s.%s".formatted(item.unwrapKey().orElseThrow().identifier().getPath(), action);
        return new KeyMapping(id, InputConstants.Type.KEYSYM, InputConstants.UNKNOWN.getValue(), CATEGORY);
    }

    public static KeyMapping getHeliumFlamingoKey() {
        if (!ACTIVATE_HELIUM_FLAMINGO.isUnbound()) {
            return ACTIVATE_HELIUM_FLAMINGO;
        }
        return Minecraft.getInstance().options.keySprint;
    }

    public static void register(Consumer<KeyMapping> registration) {
        registration.accept(ACTIVATE_HELIUM_FLAMINGO);
        registration.accept(TOGGLE_CHARM_OF_SHRINKING);
        registration.accept(TOGGLE_CHARM_OF_SINKING);
        registration.accept(TOGGLE_NIGHT_VISION_GOGGLES);
        registration.accept(TOGGLE_SCARF_OF_INVISIBILITY);
        registration.accept(TOGGLE_UNIVERSAL_ATTRACTOR);
    }
}
