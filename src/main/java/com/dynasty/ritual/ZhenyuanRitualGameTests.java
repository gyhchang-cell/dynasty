package com.dynasty.ritual;

import com.mojang.authlib.GameProfile;
import net.minecraft.commands.arguments.blocks.BlockStateParser;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.GameType;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.entity.ChestBlockEntity;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.common.util.FakePlayer;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraft.resources.ResourceLocation;

import java.util.UUID;

@GameTestHolder("dynasty") @PrefixGameTestTemplate(false)
public final class ZhenyuanRitualGameTests {
    private static final class TravelingFighter extends FakePlayer {
        int placements;
        TravelingFighter(net.minecraft.server.level.ServerLevel level) { super(level,new GameProfile(UUID.randomUUID(),"ritual-full-flow")); }
        @Override public void teleportTo(net.minecraft.server.level.ServerLevel level,double x,double y,double z,float yaw,float pitch) {
            placements++;
            // Forge FakePlayer's network listener deliberately ignores same-level position packets.
            // Keep real ServerPlayer dimension transfer, hooks and world membership, then apply that packet's position.
            super.teleportTo(level,x,y,z,yaw,pitch);
            if(serverLevel()==level) moveTo(x,y,z,yaw,pitch);
        }
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=200)
    public static void encounterNeverReanchorsEitherParticipantAtFloorHeight(GameTestHelper h) {
        var server=h.getLevel().getServer();var arena=server.getLevel(ZhenyuanArena.DIMENSION);
        var data=ZhenyuanRitualSavedData.get(arena);
        var a=new TravelingFighter(arena);var b=new TravelingFighter(arena);
        var boss=ZhenyuanBosses.FINAL_BOSS.get().create(arena);
        var s=new ZhenyuanRitualSavedData.Session(h.getLevel().dimension().location().toString(),h.absolutePos(new BlockPos(2,2,2)));
        s.owner=a.getUUID();s.participants.add(b.getUUID());s.boss=boss.getUUID();s.arenaIndex=14;s.phase="active";s.removed=true;
        var arrival=Vec3.atBottomCenterOf(ZhenyuanArena.arrival(s.arenaIndex));
        var center=ZhenyuanArena.center(s.arenaIndex);
        arena.setChunkForced(center.getX()>>4,center.getZ()>>4,true);
        arena.getChunkAt(center);boss.setPos(Vec3.atCenterOf(center));boss.setNoGravity(true);
        h.assertTrue(arena.addFreshEntity(boss),"Fixture boss must be accepted into the reserved chunk");
        h.startSequence().thenWaitUntil(()->h.assertTrue(arena.getEntity(boss.getUUID())==boss,
                "Fixture not visible yet; removed="+boss.isRemoved()+", reason="+boss.getRemovalReason()+", pos="+boss.position()))
        .thenExecute(()->{
        data.sessions.put(s.key,s);
        var current=s;
        try {
            h.assertTrue(arena.getEntity(boss.getUUID())==boss,"Fixture boss must be loaded before testing movement");
            h.assertTrue(!ZhenyuanArena.interior(s.arenaIndex).deflate(.4).contains(arrival),"Regression fixture no longer exercises the old floor-height bug");
            for(int intro:new int[]{0,60,140,190,279,280,400}) {
                current.bossIntroTick=intro;
                for(var p:new TravelingFighter[]{a,b}) {
                    for(int t=0;t<12;t++) {
                        Vec3 at=arrival.add(t*.4,p==a?0:.42,t*.2),velocity=new Vec3(.12,.25,-.08);
                        p.moveTo(at.x,at.y,at.z,37+t,-23);p.setDeltaMovement(velocity);p.setSprinting(true);p.setShiftKeyDown(true);
                        ZhenyuanRitualService.advanceSession(server,current,data,p,t*10L);
                        h.assertTrue(p.placements==0&&p.position().distanceToSqr(at)<1e-10,"Encounter tick teleported participant at intro="+intro);
                        h.assertTrue(p.getDeltaMovement().equals(velocity)&&p.getYRot()==37+t&&p.getXRot()==-23,"Encounter reset velocity or view");
                        h.assertTrue(p.isSprinting()&&p.isShiftKeyDown(),"Encounter cleared input state");
                    }
                }
                current=ZhenyuanRitualSavedData.Session.load(current.save());data.sessions.put(s.key,current);
            }
        } finally {data.sessions.remove(s.key);data.setDirty();boss.discard();a.discard();b.discard();arena.setChunkForced(center.getX()>>4,center.getZ()>>4,false);}
        h.succeed();
        });
    }
    private static FakePlayer player(GameTestHelper h) {
        var p=new FakePlayer(h.getLevel(),new GameProfile(UUID.randomUUID(),"ritual-test"));
        h.getLevel().addNewPlayer(p); p.setGameMode(GameType.SURVIVAL); return p;
    }
    private static ZhenyuanRitualSavedData.Session session(GameTestHelper h,BlockPos core,FakePlayer p) {
        var s=new ZhenyuanRitualSavedData.Session(h.getLevel().dimension().location().toString(),core);
        s.owner=p.getUUID(); s.yaw=0; return s;
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=40)
    public static void fourOfferingsAndCentralSealAreOrderedAndIdempotent(GameTestHelper h) {
        h.assertTrue(ZhenyuanRitualRules.offer(0,4,"dynasty:hunyuan_pearl")==ZhenyuanRitualRules.OfferResult.FOUR_SIGILS_REQUIRED,"Center must wait");
        int mask=0;
        for(int slot:new int[]{3,0,2,1,4}) {
            h.assertTrue(ZhenyuanRitualRules.offer(mask,slot,"minecraft:diamond")==ZhenyuanRitualRules.OfferResult.WRONG_ITEM,"Wrong offering must fail");
            h.assertTrue(ZhenyuanRitualRules.offer(mask,slot,"dynasty:"+ZhenyuanRitualRules.OFFERINGS[slot])==ZhenyuanRitualRules.OfferResult.ACCEPTED,"Correct offering rejected");
            mask|=1<<slot;
            h.assertTrue(ZhenyuanRitualRules.offer(mask,slot,"dynasty:"+ZhenyuanRitualRules.OFFERINGS[slot])==ZhenyuanRitualRules.OfferResult.ALREADY_OFFERED,"Duplicate offering accepted");
        }
        h.assertTrue(mask==31&&ZhenyuanRitualRules.CHARGE_TICKS==100,"Five sigils and visible five-second charge");
        h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=40)
    public static void durableSessionRoundTripKeepsPendingReceiptsAndArenaAllocation(GameTestHelper h) {
        var data=new ZhenyuanRitualSavedData();
        var s=new ZhenyuanRitualSavedData.Session("minecraft:overworld",new BlockPos(300,64,-200));
        s.owner=UUID.randomUUID(); s.boss=UUID.randomUUID(); s.mask=31; s.phase="paused"; s.arenaIndex=17; s.arenaReady=true;
        for(int i=0;i<4;i++)s.offeringPlayers[i]=UUID.randomUUID();
        s.bossSnapshot.putFloat("Health",3210); s.rewardPending=true; s.rewardPos=s.core.south(4); s.removed=true;
        s.nodes.put(4,s.core.above(2)); s.owned.put(s.core.above(),"minecraft:stone"); data.sessions.put(s.key,s);
        var tag=data.save(new CompoundTag()); tag.remove("NextArena");
        var loaded=ZhenyuanRitualSavedData.load(tag); var restored=loaded.sessions.get(s.key);
        h.assertTrue(loaded.nextArena==18,"Missing allocator counter must not reuse a reserved arena");
        h.assertTrue(restored.owner.equals(s.owner)&&restored.boss.equals(s.boss)&&restored.mask==31&&restored.is("paused"),"Session identity/state lost");
        h.assertTrue(restored.arenaReady&&restored.removed&&restored.rewardPending&&!restored.rewardIssued,"Transaction flags lost");
        h.assertTrue(restored.rewardPos.equals(s.rewardPos)&&restored.bossSnapshot.getFloat("Health")==3210,"Pending reward/boss health lost");
        h.assertTrue(restored.nodes.equals(s.nodes)&&restored.owned.equals(s.owned),"Ownership map lost");
        h.assertTrue(java.util.Arrays.equals(s.offeringPlayers,restored.offeringPlayers),"Offering quest receipt owners lost");
        h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=40)
    public static void altarDisappearancePreservesFloorDragonAndReplacedBlocks(GameTestHelper h) {
        var l=h.getLevel(); BlockPos core=h.absolutePos(new BlockPos(5,3,5));
        var s=new ZhenyuanRitualSavedData.Session(l.dimension().location().toString(),core);
        BlockPos owned=core.above(), changed=core.east(), dragon=core.west(), floor=core.below(), nodePos=core.north();
        for(BlockPos p:new BlockPos[]{owned,changed,dragon,floor}) l.setBlockAndUpdate(p,Blocks.STONE.defaultBlockState());
        s.owned.put(owned,"minecraft:stone"); s.owned.put(changed,"minecraft:stone"); s.owned.put(floor,"minecraft:stone");
        l.setBlockAndUpdate(changed,Blocks.DIAMOND_BLOCK.defaultBlockState());
        l.setBlockAndUpdate(nodePos,ZhenyuanRitualContent.NODE.get().defaultBlockState().setValue(ZhenyuanNodeBlock.SLOT,0));
        var node=(ZhenyuanNodeBlockEntity)l.getBlockEntity(nodePos); node.configure(core,0); node.syncRitual(31,1);
        s.nodes.put(0,nodePos); s.owned.put(nodePos,BlockStateParser.serialize(ZhenyuanRitualContent.NODE.get().defaultBlockState().setValue(ZhenyuanNodeBlock.SLOT,0)));
        int removed=ZhenyuanRitualService.removeOwnedAltar(l,s);
        h.assertTrue(removed==2&&l.isEmptyBlock(owned)&&l.isEmptyBlock(nodePos),"Active=true owned node or stone was not removed");
        h.assertTrue(l.getBlockState(changed).is(Blocks.DIAMOND_BLOCK),"Player replacement was erased");
        h.assertTrue(l.getBlockState(dragon).is(Blocks.STONE)&&l.getBlockState(floor).is(Blocks.STONE),"Dragon or ground was erased");
        h.assertTrue(ZhenyuanRitualService.removeOwnedAltar(l,s)==0,"Replayed cleanup changed extra blocks"); h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=60)
    public static void actualNodeRejectsWrongDuplicateAndForeignOfferingsWithoutConsuming(GameTestHelper h) {
        var l=h.getLevel(); var p=player(h); var other=player(h); var data=ZhenyuanRitualSavedData.get(l);
        BlockPos core=h.absolutePos(new BlockPos(5,2,5)), pos=core.east();
        l.setBlockAndUpdate(pos,ZhenyuanRitualContent.NODE.get().defaultBlockState().setValue(ZhenyuanNodeBlock.SLOT,0));
        var node=(ZhenyuanNodeBlockEntity)l.getBlockEntity(pos); node.configure(core,0);
        var s=session(h,core,p); s.nodes.put(0,pos); data.sessions.put(s.key,s);
        p.setPos(Vec3.atCenterOf(core)); other.setPos(Vec3.atCenterOf(core));
        try {
            p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(Items.DIAMOND,5));
            ZhenyuanRitualService.interact(p,node);
            h.assertTrue(p.getMainHandItem().getCount()==5&&s.mask==0,"Wrong item was consumed");
            var offering=ForgeRegistries.ITEMS.getValue(new ResourceLocation("dynasty:qinglong_scale"));
            p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(offering,5));
            other.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(offering,5));
            ZhenyuanRitualService.interact(other,node);
            h.assertTrue(other.getMainHandItem().getCount()==5&&s.mask==0,"Other player stole ritual ownership");
            ZhenyuanRitualService.interact(p,node);
            h.assertTrue(s.mask==1&&p.getMainHandItem().getCount()==4,"Correct offering did not consume exactly one");
            ZhenyuanRitualService.interact(p,node);
            h.assertTrue(p.getMainHandItem().getCount()==4&&node.getOfferingMask()==1,"Duplicate click consumed or lost client sync");
        } finally { data.sessions.remove(s.key); p.discard(); other.discard(); }
        h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=120)
    public static void victoryChestIsUniqueAndNeverRefillsAfterRemoval(GameTestHelper h) {
        var l=h.getLevel(); var p=player(h); var data=new ZhenyuanRitualSavedData();
        BlockPos core=h.absolutePos(new BlockPos(3,3,2)); var s=session(h,core,p); s.phase="victory";
        BlockPos expected=core.south(3);
        l.setBlockAndUpdate(expected.below(),Blocks.STONE.defaultBlockState()); l.setBlockAndUpdate(expected,Blocks.AIR.defaultBlockState()); l.setBlockAndUpdate(expected.above(),Blocks.AIR.defaultBlockState());
        try {
            h.assertTrue(ZhenyuanRitualService.depositReward(p,s,data),"Victory did not create reward chest");
            var chest=(ChestBlockEntity)l.getBlockEntity(expected);
            h.assertTrue(chest!=null&&!chest.getItem(0).isEmpty()&&s.rewardIssued&&s.is("returned"),"Missing reward or commit");
            h.assertTrue(chest.getPersistentData().getString("DynastyZhenyuanReward").equals(s.key),"Missing receipt");
            chest.clearContent(); l.setBlockAndUpdate(expected,Blocks.AIR.defaultBlockState());
            h.assertTrue(!ZhenyuanRitualService.depositReward(p,s,data)&&l.isEmptyBlock(expected),"Looted/removed reward was refilled");
            s.phase="victory"; // Deliberate duplicate victory notification, with the durable receipt retained.
            h.assertTrue(!ZhenyuanRitualService.depositReward(p,s,data)&&l.isEmptyBlock(expected),"Replayed victory minted rewards");
        } finally { p.discard(); }
        h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=60)
    public static void pendingChestReceiptSurvivesCrashWithoutRefillingEmptyChest(GameTestHelper h) {
        var l=h.getLevel();var p=player(h);var data=new ZhenyuanRitualSavedData();
        BlockPos core=h.absolutePos(new BlockPos(3,3,2));var s=session(h,core,p);s.phase="victory";s.rewardPending=true;s.rewardPos=core.south(3);
        l.setBlockAndUpdate(s.rewardPos,Blocks.CHEST.defaultBlockState());
        var chest=(ChestBlockEntity)l.getBlockEntity(s.rewardPos);chest.clearContent();chest.getPersistentData().putString("DynastyZhenyuanReward",s.key);
        try {
            h.assertTrue(!ZhenyuanRitualService.depositReward(p,s,data),"Existing receipt must acknowledge, not refill");
            h.assertTrue(chest.isEmpty()&&s.rewardIssued&&s.is("returned")&&!s.rewardPending,"Pending receipt reconciliation failed");
        } finally {p.discard();}
        h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=60)
    public static void rewardObstructionKeepsItemsPendingAndPreservesPlayerBlocks(GameTestHelper h) {
        var l=h.getLevel();var p=player(h);var data=new ZhenyuanRitualSavedData();
        BlockPos core=h.absolutePos(new BlockPos(2,3,2));var s=session(h,core,p);s.phase="victory";
        for(int z=3;z<=10;z++) {
            l.setBlockAndUpdate(core.south(z).below(),Blocks.STONE.defaultBlockState());
            l.setBlockAndUpdate(core.south(z),Blocks.DIAMOND_BLOCK.defaultBlockState());
        }
        try {
            h.assertTrue(!ZhenyuanRitualService.depositReward(p,s,data)&&!s.rewardIssued&&s.is("victory"),"Obstructed reward must stay pending");
            for(int z=3;z<=10;z++)h.assertTrue(l.getBlockState(core.south(z)).is(Blocks.DIAMOND_BLOCK),"Player block overwritten");
        } finally {p.discard();}
        h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=60)
    public static void arenaDimensionAndReservedCellsAreSeparated(GameTestHelper h) {
        var arena=h.getLevel().getServer().getLevel(ZhenyuanArena.DIMENSION);
        h.assertTrue(arena!=null,"Dedicated arena dimension not loaded");
        h.assertTrue(!ZhenyuanArena.interior(0).intersects(ZhenyuanArena.interior(1)),"Adjacent sessions overlap");
        h.assertTrue(ZhenyuanArena.center(1).getX()-ZhenyuanArena.center(0).getX()==512,"Incorrect cell separation");
        h.assertTrue(ZhenyuanArena.interior(0).getXsize()==96&&ZhenyuanArena.interior(0).getYsize()==40,"Arena playable size changed");
        h.assertTrue(ZhenyuanArena.interior(0).contains(Vec3.atCenterOf(ZhenyuanArena.arrival(0))),"Arrival outside sealed chamber");
        h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=100)
    public static void importedBindingRetriesAreReadOnlyAndRejectDifferentOwnership(GameTestHelper h) {
        var level=h.getLevel(); var data=ZhenyuanRitualSavedData.get(level);
        BlockPos core=h.absolutePos(new BlockPos(6,3,6));
        level.setBlockAndUpdate(core.below(),Blocks.STONE.defaultBlockState());
        var nodes=new java.util.LinkedHashMap<Integer,BlockPos>();
        var owned=new java.util.LinkedHashMap<BlockPos,net.minecraft.world.level.block.state.BlockState>();
        for(int slot=0;slot<5;slot++) {
            BlockPos p=core.offset(slot-2,1,2);
            var state=ZhenyuanRitualContent.NODE.get().defaultBlockState().setValue(ZhenyuanNodeBlock.SLOT,slot);
            level.setBlockAndUpdate(p,state);nodes.put(slot,p);owned.put(p,state);
        }
        h.assertTrue(ZhenyuanRitualService.bindImportedAltar(level,core,owned,nodes),"First import binding rejected");
        var s=data.at(level,core);s.owner=UUID.randomUUID();s.mask=1;s.phase="charging";
        ZhenyuanRitualService.syncNodes(level,s);
        try {
            h.assertTrue(ZhenyuanRitualService.bindImportedAltar(level,core,owned,nodes),"Exact retry after job-checkpoint crash must succeed");
            h.assertTrue(data.at(level,core)==s&&s.mask==1&&s.is("charging")&&s.owner!=null,"Retry reset mutable progress or replaced session");
            h.assertTrue(((ZhenyuanNodeBlockEntity)level.getBlockEntity(nodes.get(0))).getOfferingMask()==1,"Retry reset active node renderer");
            var different=new java.util.LinkedHashMap<>(owned);different.put(core.above(3),Blocks.STONE.defaultBlockState());
            h.assertTrue(!ZhenyuanRitualService.bindImportedAltar(level,core,different,nodes),"Different clear-ownership list must not be acknowledged");
            var swapped=new java.util.LinkedHashMap<>(nodes);swapped.put(0,nodes.get(1));swapped.put(1,nodes.get(0));
            h.assertTrue(!ZhenyuanRitualService.bindImportedAltar(level,core,owned,swapped),"Different slot binding must be rejected");
            s.phase="returned";s.mask=31;s.rewardIssued=true;s.removed=true;
            for(BlockPos p:nodes.values())level.removeBlock(p,false);
            h.assertTrue(ZhenyuanRitualService.bindImportedAltar(level,core,owned,nodes),"Completed exact binding should close a stale importer checkpoint");
            h.assertTrue(s.is("returned")&&s.rewardIssued&&s.removed,"Completed session must not reset");
            for(BlockPos p:nodes.values())h.assertTrue(level.isEmptyBlock(p),"Retry rebuilt a vanished altar");
        } finally {data.sessions.remove(s.key);data.setDirty();}
        h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=60)
    public static void arenaRejectsEscapeAndBuildingWithoutAffectingOtherDimensions(GameTestHelper h) {
        var arena=h.getLevel().getServer().getLevel(ZhenyuanArena.DIMENSION);
        h.assertTrue(arena!=null,"Arena dimension missing");
        var inside=new FakePlayer(arena,new GameProfile(UUID.randomUUID(),"ritual-boundary"));
        var outside=player(h);
        try {
            var exit=new net.minecraftforge.event.entity.EntityTravelToDimensionEvent(inside,net.minecraft.world.level.Level.OVERWORLD);
            ZhenyuanRitualService.travel(exit);h.assertTrue(exit.isCanceled(),"Unauthorized player portal escaped arena");
            var entry=new net.minecraftforge.event.entity.EntityTravelToDimensionEvent(outside,ZhenyuanArena.DIMENSION);
            ZhenyuanRitualService.travel(entry);h.assertTrue(entry.isCanceled(),"Uninvited player entered another session");
            var chorus=new net.minecraftforge.event.entity.EntityTeleportEvent.ChorusFruit(inside,500,65,500);
            ZhenyuanRitualService.teleport(chorus);h.assertTrue(chorus.isCanceled(),"Same-dimension teleport escaped shell");
            var ordinary=new net.minecraftforge.event.entity.EntityTeleportEvent.ChorusFruit(outside,10,65,10);
            ZhenyuanRitualService.teleport(ordinary);h.assertTrue(!ordinary.isCanceled(),"Unrelated overworld teleport blocked");
            var breakArena=new net.minecraftforge.event.level.BlockEvent.BreakEvent(arena,new BlockPos(0,64,0),Blocks.STONE.defaultBlockState(),inside);
            ZhenyuanRitualService.breakBlock(breakArena);h.assertTrue(breakArena.isCanceled(),"Arena block mining permitted");
            var breakWorld=new net.minecraftforge.event.level.BlockEvent.BreakEvent(h.getLevel(),h.absolutePos(BlockPos.ZERO),Blocks.STONE.defaultBlockState(),outside);
            ZhenyuanRitualService.breakBlock(breakWorld);h.assertTrue(!breakWorld.isCanceled(),"Ordinary overworld building affected");
            var boss=ZhenyuanBosses.FINAL_BOSS.get().create(arena);
            var bossExit=new net.minecraftforge.event.entity.EntityTravelToDimensionEvent(boss,net.minecraft.world.level.Level.OVERWORLD);
            ZhenyuanRitualService.travel(bossExit);h.assertTrue(bossExit.isCanceled(),"Boss can be pulled out of the sealed dimension");
        } finally {inside.discard();outside.discard();}
        h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=60)
    public static void cancelledOrUnrelatedDeathsNeverCommitVictory(GameTestHelper h) {
        var arena=h.getLevel().getServer().getLevel(ZhenyuanArena.DIMENSION);
        var boss=ZhenyuanBosses.FINAL_BOSS.get().create(arena);
        var unrelated=ZhenyuanBosses.FINAL_BOSS.get().create(arena);
        var data=ZhenyuanRitualSavedData.get(arena);
        var s=new ZhenyuanRitualSavedData.Session(h.getLevel().dimension().location().toString(),h.absolutePos(new BlockPos(4,3,4)));
        s.owner=UUID.randomUUID();s.boss=boss.getUUID();s.mask=31;s.phase="active";data.sessions.put(s.key,s);
        try {
            var cancelled=new net.minecraftforge.event.entity.living.LivingDeathEvent(boss,boss.damageSources().genericKill());cancelled.setCanceled(true);
            ZhenyuanRitualService.bossDeath(cancelled);
            h.assertTrue(s.is("active")&&!s.rewardIssued,"Cancelled/resurrected boss death paid victory");
            ZhenyuanRitualService.bossDeath(new net.minecraftforge.event.entity.living.LivingDeathEvent(unrelated,unrelated.damageSources().genericKill()));
            h.assertTrue(s.is("active"),"Another entity/session death paid victory");
            s.phase="paused";
            ZhenyuanRitualService.bossDeath(new net.minecraftforge.event.entity.living.LivingDeathEvent(boss,boss.damageSources().genericKill()));
            h.assertTrue(s.is("paused")&&!s.rewardIssued,"Inactive encounter paid victory");
        } finally {data.sessions.remove(s.key);data.setDirty();boss.discard();unrelated.discard();}
        h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=400)
    public static void fullRitualLifecycleTransfersDefeatsResumesAndReturnsWithOneChest(GameTestHelper h) {
        var home=h.getLevel(); var server=home.getServer(); var data=ZhenyuanRitualSavedData.get(home);
        var p=new TravelingFighter(home); home.addNewPlayer(p); p.setGameMode(GameType.SURVIVAL);
        BlockPos core=h.absolutePos(new BlockPos(7,3,7));
        for(int x=-5;x<=5;x++)for(int z=-5;z<=5;z++) {
            home.setBlockAndUpdate(core.offset(x,-1,z),Blocks.STONE.defaultBlockState());
            for(int y=0;y<=4;y++)home.setBlockAndUpdate(core.offset(x,y,z),Blocks.AIR.defaultBlockState());
        }
        var nodes=new java.util.LinkedHashMap<Integer,BlockPos>();
        nodes.put(0,core.offset(3,1,0));nodes.put(1,core.offset(-3,1,0));nodes.put(2,core.offset(0,1,3));
        nodes.put(3,core.offset(0,1,-3));nodes.put(4,core.above(2));
        var owned=new java.util.LinkedHashMap<BlockPos,net.minecraft.world.level.block.state.BlockState>();
        for(var e:nodes.entrySet()) {
            var state=ZhenyuanRitualContent.NODE.get().defaultBlockState().setValue(ZhenyuanNodeBlock.SLOT,e.getKey());
            home.setBlockAndUpdate(e.getValue(),state);owned.put(e.getValue(),state);
        }
        home.setBlockAndUpdate(core.above(),Blocks.CHISELED_DEEPSLATE.defaultBlockState());
        owned.put(core.above(),Blocks.CHISELED_DEEPSLATE.defaultBlockState());
        h.assertTrue(ZhenyuanRitualService.bindImportedAltar(home,core,owned,nodes),"Trusted new altar import did not bind");
        var s=data.at(home,core); var originalKey=s.key;
        java.util.concurrent.atomic.AtomicInteger victoryEvents=new java.util.concurrent.atomic.AtomicInteger();
        java.util.function.Consumer<ZhenyuanVictoryEvent> listener=e->{if(e.sessionKey().equals(originalKey))victoryEvents.incrementAndGet();};
        net.minecraftforge.common.MinecraftForge.EVENT_BUS.addListener(listener);
        try {
            for(int slot:new int[]{2,0,3,1,4}) {
                BlockPos at=nodes.get(slot);p.setPos(Vec3.atCenterOf(at).add(0,0,1.5));p.setYRot(0);
                var item=slot==4?ZhenyuanRitualContent.TIANMING_JADE.get():ForgeRegistries.ITEMS.getValue(new ResourceLocation("dynasty",ZhenyuanRitualRules.OFFERINGS[slot]));
                p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(item,2));
                ZhenyuanRitualService.interact(p,(ZhenyuanNodeBlockEntity)home.getBlockEntity(at));
                h.assertTrue(p.getMainHandItem().getCount()==1,"Each real offering must consume one: slot="+slot+" mask="+s.mask+" pending="+s.pendingMask+" stage="+s.ritualStage+" alive="+p.isAlive());
                if(slot<4) for(int t=0;t<260;t++)ZhenyuanRitualService.advanceSession(server,s,data,p,t);
            }
            h.assertTrue(s.ritualStage.equals("FINAL_RITUAL")&&s.mask==31&&home.getBlockEntity(nodes.get(4)) instanceof ZhenyuanNodeBlockEntity,"Charging altar disappeared too early");
            for(int t=0;t<239;t++)ZhenyuanRitualService.advanceSession(server,s,data,p,t);
            h.assertTrue(p.serverLevel()==home&&s.is("idle"),"Final animation cut short");
            ZhenyuanRitualService.advanceSession(server,s,data,p,240);
            var arena=server.getLevel(ZhenyuanArena.DIMENSION);
            h.assertTrue(s.is("active")&&s.arenaReady&&p.serverLevel()==arena,"Real dimension transfer/start failed");
            h.assertTrue(ZhenyuanArena.interior(s.arenaIndex).contains(p.position()),"Player outside arena");
            for(BlockPos at:owned.keySet())h.assertTrue(home.isEmptyBlock(at),"Managed altar remained after entry");
            h.assertTrue(home.getBlockState(core.below()).is(Blocks.STONE),"Return floor erased");
            var boss=(net.minecraft.world.entity.Mob)arena.getEntity(s.boss);
            h.assertTrue(boss!=null,"Boss missing in sealed arena");boss.setHealth(1234);
            h.assertTrue(boss.isNoAi()&&boss.isInvulnerable()&&s.bossIntroTick==0,"Arrival must start sealed, not attacking");
            for(int intro=1;intro<=280;intro++) {
                boss.tick();
                h.assertTrue(s.bossIntroTick==intro,"Arrival must advance exactly one authoritative tick");
                if(intro<280)h.assertTrue(boss.isNoAi()&&boss.isInvulnerable()&&!s.bossFightStarted,"Intro started combat early");
            }
            h.assertTrue(s.bossFightStarted&&!boss.isNoAi(),"Intro never released combat gate");
            var fatal=new net.minecraftforge.event.entity.living.LivingDeathEvent(p,p.damageSources().genericKill());
            ZhenyuanRitualService.death(fatal);
            h.assertTrue(fatal.isCanceled()&&s.is("paused")&&p.serverLevel()==home&&p.getHealth()>0,"Fatal defeat did not safely return");
            h.assertTrue(!s.rewardIssued&&p.getMainHandItem().getCount()==1,"Defeat paid reward or lost inventory");
            // Exercise a disk round-trip AND a missing entity, not just a superficial paused flag.
            var restored=ZhenyuanRitualSavedData.load(data.save(new CompoundTag())).sessions.get(s.key);
            data.sessions.put(s.key,restored);s=restored;boss.discard();
            h.assertTrue(ZhenyuanRitualService.resume(p)==1,"Resume rejected");
            ZhenyuanRitualService.advanceSession(server,s,data,p,s.chargeEnds);
            boss=(net.minecraft.world.entity.Mob)arena.getEntity(s.boss);
            h.assertTrue(s.is("active")&&p.serverLevel()==arena&&boss!=null&&boss.getHealth()==1234&&!boss.isNoAi(),"Reload must restore damaged boss and AI, not heal it");
            h.assertTrue(ZhenyuanRitualService.escape(p)==1&&s.is("paused")&&p.serverLevel()==home&&!s.rewardIssued,"Escape paid rewards or trapped player");
            ZhenyuanRitualService.resume(p);ZhenyuanRitualService.advanceSession(server,s,data,p,s.chargeEnds);
            boss=(net.minecraft.world.entity.Mob)arena.getEntity(s.boss);boss.setHealth(1);
            boss.hurt(boss.damageSources().genericKill(),Float.MAX_VALUE);
            h.assertTrue(s.is("victory")&&victoryEvents.get()==1,"Actual boss death did not commit victory exactly once");
            ZhenyuanRitualService.bossDeath(new net.minecraftforge.event.entity.living.LivingDeathEvent(boss,boss.damageSources().genericKill()));
            h.assertTrue(victoryEvents.get()==1,"Duplicate death repeated dragon scenery hook");
            // Another protection mod may veto even our authorized dimension transfer. A void
            // teleport call must not be mistaken for a successful return or grant a remote chest.
            java.util.function.Consumer<net.minecraftforge.event.entity.EntityTravelToDimensionEvent> vetoReturn=e->{
                if(e.getEntity()==p&&e.getDimension().equals(home.dimension()))e.setCanceled(true);
            };
            net.minecraftforge.common.MinecraftForge.EVENT_BUS.addListener(vetoReturn);
            try {
                ZhenyuanRitualService.advanceSession(server,s,data,p,s.victoryAt+60);
                h.assertTrue(p.serverLevel()==arena&&s.is("victory")&&!s.returnedToOrigin&&!s.rewardIssued,
                        "Cancelled return incorrectly committed rewards or stranded completed session");
                h.assertTrue(s.rewardPos==null,"Reward chest must wait until real return succeeds");
            } finally {net.minecraftforge.common.MinecraftForge.EVENT_BUS.unregister(vetoReturn);}
            ZhenyuanRitualService.advanceSession(server,s,data,p,s.victoryAt+60);
            h.assertTrue(s.is("returned")&&s.rewardIssued&&p.serverLevel()==home&&p.blockPosition().equals(core),"Victory did not return to old altar center");
            h.assertTrue(s.rewardPos!=null&&s.rewardPos.getZ()>core.getZ(),"Reward not in front of returned player");
            h.assertTrue(home.getBlockEntity(s.rewardPos) instanceof ChestBlockEntity chest&&!chest.isEmpty(),"Reward chest empty/missing");
            var rewardPos=s.rewardPos;((ChestBlockEntity)home.getBlockEntity(rewardPos)).clearContent();home.removeBlock(rewardPos,false);
            ZhenyuanRitualService.claim(p);
            h.assertTrue(home.isEmptyBlock(rewardPos),"Claim replay refilled looted chest");
        } finally {
            net.minecraftforge.common.MinecraftForge.EVENT_BUS.unregister(listener);
            var latest=data.sessions.remove(originalKey);data.setDirty();
            if(latest!=null&&latest.arenaIndex>=0) {
                var arena=server.getLevel(ZhenyuanArena.DIMENSION);
                if(arena!=null) {if(latest.boss!=null&&arena.getEntity(latest.boss)!=null)arena.getEntity(latest.boss).discard();ZhenyuanArena.forceChunks(arena,latest.arenaIndex,false);}
            }
            p.discard();
        }
        h.succeed();
    }
}
