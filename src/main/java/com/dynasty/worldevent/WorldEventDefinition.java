package com.dynasty.worldevent;

import net.minecraft.resources.ResourceLocation;
import java.util.List;
import java.util.Set;

public record WorldEventDefinition(ResourceLocation id,String name,ResourceLocation dimensionTag,
        ResourceLocation biomeTag,ResourceLocation structureTag,int minY,int maxY,int startTime,int endTime,
        String weather,Set<String> requiredWorldStates,Set<String> forbiddenWorldStates,
        int minDistanceFromSpawn,int cooldown,String globalCooldownGroup,int maxConcurrent,
        int radius,int duration,int rarity,RewardMode rewardMode,CleanupPolicy cleanupPolicy,
        Controller controller,ResourceLocation rewardTable,List<Actor> actors,List<ResourceLocation> dependencies) {
    public enum RewardMode { WORLD_ONCE, PARTICIPANT_ONCE }
    public enum CleanupPolicy { DISCARD_ACTORS_RESTORE_OWNED_BLOCKS }
    public enum Controller { PROCESSION, BATTLE, CELESTIAL, UNIMPLEMENTED }
    public record Actor(ResourceLocation type,int count,String team){}
    public WorldEventDefinition {
        actors=List.copyOf(actors);dependencies=List.copyOf(dependencies);
        requiredWorldStates=Set.copyOf(requiredWorldStates);forbiddenWorldStates=Set.copyOf(forbiddenWorldStates);
        if(minY>maxY||startTime<0||endTime>23999||radius<8||radius>128||duration<40||duration>24000
                ||maxConcurrent<1||maxConcurrent>3||rarity<1||cooldown<200
                ||actors.stream().mapToInt(Actor::count).sum()>24)throw new IllegalArgumentException("Invalid event "+id);
        for(var actor:actors)if(actor.count()<1||actor.count()>16||!List.of("ARMY","REBELS","SPIRITS").contains(actor.team()))throw new IllegalArgumentException("Invalid actor "+actor);
    }
}
