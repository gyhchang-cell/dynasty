package com.dynasty.expansion;

import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.TagKey;
import net.minecraft.world.level.biome.Biome;

/** Explicit hook for cod2 encounter population. Never injects an independent natural spawn loop. */
public final class SecondarySpawnHooks {
    public static boolean eligible(ServerLevel level,BlockPos pos,String id) {
        var spec=SecondaryMobs.SPECS.stream().filter(s->s.id().equals(id)).findFirst().orElse(null);
        if(spec==null || !level.hasChunkAt(pos) || level.getDifficulty()==net.minecraft.world.Difficulty.PEACEFUL && !spec.neutral())return false;
        String structure=java.util.Set.of("famished_refugee","swindler","paper_cut_child","paper_money_ghost").contains(id)?"ghost_sites":java.util.Set.of("bandit_thug","night_watchman","wooden_magpie","clockwork_rat").contains(id)?"military_sites":null;
        if(structure!=null && !level.structureManager().getStructureWithPieceAt(pos,TagKey.create(Registries.STRUCTURE,new ResourceLocation("dynasty","blueprint/"+structure))).isValid())return false;
        if(!level.getBiome(pos).is(TagKey.create(Registries.BIOME,new ResourceLocation("dynasty","secondary/"+id))))return false;
        if(java.util.Set.of("night_watchman","red_fox","lantern_ghost","drowning_ghost","bat_demon","paper_money_ghost","wandering_spirit").contains(id) && level.isDay())return false;
        if(id.equals("locust_swarm") && level.isRaining())return false;
        if(spec.aquatic() && !level.getFluidState(pos).is(net.minecraft.tags.FluidTags.WATER))return false;
        if(!spec.aquatic() && !spec.flying() && !level.getBlockState(pos.below()).isSolidRender(level,pos.below()))return false;
        if(level.getEntitiesOfClass(SecondaryMob.class,new net.minecraft.world.phys.AABB(pos).inflate(32)).size()>=20)return false;
        return true;
    }
    public static SecondaryMob spawn(ServerLevel level,BlockPos pos,String id) {
        if(!eligible(level,pos,id))return null;
        SecondaryMob mob=SecondaryMobs.TYPES.get(id).get().create(level);if(mob==null)return null;
        mob.moveTo(pos.getX()+.5,pos.getY(),pos.getZ()+.5,level.random.nextFloat()*360,0);
        if(!level.noCollision(mob)){mob.discard();return null;}
        level.addFreshEntity(mob);return mob;
    }
    private SecondarySpawnHooks() { }
}
