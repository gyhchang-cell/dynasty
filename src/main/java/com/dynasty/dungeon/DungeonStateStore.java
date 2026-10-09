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
    private final Map<String,DungeonEncounterState> encounters=new HashMap<>();
    private final Map<String,DungeonRewardReceipt> rewards=new HashMap<>();
    public static DungeonStateStore get(ServerLevel level){
        return level.getDataStorage().computeIfAbsent(DungeonStateStore::load,DungeonStateStore::new,"dynasty_dungeons_v1");
    }
    public DungeonRoomController room(UUID instance,String room){
        String key=instance+"/"+room;
        if(!rooms.containsKey(key)){rooms.put(key,new DungeonRoomController());setDirty();}
        return rooms.get(key);
    }
    public DungeonEncounterState encounter(UUID instance,String dungeon,boolean create){
        String key=instance+"/"+dungeon;
        if(create&&!encounters.containsKey(key)){encounters.put(key,new DungeonEncounterState());setDirty();}
        return encounters.get(key);
    }
    public DungeonRewardReceipt reward(String key){return rewards.get(key);}
    public DungeonRewardReceipt reserveReward(String key,UUID player,java.util.List<net.minecraft.world.item.ItemStack> items){
        if(!rewards.containsKey(key)){
            if(items.isEmpty()||items.size()>128)throw new IllegalArgumentException("Invalid reward bundle");
            rewards.put(key,new DungeonRewardReceipt(player,items));setDirty();
        }
        return rewards.get(key);
    }
    public static DungeonStateStore load(CompoundTag root){
        var data=new DungeonStateStore();
        var saved=root.getCompound("Rooms");
        for(String key:saved.getAllKeys()){
            var room=new DungeonRoomController();room.load(saved.getCompound(key));data.rooms.put(key,room);
        }
        var encounters=root.getCompound("Encounters");
        for(String key:encounters.getAllKeys())data.encounters.put(key,DungeonEncounterState.load(encounters.getCompound(key)));
        var rewards=root.getCompound("Rewards");
        for(String key:rewards.getAllKeys())data.rewards.put(key,DungeonRewardReceipt.load(rewards.getCompound(key)));
        return data;
    }
    @Override public CompoundTag save(CompoundTag root){
        root.putInt("Version",2);var tag=new CompoundTag();rooms.forEach((key,value)->tag.put(key,value.save()));root.put("Rooms",tag);
        var encountersTag=new CompoundTag();encounters.forEach((key,value)->encountersTag.put(key,value.save()));root.put("Encounters",encountersTag);
        var rewardsTag=new CompoundTag();rewards.forEach((key,value)->rewardsTag.put(key,value.save()));root.put("Rewards",rewardsTag);return root;
    }
}
