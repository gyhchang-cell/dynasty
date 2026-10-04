package com.dynasty.ritual;

import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.Connection;
import net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;

/** Server-owned ritual data; clients receive masks/stages and interpolate visual activation only. */
public final class ZhenyuanNodeBlockEntity extends BlockEntity {
    private BlockPos corePos;
    private int slot;
    private int offeringMask;
    private int stage;
    private long visualChangedAt;
    private int previousVisualMask;
    private CompoundTag timeline = new CompoundTag();
    private long receivedAt;
    private BlockPos naturalOrigin;
    public BlockPos naturalOrigin(){return naturalOrigin;}
    public CompoundTag timeline() { return timeline; }
    public double timelineAge(double time) { return Math.max(0,Math.min(5,time-receivedAt)); }
    public void syncTimeline(ZhenyuanRitualSavedData.Session s) {
        timeline = new CompoundTag();
        timeline.putBoolean("Enabled",s.phaseOne); timeline.putInt("Pending",s.pendingMask);
        timeline.putIntArray("OfferingTicks",s.offeringTicks); timeline.putIntArray("Order",s.completionOrder);
        timeline.putString("Stage",s.ritualStage); timeline.putInt("Tick",s.ritualTicks);
        timeline.putLong("Heart",s.nodes.getOrDefault(4,s.core).asLong());
        if(s.owner!=null) timeline.putUUID("Owner",s.owner);
    }

    public ZhenyuanNodeBlockEntity(BlockPos pos, BlockState state) {
        super(ZhenyuanRitualContent.NODE_ENTITY.get(), pos, state);
        corePos = pos.immutable();
        slot = state.hasProperty(ZhenyuanNodeBlock.SLOT) ? state.getValue(ZhenyuanNodeBlock.SLOT) : 4;
    }
    public BlockPos getCorePos() { return corePos; }
    @Override public void onLoad() {
        super.onLoad();
        if(level instanceof net.minecraft.server.level.ServerLevel server) {
            var session=ZhenyuanRitualSavedData.get(server).at(server,corePos);
            if(session!=null&&worldPosition.equals(session.nodes.get(slot))) {
                syncTimeline(session);syncRitual(session.mask,ZhenyuanRitualRules.visualStage(session.phase));
            }
        }
    }
    public int getSlot() { return slot; }
    public int getOfferingMask() { return offeringMask; }
    public int getStage() { return stage; }
    public int getPreviousVisualMask() { return previousVisualMask; }
    public long getVisualChangedAt() { return visualChangedAt; }

    public void configure(BlockPos core, int newSlot) {
        corePos = core.immutable();
        slot = Math.max(0, Math.min(4, newSlot));
        synchronize();
    }
    public void syncRitual(int mask, int newStage) {
        offeringMask = mask & 31;
        stage = Math.max(0, Math.min(3, newStage));
        synchronize();
    }
    private void synchronize() {
        setChanged();
        if (level == null || level.isClientSide) return;
        BlockState current = level.getBlockState(worldPosition);
        if (current.is(ZhenyuanRitualContent.NODE.get())) {
            BlockState next = current.setValue(ZhenyuanNodeBlock.SLOT, slot)
                    .setValue(ZhenyuanNodeBlock.ACTIVE, (offeringMask & (1 << slot)) != 0);
            if (!next.equals(current)) level.setBlock(worldPosition, next, 3);
            level.sendBlockUpdated(worldPosition, next, next, 3);
        }
    }
    @Override protected void saveAdditional(CompoundTag tag) {
        super.saveAdditional(tag);
        tag.putLong("Core", corePos.asLong());
        tag.putInt("Slot", slot);
        tag.putInt("OfferingMask", offeringMask);
        tag.putInt("Stage", stage);
        tag.put("Timeline",timeline.copy());
        if(naturalOrigin!=null)tag.putLong("NaturalOrigin",naturalOrigin.asLong());
    }
    @Override public void load(CompoundTag tag) {
        super.load(tag);
        int nextMask = tag.getInt("OfferingMask") & 31;
        int nextStage = Math.max(0, Math.min(3, tag.getInt("Stage")));
        if (level != null && level.isClientSide && (nextMask != offeringMask || nextStage != stage)) {
            previousVisualMask = offeringMask;
            visualChangedAt = level.getGameTime();
        }
        corePos = tag.contains("Core") ? BlockPos.of(tag.getLong("Core")) : worldPosition;
        slot = tag.contains("Slot") ? Math.max(0, Math.min(4, tag.getInt("Slot")))
                : getBlockState().getValue(ZhenyuanNodeBlock.SLOT);
        offeringMask = nextMask;
        stage = nextStage;
        timeline=tag.getCompound("Timeline").copy();
        naturalOrigin=tag.contains("NaturalOrigin")?BlockPos.of(tag.getLong("NaturalOrigin")):null;
        receivedAt=level==null?0:level.getGameTime();
    }
    @Override public CompoundTag getUpdateTag() { return saveWithoutMetadata(); }
    @Override public ClientboundBlockEntityDataPacket getUpdatePacket() { return ClientboundBlockEntityDataPacket.create(this); }
    @Override public void onDataPacket(Connection connection, ClientboundBlockEntityDataPacket packet) {
        if (packet.getTag() != null) load(packet.getTag());
    }
    @Override public void handleUpdateTag(CompoundTag tag) { load(tag); }
    @Override public AABB getRenderBoundingBox() {
        return new AABB(worldPosition).minmax(new AABB(corePos)).inflate(12.0);
    }
}
