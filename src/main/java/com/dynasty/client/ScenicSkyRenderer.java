package com.dynasty.client;

import com.dynasty.cod3.ScenicAurora;
import com.dynasty.cod3.ScenicSunHalo;
import com.mojang.blaze3d.vertex.BufferBuilder;
import net.minecraft.world.phys.Vec3;
import org.joml.Matrix4f;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

/** Appends only to the caller's POSITION_COLOR triangles; owns no GL state, particles or cached world. */
final class ScenicSkyRenderer {
    static int draw(BufferBuilder buffer,Matrix4f matrix,Vec3 origin,Vec3 camera,int number,long seed,
                    double age,int duration,boolean low,double visibility) {
        double distance=origin.distanceTo(camera);
        var mesh=new ArrayList<>(number==20?com.dynasty.cod3.ScenicMeteors.mesh(seed,age,duration,distance,low,visibility):ScenicAurora.mesh(seed,age,duration,distance,low,visibility));
        return append(buffer,matrix,origin,camera,mesh);
    }
    static int drawSun(BufferBuilder buffer,Matrix4f matrix,Vec3 origin,Vec3 camera,long seed,
                       double age,int duration,boolean low,double visibility,double sunAngle) {
        var mesh=new ArrayList<>(ScenicSunHalo.mesh(seed,age,duration,origin.distanceTo(camera),low,visibility)
            .stream().map(q->ScenicSunHalo.solar(q,sunAngle)).toList());
        // A solar optical phenomenon belongs to the sky direction, not a floating object above an anchor.
        // Keep the region/clock server-owned, while each observer sees it aligned with the same vanilla sun.
        return append(buffer,matrix,camera,camera,mesh);
    }
    static int drawSilverfall(BufferBuilder buffer,Matrix4f matrix,Vec3 origin,Vec3 camera,long seed,
                              double age,int duration,boolean low,double visibility) {
        return append(buffer,matrix,origin,camera,new ArrayList<>(com.dynasty.cod3.ScenicSilverfall.mesh(
            seed,age,duration,origin.distanceTo(camera),low,visibility)));
    }
    static int append(BufferBuilder buffer,Matrix4f matrix,Vec3 origin,Vec3 camera,List<ScenicAurora.Quad> mesh) {
        // Alpha surfaces must be sorted for both sides and different observers.
        mesh.sort(Comparator.comparingDouble((ScenicAurora.Quad q)->center(q,origin).distanceToSqr(camera)).reversed());
        int drawn=0;
        for(var q:mesh) {
            var center=center(q,origin);
            // Smoothly remove nearby faces before they can become a screen-filling transparent wall.
            double alpha=q.alpha()*Math.max(0,Math.min(1,(center.distanceTo(camera)-12)/16));
            if(alpha<=0)continue;
            // Conservative sphere check includes the interior, rather than testing just vertices.
            double radius=0;
            for(var corner:new ScenicAurora.Point[]{q.a(),q.b(),q.c(),q.d()})radius=Math.max(radius,point(corner,origin).distanceTo(center));
            if(center.distanceTo(camera)<radius+2)continue;
            for(var p:new ScenicAurora.Point[]{q.a(),q.b(),q.c(),q.a(),q.c(),q.d()}) {
                var world=point(p,origin);
                buffer.vertex(matrix,(float)world.x,(float)world.y,(float)world.z)
                    .color(q.color()>>16&255,q.color()>>8&255,q.color()&255,(int)(alpha*255)).endVertex();
            }
            drawn++;
        }
        return drawn;
    }
    private static Vec3 point(ScenicAurora.Point p,Vec3 origin){return origin.add(p.x(),p.y(),p.z());}
    private static Vec3 center(ScenicAurora.Quad q,Vec3 origin){return origin.add((q.a().x()+q.c().x())*.5,(q.a().y()+q.c().y())*.5,(q.a().z()+q.c().z())*.5);}
    private ScenicSkyRenderer() {}
}
