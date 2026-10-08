package com.dynasty.dungeon;

import com.dynasty.blueprint.BlueprintEntities;
import com.dynasty.blueprint.BlueprintSpawnState;
import com.dynasty.blueprint.BlueprintSpawns;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.GameRules;
import net.minecraft.world.level.block.Blocks;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.UUID;

/** Actual spawn/ledger checks. Does not certify client visuals or a finished dungeon. */
@GameTestHolder("dynasty_cod2")
@PrefixGameTestTemplate(false)
public final class ChenshaEcologyGameTests {
    @GameTest(template="bow_ritual_test",batch="cod2_middle_layout")
    public static void flyingSkullsHaveAirborneAuthoredChambers(GameTestHelper h) {
        var points=ChenshaPiece.middleSkullOffsets();
        h.assertTrue(points.size()==2&&new HashSet<>(points).size()==2,"Two distinct chamber spawn points");
        for(var point:points) {
            for(int dy=0;dy<2;dy++)for(int dx=-1;dx<=1;dx++)for(int dz=-1;dz<=1;dz++)
                h.assertTrue(ChenshaPiece.cell(point.getX()+dx,point.getY()+dy,point.getZ()+dz).isAir(),
                    "Flying skull clearance is authored air, not ordinary underground rock");
            h.assertTrue(!ChenshaPiece.cell(point.getX(),33,point.getZ()).isAir(),"Vaulted roof shields daylight");
            h.assertTrue(point.getX()<24||point.getX()>39,"Skulls are outside the sealed mercury puzzle chamber");
        }
        h.succeed();
    }

    @GameTest(template="bow_ritual_test",batch="cod2_middle_layout")
    public static void restoredPitRetainsAClimbableReturnPath(GameTestHelper h) {
        for(int y=44;y<=48;y++) {
            var ladder=ChenshaPiece.cell(35,y,41);
            h.assertTrue(ladder.is(Blocks.LADDER)&&ladder.getValue(net.minecraft.world.level.block.LadderBlock.FACING)
                ==net.minecraft.core.Direction.WEST,"Pit return ladder faces its solid support");
            h.assertTrue(!ChenshaPiece.cell(36,y,41).isAir(),"Each ladder rung retains a support block");
        }
        for(int y=49;y<=51;y++)h.assertTrue(ChenshaPiece.cell(35,y,41).isAir(),"Return opens into upper gallery with headroom");
        h.assertTrue(ChenshaPiece.markers().stream().noneMatch(m->m.offset().getX()==35&&m.offset().getZ()==41),
            "No resettable marker replaces the permanent escape path");
        h.succeed();
    }

    @GameTest(template="bow_ritual_test",batch="cod2_artisan_cache")
    public static void artisanCacheSuppliesBlueprintOnceWithoutRefilling(GameTestHelper h) {
        var level=h.getLevel();var pos=h.absolutePos(new BlockPos(2,2,2));
        level.setBlockAndUpdate(pos,Blocks.CHEST.defaultBlockState());
        var chest=(net.minecraft.world.level.block.entity.ChestBlockEntity)level.getBlockEntity(pos);
        chest.setLootTable(new net.minecraft.resources.ResourceLocation("dynasty:dungeons/chensha_artisan_supplies"),41L);
        chest.unpackLootTable(null);int blueprints=0;
        for(int i=0;i<chest.getContainerSize();i++)if(chest.getItem(i).is(com.dynasty.DynastyRelics.BLUEPRINT.get()))
            blueprints+=chest.getItem(i).getCount();
        h.assertTrue(blueprints==1,"Hidden workshop supplies exactly one existing functional blueprint");
        chest.clearContent();var saved=chest.saveWithoutMetadata();
        h.assertTrue(!saved.contains("LootTable"),"Opening consumes vanilla loot seed/table rather than allowing reroll");
        chest.load(saved);chest.unpackLootTable(null);
        h.assertTrue(chest.isEmpty(),"Reloading emptied cache does not refill blueprint or supplies");
        h.succeed();
    }

    @GameTest(template="bow_ritual_test",batch="cod2_middle_ecology",timeoutTicks=140)
    public static void middleSkullsRespectBindingBudgetAndPersistentDefeat(GameTestHelper h) {
        var level=h.getLevel();var origin=h.absolutePos(new BlockPos(2048,80,2048));
        var core=origin.offset(ChenshaPiece.core("mercury"));
        var entrant=origin.offset(32,25,60);var instance=UUID.randomUUID();
        String key="chensha@"+instance+":mercury_skulls";
        var forced=new HashSet<ChunkPos>();var entities=new ArrayList<Entity>();
        boolean spawning=level.getGameRules().getBoolean(GameRules.RULE_DOMOBSPAWNING);
        var state=BlueprintSpawnState.get(level);
        Runnable cleanup=()->{
            for(var entity:entities)if(!entity.isRemoved())entity.discard();
            var ledger=state.markers.get(key);if(ledger!=null)for(var uuid:List.copyOf(ledger.members)){var entity=level.getEntity(uuid);if(entity!=null)entity.discard();}
            level.getGameRules().getRule(GameRules.RULE_DOMOBSPAWNING).set(spawning,level.getServer());
            for(var chunk:forced)level.setChunkForced(chunk.x,chunk.z,false);
        };
        var positions=ChenshaPiece.middleSkullOffsets().stream().map(origin::offset).toList();
        for(var center:List.of(core,positions.get(0),positions.get(1)))for(int dx=-1;dx<=1;dx++)for(int dz=-1;dz<=1;dz++) {
            var chunk=new ChunkPos(center.offset(dx*16,0,dz*16));
            if(!level.getForcedChunks().contains(chunk.toLong())){level.setChunkForced(chunk.x,chunk.z,true);forced.add(chunk);}
        }
        h.startSequence().thenIdle(20).thenWaitUntil(()->{
            for(var chunk:forced){
                var loaded=level.getChunkSource().getChunkNow(chunk.x,chunk.z);
                h.assertTrue(loaded!=null&&loaded.getFullStatus().isOrAfter(net.minecraft.server.level.FullChunkStatus.ENTITY_TICKING),"Skull fixture waits for loaded entity sections");
            }
        }).thenExecute(()->{
            // Light-isolated fixture; tickets and terrain edits are test-only.
            for(var p:positions)for(int x=-3;x<=3;x++)for(int y=-3;y<=4;y++)for(int z=-3;z<=3;z++)
                level.setBlockAndUpdate(p.offset(x,y,z),(Math.abs(x)==3||Math.abs(z)==3||y==-3||y==4)?
                    Blocks.STONE.defaultBlockState():Blocks.AIR.defaultBlockState());
            level.setBlockAndUpdate(core,DungeonContent.CORE.get().defaultBlockState());
            ((DungeonMechanismBlockEntity)level.getBlockEntity(core)).configure(instance,"mercury","mercury_core",core,-1,List.of());
        }).thenIdle(30).thenExecute(()->{
            try {
                level.getGameRules().getRule(GameRules.RULE_DOMOBSPAWNING).set(true,level.getServer());
                h.assertTrue(!BlueprintSpawns.spawnChenshaMiddleMember(level,origin,origin.offset(32,49,60)),"Upper floor cannot activate middle ecology");
                h.assertTrue(!BlueprintSpawns.spawnChenshaMiddleMember(level,origin,origin.offset(32,1,20)),"Boss vault cannot activate middle ecology");
                h.assertTrue(!BlueprintSpawns.spawnChenshaMiddleMember(level,origin,origin.offset(2,25,60)),"Outside corridor cannot activate encounter");
                level.getGameRules().getRule(GameRules.RULE_DOMOBSPAWNING).set(false,level.getServer());
                h.assertTrue(!BlueprintSpawns.spawnChenshaMiddleMember(level,origin,entrant),"doMobSpawning=false is respected");
                level.getGameRules().getRule(GameRules.RULE_DOMOBSPAWNING).set(true,level.getServer());
                var be=(DungeonMechanismBlockEntity)level.getBlockEntity(core);
                h.assertTrue(be!=null,"Remote fixture core remains loaded before binding checks");
                be.configure(instance,"shendao","wrong_room",core,-1,List.of());
                h.assertTrue(!BlueprintSpawns.spawnChenshaMiddleMember(level,origin,entrant),"Wrong room core cannot fabricate an encounter");
                be.configure(instance,"mercury","mercury_core",core,-1,List.of());
                var first=positions.get(0);
                level.setBlockAndUpdate(first,Blocks.STONE.defaultBlockState());
                h.assertTrue(!BlueprintSpawns.spawnChenshaMiddleMember(level,origin,entrant),"Occupied airborne volume rejects spawn");
                h.assertTrue(!state.markers.containsKey(key),"Rejected attempt does not consume or allocate encounter state");
                level.setBlockAndUpdate(first,Blocks.AIR.defaultBlockState());
                java.util.function.Consumer<net.minecraftforge.event.entity.EntityJoinLevelEvent> hold=e->{
                    if(e.getLevel()==level&&e.getEntity().getType()==BlueprintEntities.MUXUE_FEILU.get()
                            &&positions.stream().anyMatch(p->p.equals(e.getEntity().blockPosition())))e.getEntity().setNoGravity(true);
                    if(e.getLevel()==level&&e.getEntity() instanceof com.dynasty.blueprint.TemplateMob mob
                            &&positions.contains(mob.blockPosition()))mob.setNoAi(true);
                };
                net.minecraftforge.common.MinecraftForge.EVENT_BUS.addListener(hold);
                try{
                    for(int i=0;i<2;i++) {
                        if(i>0)state.markers.get(key).nextSpawn=level.getGameTime();
                        h.assertTrue(BlueprintSpawns.spawnChenshaMiddleMember(level,origin,entrant),"Actual middle skull "+i+" spawns");
                        h.assertTrue(!BlueprintSpawns.spawnChenshaMiddleMember(level,origin,entrant.offset(1,0,0)),"Second entrant cannot bypass cooldown or cap");
                    }
                }finally{net.minecraftforge.common.MinecraftForge.EVENT_BUS.unregister(hold);}
            }catch(RuntimeException|Error e){cleanup.run();throw e;}
        }).thenWaitUntil(()->{
            h.assertTrue(state.markers.get(key).members.size()==2,"Exactly two UUIDs must remain reserved");
            for(var uuid:state.markers.get(key).members){var entity=level.getEntity(uuid);h.assertTrue(entity!=null,"Wait for each asynchronous loaded entity section");if(!entities.contains(entity))entities.add(entity);}
        }).thenExecute(()->{
            try{
                h.assertTrue(entities.size()==2&&entities.stream().allMatch(e->e.getType()==BlueprintEntities.MUXUE_FEILU.get()),"Both actors reuse cod1 flying skull entity");
                var skull=entities.get(0);skull.remove(Entity.RemovalReason.UNLOADED_TO_CHUNK);
                h.assertTrue(state.markers.get(key).members.contains(skull.getUUID()),"Chunk unload reserves UUID");
                var restored=BlueprintSpawnState.load(state.save(new CompoundTag()));
                h.assertTrue(restored.markers.get(key).members.equals(state.markers.get(key).members)
                    &&restored.markers.get(key).produced==2,"SavedData round trip preserves exact members and production cap");
                state.markers.get(key).nextSpawn=level.getGameTime();
                h.assertTrue(!BlueprintSpawns.spawnChenshaMiddleMember(level,origin,entrant),"Unloaded members do not spawn replacements");
                state.memberDied(skull.getUUID(),level.getGameTime());
                for(var entity:entities)if(!entity.isRemoved())entity.discard();
                h.assertTrue(state.markers.get(key).members.isEmpty(),"Shared removal lifecycle releases membership");
                h.assertTrue(!BlueprintSpawns.spawnChenshaMiddleMember(level,origin,entrant)&&state.markers.get(key).cleared,"Cleared gallery never refills");
                restored=BlueprintSpawnState.load(state.save(new CompoundTag()));
                h.assertTrue(restored.markers.get(key).cleared,"Permanent defeat survives serialization");
                h.succeed();
            } finally {
                cleanup.run();
            }
        });
    }
}
