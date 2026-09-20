package com.dynasty.client;

import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.entity.layers.RenderLayer;
import net.minecraft.world.entity.Mob;

/** Small, depth-tested seals attached to the creature, never a screen-space overlay. */
public final class DynastyAuraLayer<T extends Mob> extends RenderLayer<T,DynastyHumanoidModel<T>> {
    private final int style;
    public DynastyAuraLayer(RenderLayerParent<T,DynastyHumanoidModel<T>> parent,int style){super(parent);this.style=style;}
    @Override public void render(PoseStack pose,MultiBufferSource buffers,int light,T entity,float swing,
            float amount,float partial,float age,float yaw,float pitch) {
        if(!entity.isInvisible())drawSeal(pose,buffers,style,age);
    }
    public static void drawSeal(PoseStack pose,MultiBufferSource buffers,int style,float age) {
        if(style<=0||style>4)return;
        boolean boss=style<=2;
        float radius=boss?1.08F:.72F;
        int color=switch(style){case 1->0xffd575;case 2->0x99dfff;case 3->0x88efba;default->0x809fff;};
        int alpha=boss?155:95;
        var sink=buffers.getBuffer(RenderType.debugQuads());
        var matrix=pose.last().pose();
        var sigil=new BowSigilGeometry(1,(x1,y1,x2,y2,width)-> {
            double dx=x2-x1,dy=y2-y1,len=Math.hypot(dx,dy);
            if(len<1e-8)return;
            double w=Math.max(width,.0025)*radius,nx=-dy/len*w,ny=dx/len*w;
            float z=.42F;
            vertex(sink,matrix,x1*radius+nx,y1*radius+ny,z,color,alpha);
            vertex(sink,matrix,x2*radius+nx,y2*radius+ny,z,color,alpha);
            vertex(sink,matrix,x2*radius-nx,y2*radius-ny,z,color,alpha);
            vertex(sink,matrix,x1*radius-nx,y1*radius-ny,z,color,alpha);
        });
        if(boss)sigil.draw(2,age);else sigil.drawBagua(age);
    }
    private static void vertex(com.mojang.blaze3d.vertex.VertexConsumer sink,org.joml.Matrix4f matrix,
                               double x,double y,float z,int color,int alpha) {
        sink.vertex(matrix,(float)x,(float)(y+.33),z)
            .color((color>>16)&255,(color>>8)&255,color&255,alpha).endVertex();
    }
}
