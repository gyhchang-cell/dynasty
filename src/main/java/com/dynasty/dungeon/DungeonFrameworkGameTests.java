package com.dynasty.dungeon;

import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.BaseEntityBlock;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.level.material.Fluids;
import net.minecraft.world.level.material.PushReaction;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;

import java.lang.reflect.Proxy;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/** Framework-only evidence. These tests do not certify any of the ten finished dungeons. */
@GameTestHolder("dynasty_cod2")
@PrefixGameTestTemplate(false)
public final class DungeonFrameworkGameTests {
    @GameTest(template="bow_ritual_test",batch="cod2_chensha")
    public static void oldSavedArrowClockUpgradesAfterRecoveryWithoutReplayingDamage(GameTestHelper h) {
        var old=new DungeonHazard(20,4,36);old.trigger(100);
        for(long t=102;t<=120;t+=2)old.tickActive(t);
        old.consumeContact();var saved=old.save();saved.remove("PulseTicks");
        var hazards=new CompoundTag();hazards.put("poison_arrow_a",saved);
        var roomTag=new CompoundTag();roomTag.put("Hazards",hazards);
        var room=new DungeonRoomController();room.load(roomTag);
        var clock=room.hazard("poison_arrow_a",false);
        h.assertTrue(clock.duration()==4&&!clock.consumeContact(),"Old active volley is not replayed or reset on upgrade");
        clock.tickActive(10000);
        for(long t=10002;t<=10040;t+=2)clock.tickActive(t);
        clock=room.hazard("poison_arrow_a",false);clock.trigger(10042);int shots=0;
        for(long t=10044;t<=10068;t+=2){clock.tickActive(t);if(clock.consumeContact())shots++;}
        h.assertTrue(shots==3,"Existing worlds adopt three-arrow volleys after the previous recovery");
        h.succeed();
    }

    @GameTest(template="bow_ritual_test",batch="cod2_garrison",timeoutTicks=1200)
    public static void tombGarrisonUsesExistingLedgerAndCannotRefillAfterUnload(GameTestHelper h) {
        var level=h.getLevel();var origin=h.absolutePos(new BlockPos(4096,80,4096));var id=UUID.randomUUID();
        var core=origin.offset(27,48,37);var entrant=origin.offset(32,49,64);
        var positions=java.util.List.of(origin.offset(10,49,50),origin.offset(10,49,78),
            origin.offset(52,49,50),origin.offset(52,49,78));
        boolean previous=level.getGameRules().getBoolean(net.minecraft.world.level.GameRules.RULE_DOMOBSPAWNING);
        var spawned=new java.util.ArrayList<net.minecraft.world.entity.Entity>();
        var forced=new java.util.HashSet<ChunkPos>();
        var state=com.dynasty.blueprint.BlueprintSpawnState.get(level);String key="chensha@"+id+":shendao";
        Runnable cleanup=()->{
            for(var entity:spawned)if(!entity.isRemoved())entity.discard();
            var ledger=state.markers.get(key);
            if(ledger!=null)for(var uuid:java.util.List.copyOf(ledger.members)){var entity=level.getEntity(uuid);if(entity!=null)entity.discard();}
            level.setBlockAndUpdate(core,Blocks.AIR.defaultBlockState());
            level.getGameRules().getRule(net.minecraft.world.level.GameRules.RULE_DOMOBSPAWNING).set(previous,level.getServer());
            for(var chunk:forced)level.setChunkForced(chunk.x,chunk.z,false);
        };
        for(var center:java.util.List.of(core,positions.get(0),positions.get(1),positions.get(2),positions.get(3)))
            for(int dx=-1;dx<=1;dx++)for(int dz=-1;dz<=1;dz++){
                var chunk=new ChunkPos(center.offset(dx*16,0,dz*16));
                if(!level.getForcedChunks().contains(chunk.toLong())){level.setChunkForced(chunk.x,chunk.z,true);forced.add(chunk);}
            }
        // Fixture-only tickets and a real visibility barrier; production never adds these tickets.
        // Pinned FTB/Curios QA still loads entity storage asynchronously; allow up to 60 seconds,
        // retaining both ENTITY_TICKING and entity-storage readiness assertions.
        h.startSequence().thenIdle(20).thenWaitUntil(()->{
            for(var chunk:forced){
                var loaded=level.getChunkSource().getChunkNow(chunk.x,chunk.z);
                h.assertTrue(loaded!=null&&loaded.getFullStatus().isOrAfter(net.minecraft.server.level.FullChunkStatus.ENTITY_TICKING),
                    "Garrison fixture waits for loaded entity sections");
                h.assertTrue(level.areEntitiesLoaded(chunk.toLong()),"Fixture entity storage finishes asynchronous loading before spawning: "+chunk+", status="+loaded.getFullStatus());
            }
        }).thenExecute(()->{
            try{
                level.getGameRules().getRule(net.minecraft.world.level.GameRules.RULE_DOMOBSPAWNING).set(true,level.getServer());
                level.setBlockAndUpdate(core,DungeonContent.CORE.get().defaultBlockState());
                ((DungeonMechanismBlockEntity)level.getBlockEntity(core)).configure(id,"shendao","core",core,-1,java.util.List.of());
                for(var p:positions)for(int dx=-1;dx<=1;dx++)for(int dz=-1;dz<=1;dz++){
                    level.setBlockAndUpdate(p.offset(dx,-1,dz),Blocks.STONE.defaultBlockState());
                    for(int dy=0;dy<=3;dy++)level.setBlockAndUpdate(p.offset(dx,dy,dz),Blocks.AIR.defaultBlockState());
                }
                h.assertTrue(!com.dynasty.blueprint.BlueprintSpawns.spawnChenshaMember(level,origin,origin.offset(32,25,64)),
                    "Lower caves cannot trigger the upper gallery garrison");
                java.util.function.Consumer<net.minecraftforge.event.entity.EntityJoinLevelEvent> hold=e->{
                    if(e.getLevel()==level&&e.getEntity() instanceof com.dynasty.blueprint.TemplateMob mob
                            &&positions.contains(mob.blockPosition()))mob.setNoAi(true);
                };
                net.minecraftforge.common.MinecraftForge.EVENT_BUS.addListener(hold);
                try{
                    for(int n=0;n<4;n++){
                        if(n>0)state.markers.get(key).nextSpawn=level.getGameTime();
                        h.assertTrue(com.dynasty.blueprint.BlueprintSpawns.spawnChenshaMember(level,origin,entrant),
                            "Authored garrison member "+n+" must actually spawn");
                        h.assertTrue(!com.dynasty.blueprint.BlueprintSpawns.spawnChenshaMember(level,origin,entrant),
                            "Nearby players cannot bypass the spawn interval");
                    }
                }finally{net.minecraftforge.common.MinecraftForge.EVENT_BUS.unregister(hold);}
            }catch(RuntimeException|Error failure){cleanup.run();throw failure;}
        }).thenWaitUntil(()->{
            var marker=state.markers.get(key);
            h.assertTrue(marker!=null&&marker.produced==4&&marker.members.size()==4,"Four UUIDs remain reserved");
            for(var uuid:marker.members){
                var entity=level.getEntity(uuid);
                h.assertTrue(entity!=null,"Wait for each real garrison entity to become visible");
                if(!spawned.contains(entity))spawned.add(entity);
            }
        }).thenExecute(()->{
            try{
                h.assertTrue(spawned.size()==4,"Four actual entities, not only a produced counter");
                var first=spawned.get(0);first.remove(net.minecraft.world.entity.Entity.RemovalReason.UNLOADED_TO_CHUNK);
                h.assertTrue(state.markers.get(key).members.contains(first.getUUID()),"Unloaded membership remains reserved");
                var restored=com.dynasty.blueprint.BlueprintSpawnState.load(state.save(new CompoundTag()));
                h.assertTrue(restored.markers.get(key).produced==4&&restored.markers.get(key).members.size()==4,"Restart preserves garrison cap and UUIDs");
                state.markers.get(key).nextSpawn=level.getGameTime();
                h.assertTrue(!com.dynasty.blueprint.BlueprintSpawns.spawnChenshaMember(level,origin,entrant),"Unloaded entity cannot cause a fifth spawn");
                state.memberDied(first.getUUID(),level.getGameTime());
                for(var entity:spawned)if(!entity.isRemoved())entity.discard();
                h.assertTrue(state.markers.get(key).members.isEmpty(),"Existing removal listener releases living members");
                h.assertTrue(!com.dynasty.blueprint.BlueprintSpawns.spawnChenshaMember(level,origin,entrant)&&state.markers.get(key).cleared,
                    "Authored defeated garrison is permanent, not an infinite farm");
                h.succeed();
            }finally{cleanup.run();}
        });
    }

    @GameTest(template="bow_ritual_test",batch="cod2_chensha")
    public static void worldgenAcceptsChunkAccessAndDoesNotReserveEveryWorldPosition(GameTestHelper h) {
        var level=h.getLevel();var generator=level.getChunkSource().getGenerator();
        var chunk=level.getChunk(h.absolutePos(new BlockPos(3,2,3)));
        var context=new net.minecraft.world.level.levelgen.structure.Structure.GenerationContext(level.registryAccess(),generator,
            generator.getBiomeSource(),level.getChunkSource().randomState(),level.getStructureManager(),level.getSeed(),chunk.getPos(),chunk,b->true);
        h.assertTrue(ChenshaStructure.generationLevel(context)==level,"Natural generation supplies ChunkAccess, not a ServerLevelAccessor");
        boolean possible=false;
        for(int x=20000;x<40000&&!possible;x+=512)for(int z=20000;z<24000&&!possible;z+=512)
            possible=ChenshaStructure.clearOfReservedSites(context,level,x,z);
        h.assertTrue(possible,"Other-dimension structures and theoretical mineshafts must not exclude the whole world");
        h.assertTrue(!ChenshaStructure.farFromSpawn(new BlockPos(2490,0,0),BlockPos.ZERO),"Nearest edge respects spawn exclusion");
        h.assertTrue(ChenshaStructure.farFromSpawn(new BlockPos(2500,0,0),BlockPos.ZERO),"Spawn exclusion has a finite boundary");
        h.succeed();
    }

    @GameTest(template="bow_ritual_test",batch="cod2_chensha")
    public static void dungeonCommandsSelectRequestedRoomAndTrap(GameTestHelper h) {
        var level=h.getLevel();var core=h.absolutePos(new BlockPos(3,2,3));var trap=core.east(3);var id=UUID.randomUUID();
        level.setBlockAndUpdate(core,DungeonContent.CORE.get().defaultBlockState());level.setBlockAndUpdate(trap,DungeonContent.TRAP.get().defaultBlockState());
        ((DungeonMechanismBlockEntity)level.getBlockEntity(core)).configure(id,"probe","core",core,-1,java.util.List.of());
        ((DungeonMechanismBlockEntity)level.getBlockEntity(trap)).configure(id,"shendao","poison_arrow_b",core,-1,java.util.List.of());
        var source=level.getServer().createCommandSourceStack().withLevel(level).withPosition(net.minecraft.world.phys.Vec3.atCenterOf(core)).withPermission(2);
        var commands=level.getServer().getCommands();var state=DungeonStateStore.get(level);
        commands.performPrefixedCommand(source,"dynasty dungeon trap test poison_arrow_b");
        h.assertTrue(state.room(id,"shendao").hazard("poison_arrow_b",false).phase()==DungeonMechanism.Phase.WARNING,"Named trap command must not silently select the nearer core");
        commands.performPrefixedCommand(source,"dynasty dungeon room complete shendao");
        h.assertTrue(state.room(id,"shendao").completed()&&!state.room(id,"probe").completed(),"Room command must match its requested ID");
        h.succeed();
    }

    @GameTest(template="bow_ritual_test",batch="cod2_chensha")
    public static void arrowVolleyDoesNotReplayShotsAfterReload(GameTestHelper h) {
        var clock=new DungeonHazard(20,6,36,2);clock.trigger(100);int shots=0;
        for(long t=102;t<=120;t+=2){clock.tickActive(t);if(clock.consumeContact())shots++;}
        h.assertTrue(shots==1,"First arrow launches only after the full warning");
        clock=DungeonHazard.restore(clock.save());clock.tickActive(10000);
        h.assertTrue(!clock.consumeContact(),"Reload cannot replay the first arrow");
        for(long t=10002;t<=10008;t+=2){clock.tickActive(t);if(clock.consumeContact())shots++;}
        h.assertTrue(shots==3&&clock.phase()==DungeonMechanism.Phase.RECOVERY,"Exactly three server contact frames per volley");
        h.succeed();
    }

    @GameTest(template="bow_ritual_test",batch="cod2_chensha",timeoutTicks=80)
    public static void trapArrowsActuallyHitPoisonAndExpire(GameTestHelper h) {
        for(int x=3;x<=10;x++)for(int z=6;z<=10;z++)for(int y=2;y<=6;y++)h.setBlock(x,y,z,y==2?net.minecraft.world.level.block.Blocks.STONE:net.minecraft.world.level.block.Blocks.AIR);
        var cow=h.spawn(net.minecraft.world.entity.EntityType.COW,new BlockPos(8,3,8));cow.setNoAi(true);cow.setNoGravity(true);
        h.startSequence().thenWaitUntil(()->h.assertTrue(h.getLevel().getEntity(cow.getUUID())==cow&&cow.tickCount>=2,"Real damage target visible and ticking before projectile launch"))
        .thenExecute(()->{
            var arrow=DungeonContent.TRAP_ARROW.get().create(h.getLevel());arrow.setPos(cow.getX()-3,cow.getY()+.6,cow.getZ());arrow.shoot(1,0,0,1.6F,0);h.getLevel().addFreshEntity(arrow);
            var survivor=DungeonContent.TRAP_ARROW.get().create(h.getLevel());survivor.setPos(cow.getX(),cow.getY()+10,cow.getZ());survivor.setNoGravity(true);h.getLevel().addFreshEntity(survivor);
            h.runAfterDelay(8,()->h.assertTrue(cow.hasEffect(net.minecraft.world.effect.MobEffects.POISON)&&cow.getHealth()<cow.getMaxHealth(),"Real poison arrow collision must hurt the target; arrow ticks="+arrow.tickCount+", target ticks="+cow.tickCount+", at="+arrow.position()));
            h.runAfterDelay(10,()->{
                var saved=survivor.saveWithoutId(new CompoundTag());var restored=DungeonContent.TRAP_ARROW.get().create(h.getLevel());restored.load(saved);
                h.assertTrue(restored.pickup==net.minecraft.world.entity.projectile.AbstractArrow.Pickup.DISALLOWED,"Reload cannot enable arrow farming");
                h.assertTrue(survivor.tickCount>=9&&restored.saveWithoutId(new CompoundTag()).getInt("DungeonRemainingTicks")<=31,"Actual native ticking remaining lifetime survives NBT");restored.discard();
            });
            h.runAfterDelay(45,()->{try{h.assertTrue(survivor.isRemoved(),"Unclaimed projectiles expire without a global scanner");h.succeed();}finally{arrow.discard();survivor.discard();cow.discard();}});
        });
    }

    @GameTest(template="bow_ritual_test",batch="cod2_chensha")
    public static void shortcutNeedsSteleAndIsSharedPersistently(GameTestHelper h) {
        var level=h.getLevel();var pos=h.absolutePos(new BlockPos(3,2,3));var lift=pos.east(3);var id=UUID.randomUUID();
        level.setBlockAndUpdate(pos,DungeonContent.SHORTCUT_STELE.get().defaultBlockState());
        level.setBlockAndUpdate(lift,DungeonContent.ELEVATOR.get().defaultBlockState());
        var stele=(DungeonMechanismBlockEntity)level.getBlockEntity(pos);var elevator=(DungeonMechanismBlockEntity)level.getBlockEntity(lift);
        stele.configure(id,"imperial_vault","return_lift",pos,-1,java.util.List.of());
        elevator.configure(id,"imperial_vault","return_lift",pos,-1,java.util.List.of());
        var first=h.makeMockSurvivalPlayer();first.setPos(lift.getX()+.5,lift.getY()+1,lift.getZ()+.5);
        var room=DungeonStateStore.get(level).room(id,"imperial_vault");
        elevator.interact(first);h.assertTrue(!room.shortcutOpen("return_lift"),"The lift cannot unlock itself");
        first.setPos(pos.getX()+.5,pos.getY()+1,pos.getZ()+.5);stele.interact(first);
        h.assertTrue(!room.shortcutOpen("return_lift"),"Bare-handed interaction cannot break the protected stele");
        first.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND,new net.minecraft.world.item.ItemStack(net.minecraft.world.item.Items.IRON_PICKAXE));
        stele.interact(first);stele.interact(first);
        var restored=DungeonStateStore.load(DungeonStateStore.get(level).save(new CompoundTag())).room(id,"imperial_vault");
        h.assertTrue(restored.shortcutOpen("return_lift")&&!restored.unlockShortcut("return_lift"),"Shortcut is instance-wide and survives a save/reload");
        elevator.syncVisual(restored);
        h.assertTrue(level.getBlockState(pos).getValue(DungeonMechanismBlock.OPEN)&&level.getBlockState(lift).getValue(DungeonMechanismBlock.ACTIVE),"Broken stele and shared lift synchronise their state");
        restored.reset();h.assertTrue(restored.shortcutOpen("return_lift"),"Room reset cannot erase the permanent route");h.succeed();
    }

    @GameTest(template="bow_ritual_test",batch="cod2_chensha")
    public static void floorWaitsForOccupantBeforeRestoringCollision(GameTestHelper h) {
        var level=h.getLevel();var pos=h.absolutePos(new BlockPos(3,2,3));
        level.setBlockAndUpdate(pos,DungeonContent.FLOOR.get().defaultBlockState().setValue(DungeonMechanismBlock.OPEN,true));
        var floor=(DungeonMechanismBlockEntity)level.getBlockEntity(pos);floor.configure(UUID.randomUUID(),"shendao","floor",pos,-1,java.util.List.of());
        var cow=h.spawn(net.minecraft.world.entity.EntityType.COW,new BlockPos(3,2,3));cow.setNoAi(true);
        var room=new DungeonRoomController();floor.syncVisual(room);
        h.assertTrue(level.getBlockState(pos).getValue(DungeonMechanismBlock.OPEN),"Restoring floor must not suffocate an occupant");
        cow.setPos(cow.getX()+4,cow.getY(),cow.getZ());floor.syncVisual(room);
        h.assertTrue(!level.getBlockState(pos).getValue(DungeonMechanismBlock.OPEN),"Floor restores as soon as the cell is clear");h.succeed();
    }

    @GameTest(template="bow_ritual_test",batch="cod2_chensha")
    public static void mercuryTimeoutReleasesEntranceWithoutUnlockingExit(GameTestHelper h) {
        var room=new DungeonRoomController();room.configureTargets(56,true);
        h.assertTrue(room.startTrial(100),"An occupied trial starts once");
        room.recordTarget(3);room.recordTarget(4);
        for(long t=102;t<=1300;t+=2)room.tickRoom(t,true);
        h.assertTrue(room.trialFailed()&&!room.trialRunning()&&!room.doorOpen(),"Timeout must not bypass the third eye");
        var level=h.getLevel();var entrance=h.absolutePos(new BlockPos(3,2,3));var exit=entrance.east(3);
        var id=UUID.randomUUID();
        for(var p:java.util.List.of(entrance,exit))level.setBlockAndUpdate(p,DungeonContent.DOOR.get().defaultBlockState());
        var entryBe=(DungeonMechanismBlockEntity)level.getBlockEntity(entrance);
        var exitBe=(DungeonMechanismBlockEntity)level.getBlockEntity(exit);
        entryBe.configure(id,"mercury","trial_entry",entrance,-1,java.util.List.of());
        exitBe.configure(id,"mercury","mercury_exit",entrance,-1,java.util.List.of());
        entryBe.syncVisual(room);exitBe.syncVisual(room);
        h.assertTrue(level.getBlockState(entrance).getValue(DungeonMechanismBlock.OPEN),"Failed players can retreat");
        h.assertTrue(!level.getBlockState(exit).getValue(DungeonMechanismBlock.OPEN),"Boss route remains sealed");
        var restored=new DungeonRoomController();restored.load(room.save());
        h.assertTrue(restored.trialFailed()&&!restored.doorOpen()&&!restored.startTrial(1500),"Restart cannot bypass retry/exit gates");
        h.assertTrue(restored.allowRetry()&&restored.startTrial(1500),"Leaving the room permits another attempt");
        h.assertTrue(restored.progress()==24,"Two players' eye progress survives retry");
        restored.recordTarget(5);
        for(long t=1502;t<=1512;t+=2)restored.tickRoom(t,true);
        exitBe.syncVisual(restored);
        h.assertTrue(level.getBlockState(exit).getValue(DungeonMechanismBlock.OPEN),"All eyes open the exit after its animation");
        h.succeed();
    }

    @GameTest(template="bow_ritual_test",batch="cod2_chensha")
    public static void allThreeChenshaStairRunsHaveSupportAndPlayerHeadroom(GameTestHelper h) {
        var origin=new BlockPos(-23,20,-31);var id=ChenshaStructure.instanceId(39,origin);var capture=new Capture(h.getLevel());
        for(int x=0;x<4;x++)for(int z=0;z<6;z++){
            var original=new ChenshaPiece(origin,x,z,id);var restored=new ChenshaPiece(null,original.createTag(null));
            h.assertTrue(restored.getBoundingBox().equals(original.getBoundingBox()),"Column extent survives piece NBT");
            var box=restored.getBoundingBox();
            for(int cx=box.minX()>>4;cx<=box.maxX()>>4;cx++)for(int cz=box.minZ()>>4;cz<=box.maxZ()>>4;cz++){
                var clip=new BoundingBox(cx*16,-64,cz*16,cx*16+15,320,cz*16+15);capture.clip=clip;
                restored.postProcess(capture.level,null,null,RandomSource.create(9),clip,new ChunkPos(cx,cz),origin);
            }
        }
        for(var marker:ChenshaPiece.markers()){
            var part=capture.entities.get(origin.offset(marker.offset()));
            h.assertTrue(part instanceof DungeonMechanismBlockEntity be&&id.equals(be.instance())&&marker.room().equals(be.roomId())&&be.validBinding(),"Invalid generated binding: "+marker.id());
            if(marker.block()==DungeonContent.CORE.get()){
                long count=ChenshaPiece.markers().stream().filter(m->m.room().equals(marker.room())).count();
                h.assertTrue(part.saveWithoutMetadata().getLongArray("Markers").length==count,"Room marker list was silently truncated: "+marker.room());
            }
        }
        for(int y=44;y<=48;y++)h.assertTrue(capture.postprocessed.contains(origin.offset(35,y,41)),
            "Every generated return ladder is queued for vanilla postprocessing inside its own chunk");
        var pearls=ChenshaVaultLayout.constellationOffsets();
        var stars=ChenshaPiece.vaultStars();
        h.assertTrue(stars.size()==28&&new java.util.HashSet<>(stars).size()==28,"All existing vault lights remain distinct");
        for(var star:stars)h.assertTrue(capture.blocks.get(origin.offset(star)).is(Blocks.SEA_LANTERN),"Existing vault lights survive alongside new constellation fixtures");
        h.assertTrue(pearls.size()==28&&new java.util.HashSet<>(pearls).size()==28,"Exactly 28 distinct constellation lamps");
        for(var pearl:pearls)h.assertTrue(capture.blocks.get(origin.offset(pearl)).is(Blocks.PEARLESCENT_FROGLIGHT),
            "Constellation fixtures survive negative-coordinate cross-chunk clipping: "+pearl);
        int last=0;
        for(int z=25;z>=17;z--) {
            int tier=ChenshaVaultLayout.daisHeight(32,z);
            h.assertTrue(tier==last+1,"All nine main-axis tiers are reachable by single-block jumps");
            h.assertTrue(capture.blocks.get(origin.offset(32,tier,z)).is(Blocks.QUARTZ_BLOCK),"Missing authored dais tier "+tier);
            for(int dy=1;dy<=3;dy++)h.assertTrue(capture.blocks.get(origin.offset(32,tier+dy,z)).isAir(),"Dais lacks player headroom");
            last=tier;
        }
        h.assertTrue(last==9,"Dais contains nine actual levels, not just decorative trim");
        for(int z=22;z<=27;z++)h.assertTrue(!capture.blocks.get(origin.offset(32,0,z)).is(DungeonContent.MERCURY_CHANNEL.get()),
            "Main route across the moat remains dry");
        for(int run=0;run<3;run++){
            int start=run==0?10:run==1?59:28,end=run==0?34:run==1?83:52;
            for(int z=start;z<=end;z++){
                int floor=run==0?82-z:run==1?107-z:z-28;
                for(int x=30;x<=34;x++){
                    h.assertTrue(capture.blocks.get(origin.offset(x,floor,z)).is(DungeonContent.MASONRY.get()),"Missing stair support: "+run+"/"+x+"/"+z);
                    for(int dy=1;dy<=3;dy++){
                        var state=capture.blocks.get(origin.offset(x,floor+dy,z));
                        h.assertTrue(state.isAir()||state.is(DungeonContent.DOOR.get()),"Blocked stair headroom: "+run+"/"+x+"/"+z+"/"+dy);
                    }
                }
            }
        }
        h.succeed();
    }

    @GameTest(template="bow_ritual_test",batch="cod2_chensha")
    public static void chenshaRoomHazardsPauseIndependentlyAcrossRestart(GameTestHelper h) {
        var room=new DungeonRoomController();room.configureTargets(0,false);
        var a=room.hazard("poison_arrow_a",false);var b=room.hazard("poison_arrow_b",false);
        a.trigger(100);b.trigger(110);
        for(long t=102;t<=120;t+=2)a.tickActive(t);
        for(long t=112;t<=120;t+=2)b.tickActive(t);
        h.assertTrue(a.consumeContact()&&!b.consumeContact(),"Independent emitters cannot share a contact frame");
        var restored=new DungeonRoomController();restored.load(room.save());
        var reloaded=restored.hazard("poison_arrow_b",false);reloaded.tickActive(10000);
        h.assertTrue(reloaded.phase()==DungeonMechanism.Phase.WARNING&&reloaded.ticks()==10&&!reloaded.consumeContact(),"Unloaded time does not fire the second trap");
        for(long t=10002;t<=10010;t+=2)reloaded.tickActive(t);
        h.assertTrue(reloaded.consumeContact()&&!reloaded.consumeContact(),"Resumed trap fires once");
        h.succeed();
    }

    @GameTest(template="bow_ritual_test",batch="cod2_framework")
    public static void targetsAreIdempotentAndProgressSurvivesReload(GameTestHelper h) {
        var room=new DungeonRoomController();
        h.assertTrue(!room.recordTarget(-1)&&!room.recordTarget(6),"Reject invalid target index");
        for(int i=0;i<5;i++) {
            h.assertTrue(room.recordTarget(i),"New target advances progress");
            h.assertTrue(!room.recordTarget(i),"Repeated hit cannot advance progress");
        }
        var copy=new DungeonRoomController();copy.load(room.save());
        h.assertTrue(copy.progress()==31&&!copy.completed(),"Partial progress retained");
        h.assertTrue(copy.recordTarget(5)&&copy.completed(),"Six distinct markers complete the room");
        h.assertTrue(!copy.recordTarget(5),"Completed eye is not counted again");h.succeed();
    }

    @GameTest(template="bow_ritual_test",batch="cod2_framework")
    public static void worldAndPlayerRewardsAreSeparateAndCannotReset(GameTestHelper h) {
        var room=new DungeonRoomController();var player=UUID.randomUUID();var other=UUID.randomUUID();
        h.assertTrue(!room.claimWorldReward()&&!room.claimPlayerReward(player),"Unsolved room cannot grant rewards");
        room.complete();
        h.assertTrue(room.claimWorldReward()&&room.claimPlayerReward(player),"First claims accepted");
        h.assertTrue(!room.claimWorldReward()&&!room.claimPlayerReward(player),"Repeat claims rejected");
        h.assertTrue(room.claimPlayerReward(other),"Another player has a distinct entitlement");
        room.unlockShortcut("lift");room.reset();room.complete();
        var copy=new DungeonRoomController();copy.load(room.save());
        h.assertTrue(!copy.claimWorldReward()&&!copy.claimPlayerReward(player)&&!copy.claimPlayerReward(other),"Reset/reload never erase unique claims");
        h.assertTrue(copy.shortcutOpen("lift"),"Permanent shortcut survives reset and reload");h.succeed();
    }

    @GameTest(template="bow_ritual_test",batch="cod2_framework")
    public static void roomInstancesAndDimensionsAreIsolated(GameTestHelper h) {
        var a=UUID.randomUUID();var b=UUID.randomUUID();var state=new DungeonStateStore();
        state.room(a,"first").recordTarget(2);
        h.assertTrue(state.room(a,"second").progress()==0&&state.room(b,"first").progress()==0,"No cross-room or cross-instance progress");
        var copy=DungeonStateStore.load(state.save(new CompoundTag()));
        h.assertTrue(copy.room(a,"first").progress()==4&&copy.room(b,"first").progress()==0,"SavedData preserves isolated keys");
        var nether=h.getLevel().getServer().getLevel(net.minecraft.world.level.Level.NETHER);
        h.assertTrue(nether!=null&&DungeonStateStore.get(nether)!=DungeonStateStore.get(h.getLevel()),"Each dimension has its own store");h.succeed();
    }

    @GameTest(template="bow_ritual_test",batch="cod2_framework")
    public static void warningContactAndRecoveryHaveOneDamageFrame(GameTestHelper h) {
        var room=new DungeonRoomController();room.trigger(100);room.trigger(105);
        room.tickActive(102);h.assertTrue(room.phaseTicks()==2,"Repeat trigger cannot restart warning");
        for(int time=104;time<120;time+=2)room.tickActive(time);
        h.assertTrue(room.phase()==DungeonMechanism.Phase.WARNING&&!room.consumeContact(),"No damage before warning ends");
        room.tickActive(120);
        h.assertTrue(room.phase()==DungeonMechanism.Phase.ACTIVE&&room.consumeContact()&&!room.consumeContact(),"Exactly one contact frame");
        room.tickActive(122);room.tickActive(124);
        h.assertTrue(room.phase()==DungeonMechanism.Phase.RECOVERY,"Collision-disabled phase ends predictably");
        for(int time=126;time<=160;time+=2)room.tickActive(time);
        h.assertTrue(room.phase()==DungeonMechanism.Phase.IDLE&&!room.consumeContact(),"Trap restores without another damage frame");h.succeed();
    }

    @GameTest(template="bow_ritual_test",batch="cod2_framework")
    public static void unloadedRoomCannotReplayMissedContact(GameTestHelper h) {
        var room=new DungeonRoomController();room.trigger(10);room.tickActive(12);
        var copy=new DungeonRoomController();copy.load(room.save());copy.tickActive(10000);
        h.assertTrue(copy.phase()==DungeonMechanism.Phase.WARNING&&copy.phaseTicks()==2&&!copy.consumeContact(),"Reload does not catch up damage");
        copy.pause(20000);copy.tickActive(20002);
        h.assertTrue(copy.phaseTicks()==4,"Active time resumes after pause");
        for(int time=20004;time<=20018;time+=2)copy.tickActive(time);
        h.assertTrue(copy.consumeContact(),"Resumed warning eventually fires once");
        var afterContact=new DungeonRoomController();afterContact.load(copy.save());
        h.assertTrue(!afterContact.consumeContact(),"NBT never replays a delivered contact");h.succeed();
    }

    @GameTest(template="bow_ritual_test",batch="cod2_framework")
    public static void mechanismBindingsRoundTripAndRejectOutOfRange(GameTestHelper h) {
        var p=h.absolutePos(new BlockPos(3,2,3));var id=UUID.randomUUID();
        var be=new DungeonMechanismBlockEntity(p,DungeonContent.CORE.get().defaultBlockState());
        be.configure(id,"probe","core",p,99,java.util.List.of(p,p.offset(300,0,0)));
        var tag=be.saveWithoutMetadata();
        h.assertTrue(tag.getInt("Symbol")==-1&&tag.getLongArray("Markers").length==1,"Invalid symbols and distant markers rejected");
        var copy=new DungeonMechanismBlockEntity(p,DungeonContent.CORE.get().defaultBlockState());copy.load(tag);
        h.assertTrue(copy.validBinding()&&id.equals(copy.instance())&&copy.roomId().equals("probe"),"Minimal BE binding survives NBT");
        copy.configure(id,"probe","core",p.offset(300,0,0),-1,java.util.List.of());
        h.assertTrue(!copy.validBinding(),"Core binding cannot force-load a distant room");h.succeed();
    }

    @GameTest(template="bow_ritual_test",batch="cod2_framework")
    public static void protectedMarkersAndOpenCollisionAreCorrect(GameTestHelper h) {
        var p=h.absolutePos(new BlockPos(3,2,3));
        for(var block:java.util.List.of(DungeonContent.CORE.get(),DungeonContent.DOOR.get(),DungeonContent.FLOOR.get(),DungeonContent.EYE.get())) {
            var state=block.defaultBlockState();
            h.assertTrue(state.getPistonPushReaction()==PushReaction.BLOCK&&state.getDestroySpeed(h.getLevel(),p)<0,"Critical marker cannot be mined or pushed");
        }
        var door=DungeonContent.DOOR.get().defaultBlockState();var floor=DungeonContent.FLOOR.get().defaultBlockState();
        h.assertTrue(!door.getCollisionShape(h.getLevel(),p).isEmpty()&&!floor.getCollisionShape(h.getLevel(),p).isEmpty(),"Closed markers retain collision");
        h.assertTrue(door.setValue(DungeonMechanismBlock.OPEN,true).getCollisionShape(h.getLevel(),p).isEmpty(),"Solved door removes collision");
        h.assertTrue(floor.setValue(DungeonMechanismBlock.OPEN,true).getCollisionShape(h.getLevel(),p).isEmpty(),"Active floor temporarily disables collision");h.succeed();
    }

    @GameTest(template="bow_ritual_test",batch="cod2_framework")
    public static void realBlockInteractionOpensBoundDoorAndReconcilesOnLoad(GameTestHelper h) {
        var level=h.getLevel();var seal=h.absolutePos(new BlockPos(3,2,3));var door=seal.east(3);var id=UUID.randomUUID();
        level.setBlockAndUpdate(seal,DungeonContent.SEAL.get().defaultBlockState());
        level.setBlockAndUpdate(door,DungeonContent.DOOR.get().defaultBlockState());
        var sealBe=(DungeonMechanismBlockEntity)level.getBlockEntity(seal);var doorBe=(DungeonMechanismBlockEntity)level.getBlockEntity(door);
        sealBe.configure(id,"probe","seal_0",seal,0,java.util.List.of());
        doorBe.configure(id,"probe","trial_door",seal,-1,java.util.List.of());
        var player=h.makeMockSurvivalPlayer();player.setPos(seal.getX()+.5,seal.getY()+1,seal.getZ()+.5);
        sealBe.interact(player);sealBe.interact(player);
        var state=DungeonStateStore.get(level).room(id,"probe");
        h.assertTrue(state.progress()==1&&level.getBlockState(seal).getValue(DungeonMechanismBlock.ACTIVE),"Right-click updates authoritative state once");
        for(int i=1;i<6;i++)state.recordTarget(i);DungeonStateStore.get(level).setDirty();
        var restored=new DungeonMechanismBlockEntity(door,level.getBlockState(door));restored.load(doorBe.saveWithoutMetadata());level.setBlockEntity(restored);
        DungeonMechanismBlockEntity.tick(level,door,level.getBlockState(door),restored);
        h.assertTrue(level.getBlockState(door).getValue(DungeonMechanismBlock.OPEN),"Re-entered marker reads saved room completion");
        state.reset();restored.syncVisual(state);
        h.assertTrue(!level.getBlockState(door).getValue(DungeonMechanismBlock.OPEN),"Admin reset closes the test door");h.succeed();
    }

    @GameTest(template="bow_ritual_test",batch="cod2_framework")
    public static void structureAndLootResolveFromRealResourceRegistry(GameTestHelper h) {
        var structure=h.getLevel().registryAccess().registryOrThrow(Registries.STRUCTURE)
            .get(new ResourceLocation("dynasty","dungeon_framework_probe"));
        h.assertTrue(structure instanceof DungeonProbeStructure,"Formal structure JSON resolves to production type");
        var loot=h.getLevel().getServer().getLootData().getLootTable(new ResourceLocation("dynasty","dungeons/probe_supplies"));
        h.assertTrue(loot!=net.minecraft.world.level.storage.loot.LootTable.EMPTY,"LootTable exists and parses");
        var registry=h.getLevel().registryAccess().registryOrThrow(Registries.STRUCTURE_SET);
        h.assertTrue(registry.stream().noneMatch(set->set.structures().stream().anyMatch(entry->entry.structure().value()==structure)),"Prototype cannot naturally generate");
        h.assertTrue(DungeonDefinition.PROBE.piecePool().size()==3,"Definition includes all test pieces");h.succeed();
    }

    @GameTest(template="bow_ritual_test",batch="cod2_framework")
    public static void debugCommandsStayScopedToDungeonBranch(GameTestHelper h) {
        var root=h.getLevel().getServer().getCommands().getDispatcher().getRoot().getChild("dynasty");
        var dungeon=root.getChild("dungeon");
        h.assertTrue(dungeon!=null,"Dungeon debug branch is registered");
        h.assertTrue(dungeon.getChild("room").getChild("reset").getChild("roomId").getCommand()!=null,"Room reset is executable");
        h.assertTrue(dungeon.getChild("room").getChild("complete").getChild("roomId").getCommand()!=null,"Room complete is executable");
        h.assertTrue(dungeon.getChild("mechanism").getChild("set").getChild("pos").getChild("state").getCommand()!=null,"Mechanism debug command is correctly nested");
        h.assertTrue(dungeon.getChild("trap").getChild("test").getChild("id").getCommand()!=null,"Trap debug command is correctly nested");h.succeed();
    }

    @GameTest(template="bow_ritual_test",batch="cod2_framework")
    public static void pieceRoundTripAndChunkClippingKeepAllMarkers(GameTestHelper h) {
        BlockPos origin=new BlockPos(-23,70,-31);var id=DungeonProbeStructure.instanceId(39,origin);
        var capture=new Capture(h.getLevel());
        for(int part=0;part<3;part++) {
            var original=new DungeonProbePiece(origin,part,id);var restored=new DungeonProbePiece(null,original.createTag(null));
            h.assertTrue(restored.getBoundingBox().equals(original.getBoundingBox()),"Piece extent unchanged after reload");
            var box=restored.getBoundingBox();
            for(int cx=box.minX()>>4;cx<=box.maxX()>>4;cx++)for(int cz=box.minZ()>>4;cz<=box.maxZ()>>4;cz++) {
                var clip=new BoundingBox(cx*16,-64,cz*16,cx*16+15,320,cz*16+15);
                capture.clip=clip;
                restored.postProcess(capture.level,null,null,RandomSource.create(9),clip,new ChunkPos(cx,cz),origin);
            }
        }
        for(var marker:DungeonProbePiece.markers()) {
            BlockPos p=origin.offset(marker.offset());
            h.assertTrue(capture.blocks.get(p).is(marker.block()),"Marker generated at intended world coordinate: "+marker.id());
            var be=(DungeonMechanismBlockEntity)capture.entities.get(p);
            h.assertTrue(be!=null&&be.validBinding()&&id.equals(be.instance()),"Marker has matching instance binding");
        }
        for(int z:new int[]{0,15,16,31,47})
            h.assertTrue(capture.blocks.get(origin.offset(6,1,z)).isAir(),"Connected center path is not walled off at z="+z);
        h.assertTrue(capture.blocks.get(origin.offset(6,1,32)).is(DungeonContent.DOOR.get()),"One bound gate intentionally closes treasury entrance");
        h.assertTrue(capture.blocks.get(origin.offset(6,1,42)).is(Blocks.CHEST),"Supply LootTable chest generated");
        h.assertTrue(capture.blocks.size()==13*7*48,"Every cell fits deterministic three-piece footprint");
        h.assertTrue(id.equals(DungeonProbeStructure.instanceId(39,origin))&&!id.equals(DungeonProbeStructure.instanceId(40,origin)),"Seed/origin identity stable and distinct");h.succeed();
    }

    @GameTest(template="bow_ritual_test",batch="cod2_framework",timeoutTicks=400)
    public static void formalStructurePlacementAndDiskStateWorkInServerWorld(GameTestHelper h) throws Exception {
        var level=h.getLevel();var generator=level.getChunkSource().getGenerator();
        var structure=level.registryAccess().registryOrThrow(Registries.STRUCTURE)
            .get(new ResourceLocation("dynasty","dungeon_framework_probe"));
        var chunk=new ChunkPos(12000>>4,12000>>4);
        var start=structure.generate(level.registryAccess(),generator,generator.getBiomeSource(),level.getChunkSource().randomState(),
            level.getStructureManager(),level.getSeed(),chunk,0,level,biome->true);
        h.assertTrue(start.isValid()&&start.getPieces().size()==3,"Formal generation produces three connected pieces");
        var box=start.getBoundingBox();BlockPos origin=new BlockPos(box.minX(),box.minY(),box.minZ());
        long began=System.nanoTime();
        for(int cx=box.minX()>>4;cx<=box.maxX()>>4;cx++)for(int cz=box.minZ()>>4;cz<=box.maxZ()>>4;cz++) {
            // Explicit disposable QA only, equivalent to the player loading three chunks.
            // The production structure never loads extra chunks or adds tickets.
            level.getChunk(cx,cz);
            var clip=new BoundingBox(cx*16,level.getMinBuildHeight(),cz*16,cx*16+15,level.getMaxBuildHeight()-1,cz*16+15);
            start.placeInChunk(level,level.structureManager(),generator,RandomSource.create(19),clip,new ChunkPos(cx,cz));
        }
        var id=DungeonProbeStructure.instanceId(level.getSeed(),origin);
        for(var marker:DungeonProbePiece.markers()) {
            var be=level.getBlockEntity(origin.offset(marker.offset()));
            h.assertTrue(be instanceof DungeonMechanismBlockEntity binding&&binding.validBinding()&&id.equals(binding.instance()),"Live-world marker has persistent binding: "+marker.id());
        }
        var state=DungeonStateStore.get(level);var room=state.room(id,"probe");
        room.recordTarget(2);room.unlockShortcut("lift");room.complete();h.assertTrue(room.claimWorldReward(),"World reward recorded once");state.setDirty();
        level.getDataStorage().save();
        var path=level.getServer().getWorldPath(net.minecraft.world.level.storage.LevelResource.ROOT).resolve("data/dynasty_dungeons_v1.dat");
        var disk=net.minecraft.nbt.NbtIo.readCompressed(path.toFile());var loaded=DungeonStateStore.load(disk.getCompound("data"));
        var saved=loaded.room(id,"probe");
        h.assertTrue(saved.completed()&&saved.progress()==4&&saved.shortcutOpen("lift")&&!saved.claimWorldReward(),"Actual .dat keeps progress/shortcut/claim ledger");
        System.out.println("COD2_PROBE_REAL_STRUCTURE_AND_DISK_PASS elapsedMs="+(System.nanoTime()-began)/1_000_000+" markers="+DungeonProbePiece.markers().size());h.succeed();
    }

    /** Observe real StructurePiece.placeBlock; fail immediately on out-of-chunk writes. */
    private static final class Capture {
        final Map<BlockPos,BlockState> blocks=new HashMap<>();
        final Map<BlockPos,BlockEntity> entities=new HashMap<>();
        BoundingBox clip;
        final java.util.Set<BlockPos> postprocessed=new java.util.HashSet<>();
        final Map<ChunkPos,net.minecraft.world.level.chunk.ProtoChunk> chunks=new HashMap<>();
        final WorldGenLevel level;
        Capture(net.minecraft.server.level.ServerLevel source){level=(WorldGenLevel)Proxy.newProxyInstance(WorldGenLevel.class.getClassLoader(),new Class<?>[]{WorldGenLevel.class},(proxy,method,args)->{
            switch(method.getName()) {
                case "setBlock": {
                    var pos=((BlockPos)args[0]).immutable();var state=(BlockState)args[1];
                    if(!clip.isInside(pos))throw new AssertionError("Cross-chunk write: "+pos);
                    blocks.put(pos,state);entities.remove(pos);
                    if(state.getBlock() instanceof BaseEntityBlock block)entities.put(pos,block.newBlockEntity(pos,state));
                    return true;
                }
                case "getChunk": {
                    var chunk=args[0] instanceof BlockPos p?new ChunkPos(p):new ChunkPos((int)args[0],(int)args[1]);
                    if(chunk.x!=(clip.minX()>>4)||chunk.z!=(clip.minZ()>>4))
                        throw new AssertionError("Cross-chunk postprocessing request: "+chunk);
                    return chunks.computeIfAbsent(chunk,c->new net.minecraft.world.level.chunk.ProtoChunk(c,
                        net.minecraft.world.level.chunk.UpgradeData.EMPTY,source,source.registryAccess().registryOrThrow(Registries.BIOME),null){
                            @Override public void markPosForPostprocessing(BlockPos pos){
                                if(!clip.isInside(pos))throw new AssertionError("Cross-chunk postprocessing: "+pos);
                                postprocessed.add(pos.immutable());super.markPosForPostprocessing(pos);
                            }
                        });
                }
                case "getBlockState":return blocks.getOrDefault(args[0],Blocks.AIR.defaultBlockState());
                case "getBlockEntity":return entities.get(args[0]);
                case "getFluidState":return Fluids.EMPTY.defaultFluidState();
                case "toString":return "DungeonChunkCapture";
                default:throw new AssertionError("Unexpected worldgen operation: "+method.getName());
            }
        });}
    }
}
