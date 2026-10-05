package com.dynasty.dungeon;

import net.minecraft.nbt.CompoundTag;

/** A contact clock owned by a room, never by a client animation or an unloaded BE. */
public final class DungeonHazard implements DungeonMechanism {
    private final int warning, active, recovery;
    private Phase phase = Phase.IDLE;
    private int ticks;
    private long lastUpdate = -1;
    private boolean contact;

    public DungeonHazard(int warning, int active, int recovery) {
        if (warning < 10 || warning > 30 || active < 1 || recovery < 1)
            throw new IllegalArgumentException("Invalid hazard timing");
        this.warning = warning; this.active = active; this.recovery = recovery;
    }
    public Phase phase() { return phase; }
    public int ticks() { return ticks; }
    public int duration() { return switch (phase) { case WARNING -> warning; case ACTIVE -> active; case RECOVERY -> recovery; default -> 1; }; }
    @Override public void trigger(long time) {
        if (phase != Phase.IDLE) return;
        phase = Phase.WARNING; ticks = 0; lastUpdate = time; contact = false;
    }
    @Override public void tickActive(long time) {
        long delta = lastUpdate < 0 ? 0 : time - lastUpdate;
        lastUpdate = time;
        if (delta < 0 || delta > 4 || phase == Phase.IDLE) return;
        ticks += (int)delta;
        if (ticks < duration()) return;
        ticks = 0;
        phase = switch (phase) { case WARNING -> Phase.ACTIVE; case ACTIVE -> Phase.RECOVERY; default -> Phase.IDLE; };
        contact = phase == Phase.ACTIVE;
    }
    public void pause(long time) { lastUpdate = time; contact = false; }
    public boolean consumeContact() { boolean hit = contact; contact = false; return hit; }
    @Override public void reset() { phase = Phase.IDLE; ticks = 0; lastUpdate = -1; contact = false; }
    @Override public void complete() { reset(); }
    @Override public void syncVisual() { }
    @Override public CompoundTag save() {
        var tag = new CompoundTag();
        tag.putInt("Warning", warning); tag.putInt("Active", active); tag.putInt("Recovery", recovery);
        tag.putString("Phase", phase.name()); tag.putInt("Ticks", ticks); tag.putLong("LastUpdate", lastUpdate);
        return tag;
    }
    @Override public void load(CompoundTag tag) {
        try { phase = Phase.valueOf(tag.getString("Phase")); } catch (IllegalArgumentException e) { phase = Phase.IDLE; }
        ticks = Math.max(0, Math.min(duration() - 1, tag.getInt("Ticks")));
        lastUpdate = tag.contains("LastUpdate") ? tag.getLong("LastUpdate") : -1;
        contact = false;
    }
    static DungeonHazard restore(CompoundTag tag) {
        var clock = new DungeonHazard(Math.max(10, Math.min(30, tag.getInt("Warning"))),
            Math.max(1, Math.min(1200, tag.getInt("Active"))), Math.max(1, Math.min(1200, tag.getInt("Recovery"))));
        clock.load(tag); return clock;
    }
}
