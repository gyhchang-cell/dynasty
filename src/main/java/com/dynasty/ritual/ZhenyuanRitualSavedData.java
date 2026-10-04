package com.dynasty.ritual;

import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.saveddata.SavedData;

import java.util.Collection;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.UUID;

/** One durable ledger in the overworld. No static world/session state crosses servers. */
public final class ZhenyuanRitualSavedData extends SavedData {
    public static final String FILE_ID = "dynasty_zhenyuan_rituals";
    final Map<String, Session> sessions = new LinkedHashMap<>();
    int nextArena;

    public static final class Session {
        public String key;
        public String dimension;
        public BlockPos core;
        public UUID owner;
        public UUID boss;
        public final java.util.Set<UUID> participants = new java.util.LinkedHashSet<>();
        public CompoundTag bossSnapshot = new CompoundTag();
        public String phase = "idle";
        public int mask;
        public boolean phaseOne;
        public int pendingMask;
        public int[] offeringTicks = new int[4];
        public int[] completionOrder = new int[4];
        public UUID[] offeringPlayers = new UUID[4];
        public int ritualTicks;
        public String ritualStage = "OFFERINGS";
        public boolean finalOfferingReady, ritualRunning, bossFightStarted, bossDefeated;
        public int arenaIndex = -1;
        public boolean arenaReady;
        public int bossIntroTick;
        public long chargeEnds;
        public long victoryAt;
        public float yaw;
        public boolean removed;
        public boolean rewardIssued;
        public boolean rewardPending;
        public boolean returnedToOrigin;
        public BlockPos rewardPos;
        public final Map<BlockPos, String> owned = new LinkedHashMap<>();
        public final Map<Integer, BlockPos> nodes = new LinkedHashMap<>();

        public Session(String dimension, BlockPos core) {
            this.dimension = dimension;
            this.core = core.immutable();
            this.key = key(dimension, core);
        }
        public boolean is(String phase) { return this.phase.equals(phase); }
        CompoundTag save() {
            CompoundTag tag = new CompoundTag();
            tag.putString("Dimension", dimension); tag.putLong("Core", core.asLong());
            if (owner != null) tag.putUUID("Owner", owner);
            if (boss != null) tag.putUUID("Boss", boss);
            ListTag party=new ListTag();for(UUID id:participants)party.add(net.minecraft.nbt.StringTag.valueOf(id.toString()));tag.put("Participants",party);
            if (!bossSnapshot.isEmpty()) tag.put("BossSnapshot", bossSnapshot.copy());
            tag.putString("Phase", phase); tag.putInt("Mask", mask); tag.putInt("Arena", arenaIndex);
            tag.putBoolean("PhaseOne", phaseOne); tag.putInt("PendingMask", pendingMask);
            tag.putIntArray("OfferingTicks", offeringTicks); tag.putIntArray("CompletionOrder", completionOrder);
            for(int i=0;i<4;i++)if(offeringPlayers[i]!=null)tag.putUUID("OfferingPlayer"+i,offeringPlayers[i]);
            tag.putString("RitualStage", ritualStage); tag.putInt("RitualTicks", ritualTicks);
            tag.putBoolean("FinalOfferingReady", finalOfferingReady); tag.putBoolean("RitualRunning", ritualRunning);
            tag.putBoolean("BossFightStarted", bossFightStarted); tag.putBoolean("BossDefeated", bossDefeated);
            tag.putBoolean("ArenaReady", arenaReady);
            tag.putInt("BossIntroTick",bossIntroTick);
            tag.putLong("ChargeEnds", chargeEnds); tag.putLong("VictoryAt", victoryAt); tag.putFloat("Yaw", yaw);
            tag.putBoolean("Removed", removed); tag.putBoolean("RewardIssued", rewardIssued);
            tag.putBoolean("ReturnedToOrigin", returnedToOrigin);
            tag.putBoolean("RewardPending", rewardPending);
            if (rewardPos != null) tag.putLong("RewardPos", rewardPos.asLong());
            ListTag blocks = new ListTag();
            owned.forEach((pos, state) -> {
                CompoundTag b = new CompoundTag(); b.putLong("Pos", pos.asLong()); b.putString("State", state); blocks.add(b);
            });
            tag.put("Owned", blocks);
            ListTag nodeList = new ListTag();
            nodes.forEach((slot, pos) -> {
                CompoundTag n = new CompoundTag(); n.putInt("Slot", slot); n.putLong("Pos", pos.asLong()); nodeList.add(n);
            });
            tag.put("Nodes", nodeList);
            return tag;
        }
        static Session load(CompoundTag tag) {
            Session s = new Session(tag.getString("Dimension"), BlockPos.of(tag.getLong("Core")));
            if (tag.hasUUID("Owner")) s.owner = tag.getUUID("Owner");
            if (tag.hasUUID("Boss")) s.boss = tag.getUUID("Boss");
            for(Tag member:tag.getList("Participants",Tag.TAG_STRING))try{s.participants.add(UUID.fromString(member.getAsString()));}catch(IllegalArgumentException ignored){}
            s.bossSnapshot = tag.getCompound("BossSnapshot").copy();
            s.phase = tag.getString("Phase"); s.mask = tag.getInt("Mask") & 31; s.arenaIndex = tag.contains("Arena")?tag.getInt("Arena"):-1;
            if (!java.util.Set.of("installing","idle","charging","active","paused","victory","returned").contains(s.phase)) s.phase="paused";
            // Migrate only unstarted altars; never reset an existing combat or reward transaction.
            s.phaseOne = tag.contains("PhaseOne") ? tag.getBoolean("PhaseOne") : s.is("idle");
            s.pendingMask = tag.getInt("PendingMask") & 15 & ~s.mask;
            int[] ticks=tag.getIntArray("OfferingTicks"), order=tag.getIntArray("CompletionOrder");
            for(int i=0;i<4;i++)if(tag.hasUUID("OfferingPlayer"+i))s.offeringPlayers[i]=tag.getUUID("OfferingPlayer"+i);
            for(int i=0;i<4;i++) { s.offeringTicks[i]=i<ticks.length?Math.max(0,Math.min(160,ticks[i])):0;
                s.completionOrder[i]=i<order.length?Math.max(0,Math.min(4,order[i])):0; }
            if(order.length!=4) {int rank=0;for(int i=0;i<4;i++)if((s.mask&(1<<i))!=0)s.completionOrder[i]=++rank;}
            s.ritualStage=tag.contains("RitualStage")?tag.getString("RitualStage"):((s.mask&15)==15?"FINAL_OFFERING_READY":"OFFERINGS");
            if(!java.util.Set.of("OFFERINGS","THIRD_OMEN","FOURTH_CONVERGENCE","FINAL_OFFERING_READY","FINAL_RITUAL","TRANSFER_READY","COMPLETE").contains(s.ritualStage)) s.ritualStage="OFFERINGS";
            s.ritualTicks=Math.max(0,Math.min(240,tag.getInt("RitualTicks")));
            s.finalOfferingReady=s.ritualStage.equals("FINAL_OFFERING_READY");
            s.ritualRunning=s.ritualStage.equals("FINAL_RITUAL")||s.ritualStage.equals("TRANSFER_READY");
            s.bossIntroTick=tag.contains("BossIntroTick")?Math.max(0,Math.min(280,tag.getInt("BossIntroTick"))):(s.boss!=null||s.is("active")?280:0);
            s.bossFightStarted=s.bossIntroTick>=280;
            s.bossDefeated=tag.getBoolean("BossDefeated")||s.is("victory")||s.is("returned");
            if(s.arenaIndex < -1 || s.arenaIndex >= 1024*1024) s.arenaIndex=-1;
            s.arenaReady = tag.getBoolean("ArenaReady");
            s.chargeEnds = tag.getLong("ChargeEnds"); s.victoryAt = tag.getLong("VictoryAt"); s.yaw = tag.getFloat("Yaw");
            s.removed = tag.getBoolean("Removed"); s.rewardIssued = tag.getBoolean("RewardIssued");
            s.returnedToOrigin = tag.getBoolean("ReturnedToOrigin");
            s.rewardPending = tag.getBoolean("RewardPending");
            if (tag.contains("RewardPos")) s.rewardPos = BlockPos.of(tag.getLong("RewardPos"));
            ListTag blocks = tag.getList("Owned", Tag.TAG_COMPOUND);
            for (int i = 0; i < blocks.size(); i++) {
                CompoundTag b = blocks.getCompound(i); s.owned.put(BlockPos.of(b.getLong("Pos")), b.getString("State"));
            }
            ListTag nodes = tag.getList("Nodes", Tag.TAG_COMPOUND);
            for (int i = 0; i < nodes.size(); i++) {
                CompoundTag n = nodes.getCompound(i); s.nodes.put(n.getInt("Slot"), BlockPos.of(n.getLong("Pos")));
            }
            return s;
        }
    }
    public static String key(String dimension, BlockPos core) { return dimension + "/" + core.asLong(); }
    public static ZhenyuanRitualSavedData get(ServerLevel level) {
        return level.getServer().overworld().getDataStorage().computeIfAbsent(
                ZhenyuanRitualSavedData::load, ZhenyuanRitualSavedData::new, FILE_ID);
    }
    public Collection<Session> sessions() { return sessions.values(); }
    public Session at(ServerLevel level, BlockPos core) { return sessions.get(key(level.dimension().location().toString(), core)); }
    public Session forOwner(UUID player) {
        return sessions.values().stream().filter(s -> (player.equals(s.owner)||s.participants.contains(player)) && !s.is("returned")).findFirst().orElse(null);
    }
    public Session forBoss(UUID boss) {
        return sessions.values().stream().filter(s -> boss.equals(s.boss)).findFirst().orElse(null);
    }
    public static ZhenyuanRitualSavedData load(CompoundTag tag) {
        ZhenyuanRitualSavedData data = new ZhenyuanRitualSavedData(); data.nextArena = Math.max(0,Math.min(1024*1024,tag.getInt("NextArena")));
        ListTag sessions = tag.getList("Sessions", Tag.TAG_COMPOUND);
        for (int i = 0; i < sessions.size(); i++) {
            Session s = Session.load(sessions.getCompound(i)); data.sessions.put(s.key, s);
            data.nextArena = Math.max(data.nextArena, s.arenaIndex + 1);
        }
        return data;
    }
    @Override public CompoundTag save(CompoundTag tag) {
        tag.putInt("NextArena", nextArena);
        ListTag list = new ListTag(); sessions.values().forEach(s -> list.add(s.save())); tag.put("Sessions", list);
        return tag;
    }
}
