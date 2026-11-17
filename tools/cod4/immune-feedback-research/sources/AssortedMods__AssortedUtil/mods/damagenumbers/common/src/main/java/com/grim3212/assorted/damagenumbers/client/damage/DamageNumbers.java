package com.grim3212.assorted.damagenumbers.client.damage;

import com.grim3212.assorted.damagenumbers.Constants;
import com.grim3212.assorted.damagenumbers.client.DamageNumbersClient;
import com.grim3212.assorted.lib.conditions.PartToggles;
import com.mojang.blaze3d.vertex.PoseStack;
import it.unimi.dsi.fastutil.ints.Int2FloatOpenHashMap;
import it.unimi.dsi.fastutil.ints.Int2LongOpenHashMap;
import it.unimi.dsi.fastutil.ints.Int2ObjectOpenHashMap;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.state.level.CameraRenderState;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.util.LightCoordsUtil;
import net.minecraft.util.Mth;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.phys.Vec3;
import org.jetbrains.annotations.Nullable;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 * RPG Damage, client only: the amount is how far synced health moved, after armour, where 1.2.5 showed
 * the raw hit. The source is vanilla's own damage packet, so no server side is needed.
 */
public final class DamageNumbers {

    private static final float TEXT_SCALE = 0.025F;
    // The damage packet and the health update can land a tick or two apart.
    private static final long SOURCE_MEMORY_TICKS = 5L;
    private static final float SMALLEST_CHANGE = 0.05F;

    private static Int2FloatOpenHashMap lastHealth = new Int2FloatOpenHashMap();
    private static final Int2ObjectOpenHashMap<DamageSource> recentSources = new Int2ObjectOpenHashMap<>();
    private static final Int2LongOpenHashMap recentSourceTimes = new Int2LongOpenHashMap();
    private static final List<DamagePopup> popups = new ArrayList<>();
    private static @Nullable ClientLevel trackedLevel;

    private DamageNumbers() {
    }

    /** From LivingEntityDamageEventMixin, as the damage packet is handled. */
    public static void onDamageEvent(LivingEntity entity, DamageSource source) {
        if (entity.level().isClientSide()) {
            recentSources.put(entity.getId(), source);
            recentSourceTimes.put(entity.getId(), entity.level().getGameTime());
        }
    }

    /** The numbers showing right now. */
    public static List<DamagePopup> popups() {
        return Collections.unmodifiableList(popups);
    }

    public static void tick(Minecraft minecraft) {
        ClientLevel level = minecraft.level;
        LocalPlayer player = minecraft.player;
        // Entity ids start over in each level.
        if (level != trackedLevel || level == null || player == null || !PartToggles.isEnabled(Constants.MOD_ID)) {
            trackedLevel = level;
            lastHealth.clear();
            recentSources.clear();
            recentSourceTimes.clear();
            popups.clear();
            return;
        }

        popups.removeIf(popup -> !popup.tick());

        long now = level.getGameTime();
        double range = DamageNumbersClient.CONFIG.damageNumbersRange.get();
        Int2FloatOpenHashMap health = new Int2FloatOpenHashMap();
        for (Entity entity : level.entitiesForRendering()) {
            if (!(entity instanceof LivingEntity living) || living.distanceToSqr(player) > range * range) {
                continue;
            }

            float current = living.getHealth();
            health.put(living.getId(), current);
            if (!lastHealth.containsKey(living.getId())) {
                continue;
            }

            float change = current - lastHealth.get(living.getId());
            // Not for what the player cannot see, or their own number in their face.
            if (Math.abs(change) < SMALLEST_CHANGE || living.isInvisibleTo(player) || (living == minecraft.getCameraEntity() && minecraft.options.getCameraType().isFirstPerson())) {
                continue;
            }

            if (change < 0.0F) {
                DamageSource source = now - recentSourceTimes.getOrDefault(living.getId(), Long.MIN_VALUE / 2) <= SOURCE_MEMORY_TICKS ? recentSources.get(living.getId()) : null;
                DamageKind kind = DamageKind.of(source);
                spawn(minecraft, level, living, "-" + DamagePopup.amount(-change), label(kind, source), kind.color(source));
            } else if (DamageNumbersClient.CONFIG.damageNumbersShowHealing.get()) {
                spawn(minecraft, level, living, "+" + DamagePopup.amount(change), DamageKind.HEALING.label(), DamageKind.HEALING.color());
            }
        }
        lastHealth = health;

        for (int id : recentSourceTimes.keySet().toIntArray()) {
            if (now - recentSourceTimes.get(id) > SOURCE_MEMORY_TICKS) {
                recentSourceTimes.remove(id);
                recentSources.remove(id);
            }
        }
    }

    private static void spawn(Minecraft minecraft, ClientLevel level, LivingEntity entity, String amount, Component label, int color) {
        MutableComponent text = Component.literal(amount);
        if (DamageNumbersClient.CONFIG.damageNumbersShowSource.get()) {
            text.append(" (").append(label).append(")");
        }

        // Out in front of the creature on the viewer's side, or its own head hides the number.
        Vec3 toViewer = minecraft.gameRenderer.mainCamera().position().subtract(entity.position()).multiply(1.0D, 0.0D, 1.0D);
        Vec3 front = toViewer.lengthSqr() < 1.0E-4D ? Vec3.ZERO : toViewer.normalize().scale(entity.getBbWidth() / 2.0D + 0.3D);

        float offset = -minecraft.font.width(text) / 2.0F;
        popups.add(new DamagePopup(text.getVisualOrderText(), offset, color, DamageNumbersClient.CONFIG.damageNumbersLifetime.get(),
                entity.getX() + front.x, entity.getY() + entity.getBbHeight() * 0.8D, entity.getZ() + front.z, entity.getY() + 0.25D, level.getRandom()));
    }

    /** A player's hit names the weapon, as 1.2.5 did; a creature's names the creature, and a projectile itself. */
    private static Component label(DamageKind kind, @Nullable DamageSource source) {
        if (source != null && kind == DamageKind.MELEE && source.getEntity() != null) {
            if (source.getEntity() instanceof Player attacker) {
                ItemStack weapon = attacker.getMainHandItem();
                return weapon.isEmpty() ? kind.label() : weapon.getHoverName();
            }
            return source.getEntity().getName();
        }
        if (source != null && kind == DamageKind.PROJECTILE && source.getDirectEntity() != null) {
            return source.getDirectEntity().getName();
        }
        return kind.label(source);
    }

    public static void submit(PoseStack poseStack, SubmitNodeCollector collector, CameraRenderState camera) {
        if (popups.isEmpty()) {
            return;
        }

        float partialTick = Minecraft.getInstance().getDeltaTracker().getGameTimeDeltaPartialTick(false);
        Vec3 cam = camera.pos;
        for (DamagePopup popup : popups) {
            int alpha = popup.alpha(partialTick);
            if (alpha <= 0) {
                continue;
            }

            poseStack.pushPose();
            poseStack.translate(Mth.lerp(partialTick, popup.lastX, popup.x) - cam.x, Mth.lerp(partialTick, popup.lastY, popup.y) - cam.y, Mth.lerp(partialTick, popup.lastZ, popup.z) - cam.z);
            poseStack.rotate(camera.orientation);
            poseStack.scale(TEXT_SCALE, -TEXT_SCALE, TEXT_SCALE);
            // 1.2.5 drew the number four times around itself in the background colour; an outline is the same look.
            collector.submitText(poseStack, popup.offset, 0.0F, popup.text, false, Font.DisplayMode.NORMAL, LightCoordsUtil.FULL_BRIGHT,
                    alpha << 24 | popup.color, 0, alpha << 24);
            poseStack.popPose();
        }
    }
}
