package com.dynasty.client;

import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;

/** Existing rune language, depth-tested behind the new cuboid storm regalia. */
final class BossCuboidAura {
    static void draw(PoseStack pose,MultiBufferSource buffers,float age,float fold){
        // Called in the body bone's space. Fold the rune plane with the actual
        // storm rings during death, keeping every live rune and its depth test.
        pose.pushPose();
        float yCenter=1.501f*1.28f-.33f*1.28f,z=-.42f*1.28f;
        pose.translate(0,yCenter,z);pose.mulPose(com.mojang.math.Axis.YP.rotation(fold));pose.translate(0,-yCenter,-z);
        var sink=buffers.getBuffer(RenderType.debugQuads());var matrix=pose.last().pose();
        new BowSigilGeometry(1,(x1,y1,x2,y2,width)->{
            double dx=x2-x1,dy=y2-y1,len=Math.hypot(dx,dy);if(len<1e-8)return;
            double radius=1.08*1.28,w=Math.max(width,.0025)*radius,nx=-dy/len*w,ny=dx/len*w;
            vertex(sink,matrix,x1*radius+nx,yCenter-(y1*radius+ny),z);
            vertex(sink,matrix,x2*radius+nx,yCenter-(y2*radius+ny),z);
            vertex(sink,matrix,x2*radius-nx,yCenter-(y2*radius-ny),z);
            vertex(sink,matrix,x1*radius-nx,yCenter-(y1*radius-ny),z);
        }).draw(2,age);
        pose.popPose();
    }
    private static void vertex(com.mojang.blaze3d.vertex.VertexConsumer sink,org.joml.Matrix4f matrix,double x,double y,float z){
        sink.vertex(matrix,(float)x,(float)y,z).color(153,223,255,155).endVertex();
    }
}
