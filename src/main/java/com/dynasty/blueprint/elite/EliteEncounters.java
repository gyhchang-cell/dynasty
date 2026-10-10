package com.dynasty.blueprint.elite;

import com.dynasty.blueprint.BlueprintSpawnState;
import net.minecraft.core.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.TagKey;
import net.minecraft.world.Difficulty;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.level.*;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.phys.AABB;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.HashSet;

/** Existing structure references and encounter ledger, never a biome population or a forced chunk load. */
@Mod.EventBusSubscriber(modid="dynasty")
public final class EliteEncounters {
    public record Placement(String dimension,String primaryLocation,String spawnMethod,String respawnRule,int maxAlive,String bossDependency){}
    public static final Placement HEADLESS=new Placement("minecraft:overworld","existing ruined battlefield military camp","STRUCTURE_ENCOUNTER","12000 ticks after confirmed death; unloaded UUID retains slot",1,"NONE");
    private static final TagKey<Structure> SITES=TagKey.create(Registries.STRUCTURE,new ResourceLocation("dynasty","blueprint/battlefields"));
    @SubscribeEvent public static void tick(TickEvent.LevelTickEvent event){
        if(event.phase!=TickEvent.Phase.END||!(event.level instanceof ServerLevel level)||level.dimension()!=Level.OVERWORLD
                ||level.getGameTime()%100!=0||level.getDifficulty()==Difficulty.PEACEFUL||!level.getGameRules().getBoolean(GameRules.RULE_DOMOBSPAWNING))return;
        var registry=level.registryAccess().registryOrThrow(Registries.STRUCTURE);var visited=new HashSet<String>();int budget=2,refs=0;
        for(var player:level.players()){
            if(player.isSpectator()||!player.isAlive())continue;var centre=player.chunkPosition();
            for(int dx=-1;dx<=1;dx++)for(int dz=-1;dz<=1;dz++){
                var chunk=level.getChunkSource().getChunkNow(centre.x+dx,centre.z+dz);if(chunk==null)continue;
                var candidates=new java.util.ArrayList<net.minecraft.world.level.levelgen.structure.StructureStart>();
                chunk.getAllStarts().forEach((type,start)->{if(registry.wrapAsHolder(type).is(SITES))candidates.add(start);});
                for(var entry:chunk.getAllReferences().entrySet())if(registry.wrapAsHolder(entry.getKey()).is(SITES))for(long packed:entry.getValue()){
                    if(++refs>64)return;var startChunk=level.getChunkSource().getChunkNow(ChunkPos.getX(packed),ChunkPos.getZ(packed));
                    if(startChunk!=null)candidates.add(startChunk.getStartForStructure(entry.getKey()));
                }
                for(var start:candidates){
                    if(start==null||!start.isValid())continue;var b=start.getBoundingBox();
                    if(player.getX()<b.minX()-24||player.getX()>b.maxX()+24||player.getZ()<b.minZ()-24||player.getZ()>b.maxZ()+24)continue;
                    String key=level.dimension().location()+"/"+registry.getKey(start.getStructure())+"@"+start.getChunkPos().toLong()+":headless_general";
                    if(!visited.add(key))continue;
                    for(int n=0;n<24;n++){
                        var p=player.blockPosition().offset(level.random.nextInt(25)-12,0,level.random.nextInt(25)-12);
                        for(int dy=4;dy>=-4;dy--){var feet=p.above(dy);if(!b.isInside(feet)||feet.distSqr(player.blockPosition())<49)continue;
                            if(spawn(level,key,feet,player.blockPosition())){if(--budget<=0)return;n=24;break;}
                        }
                    }
                }
            }
        }
    }
    public static boolean spawn(ServerLevel level,String key,BlockPos feet,BlockPos entrant){
        if(level.dimension()!=Level.OVERWORLD||level.getDifficulty()==Difficulty.PEACEFUL||!level.getGameRules().getBoolean(GameRules.RULE_DOMOBSPAWNING)
                ||!level.hasChunkAt(feet)||feet.distSqr(entrant)>48*48||feet.distSqr(entrant)<36)return false;
        var state=BlueprintSpawnState.get(level);var marker=state.markers.get(key);
        if(marker!=null&&(marker.cleared||!marker.members.isEmpty()||marker.nextSpawn>level.getGameTime()))return false;
        var type=EliteContent.HEADLESS.get();var box=type.getDimensions().makeBoundingBox(feet.getX()+.5,feet.getY(),feet.getZ()+.5);
        if(!level.getBlockState(feet.below()).isFaceSturdy(level,feet.below(),Direction.UP)||!level.getFluidState(feet).isEmpty()
                ||!level.noCollision(null,box)||!level.getEntitiesOfClass(HeadlessGeneral.class,new AABB(feet).inflate(32),e->e.isAlive()).isEmpty())return false;
        var mob=type.create(level);if(mob==null)return false;
        mob.moveTo(feet.getX()+.5,feet.getY(),feet.getZ()+.5,0,0);mob.setPersistenceRequired();mob.bindEncounter(key);
        mob.finalizeSpawn(level,level.getCurrentDifficultyAt(feet),MobSpawnType.STRUCTURE,null,null);
        if(!level.addFreshEntity(mob))return false;
        if(marker==null){marker=new BlueprintSpawnState.Marker(key,feet);state.markers.put(key,marker);}
        marker.members.add(mob.getUUID());marker.produced=1;state.setDirty();return true;
    }
    private EliteEncounters(){}
}
