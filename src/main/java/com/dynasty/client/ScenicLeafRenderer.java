package com.dynasty.client;

import com.dynasty.cod3.ScenicAurora;
import com.dynasty.cod3.ScenicGoldenLeaves;
import com.mojang.blaze3d.vertex.BufferBuilder;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.core.BlockPos;
import net.minecraft.util.Mth;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.Vec3;
import org.joml.Matrix4f;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;

/** Terrain-aware foliage: no blocks, chunk requests, game entities or persistent particle queue. */
final class ScenicLeafRenderer {
    static int draw(BufferBuilder buffer,Matrix4f matrix,ClientLevel level,Vec3 origin,Vec3 camera,long seed,
                    double age,int duration,boolean low,double visibility) {
        var columns=new HashMap<Long,ScenicGoldenLeaves.Column>();
        var mesh=new ArrayList<>(ScenicGoldenLeaves.mesh(seed,age,duration,origin.distanceTo(camera),low,visibility,(x,z)->{
            int wx=Mth.floor(origin.x+x),wz=Mth.floor(origin.z+z);
            long key=BlockPos.asLong(wx,0,wz);
            if(!columns.containsKey(key))columns.put(key,column(level,wx,wz,origin.y));
            return columns.get(key);
        }));
        mesh.sort(Comparator.comparingDouble((ScenicAurora.Quad q)->center(q,origin).distanceToSqr(camera)).reversed());
        int count=0;
        for(var q:mesh) {
            Vec3 at=center(q,origin);
            double alpha=q.alpha()*Mth.clamp((at.distanceTo(camera)-.5)/1.5,0,1);
            if(alpha<=0)continue;
            float light=.3f+.7f*level.getMaxLocalRawBrightness(BlockPos.containing(at))/15f;
            for(var p:new ScenicAurora.Point[]{q.a(),q.b(),q.c(),q.a(),q.c(),q.d()})
                buffer.vertex(matrix,(float)(origin.x+p.x()),(float)(origin.y+p.y()),(float)(origin.z+p.z()))
                    .color((int)((q.color()>>16&255)*light),(int)((q.color()>>8&255)*light),(int)((q.color()&255)*light),(int)(alpha*255)).endVertex();
            count++;
        }
        return count;
    }
    static ScenicGoldenLeaves.Column column(ClientLevel level,int x,int z,double originY) {
        if(!level.hasChunk(x>>4,z>>4))return null;
        int canopy=level.getHeight(Heightmap.Types.MOTION_BLOCKING,x,z);
        var pos=new BlockPos.MutableBlockPos(x,canopy-1,z);
        if(!level.getBlockState(pos).is(net.minecraft.tags.BlockTags.LEAVES))
            return new ScenicGoldenLeaves.Column(canopy-originY,canopy-originY);
        // NO_LEAVES is LIVE_WORLD, not CLIENT: chunk packets do not prime it.
        // Inspect actual loaded blocks so roofs and refreshed chunks stop falling leaves.
        int bottom=Math.max(level.getMinBuildHeight(),canopy-96);
        for(int y=canopy-2;y>=bottom;y--) {
            pos.setY(y);
            var block=level.getBlockState(pos);
            if(!block.is(net.minecraft.tags.BlockTags.LEAVES)&&(block.blocksMotion()||!block.getFluidState().isEmpty()))
                return new ScenicGoldenLeaves.Column(y+1-originY,canopy-originY);
        }
        return null; // No confirmed landing surface within the bounded scan.
    }
    private static Vec3 center(ScenicAurora.Quad q,Vec3 o){return o.add((q.a().x()+q.c().x())*.5,(q.a().y()+q.c().y())*.5,(q.a().z()+q.c().z())*.5);}
    private ScenicLeafRenderer() {}
}
