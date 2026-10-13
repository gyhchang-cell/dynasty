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
    public static final Placement ALCHEMIST=new Placement("minecraft:overworld","open alchemy shed in existing forest herbal retreat","STRUCTURE_ENCOUNTER","12000 ticks after confirmed death; unloaded UUID retains slot",1,"NONE");
    public static final Placement TIDE_YASHA=new Placement("minecraft:overworld","loaded submerged warm or cold ocean ruin","STRUCTURE_ENCOUNTER","12000 ticks after confirmed death; unloaded UUID retains slot",1,"NONE");
    public static final Placement RAGE_CORPSE=new Placement("minecraft:overworld","open east flank of the existing remastered imperial tomb vault","FIXED_STRUCTURE_ELITE","12000 ticks after confirmed death; unloaded UUID retains slot",1,"NONE");
    public static final Placement INK_ASSASSIN=new Placement("minecraft:overworld","existing Tiangong inner-vault approach in the central hall","FIXED_STRUCTURE_ELITE","12000 ticks after confirmed death; unloaded UUID retains slot",1,"NONE");
    public static final Placement BRONZE_GORILLA=new Placement("minecraft:overworld","loaded high-mountain ruined portal clearing; secondary existing ancient battlefield west muster ground","STRUCTURE_ELITE","12000 ticks after confirmed death; unloaded UUID retains slot",1,"NONE");
    public static final Placement LAMP_JUDGE=new Placement("dynasty:underworld","loaded open foyer approach of the current seal vault","STRUCTURE_ELITE","12000 ticks after confirmed death; unloaded UUID retains slot",1,"NONE");
    private static final ResourceLocation UNDERWORLD=new ResourceLocation("dynasty","underworld");
    public static final Placement GOLDEN_EAGLE=new Placement("minecraft:overworld","loaded snowy high-mountain ground beside existing pillager outposts; hover4m","STRUCTURE_ELITE","12000 ticks after confirmed death; unloaded UUID retains slot",1,"NONE");
    public static final Placement BRONZE_SUANNI=new Placement("minecraft:overworld","existing remastered imperial tomb western vault flank15,1,17","FIXED_GUARD","ONE_SHOT_SAVEDDATA after confirmed death; unloaded UUID retains slot",1,"NONE");
    private static final TagKey<Structure> SUANNI_SITES=TagKey.create(Registries.STRUCTURE,new ResourceLocation("dynasty","blueprint/suanni_sites"));
    private static final TagKey<Structure> EAGLE_SITES=TagKey.create(Registries.STRUCTURE,new ResourceLocation("dynasty","blueprint/eagle_sites"));
    private static final TagKey<Structure> JUDGE_SITES=TagKey.create(Registries.STRUCTURE,new ResourceLocation("dynasty","blueprint/judge_sites"));
    private static final TagKey<Structure> GORILLA_SITES=TagKey.create(Registries.STRUCTURE,new ResourceLocation("dynasty","blueprint/gorilla_sites"));
    private static final TagKey<Structure> TIDE_YASHA_SITES=TagKey.create(Registries.STRUCTURE,new ResourceLocation("dynasty","blueprint/tide_yasha_sites"));
    private static final TagKey<Structure> ALCHEMIST_SITES=TagKey.create(Registries.STRUCTURE,new ResourceLocation("dynasty","blueprint/alchemist_sites"));
    private static final TagKey<Structure> SPIDER_WOMAN_SITES=TagKey.create(Registries.STRUCTURE,new ResourceLocation("dynasty","blueprint/spider_woman_sites"));
    private static final TagKey<Structure> SITES=TagKey.create(Registries.STRUCTURE,new ResourceLocation("dynasty","blueprint/battlefields"));
    private static final TagKey<Structure> MECHANIST_SITES=TagKey.create(Registries.STRUCTURE,new ResourceLocation("dynasty","blueprint/mechanist_sites"));
    private static final TagKey<Structure> JINWU_SITES=TagKey.create(Registries.STRUCTURE,new ResourceLocation("dynasty","blueprint/jinwu_sites"));
    private static final TagKey<Structure> FOX_SITES=TagKey.create(Registries.STRUCTURE,new ResourceLocation("dynasty","blueprint/fox_sites"));
    private static final TagKey<Structure> HAMMER_SITES=TagKey.create(Registries.STRUCTURE,new ResourceLocation("dynasty","blueprint/hammer_sites"));
    public static void memberDied(Entity mob){
        if(mob.level() instanceof ServerLevel level){
            var state=BlueprintSpawnState.get(level);
            if(mob instanceof Jinwu||mob instanceof HammerGuardian||mob instanceof BronzeSuanni)for(var marker:state.markers.values())if(marker.members.contains(mob.getUUID())){marker.cleared=true;state.setDirty();break;}
            state.memberDied(mob.getUUID(),level.getGameTime());
        }
    }
    @SubscribeEvent public static void left(EntityLeaveLevelEvent event){
        var entity=event.getEntity();
        if((entity instanceof HeadlessGeneral||entity instanceof GhostCarriageBird||entity instanceof Mechanist||entity instanceof Jinwu||entity instanceof HammerGuardian||entity instanceof SpiderWoman||entity instanceof Alchemist||entity instanceof TideYasha||entity instanceof RageCorpse||entity instanceof InkAssassin||entity instanceof BronzeGorilla||entity instanceof LampJudge||entity instanceof GoldenEagle||entity instanceof BronzeSuanni||entity instanceof FoxMatron fox&&!fox.isDecoy())&&entity.getRemovalReason()!=null&&entity.getRemovalReason().shouldDestroy())memberDied(entity);
    }
    @SubscribeEvent public static void tick(TickEvent.LevelTickEvent event){
        if(event.phase!=TickEvent.Phase.END||!(event.level instanceof ServerLevel level)||level.dimension()!=Level.OVERWORLD&&!level.dimension().location().equals(UNDERWORLD)
                ||level.getGameTime()%100!=0||level.getDifficulty()==Difficulty.PEACEFUL||!level.getGameRules().getBoolean(GameRules.RULE_DOMOBSPAWNING))return;
        var registry=level.registryAccess().registryOrThrow(Registries.STRUCTURE);var visited=new HashSet<String>();int budget=2,refs=0;
        for(var player:level.players()){
            if(player.isSpectator()||!player.isAlive())continue;var centre=player.chunkPosition();
            for(int dx=-1;dx<=1;dx++)for(int dz=-1;dz<=1;dz++){
                var chunk=level.getChunkSource().getChunkNow(centre.x+dx,centre.z+dz);if(chunk==null)continue;
                var candidates=new java.util.ArrayList<net.minecraft.world.level.levelgen.structure.StructureStart>();
                chunk.getAllStarts().forEach((type,start)->{var holder=registry.wrapAsHolder(type);if(holder.is(SITES)||holder.is(MECHANIST_SITES)||holder.is(JINWU_SITES)||holder.is(FOX_SITES)||holder.is(ALCHEMIST_SITES)||holder.is(HAMMER_SITES)||holder.is(SPIDER_WOMAN_SITES)||holder.is(TIDE_YASHA_SITES)||holder.is(GORILLA_SITES)||holder.is(JUDGE_SITES)||holder.is(EAGLE_SITES)||holder.is(SUANNI_SITES))candidates.add(start);});
                for(var entry:chunk.getAllReferences().entrySet())if(registry.wrapAsHolder(entry.getKey()).is(SITES)||registry.wrapAsHolder(entry.getKey()).is(MECHANIST_SITES)||registry.wrapAsHolder(entry.getKey()).is(JINWU_SITES)||registry.wrapAsHolder(entry.getKey()).is(FOX_SITES)||registry.wrapAsHolder(entry.getKey()).is(ALCHEMIST_SITES)||registry.wrapAsHolder(entry.getKey()).is(HAMMER_SITES)||registry.wrapAsHolder(entry.getKey()).is(SPIDER_WOMAN_SITES)||registry.wrapAsHolder(entry.getKey()).is(TIDE_YASHA_SITES)||registry.wrapAsHolder(entry.getKey()).is(GORILLA_SITES)||registry.wrapAsHolder(entry.getKey()).is(JUDGE_SITES)||registry.wrapAsHolder(entry.getKey()).is(EAGLE_SITES)||registry.wrapAsHolder(entry.getKey()).is(SUANNI_SITES))for(long packed:entry.getValue()){
                    if(++refs>64)return;var startChunk=level.getChunkSource().getChunkNow(ChunkPos.getX(packed),ChunkPos.getZ(packed));
                    if(startChunk!=null)candidates.add(startChunk.getStartForStructure(entry.getKey()));
                }
                for(var start:candidates){
                    if(start==null||!start.isValid())continue;var b=start.getBoundingBox();
                    if(player.getX()<b.minX()-24||player.getX()>b.maxX()+24||player.getZ()<b.minZ()-24||player.getZ()>b.maxZ()+24)continue;
                    if(registry.wrapAsHolder(start.getStructure()).is(EAGLE_SITES)){
                        String key=level.dimension().location()+"/"+registry.getKey(start.getStructure())+"@"+start.getChunkPos().toLong()+":golden_eagle";
                        if(visited.add(key)&&spawnGoldenEagleAtOutpost(level,key,b,player.blockPosition())&&--budget<=0)return;
                        continue;
                    }
                    if(registry.wrapAsHolder(start.getStructure()).is(JUDGE_SITES)){
                        String key=level.dimension().location()+"/"+registry.getKey(start.getStructure())+"@"+start.getChunkPos().toLong()+":lamp_judge";
                        if(visited.add(key))for(var piece:start.getPieces())if(piece instanceof com.dynasty.puzzle.PuzzleRuinPiece ruin){var feet=ruin.judgePosition();if(feet!=null&&spawnLampJudgeAtVault(level,key,feet,player.blockPosition())&&--budget<=0)return;}
                        continue;
                    }
                    if(registry.wrapAsHolder(start.getStructure()).is(GORILLA_SITES)){
                        String key=level.dimension().location()+"/"+registry.getKey(start.getStructure())+"@"+start.getChunkPos().toLong()+":bronze_gorilla";
                        if(visited.add(key)&&spawnBronzeGorillaAtMountainRuin(level,key,b,player.blockPosition())&&--budget<=0)return;
                        continue;
                    }
                    if(registry.wrapAsHolder(start.getStructure()).is(TIDE_YASHA_SITES)){
                        String key=level.dimension().location()+"/"+registry.getKey(start.getStructure())+"@"+start.getChunkPos().toLong()+":tide_yasha";
                        if(visited.add(key)&&spawnTideYashaAtRuin(level,key,b,player.blockPosition())&&--budget<=0)return;
                        continue;
                    }
                    if(registry.wrapAsHolder(start.getStructure()).is(SUANNI_SITES)){
                        String key=level.dimension().location()+"/"+registry.getKey(start.getStructure())+"@"+start.getChunkPos().toLong()+":bronze_suanni";
                        if(visited.add(key))for(var piece:start.getPieces())if(piece instanceof com.dynasty.structure.TombPiece tomb){var feet=tomb.suanniPosition();if(feet!=null&&spawnBronzeSuanni(level,key,feet,player.blockPosition())&&--budget<=0)return;}
                    }
                    if(registry.wrapAsHolder(start.getStructure()).is(HAMMER_SITES)){
                        String corpseKey=level.dimension().location()+"/"+registry.getKey(start.getStructure())+"@"+start.getChunkPos().toLong()+":rage_corpse";
                        if(visited.add(corpseKey))for(var piece:start.getPieces())if(piece instanceof com.dynasty.structure.TombPiece tomb){var feet=tomb.rageCorpsePosition();if(feet!=null&&spawnRageCorpse(level,corpseKey,feet,player.blockPosition())&&--budget<=0)return;}
                        String key=registry.getKey(start.getStructure())+"@"+start.getChunkPos().toLong()+":hammer_guardian";
                        if(visited.add(key))for(var piece:start.getPieces())if(piece instanceof com.dynasty.structure.TombPiece tomb
                            &&spawnHammer(level,key,tomb.hammerPosition(),player.blockPosition())&&--budget<=0)return;
                    }
                    if(registry.wrapAsHolder(start.getStructure()).is(ALCHEMIST_SITES)){
                        String key=level.dimension().location()+"/"+registry.getKey(start.getStructure())+"@"+start.getChunkPos().toLong()+":alchemist";
                        if(visited.add(key))for(var piece:start.getPieces())if(piece instanceof com.dynasty.structure.TravelSitePiece travel){var feet=travel.alchemistPosition();if(feet!=null&&spawnAlchemist(level,key,feet,player.blockPosition())&&--budget<=0)return;}
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
                        String inkKey=level.dimension().location()+"/"+registry.getKey(start.getStructure())+"@"+start.getChunkPos().toLong()+":ink_assassin";
                        if(visited.add(inkKey))for(var piece:start.getPieces())for(var feet:com.dynasty.structure.megabuild.MechanicalPatrols.inkAssassinPositions(piece))
                            if(spawnInkAssassin(level,inkKey,feet,player.blockPosition())&&--budget<=0)return;
                        String key=level.dimension().location()+"/"+registry.getKey(start.getStructure())+"@"+start.getChunkPos().toLong()+":mechanist";
                        if(!visited.add(key))continue;
                        boolean spawned=false;
                        for(var piece:start.getPieces())for(var feet:com.dynasty.structure.megabuild.MechanicalPatrols.mechanistPositions(piece))
                            if(!spawned&&spawnMechanist(level,key,feet,player.blockPosition()))spawned=true;
                        if(spawned&&--budget<=0)return;
                        continue;
                    }
                    if(registry.wrapAsHolder(start.getStructure()).is(SITES)){
                        String apeKey=level.dimension().location()+"/"+registry.getKey(start.getStructure())+"@"+start.getChunkPos().toLong()+":bronze_gorilla";
                        if(visited.add(apeKey))for(var piece:start.getPieces())if(piece instanceof com.dynasty.structure.BattlefieldPiece camp&&spawnBronzeGorilla(level,apeKey,camp.bronzeGorillaPosition(),player.blockPosition())&&--budget<=0)return;
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
    private static boolean spawnLampJudgeAtVault(ServerLevel level,String key,BlockPos authored,BlockPos entrant){
        if(!level.dimension().location().equals(UNDERWORLD))return false;
        for(int dy=2;dy>=-3;dy--)if(spawnLampJudge(level,key,authored.above(dy),entrant))return true;
        return false;
    }
    public static boolean spawnLampJudge(ServerLevel level,String key,BlockPos feet,BlockPos entrant){
        if(!level.dimension().location().equals(UNDERWORLD)||level.getDifficulty()==Difficulty.PEACEFUL||!level.getGameRules().getBoolean(GameRules.RULE_DOMOBSPAWNING)||feet.distSqr(entrant)>48*48||feet.distSqr(entrant)<36)return false;
        for(int dx:new int[]{-4,4})for(int dz:new int[]{-4,4})if(!level.hasChunkAt(feet.offset(dx,0,dz)))return false;
        var state=BlueprintSpawnState.get(level);var marker=state.markers.get(key);if(marker!=null&&(marker.cleared||!marker.members.isEmpty()||marker.nextSpawn>level.getGameTime()))return false;
        var type=EliteContent.LAMP_JUDGE.get();var box=type.getDimensions().makeBoundingBox(feet.getX()+.5,feet.getY(),feet.getZ()+.5);
        for(int dx=-3;dx<=3;dx++)for(int dz=-3;dz<=3;dz++)if(dx*dx+dz*dz<=10){var cell=feet.offset(dx,0,dz);if(!level.getBlockState(cell.below()).isFaceSturdy(level,cell.below(),Direction.UP)||!level.getFluidState(cell).isEmpty())return false;}
        var arena=new AABB(feet.getX()-3,feet.getY(),feet.getZ()-3,feet.getX()+4,feet.getY()+6,feet.getZ()+4);
        if(!level.getWorldBorder().isWithinBounds(arena)||!level.noCollision(null,arena)||!level.getEntitiesOfClass(LampJudge.class,new AABB(feet).inflate(32),Entity::isAlive).isEmpty())return false;
        var mob=type.create(level);if(mob==null)return false;mob.moveTo(feet.getX()+.5,feet.getY(),feet.getZ()+.5,0,0);mob.setPersistenceRequired();mob.bindEncounter(key);mob.finalizeSpawn(level,level.getCurrentDifficultyAt(feet),MobSpawnType.STRUCTURE,null,null);if(!level.addFreshEntity(mob))return false;
        if(marker==null){marker=new BlueprintSpawnState.Marker(key,feet);state.markers.put(key,marker);}marker.members.add(mob.getUUID());marker.produced=1;state.setDirty();return true;
    }
    public static boolean spawnInkAssassin(ServerLevel level,String key,BlockPos feet,BlockPos entrant){
        if(level.dimension()!=Level.OVERWORLD||level.getDifficulty()==Difficulty.PEACEFUL||!level.getGameRules().getBoolean(GameRules.RULE_DOMOBSPAWNING)||feet.distSqr(entrant)>48*48||feet.distSqr(entrant)<36)return false;
        for(int dx:new int[]{-2,2})for(int dz:new int[]{-2,2})if(!level.hasChunkAt(feet.offset(dx,0,dz)))return false;
        var state=BlueprintSpawnState.get(level);var marker=state.markers.get(key);if(marker!=null&&(marker.cleared||!marker.members.isEmpty()||marker.nextSpawn>level.getGameTime()))return false;
        var type=EliteContent.INK_ASSASSIN.get();var box=type.getDimensions().makeBoundingBox(feet.getX()+.5,feet.getY(),feet.getZ()+.5);
        if(!level.getBlockState(feet.below()).isFaceSturdy(level,feet.below(),Direction.UP)||!level.getFluidState(feet).isEmpty()||!level.getWorldBorder().isWithinBounds(box)||!level.noCollision(null,box)||!level.getEntitiesOfClass(InkAssassin.class,new AABB(feet).inflate(32),Entity::isAlive).isEmpty())return false;
        var mob=type.create(level);if(mob==null)return false;mob.moveTo(feet.getX()+.5,feet.getY(),feet.getZ()+.5,0,0);mob.setPersistenceRequired();mob.bindEncounter(key);mob.finalizeSpawn(level,level.getCurrentDifficultyAt(feet),MobSpawnType.STRUCTURE,null,null);if(!level.addFreshEntity(mob))return false;
        if(marker==null){marker=new BlueprintSpawnState.Marker(key,feet);state.markers.put(key,marker);}marker.members.add(mob.getUUID());marker.produced=1;state.setDirty();return true;
    }
    public static boolean spawnBronzeSuanni(ServerLevel level,String key,BlockPos feet,BlockPos entrant){
        if(level.dimension()!=Level.OVERWORLD||level.getDifficulty()==Difficulty.PEACEFUL||!level.getGameRules().getBoolean(GameRules.RULE_DOMOBSPAWNING)||feet.distSqr(entrant)>48*48||feet.distSqr(entrant)<36)return false;
        for(int x:new int[]{-3,3})for(int z:new int[]{-3,3})if(!level.hasChunkAt(feet.offset(x,0,z)))return false;
        var state=BlueprintSpawnState.get(level);var marker=state.markers.get(key);if(marker!=null&&(marker.cleared||!marker.members.isEmpty()||marker.nextSpawn>level.getGameTime()))return false;
        for(int x=-2;x<=2;x++)for(int z=-2;z<=2;z++){var cell=feet.offset(x,0,z);if(!level.getBlockState(cell.below()).isFaceSturdy(level,cell.below(),Direction.UP)||!level.getFluidState(cell).isEmpty())return false;}
        var type=EliteContent.BRONZE_SUANNI.get();var box=type.getDimensions().makeBoundingBox(feet.getX()+.5,feet.getY(),feet.getZ()+.5);var clear=new AABB(feet.getX()-2.5,feet.getY(),feet.getZ()-2.5,feet.getX()+3.5,feet.getY()+4,feet.getZ()+3.5);
        if(!level.getWorldBorder().isWithinBounds(clear)||!level.noCollision(null,clear)||!level.noCollision(null,box)||!level.getEntitiesOfClass(BronzeSuanni.class,new AABB(feet).inflate(32),Entity::isAlive).isEmpty())return false;
        var mob=type.create(level);if(mob==null)return false;mob.moveTo(feet.getX()+.5,feet.getY(),feet.getZ()+.5,0,0);mob.setPersistenceRequired();mob.bindEncounter(key);mob.finalizeSpawn(level,level.getCurrentDifficultyAt(feet),MobSpawnType.STRUCTURE,null,null);if(!level.addFreshEntity(mob))return false;
        if(marker==null){marker=new BlueprintSpawnState.Marker(key,feet);state.markers.put(key,marker);}marker.members.add(mob.getUUID());marker.produced=1;state.setDirty();return true;
    }
    private static boolean spawnGoldenEagleAtOutpost(ServerLevel level,String key,net.minecraft.world.level.levelgen.structure.BoundingBox bounds,BlockPos entrant){
        if(level.dimension()!=Level.OVERWORLD)return false;var marker=BlueprintSpawnState.get(level).markers.get(key);if(marker!=null&&(marker.cleared||!marker.members.isEmpty()||marker.nextSpawn>level.getGameTime()))return false;
        int cx=(bounds.minX()+bounds.maxX())/2,cz=(bounds.minZ()+bounds.maxZ())/2,top=Math.min(bounds.maxY()+1,level.getMaxBuildHeight()-8);
        for(int dx:new int[]{-10,0,10})for(int dz:new int[]{-10,0,10}){if(dx==0&&dz==0)continue;
            for(int y=top;y>=Math.max(100,top-23);y--){var feet=new BlockPos(cx+dx,y,cz+dz);boolean loaded=true;for(int x:new int[]{-3,3})for(int z:new int[]{-3,3})if(!level.hasChunkAt(feet.offset(x,0,z)))loaded=false;if(!loaded)continue;
                var biome=level.getBiome(feet);if(!(biome.is(net.minecraft.world.level.biome.Biomes.FROZEN_PEAKS)||biome.is(net.minecraft.world.level.biome.Biomes.JAGGED_PEAKS)||biome.is(net.minecraft.world.level.biome.Biomes.STONY_PEAKS)||biome.is(net.minecraft.world.level.biome.Biomes.SNOWY_SLOPES)))continue;
                if(spawnGoldenEagle(level,key,feet,entrant))return true;
            }
        }return false;
    }
    public static boolean spawnGoldenEagle(ServerLevel level,String key,BlockPos ground,BlockPos entrant){
        if(level.dimension()!=Level.OVERWORLD||level.getDifficulty()==Difficulty.PEACEFUL||!level.getGameRules().getBoolean(GameRules.RULE_DOMOBSPAWNING)||ground.distSqr(entrant)>48*48||ground.distSqr(entrant)<36)return false;
        for(int x:new int[]{-3,3})for(int z:new int[]{-3,3})if(!level.hasChunkAt(ground.offset(x,0,z)))return false;
        var state=BlueprintSpawnState.get(level);var marker=state.markers.get(key);if(marker!=null&&(marker.cleared||!marker.members.isEmpty()||marker.nextSpawn>level.getGameTime()))return false;
        for(int x=-1;x<=1;x++)for(int z=-1;z<=1;z++){var cell=ground.offset(x,0,z);if(!level.getBlockState(cell.below()).isFaceSturdy(level,cell.below(),Direction.UP)||!level.getFluidState(cell).isEmpty())return false;}
        var type=EliteContent.GOLDEN_EAGLE.get();var air=ground.above(4);var box=type.getDimensions().makeBoundingBox(air.getX()+.5,air.getY(),air.getZ()+.5);
        var clearance=new AABB(ground.getX()-2.5,ground.getY(),ground.getZ()-2.5,ground.getX()+3.5,ground.getY()+7,ground.getZ()+3.5);
        if(!level.getWorldBorder().isWithinBounds(clearance)||!level.noCollision(null,clearance)||!level.noCollision(null,box)||!level.getEntitiesOfClass(GoldenEagle.class,new AABB(ground).inflate(32),Entity::isAlive).isEmpty())return false;
        var mob=type.create(level);if(mob==null)return false;mob.moveTo(air.getX()+.5,air.getY(),air.getZ()+.5,0,0);mob.setPersistenceRequired();mob.bindEncounter(key);mob.finalizeSpawn(level,level.getCurrentDifficultyAt(air),MobSpawnType.STRUCTURE,null,null);if(!level.addFreshEntity(mob))return false;
        if(marker==null){marker=new BlueprintSpawnState.Marker(key,ground);state.markers.put(key,marker);}marker.members.add(mob.getUUID());marker.produced=1;state.setDirty();return true;
    }
    private static boolean spawnBronzeGorillaAtMountainRuin(ServerLevel level,String key,net.minecraft.world.level.levelgen.structure.BoundingBox bounds,BlockPos entrant){
        var marker=BlueprintSpawnState.get(level).markers.get(key);if(marker!=null&&(marker.cleared||!marker.members.isEmpty()||marker.nextSpawn>level.getGameTime()))return false;
        int cx=(bounds.minX()+bounds.maxX())/2,cz=(bounds.minZ()+bounds.maxZ())/2,top=Math.min(bounds.maxY()+1,level.getMaxBuildHeight()-4);
        // Nine local columns, at most24 vertical candidates. This reads loaded terrain only.
        for(int dx:new int[]{-8,0,8})for(int dz:new int[]{-8,0,8})for(int y=top;y>=Math.max(96,top-23);y--){
            var feet=new BlockPos(cx+dx,y,cz+dz);boolean loaded=true;
            for(int x:new int[]{-2,2})for(int z:new int[]{-2,2})if(!level.hasChunkAt(feet.offset(x,0,z)))loaded=false;
            if(!loaded||!level.getBiome(feet).is(net.minecraft.tags.BiomeTags.IS_MOUNTAIN)||!level.getBlockState(feet.below()).isFaceSturdy(level,feet.below(),Direction.UP))continue;
            boolean floor=true;for(int x=-2;x<=2;x++)for(int z=-2;z<=2;z++){var cell=feet.offset(x,0,z);if(!level.getBlockState(cell.below()).isFaceSturdy(level,cell.below(),Direction.UP)||!level.getFluidState(cell).isEmpty())floor=false;}
            if(floor&&spawnBronzeGorilla(level,key,feet,entrant))return true;
        }return false;
    }
    public static boolean spawnBronzeGorilla(ServerLevel level,String key,BlockPos feet,BlockPos entrant){
        if(level.dimension()!=Level.OVERWORLD||level.getDifficulty()==Difficulty.PEACEFUL||!level.getGameRules().getBoolean(GameRules.RULE_DOMOBSPAWNING)||feet.distSqr(entrant)>48*48||feet.distSqr(entrant)<36)return false;
        for(int dx:new int[]{-3,3})for(int dz:new int[]{-3,3})if(!level.hasChunkAt(feet.offset(dx,0,dz)))return false;
        var state=BlueprintSpawnState.get(level);var marker=state.markers.get(key);if(marker!=null&&(marker.cleared||!marker.members.isEmpty()||marker.nextSpawn>level.getGameTime()))return false;
        var type=EliteContent.BRONZE_GORILLA.get();var box=type.getDimensions().makeBoundingBox(feet.getX()+.5,feet.getY(),feet.getZ()+.5);
        if(!level.getBlockState(feet.below()).isFaceSturdy(level,feet.below(),Direction.UP)||!level.getFluidState(feet).isEmpty()||!level.getWorldBorder().isWithinBounds(box)||!level.noCollision(null,box)||!level.getEntitiesOfClass(BronzeGorilla.class,new AABB(feet).inflate(32),Entity::isAlive).isEmpty())return false;
        var mob=type.create(level);if(mob==null)return false;mob.moveTo(feet.getX()+.5,feet.getY(),feet.getZ()+.5,0,0);mob.setPersistenceRequired();mob.bindEncounter(key);mob.finalizeSpawn(level,level.getCurrentDifficultyAt(feet),MobSpawnType.STRUCTURE,null,null);if(!level.addFreshEntity(mob))return false;
        if(marker==null){marker=new BlueprintSpawnState.Marker(key,feet);state.markers.put(key,marker);}marker.members.add(mob.getUUID());marker.produced=1;state.setDirty();return true;
    }
    public static boolean spawnRageCorpse(ServerLevel level,String key,BlockPos feet,BlockPos entrant){
        if(level.dimension()!=Level.OVERWORLD||level.getDifficulty()==Difficulty.PEACEFUL||!level.getGameRules().getBoolean(GameRules.RULE_DOMOBSPAWNING)||feet.distSqr(entrant)>48*48||feet.distSqr(entrant)<36)return false;
        for(int dx:new int[]{-3,3})for(int dz:new int[]{-3,3})if(!level.hasChunkAt(feet.offset(dx,0,dz)))return false;
        var state=BlueprintSpawnState.get(level);var marker=state.markers.get(key);if(marker!=null&&(marker.cleared||!marker.members.isEmpty()||marker.nextSpawn>level.getGameTime()))return false;
        var type=EliteContent.RAGE_CORPSE.get();var box=type.getDimensions().makeBoundingBox(feet.getX()+.5,feet.getY(),feet.getZ()+.5);
        if(!level.getBlockState(feet.below()).isFaceSturdy(level,feet.below(),Direction.UP)||!level.getFluidState(feet).isEmpty()||!level.getWorldBorder().isWithinBounds(box)||!level.noCollision(null,box)||!level.getEntitiesOfClass(RageCorpse.class,new AABB(feet).inflate(32),Entity::isAlive).isEmpty())return false;
        var mob=type.create(level);if(mob==null)return false;mob.moveTo(feet.getX()+.5,feet.getY(),feet.getZ()+.5,0,0);mob.setPersistenceRequired();mob.bindEncounter(key);mob.finalizeSpawn(level,level.getCurrentDifficultyAt(feet),MobSpawnType.STRUCTURE,null,null);if(!level.addFreshEntity(mob))return false;
        if(marker==null){marker=new BlueprintSpawnState.Marker(key,feet);state.markers.put(key,marker);}marker.members.add(mob.getUUID());marker.produced=1;state.setDirty();return true;
    }
    private static boolean spawnTideYashaAtRuin(ServerLevel level,String key,net.minecraft.world.level.levelgen.structure.BoundingBox b,BlockPos entrant){
        var marker=BlueprintSpawnState.get(level).markers.get(key);
        if(marker!=null&&(marker.cleared||!marker.members.isEmpty()||marker.nextSpawn>level.getGameTime()))return false;
        int cx=(b.minX()+b.maxX())/2,cz=(b.minZ()+b.maxZ())/2,top=Math.min(b.maxY()+1,level.getMaxBuildHeight()-3);
        for(int dx=-6;dx<=6;dx+=3)for(int dz=-6;dz<=6;dz+=3)for(int y=top;y>=Math.max(b.minY()-8,top-14);y--){
            var feet=new BlockPos(cx+dx,y,cz+dz);
            if(feet.getX()<b.minX()-2||feet.getX()>b.maxX()+2||feet.getZ()<b.minZ()-2||feet.getZ()>b.maxZ()+2)continue;
            if(spawnTideYasha(level,key,feet,entrant))return true;
        }return false;
    }
    public static boolean spawnTideYasha(ServerLevel level,String key,BlockPos feet,BlockPos entrant){
        if(level.dimension()!=Level.OVERWORLD||level.getDifficulty()==Difficulty.PEACEFUL||!level.getGameRules().getBoolean(GameRules.RULE_DOMOBSPAWNING)||feet.distSqr(entrant)>48*48||feet.distSqr(entrant)<36)return false;
        for(int dx:new int[]{-2,2})for(int dz:new int[]{-2,2})if(!level.hasChunkAt(feet.offset(dx,0,dz)))return false;
        var state=BlueprintSpawnState.get(level);var marker=state.markers.get(key);
        if(marker!=null&&(marker.cleared||!marker.members.isEmpty()||marker.nextSpawn>level.getGameTime()))return false;
        for(int dx=-1;dx<=1;dx++)for(int dz=-1;dz<=1;dz++){var cell=feet.offset(dx,0,dz);if(!level.getFluidState(cell).is(net.minecraft.tags.FluidTags.WATER)||!level.getFluidState(cell.above()).is(net.minecraft.tags.FluidTags.WATER)||!level.getBlockState(cell.below()).isFaceSturdy(level,cell.below(),Direction.UP))return false;}
        var type=EliteContent.TIDE_YASHA.get();var box=type.getDimensions().makeBoundingBox(feet.getX()+.5,feet.getY(),feet.getZ()+.5);
        if(!level.getWorldBorder().isWithinBounds(box)||!level.noCollision(null,box)||!level.getEntitiesOfClass(TideYasha.class,new AABB(feet).inflate(32),Entity::isAlive).isEmpty())return false;
        var actor=type.create(level);if(actor==null)return false;actor.moveTo(feet.getX()+.5,feet.getY(),feet.getZ()+.5,0,0);actor.setPersistenceRequired();actor.bindEncounter(key);actor.finalizeSpawn(level,level.getCurrentDifficultyAt(feet),MobSpawnType.STRUCTURE,null,null);if(!level.addFreshEntity(actor))return false;
        if(marker==null){marker=new BlueprintSpawnState.Marker(key,feet);state.markers.put(key,marker);}marker.members.add(actor.getUUID());marker.produced=1;state.setDirty();return true;
    }
    public static boolean spawnAlchemist(ServerLevel level,String key,BlockPos feet,BlockPos entrant){
        if(level.dimension()!=Level.OVERWORLD||level.getDifficulty()==Difficulty.PEACEFUL||!level.getGameRules().getBoolean(GameRules.RULE_DOMOBSPAWNING)||!level.hasChunkAt(feet)||feet.distSqr(entrant)>48*48||feet.distSqr(entrant)<36)return false;
        var state=BlueprintSpawnState.get(level);var marker=state.markers.get(key);if(marker!=null&&(marker.cleared||!marker.members.isEmpty()||marker.nextSpawn>level.getGameTime()))return false;
        var type=EliteContent.ALCHEMIST.get();var box=type.getDimensions().makeBoundingBox(feet.getX()+.5,feet.getY(),feet.getZ()+.5);
        if(!level.getBlockState(feet.below()).isFaceSturdy(level,feet.below(),Direction.UP)||!level.getFluidState(feet).isEmpty()||!level.noCollision(null,box)||!level.getEntitiesOfClass(Alchemist.class,new AABB(feet).inflate(32),Entity::isAlive).isEmpty())return false;
        var actor=type.create(level);if(actor==null)return false;actor.moveTo(feet.getX()+.5,feet.getY(),feet.getZ()+.5,0,0);actor.setPersistenceRequired();actor.bindEncounter(key);actor.finalizeSpawn(level,level.getCurrentDifficultyAt(feet),MobSpawnType.STRUCTURE,null,null);if(!level.addFreshEntity(actor))return false;
        if(marker==null){marker=new BlueprintSpawnState.Marker(key,feet);state.markers.put(key,marker);}marker.members.add(actor.getUUID());marker.produced=1;state.setDirty();return true;
    }
}
