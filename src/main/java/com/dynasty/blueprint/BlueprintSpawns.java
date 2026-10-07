package com.dynasty.blueprint;

import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.TagKey;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.SpawnPlacements;
import net.minecraft.world.level.GameRules;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.phys.AABB;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.SpawnPlacementRegisterEvent;
import net.minecraftforge.event.entity.EntityLeaveLevelEvent;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.List;

/** Ecology uses biome modifiers; troops are bounded encounters inside real existing structure starts. */
@Mod.EventBusSubscriber(modid="dynasty")
public final class BlueprintSpawns {
    private static final TagKey<Structure> MILITARY=TagKey.create(Registries.STRUCTURE,new ResourceLocation("dynasty","blueprint/military_sites"));
    private static final TagKey<Structure> RITUAL=TagKey.create(Registries.STRUCTURE,new ResourceLocation("dynasty","blueprint/ritual_sites"));
    private static final TagKey<Structure> BATTLEFIELD=TagKey.create(Registries.STRUCTURE,new ResourceLocation("dynasty","blueprint/battlefields"));
    private static final TagKey<Structure> TOMBS=TagKey.create(Registries.STRUCTURE,new ResourceLocation("dynasty","dungeons/chensha_garrisons"));
    private static final TagKey<Structure> GUARDS=TagKey.create(Registries.STRUCTURE,new ResourceLocation("dynasty","blueprint/rebel_guard_sites"));
    private static final TagKey<Structure> GHOSTS=TagKey.create(Registries.STRUCTURE,new ResourceLocation("dynasty","blueprint/ghost_sites"));
    private static final TagKey<Structure> CORPSES=TagKey.create(Registries.STRUCTURE,new ResourceLocation("dynasty","blueprint/corpse_sites"));
    private static final TagKey<Structure> CHILDREN=TagKey.create(Registries.STRUCTURE,new ResourceLocation("dynasty","blueprint/shroud_child_sites"));
    private static final TagKey<Structure> PAPERS=TagKey.create(Registries.STRUCTURE,new ResourceLocation("dynasty","blueprint/paper_swordsman_sites"));
    private static final TagKey<Structure> SKULLS=TagKey.create(Registries.STRUCTURE,new ResourceLocation("dynasty","blueprint/flying_skull_sites"));
    private static final TagKey<Structure> STONE_GUARDS=TagKey.create(Registries.STRUCTURE,new ResourceLocation("dynasty","blueprint/stone_guard_sites"));
    private static final TagKey<Structure> PALANQUINS=TagKey.create(Registries.STRUCTURE,new ResourceLocation("dynasty","blueprint/palanquin_sites"));
    private static final TagKey<Structure> BIXI=TagKey.create(Registries.STRUCTURE,new ResourceLocation("dynasty","blueprint/bixi_sites"));
    private static final TagKey<Structure> DOGS=TagKey.create(Registries.STRUCTURE,new ResourceLocation("dynasty","blueprint/clockwork_dog_sites"));
    private static final TagKey<Structure> BRONZE_SNAKES=TagKey.create(Registries.STRUCTURE,new ResourceLocation("dynasty","blueprint/bronze_snake_sites"));
    private static final TagKey<Structure> SPIDERS=TagKey.create(Registries.STRUCTURE,new ResourceLocation("dynasty","blueprint/mining_spider_sites"));
    private BlueprintSpawns() {}
    public static void register(SpawnPlacementRegisterEvent event) {
        event.register(BlueprintEntities.TONGBI_FEITIAN_YECHA.get(),SpawnPlacements.Type.NO_RESTRICTIONS,
            Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,(type,level,reason,pos,random)->
                reason==MobSpawnType.SPAWN_EGG||reason==MobSpawnType.COMMAND||yechaHabitat(level.getLevel(),pos),SpawnPlacementRegisterEvent.Operation.REPLACE);
        event.register(BlueprintEntities.BAIMU_MOWU.get(),SpawnPlacements.Type.ON_GROUND,
            Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,(type,level,reason,pos,random)->
                reason==MobSpawnType.SPAWN_EGG||reason==MobSpawnType.COMMAND||centipedeHabitat(level.getLevel(),pos),SpawnPlacementRegisterEvent.Operation.REPLACE);
        event.register(BlueprintEntities.SHASHUI_FUNIGUI.get(),SpawnPlacements.Type.NO_RESTRICTIONS,
            Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,(type,level,reason,pos,random)->
                reason==MobSpawnType.SPAWN_EGG||reason==MobSpawnType.COMMAND||drownerHabitat(level.getLevel(),pos),SpawnPlacementRegisterEvent.Operation.REPLACE);
        event.register(BlueprintEntities.XUEJU_MANGGUYU.get(),SpawnPlacements.Type.NO_RESTRICTIONS,
            Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,(type,level,reason,pos,random)->
                reason==MobSpawnType.SPAWN_EGG||reason==MobSpawnType.COMMAND||fishHabitat(level.getLevel(),pos),SpawnPlacementRegisterEvent.Operation.REPLACE);
        event.register(BlueprintEntities.YOUDENG_GUIMIANFU.get(),SpawnPlacements.Type.NO_RESTRICTIONS,
            Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,(type,level,reason,pos,random)->
                reason==MobSpawnType.SPAWN_EGG||reason==MobSpawnType.COMMAND||batHabitat(level.getLevel(),pos),SpawnPlacementRegisterEvent.Operation.REPLACE);
        event.register(BlueprintEntities.BISHUI_XUANJIAO_YOUZI.get(),SpawnPlacements.Type.NO_RESTRICTIONS,
            Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,(type,level,reason,pos,random)->
                reason==MobSpawnType.SPAWN_EGG||reason==MobSpawnType.COMMAND||serpentHabitat(level.getLevel(),pos),SpawnPlacementRegisterEvent.Operation.REPLACE);
        event.register(BlueprintEntities.MINGSHA_SHIXIE.get(),SpawnPlacements.Type.ON_GROUND,
            Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,(type,level,reason,pos,random)->
                reason==MobSpawnType.SPAWN_EGG||reason==MobSpawnType.COMMAND||scorpionHabitat(level.getLevel(),pos),SpawnPlacementRegisterEvent.Operation.REPLACE);
        event.register(BlueprintEntities.KUMU_SHUJING.get(),SpawnPlacements.Type.ON_GROUND,
            Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,(type,level,reason,pos,random)->
                reason==MobSpawnType.SPAWN_EGG||reason==MobSpawnType.COMMAND||treeHabitat(level.getLevel(),pos),SpawnPlacementRegisterEvent.Operation.REPLACE);
        event.register(BlueprintEntities.CHIMU_ZHUHA.get(),SpawnPlacements.Type.NO_RESTRICTIONS,
            Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,(type,level,reason,pos,random)->
                reason==MobSpawnType.SPAWN_EGG||reason==MobSpawnType.COMMAND||toadHabitat(level.getLevel(),pos),SpawnPlacementRegisterEvent.Operation.REPLACE);
        event.register(BlueprintEntities.TIESUO_CHIHOU.get(),SpawnPlacements.Type.ON_GROUND,
            Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,(type,level,reason,pos,random)->{
                if(reason==MobSpawnType.SPAWN_EGG||reason==MobSpawnType.COMMAND)return true;
                var server=level.getLevel();
                return server.dimension()==Level.OVERWORLD&&server.getDifficulty()!=net.minecraft.world.Difficulty.PEACEFUL
                    &&!server.isDay()&&pos.getY()>=60&&pos.getY()<=220&&server.getMaxLocalRawBrightness(pos)<=7
                    &&com.dynasty.entity.DynastySpawnPlacement.hasStandingSpace(level,pos,type.getDimensions().makeBoundingBox(pos.getX()+.5,pos.getY(),pos.getZ()+.5))
                    &&server.getEntitiesOfClass(TemplateMob.class,new AABB(pos).inflate(32),e->e.getType()==type).size()<2;
            },SpawnPlacementRegisterEvent.Operation.REPLACE);
        event.register(BlueprintEntities.SHANJING_SHANXIAO.get(),SpawnPlacements.Type.ON_GROUND,
            Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,(type,level,reason,pos,random)-> {
                if(reason==MobSpawnType.SPAWN_EGG||reason==MobSpawnType.COMMAND)return true;
                var server=level.getLevel();
                return server.dimension()==Level.OVERWORLD && server.getDifficulty()!=net.minecraft.world.Difficulty.PEACEFUL
                    && pos.getY()>=50 && pos.getY()<=240 && (!server.isDay()||random.nextInt(4)==0)
                    && com.dynasty.entity.DynastySpawnPlacement.hasStandingSpace(level,pos,type.getDimensions().makeBoundingBox(pos.getX()+.5,pos.getY(),pos.getZ()+.5))
                    && server.getEntitiesOfClass(TemplateMob.class,new AABB(pos).inflate(24),e->e.getType()==type).size()<3;
            },SpawnPlacementRegisterEvent.Operation.REPLACE);
    }
    static boolean yechaHabitat(ServerLevel level,BlockPos pos){
        boolean dimension=level.dimension()==Level.OVERWORLD||level.dimension().location().toString().equals("dynasty:underworld");
        var type=BlueprintEntities.TONGBI_FEITIAN_YECHA.get();
        if(!dimension||level.getDifficulty()==net.minecraft.world.Difficulty.PEACEFUL||!level.hasChunkAt(pos)||pos.getY()<level.getMinBuildHeight()+10||pos.getY()>220
            ||!level.getBiome(pos).is(TagKey.create(Registries.BIOME,new ResourceLocation("dynasty","blueprint/yecha_habitat")))
            ||!level.noCollision(null,type.getDimensions().makeBoundingBox(pos.getX()+.5,pos.getY(),pos.getZ()+.5))
            ||level.getEntitiesOfClass(TemplateMob.class,new AABB(pos).inflate(32),m->m.isAlive()&&m.kind()==TemplateMob.Kind.YECHA).size()>=2)return false;
        for(int i=0;i<=5;i++)if(!level.getBlockState(pos.below(i)).getCollisionShape(level,pos.below(i)).isEmpty()||!level.getFluidState(pos.below(i)).isEmpty())return false;
        for(var direction:net.minecraft.core.Direction.Plane.HORIZONTAL){var p=pos.relative(direction,3).below();if(level.hasChunkAt(p)&&level.getBlockState(p).isFaceSturdy(level,p,net.minecraft.core.Direction.UP))return true;}
        return false;
    }
    static boolean centipedeHabitat(ServerLevel level,BlockPos pos){
        var type=BlueprintEntities.BAIMU_MOWU.get();
        return level.dimension()==Level.OVERWORLD&&level.getDifficulty()!=net.minecraft.world.Difficulty.PEACEFUL&&level.hasChunkAt(pos)
            &&pos.getY()<=0&&pos.getY()>level.getMinBuildHeight()&&!level.canSeeSky(pos)&&level.getMaxLocalRawBrightness(pos)<=7
            &&com.dynasty.entity.DynastySpawnPlacement.hasStandingSpace(level,pos,type.getDimensions().makeBoundingBox(pos.getX()+.5,pos.getY(),pos.getZ()+.5))
            &&level.getEntitiesOfClass(TemplateMob.class,new AABB(pos).inflate(32),m->m.isAlive()&&m.kind()==TemplateMob.Kind.CENTIPEDE).isEmpty();
    }
    static boolean drownerHabitat(ServerLevel level,BlockPos pos){
        boolean dimension=level.dimension()==Level.OVERWORLD||level.dimension().location().toString().equals("dynasty:underworld");
        return dimension&&level.getDifficulty()!=net.minecraft.world.Difficulty.PEACEFUL&&level.hasChunkAt(pos)
            &&level.getMaxLocalRawBrightness(pos)<=7&&level.getBiome(pos).is(TagKey.create(Registries.BIOME,new ResourceLocation("dynasty","blueprint/drowner_habitat")))
            &&DrownerBehavior.deepWater(level,pos)&&level.noCollision(null,BlueprintEntities.SHASHUI_FUNIGUI.get().getDimensions().makeBoundingBox(pos.getX()+.5,pos.getY(),pos.getZ()+.5))
            &&level.getEntitiesOfClass(TemplateMob.class,new AABB(pos).inflate(32),m->m.isAlive()&&m.kind()==TemplateMob.Kind.DROWNER).size()<2;
    }
    static boolean fishHabitat(ServerLevel level,BlockPos pos){
        if(pos.getY()>0||!cavePocket(level,pos))return false;
        return level.getEntitiesOfClass(TemplateMob.class,new AABB(pos).inflate(32),m->m.isAlive()&&m.kind()==TemplateMob.Kind.BLIND_FISH).size()<3;
    }
    /** A loaded five-by-five, six-block-tall dry cave pocket; no chunk generation during spawn checks. */
    static boolean batHabitat(ServerLevel level,BlockPos pos){
        return cavePocket(level,pos)&&level.getEntitiesOfClass(TemplateMob.class,new AABB(pos).inflate(32),m->m.isAlive()&&m.kind()==TemplateMob.Kind.LANTERN_BAT).size()<3;
    }
    static boolean cavePocket(ServerLevel level,BlockPos pos){
        if(level.dimension()!=Level.OVERWORLD||level.getDifficulty()==net.minecraft.world.Difficulty.PEACEFUL
            ||pos.getY()<level.getMinBuildHeight()+3||pos.getY()>80||!level.hasChunkAt(pos)||level.canSeeSky(pos)
            ||level.getMaxLocalRawBrightness(pos)>7)return false;
        for(int x=-2;x<=2;x++)for(int z=-2;z<=2;z++)for(int y=-1;y<=4;y++){
            var p=pos.offset(x,y,z);if(!level.hasChunkAt(p)||!level.getFluidState(p).isEmpty()||!level.getBlockState(p).getCollisionShape(level,p).isEmpty())return false;
        }return true;
    }
    /** Deep connected water only: river caves and mountain pools, never a lone puddle. */
    static boolean serpentHabitat(ServerLevel level,BlockPos pos){
        var type=BlueprintEntities.BISHUI_XUANJIAO_YOUZI.get();
        var habitat=TagKey.create(Registries.BIOME,new ResourceLocation("dynasty","blueprint/serpent_habitat"));
        if(level.dimension()!=Level.OVERWORLD||level.getDifficulty()==net.minecraft.world.Difficulty.PEACEFUL
                ||!level.hasChunkAt(pos)||pos.getY()<level.getMinBuildHeight()+2||pos.getY()>220
                ||!level.getBiome(pos).is(habitat)||level.canSeeSky(pos)&&pos.getY()<90
                ||!level.getFluidState(pos).is(net.minecraft.tags.FluidTags.WATER)
                ||!level.getFluidState(pos.below()).is(net.minecraft.tags.FluidTags.WATER)
                ||!level.noCollision(null,type.getDimensions().makeBoundingBox(pos.getX()+.5,pos.getY(),pos.getZ()+.5))
                ||level.getEntitiesOfClass(TemplateMob.class,new AABB(pos).inflate(32),e->e.isAlive()&&e.getType()==type).size()>=2)return false;
        var seen=new java.util.HashSet<BlockPos>();var queue=new java.util.ArrayDeque<BlockPos>();queue.add(pos);seen.add(pos);
        int water=0;
        while(!queue.isEmpty()&&seen.size()<=128){
            var p=queue.remove();
            if(!level.hasChunkAt(p)||!level.getFluidState(p).is(net.minecraft.tags.FluidTags.WATER))continue;
            if(++water>=24)return true;
            for(var direction:net.minecraft.core.Direction.values()){
                var next=p.relative(direction);
                if(Math.abs(next.getX()-pos.getX())<=3&&Math.abs(next.getZ()-pos.getZ())<=3&&Math.abs(next.getY()-pos.getY())<=2&&seen.add(next))queue.add(next);
            }
        }
        return false;
    }
    static boolean scorpionHabitat(ServerLevel level,BlockPos pos){
        var habitat=TagKey.create(Registries.BIOME,new ResourceLocation("dynasty","blueprint/scorpion_habitat"));
        var type=BlueprintEntities.MINGSHA_SHIXIE.get();
        return level.dimension()==Level.OVERWORLD&&level.getDifficulty()!=net.minecraft.world.Difficulty.PEACEFUL
            &&pos.getY()>=50&&pos.getY()<=200&&level.hasChunkAt(pos)&&level.getBiome(pos).is(habitat)
            &&pos.getY()>=level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,pos.getX(),pos.getZ())-4
            &&!level.isRainingAt(pos)&&level.getFluidState(pos).isEmpty()&&level.getBlockState(pos.below()).is(net.minecraft.tags.BlockTags.SAND)
            &&com.dynasty.entity.DynastySpawnPlacement.hasStandingSpace(level,pos,type.getDimensions().makeBoundingBox(pos.getX()+.5,pos.getY(),pos.getZ()+.5))
            &&level.getEntitiesOfClass(TemplateMob.class,new AABB(pos).inflate(32),e->e.isAlive()&&e.getType()==type).size()<3;
    }
    /** At most245 loaded block reads per spawn attempt; no periodic terrain scan. */
    static boolean treeHabitat(ServerLevel level,BlockPos pos){
        var habitat=TagKey.create(Registries.BIOME,new ResourceLocation("dynasty","blueprint/tree_habitat"));
        var type=BlueprintEntities.KUMU_SHUJING.get();
        if(level.dimension()!=Level.OVERWORLD||level.getDifficulty()==net.minecraft.world.Difficulty.PEACEFUL
                ||pos.getY()<level.getMinBuildHeight()+1||pos.getY()>220||!level.hasChunkAt(pos)
                ||!level.getBiome(pos).is(habitat)||level.getMaxLocalRawBrightness(pos)>12
                ||!level.getBlockState(pos.below()).is(net.minecraft.tags.BlockTags.DIRT)
                ||!level.getFluidState(pos).isEmpty()
                ||!com.dynasty.entity.DynastySpawnPlacement.hasStandingSpace(level,pos,type.getDimensions().makeBoundingBox(pos.getX()+.5,pos.getY(),pos.getZ()+.5))
                ||level.getEntitiesOfClass(TemplateMob.class,new AABB(pos).inflate(32),e->e.isAlive()&&e.getType()==type).size()>=2)return false;
        int logs=0;
        for(int x=-3;x<=3;x++)for(int z=-3;z<=3;z++)for(int y=0;y<5;y++){
            var p=pos.offset(x,y,z);
            if(level.hasChunkAt(p)&&level.getBlockState(p).is(net.minecraft.tags.BlockTags.LOGS)&&++logs>=3)return true;
        }
        return false;
    }
    /** Spawn-attempt-only bounded water connectivity check; never scans from a mob tick. */
    static boolean toadHabitat(ServerLevel level,BlockPos pos){
        var habitat=TagKey.create(Registries.BIOME,new ResourceLocation("dynasty","blueprint/toad_habitat"));
        if(level.dimension()!=Level.OVERWORLD||level.getDifficulty()==net.minecraft.world.Difficulty.PEACEFUL
                ||pos.getY()<level.getMinBuildHeight()+1||pos.getY()>100||!level.hasChunkAt(pos)||!level.getBiome(pos).is(habitat)
                ||level.getMaxLocalRawBrightness(pos)>12||level.isDay()&&!level.isRainingAt(pos)&&level.canSeeSky(pos))return false;
        var type=BlueprintEntities.CHIMU_ZHUHA.get();var box=type.getDimensions().makeBoundingBox(pos.getX()+.5,pos.getY(),pos.getZ()+.5);
        if(!level.noCollision(null,box)||level.getEntitiesOfClass(TemplateMob.class,new AABB(pos).inflate(32),e->e.isAlive()&&e.getType()==type).size()>=2)return false;
        if(!level.getFluidState(pos).is(net.minecraft.tags.FluidTags.WATER)
                &&!com.dynasty.entity.DynastySpawnPlacement.hasStandingSpace(level,pos,box))return false;
        var wet=new java.util.HashSet<BlockPos>();
        for(int x=-3;x<=3;x++)for(int z=-3;z<=3;z++)for(int y=-1;y<=1;y++){
            var p=pos.offset(x,y,z);if(level.hasChunkAt(p)&&level.getFluidState(p).is(net.minecraft.tags.FluidTags.WATER))wet.add(p);
        }
        while(!wet.isEmpty()){
            var queue=new java.util.ArrayDeque<BlockPos>();var first=wet.iterator().next();wet.remove(first);queue.add(first);
            int water=0;var columns=new java.util.HashSet<Long>();
            while(!queue.isEmpty()){
                var p=queue.remove();water++;columns.add(BlockPos.asLong(p.getX(),0,p.getZ()));
                if(water>=12&&columns.size()>=9)return true;
                for(var direction:net.minecraft.core.Direction.values()){var next=p.relative(direction);if(wet.remove(next))queue.add(next);}
            }
        }
        return false;
    }
    @SubscribeEvent public static void tick(TickEvent.LevelTickEvent event) {
        if(event.phase!=TickEvent.Phase.END || !(event.level instanceof ServerLevel level) || level.dimension()!=Level.OVERWORLD
                || level.getGameTime()%100!=0 || level.getDifficulty()==net.minecraft.world.Difficulty.PEACEFUL
                || !level.getGameRules().getBoolean(GameRules.RULE_DOMOBSPAWNING))return;
        var registry=level.registryAccess().registryOrThrow(Registries.STRUCTURE);
        var checked=new java.util.HashSet<String>();
        int remaining=2; // Absolute per-level work cap, independent of player count.
        for(var player:level.players()) {
            if(player.isSpectator())continue;
            for(var group:List.of(MILITARY,RITUAL,BATTLEFIELD,TOMBS,GUARDS,GHOSTS,CORPSES,CHILDREN,PAPERS,SKULLS,STONE_GUARDS,BIXI,PALANQUINS,DOGS,BRONZE_SNAKES,SPIDERS)) for(var holder:registry.getTagOrEmpty(group)) {
                if(remaining<=0)return;
                if(group==BATTLEFIELD&&level.isDay())continue;
                var start=level.structureManager().getStructureAt(player.blockPosition(),holder.value());
                if(!start.isValid())continue;
                var box=start.getBoundingBox();var centre=box.getCenter();
                String key=registry.getKey(holder.value())+"@"+start.getChunkPos().toLong();
                if(group==GHOSTS)key+=":ghosts";
                if(group==PALANQUINS){
                    if(!checked.add(key+":palanquin")||!palanquinHour(level))continue;
                    for(var piece:start.getPieces())if(piece instanceof com.dynasty.structure.TombAccessPiece access
                        &&spawnPalanquin(level,key+":palanquin",access.palanquinPosition(),player.blockPosition())){remaining--;break;}
                    continue;
                }
                if(group==BIXI){
                    if(!checked.add(key+":bixi"))continue;
                    for(var piece:start.getPieces())if(piece instanceof com.dynasty.structure.TombPiece tomb
                        &&spawnBixi(level,key+":bixi",tomb.bixiPosition(),player.blockPosition())){remaining--;break;}
                    continue;
                }
                if(group==SKULLS){
                    if(!checked.add(key+":flying_skulls"))continue;
                    for(var piece:start.getPieces())if(piece instanceof com.dynasty.structure.TombPiece tomb
                            &&spawnFlyingSkull(level,key+":flying_skulls",tomb.flyingSkullPositions(),player.blockPosition())){remaining--;break;}
                    continue;
                }
                if(group==PAPERS){
                    if(!checked.add(key+":paper_swordsmen"))continue;
                    for(var piece:start.getPieces())if(piece instanceof com.dynasty.structure.TombPiece tomb
                            &&spawnPaperSwordsman(level,key+":paper_swordsmen",tomb.paperSwordsmanPositions(),player.blockPosition())){remaining--;break;}
                    continue;
                }
                if(group==CHILDREN){
                    if(!checked.add(key+":shroud_child"))continue;
                    for(var piece:start.getPieces())if(piece instanceof com.dynasty.structure.TombPiece tomb
                            &&spawnShroudChild(level,key+":shroud_child",tomb.shroudChildPosition(),player.blockPosition())){remaining--;break;}
                    continue;
                }
                if(group==CORPSES){
                    if(!checked.add(key+":corpses"))continue;
                    for(var piece:start.getPieces())if(piece instanceof com.dynasty.structure.TombPiece tomb
                            &&spawnTombCorpse(level,key+":corpses",tomb.corpsePositions(),player.blockPosition())){remaining--;break;}
                    continue;
                }
                if(group==SPIDERS){
                    if(!checked.add(key+":mining_spiders"))continue;
                    for(var piece:start.getPieces())if(spawnMiningSpiders(level,key+":mining_spiders",com.dynasty.structure.megabuild.MechanicalPatrols.spiderPositions(piece),player.blockPosition())){remaining--;break;}
                    continue;
                }
                if(group==BRONZE_SNAKES){
                    if(!checked.add(key+":bronze_snakes"))continue;
                    for(var piece:start.getPieces())if(spawnBronzeSnakes(level,key+":bronze_snakes",com.dynasty.structure.megabuild.MechanicalPatrols.snakePositions(piece),player.blockPosition())){remaining--;break;}
                    continue;
                }
                if(group==DOGS){
                    if(!checked.add(key+":clockwork_dogs"))continue;
                    for(var piece:start.getPieces()){
                        var positions=com.dynasty.structure.megabuild.MechanicalPatrols.dogPositions(piece);
                        if(spawnClockworkDogs(level,key+":clockwork_dogs",positions,player.blockPosition())){remaining--;break;}
                    }continue;
                }
                if(group==STONE_GUARDS){
                    if(!checked.add(key+":stone_guard"))continue;
                    for(var piece:start.getPieces())if(piece instanceof com.dynasty.structure.WallGatePiece gate
                        &&spawnStoneGuard(level,key+":stone_guard",gate.stoneGuardPosition(),player.blockPosition())){remaining--;break;}
                    continue;
                }
                if(group==GUARDS){
                    if(!checked.add(key+":upper_guards"))continue;
                    for(var piece:start.getPieces())if(piece instanceof com.dynasty.structure.WallGatePiece gate
                            &&spawnGateGuard(level,key+":upper_guards",gate.upperGuardPositions(),player.blockPosition())){remaining--;break;}
                    continue;
                }
                if(group==TOMBS) {
                    if(!checked.contains(key)&&spawnChenshaMember(level,new BlockPos(box.minX(),box.minY(),box.minZ()),player.blockPosition())) {
                        checked.add(key);remaining--;
                    }
                    continue;
                }
                if(!checked.add(key))continue;
                var state=BlueprintSpawnState.get(level);var marker=state.markers.get(key);
                if(marker==null) {marker=new BlueprintSpawnState.Marker(key,centre);state.markers.put(key,marker);state.setDirty();}
                if(marker.cleared || marker.nextSpawn>level.getGameTime())continue;
                int wanted=group==GHOSTS?2+Math.floorMod(key.hashCode(),4):group==BATTLEFIELD?7:group==MILITARY?4:3;
                if(marker.produced>=wanted) {
                    if(!marker.members.isEmpty())continue;
                    marker.produced=0;state.setDirty();
                }
                if(group==GHOSTS&&level.getEntitiesOfClass(TemplateMob.class,new AABB(player.blockPosition()).inflate(32),
                    e->e.isAlive()&&e.kind()==TemplateMob.Kind.GHOST).size()>=5)continue;
                var type=group==GHOSTS?BlueprintEntities.YINBING_GUIZU.get():group==BATTLEFIELD?battlefieldMember(marker.produced):group==MILITARY?militaryMember(marker.produced):marker.produced==0?
                    BlueprintEntities.FUFA_JIJIU.get():BlueprintEntities.ZUWU_DAOSHOU.get();
                var id=net.minecraftforge.registries.ForgeRegistries.ENTITY_TYPES.getKey(type).getPath();
                var definition=TemplateContentDefinitions.ALL.stream().filter(d->d.id().equals(id)).findFirst().orElseThrow();
                // Only the already-loaded room around the entrant, never generate neighbouring chunks to spawn.
                BlockPos found=null;
                for(int n=0;n<32&&found==null;n++) {
                    int x=player.getBlockX()+level.random.nextInt(25)-12,z=player.getBlockZ()+level.random.nextInt(25)-12;
                    for(int dy=5;dy>=-6;dy--) {
                        var pos=new BlockPos(x,player.getBlockY()+dy,z);
                        if(!box.isInside(pos)||pos.getY()<definition.minY()||pos.getY()>definition.maxY()
                                ||!level.hasChunkAt(pos)||pos.distSqr(player.blockPosition())<36)continue;
                        if(com.dynasty.entity.DynastySpawnPlacement.hasStandingSpace(level,pos,type.getDimensions().makeBoundingBox(x+.5,pos.getY(),z+.5))) {found=pos;break;}
                    }
                }
                if(found==null)continue;
                // Weight affects attempts, never multiplies the authored squad or bypasses its cap/cooldown.
                int light=level.getMaxLocalRawBrightness(found);
                if(light<definition.minLight()||light>definition.maxLight()
                        ||group==BATTLEFIELD&&light>7
                        ||level.random.nextInt(TemplateContentDefinitions.maximumWeight(definition))
                            >=TemplateContentDefinitions.effectiveWeight(definition,!level.isDay(),light))continue;
                var mob=type.create(level);if(mob==null)continue;
                mob.moveTo(found.getX()+.5,found.getY(),found.getZ()+.5,0,0);mob.setPersistenceRequired();mob.bindEncounter(key);
                mob.finalizeSpawn(level,level.getCurrentDifficultyAt(found),MobSpawnType.STRUCTURE,null,null);
                if(level.addFreshEntity(mob)) {marker.members.add(mob.getUUID());marker.produced++;state.setDirty();remaining--;}
            }
        }
    }
    /** Authored upper-gate positions reuse the existing encounter ledger and death/unload lifecycle. */
    public static boolean spawnGateGuard(ServerLevel level,String key,List<BlockPos> positions,BlockPos entrant){
        return spawnAuthoredGroup(level,key,positions,entrant,BlueprintEntities.PIJIA_PANJIANG_HUWEI.get(),-32,300);
    }
    public static boolean spawnTombCorpse(ServerLevel level,String key,List<BlockPos> positions,BlockPos entrant){
        return spawnAuthoredGroup(level,key,positions,entrant,BlueprintEntities.SHIBIAN_LISHI.get(),level.getMinBuildHeight()+1,48);
    }
    public static boolean spawnShroudChild(ServerLevel level,String key,BlockPos pos,BlockPos entrant){
        if(!level.hasChunkAt(pos)||level.isDay()&&level.getMaxLocalRawBrightness(pos)>7)return false;
        return spawnAuthoredGroup(level,key,List.of(pos),entrant,BlueprintEntities.FUHUN_BAIBU_TONGZI.get(),level.getMinBuildHeight()+1,64);
    }
    public static boolean spawnPaperSwordsman(ServerLevel level,String key,List<BlockPos> positions,BlockPos entrant){
        return spawnAuthoredGroup(level,key,positions,entrant,BlueprintEntities.ZHIREN_JIANKE.get(),level.getMinBuildHeight()+1,64);
    }
    public static boolean spawnFlyingSkull(ServerLevel level,String key,List<BlockPos> positions,BlockPos entrant){
        return spawnAuthoredGroup(level,key,positions,entrant,BlueprintEntities.MUXUE_FEILU.get(),level.getMinBuildHeight()+1,64);
    }
    static boolean palanquinHour(ServerLevel level){long t=Math.floorMod(level.getDayTime(),24000);return t>=17000&&t<=19000;}
    public static boolean spawnPalanquin(ServerLevel level,String key,BlockPos pos,BlockPos entrant){
        return palanquinHour(level)&&spawnAuthoredGroup(level,key,List.of(pos),entrant,BlueprintEntities.YINYANG_ZHIJIAO_YOUHUN.get(),level.getMinBuildHeight()+1,300);
    }
    public static boolean spawnBixi(ServerLevel level,String key,BlockPos pos,BlockPos entrant){
        return spawnAuthoredGroup(level,key,List.of(pos),entrant,BlueprintEntities.JULI_BIXI_KUILEI.get(),level.getMinBuildHeight()+1,300);
    }
    public static boolean spawnStoneGuard(ServerLevel level,String key,BlockPos pos,BlockPos entrant){
        return spawnAuthoredGroup(level,key,List.of(pos),entrant,BlueprintEntities.JUBI_SHIGANDANG.get(),level.getMinBuildHeight()+1,300);
    }
    public static boolean spawnClockworkDogs(ServerLevel level,String key,List<BlockPos> positions,BlockPos entrant){
        return spawnAuthoredGroup(level,key,positions,entrant,BlueprintEntities.XUNSHAN_MUJIAQUAN.get(),level.getMinBuildHeight()+1,300);
    }
    public static boolean spawnBronzeSnakes(ServerLevel level,String key,List<BlockPos> positions,BlockPos entrant){
        return spawnAuthoredGroup(level,key,positions,entrant,BlueprintEntities.QINGTONG_SHUANGTOUSHEKUI.get(),level.getMinBuildHeight()+1,300);
    }
    public static boolean spawnMiningSpiders(ServerLevel level,String key,List<BlockPos> positions,BlockPos entrant){
        return spawnAuthoredGroup(level,key,positions,entrant,BlueprintEntities.BAZU_DIGONGZHU.get(),level.getMinBuildHeight()+1,300);
    }
    private static boolean spawnAuthoredGroup(ServerLevel level,String key,List<BlockPos> positions,BlockPos entrant,
            net.minecraft.world.entity.EntityType<TemplateMob> type,int minY,int maxY){
        if(positions.isEmpty()||positions.size()>3||level.dimension()!=Level.OVERWORLD||level.getDifficulty()==net.minecraft.world.Difficulty.PEACEFUL
                ||!level.getGameRules().getBoolean(GameRules.RULE_DOMOBSPAWNING))return false;
        var state=BlueprintSpawnState.get(level);var marker=state.markers.get(key);
        if(marker!=null&&(marker.cleared||marker.nextSpawn>level.getGameTime()||marker.produced>=positions.size()&&!marker.members.isEmpty()))return false;
        int index=marker==null||marker.produced>=positions.size()?0:marker.produced;
        var pos=positions.get(index);
        if(pos.getY()<minY||pos.getY()>Math.min(maxY,level.getMaxBuildHeight()-3)||!level.hasChunkAt(pos)||pos.distSqr(entrant)<25||pos.distSqr(entrant)>32*32
                ||level.getEntitiesOfClass(TemplateMob.class,new AABB(pos).inflate(32),e->e.isAlive()&&e.getType()==type).size()>=positions.size()
                ||!authoredSpace(level,type,pos))return false;
        var mob=type.create(level);if(mob==null)return false;
        mob.moveTo(pos.getX()+.5,pos.getY()+(type==BlueprintEntities.BAZU_DIGONGZHU.get()?.6:0),pos.getZ()+.5,0,0);mob.setPersistenceRequired();mob.bindEncounter(key);
        mob.finalizeSpawn(level,level.getCurrentDifficultyAt(pos),MobSpawnType.STRUCTURE,null,null);
        if(!level.addFreshEntity(mob))return false;
        if(marker==null){marker=new BlueprintSpawnState.Marker(key,pos);state.markers.put(key,marker);}
        if(index==0)marker.produced=0;
        marker.members.add(mob.getUUID());marker.produced++;marker.nextSpawn=level.getGameTime()+100;state.setDirty();return true;
    }

    private static boolean authoredSpace(ServerLevel level,net.minecraft.world.entity.EntityType<TemplateMob> type,BlockPos pos){
        var box=type.getDimensions().makeBoundingBox(pos.getX()+.5,pos.getY(),pos.getZ()+.5);
        if(type==BlueprintEntities.BAZU_DIGONGZHU.get())return level.noCollision(null,box.move(0,.6,0))
            &&MiningSpiderBehavior.supported(level,new net.minecraft.world.phys.Vec3(pos.getX()+.5,pos.getY()+.6,pos.getZ()+.5),type.getHeight());
        if(type==BlueprintEntities.MUXUE_FEILU.get())return level.getMaxLocalRawBrightness(pos)<=7
            &&level.getFluidState(pos).isEmpty()&&level.noCollision(null,box);
        return com.dynasty.entity.DynastySpawnPlacement.hasStandingSpace(level,pos,box);
    }

    /** Authored upper-gallery garrison, using the existing encounter ledger and death/unload lifecycle. */
    public static boolean spawnChenshaMember(ServerLevel level,BlockPos origin,BlockPos entrant) {
        if(level.dimension()!=Level.OVERWORLD||level.getDifficulty()==net.minecraft.world.Difficulty.PEACEFUL
                ||!level.getGameRules().getBoolean(GameRules.RULE_DOMOBSPAWNING))return false;
        int x=entrant.getX()-origin.getX(),y=entrant.getY()-origin.getY(),z=entrant.getZ()-origin.getZ();
        if(x<5||x>58||y<49||y>56||z<34||z>87)return false;
        var core=origin.offset(27,48,37);
        if(!level.hasChunkAt(core)||!(level.getBlockEntity(core) instanceof com.dynasty.dungeon.DungeonMechanismBlockEntity be)
                ||!be.validBinding()||!be.roomId().equals("shendao"))return false;
        var state=BlueprintSpawnState.get(level);String key="chensha@"+be.instance()+":shendao";
        var marker=state.markers.computeIfAbsent(key,k->new BlueprintSpawnState.Marker(k,origin.offset(32,49,64)));
        if(marker.cleared)return false;
        if(marker.produced>=4) {
            if(marker.members.isEmpty()){marker.cleared=true;state.setDirty();}
            return false;
        }
        if(marker.nextSpawn>level.getGameTime()||marker.members.size()>=4)return false;
        var type=marker.produced%2==0?BlueprintEntities.ZUWU_DAOSHOU.get():BlueprintEntities.JUMA_CHANGQIANGBING.get();
        // Fixed authored floor positions: never select ordinary caves within the structure's bounding box.
        var offsets=List.of(new BlockPos(10,49,50),new BlockPos(52,49,50),new BlockPos(10,49,78),new BlockPos(52,49,78));
        var pos=origin.offset(offsets.get(marker.produced));
        if(!level.hasChunkAt(pos)||pos.distSqr(entrant)<36||pos.distSqr(entrant)>48*48
                ||!com.dynasty.entity.DynastySpawnPlacement.hasStandingSpace(level,pos,
                    type.getDimensions().makeBoundingBox(pos.getX()+.5,pos.getY(),pos.getZ()+.5)))return false;
        var mob=type.create(level);if(mob==null)return false;
        mob.moveTo(pos.getX()+.5,pos.getY()+(type==BlueprintEntities.BAZU_DIGONGZHU.get()?.6:0),pos.getZ()+.5,0,0);mob.setPersistenceRequired();mob.bindEncounter(key);
        mob.finalizeSpawn(level,level.getCurrentDifficultyAt(pos),MobSpawnType.STRUCTURE,null,null);
        if(!level.addFreshEntity(mob))return false;
        marker.members.add(mob.getUUID());marker.produced++;marker.nextSpawn=level.getGameTime()+100;state.setDirty();
        return true;
    }
    static net.minecraft.world.entity.EntityType<TemplateMob> militaryMember(int index){
        return switch(index){case 0->BlueprintEntities.LUDUN_JIASHI.get();case 1,2->BlueprintEntities.LIANNU_ZHENZU.get();default->BlueprintEntities.JUMA_CHANGQIANGBING.get();};
    }
    static net.minecraft.world.entity.EntityType<TemplateMob> battlefieldMember(int index){
        return switch(index){case 0->BlueprintEntities.ZHENWANG_ZHANGQIGUAN.get();case 1->BlueprintEntities.FUFA_JIJIU.get();
            case 2,3->BlueprintEntities.TIESUO_CHIHOU.get();case 4,5,6->BlueprintEntities.KUIJUN_SISHI.get();
            default->throw new IllegalArgumentException("Battlefield squad index: "+index);};
    }
    @SubscribeEvent public static void died(LivingDeathEvent event) {
        if(!(event.getEntity().level() instanceof ServerLevel level))return;
        if(event.getEntity() instanceof TemplateMob) releaseMember(level,event.getEntity().getUUID());
        // Existing encounter bosses clear nearby template markers without changing their own death/reward logic.
        if(event.getEntity() instanceof com.dynasty.DynastyBossCombat.BarHolder) {
            var data=BlueprintSpawnState.get(level);
            for(var m:data.markers.values()) if(m.centre.distSqr(event.getEntity().blockPosition())<64*64) {m.cleared=true;data.setDirty();}
        }
    }
    @SubscribeEvent public static void removed(EntityLeaveLevelEvent event) {
        if (!(event.getLevel() instanceof ServerLevel level) || !(event.getEntity() instanceof TemplateMob mob)) return;
        var reason = mob.getRemovalReason();
        // Peaceful/removal must release the encounter slot. Chunk unload and dimension transfers must not.
        if (reason == net.minecraft.world.entity.Entity.RemovalReason.DISCARDED
                || reason == net.minecraft.world.entity.Entity.RemovalReason.KILLED)
            releaseMember(level,mob.getUUID());
    }
    static void releaseMember(ServerLevel currentLevel, java.util.UUID member) {
        // These encounters are authored in Overworld only. A mob may cross a portal before dying;
        // the destination dimension must not orphan its UUID in the encounter owner's SavedData.
        var owner=currentLevel.getServer().overworld();
        BlueprintSpawnState.get(owner).memberDied(member,owner.getGameTime());
    }
}
