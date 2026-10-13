package com.dynasty.blueprint.boss;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.*;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.saveddata.SavedData;
import java.util.*;

/** One boss UUID per authored platform; only its confirmed death unlocks the central rope. */
public final class StargazerPlatformState extends SavedData {
    public static final class Platform {
        public final BlockPos centre;
        public UUID boss;
        public boolean defeated;
        public long victoryAt=-1;
        public int ropeY=Integer.MIN_VALUE;
        public final Set<Long> removed=new HashSet<>();
        public final Map<Long,Long> charred=new LinkedHashMap<>();
        public Platform(BlockPos p){centre=p.immutable();}
    }
    public final Map<Long,Platform> platforms=new LinkedHashMap<>();
    public final Set<UUID> firstRewarded=new HashSet<>();
    public static StargazerPlatformState get(ServerLevel w){return w.getDataStorage().computeIfAbsent(StargazerPlatformState::load,StargazerPlatformState::new,"dynasty_cod1_stargazer_platforms_v1");}
    public Platform register(BlockPos p){var entry=platforms.get(p.asLong());if(entry==null){entry=new Platform(p);platforms.put(p.asLong(),entry);setDirty();}return entry;}
    public static StargazerPlatformState load(CompoundTag t){var s=new StargazerPlatformState();for(var row:t.getList("Platforms",10)){var n=(CompoundTag)row;var p=new Platform(BlockPos.of(n.getLong("Centre")));p.boss=n.hasUUID("Boss")?n.getUUID("Boss"):null;p.defeated=n.getBoolean("Defeated");p.victoryAt=n.contains("VictoryAt")?n.getLong("VictoryAt"):-1;p.ropeY=n.contains("RopeY")?n.getInt("RopeY"):Integer.MIN_VALUE;for(long pos:n.getLongArray("Removed"))if(p.removed.size()<StargazerPlatforms.FLOOR_LOSS_CAP&&StargazerPlatforms.breakableCell(p.centre,BlockPos.of(pos)))p.removed.add(pos);for(var entry:n.getList("Charred",10)){var v=(CompoundTag)entry;long pos=v.getLong("Pos");if(p.charred.size()+p.removed.size()<StargazerPlatforms.FLOOR_LOSS_CAP&&!p.removed.contains(pos)&&StargazerPlatforms.breakableCell(p.centre,BlockPos.of(pos)))p.charred.put(pos,v.getLong("At"));}s.platforms.put(p.centre.asLong(),p);}for(var row:t.getList("FirstRewarded",10)){var n=(CompoundTag)row;if(n.hasUUID("Id"))s.firstRewarded.add(n.getUUID("Id"));}return s;}
    @Override public CompoundTag save(CompoundTag t){t.putInt("Version",1);var rows=new ListTag();for(var p:platforms.values()){var n=new CompoundTag();n.putLong("Centre",p.centre.asLong());if(p.boss!=null)n.putUUID("Boss",p.boss);n.putBoolean("Defeated",p.defeated);n.putLong("VictoryAt",p.victoryAt);n.putInt("RopeY",p.ropeY);n.putLongArray("Removed",p.removed.stream().mapToLong(Long::longValue).toArray());var scars=new ListTag();for(var e:p.charred.entrySet()){var v=new CompoundTag();v.putLong("Pos",e.getKey());v.putLong("At",e.getValue());scars.add(v);}n.put("Charred",scars);rows.add(n);}t.put("Platforms",rows);var players=new ListTag();for(var id:firstRewarded){var n=new CompoundTag();n.putUUID("Id",id);players.add(n);}t.put("FirstRewarded",players);return t;}
}
