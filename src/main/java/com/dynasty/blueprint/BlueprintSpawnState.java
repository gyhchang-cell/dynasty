package com.dynasty.blueprint;

import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.saveddata.SavedData;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

/** Marker membership remains authoritative while members are in unloaded chunks. Null lookup is NOT death. */
public final class BlueprintSpawnState extends SavedData {
    public static final class Marker {
        public final String key;
        public final BlockPos centre;
        public final Set<UUID> members = new LinkedHashSet<>();
        public int produced;
        public long nextSpawn;
        public boolean cleared;
        public Marker(String key, BlockPos centre) {this.key=key;this.centre=centre.immutable();}
    }
    public final Map<String, Marker> markers = new LinkedHashMap<>();
    public static BlueprintSpawnState get(ServerLevel level) {
        return level.getDataStorage().computeIfAbsent(BlueprintSpawnState::load,BlueprintSpawnState::new,"dynasty_blueprint_spawns_v1");
    }
    public void memberDied(UUID uuid,long time) {
        for(var m:markers.values()) if(m.members.remove(uuid)) {
            m.nextSpawn=time+12000;setDirty();return;
        }
    }
    public static BlueprintSpawnState load(CompoundTag tag) {
        var data=new BlueprintSpawnState();
        for(var entry:tag.getList("Markers",10)) {
            var t=(CompoundTag)entry;var m=new Marker(t.getString("Key"),BlockPos.of(t.getLong("Centre")));
            m.produced=Math.max(0,t.getInt("Produced"));m.nextSpawn=t.getLong("NextSpawn");m.cleared=t.getBoolean("Cleared");
            for(var member:t.getList("Members",10)) {var n=(CompoundTag)member;if(n.hasUUID("Id"))m.members.add(n.getUUID("Id"));}
            data.markers.put(m.key,m);
        }
        return data;
    }
    @Override public CompoundTag save(CompoundTag tag) {
        var list=new ListTag();
        for(var m:markers.values()) {
            var t=new CompoundTag();t.putString("Key",m.key);t.putLong("Centre",m.centre.asLong());
            t.putInt("Produced",m.produced);t.putLong("NextSpawn",m.nextSpawn);t.putBoolean("Cleared",m.cleared);
            var members=new ListTag();for(UUID id:m.members){var n=new CompoundTag();n.putUUID("Id",id);members.add(n);}t.put("Members",members);list.add(t);
        }
        tag.putInt("Version",1);tag.put("Markers",list);return tag;
    }
}
