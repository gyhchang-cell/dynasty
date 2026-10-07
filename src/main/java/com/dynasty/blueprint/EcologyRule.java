package com.dynasty.blueprint;

import com.dynasty.blueprint.combat.Faction;
import net.minecraft.resources.ResourceLocation;
import java.util.List;
import java.util.Set;

/** Server ecology contract. Unregistered cod1 dependencies remain IDs, never replacement mobs. */
public record EcologyRule(ResourceLocation id, ResourceLocation dimensionTag,
        ResourceLocation biomeTag, ResourceLocation structureTag, int structureRadius,
        int minY, int maxY, TimeWindow timeWindow, Weather weather, int maxLight,
        boolean nearWater, boolean naturalSpawning, Caps caps, List<Member> members,
        Set<Faction> hostileFactions, Set<Faction> allyFactions, String specialWorldState) {
    public enum TimeWindow { ALL, NIGHT, DUSK, OUTSIDE_NOON }
    public enum Weather { ANY, RAIN, THUNDER }
    public record Caps(int ordinary, int flying, int elite) {}
    public record Member(ResourceLocation mobType, int weight, int minGroup, int maxGroup,
            int localCap, boolean flying, boolean elite, boolean existingSpawner,
            Set<ResourceLocation> predatorTargets) {}
    public EcologyRule {
        members=List.copyOf(members); hostileFactions=Set.copyOf(hostileFactions); allyFactions=Set.copyOf(allyFactions);
        if(minY>maxY||maxLight<0||maxLight>15||structureRadius<0||structureRadius>48
                ||caps.ordinary()<0||caps.flying()<0||caps.elite()<0)throw new IllegalArgumentException("Invalid ecology rule "+id);
        for(var member:members)if(member.weight()<1||member.minGroup()<1||member.maxGroup()<member.minGroup()
                ||member.localCap()<1)throw new IllegalArgumentException("Invalid ecology member "+member.mobType());
    }
}
