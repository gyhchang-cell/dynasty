package com.dynasty.dungeon;

/** Timings in server ticks. Every trap warns for 0.5–1.5 seconds and has a finite recovery. */
public enum DungeonTrapProfile {
    CRUSHER("crusher",15,1,14,4,true),CONVEYOR("conveyor",10,60,10,0,false),
    STEAM("steam",20,4,36,3,true),MINE("mine",16,1,60,6,false),
    ARROW_RAIN("arrow_rain",30,40,80,2,true),WIND_FIELD("wind_field",20,60,20,0,true);
    public final String id;public final int warning,active,recovery;public final float damage;public final boolean periodic;
    DungeonTrapProfile(String id,int warning,int active,int recovery,float damage,boolean periodic){
        this.id=id;this.warning=warning;this.active=active;this.recovery=recovery;this.damage=damage;this.periodic=periodic;
    }
    public DungeonHazard clock(){return new DungeonHazard(warning,active,recovery,this==ARROW_RAIN?20:0);}
    public static DungeonTrapProfile forId(String id){for(var p:values())if(id.equals(p.id)||id.startsWith(p.id+"_"))return p;return null;}
}
