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
    private int requiredTargets=63, openingTicks;
    private final java.util.Map<String,DungeonHazard> hazards=new java.util.HashMap<>();
    private boolean timedTrial, trialRunning, trialFailed;
    private int trialTicks;
    private long trialLastUpdate=-1;
    private final java.util.Map<UUID,DungeonExposure> exposures=new java.util.HashMap<>();

    public DungeonExposure exposure(UUID player,boolean create) {
        if(!exposures.containsKey(player)&&create&&exposures.size()<64)exposures.put(player,new DungeonExposure());
        return exposures.get(player);
    }
    public boolean retainExposures(Set<UUID> present) {return exposures.keySet().removeIf(id->!present.contains(id));}
    public boolean clearExposure(UUID player) {return exposures.remove(player)!=null;}

    public void configureTargets(int mask,boolean timed) {
        requiredTargets=mask&63;timedTrial=timed;
        if(requiredTargets!=0&&(progress&requiredTargets)==requiredTargets)complete();
    }
    public DungeonHazard hazard(String key,boolean floor) {
        if(hazards.size()>=64&&!hazards.containsKey(key))throw new IllegalStateException("Room hazard budget exceeded");
        var profile=DungeonTrapProfile.forId(key);
        var clock=hazards.computeIfAbsent(key,k->profile!=null?profile.clock():new DungeonHazard(20,floor?40:6,36,floor?0:2));
        if(!floor&&profile==null){var upgraded=clock.upgradeIdleArrowVolley();if(upgraded!=clock){hazards.put(key,upgraded);clock=upgraded;}}
        return clock;
    }
    // Failure releases the trial entrance only. The exit still requires the eyes.
    public boolean doorOpen(){return completed&&(requiredTargets==63||openingTicks>=12);}
    public int openingTicks(){return openingTicks;}
    public boolean trialRunning(){return trialRunning;}
    public boolean trialFailed(){return trialFailed;}
    public boolean allowRetry(){if(!trialFailed)return false;trialFailed=false;return true;}
    public int trialTicks(){return trialTicks;}
    public boolean startTrial(long time){
        if(!timedTrial||completed||trialRunning||trialFailed)return false;
        trialFailed=false;trialRunning=true;trialTicks=0;trialLastUpdate=time;return true;
    }
    /** Loaded/occupied time only. A timeout releases doors; another attempt keeps hit eyes. */
    public boolean tickRoom(long time,boolean occupied){
        long delta=trialLastUpdate<0?0:time-trialLastUpdate;trialLastUpdate=time;
        if(!occupied||delta<0||delta>4)return false;
        boolean changed=false;
        if(completed&&openingTicks<12){openingTicks=Math.min(12,openingTicks+(int)delta);changed=true;}
        if(trialRunning){trialTicks=Math.min(1200,trialTicks+(int)delta);changed|=delta>0;
            if(trialTicks>=1200){trialRunning=false;trialFailed=true;changed=true;}}
        return changed;
    }
    public void pauseHazards(long time){hazards.values().forEach(h->h.pause(time));}

    public int progress(){return progress;}
    public boolean completed(){return completed;}
    public Phase phase(){return phase;}
    public int phaseTicks(){return phaseTicks;}
    public boolean recordTarget(int target){
        if(target<0||target>5) return false;
        int bit=1<<target;
        if((progress&bit)!=0) return false;
        progress|=bit;
        if(requiredTargets!=0&&(progress&requiredTargets)==requiredTargets) complete();
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
        openingTicks=0;trialRunning=false;trialFailed=false;trialTicks=0;trialLastUpdate=-1;
        hazards.values().forEach(DungeonHazard::reset);
        exposures.clear();
    }
    @Override public void complete(){completed=true;phase=Phase.IDLE;phaseTicks=0;contactPending=false;trialRunning=false;trialFailed=false;}
    @Override public void syncVisual(){/* The owning core updates only loaded marker BEs. */}
    @Override public CompoundTag save(){
        CompoundTag tag=new CompoundTag();tag.putInt("Progress",progress);tag.putBoolean("Completed",completed);
        tag.putString("Phase",phase.name());tag.putInt("PhaseTicks",phaseTicks);tag.putLong("LastUpdate",lastUpdate);
        tag.putBoolean("WorldReward",worldRewardGranted);
        var players=new net.minecraft.nbt.ListTag();for(var id:rewardedPlayers)players.add(net.minecraft.nbt.StringTag.valueOf(id.toString()));
        tag.put("Players",players);
        var paths=new net.minecraft.nbt.ListTag();for(String id:shortcuts)paths.add(net.minecraft.nbt.StringTag.valueOf(id));tag.put("Shortcuts",paths);
        tag.putInt("RequiredTargets",requiredTargets);tag.putInt("OpeningTicks",openingTicks);
        tag.putBoolean("TimedTrial",timedTrial);tag.putBoolean("TrialRunning",trialRunning);tag.putBoolean("TrialFailed",trialFailed);
        tag.putInt("TrialTicks",trialTicks);tag.putLong("TrialLastUpdate",trialLastUpdate);
        var clocks=new CompoundTag();hazards.forEach((key,value)->clocks.put(key,value.save()));tag.put("Hazards",clocks);
        var contacts=new CompoundTag();exposures.forEach((key,value)->contacts.put(key.toString(),value.save()));tag.put("Exposures",contacts);
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
        requiredTargets=tag.contains("RequiredTargets")?tag.getInt("RequiredTargets")&63:63;
        openingTicks=tag.contains("OpeningTicks")?Math.max(0,Math.min(12,tag.getInt("OpeningTicks"))):completed?12:0;
        timedTrial=tag.getBoolean("TimedTrial");trialRunning=tag.getBoolean("TrialRunning")&&!completed;
        trialFailed=tag.getBoolean("TrialFailed");trialTicks=Math.max(0,Math.min(1200,tag.getInt("TrialTicks")));
        trialLastUpdate=tag.contains("TrialLastUpdate")?tag.getLong("TrialLastUpdate"):-1;
        hazards.clear();var clocks=tag.getCompound("Hazards");
        for(String key:clocks.getAllKeys())if(hazards.size()<64)hazards.put(key,DungeonHazard.restore(clocks.getCompound(key)));
        exposures.clear();var contacts=tag.getCompound("Exposures");
        for(String key:contacts.getAllKeys())if(exposures.size()<64)try {
            exposures.put(UUID.fromString(key),DungeonExposure.load(contacts.getCompound(key)));
        }catch(IllegalArgumentException ignored){}
    }
}
