package com.dynasty.dungeon;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.saveddata.SavedData;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/** Dimension-local keys isolate multiplayer rooms and survive core replacement. */
public final class DungeonStateStore extends SavedData {
    private final Map<String,DungeonRoomController> rooms=new HashMap<>();
    public static DungeonStateStore get(ServerLevel level){
        return level.getDataStorage().computeIfAbsent(DungeonStateStore::load,DungeonStateStore::new,"dynasty_dungeons_v1");
    }
    public DungeonRoomController room(UUID instance,String room){
        String key=instance+"/"+room;
        if(!rooms.containsKey(key)){rooms.put(key,new DungeonRoomController());setDirty();}
        return rooms.get(key);
    }
    public static DungeonStateStore load(CompoundTag root){
        var data=new DungeonStateStore();
        var saved=root.getCompound("Rooms");
        for(String key:saved.getAllKeys()){
            var room=new DungeonRoomController();room.load(saved.getCompound(key));data.rooms.put(key,room);
        }
        return data;
    }
    @Override public CompoundTag save(CompoundTag root){
        root.putInt("Version",1);var tag=new CompoundTag();rooms.forEach((key,value)->tag.put(key,value.save()));root.put("Rooms",tag);return root;
    }
}
