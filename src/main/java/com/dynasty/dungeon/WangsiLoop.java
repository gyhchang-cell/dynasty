package com.dynasty.dungeon;

import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

/** One authored alley loop. Its soul lamp permanently disables it for this city. */
public final class WangsiLoop {
    public static final BlockPos CORE=new BlockPos(22,11,43),LAMP=new BlockPos(20,14,41),ARRIVAL=new BlockPos(22,13,35);
    public static final String ROOM="wangsi_market",KEY="wangsi_soul_lamp";
    private static final String PLAYER_TAG="DynastyWangsiLoop";
    private WangsiLoop(){}
    public static void tick(ServerLevel level,DungeonMechanismBlockEntity be,DungeonRoomController room,long time){
        if(time%4!=0||!be.roomId().equals(ROOM)||!be.getBlockState().is(DungeonContent.LOOP_GATE.get()))return;
        BlockPos origin=be.getBlockPos().subtract(CORE);
        if(!level.dimension().location().toString().equals("dynasty:underworld")
                ||!WangsiStructure.instanceId(level.getSeed(),origin).equals(be.instance()))return;
        String identity=be.instance().toString();
        AABB trigger=new AABB(origin.offset(21,13,43),origin.offset(25,16,45));
        for(var player:level.players()){
            var data=player.getPersistentData();var pending=data.getCompound(PLAYER_TAG);
            boolean ours=identity.equals(pending.getString("Instance"));
            if(!player.isAlive()||player.isCreative()||player.isSpectator()||player.isPassenger()
                    ||!trigger.intersects(player.getBoundingBox())||room.shortcutOpen(KEY)){
                if(ours)data.remove(PLAYER_TAG);
                continue;
            }
            long age=time-pending.getLong("Since");
            if(!ours||age<0||age>40){
                pending=new CompoundTag();pending.putString("Instance",identity);pending.putLong("Since",time);data.put(PLAYER_TAG,pending);
                player.displayClientMessage(Component.translatable("message.dynasty.wangsi.loop_warning"),true);continue;
            }
            if(age<20)continue;
            BlockPos dest=origin.offset(ARRIVAL);Vec3 target=Vec3.atBottomCenterOf(dest);
            AABB landing=player.getBoundingBox().move(target.subtract(player.position()));
            boolean loaded=true;
            for(int x=(int)Math.floor(landing.minX)>>4;x<=(int)Math.floor(landing.maxX)>>4;x++)
                for(int z=(int)Math.floor(landing.minZ)>>4;z<=(int)Math.floor(landing.maxZ)>>4;z++)
                    loaded&=level.getChunkSource().getChunkNow(x,z)!=null;
            if(!loaded||!level.getWorldBorder().isWithinBounds(landing)||!level.noCollision(player,landing)
                    ||!level.getBlockState(dest.below()).isFaceSturdy(level,dest.below(),net.minecraft.core.Direction.UP)
                    ||!level.getFluidState(dest).isEmpty())continue;
            player.teleportTo(target.x,target.y,target.z);player.setDeltaMovement(Vec3.ZERO);player.fallDistance=0;
            data.remove(PLAYER_TAG);
            player.displayClientMessage(Component.translatable("message.dynasty.wangsi.loop_return"),true);
        }
    }
}
