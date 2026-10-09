package com.dynasty.expansion;

import com.dynasty.cod3.SecretTracker;
import com.mojang.authlib.GameProfile;
import java.util.UUID;
import net.minecraft.core.*;
import net.minecraft.gametest.framework.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.item.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.*;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.gametest.*;

@GameTestHolder("dynasty_cod4") @PrefixGameTestTemplate(false)
public final class PuzzleSecretGameTests {
    private static ServerPlayer player(GameTestHelper h){return player(h,new GameProfile(UUID.randomUUID(),"lock-native"));}
    private static ServerPlayer player(GameTestHelper h,GameProfile profile){
        var p=new ServerPlayer(h.getLevel().getServer(),h.getLevel(),profile);
        p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);
        p.setPos(Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(3,2,3))));return p;
    }
    private static BlockPos box(GameTestHelper h){var at=h.absolutePos(new BlockPos(3,2,3));h.getLevel().setBlockAndUpdate(at,SmallInteractions.ENTRIES.get("puzzle_box").get().defaultBlockState());return at;}
    private static void use(GameTestHelper h,ServerPlayer p,BlockPos at){h.getLevel().getBlockState(at).use(h.getLevel(),p,InteractionHand.MAIN_HAND,new BlockHitResult(Vec3.atCenterOf(at),Direction.UP,at,false));}
    private static void pose(ServerPlayer p,int step){float[] yaw={180,-90,0,90};p.setYRot(yaw[step%4]);p.setShiftKeyDown(step%2==1);}
    private static void ready(ServerPlayer p){var root=EquipmentBehaviors.saved(p);root.putLong("site_puzzle_box_start",p.level().getGameTime()-2400);root.putLong("site_puzzle_box_next",p.level().getGameTime());}
    private static CompoundTag partial(ServerPlayer p,BlockPos at,int count){var n=new CompoundTag();n.putLong("Anchor",at.asLong());n.putString("SiteDimension",p.level().dimension().location().toString());n.putInt("Count",count);n.putLong("Last",p.level().getGameTime()-10);p.getPersistentData().put("cod3_progress_30",n);return n;}
    @GameTest(template="bow_ritual_test",batch="cod4_lock_native",setupTicks=20)
    public static void directionPostureAndOriginalTwoMinuteDeadlineAreActualPredicates(GameTestHelper h){
        var p=player(h);var at=box(h);pose(p,1);use(h,p,at);var root=EquipmentBehaviors.saved(p);
        h.assertTrue(!root.contains("site_puzzle_box_start"),"Wrong starting direction/posture starts no lock timer");pose(p,0);use(h,p,at);long now=h.getLevel().getGameTime();
        h.assertTrue(root.getLong("site_puzzle_box_start")==now&&root.getLong("site_puzzle_box_next")==now+800,"Original three 800-tick stages retain the two-minute timer");
        use(h,p,at);h.assertTrue(SecretTracker.puzzleCount(p)==0,"Early/spammed presses cannot add progress");
        ready(p);partial(p,at,3);root.putLong("site_puzzle_box_start",now-2399);pose(p,3);use(h,p,at);
        h.assertTrue(!SecretTracker.puzzleClaimed(p)&&SecretTracker.puzzleCount(p)==3&&p.getInventory().countItem(ExpansionContent.item("blueprint"))==0,"Final pin cannot bypass original total duration via overdue per-step field");
        ready(p);p.setShiftKeyDown(false);use(h,p,at);h.assertTrue(SecretTracker.puzzleCount(p)==3,"Original final alternating sneak posture remains required");
        p.setShiftKeyDown(true);p.setPos(p.getX()+30,p.getY(),p.getZ());h.assertTrue(!SecretTracker.pressPuzzle(p,at).accepted(),"Remote player cannot press a lock");
        p.setPos(Vec3.atBottomCenterOf(at));h.getLevel().setBlockAndUpdate(at,Blocks.STONE.defaultBlockState());h.assertTrue(!SecretTracker.pressPuzzle(p,at).accepted(),"Removed Site is not a forged secret anchor");h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod4_lock_sequence",setupTicks=20,timeoutTicks=100)
    public static void fourNativePinsRetainOldThreePosesAndGiveEachOriginalRewardOnce(GameTestHelper h){
        var p=player(h);var at=box(h);p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(Items.PAPER,5));pose(p,0);use(h,p,at);ready(p);
        for(int i=0;i<4;i++){final int step=i;h.runAtTickTime(1+i*10,()->{
            pose(p,step);var root=EquipmentBehaviors.saved(p);root.putLong("site_puzzle_box_next",h.getLevel().getGameTime());use(h,p,at);
            h.assertTrue(SecretTracker.puzzleCount(p)==step+1&&root.getInt("site_puzzle_box_count")==Math.min(3,step+1),"Original secret owns four cardinal pins; old Site three-count record is retained");
            h.assertTrue(root.getLong("site_puzzle_box_next")==h.getLevel().getGameTime()+(step<2?800:10),"Original long stage intervals stay intact and the final latch is bounded by ten ticks");
            h.assertTrue(p.getInventory().countItem(Items.PAPER)==5,"Unpaid original lock never invents an item charge");
            if(step<3)h.assertTrue(!SecretTracker.puzzleClaimed(p)&&!root.getBoolean("site_puzzle_box_done")&&p.getInventory().countItem(ExpansionContent.item("blueprint"))==0,"Incomplete cardinal sequence awards no reward");
            else{
                h.assertTrue(SecretTracker.puzzleClaimed(p)&&root.getBoolean("site_puzzle_box_done")&&p.getInventory().countItem(ExpansionContent.item("blueprint"))==1&&p.getInventory().countItem(ExpansionContent.item("copper_coin"))==2,"Completed native secret gives one original blueprint and preserves the original Site's two coins");
                var adv=p.server.getAdvancements().getAdvancement(new net.minecraft.resources.ResourceLocation("dynasty","cod4_puzzle_box"));h.assertTrue(p.getAdvancements().getOrStartProgress(adv).isDone(),"Existing actual COD4 task advancement is awarded");
                use(h,p,at);h.assertTrue(p.getInventory().countItem(ExpansionContent.item("blueprint"))==1&&p.getInventory().countItem(ExpansionContent.item("copper_coin"))==2,"Repeat use cannot replay either reward");h.succeed();
            }
        });}
    }
    @GameTest(template="bow_ritual_test",batch="cod4_lock_native",setupTicks=20)
    public static void wrongFacingResetsNativeSequenceButNeverErasesOldCompletedRecords(GameTestHelper h){
        var p=player(h);var at=box(h);ready(p);var root=EquipmentBehaviors.saved(p);root.putBoolean("site_puzzle_box_done",true);root.putInt("site_puzzle_box_count",3);
        partial(p,at,2);pose(p,0);use(h,p,at);
        h.assertTrue(SecretTracker.puzzleCount(p)==0&&!SecretTracker.puzzleClaimed(p),"Wrong cardinal direction resets original native sequence rather than faking a completed old generic counter");
        h.assertTrue(root.getBoolean("site_puzzle_box_done")&&root.getInt("site_puzzle_box_count")==3,"Legacy completion and three-count record remain intact after a wrong missing-secret attempt");
        h.assertTrue(!SecretTracker.get(h.getLevel()).claim(p,30,at),"Legacy generic completion alone is not native readiness proof");
        var other=player(h);h.assertTrue(SecretTracker.puzzleCount(other)==0&&!SecretTracker.puzzleClaimed(other),"Detached second character has independent existing player-scope progress, not real network multiplayer evidence");h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod4_lock_native",setupTicks=20)
    public static void legacyMissingBlueprintAndPartialDeathCloneNeverReplaySiteCoins(GameTestHelper h){
        var p=player(h);var at=box(h);ready(p);var root=EquipmentBehaviors.saved(p);root.putBoolean("site_puzzle_box_done",true);root.putInt("site_puzzle_box_count",3);var original=partial(p,at,3);
        var q=player(h,p.getGameProfile());SecretTracker.clone(new PlayerEvent.Clone(q,p,true));pose(q,3);use(h,q,at);
        h.assertTrue(SecretTracker.puzzleClaimed(q)&&q.getInventory().countItem(ExpansionContent.item("blueprint"))==1&&q.getInventory().countItem(ExpansionContent.item("copper_coin"))==0,"Death clone retains actual first three pins; earning missing native blueprint does not replay legacy Site coins");
        h.assertTrue(original.getInt("Count")==3,"Cloned native pin progress is a deep copy");
        var next=player(h,p.getGameProfile());SecretTracker.clone(new PlayerEvent.Clone(next,q,true));pose(next,3);use(h,next,at);
        h.assertTrue(SecretTracker.puzzleClaimed(next)&&next.getInventory().countItem(ExpansionContent.item("blueprint"))==0&&next.getInventory().countItem(ExpansionContent.item("copper_coin"))==0,"Completed native claim survives a further death without replaying any reward");h.succeed();
    }
}
