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
            for(var group:List.of(MILITARY,RITUAL,BATTLEFIELD)) for(var holder:registry.getTagOrEmpty(group)) {
                if(remaining<=0)return;
                if(group==BATTLEFIELD&&level.isDay())continue;
                var start=level.structureManager().getStructureAt(player.blockPosition(),holder.value());
                if(!start.isValid())continue;
                var box=start.getBoundingBox();var centre=box.getCenter();
                String key=registry.getKey(holder.value())+"@"+start.getChunkPos().toLong();
                if(!checked.add(key))continue;
                var state=BlueprintSpawnState.get(level);var marker=state.markers.get(key);
                if(marker==null) {marker=new BlueprintSpawnState.Marker(key,centre);state.markers.put(key,marker);state.setDirty();}
                if(marker.cleared || marker.nextSpawn>level.getGameTime())continue;
                int wanted=group==BATTLEFIELD?7:group==MILITARY?4:3;
                if(marker.produced>=wanted) {
                    if(!marker.members.isEmpty())continue;
                    marker.produced=0;state.setDirty();
                }
                var type=group==BATTLEFIELD?battlefieldMember(marker.produced):group==MILITARY?militaryMember(marker.produced):marker.produced==0?
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
