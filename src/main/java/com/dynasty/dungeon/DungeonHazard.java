package com.dynasty.dungeon;

import net.minecraft.nbt.CompoundTag;

/** A contact clock owned by a room, never by a client animation or an unloaded BE. */
public final class DungeonHazard implements DungeonMechanism {
    private final int warning, active, recovery, pulseTicks, contactDelay;
    private Phase phase = Phase.IDLE;
    private int ticks, warningGear;
    private long lastUpdate = -1;
    private boolean contact;

    public DungeonHazard(int warning, int active, int recovery) {
        this(warning,active,recovery,0);
    }
    public DungeonHazard(int warning, int active, int recovery, int pulseTicks) {
        this(warning,active,recovery,pulseTicks,0);
    }
    public DungeonHazard(int warning, int active, int recovery, int pulseTicks,int contactDelay) {
        if (warning < 10 || warning > 30 || active < 1 || recovery < 1||contactDelay<0||contactDelay>=active)
            throw new IllegalArgumentException("Invalid hazard timing");
        this.warning = warning; this.active = active; this.recovery = recovery;
        this.pulseTicks=Math.max(0,pulseTicks);
        this.contactDelay=contactDelay;
    }
    public Phase phase() { return phase; }
    public int ticks() { return ticks; }
    /** One native paid fitting, while idle; damage, active contacts and recovery remain original. */
    public boolean fitWarningGear(){
        if(phase!=Phase.IDLE||warningGear!=0||warning>=30)return false;
        warningGear=Math.min(5,30-warning);return true;
    }
    public int warningGear(){return warningGear;}

    DungeonHazard upgradeIdleArrowVolley() {
        // Old v1 saves contain a single four-tick pulse. Let an in-flight cycle
        // finish unchanged, then adopt the new volley without replaying damage.
        if(pulseTicks!=0||active!=4||phase!=Phase.IDLE)return this;
        var upgraded=new DungeonHazard(warning,6,recovery,2);upgraded.load(save());return upgraded;
    }
    public int duration() { return switch (phase) { case WARNING -> warning+warningGear; case ACTIVE -> active; case RECOVERY -> recovery; default -> 1; }; }
    @Override public void trigger(long time) {
        if (phase != Phase.IDLE) return;
        phase = Phase.WARNING; ticks = 0; lastUpdate = time; contact = false;
    }
    @Override public void tickActive(long time) {
        long delta = lastUpdate < 0 ? 0 : time - lastUpdate;
        lastUpdate = time;
        if (delta < 0 || delta > 4) {
            // A delayed mechanical stroke must re-warn after a core unload or
            // time jump. A newly arriving player never inherits a half-fallen blade.
            if(contactDelay>0&&phase!=Phase.IDLE){phase=Phase.WARNING;ticks=0;contact=false;}
            return;
        }
        if(phase == Phase.IDLE) return;
        int previous=ticks;ticks += (int)delta;
        if (ticks < duration()) {
            if(phase==Phase.ACTIVE){
                if(previous<contactDelay&&ticks>=contactDelay)contact=true;
                else if(pulseTicks>0&&previous>=contactDelay&&(ticks-contactDelay)/pulseTicks>(previous-contactDelay)/pulseTicks)contact=true;
            }
            return;
        }
        ticks = 0;
        phase = switch (phase) { case WARNING -> Phase.ACTIVE; case ACTIVE -> Phase.RECOVERY; default -> Phase.IDLE; };
        contact = phase == Phase.ACTIVE&&contactDelay==0;
    }
    public void pause(long time) { lastUpdate = time; contact = false; }
    public boolean consumeContact() { boolean hit = contact; contact = false; return hit; }
    @Override public void reset() { phase = Phase.IDLE; ticks = 0; lastUpdate = -1; contact = false; }
    @Override public void complete() { reset(); }
    @Override public void syncVisual() { }
    @Override public CompoundTag save() {
        var tag = new CompoundTag();
        tag.putInt("Warning", warning); tag.putInt("Active", active); tag.putInt("Recovery", recovery);
        tag.putInt("PulseTicks",pulseTicks);tag.putInt("WarningGear",warningGear);
        tag.putInt("ContactDelay",contactDelay);
        tag.putString("Phase", phase.name()); tag.putInt("Ticks", ticks); tag.putLong("LastUpdate", lastUpdate);
        return tag;
    }
    @Override public void load(CompoundTag tag) {
        warningGear=Math.max(0,Math.min(Math.min(5,30-warning),tag.getInt("WarningGear")));
        try { phase = Phase.valueOf(tag.getString("Phase")); } catch (IllegalArgumentException e) { phase = Phase.IDLE; }
        ticks = Math.max(0, Math.min(duration() - 1, tag.getInt("Ticks")));
        lastUpdate = tag.contains("LastUpdate") ? tag.getLong("LastUpdate") : -1;
        contact = false;
    }
    static DungeonHazard restore(CompoundTag tag) {
        var clock = new DungeonHazard(Math.max(10, Math.min(30, tag.getInt("Warning"))),
            Math.max(1, Math.min(1200, tag.getInt("Active"))), Math.max(1, Math.min(1200, tag.getInt("Recovery"))),
            Math.max(0,Math.min(1200,tag.getInt("PulseTicks"))),
            Math.max(0,Math.min(Math.max(1,Math.min(1200,tag.getInt("Active")))-1,tag.getInt("ContactDelay"))));
        clock.load(tag); return clock;
    }
}
