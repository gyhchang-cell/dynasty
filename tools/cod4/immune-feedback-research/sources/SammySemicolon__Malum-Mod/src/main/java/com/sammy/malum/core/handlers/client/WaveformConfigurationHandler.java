package com.sammy.malum.core.handlers.client;

import com.sammy.malum.client.screen.waveform.*;
import com.sammy.malum.common.block.curiosities.artifice.ConfigurableArtificeBlockEntity;
import com.sammy.malum.common.block.curiosities.artifice.elemental_artifice.aerial.GustIgniterBlockEntity;
import com.sammy.malum.common.block.curiosities.artifice.elemental_artifice.base.ElementalArtificeBlockEntity;
import com.sammy.malum.common.block.curiosities.artifice.waveform.*;
import com.sammy.malum.registry.common.*;

import net.minecraft.client.*;
import net.minecraft.client.gui.screens.*;
import net.minecraft.core.*;
import net.minecraft.world.*;
import net.minecraft.world.entity.player.*;
import net.minecraft.world.item.*;
import net.minecraft.world.level.*;
import net.minecraft.world.phys.*;
import net.neoforged.neoforge.client.event.*;
import net.neoforged.neoforge.event.entity.player.*;

public class WaveformConfigurationHandler {

    public static BlockPos interactionPos;
    public static InteractionHand interactionHand;
    public static int interactionTime;

    public static void tick(ClientTickEvent event) {
        var minecraft = Minecraft.getInstance();
        if (interactionPos == null) {
            return;
        }
        var hitResult = minecraft.hitResult;
        if (!(hitResult instanceof BlockHitResult blockHitResult)) {
            resetInteraction();
            return;
        }
        var blockPos = blockHitResult.getBlockPos();
        if (!blockPos.equals(interactionPos)) {
            resetInteraction();
            return;
        }
        if (!(minecraft.level.getBlockEntity(blockPos) instanceof ConfigurableArtificeBlockEntity entity)) {
            resetInteraction();
            return;
        }
        if (!entity.canBeTinkered()) {
            resetInteraction();
            return;
        }
        if (!minecraft.options.keyUse.isDown()) {
            resetInteraction();
            return;
        }

        interactionTime++;
        if (interactionTime == 5) {
            Screen screen = null;
            if (entity instanceof ElementalArtificeBlockEntity gustGizmo) {
                if (gustGizmo.redirectTinkerFocus() instanceof GustIgniterBlockEntity igniter) {
                    screen = new GustGizmoConfigurationScreen(igniter, igniter != gustGizmo);
                }
            }
            else if (entity instanceof SpiritDiodeBlockEntity spiritDiode) {
                screen = new DiodeValueConfigurationScreen(spiritDiode);
            }
            minecraft.setScreen(screen);
            resetInteraction();
        }
    }

    public static void onBlockActivated(PlayerInteractEvent.RightClickBlock event) {
        Level level = event.getLevel();
        BlockPos pos = event.getPos();
        Player player = event.getEntity();
        InteractionHand hand = event.getHand();
        ItemStack stack = player.getItemInHand(hand);
        if (!stack.is(MalumTags.Items.IS_REDSTONE_TOOL)) {
            return;
        }
        if (!canInteract(player)) {
            return;
        }
        if (!(level.getBlockEntity(pos) instanceof ConfigurableArtificeBlockEntity)) {
            return;
        }
        if (interactionPos != null) {
            event.setCanceled(true);
            return;
        }
        interactionPos = pos;
        interactionHand = hand;
        interactionTime = 0;
        player.swing(hand);
        event.setCanceled(true);
    }

    public static void resetInteraction() {
        interactionPos = null;
        interactionHand = null;
        interactionTime = 0;
    }

    public static boolean canInteract(Player player) {
        return player != null && !player.isSpectator() && !player.isShiftKeyDown() && player.mayBuild();
    }
}