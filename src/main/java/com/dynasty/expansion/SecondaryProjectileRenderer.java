package com.dynasty.expansion;

import com.mojang.blaze3d.vertex.*;
import com.mojang.math.Axis;
import net.minecraft.client.renderer.*;
import net.minecraft.client.renderer.entity.*;
import net.minecraft.resources.ResourceLocation;

/** Small world-space solids, rather than arrow skins or screen effects. */
public final class SecondaryProjectileRenderer extends EntityRenderer<SecondaryProjectile> {
    public SecondaryProjectileRenderer(EntityRendererProvider.Context context){super(context);}
    @Override public ResourceLocation getTextureLocation(SecondaryProjectile p){return net.minecraft.client.renderer.texture.TextureAtlas.LOCATION_BLOCKS;}
    @Override public void render(SecondaryProjectile p,float yaw,float partial,PoseStack stack,MultiBufferSource buffers,int light){
        drawSkill(p.kind(),p.tickCount+partial,p.getYRot(),stack,buffers);super.render(p,yaw,partial,stack,buffers,light);
    }
    public static void drawSkill(int kind,float age,float yaw,PoseStack stack,MultiBufferSource buffers){
        stack.pushPose();
        stack.mulPose(Axis.YP.rotationDegrees(kind==SecondaryProjectile.WATER?yaw:age*(kind==SecondaryProjectile.STONE?11:4)));
        var vertex=buffers.getBuffer(RenderType.lightning());var matrix=stack.last().pose();
        int color=switch(kind){case SecondaryProjectile.LIGHT->0xF8D980;case SecondaryProjectile.WATER->0x66CFE9;case SecondaryProjectile.STONE->0x8A8176;default->0x74A543;};
        float r=kind==SecondaryProjectile.LIGHT?.18F:kind==SecondaryProjectile.WATER?.13F:.11F;
        float height=kind==SecondaryProjectile.SEED?.25F:r;
        for(int side=0;side<4;side++){
            double a=side*Math.PI/2,b=(side+1)*Math.PI/2;
            float x=(float)Math.cos(a)*r,z=(float)Math.sin(a)*r,xx=(float)Math.cos(b)*r,zz=(float)Math.sin(b)*r;
            face(vertex,matrix,color,0,height,0,x,0,z,xx,0,zz);
            face(vertex,matrix,color,0,-height,0,xx,0,zz,x,0,z);
        }
        // Water has an axial jet; a lantern core has two crossing orbital bands.
        if(kind==SecondaryProjectile.WATER){var m=stack.last().pose();for(int i=0;i<3;i++)face(vertex,m,color,-r,0,-i*.13F,r,0,-i*.13F,0,r,-(i+1)*.13F);}
        if(kind==SecondaryProjectile.LIGHT)for(int axis=0;axis<2;axis++)for(int i=0;i<12;i++){
            double a=i*Math.PI/6,b=(i+1)*Math.PI/6;
            float x=(float)Math.cos(a)*r*1.6F,y=(float)Math.sin(a)*r*1.6F,xx=(float)Math.cos(b)*r*1.6F,yy=(float)Math.sin(b)*r*1.6F;
            face(vertex,matrix,color,x,axis==0?y:0,axis==0?0:y,xx,axis==0?yy:0,axis==0?0:yy,x*.93F,axis==0?y*.93F:0,axis==0?0:y*.93F);
        }
        stack.popPose();
    }
    private static void face(VertexConsumer v,org.joml.Matrix4f m,int color,float ax,float ay,float az,float bx,float by,float bz,float cx,float cy,float cz){
        for(float[] p:new float[][]{{ax,ay,az},{bx,by,bz},{cx,cy,cz},{cx,cy,cz}})
            v.vertex(m,p[0],p[1],p[2]).color((color>>16)&255,(color>>8)&255,color&255,220).endVertex();
    }
}
