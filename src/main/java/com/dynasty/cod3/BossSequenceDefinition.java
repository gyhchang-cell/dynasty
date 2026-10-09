package com.dynasty.cod3;

import com.google.gson.Gson;
import com.google.gson.JsonObject;
import java.util.Comparator;
import java.util.List;
import java.util.Objects;

/** Immutable authoring contract. A supported data type does not imply a bound scene executor. */
public record BossSequenceDefinition(String id, String name, int totalTicks, String arenaTag,
                                     List<String> bossIds, List<Step> steps) {
    private static final Gson JSON = new Gson();

    public enum Type {
        WAIT, PLAY_BOSS_ANIMATION, SET_BOSS_VISIBILITY, SET_BOSS_INVULNERABLE,
        PLAY_SOUND, SPAWN_CLIENT_VFX, SPAWN_VISUAL_ENTITY, SET_ARENA_STATE,
        SET_BLOCK_PRESET_STATE, CAMERA_SHAKE_LOCAL, SHOW_BOSSBAR, SET_BOSS_PHASE,
        SET_MODEL_VARIANT, FOG_LOCAL, LIGHTNING_VISUAL, DIALOGUE, TRIGGER_WORLD_STATE
    }

    public record Step(int startTick, int duration, Type type, int vfx, double radius,
                       String detail, JsonObject params) {
        public Step(int startTick, int duration, Type type, int vfx, double radius, String detail) {
            this(startTick, duration, type, vfx, radius, detail, new JsonObject());
        }

        public Step {
            Objects.requireNonNull(type, "Unknown or missing sequence step type");
            if (startTick < 0 || duration < 0 || duration > 1200
                    || !Double.isFinite(radius) || radius < 0 || radius > 96)
                throw new IllegalArgumentException("Invalid sequence step bounds");
            if (type == Type.SPAWN_CLIENT_VFX && (vfx < 1 || vfx > 40 || duration == 0 || radius == 0))
                throw new IllegalArgumentException("Invalid sequence VFX");
            detail = detail == null ? "" : detail;
            params = params == null ? new JsonObject() : params.deepCopy();
        }

        // Do not let a caller mutate the shared catalogue through JSON parameters.
        @Override public JsonObject params() { return params.deepCopy(); }
        public boolean booleanParam(String key, boolean fallback) {
            return params.has(key) ? params.get(key).getAsBoolean() : fallback;
        }
        public String stringParam(String key, String fallback) {
            return params.has(key) ? params.get(key).getAsString() : fallback;
        }
        public int visualDuration() { return Math.min(120, duration); }
        public boolean visualActiveAt(int tick) {
            return type == Type.SPAWN_CLIENT_VFX && tick >= startTick && tick - startTick < visualDuration();
        }
        /** Death scenes cannot unlock combat or grant story rewards through steps. */
        public boolean allowedDuringDeath() {
            return switch (type) {
                case PLAY_BOSS_ANIMATION, SET_BOSS_VISIBILITY, PLAY_SOUND, SPAWN_CLIENT_VFX,
                     SET_ARENA_STATE, SET_BLOCK_PRESET_STATE, FOG_LOCAL, LIGHTNING_VISUAL, DIALOGUE -> true;
                default -> false;
            };
        }
    }

    public BossSequenceDefinition {
        if (id == null || id.isBlank() || id.length() > 128 || name == null || arenaTag == null)
            throw new IllegalArgumentException("Missing sequence identity");
        if (totalTicks < 20 || totalTicks > 1200)
            throw new IllegalArgumentException("Sequence duration outside budget");
        bossIds = List.copyOf(bossIds);
        steps = steps.stream().sorted(Comparator.comparingInt(Step::startTick)).toList();
        for (var step : steps) {
            if (step.startTick() >= totalTicks || step.duration() > totalTicks - step.startTick())
                throw new IllegalArgumentException("Step extends beyond sequence: " + id);
        }
    }
    public String toJson() { return JSON.toJson(this); }
    public static BossSequenceDefinition fromJson(String json) {
        return Objects.requireNonNull(JSON.fromJson(json, BossSequenceDefinition.class), "Missing sequence");
    }
}
