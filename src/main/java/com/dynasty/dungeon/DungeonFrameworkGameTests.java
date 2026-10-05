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
        var capture=new Capture();
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
        final WorldGenLevel level=(WorldGenLevel)Proxy.newProxyInstance(WorldGenLevel.class.getClassLoader(),new Class<?>[]{WorldGenLevel.class},(proxy,method,args)->{
            switch(method.getName()) {
                case "setBlock": {
                    var pos=((BlockPos)args[0]).immutable();var state=(BlockState)args[1];
                    if(!clip.isInside(pos))throw new AssertionError("Cross-chunk write: "+pos);
                    blocks.put(pos,state);entities.remove(pos);
                    if(state.getBlock() instanceof BaseEntityBlock block)entities.put(pos,block.newBlockEntity(pos,state));
                    return true;
                }
                case "getBlockState":return blocks.getOrDefault(args[0],Blocks.AIR.defaultBlockState());
                case "getBlockEntity":return entities.get(args[0]);
                case "getFluidState":return Fluids.EMPTY.defaultFluidState();
                case "toString":return "DungeonChunkCapture";
                default:throw new AssertionError("Unexpected worldgen operation: "+method.getName());
            }
        });
    }
}
