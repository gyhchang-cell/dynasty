package com.dynasty.dungeon;

import net.minecraft.nbt.CompoundTag;

/** An occupied-time warning and damage pulse; downtime never catches up damage. */
public final class DungeonExposure {
    public enum Contact {NONE, WARNING, DAMAGE}
    public static final int WARNING_TICKS=40, PULSE_TICKS=20;
    private String zone="";
    private int occupiedTicks;
    private long lastUpdate=-1;

    public Contact tick(String nextZone,long time) {
        if(nextZone.isEmpty()) {zone="";occupiedTicks=0;lastUpdate=time;return Contact.NONE;}
        if(!nextZone.equals(zone)) {
            zone=nextZone;occupiedTicks=0;lastUpdate=time;return Contact.WARNING;
        }
        long delta=lastUpdate<0?0:time-lastUpdate;lastUpdate=time;
        if(delta>4||delta<0) {occupiedTicks=0;return Contact.WARNING;}
        if(delta==0)return Contact.NONE;
        int before=occupiedTicks;
        occupiedTicks=Math.min(WARNING_TICKS+PULSE_TICKS,occupiedTicks+(int)delta);
        if(before<WARNING_TICKS&&occupiedTicks>=WARNING_TICKS)return Contact.DAMAGE;
        if(occupiedTicks>=WARNING_TICKS+PULSE_TICKS) {occupiedTicks=WARNING_TICKS;return Contact.DAMAGE;}
        return Contact.NONE;
    }
    public CompoundTag save() {
        var tag=new CompoundTag();tag.putString("Zone",zone);tag.putInt("Ticks",occupiedTicks);tag.putLong("LastUpdate",lastUpdate);return tag;
    }
    public static DungeonExposure load(CompoundTag tag) {
        var exposure=new DungeonExposure();exposure.zone=tag.getString("Zone");
        exposure.occupiedTicks=Math.max(0,Math.min(WARNING_TICKS+PULSE_TICKS,tag.getInt("Ticks")));
        exposure.lastUpdate=tag.contains("LastUpdate")?tag.getLong("LastUpdate"):-1;return exposure;
    }
}
