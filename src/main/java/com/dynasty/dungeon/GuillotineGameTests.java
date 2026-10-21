package com.dynasty.dungeon;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;

/** Prepared native regression cases; no Java execution in the 2026-10-18 batch. */
@GameTestHolder("dynasty_cod2")
@PrefixGameTestTemplate(false)
public final class GuillotineGameTests {
    @GameTest(template="bow_ritual_test",batch="cod2_guillotine")
    public static void contactFollowsTheDropAndNeverReplaysAfterReload(GameTestHelper h){
        var clock=DungeonTrapProfile.GUILLOTINE.clock();clock.trigger(100);
        for(int time=102;time<=120;time+=2){clock.tickActive(time);h.assertTrue(!clock.consumeContact(),"Warning and initial active frame cannot damage");}
        h.assertTrue(clock.phase()==DungeonMechanism.Phase.ACTIVE,"Twenty-tick tell ends in an actual falling phase");
        var inFlight=DungeonHazard.restore(clock.save());inFlight.pause(10000);inFlight.tickActive(10002);
        h.assertTrue(inFlight.consumeContact()&&!inFlight.consumeContact(),"One contact at the saved drop's second tick");
        var after=DungeonHazard.restore(inFlight.save());after.tickActive(10004);
        h.assertTrue(!after.consumeContact(),"Reloading a consumed impact never repeats damage");
        var gap=DungeonTrapProfile.GUILLOTINE.clock();gap.trigger(0);gap.tickActive(2);gap.tickActive(10000);
        h.assertTrue(gap.phase()==DungeonMechanism.Phase.WARNING&&gap.ticks()==0&&!gap.consumeContact(),"Long inactive time restarts a full warning and never catches up hits");
        h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod2_guillotine")
    public static void unfittedCoreCycleRepeatsEveryFortyTicks(GameTestHelper h){
        var clock=DungeonTrapProfile.GUILLOTINE.clock();var hits=new java.util.ArrayList<Integer>();
        for(int time=0;time<=122;time+=2){
            if(clock.phase()==DungeonMechanism.Phase.IDLE)clock.trigger(time);
            clock.tickActive(time);
            if(clock.phase()==DungeonMechanism.Phase.IDLE)clock.trigger(time);
            if(clock.consumeContact())hits.add(time);
        }
        h.assertTrue(hits.equals(java.util.List.of(22,62,102)),"Same two-tick scheduler cadence as production core, with no extra idle frame");
        h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod2_guillotine")
    public static void fourFacingsUseTheVisibleSweptPlane(GameTestHelper h){
        var p=new BlockPos(-16,20,-1);
        for(var facing:Direction.Plane.HORIZONTAL){
            var box=GuillotineTrap.sweep(p,facing);boolean alongX=facing.getAxis()==Direction.Axis.Z;
            h.assertTrue(Math.abs(box.getXsize()-(alongX?2.75:.375))<1e-6&&Math.abs(box.getZsize()-(alongX?.375:2.75))<1e-6,
                "Facing rotates the same narrow blade plane; it never hits the whole hallway");
            h.assertTrue(box.minY==17&&box.maxY==19.875,"Sweep stops at the floor and below the ceiling anchor");
            h.assertTrue(GuillotineTrap.renderBounds(p).contains(box.minX,box.minY,box.minZ)
                &&GuillotineTrap.renderBounds(p).contains(box.maxX,box.maxY,box.maxZ),"Animated blade is inside expanded renderer bounds");
        }
        h.assertTrue(GuillotineTrap.bladeY(2,.5)==GuillotineTrap.LOWERED,"Visible edge reaches floor on contact tick 2 of active duration 4");
        h.assertTrue(GuillotineTrap.bladeY(3,1)==GuillotineTrap.RAISED,"Recovery returns to supported hanging position");
        h.succeed();
    }
}
