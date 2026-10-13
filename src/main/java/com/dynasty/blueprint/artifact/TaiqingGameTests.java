package com.dynasty.blueprint.artifact;

import net.minecraft.core.*;
import net.minecraft.gametest.framework.*;
import net.minecraft.server.level.*;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.MoverType;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.gametest.*;
import java.util.*;

/** Two additional native temple acceptance SOURCES. Neither has run during the user's Java pause. */
@GameTestHolder("dynasty_army") @PrefixGameTestTemplate(false)
public final class TaiqingGameTests {
    private static final Map<ServerLevel,List<ServerPlayer>> PLAYERS=new HashMap<>();
    private record Fixture(ServerPlayer player,BlockPos swordCase){}
    private static Fixture temple(GameTestHelper h){
        var p=ArtifactGameTests.player(h);PLAYERS.computeIfAbsent(h.getLevel(),k->new ArrayList<>()).add(p);p.setItemInHand(InteractionHand.MAIN_HAND,ItemStack.EMPTY);
        var piece=new TaiqingTemplePiece(p.blockPosition().offset(-10,-7,-10));var c=piece.swordCase();
        piece.postProcess(h.getLevel(),h.getLevel().structureManager(),h.getLevel().getChunkSource().getGenerator(),net.minecraft.util.RandomSource.create(13),piece.getBoundingBox(),new ChunkPos(c),c);
        ZhanluTrialRewards.registerSwordCase(h.getLevel(),c);var at=Vec3.atBottomCenterOf(c.offset(-6,0,-6));p.setPos(at);p.setNoGravity(false);p.setDeltaMovement(Vec3.ZERO);
        h.onEachTick(()->{if(p.isAlive())p.move(MoverType.SELF,new Vec3(0,-.01,0));});return new Fixture(p,c);
    }
    @AfterBatch(batch="taiqing_trials") public static void release(ServerLevel w){var ps=PLAYERS.remove(w);if(ps!=null)for(var p:ps)TaiqingTrials.cancel(p);ArtifactGameTests.release(w);}
    @GameTest(template="cauldron_pit_test",timeoutTicks=100,batch="taiqing_trials")
    public static void realTempleFloorSupportedRoofsTwoMetreCaseAndFortyTickMeditation(GameTestHelper h){
        var f=temple(h);var p=f.player();var c=f.swordCase();
        h.runAfterDelay(4,()->{
            h.assertTrue(h.getLevel().getBlockState(c.offset(-6,-1,-6)).is(Blocks.LIME_TERRACOTTA)&&h.getLevel().getBlockState(c.offset(6,-1,-3)).is(Blocks.CALCITE),"Real meditation and connected white path floors exist");
            h.assertTrue(h.getLevel().getBlockState(c.offset(-8,2,-8)).is(Blocks.STRIPPED_SPRUCE_LOG)&&h.getLevel().getBlockState(c.offset(-5,7,-6)).is(Blocks.DARK_PRISMARINE_STAIRS),"Native roof and continuously supported pillars, not proposed-only temple");
            var state=h.getLevel().getBlockState(c);var box=state.getCollisionShape(h.getLevel(),c).bounds();h.assertTrue(Math.abs(box.getZsize()-2)<.001,"Sword case is actually2m long, fitting the1.4m sword");
            h.assertTrue(TaiqingTrials.begin(p,c),"Real case starts this player's native trial");
        });
        h.runAfterDelay(42,()->h.assertTrue(TaiqingTrials.stage(p)==1,"Thirty-eight stationary ticks cannot finish the40-tick objective"));
        h.runAfterDelay(49,()->{h.assertTrue(TaiqingTrials.stage(p)==2&&ZhanluTrialRewards.active(p,c)&&!ZhanluTrialRewards.completeStage(p,c,1),"Only actual continued standing on native floor advances to ordered path stage");h.succeed();});
    }
    @GameTest(template="cauldron_pit_test",timeoutTicks=95,batch="taiqing_trials")
    public static void realDamageAndMovementDiscontinuityCannotGrantTempleSword(GameTestHelper h){
        var f=temple(h);var p=f.player();var c=f.swordCase();
        h.runAfterDelay(4,()->h.assertTrue(TaiqingTrials.begin(p,c),"Registered real case begins"));
        h.runAfterDelay(20,()->{p.hurt(p.damageSources().generic(),1);h.assertTrue(TaiqingTrials.stage(p)==0&&!ZhanluTrialRewards.active(p,c)&&!ZhanluTrialRewards.claim(p,c,InteractionHand.MAIN_HAND),"Actual accepted damage cancels both goal session and reward eligibility");});
        h.runAfterDelay(35,()->{h.assertTrue(TaiqingTrials.begin(p,c),"Unclaimed player may retry");var saved=p.saveWithoutId(new net.minecraft.nbt.CompoundTag());p.load(saved);p.setPos(c.getX()+.5,c.getY(),c.getZ()+.5);});
        h.runAfterDelay(88,()->{h.assertTrue(!ZhanluTrialRewards.eligible(p,c)&&!ZhanluTrialRewards.claim(p,c,InteractionHand.MAIN_HAND),"Moving off the meditation stone or reloading cannot bypass all three native goals");h.succeed();});
    }
}
