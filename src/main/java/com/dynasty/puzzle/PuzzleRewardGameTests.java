package com.dynasty.puzzle;

import com.dynasty.Dynasty;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.entity.ChestBlockEntity;
import net.minecraft.world.item.Items;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;

@GameTestHolder(Dynasty.MODID) @PrefixGameTestTemplate(false)
public final class PuzzleRewardGameTests {
    @GameTest(template="bow_ritual_test",timeoutTicks=80)
    public static void chestIsCreatedOnceAndNeverRefills(GameTestHelper h){
        var l=h.getLevel();var pos=h.absolutePos(new BlockPos(2,2,2));
        l.setBlock(pos.above(),Blocks.AIR.defaultBlockState(),3);
        var room=new PuzzleRoomState(PuzzleRules.Kind.BELL,1);room.solve("minecraft:diamond=2,minecraft:bread=5");
        var data=PuzzleSavedData.get(l);
        h.assertTrue(PuzzleService.depositReward(l,pos,room,data),"Solved room should create its chest");
        var chest=(ChestBlockEntity)l.getBlockEntity(pos.above());
        h.assertTrue(chest!=null&&chest.getItem(0).is(Items.DIAMOND)&&chest.getItem(0).getCount()==2,"Reward contents missing");
        chest.clearContent();l.removeBlock(pos.above(),false);
        h.assertTrue(!PuzzleService.depositReward(l,pos,room,data)&&l.isEmptyBlock(pos.above()),"Breaking or looting a chest must not generate another reward");
        h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=80)
    public static void occupiedChestSpaceIsNotOverwritten(GameTestHelper h){
        var l=h.getLevel();var pos=h.absolutePos(new BlockPos(2,2,2));
        l.setBlock(pos.above(),Blocks.DIAMOND_BLOCK.defaultBlockState(),3);
        var room=new PuzzleRoomState(PuzzleRules.Kind.ELEMENTS,0);room.solve("minecraft:bread=2");
        var data=PuzzleSavedData.get(l);
        h.assertTrue(!PuzzleService.depositReward(l,pos,room,data)&&!room.rewardClaimed(),"Must keep reward pending");
        h.assertTrue(l.getBlockState(pos.above()).is(Blocks.DIAMOND_BLOCK),"Do not erase a player's block");
        l.removeBlock(pos.above(),false);
        h.assertTrue(PuzzleService.depositReward(l,pos,room,data),"Pending chest should succeed after clearing space");
        h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=80)
    public static void rearShellAndSealCannotBeMined(GameTestHelper h){
        var p=h.absolutePos(new BlockPos(2,2,2));
        h.assertTrue(PuzzleBlocks.RUIN_GATE.get().defaultBlockState().getDestroySpeed(h.getLevel(),p)<0,"Gate must be survival-unbreakable");
        h.assertTrue(PuzzleBlocks.RUIN_SHELL.get().defaultBlockState().getDestroySpeed(h.getLevel(),p)<0,"Rear shell must be survival-unbreakable");
        for(int x=-4;x<=4;x++)for(int y=0;y<=3;y++)h.assertTrue(RuinLayout.roleAt(x,y,RuinLayout.BACK_Z)==RuinLayout.Role.WALL,"Back wall has an opening");
        h.succeed();
    }
}
