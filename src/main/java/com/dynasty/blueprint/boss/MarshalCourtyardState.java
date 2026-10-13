package com.dynasty.blueprint.boss;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.*;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.saveddata.SavedData;
import java.util.*;

public final class MarshalCourtyardState extends SavedData {
    public static final class Yard {
        public final BlockPos centre;
        public UUID boss,memorial;
        public long victoryAt=-1;
        public boolean defeated;
        public int environmentCursor;
        public Yard(BlockPos p){centre=p.immutable();}
    }
    public final Map<Long,Yard> yards=new LinkedHashMap<>();
    public final Set<UUID> firstRewarded=new HashSet<>(),bladeClaimed=new HashSet<>();
    public static MarshalCourtyardState get(ServerLevel w){return w.getDataStorage().computeIfAbsent(MarshalCourtyardState::load,MarshalCourtyardState::new,"dynasty_cod1_marshal_yards_v1");}
    public Yard register(BlockPos p){var yard=yards.get(p.asLong());if(yard==null){yard=new Yard(p);yards.put(p.asLong(),yard);setDirty();}return yard;}
    public static MarshalCourtyardState load(CompoundTag t){var s=new MarshalCourtyardState();for(var row:t.getList("Yards",10)){var n=(CompoundTag)row;var y=new Yard(BlockPos.of(n.getLong("Centre")));y.boss=n.hasUUID("Boss")?n.getUUID("Boss"):null;y.defeated=n.getBoolean("Defeated");y.memorial=n.hasUUID("Memorial")?n.getUUID("Memorial"):null;y.victoryAt=n.contains("VictoryAt")?n.getLong("VictoryAt"):-1;y.environmentCursor=Math.max(0,Math.min(64,n.getInt("EnvironmentCursor")));s.yards.put(y.centre.asLong(),y);}for(var row:t.getList("FirstRewarded",10)){var n=(CompoundTag)row;if(n.hasUUID("Id"))s.firstRewarded.add(n.getUUID("Id"));}for(var row:t.getList("BladeClaimed",10)){var n=(CompoundTag)row;if(n.hasUUID("Id"))s.bladeClaimed.add(n.getUUID("Id"));}return s;}
    @Override public CompoundTag save(CompoundTag t){var rows=new ListTag();for(var y:yards.values()){var n=new CompoundTag();n.putLong("Centre",y.centre.asLong());n.putBoolean("Defeated",y.defeated);n.putInt("EnvironmentCursor",y.environmentCursor);if(y.boss!=null)n.putUUID("Boss",y.boss);if(y.memorial!=null)n.putUUID("Memorial",y.memorial);n.putLong("VictoryAt",y.victoryAt);rows.add(n);}t.put("Yards",rows);var rewards=new ListTag();for(var id:firstRewarded){var n=new CompoundTag();n.putUUID("Id",id);rewards.add(n);}t.put("FirstRewarded",rewards);var blades=new ListTag();for(var id:bladeClaimed){var n=new CompoundTag();n.putUUID("Id",id);blades.add(n);}t.put("BladeClaimed",blades);t.putInt("Version",2);return t;}
}
