package com.dynasty.puzzle;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.StringTag;
import net.minecraft.nbt.Tag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.saveddata.SavedData;

import java.util.HashMap;
import java.util.Map;

/**
 * 房间状态存档：每个世界一份（挂在主世界 DataStorage）。
 *
 * 键 = {@link PuzzleRules#roomKey}（维度 + 控制器坐标）→ 同一模板多次放置天然是不同房间，
 * 不会沿用模板里写死的身份；区块卸载/服务器重启后状态保留。
 */
public final class PuzzleSavedData extends SavedData {

    public static final String FILE_ID = "dynasty_puzzles";
    private static final String TAG_ROOMS = "rooms";
    private static final String TAG_KEY = "key";
    private static final String TAG_LINE = "line";

    private final Map<String, PuzzleRoomState> rooms = new HashMap<>();

    public static PuzzleSavedData get(ServerLevel level) {
        return level.getServer().overworld().getDataStorage()
                .computeIfAbsent(PuzzleSavedData::load, PuzzleSavedData::new, FILE_ID);
    }

    public PuzzleRoomState state(String roomKey, PuzzleRules.Kind kind, int layout) {
        PuzzleRoomState state = rooms.get(roomKey);
        if (state == null || state.kind() != kind) {
            state = new PuzzleRoomState(kind, layout);
            rooms.put(roomKey, state);
            setDirty();
        }
        return state;
    }

    public PuzzleRoomState existing(String roomKey) {
        return rooms.get(roomKey);
    }

    public int size() {
        return rooms.size();
    }

    public static PuzzleSavedData load(CompoundTag tag) {
        PuzzleSavedData data = new PuzzleSavedData();
        ListTag list = tag.getList(TAG_ROOMS, Tag.TAG_COMPOUND);
        for (int i = 0; i < list.size(); i++) {
            CompoundTag entry = list.getCompound(i);
            String key = entry.getString(TAG_KEY);
            PuzzleRoomState state = PuzzleRoomState.fromLine(entry.getString(TAG_LINE));
            if (!key.isEmpty() && state != null) {
                data.rooms.put(key, state);
            }
        }
        return data;
    }

    @Override
    public CompoundTag save(CompoundTag tag) {
        ListTag list = new ListTag();
        for (Map.Entry<String, PuzzleRoomState> entry : rooms.entrySet()) {
            CompoundTag record = new CompoundTag();
            record.putString(TAG_KEY, entry.getKey());
            record.putString(TAG_LINE, entry.getValue().toLine());
            list.add(record);
        }
        tag.put(TAG_ROOMS, list);
        return tag;
    }
}
