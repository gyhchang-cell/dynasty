package com.dynasty.structure.megabuild;

import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.level.saveddata.SavedData;
import java.util.HashSet;
import java.util.Set;
import java.util.UUID;
import java.util.BitSet;

/** Small durable checkpoint, including only the altar's exact newly-created ownership indices. */
public final class SculptureSavedData extends SavedData {
    public static final String KEY="dynasty_sculpture_workshop";
    public String id="",dimension="",hash="",phase="checking",message="";
    public BlockPos origin=BlockPos.ZERO;
    public UUID owner;
    public int chunk,cell;
    public long checked,placed;
    public boolean paused=true;
    // Explicit per-run consent only: a server restart must never launch a blocking paste.
    public transient boolean direct;
    public final Set<Integer> altarWrites=new HashSet<>();
    // Precise receipts, not a claim on every matching block in the bounding box.
    public final BitSet placedVoxels=new BitSet();
    public boolean present(){return !id.isEmpty();}
    public static SculptureSavedData get(MinecraftServer server){return server.overworld().getDataStorage().computeIfAbsent(SculptureSavedData::load,SculptureSavedData::new,KEY);}
    public static SculptureSavedData load(CompoundTag tag){
        SculptureSavedData d=new SculptureSavedData();d.id=tag.getString("Id");d.dimension=tag.getString("Dimension");d.hash=tag.getString("Hash");d.phase=tag.getString("Phase");
        d.origin=BlockPos.of(tag.getLong("Origin"));if(tag.hasUUID("Owner"))d.owner=tag.getUUID("Owner");d.chunk=tag.getInt("Chunk");d.cell=tag.getInt("Cell");
        d.checked=Math.max(0,tag.getLong("Checked"));d.placed=Math.max(0,tag.getLong("Placed"));d.message=tag.getString("Message");
        for(int i:tag.getIntArray("AltarWrites"))if(i>=0&&i<20_000)d.altarWrites.add(i);
        long[] receipts=tag.getLongArray("PlacedVoxels");if(receipts.length<=1_000_000)d.placedVoxels.or(BitSet.valueOf(receipts));
        // Restarts never silently resume million-block edits. Admin explicitly resumes.
        d.paused=true;return d;
    }
    public void clear(){id="";dimension="";hash="";phase="checking";message="";origin=BlockPos.ZERO;owner=null;chunk=cell=0;checked=placed=0;paused=true;direct=false;altarWrites.clear();placedVoxels.clear();setDirty();}
    @Override public CompoundTag save(CompoundTag tag){
        tag.putString("Id",id);tag.putString("Dimension",dimension);tag.putString("Hash",hash);tag.putString("Phase",phase);tag.putString("Message",message);tag.putLong("Origin",origin.asLong());
        if(owner!=null)tag.putUUID("Owner",owner);tag.putInt("Chunk",chunk);tag.putInt("Cell",cell);tag.putLong("Checked",checked);tag.putLong("Placed",placed);
        tag.putIntArray("AltarWrites",altarWrites.stream().mapToInt(Integer::intValue).toArray());tag.putLongArray("PlacedVoxels",placedVoxels.toLongArray());tag.putBoolean("Paused",paused);return tag;
    }
}
