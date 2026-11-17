package com.dynasty.cod3;

import com.dynasty.structure.ScenicFireTreeStructure;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.server.level.*;
import net.minecraft.world.level.*;
import net.minecraft.world.level.levelgen.structure.StructureStart;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.network.PacketDistributor;
import java.util.*;

/** Existing loaded StructureStarts only; never force-load chunks or create a tree for an observer. */
@Mod.EventBusSubscriber(modid="dynasty")
public final class ScenicFireTreeSite {
    public static boolean night(long dayTime,double rain){long t=Math.floorMod(dayTime,24000);return t>=13000&&t<23000&&rain<=.01;}
    public static Optional<BlockPos> originNear(ServerLevel level,BlockPos viewer){
        if(level.dimension()!=Level.OVERWORLD)return Optional.empty();
        var structure=level.registryAccess().registryOrThrow(Registries.STRUCTURE).get(ScenicFireTreeStructure.ID);
        if(structure==null)return Optional.empty();
        var visited=new HashSet<Long>();BlockPos best=null;double nearest=Double.MAX_VALUE;
        int cx=viewer.getX()>>4,cz=viewer.getZ()>>4;
        for(int dx=-4;dx<=4;dx++)for(int dz=-4;dz<=4;dz++){
            var chunk=level.getChunkSource().getChunkNow(cx+dx,cz+dz);if(chunk==null)continue;
            var candidates=new ArrayList<StructureStart>();var own=chunk.getStartForStructure(structure);if(own!=null)candidates.add(own);
            for(long ref:chunk.getReferencesForStructure(structure))if(visited.add(ref)){
                var startChunk=level.getChunkSource().getChunkNow(ChunkPos.getX(ref),ChunkPos.getZ(ref));
                if(startChunk!=null){var start=startChunk.getStartForStructure(structure);if(start!=null)candidates.add(start);}
            }
            for(var start:candidates)if(start.isValid()){
                var box=start.getBoundingBox();var origin=new BlockPos(box.minX(),box.minY(),box.minZ());
                double d=viewer.distSqr(origin.offset(24,20,24));
                if(d<160*160&&d<nearest){nearest=d;best=origin;}
            }
        }
        return Optional.ofNullable(best);
    }
    public static Cod3VisualPacket packet(ServerLevel level,BlockPos origin){
        long now=level.getGameTime(),start=now-Math.floorMod(now,1200)-200;
        // Overlapping 1200-tick refresh windows avoid a lifetime fade/gap. Render clock is world time.
        return new Cod3VisualPacket(level.dimension().location().toString(),15,-1,origin.asLong()^level.getSeed(),start,2400,1,
            Vec3.atLowerCornerOf(origin),new Vec3(0,0,1),"scenic_13",(int)(now-start));
    }
    @SubscribeEvent public static void tick(TickEvent.PlayerTickEvent event){
        if(event.phase!=TickEvent.Phase.END||!(event.player instanceof ServerPlayer player)||player.tickCount%100!=0||!player.isAlive())return;
        var level=player.serverLevel();if(!night(level.getDayTime(),level.getRainLevel(1)))return;
        originNear(level,player.blockPosition()).ifPresent(origin->com.dynasty.network.DynastyNetwork.CHANNEL.send(PacketDistributor.PLAYER.with(()->player),packet(level,origin)));
    }
    private ScenicFireTreeSite(){}
}
