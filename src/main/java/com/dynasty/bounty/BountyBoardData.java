package com.dynasty.bounty;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.StringTag;
import net.minecraft.nbt.Tag;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.saveddata.SavedData;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * 委托存档：**每个世界一份**（挂在主世界的 DataStorage 上）。
 *
 * 为什么用 SavedData 而不是 Capability：
 *   * 需求要求「按玩家 UUID 保存 / 重启与死亡重生后保留 / 区分不同世界」——SavedData 天然按存档隔离，
 *     死亡重生不影响（不挂在实体上），专用服务器也不需要客户端类；
 *   * 数据结构就是「UUID → 纯文本行」，用 {@link BountyStateMachine} 的行格式读写，
 *     反序列化对坏行容错（不会因为一条坏记录让服务器起不来）；
 *   * 不使用 FTB 任务 ID，也不写任何 FTB 数据。
 *
 * Per-world SavedData keyed by player UUID. No Capability needed: the state is plain lines.
 */
public final class BountyBoardData extends SavedData {

    public static final String FILE_ID = "dynasty_bounty";
    private static final String TAG_PLAYERS = "players";
    private static final String TAG_ID = "id";
    private static final String TAG_LINES = "lines";

    private final Map<UUID, BountyStateMachine> players = new HashMap<>();

    public static BountyBoardData get(ServerLevel level) {
        MinecraftServer server = level.getServer();
        ServerLevel overworld = server.overworld();
        return overworld.getDataStorage().computeIfAbsent(BountyBoardData::load, BountyBoardData::new, FILE_ID);
    }

    public BountyStateMachine stateOf(UUID playerId) {
        BountyStateMachine state = players.get(playerId);
        if (state == null) {
            state = new BountyStateMachine();
            players.put(playerId, state);
            setDirty();
        }
        return state;
    }

    public int knownPlayers() {
        return players.size();
    }

    public static BountyBoardData load(CompoundTag tag) {
        BountyBoardData data = new BountyBoardData();
        ListTag list = tag.getList(TAG_PLAYERS, Tag.TAG_COMPOUND);
        for (int i = 0; i < list.size(); i++) {
            CompoundTag entry = list.getCompound(i);
            try {
                UUID id = UUID.fromString(entry.getString(TAG_ID));
                ListTag lines = entry.getList(TAG_LINES, Tag.TAG_STRING);
                data.players.put(id, BountyStateMachine.fromLines(
                        lines.stream().map(Tag::getAsString).toList()));
            } catch (RuntimeException ignored) {
                // 单个玩家记录坏了就跳过，不影响其他人
            }
        }
        return data;
    }

    @Override
    public CompoundTag save(CompoundTag tag) {
        ListTag list = new ListTag();
        for (Map.Entry<UUID, BountyStateMachine> entry : players.entrySet()) {
            CompoundTag record = new CompoundTag();
            record.putString(TAG_ID, entry.getKey().toString());
            ListTag lines = new ListTag();
            for (String line : entry.getValue().toLines()) {
                lines.add(StringTag.valueOf(line));
            }
            record.put(TAG_LINES, lines);
            list.add(record);
        }
        tag.put(TAG_PLAYERS, list);
        return tag;
    }

    /** 供测试与诊断：导出某个玩家的存档行。 */
    public List<String> dump(UUID playerId) {
        return stateOf(playerId).toLines();
    }
}
