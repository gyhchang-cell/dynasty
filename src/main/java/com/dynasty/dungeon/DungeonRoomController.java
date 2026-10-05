package com.dynasty.dungeon;

import net.minecraft.nbt.CompoundTag;
import java.util.HashSet;
import java.util.Set;
import java.util.UUID;

/** Small, dimension-owned room record. No entity references or per-block NBT copies. */
public final class DungeonRoomController implements DungeonMechanism {
    public static final int WARNING_TICKS=20, ACTIVE_TICKS=4, RECOVERY_TICKS=36;
    private int progress;
    private boolean completed;
    private Phase phase=Phase.IDLE;
    private int phaseTicks;
    private long lastUpdate=-1;
    private boolean contactPending;
    private boolean worldRewardGranted;
    private final Set<UUID> rewardedPlayers=new HashSet<>();
    private final Set<String> shortcuts=new HashSet<>();

    public int progress(){return progress;}
    public boolean completed(){return completed;}
    public Phase phase(){return phase;}
    public int phaseTicks(){return phaseTicks;}
    public boolean recordTarget(int target){
        if(target<0||target>5) return false;
        int bit=1<<target;
        if((progress&bit)!=0) return false;
        progress|=bit;
        if(progress==63) complete();
        return true;
    }
    public boolean claimWorldReward(){
        if(!completed||worldRewardGranted)return false;
        worldRewardGranted=true;return true;
    }
    public boolean claimPlayerReward(UUID player){return completed&&rewardedPlayers.add(player);}
    public boolean unlockShortcut(String id){return shortcuts.add(id);}
    public boolean shortcutOpen(String id){return shortcuts.contains(id);}

    @Override public void trigger(long time){
        if(completed||phase!=Phase.IDLE)return;
        phase=Phase.WARNING;phaseTicks=0;lastUpdate=time;contactPending=false;
    }
    @Override public void tickActive(long time){
        // A reloaded chunk never executes missed contact frames. Inactive rooms
        // and server downtime do not create a catch-up damage burst.
        long delta=lastUpdate<0?0:time-lastUpdate;
        lastUpdate=time;
        if(delta<0||delta>4||phase==Phase.IDLE)return;
        phaseTicks+=(int)delta;
        if(phase==Phase.WARNING&&phaseTicks>=WARNING_TICKS){
            phase=Phase.ACTIVE;phaseTicks=0;contactPending=true;
        }else if(phase==Phase.ACTIVE&&phaseTicks>=ACTIVE_TICKS){
            phase=Phase.RECOVERY;phaseTicks=0;
        }else if(phase==Phase.RECOVERY&&phaseTicks>=RECOVERY_TICKS){
            phase=Phase.IDLE;phaseTicks=0;
        }
    }
    public void pause(long time){lastUpdate=time;contactPending=false;}
    public boolean consumeContact(){boolean hit=contactPending;contactPending=false;return hit;}
    @Override public void reset(){
        // Resetting a room cannot reopen its world/player unique reward ledger.
        progress=0;completed=false;phase=Phase.IDLE;phaseTicks=0;contactPending=false;lastUpdate=-1;
    }
    @Override public void complete(){completed=true;phase=Phase.IDLE;phaseTicks=0;contactPending=false;}
    @Override public void syncVisual(){/* The owning core updates only loaded marker BEs. */}
    @Override public CompoundTag save(){
        CompoundTag tag=new CompoundTag();tag.putInt("Progress",progress);tag.putBoolean("Completed",completed);
        tag.putString("Phase",phase.name());tag.putInt("PhaseTicks",phaseTicks);tag.putLong("LastUpdate",lastUpdate);
        tag.putBoolean("WorldReward",worldRewardGranted);
        var players=new net.minecraft.nbt.ListTag();for(var id:rewardedPlayers)players.add(net.minecraft.nbt.StringTag.valueOf(id.toString()));
        tag.put("Players",players);
        var paths=new net.minecraft.nbt.ListTag();for(String id:shortcuts)paths.add(net.minecraft.nbt.StringTag.valueOf(id));tag.put("Shortcuts",paths);
        return tag;
    }
    @Override public void load(CompoundTag tag){
        progress=tag.getInt("Progress")&63;completed=tag.getBoolean("Completed");
        try{phase=Phase.valueOf(tag.getString("Phase"));}catch(IllegalArgumentException e){phase=Phase.IDLE;}
        phaseTicks=Math.max(0,Math.min(RECOVERY_TICKS,tag.getInt("PhaseTicks")));
        lastUpdate=tag.contains("LastUpdate")?tag.getLong("LastUpdate"):-1;
        contactPending=false;worldRewardGranted=tag.getBoolean("WorldReward");
        rewardedPlayers.clear();shortcuts.clear();
        for(var value:tag.getList("Players",8))try{rewardedPlayers.add(UUID.fromString(value.getAsString()));}catch(IllegalArgumentException ignored){}
        for(var value:tag.getList("Shortcuts",8))shortcuts.add(value.getAsString());
    }
}
