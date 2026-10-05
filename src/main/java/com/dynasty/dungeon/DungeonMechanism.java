package com.dynasty.dungeon;

/** Server-owned room lifecycle; implementations must pause when inactive. */
public interface DungeonMechanism {
    enum Phase { IDLE, WARNING, ACTIVE, RECOVERY }
    void trigger(long gameTime);
    void tickActive(long gameTime);
    void reset();
    void complete();
    net.minecraft.nbt.CompoundTag save();
    void load(net.minecraft.nbt.CompoundTag tag);
    void syncVisual();
}
