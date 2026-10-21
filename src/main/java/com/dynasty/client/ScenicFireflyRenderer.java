package com.dynasty.client;

import com.dynasty.cod3.ScenicAurora;
import com.dynasty.cod3.ScenicFireflies;
import com.mojang.blaze3d.vertex.BufferBuilder;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.core.BlockPos;
import net.minecraft.tags.BlockTags;
import net.minecraft.util.Mth;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.Vec3;
import org.joml.Matrix4f;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;

/** Uses the validated loaded-column sampler; grass/moss only, so buildings cannot emit green roots. */
final class ScenicFireflyRenderer {
    static int draw(BufferBuilder buffer,Matrix4f matrix,ClientLevel level,Vec3 origin,Vec3 camera,long seed,
                    double age,int duration,boolean low,double visibility) {
        var columns=new HashMap<Long,Double>();
        var mesh=new ArrayList<>(ScenicFireflies.mesh(seed,age,duration,origin.distanceTo(camera),low,visibility,(x,z)->{
            int wx=Mth.floor(origin.x+x),wz=Mth.floor(origin.z+z);long key=BlockPos.asLong(wx,0,wz);
            return columns.computeIfAbsent(key,k->ground(level,wx,wz,origin.y));
        }));
        mesh.sort(Comparator.comparingDouble((ScenicAurora.Quad q)->center(q,origin).distanceToSqr(camera)).reversed());
        int count=0;
        for(var q:mesh){
            double alpha=q.alpha()*Mth.clamp((center(q,origin).distanceTo(camera)-.5)/1.5,0,1);
            if(alpha<=0)continue;
            for(var p:new ScenicAurora.Point[]{q.a(),q.b(),q.c(),q.a(),q.c(),q.d()})
                buffer.vertex(matrix,(float)(origin.x+p.x()),(float)(origin.y+p.y()),(float)(origin.z+p.z()))
                    .color(q.color()>>16&255,q.color()>>8&255,q.color()&255,(int)(alpha*255)).endVertex();
            count++;
        }
        return count;
    }
    static double ground(ClientLevel level,int x,int z,double originY){
        var column=ScenicLeafRenderer.column(level,x,z,originY);if(column==null)return Double.NaN;
        var pos=BlockPos.containing(x,originY+column.ground()-.01,z);var block=level.getBlockState(pos);
        return (block.is(BlockTags.DIRT)||block.is(Blocks.MOSS_BLOCK))&&block.getFluidState().isEmpty()?column.ground():Double.NaN;
    }
    private static Vec3 center(ScenicAurora.Quad q,Vec3 o){return o.add((q.a().x()+q.c().x())*.5,(q.a().y()+q.c().y())*.5,(q.a().z()+q.c().z())*.5);}
    private ScenicFireflyRenderer(){}
}
