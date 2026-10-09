package com.dynasty.dungeon;

import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.AABB;
import java.util.List;

/** One core clock; no per-tile ticks, fluid updates, new entity, or chunk tickets. */
public final class ChenshaMercuryMoat {
    private ChenshaMercuryMoat() {}

    public static boolean exposed(ServerLevel level,BlockPos origin,Player player) {
        if(!player.isAlive()||player.isSpectator()||player.isCreative())return false;
        BlockPos feet=player.blockPosition();
        int x=feet.getX()-origin.getX(), z=feet.getZ()-origin.getZ();
        if(player.getY()<origin.getY()+1||player.getY()>origin.getY()+1.35||!ChenshaVaultLayout.moatCell(x,z))return false;
        BlockPos surface=new BlockPos(feet.getX(),origin.getY(),feet.getZ());
        // Old glass-only vaults are never retroactively turned into hazards.
        return level.hasChunkAt(surface)&&level.getBlockState(surface).is(DungeonContent.MERCURY_CHANNEL.get());
    }

    public static boolean tick(ServerLevel level,DungeonMechanismBlockEntity core,DungeonRoomController room,long time) {
        if(!core.roomId().equals("imperial_vault")||!core.mechanismId().equals("vault_core"))return false;
        BlockPos origin=core.getBlockPos().offset(-24,0,-12);
        var clock=room.mercuryMoat();
        var previous=clock.phase();int before=clock.ticks();
        var area=new AABB(origin.offset(8,1,2),origin.offset(56,3,30));
        List<Player> players=level.getEntitiesOfClass(Player.class,area,p->exposed(level,origin,p));
        if(room.completed()||players.isEmpty()) {
            clock.reset();
            return previous!=clock.phase()||before!=clock.ticks();
        }
        if(clock.phase()==DungeonMechanism.Phase.IDLE) {
            clock.trigger(time);
            for(Player player:players)level.playSound(null,player.blockPosition(),SoundEvents.FIRE_EXTINGUISH,SoundSource.BLOCKS,.4F,.55F);
        } else clock.tickActive(time);
        if(clock.phase()==DungeonMechanism.Phase.WARNING||clock.phase()==DungeonMechanism.Phase.ACTIVE) {
            // The warning and contact use the same exposed list and surface height.
            if(time%4==0)for(Player player:players)
                level.sendParticles(clock.phase()==DungeonMechanism.Phase.WARNING?ParticleTypes.SOUL:ParticleTypes.SOUL_FIRE_FLAME,
                    player.getX(),origin.getY()+1.08,player.getZ(),4,.4,.03,.4,.01);
            if(clock.consumeContact())for(Player player:players)player.hurt(level.damageSources().magic(),2);
        }
        return previous!=clock.phase()||before!=clock.ticks();
    }
}
