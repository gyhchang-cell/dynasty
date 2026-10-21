package com.dynasty.client;

import com.dynasty.cod3.ScenicAurora;
import com.dynasty.cod3.ScenicAncientArray;
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

/** Terrain-conforming ritual marks, with only loaded soil surfaces and no world or GL state ownership. */
final class ScenicArrayRenderer {
    static int draw(BufferBuilder buffer,Matrix4f matrix,ClientLevel level,Vec3 origin,Vec3 camera,long seed,
                    double age,int duration,boolean low,double visibility) {
        var columns=new HashMap<Long,Double>();
        var mesh=new ArrayList<>(ScenicAncientArray.mesh(seed,age,duration,origin.distanceTo(camera),low,visibility,(x,z)->{
            int wx=Mth.floor(origin.x+x),wz=Mth.floor(origin.z+z);long key=BlockPos.asLong(wx,0,wz);
            return columns.computeIfAbsent(key,k->ground(level,wx,wz,origin.y));
        }));
        mesh.sort(Comparator.comparingDouble((ScenicAurora.Quad q)->center(q,origin).distanceToSqr(camera)).reversed());
        int count=0;
        for(var q:mesh){
            var center=center(q,origin);double radius=0;
            for(var corner:new ScenicAurora.Point[]{q.a(),q.b(),q.c(),q.d()})radius=Math.max(radius,origin.add(corner.x(),corner.y(),corner.z()).distanceTo(center));
            if(center.distanceTo(camera)<radius+.5)continue;
            double alpha=q.alpha()*Mth.clamp((center.distanceTo(camera)-.5)/1.5,0,1);
            if(alpha<=0)continue;
            for(var p:new ScenicAurora.Point[]{q.a(),q.b(),q.c(),q.a(),q.c(),q.d()})
                buffer.vertex(matrix,(float)(origin.x+p.x()),(float)(origin.y+p.y()),(float)(origin.z+p.z()))
                    .color(q.color()>>16&255,q.color()>>8&255,q.color()&255,(int)(alpha*255)).endVertex();
            count++;
        }
        return count;
    }
    static double ground(ClientLevel level,int x,int z,double originY){return ScenicFireflyRenderer.ground(level,x,z,originY);}
    private static Vec3 center(ScenicAurora.Quad q,Vec3 o){return o.add((q.a().x()+q.c().x())*.5,(q.a().y()+q.c().y())*.5,(q.a().z()+q.c().z())*.5);}
    private ScenicArrayRenderer(){}
}
