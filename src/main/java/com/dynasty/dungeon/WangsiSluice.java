package com.dynasty.dungeon;

import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.block.Blocks;

/** Drain a sealed branch sump, never the main river or neighbouring chunks. */
public final class WangsiSluice {
    public static final BlockPos CORE=new BlockPos(15,11,88),PUMP=new BlockPos(14,17,84);
    public static final String ROOM="wangsi_sluice",DRAINED="wangsi_sump_drained";
    private WangsiSluice(){}
    public static boolean tick(ServerLevel level,DungeonMechanismBlockEntity be,DungeonRoomController room){
        if(!be.roomId().equals(ROOM)||!be.mechanismId().equals("wangsi_sluice_core")||!room.completed()||room.shortcutOpen(DRAINED))return false;
        BlockPos origin=be.getBlockPos().subtract(CORE);
        if(!level.dimension().location().toString().equals("dynasty:underworld")
                ||!WangsiStructure.instanceId(level.getSeed(),origin).equals(be.instance()))return false;
        // Require the whole small chamber loaded before changing even one water cell.
        for(int x=14;x<=16;x++)for(int z=94;z<=99;z++)
            if(level.getChunkSource().getChunkNow((origin.getX()+x)>>4,(origin.getZ()+z)>>4)==null)return false;
        int budget=16;boolean remains=false;
        for(int y=6;y<=8;y++)for(int z=94;z<=99;z++)for(int x=14;x<=16;x++){
            BlockPos p=origin.offset(x,y,z);var state=level.getBlockState(p);
            if(state.is(Blocks.WATER)){
                if(budget>0){
                    if(!level.setBlock(p,Blocks.AIR.defaultBlockState(),2))return false;
                    budget--;
                }
                else remains=true;
            }else if(!state.isAir())return false; // Never erase a player/mod replacement.
        }
        return !remains&&room.unlockShortcut(DRAINED);
    }
}
