package com.dynasty.cod3;

import com.dynasty.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.*;
import net.minecraft.sounds.*;
import net.minecraft.world.entity.Mob;
import net.minecraftforge.event.entity.EntityJoinLevelEvent;
import net.minecraftforge.event.entity.living.LivingEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.*;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;

@Mod.EventBusSubscriber(modid=Dynasty.MODID)
public final class BossSequenceRunner {
    public static final String KEY="dynasty_cod3_intro";
    public static boolean active(Mob boss) {
        return boss.getPersistentData().contains(KEY) && !boss.getPersistentData().getCompound(KEY).getBoolean("Finished");
    }
    public static boolean start(Mob boss) { return start(boss, 0); }
    public static boolean start(Mob boss, int previewTicks) {
        if (!(boss.level() instanceof ServerLevel) || !boss.isAlive() || BossDeathState.managed(boss)) return false;
        var def = definition(boss);
        if (def == null || boss.getPersistentData().contains(KEY)) return false;
        int preview = Math.max(0, Math.min(20, previewTicks));
        CompoundTag state = new CompoundTag();
        state.putString("Id", def.id());
        state.putInt("Tick", 0);
        state.putInt("Watchdog", 0);
        state.putInt("Preview", preview);
        state.putBoolean("Visible", preview == 0);
        boss.getPersistentData().put(KEY, state);
        freeze(boss);
        boss.setPersistenceRequired();
        boss.setInvisible(preview > 0);
        return true;
    }
    private static BossSequenceDefinition definition(Mob boss) {
        var id = ForgeRegistries.ENTITY_TYPES.getKey(boss.getType());
        return id == null ? null : Cod3Catalog.sequence("intros", id.toString());
    }
    private static void freeze(Mob boss) {
        boss.setNoAi(true);
        boss.setInvulnerable(true);
        boss.setTarget(null);
        boss.getNavigation().stop();
        bar(boss, false);
    }
    public static void finish(Mob boss) {
        if (!(boss.level() instanceof ServerLevel)) return;
        var state = boss.getPersistentData().getCompound(KEY);
        state.putBoolean("Finished", true);
        boss.getPersistentData().put(KEY, state);
        boss.setInvulnerable(false);
        boss.setNoAi(false);
        boss.setInvisible(false);
        boss.getPersistentData().remove("dynasty_cod3_visual_stage");
        bar(boss, true);
    }
    private static void bar(Mob boss, boolean show) {
        if (boss instanceof DynastyBossCombat.BarHolder holder) holder.dynastyBossBar().setVisible(show);
    }
    private static boolean validCheckpoint(Mob boss, BossSequenceDefinition def) {
        if (def == null || !boss.getPersistentData().contains(KEY, Tag.TAG_COMPOUND)) return false;
        var state = boss.getPersistentData().getCompound(KEY);
        return state.contains("Tick", Tag.TAG_INT) && def.id().equals(state.getString("Id"))
                && state.getInt("Tick") >= 0 && state.getInt("Tick") <= def.totalTicks()
                && state.getInt("Watchdog") >= 0 && state.getInt("Watchdog") < def.totalTicks() + 40
                && state.getInt("Preview") >= 0 && state.getInt("Preview") <= 20;
    }
    private static void fallback(Mob boss) {
        Dynasty.LOGGER.warn("[Dynasty][BossIntro] forced-to-combat boss={} checkpoint={}",
                boss.getType(), boss.getPersistentData().getCompound(KEY));
        finish(boss);
    }
    public static void tick(Mob boss) {
        if (!active(boss) || BossDeathState.managed(boss) || !(boss.level() instanceof ServerLevel level)) return;
        var def = definition(boss);
        if (!validCheckpoint(boss, def)) { fallback(boss); return; }
        var state = boss.getPersistentData().getCompound(KEY);
        int tick = state.getInt("Tick");
        if (tick >= def.totalTicks()) { finish(boss); return; }
        // Count preview ticks too: neither a damaged preview nor integer overflow can bypass recovery.
        state.putInt("Watchdog", state.getInt("Watchdog") + 1);
        if (state.getInt("Watchdog") >= def.totalTicks() + 40) { fallback(boss); return; }
        freeze(boss);
        if (state.getInt("Preview") > 0) {
            state.putInt("Preview", state.getInt("Preview") - 1);
            return;
        }
        if (tick == 0) { boss.setInvisible(false); state.putBoolean("Visible", true); }
        for (var step : def.steps()) if (step.startTick() == tick) {
            try {
                if (step.type() == BossSequenceDefinition.Type.SPAWN_CLIENT_VFX) Cod3Vfx.sequence(boss, def.id(), tick, step);
                else play(boss, step);
            } catch (RuntimeException e) {
                Dynasty.LOGGER.warn("cod3 sequence step skipped {} type={}", def.id(), step.type(), e);
            }
        }
        // Intro owns these invariants until COMBAT, including definitions containing SET_* steps.
        freeze(boss);
        if (tick == 20) level.playSound(null, boss.blockPosition(), SoundEvents.BEACON_ACTIVATE, SoundSource.HOSTILE, .8f, .75f);
        if (tick % 100 == 0) for (var p : level.players()) if (p.distanceToSqr(boss) <= 32 * 32)
            Cod3Vfx.sync(p, boss, def.id(), tick, def.totalTicks());
        state.putInt("Tick", tick + 1);
        if (tick + 1 == def.totalTicks()) finish(boss);
    }
    public static void play(Mob boss, BossSequenceDefinition.Step step) {
        if (!(boss.level() instanceof ServerLevel level)) return;
        if (BossDeathState.managed(boss) && !step.allowedDuringDeath()) return;
        switch (step.type()) {
            case SPAWN_CLIENT_VFX -> Cod3Vfx.send(level, step.vfx(), boss.position(), boss.getLookAngle(), step.visualDuration(), step.radius()/3);
            case PLAY_SOUND -> {
                var id = ResourceLocation.tryParse(step.stringParam("sound", "minecraft:block.beacon.ambient"));
                var sound = id == null ? null : ForgeRegistries.SOUND_EVENTS.getValue(id);
                if (sound == null) throw new IllegalArgumentException("Unregistered sequence sound");
                level.playSound(null, boss.blockPosition(), sound, SoundSource.HOSTILE, .6f, .8f);
            }
            case SET_BOSS_VISIBILITY -> {
                boolean visible = step.booleanParam("visible", true);
                boss.setInvisible(!visible);
                if (active(boss)) boss.getPersistentData().getCompound(KEY).putBoolean("Visible", visible);
            }
            case SET_BOSS_INVULNERABLE -> boss.setInvulnerable(BossDeathState.managed(boss) || active(boss) || step.booleanParam("invulnerable", true));
            case SHOW_BOSSBAR -> bar(boss, !active(boss) && !BossDeathState.managed(boss) && step.booleanParam("visible", true));
            case SET_MODEL_VARIANT, PLAY_BOSS_ANIMATION -> boss.getPersistentData().putString("dynasty_cod3_visual_stage", step.stringParam("value", step.detail()));
            case WAIT -> {}
            // Scene-specific bindings must be implemented explicitly; never silently execute guessed terrain/camera actions.
            default -> throw new UnsupportedOperationException("Unbound sequence step: " + step.type());
        }
    }
    @SubscribeEvent public static void join(EntityJoinLevelEvent e) {
        if (!(e.getLevel() instanceof ServerLevel) || !(e.getEntity() instanceof Mob boss)
                || !active(boss) || BossDeathState.managed(boss)) return;
        var def = definition(boss);
        if (!validCheckpoint(boss, def)) fallback(boss);
        else if (boss.getPersistentData().getCompound(KEY).getInt("Tick") >= def.totalTicks()) finish(boss);
        else {
            freeze(boss);
            var state = boss.getPersistentData().getCompound(KEY);
            // Entity's transient invisible flag is not restored by vanilla NBT loading.
            boss.setInvisible(state.getInt("Preview") > 0 || state.contains("Visible") && !state.getBoolean("Visible"));
        }
    }
    @SubscribeEvent public static void living(LivingEvent.LivingTickEvent e) {
        if (e.getEntity() instanceof Mob boss && !boss.level().isClientSide && boss.isAlive()) tick(boss);
    }
    @SubscribeEvent public static void tracking(PlayerEvent.StartTracking e) {
        if (e.getEntity() instanceof ServerPlayer p && e.getTarget() instanceof Mob boss && active(boss)
                && !BossDeathState.managed(boss) && p.distanceToSqr(boss) <= 32 * 32) {
            var state = boss.getPersistentData().getCompound(KEY);
            var def = definition(boss);
            if (validCheckpoint(boss, def) && state.getInt("Preview") == 0 && state.getInt("Tick") > 0)
                Cod3Vfx.sync(p, boss, def.id(), state.getInt("Tick") - 1, def.totalTicks());
        }
    }
    private BossSequenceRunner() {}
}
