package com.dynasty.worldevent;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.saveddata.SavedData;
import java.util.*;

public final class WorldEventStore extends SavedData {
    public final Map<UUID,WorldEventInstance> instances=new LinkedHashMap<>();
    public final Map<String,Long> cooldowns=new HashMap<>();
    public final Set<String> worldStates=new HashSet<>();
    public static WorldEventStore get(ServerLevel level){return level.getDataStorage().computeIfAbsent(WorldEventStore::load,WorldEventStore::new,"dynasty_world_events_v1");}
    public static WorldEventStore load(CompoundTag root){
        var out=new WorldEventStore();for(var e:root.getList("Instances",10))if(out.instances.size()<256){var i=WorldEventInstance.load((CompoundTag)e);if(i!=null)out.instances.put(i.uuid,i);}
        var timers=root.getCompound("Cooldowns");for(String k:timers.getAllKeys())if(out.cooldowns.size()<4096)out.cooldowns.put(k,timers.getLong(k));
        for(var s:root.getList("WorldStates",8))if(out.worldStates.size()<128)out.worldStates.add(s.getAsString());return out;
    }
    @Override public CompoundTag save(CompoundTag root){
        root.putInt("Version",1);var list=new net.minecraft.nbt.ListTag();instances.values().forEach(i->list.add(i.save()));root.put("Instances",list);
        var timers=new CompoundTag();cooldowns.forEach(timers::putLong);root.put("Cooldowns",timers);var states=new net.minecraft.nbt.ListTag();worldStates.forEach(s->states.add(net.minecraft.nbt.StringTag.valueOf(s)));root.put("WorldStates",states);return root;
    }
}
