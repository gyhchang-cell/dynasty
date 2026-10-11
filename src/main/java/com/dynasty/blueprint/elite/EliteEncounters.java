package com.dynasty.blueprint.elite;

import com.dynasty.blueprint.BlueprintSpawnState;
import net.minecraft.core.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.TagKey;
import net.minecraft.world.Difficulty;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.*;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.phys.AABB;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.EntityLeaveLevelEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.HashSet;

/** Existing structure references and encounter ledger, never a biome population or a forced chunk load. */
@Mod.EventBusSubscriber(modid="dynasty")
public final class EliteEncounters {
    public record Placement(String dimension,String primaryLocation,String spawnMethod,String respawnRule,int maxAlive,String bossDependency){}
    public static final Placement HEADLESS=new Placement("minecraft:overworld","existing ruined battlefield military camp","STRUCTURE_ENCOUNTER","12000 ticks after confirmed death; unloaded UUID retains slot",1,"NONE");
    public static final Placement BIRD=new Placement("minecraft:overworld","night sky over an existing ruined battlefield","RARE_STRUCTURE_FLIGHT_EVENT","12000 ticks after confirmed death; unloaded UUID retains slot",1,"NONE");
    public static final Placement MECHANIST=new Placement("minecraft:overworld","authored workshop in existing Tiangong citadel or mining estate","STRUCTURE_ENCOUNTER","12000 ticks after confirmed death; unloaded UUID retains slot",1,"NONE");
    public static final Placement JINWU=new Placement("minecraft:overworld","existing imperial tomb central hall; secondary Great Wall gate passage","FIXED_GUARD","one cleared SavedData slot per structure; unloading retains UUID",1,"NONE");
    public static final Placement FOX=new Placement("minecraft:overworld","night courtyard of existing forest herbal retreat","STRUCTURE_ENCOUNTER","12000 ticks after confirmed death; unloaded UUID retains slot",1,"NONE");
    public static final Placement HAMMER=new Placement("minecraft:overworld","east guard court in existing imperial tomb","FIXED_GUARD","one cleared SavedData slot per structure; unloading retains UUID",1,"NONE");
    public static final Placement SPIDER_WOMAN=new Placement("minecraft:overworld","ceiling of the west ore gallery in existing mining estate","STRUCTURE_ENCOUNTER","12000 ticks after confirmed death; unloaded UUID retains slot",1,"NONE");
    private static final TagKey<Structure> SPIDER_WOMAN_SITES=TagKey.create(Registries.STRUCTURE,new ResourceLocation("dynasty","blueprint/spider_woman_sites"));
    private static final TagKey<Structure> SITES=TagKey.create(Registries.STRUCTURE,new ResourceLocation("dynasty","blueprint/battlefields"));
    private static final TagKey<Structure> MECHANIST_SITES=TagKey.create(Registries.STRUCTURE,new ResourceLocation("dynasty","blueprint/mechanist_sites"));
    private static final TagKey<Structure> JINWU_SITES=TagKey.create(Registries.STRUCTURE,new ResourceLocation("dynasty","blueprint/jinwu_sites"));
    private static final TagKey<Structure> FOX_SITES=TagKey.create(Registries.STRUCTURE,new ResourceLocation("dynasty","blueprint/fox_sites"));
    private static final TagKey<Structure> HAMMER_SITES=TagKey.create(Registries.STRUCTURE,new ResourceLocation("dynasty","blueprint/hammer_sites"));
    public static void memberDied(Entity mob){
        if(mob.level() instanceof ServerLevel level){
            var state=BlueprintSpawnState.get(level.getServer().overworld());
            if(mob instanceof Jinwu||mob instanceof HammerGuardian)for(var marker:state.markers.values())if(marker.members.contains(mob.getUUID())){marker.cleared=true;state.setDirty();break;}
            state.memberDied(mob.getUUID(),level.getGameTime());
        }
    }
    @SubscribeEvent public static void left(EntityLeaveLevelEvent event){
        var entity=event.getEntity();
        if((entity instanceof HeadlessGeneral||entity instanceof GhostCarriageBird||entity instanceof Mechanist||entity instanceof Jinwu||entity instanceof HammerGuardian||entity instanceof SpiderWoman||entity instanceof FoxMatron fox&&!fox.isDecoy())&&entity.getRemovalReason()!=null&&entity.getRemovalReason().shouldDestroy())memberDied(entity);
    }
    @SubscribeEvent public static void tick(TickEvent.LevelTickEvent event){
        if(event.phase!=TickEvent.Phase.END||!(event.level instanceof ServerLevel level)||level.dimension()!=Level.OVERWORLD
                ||level.getGameTime()%100!=0||level.getDifficulty()==Difficulty.PEACEFUL||!level.getGameRules().getBoolean(GameRules.RULE_DOMOBSPAWNING))return;
        var registry=level.registryAccess().registryOrThrow(Registries.STRUCTURE);var visited=new HashSet<String>();int budget=2,refs=0;
        for(var player:level.players()){
            if(player.isSpectator()||!player.isAlive())continue;var centre=player.chunkPosition();
            for(int dx=-1;dx<=1;dx++)for(int dz=-1;dz<=1;dz++){
                var chunk=level.getChunkSource().getChunkNow(centre.x+dx,centre.z+dz);if(chunk==null)continue;
                var candidates=new java.util.ArrayList<net.minecraft.world.level.levelgen.structure.StructureStart>();
                chunk.getAllStarts().forEach((type,start)->{var holder=registry.wrapAsHolder(type);if(holder.is(SITES)||holder.is(MECHANIST_SITES)||holder.is(JINWU_SITES)||holder.is(FOX_SITES))candidates.add(start);});
                for(var entry:chunk.getAllReferences().entrySet())if(registry.wrapAsHolder(entry.getKey()).is(SITES)||registry.wrapAsHolder(entry.getKey()).is(MECHANIST_SITES)||registry.wrapAsHolder(entry.getKey()).is(JINWU_SITES)||registry.wrapAsHolder(entry.getKey()).is(FOX_SITES))for(long packed:entry.getValue()){
                    if(++refs>64)return;var startChunk=level.getChunkSource().getChunkNow(ChunkPos.getX(packed),ChunkPos.getZ(packed));
                    if(startChunk!=null)candidates.add(startChunk.getStartForStructure(entry.getKey()));
                }
                for(var start:candidates){
                    if(start==null||!start.isValid())continue;var b=start.getBoundingBox();
                    if(player.getX()<b.minX()-24||player.getX()>b.maxX()+24||player.getZ()<b.minZ()-24||player.getZ()>b.maxZ()+24)continue;
                    if(registry.wrapAsHolder(start.getStructure()).is(HAMMER_SITES)){
                        String key=registry.getKey(start.getStructure())+"@"+start.getChunkPos().toLong()+":hammer_guardian";
                        if(visited.add(key))for(var piece:start.getPieces())if(piece instanceof com.dynasty.structure.TombPiece tomb
                            &&spawnHammer(level,key,tomb.hammerPosition(),player.blockPosition())&&--budget<=0)return;
                    }
                    if(registry.wrapAsHolder(start.getStructure()).is(FOX_SITES)){
                        String key=registry.getKey(start.getStructure())+"@"+start.getChunkPos().toLong()+":fox_matron";
                        if(!visited.add(key)||level.isDay())continue;
                        for(var piece:start.getPieces())if(piece instanceof com.dynasty.structure.TravelSitePiece travel){var feet=travel.foxPosition();if(feet!=null&&spawnFox(level,key,feet,player.blockPosition())&&--budget<=0)return;}
                        continue;
                    }
                    if(registry.wrapAsHolder(start.getStructure()).is(JINWU_SITES)){
                        String key=registry.getKey(start.getStructure())+"@"+start.getChunkPos().toLong()+":jinwu";
                        if(!visited.add(key))continue;
                        for(var piece:start.getPieces()){
                            BlockPos feet=piece instanceof com.dynasty.structure.TombPiece tomb?tomb.jinwuPosition():piece instanceof com.dynasty.structure.WallGatePiece gate?gate.jinwuPosition():null;
                            if(feet!=null&&spawnJinwu(level,key,feet,player.blockPosition())&&--budget<=0)return;
                        }
                        continue;
                    }
                    if(registry.wrapAsHolder(start.getStructure()).is(SPIDER_WOMAN_SITES)){
                        String key=level.dimension().location()+"/"+registry.getKey(start.getStructure())+"@"+start.getChunkPos().toLong()+":spider_woman";
                        if(visited.add(key))for(var piece:start.getPieces())for(var pos:com.dynasty.structure.megabuild.MechanicalPatrols.spiderWomanPositions(piece))
                            if(spawnSpiderWoman(level,key,pos,player.blockPosition())&&--budget<=0)return;
                    }
                    if(registry.wrapAsHolder(start.getStructure()).is(MECHANIST_SITES)){
                        String key=level.dimension().location()+"/"+registry.getKey(start.getStructure())+"@"+start.getChunkPos().toLong()+":mechanist";
                        if(!visited.add(key))continue;
                        boolean spawned=false;
                        for(var piece:start.getPieces())for(var feet:com.dynasty.structure.megabuild.MechanicalPatrols.mechanistPositions(piece))
                            if(!spawned&&spawnMechanist(level,key,feet,player.blockPosition()))spawned=true;
                        if(spawned&&--budget<=0)return;
                        continue;
                    }
                    String key=level.dimension().location()+"/"+registry.getKey(start.getStructure())+"@"+start.getChunkPos().toLong()+":headless_general";
                    if(!visited.add(key))continue;
                    if(!level.isDay()&&level.random.nextInt(8)==0){
                        var air=player.blockPosition().above(6).offset(10,0,0);
                        if(air.getX()>=b.minX()&&air.getX()<=b.maxX()&&air.getZ()>=b.minZ()&&air.getZ()<=b.maxZ()
                                &&spawnBird(level,key.replace(":headless_general",":ghost_carriage_bird"),air,player.blockPosition())&&--budget<=0)return;
                    }
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
    public static boolean spawnJinwu(ServerLevel level,String key,BlockPos feet,BlockPos entrant){
        if(level.dimension()!=Level.OVERWORLD||level.getDifficulty()==Difficulty.PEACEFUL||!level.getGameRules().getBoolean(GameRules.RULE_DOMOBSPAWNING)
            ||!level.hasChunkAt(feet)||feet.distSqr(entrant)>48*48||feet.distSqr(entrant)<36)return false;
        var state=BlueprintSpawnState.get(level);var marker=state.markers.get(key);
        if(marker!=null&&(marker.cleared||!marker.members.isEmpty()))return false;
        var type=EliteContent.JINWU.get();var box=type.getDimensions().makeBoundingBox(feet.getX()+.5,feet.getY(),feet.getZ()+.5);
        if(!level.getBlockState(feet.below()).isFaceSturdy(level,feet.below(),Direction.UP)||!level.getFluidState(feet).isEmpty()||!level.noCollision(null,box)
            ||!level.getEntitiesOfClass(Jinwu.class,new AABB(feet).inflate(32),Entity::isAlive).isEmpty())return false;
        var mob=type.create(level);if(mob==null)return false;mob.moveTo(feet.getX()+.5,feet.getY(),feet.getZ()+.5,0,0);mob.setPersistenceRequired();mob.bindEncounter(key);
        mob.finalizeSpawn(level,level.getCurrentDifficultyAt(feet),MobSpawnType.STRUCTURE,null,null);if(!level.addFreshEntity(mob))return false;
        if(marker==null){marker=new BlueprintSpawnState.Marker(key,feet);state.markers.put(key,marker);}marker.members.add(mob.getUUID());marker.produced=1;state.setDirty();return true;
    }
    public static boolean spawnHammer(ServerLevel level,String key,BlockPos feet,BlockPos entrant){
        if(level.dimension()!=Level.OVERWORLD||level.getDifficulty()==Difficulty.PEACEFUL||!level.getGameRules().getBoolean(GameRules.RULE_DOMOBSPAWNING)
            ||!level.hasChunkAt(feet)||feet.distSqr(entrant)>48*48||feet.distSqr(entrant)<36)return false;
        var state=BlueprintSpawnState.get(level);var marker=state.markers.get(key);if(marker!=null&&(marker.cleared||!marker.members.isEmpty()))return false;
        var type=EliteContent.HAMMER.get();var box=type.getDimensions().makeBoundingBox(feet.getX()+.5,feet.getY(),feet.getZ()+.5);
        if(!level.getBlockState(feet.below()).isFaceSturdy(level,feet.below(),Direction.UP)||!level.getFluidState(feet).isEmpty()||!level.noCollision(null,box)
            ||!level.getEntitiesOfClass(HammerGuardian.class,new AABB(feet).inflate(32),Entity::isAlive).isEmpty())return false;
        var actor=type.create(level);if(actor==null)return false;actor.moveTo(feet.getX()+.5,feet.getY(),feet.getZ()+.5,0,0);actor.setPersistenceRequired();actor.bindEncounter(key);
        actor.finalizeSpawn(level,level.getCurrentDifficultyAt(feet),MobSpawnType.STRUCTURE,null,null);if(!level.addFreshEntity(actor))return false;
        if(marker==null){marker=new BlueprintSpawnState.Marker(key,feet);state.markers.put(key,marker);}marker.members.add(actor.getUUID());marker.produced=1;state.setDirty();return true;
    }
    public static boolean spawnFox(ServerLevel level,String key,BlockPos feet,BlockPos entrant){
        if(level.dimension()!=Level.OVERWORLD||level.isDay()||level.getDifficulty()==Difficulty.PEACEFUL||!level.getGameRules().getBoolean(GameRules.RULE_DOMOBSPAWNING)||!level.hasChunkAt(feet)||feet.distSqr(entrant)<36||feet.distSqr(entrant)>48*48)return false;
        var state=BlueprintSpawnState.get(level);var marker=state.markers.get(key);if(marker!=null&&(marker.cleared||!marker.members.isEmpty()||marker.nextSpawn>level.getGameTime()))return false;
        var type=EliteContent.FOX.get();var box=type.getDimensions().makeBoundingBox(feet.getX()+.5,feet.getY()+.5,feet.getZ()+.5);
        if(!level.getBlockState(feet.below()).isFaceSturdy(level,feet.below(),Direction.UP)||!level.getFluidState(feet).isEmpty()||!level.noCollision(null,box)||!level.getEntitiesOfClass(FoxMatron.class,new AABB(feet).inflate(32),f->f.isAlive()&&!f.isDecoy()).isEmpty())return false;
        var mob=type.create(level);if(mob==null)return false;mob.moveTo(feet.getX()+.5,feet.getY()+.5,feet.getZ()+.5,0,0);mob.setPersistenceRequired();mob.bindEncounter(key);mob.finalizeSpawn(level,level.getCurrentDifficultyAt(feet),MobSpawnType.STRUCTURE,null,null);if(!level.addFreshEntity(mob))return false;
        if(marker==null){marker=new BlueprintSpawnState.Marker(key,feet);state.markers.put(key,marker);}marker.members.add(mob.getUUID());marker.produced=1;state.setDirty();return true;
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
    public static boolean spawnBird(ServerLevel level,String key,BlockPos air,BlockPos entrant){
        if(level.dimension()!=Level.OVERWORLD||level.isDay()||level.getDifficulty()==Difficulty.PEACEFUL
                ||!level.getGameRules().getBoolean(GameRules.RULE_DOMOBSPAWNING)||!level.hasChunkAt(air)
                ||air.distSqr(entrant)>48*48||air.distSqr(entrant)<36||air.getY()>=level.getMaxBuildHeight()-10)return false;
        var state=BlueprintSpawnState.get(level);var marker=state.markers.get(key);
        if(marker!=null&&(marker.cleared||!marker.members.isEmpty()||marker.nextSpawn>level.getGameTime()))return false;
        var type=EliteContent.BIRD.get();var box=type.getDimensions().makeBoundingBox(air.getX()+.5,air.getY(),air.getZ()+.5);
        if(!level.canSeeSky(air)||!level.getFluidState(air).isEmpty()||!level.noCollision(null,box)
                ||!level.getEntitiesOfClass(GhostCarriageBird.class,new AABB(air).inflate(48),Entity::isAlive).isEmpty())return false;
        var mob=type.create(level);if(mob==null)return false;
        mob.moveTo(air.getX()+.5,air.getY(),air.getZ()+.5,0,0);mob.setPersistenceRequired();mob.bindEncounter(key);
        mob.finalizeSpawn(level,level.getCurrentDifficultyAt(air),MobSpawnType.EVENT,null,null);
        if(!level.addFreshEntity(mob))return false;
        if(marker==null){marker=new BlueprintSpawnState.Marker(key,air);state.markers.put(key,marker);}
        marker.members.add(mob.getUUID());marker.produced=1;state.setDirty();return true;
    }
    public static boolean spawnMechanist(ServerLevel level,String key,BlockPos feet,BlockPos entrant){
        if(level.dimension()!=Level.OVERWORLD||level.getDifficulty()==Difficulty.PEACEFUL||!level.getGameRules().getBoolean(GameRules.RULE_DOMOBSPAWNING)
                ||!level.hasChunkAt(feet)||feet.distSqr(entrant)>48*48||feet.distSqr(entrant)<36)return false;
        var state=BlueprintSpawnState.get(level);var marker=state.markers.get(key);
        if(marker!=null&&(marker.cleared||!marker.members.isEmpty()||marker.nextSpawn>level.getGameTime()))return false;
        var type=EliteContent.MECHANIST.get();var box=type.getDimensions().makeBoundingBox(feet.getX()+.5,feet.getY(),feet.getZ()+.5);
        if(!level.getBlockState(feet.below()).isFaceSturdy(level,feet.below(),Direction.UP)||!level.getFluidState(feet).isEmpty()
                ||!level.noCollision(null,box)||!level.getEntitiesOfClass(Mechanist.class,new AABB(feet).inflate(32),Entity::isAlive).isEmpty())return false;
        var actor=type.create(level);if(actor==null)return false;actor.moveTo(feet.getX()+.5,feet.getY(),feet.getZ()+.5,0,0);actor.setPersistenceRequired();actor.bindEncounter(key);
        actor.finalizeSpawn(level,level.getCurrentDifficultyAt(feet),MobSpawnType.STRUCTURE,null,null);if(!level.addFreshEntity(actor))return false;
        if(marker==null){marker=new BlueprintSpawnState.Marker(key,feet);state.markers.put(key,marker);}marker.members.add(actor.getUUID());marker.produced=1;state.setDirty();return true;
    }
    public static boolean spawnSpiderWoman(ServerLevel level,String key,BlockPos feet,BlockPos entrant){
        if(level.dimension()!=Level.OVERWORLD||level.getDifficulty()==Difficulty.PEACEFUL||!level.getGameRules().getBoolean(GameRules.RULE_DOMOBSPAWNING)
            ||!level.hasChunkAt(feet)||feet.distSqr(entrant)>48*48||feet.distSqr(entrant)<36)return false;
        var state=BlueprintSpawnState.get(level);var marker=state.markers.get(key);if(marker!=null&&(marker.cleared||!marker.members.isEmpty()||marker.nextSpawn>level.getGameTime()))return false;
        var type=EliteContent.SPIDER_WOMAN.get();var box=type.getDimensions().makeBoundingBox(feet.getX()+.5,feet.getY(),feet.getZ()+.5);var ceiling=BlockPos.containing(feet.getX()+.5,box.maxY+.06,feet.getZ()+.5);
        if(!level.getBlockState(ceiling).isFaceSturdy(level,ceiling,Direction.DOWN)||!level.getFluidState(feet).isEmpty()||!level.noCollision(null,box)
            ||!level.getEntitiesOfClass(SpiderWoman.class,new AABB(feet).inflate(32),Entity::isAlive).isEmpty())return false;
        var actor=type.create(level);if(actor==null)return false;actor.moveTo(feet.getX()+.5,feet.getY(),feet.getZ()+.5,0,0);actor.setPersistenceRequired();actor.bindEncounter(key);
        actor.finalizeSpawn(level,level.getCurrentDifficultyAt(feet),MobSpawnType.STRUCTURE,null,null);if(!level.addFreshEntity(actor))return false;
        if(marker==null){marker=new BlueprintSpawnState.Marker(key,feet);state.markers.put(key,marker);}marker.members.add(actor.getUUID());marker.produced=1;state.setDirty();return true;
    }
    private EliteEncounters(){}
}
