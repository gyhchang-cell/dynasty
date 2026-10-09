package com.dynasty.expansion;

import com.dynasty.blueprint.EcologyManager;
import com.dynasty.blueprint.LoadedStructureRegions;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.TagKey;
import net.minecraft.world.entity.*;
import net.minecraft.world.Difficulty;
import net.minecraft.world.level.*;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraftforge.event.entity.SpawnPlacementRegisterEvent;

/** Native biome spawning and the existing loaded-only encounter helper share one habitat check. */
public final class SecondarySpawnHooks {
    private static final java.util.Map<String,SecondaryMobs.Spec> SPECS=SecondaryMobs.SPECS.stream().collect(java.util.stream.Collectors.toUnmodifiableMap(SecondaryMobs.Spec::id,s->s));
    private static final java.util.Set<String> NIGHT=java.util.Set.of("night_watchman","red_fox","lantern_ghost","drowning_ghost","bat_demon","paper_money_ghost","wandering_spirit");
    private static final java.util.Set<String> CAVE=java.util.Set.of("bat_demon","stone_worm");
    public static void register(SpawnPlacementRegisterEvent event){
        for(var spec:SecondaryMobs.SPECS)event.register(SecondaryMobs.TYPES.get(spec.id()).get(),
            spec.aquatic()||spec.flying()?SpawnPlacements.Type.NO_RESTRICTIONS:SpawnPlacements.Type.ON_GROUND,
            Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,
            // Noise-stage creature placement runs on a worldgen worker. Never
            // turn its partially built region into a synchronous server query.
            (type,level,reason,pos,random)->reason!=MobSpawnType.CHUNK_GENERATION
                &&(reason!=MobSpawnType.NATURAL||level instanceof ServerLevel server&&eligible(server,pos,spec.id())),
            SpawnPlacementRegisterEvent.Operation.REPLACE);
    }
    private static boolean structure(ServerLevel level,BlockPos pos,String tag,int radius){return LoadedStructureRegions.contains(level,pos,new ResourceLocation("dynasty",tag),radius);}
    public static boolean eligible(ServerLevel level,BlockPos pos,String id) {
        var spec=SPECS.get(id);
        if(spec==null||!level.getServer().isSameThread()||(level.dimension()!=Level.OVERWORLD&&!(id.equals("crab_soldier")&&level.dimension()==com.dynasty.block.DynastyPortalBlock.DRAGON_PALACE))||level.getChunkSource().getChunkNow(pos.getX()>>4,pos.getZ()>>4)==null||pos.getY()<=level.getMinBuildHeight()||pos.getY()>=level.getMaxBuildHeight()-3
            ||!level.getGameRules().getBoolean(GameRules.RULE_DOMOBSPAWNING)||level.getDifficulty()==Difficulty.PEACEFUL&&!spec.neutral())return false;
        if(!level.getBiome(pos).is(TagKey.create(Registries.BIOME,new ResourceLocation("dynasty","secondary/"+id))))return false;
        boolean cave=!level.canSeeSky(pos)&&pos.getY()<=64;
        if(CAVE.contains(id)&&(!cave||level.getMaxLocalRawBrightness(pos)>7))return false;
        if(id.equals("stone_sprite")&&!cave&&!level.getBiome(pos).is(net.minecraft.tags.BiomeTags.IS_MOUNTAIN))return false;
        if(id.equals("corpse_beetle")&&!(cave&&level.getMaxLocalRawBrightness(pos)<=7||structure(level,pos,"ecology/tombs",0)))return false;
        if(NIGHT.contains(id)&&level.isDay())return false;
        if(id.equals("locust_swarm")&&level.isRaining())return false;
        boolean habitat=switch(id){
            case "famished_refugee","lantern_ghost"->structure(level,pos,"blueprint/ghost_sites",16)||structure(level,pos,"secondary/ruins",16);
            case "swindler"->structure(level,pos,"ecology/roads",16);
            case "night_watchman"->structure(level,pos,"ecology/roads",16)||structure(level,pos,"blueprint/military_sites",16);
            case "paper_cut_child","paper_money_ghost"->structure(level,pos,"ecology/tombs",0)||structure(level,pos,"blueprint/ghost_sites",8);
            case "wooden_magpie"->structure(level,pos,"blueprint/clockwork_dog_sites",16);
            case "clockwork_rat"->cave||structure(level,pos,"blueprint/clockwork_dog_sites",0)||structure(level,pos,"blueprint/mining_spider_sites",0);
            default->true;
        };
        if(!habitat)return false;
        var type=SecondaryMobs.TYPES.get(id).get();var box=type.getDimensions().makeBoundingBox(pos.getX()+.5,pos.getY(),pos.getZ()+.5);
        // Native collision queries include a one-block margin. Read only FULL
        // loaded chunks for that entire footprint (and the existing water check).
        int margin=spec.aquatic()?4:1;
        int minX=net.minecraft.util.Mth.floor(box.minX)-margin,maxX=net.minecraft.util.Mth.floor(box.maxX)+margin;
        int minZ=net.minecraft.util.Mth.floor(box.minZ)-margin,maxZ=net.minecraft.util.Mth.floor(box.maxZ)+margin;
        for(int x=minX>>4;x<=maxX>>4;x++)for(int z=minZ>>4;z<=maxZ>>4;z++)if(level.getChunkSource().getChunkNow(x,z)==null)return false;
        if(!level.noCollision(null,box))return false;
        if(spec.aquatic()){
            if(!level.getFluidState(pos).is(net.minecraft.tags.FluidTags.WATER)||!EcologyManager.connectedWater(level,pos))return false;
            if(id.equals("drowning_ghost")&&!level.getFluidState(pos.below()).is(net.minecraft.tags.FluidTags.WATER))return false;
        }else {
            if(!level.getFluidState(pos).isEmpty())return false;
            if(!spec.flying()&&!com.dynasty.entity.DynastySpawnPlacement.hasStandingSpace(level,pos,box))return false;
        }
        // Retain the shared twenty-mob bound, and prevent one species filling it.
        var local=level.getEntitiesOfClass(SecondaryMob.class,new net.minecraft.world.phys.AABB(pos).inflate(32),m->m.isAlive()&&!m.getPersistentData().hasUUID("cod4Summoner"));
        return local.size()<20&&local.stream().filter(m->m.spec.id().equals(id)).count()<3;
    }
    public static SecondaryMob spawn(ServerLevel level,BlockPos pos,String id) {
        if(!eligible(level,pos,id))return null;
        var mob=SecondaryMobs.TYPES.get(id).get().create(level);if(mob==null)return null;
        mob.moveTo(pos.getX()+.5,pos.getY(),pos.getZ()+.5,level.random.nextFloat()*360,0);
        mob.finalizeSpawn(level,level.getCurrentDifficultyAt(pos),MobSpawnType.STRUCTURE,null,null);
        if(!mob.checkSpawnObstruction(level)||!level.addFreshEntity(mob)){mob.discard();return null;}return mob;
    }
    private SecondarySpawnHooks() { }
}
