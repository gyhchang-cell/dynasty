package com.dynasty.cod3;

import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.protocol.game.ClientboundSoundPacket;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import javax.annotation.Nullable;

/** Quiet, player-local ice creaks; no block changes, particles, entities or saved timers. */
@Mod.EventBusSubscriber(modid="dynasty")
public final class ScenicIceAmbience {
    private static final ResourceLocation STRUCTURE=new ResourceLocation("dynasty","scenic_ice_bloom");

    @Nullable public static ClientboundSoundPacket packetAt(ServerLevel level,BlockPos at,long seed){
        if(level.dimension()!=Level.OVERWORLD||at.getY()>=0||!level.hasChunkAt(at))return null;
        var structure=level.registryAccess().registryOrThrow(Registries.STRUCTURE).get(STRUCTURE);
        if(structure==null)return null;
        // StructureManager may follow a reference to a start chunk: never generate that chunk for audio.
        var references=level.getChunkAt(at).getReferencesForStructure(structure);
        if(references.isEmpty())return null;
        for(long ref:references)if(!level.hasChunk(ChunkPos.getX(ref),ChunkPos.getZ(ref)))return null;
        var start=level.structureManager().getStructureWithPieceAt(at,structure);
        if(!start.isValid()||!level.isEmptyBlock(at))return null;
        BlockPos nearest=null;double distance=Double.MAX_VALUE;
        for(var pos:BlockPos.betweenClosed(at.offset(-4,-4,-4),at.offset(4,4,4))){
            if(!level.hasChunkAt(pos))continue;
            var state=level.getBlockState(pos);
            if(!state.is(Blocks.BLUE_ICE)&&!state.is(Blocks.PACKED_ICE))continue;
            double d=pos.distSqr(at);
            if(d<distance){nearest=pos.immutable();distance=d;}
        }
        if(nearest==null)return null;
        return new ClientboundSoundPacket(BuiltInRegistries.SOUND_EVENT.wrapAsHolder(SoundEvents.GLASS_HIT),SoundSource.AMBIENT,
                nearest.getX()+.5,nearest.getY()+.5,nearest.getZ()+.5,.12f,.7f,seed);
    }

    @SubscribeEvent public static void tick(TickEvent.PlayerTickEvent event){
        if(event.phase!=TickEvent.Phase.END||!(event.player instanceof ServerPlayer player)
                ||!player.isAlive()||player.isSpectator()||player.tickCount%240!=0)return;
        var sound=packetAt(player.serverLevel(),player.blockPosition(),player.level().getGameTime()^player.getUUID().getLeastSignificantBits());
        if(sound!=null)player.connection.send(sound);
    }
    private ScenicIceAmbience(){}
}
