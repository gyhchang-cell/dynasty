package com.dynasty;

import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.common.ForgeHooks;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.event.server.ServerStoppedEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.*;

/** Holds the guardian behind the wielder; only clears ordinary blocks intersecting its shape. */
@Mod.EventBusSubscriber(modid=Dynasty.MODID)
public final class GuanYuGuardian {
    private static final Map<UUID,Integer> HELD=new HashMap<>();
    @SubscribeEvent
    public static void tick(TickEvent.PlayerTickEvent event) {
        if(event.phase!=TickEvent.Phase.END || !(event.player instanceof ServerPlayer player))return;
        if(!player.isAlive() || player.isSpectator() || !player.getMainHandItem().is(DynastyWeapons.QINGLONG_DAO.get())) {
            HELD.remove(player.getUUID());return;
        }
        int ticks=HELD.merge(player.getUUID(),1,(a,b)->Math.min(40,a+b));
        if(player.tickCount%10==0)clearSpace(player.serverLevel(),player,Math.min(1,ticks/40.0));
    }
    static void clearSpace(ServerLevel level,ServerPlayer player,double formed) {
        if(!player.mayBuild() || player.isSpectator() || formed<=0)return;
        Vec3 forward=HouyiAvatarShape.forward(player.getYRot()),right=new Vec3(forward.z,0,-forward.x);
        Vec3 origin=GuanYuAvatarShape.origin(player.position(),player.getYRot());
        int removed=0;
        for(BlockPos pos:BlockPos.betweenClosed(BlockPos.containing(origin.add(-4.5,0,-4.5)),
                BlockPos.containing(origin.add(4.5,GuanYuAvatarShape.HEIGHT*Math.min(1,formed),4.5)))) {
            if(!level.hasChunkAt(pos) || !level.mayInteract(player,pos))continue;
            Vec3 local=Vec3.atCenterOf(pos).subtract(origin);
            if(!GuanYuAvatarShape.contains(local.dot(right),local.y,local.dot(forward),formed))continue;
            var state=level.getBlockState(pos);
            if(state.isAir() || state.hasBlockEntity() || !state.getFluidState().isEmpty()
                    || state.getDestroySpeed(level,pos)<0)continue;
            BlockPos stable=pos.immutable();
            if(ForgeHooks.onBlockBreakEvent(level,player.gameMode.getGameModeForPlayer(),player,stable)>=0
                    && level.destroyBlock(stable,true,player) && ++removed>=64)break;
        }
    }
    @SubscribeEvent public static void logout(PlayerEvent.PlayerLoggedOutEvent event){HELD.remove(event.getEntity().getUUID());}
    @SubscribeEvent public static void stop(ServerStoppedEvent event){HELD.clear();}
    private GuanYuGuardian(){}
}
