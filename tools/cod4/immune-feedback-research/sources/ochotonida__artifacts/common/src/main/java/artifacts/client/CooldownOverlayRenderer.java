package artifacts.client;

import artifacts.Artifacts;
import artifacts.equipment.EquipmentSlotManager;
import artifacts.registry.ModDataComponents;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.world.entity.player.Player;
import org.apache.commons.lang3.mutable.MutableInt;

public class CooldownOverlayRenderer {

    public static void render(GuiGraphicsExtractor guiGraphics, DeltaTracker ignored) {
        if (!Artifacts.CONFIG.client.enableCooldownOverlay.get() || !(Minecraft.getInstance().getCameraEntity() instanceof Player player)) {
            return;
        }

        int y = guiGraphics.guiHeight() - 16 - 3;
        int cooldownOverlayOffset = Artifacts.CONFIG.client.cooldownOverlayOffset.get();

        final int step, start;
        if (cooldownOverlayOffset < 0) {
            step = -20;
            start = guiGraphics.guiWidth() / 2 - 91 - 16 + cooldownOverlayOffset;
        } else {
            step = 20;
            start = guiGraphics.guiWidth() / 2 + 91 + cooldownOverlayOffset;
        }

        MutableInt k = new MutableInt(0);

        EquipmentSlotManager.iterateEquipment(player, false, false, stack -> {
            if (!stack.isEmpty()
                    && ModDataComponents.hasAbilityWithCooldown(stack)
                    && player.getCooldowns().isOnCooldown(stack)
            ) {
                int x = start + step * k.intValue();
                k.add(1);
                guiGraphics.item(player, stack, x, y, k.intValue() + 1);
                guiGraphics.itemDecorations(Minecraft.getInstance().font, stack, x, y);
            }
        });
    }
}
