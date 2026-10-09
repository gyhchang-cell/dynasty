package com.dynasty.dungeon;

import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.world.level.block.Blocks;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;

/** Server hazard checks; full dungeon and visual acceptance remain separate. */
@GameTestHolder("dynasty_cod2")
@PrefixGameTestTemplate(false)
public final class ChenshaVaultGameTests {
    @GameTest(template="bow_ritual_test",batch="cod2_vault")
    public static void mercuryWarningContactAndReloadAreAuthoritative(GameTestHelper h) {
        var room=new DungeonRoomController();var clock=room.mercuryMoat();clock.trigger(100);
        for(long t=102;t<120;t+=2)clock.tickActive(t);
        h.assertTrue(clock.phase()==DungeonMechanism.Phase.WARNING&&!clock.consumeContact(),"Full one-second warning before damage");
        clock.tickActive(120);
        h.assertTrue(clock.consumeContact()&&!clock.consumeContact(),"First contact consumed once");
        var restored=new DungeonRoomController();restored.load(room.save());clock=restored.mercuryMoat();
        clock.tickActive(10000);
        h.assertTrue(!clock.consumeContact()&&clock.ticks()==0,"Unloaded interval cannot replay a contact or burst damage");
        int hits=0;for(long t=10002;t<=10020;t+=2){clock.tickActive(t);if(clock.consumeContact())hits++;}
        h.assertTrue(hits==1&&clock.phase()==DungeonMechanism.Phase.RECOVERY,"Only the remaining contact occurs before recovery");
        room.complete();
        h.assertTrue(restored.mercuryMoat()!=room.mercuryMoat(),"Two room instances do not share a hazard clock");
        h.succeed();
    }

    @GameTest(template="bow_ritual_test",batch="cod2_vault")
    public static void onlyNewMoatSurfacesExposeSurvivalPlayers(GameTestHelper h) {
        var level=h.getLevel();var origin=h.absolutePos(new BlockPos(-32,1,-27));
        var surface=origin.offset(32,0,4);var player=h.makeMockSurvivalPlayer();
        try {
            player.setPos(surface.getX()+.5,surface.getY()+1,surface.getZ()+.5);
            level.setBlockAndUpdate(surface,Blocks.LIGHT_BLUE_STAINED_GLASS.defaultBlockState());
            h.assertTrue(!ChenshaMercuryMoat.exposed(level,origin,player),"Existing glass-only vaults retain their behavior");
            level.setBlockAndUpdate(surface,DungeonContent.MERCURY_CHANNEL.get().defaultBlockState());
            h.assertTrue(ChenshaMercuryMoat.exposed(level,origin,player),"Authored new channel actually exposes a survival player");
            player.setPos(player.getX(),surface.getY()+1.6,player.getZ());
            h.assertTrue(!ChenshaMercuryMoat.exposed(level,origin,player),"Jumping clear of the surface avoids contact");
            player.setPos(origin.getX()+32.5,origin.getY()+1,origin.getZ()+26.5);
            h.assertTrue(!ChenshaMercuryMoat.exposed(level,origin,player),"The main route remains outside the hazard");
            h.assertTrue(DungeonContent.MERCURY_CHANNEL.get().defaultBlockState().getDestroySpeed(level,surface)<0,
                "Ordinary mining cannot bypass or harvest the key channel");
            h.succeed();
        } finally {level.setBlockAndUpdate(surface,Blocks.AIR.defaultBlockState());player.discard();}
    }
}
