package com.dynasty;

import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.GameType;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.common.util.FakePlayer;
import net.minecraftforge.event.level.BlockEvent;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;

@GameTestHolder(Dynasty.MODID)
@PrefixGameTestTemplate(false)
public final class GuanYuGuardianGameTests {
    @GameTest(template="bow_ritual_test",timeoutTicks=30)
    public static void silhouetteClearRespectsContainersProtectionAndFloor(GameTestHelper h) {
        var level=h.getLevel();
        var player=new FakePlayer(level,new com.mojang.authlib.GameProfile(java.util.UUID.randomUUID(),"guanyu-test"));
        level.addNewPlayer(player);player.setGameMode(GameType.SURVIVAL);
        player.setPos(Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(8,2,11))));player.setYRot(0);
        BlockPos stone=h.absolutePos(new BlockPos(8,7,7));
        BlockPos chest=h.absolutePos(new BlockPos(8,8,7));
        BlockPos bedrock=h.absolutePos(new BlockPos(8,9,7));
        BlockPos protectedBlock=h.absolutePos(new BlockPos(7,7,7));
        BlockPos outside=h.absolutePos(new BlockPos(13,7,7));
        BlockPos floor=h.absolutePos(new BlockPos(8,1,7));
        level.setBlockAndUpdate(stone,Blocks.STONE.defaultBlockState());
        level.setBlockAndUpdate(chest,Blocks.CHEST.defaultBlockState());
        level.setBlockAndUpdate(bedrock,Blocks.BEDROCK.defaultBlockState());
        for(var p:new BlockPos[]{protectedBlock,outside,floor})level.setBlockAndUpdate(p,Blocks.STONE.defaultBlockState());
        java.util.function.Consumer<BlockEvent.BreakEvent> protect=e->{if(e.getPlayer()==player&&e.getPos().equals(protectedBlock))e.setCanceled(true);};
        MinecraftForge.EVENT_BUS.addListener(protect);
        try {
            GuanYuGuardian.clearSpace(level,player,.1);
            h.assertTrue(level.getBlockState(stone).is(Blocks.STONE),"Unformed upper body must not destroy blocks yet");
            GuanYuGuardian.clearSpace(level,player,1);
            h.assertTrue(level.getBlockState(stone).isAir(),"Body obstruction must clear");
            h.assertTrue(level.getBlockState(chest).is(Blocks.CHEST),"Container must survive");
            h.assertTrue(level.getBlockState(bedrock).is(Blocks.BEDROCK),"Unbreakable blocks must survive");
            h.assertTrue(level.getBlockState(protectedBlock).is(Blocks.STONE),"Protection cancellation must be honored");
            h.assertTrue(level.getBlockState(outside).is(Blocks.STONE),"Outside silhouette must survive");
            h.assertTrue(level.getBlockState(floor).is(Blocks.STONE),"Supporting floor must survive");
        }finally{MinecraftForge.EVENT_BUS.unregister(protect);player.discard();}
        h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=30)
    public static void spectatorCannotClearBlocks(GameTestHelper h) {
        var level=h.getLevel();
        var player=new FakePlayer(level,new com.mojang.authlib.GameProfile(java.util.UUID.randomUUID(),"guanyu-spectate"));
        level.addNewPlayer(player);player.setGameMode(GameType.SPECTATOR);
        player.setPos(Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(8,2,11))));player.setYRot(0);
        BlockPos stone=h.absolutePos(new BlockPos(8,7,7));level.setBlockAndUpdate(stone,Blocks.STONE.defaultBlockState());
        GuanYuGuardian.clearSpace(level,player,1);
        h.assertTrue(level.getBlockState(stone).is(Blocks.STONE),"Spectator must never clear a structure");
        player.discard();h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=30)
    public static void remodeledGuardianClearsBehindInAllFourDirections(GameTestHelper h) {
        var level=h.getLevel();
        var player=new FakePlayer(level,new com.mojang.authlib.GameProfile(java.util.UUID.randomUUID(),"guanyu-facing"));
        level.addNewPlayer(player);player.setGameMode(GameType.SURVIVAL);
        player.setPos(Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(8,2,8))));
        try {
            for(float yaw:new float[]{0,90,180,270}) {
                player.setYRot(yaw);
                Vec3 origin=GuanYuAvatarShape.origin(player.position(),yaw);
                Vec3 forward=HouyiAvatarShape.forward(yaw),right=new Vec3(forward.z,0,-forward.x);
                BlockPos torso=BlockPos.containing(origin.add(0,5,0));
                BlockPos outside=BlockPos.containing(origin.add(right.scale(3.7)).add(0,5,0));
                level.setBlockAndUpdate(torso,Blocks.STONE.defaultBlockState());
                level.setBlockAndUpdate(outside,Blocks.STONE.defaultBlockState());
                GuanYuGuardian.clearSpace(level,player,1);
                h.assertTrue(level.getBlockState(torso).isAir(),"Torso obstruction must clear behind yaw "+yaw);
                h.assertTrue(level.getBlockState(outside).is(Blocks.STONE),"Outside silhouette must survive yaw "+yaw);
                level.setBlockAndUpdate(outside,Blocks.AIR.defaultBlockState());
            }
        } finally {player.discard();}
        h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=30)
    public static void remodeledSilhouetteKeepsClearBudgetAndFluids(GameTestHelper h) {
        var level=h.getLevel();
        var player=new FakePlayer(level,new com.mojang.authlib.GameProfile(java.util.UUID.randomUUID(),"guanyu-budget"));
        level.addNewPlayer(player);player.setGameMode(GameType.SURVIVAL);
        player.setPos(Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(8,2,11))));player.setYRot(0);
        var stones=new java.util.ArrayList<BlockPos>();
        Vec3 origin=GuanYuAvatarShape.origin(player.position(),0);
        BlockPos water=BlockPos.containing(origin.add(0,5,0));
        try {
            for(BlockPos at:BlockPos.betweenClosed(BlockPos.containing(origin.add(-4,0,-2)),BlockPos.containing(origin.add(3,9,2)))) {
                BlockPos stable=at.immutable();
                if(stable.equals(water))continue;
                level.setBlockAndUpdate(stable,Blocks.STONE.defaultBlockState());stones.add(stable);
            }
            level.setBlockAndUpdate(water,Blocks.WATER.defaultBlockState());
            GuanYuGuardian.clearSpace(level,player,1);
            long removed=stones.stream().filter(at->level.getBlockState(at).isAir()).count();
            h.assertTrue(removed>0&&removed<=64,"Detailed model must retain the 64-block clear budget, actual="+removed);
            h.assertTrue(level.getBlockState(water).is(Blocks.WATER),"Water inside the new torso must not be removed");
        } finally {player.discard();}
        h.succeed();
    }
}
