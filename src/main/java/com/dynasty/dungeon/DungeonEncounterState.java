package com.dynasty.dungeon;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.StringTag;
import net.minecraft.resources.ResourceLocation;
import java.util.HashSet;
import java.util.Set;
import java.util.UUID;

/** An unloaded boss remains reserved. Only its confirmed death completes the encounter. */
public final class DungeonEncounterState {
    public enum Phase { READY, STARTING, ACTIVE, DEFEATED }
    private Phase phase=Phase.READY;
    private UUID attempt,boss;
    private ResourceLocation bossType;
    private final Set<UUID> participants=new HashSet<>();

    public Phase phase(){return phase;}
    public UUID attempt(){return attempt;}
    public UUID boss(){return boss;}
    public ResourceLocation bossType(){return bossType;}
    public boolean participant(UUID player){return participants.contains(player);}
    public boolean join(UUID player){return phase==Phase.ACTIVE&&participants.size()<64&&participants.add(player);}
    public boolean reserve(ResourceLocation type){
        if(phase!=Phase.READY)return false;
        bossType=type;attempt=UUID.randomUUID();phase=Phase.STARTING;return true;
    }
    public boolean activate(UUID actor){
        if(phase!=Phase.STARTING||actor==null||attempt==null||bossType==null)return false;
        boss=actor;phase=Phase.ACTIVE;return true;
    }
    public boolean defeat(UUID actor,ResourceLocation type,UUID token){
        if(phase!=Phase.ACTIVE||!boss.equals(actor)||!bossType.equals(type)||!attempt.equals(token))return false;
        phase=Phase.DEFEATED;return true;
    }
    public CompoundTag save(){
        var tag=new CompoundTag();tag.putString("Phase",phase.name());
        if(attempt!=null)tag.putUUID("Attempt",attempt);
        if(boss!=null)tag.putUUID("Boss",boss);
        if(bossType!=null)tag.putString("BossType",bossType.toString());
        var players=new ListTag();participants.forEach(p->players.add(StringTag.valueOf(p.toString())));tag.put("Participants",players);
        return tag;
    }
    public static DungeonEncounterState load(CompoundTag tag){
        var state=new DungeonEncounterState();
        // Invalid nonempty saves fail closed instead of spawning a replacement boss.
        try{state.phase=Phase.valueOf(tag.getString("Phase"));}catch(IllegalArgumentException ignored){state.phase=Phase.STARTING;}
        state.attempt=tag.hasUUID("Attempt")?tag.getUUID("Attempt"):null;
        state.boss=tag.hasUUID("Boss")?tag.getUUID("Boss"):null;
        state.bossType=ResourceLocation.tryParse(tag.getString("BossType"));
        if(state.phase!=Phase.READY&&(state.attempt==null||state.bossType==null
                ||state.phase!=Phase.STARTING&&state.boss==null))state.phase=Phase.STARTING;
        for(var player:tag.getList("Participants",8))if(state.participants.size()<64)try{
            state.participants.add(UUID.fromString(player.getAsString()));
        }catch(IllegalArgumentException ignored){}
        return state;
    }
}
