package com.dynasty.blueprint.boss;

import net.minecraft.core.BlockPos;
import net.minecraft.nbt.*;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.saveddata.SavedData;
import java.util.*;

/** Null entity lookup is unload, never victory. Arena environment edits have a resumable cursor. */
public final class CauldronPitState extends SavedData {
    public static final class Pit {
        public final BlockPos centre;
        public int ritualMask,environmentCursor;
        public UUID boss;
        public boolean defeated;
        public Pit(BlockPos centre){this.centre=centre.immutable();}
    }
    public final Map<Long,Pit> pits=new LinkedHashMap<>();
    public final Set<UUID> firstRewarded=new HashSet<>();
    public static CauldronPitState get(ServerLevel world){return world.getDataStorage().computeIfAbsent(CauldronPitState::load,CauldronPitState::new,"dynasty_cod1_cauldron_pits_v1");}
    public Pit register(BlockPos centre){var pit=pits.get(centre.asLong());if(pit==null){pit=new Pit(centre);pits.put(centre.asLong(),pit);setDirty();}return pit;}
    public static CauldronPitState load(CompoundTag tag){var state=new CauldronPitState();for(var row:tag.getList("Pits",10)){var t=(CompoundTag)row;var pit=new Pit(BlockPos.of(t.getLong("Centre")));pit.ritualMask=Math.max(0,Math.min(7,t.getInt("RitualMask")));pit.environmentCursor=Math.max(0,Math.min(2000,t.getInt("EnvironmentCursor")));pit.defeated=t.getBoolean("Defeated");pit.boss=t.hasUUID("Boss")?t.getUUID("Boss"):null;state.pits.put(pit.centre.asLong(),pit);}for(var row:tag.getList("FirstRewarded",10)){var t=(CompoundTag)row;if(t.hasUUID("Id"))state.firstRewarded.add(t.getUUID("Id"));}return state;}
    @Override public CompoundTag save(CompoundTag tag){var rows=new ListTag();for(var pit:pits.values()){var t=new CompoundTag();t.putLong("Centre",pit.centre.asLong());t.putInt("RitualMask",pit.ritualMask);t.putInt("EnvironmentCursor",pit.environmentCursor);t.putBoolean("Defeated",pit.defeated);if(pit.boss!=null)t.putUUID("Boss",pit.boss);rows.add(t);}tag.put("Pits",rows);var rewards=new ListTag();for(var id:firstRewarded){var t=new CompoundTag();t.putUUID("Id",id);rewards.add(t);}tag.put("FirstRewarded",rewards);tag.putInt("Version",1);return tag;}
}
