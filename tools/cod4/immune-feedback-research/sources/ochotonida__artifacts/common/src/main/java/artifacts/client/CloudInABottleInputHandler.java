package artifacts.client;

import artifacts.component.ability.DoubleJump;
import artifacts.network.NetworkHandler;
import artifacts.network.payload.DoubleJumpPacket;
import artifacts.registry.ModDataComponents;
import net.minecraft.client.Minecraft;
import net.minecraft.client.player.LocalPlayer;

public class CloudInABottleInputHandler {

    private static boolean canDoubleJump;
    private static boolean hasReleasedJumpKey;

    public static void onClientTick(Minecraft instance) {
        LocalPlayer player = instance.player;
        // noinspection ConstantValue
        if (player != null && player.input != null) {
            handleCloudInABottleInput(player);
        }
    }

    private static void handleCloudInABottleInput(LocalPlayer player) {
        if ((player.onGround() || player.onClimbable()) && (!player.isInWater() || ModDataComponents.SINKING.on(player).findAny())) {
            hasReleasedJumpKey = false;
            canDoubleJump = true;
        } else if (!player.input.keyPresses.jump()) {
            hasReleasedJumpKey = true;
        } else if (!player.getAbilities().flying && canDoubleJump && hasReleasedJumpKey) {
            canDoubleJump = false;
            if (ModDataComponents.DOUBLE_JUMP.on(player).findAny()) {
                NetworkHandler.sendToServer(new DoubleJumpPacket());
                DoubleJump.jump(player);
            }
        }
    }
}
