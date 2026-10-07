package com.dynasty.blueprint;

import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.TagKey;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.levelgen.structure.Structure;
import java.util.HashSet;

/** Loaded references only. This query cannot acquire a chunk ticket or generate a structure. */
public final class LoadedStructureRegions {
    public static boolean contains(ServerLevel level,BlockPos pos,ResourceLocation tag,int radius){
        if(tag==null)return true;
        var key=TagKey.create(Registries.STRUCTURE,tag);var registry=level.registryAccess().registryOrThrow(Registries.STRUCTURE);
        var visited=new HashSet<Long>();var center=new ChunkPos(pos);int references=0;
        for(int dx=-1;dx<=1;dx++)for(int dz=-1;dz<=1;dz++){
            var chunk=level.getChunkSource().getChunkNow(center.x+dx,center.z+dz);if(chunk==null)continue;
            for(var entry:chunk.getAllStarts().entrySet())if(registry.wrapAsHolder(entry.getKey()).is(key)
                    &&inside(entry.getValue(),pos,radius))return true;
            for(var entry:chunk.getAllReferences().entrySet()){
                if(!registry.wrapAsHolder(entry.getKey()).is(key))continue;
                for(long packed:entry.getValue()){
                    if(++references>64)return false;
                    if(!visited.add(packed))continue;
                    var startChunk=level.getChunkSource().getChunkNow(ChunkPos.getX(packed),ChunkPos.getZ(packed));
                    if(startChunk!=null&&inside(startChunk.getStartForStructure(entry.getKey()),pos,radius))return true;
                }
            }
        }
        return false;
    }
    private static boolean inside(net.minecraft.world.level.levelgen.structure.StructureStart start,BlockPos p,int radius){
        if(start==null||!start.isValid())return false;var b=start.getBoundingBox();
        return p.getX()>=b.minX()-radius&&p.getX()<=b.maxX()+radius&&p.getZ()>=b.minZ()-radius&&p.getZ()<=b.maxZ()+radius
                &&p.getY()>=b.minY()-radius&&p.getY()<=b.maxY()+radius;
    }
    private LoadedStructureRegions(){}
}
