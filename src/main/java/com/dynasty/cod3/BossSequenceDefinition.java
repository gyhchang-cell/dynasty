package com.dynasty.cod3;

import java.util.List;

public record BossSequenceDefinition(String id,String name,int totalTicks,String arenaTag,List<String> bossIds,List<Step> steps) {
    public enum Type {WAIT,SPAWN_CLIENT_VFX,PLAY_SOUND,SET_BOSS_VISIBILITY,SET_MODEL_VARIANT,PLAY_BOSS_ANIMATION}
    public record Step(int startTick,int duration,Type type,int vfx,double radius,String detail){}
    public BossSequenceDefinition {
        if(totalTicks<20||totalTicks>1200)throw new IllegalArgumentException("Sequence duration outside budget");
        steps=List.copyOf(steps);bossIds=List.copyOf(bossIds);
        for(var s:steps)if(s.startTick<0||s.startTick>=totalTicks||s.duration<0)throw new IllegalArgumentException("Invalid sequence step");
    }
}
