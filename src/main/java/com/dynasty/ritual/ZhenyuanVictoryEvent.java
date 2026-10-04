package com.dynasty.ritual;

import net.minecraft.core.BlockPos;
import net.minecraftforge.eventbus.api.Event;

import java.util.UUID;

/**
 * Notification after the first active -> victory transition. It does not change any dragon blocks.
 * Future scenery listeners must deduplicate by sessionKey and may reconcile completed SavedData
 * sessions after a restart; cosmetic changes are deliberately not prescribed by this event.
 */
public final class ZhenyuanVictoryEvent extends Event {
    private final UUID owner;
    private final String sessionKey;
    private final String originDimension;
    private final BlockPos core;
    public ZhenyuanVictoryEvent(UUID owner,String sessionKey,String originDimension,BlockPos core) {
        this.owner=owner; this.sessionKey=sessionKey; this.originDimension=originDimension; this.core=core.immutable();
    }
    public UUID owner() { return owner; }
    public String sessionKey() { return sessionKey; }
    public String originDimension() { return originDimension; }
    public BlockPos core() { return core; }
}
