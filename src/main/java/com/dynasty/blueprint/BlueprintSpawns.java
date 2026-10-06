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
    private BlueprintSpawns() {}
    public static void register(SpawnPlacementRegisterEvent event) {
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
    @SubscribeEvent public static void tick(TickEvent.LevelTickEvent event) {
        if(event.phase!=TickEvent.Phase.END || !(event.level instanceof ServerLevel level) || level.dimension()!=Level.OVERWORLD
                || level.getGameTime()%100!=0 || level.getDifficulty()==net.minecraft.world.Difficulty.PEACEFUL
                || !level.getGameRules().getBoolean(GameRules.RULE_DOMOBSPAWNING))return;
        var registry=level.registryAccess().registryOrThrow(Registries.STRUCTURE);
        var checked=new java.util.HashSet<String>();
        int remaining=2; // Absolute per-level work cap, independent of player count.
        for(var player:level.players()) {
            if(player.isSpectator())continue;
            for(var group:List.of(MILITARY,RITUAL,BATTLEFIELD,TOMBS,GUARDS,GHOSTS,CORPSES,CHILDREN)) for(var holder:registry.getTagOrEmpty(group)) {
                if(remaining<=0)return;
                if(group==BATTLEFIELD&&level.isDay())continue;
                var start=level.structureManager().getStructureAt(player.blockPosition(),holder.value());
                if(!start.isValid())continue;
                var box=start.getBoundingBox();var centre=box.getCenter();
                String key=registry.getKey(holder.value())+"@"+start.getChunkPos().toLong();
                if(group==GHOSTS)key+=":ghosts";
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
                mob.moveTo(found.getX()+.5,found.getY(),found.getZ()+.5,0,0);mob.setPersistenceRequired();
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
    private static boolean spawnAuthoredGroup(ServerLevel level,String key,List<BlockPos> positions,BlockPos entrant,
            net.minecraft.world.entity.EntityType<TemplateMob> type,int minY,int maxY){
        if(positions.isEmpty()||positions.size()>2||level.dimension()!=Level.OVERWORLD||level.getDifficulty()==net.minecraft.world.Difficulty.PEACEFUL
                ||!level.getGameRules().getBoolean(GameRules.RULE_DOMOBSPAWNING))return false;
        var state=BlueprintSpawnState.get(level);var marker=state.markers.get(key);
        if(marker!=null&&(marker.cleared||marker.nextSpawn>level.getGameTime()||marker.produced>=positions.size()&&!marker.members.isEmpty()))return false;
        int index=marker==null||marker.produced>=positions.size()?0:marker.produced;
        var pos=positions.get(index);
        if(pos.getY()<minY||pos.getY()>Math.min(maxY,level.getMaxBuildHeight()-3)||!level.hasChunkAt(pos)||pos.distSqr(entrant)<25||pos.distSqr(entrant)>32*32
                ||level.getEntitiesOfClass(TemplateMob.class,new AABB(pos).inflate(32),e->e.isAlive()&&e.getType()==type).size()>=positions.size()
                ||!com.dynasty.entity.DynastySpawnPlacement.hasStandingSpace(level,pos,type.getDimensions().makeBoundingBox(pos.getX()+.5,pos.getY(),pos.getZ()+.5)))return false;
        var mob=type.create(level);if(mob==null)return false;
        mob.moveTo(pos.getX()+.5,pos.getY(),pos.getZ()+.5,0,0);mob.setPersistenceRequired();
        mob.finalizeSpawn(level,level.getCurrentDifficultyAt(pos),MobSpawnType.STRUCTURE,null,null);
        if(!level.addFreshEntity(mob))return false;
        if(marker==null){marker=new BlueprintSpawnState.Marker(key,pos);state.markers.put(key,marker);}
        if(index==0)marker.produced=0;
        marker.members.add(mob.getUUID());marker.produced++;marker.nextSpawn=level.getGameTime()+100;state.setDirty();return true;
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
        mob.moveTo(pos.getX()+.5,pos.getY(),pos.getZ()+.5,0,0);mob.setPersistenceRequired();
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
