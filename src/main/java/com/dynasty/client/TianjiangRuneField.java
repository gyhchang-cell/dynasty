package com.dynasty.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.renderer.MultiBufferSource;
import org.joml.Matrix4f;
import org.joml.Vector3f;

/** Original extruded light calligraphy and drifting facets. Client quads, never entities/colliders. */
final class TianjiangRuneField {
    // Broken knots, hooked spirals and branching strokes; no text font or borrowed glyph atlas.
    private static final float[][][][] SIGNS={
        {{{-.30f,.16f},{-.30f,.34f},{-.09f,.34f},{.08f,.16f},{.08f,-.08f},{-.10f,-.25f},{-.10f,-.40f}},
         {{-.17f,.08f},{-.05f,.08f},{-.05f,.20f}},{{.23f,.35f},{.36f,.22f},{.24f,.09f}},
         {{.09f,-.11f},{.30f,-.11f},{.30f,-.29f},{.17f,-.29f}},{{-.33f,-.12f},{-.33f,-.30f},{-.23f,-.30f}}},
        {{{-.30f,.28f},{-.10f,.28f},{-.10f,.07f},{.13f,.07f},{.13f,-.15f},{-.07f,-.15f},{-.07f,-.35f}},
         {{.04f,.41f},{.25f,.41f},{.25f,.22f},{.37f,.22f}},{{-.29f,-.03f},{-.40f,-.14f},{-.29f,-.25f}},
         {{.26f,-.21f},{.37f,-.33f},{.25f,-.42f}},{{-.27f,.42f},{-.27f,.37f}}},
        {{{-.25f,.24f},{-.05f,.41f},{.15f,.24f},{-.05f,.07f},{-.25f,.24f}},
         {{.29f,.13f},{.29f,-.08f},{.05f,-.08f},{.05f,-.29f},{-.16f,-.29f},{-.16f,-.41f}},
         {{-.28f,-.05f},{-.39f,-.16f},{-.28f,-.27f}},{{.26f,-.25f},{.37f,-.36f}},{{.29f,.35f},{.40f,.35f}}},
        {{{-.32f,.31f},{-.12f,.31f},{-.12f,.12f},{.08f,-.08f},{.08f,-.31f},{.27f,-.31f}},
         {{.08f,.38f},{.28f,.19f},{.09f,.01f}},{{-.25f,.02f},{-.39f,-.11f},{-.25f,-.25f},{-.08f,-.25f}},
         {{.26f,-.04f},{.40f,-.04f},{.40f,-.17f}},{{-.16f,-.40f},{-.28f,-.40f}}}
    };
    private static final Vector3f FACE=new Vector3f(.61f,.80f,.82f),SIDE=new Vector3f(.12f,.34f,.43f),CORE=new Vector3f(1f,.83f,.49f);
    private record Sign(double x,double y,double z,double yaw,double roll,float size,int kind,float alpha){}
    private TianjiangRuneField(){}
    static void draw(PoseStack pose,MultiBufferSource buffers,float age,boolean reduced,boolean minimal){
        int major=reduced?8:18,minor=minimal?0:reduced?12:48,shards=minimal?4:reduced?12:36;
        Sign[] signs=new Sign[major+minor];
        for(int i=0;i<major;i++){
            double a=(i+.5)*Math.PI*2/major+Math.sin(i*2.31)*.13;
            double radius=1.92+Math.sin(i*1.71)*.25+Math.sin(age*.024+i*.9)*.07;
            signs[i]=new Sign(Math.cos(a)*radius,2.16+Math.sin(a)*1.22+Math.sin(i*2.73)*.16,
                    -1.02+Math.sin(i*1.97+age*.012)*.46,Math.sin(a+age*.014+i)*.65,
                    Math.sin(i*1.83)*.38+Math.sin(age*.017+i)*.13,.57f+(i%4)*.065f,i%4,.84f);
        }
        for(int i=0;i<minor;i++){
            double a=i*2.39996+age*(i%2==0?.006:-.004),r=1.25+fract(i*.754877666)*1.0;
            // Uneven heights and depth, with the face's frontal sightline left open.
            double y=.55+fract(i*.618033989)*2.72+Math.sin(age*.015+i)*.11;
            double z=Math.sin(a)*r*.65-.45;
            if(z>-.25&&y>1.95)y=.72+fract(i*.41421356)*.95;
            signs[major+i]=new Sign(Math.cos(a)*r,y,z,
                    a+Math.PI/2,Math.sin(i*1.73+age*.018)*.52,.24f+(i%4)*.035f,(i+1)%4,.62f);
        }
        Matrix4f matrix=pose.last().pose();
        // Slim cool faces and dark side planes retain depth beneath the luminous engraving.
        var base=buffers.getBuffer(TianjiangAuraRenderType.VEIL);
        for(Sign sign:signs)glyph(base,matrix,sign,false);
        for(int i=0;i<shards;i++){
            double cycle=fract(age*.0025+i*.61803398875),a=i*2.39996-age*.009;
            double r=1.4+(i%5)*.22,y=.14+cycle*3.5;
            // The few front-facing facets stay below the eye line.
            double z=Math.sin(a)*r*.70-.45;if(z>.15&&y>2.05)y=1.5+(y-2.05)*.3;
            Sign s=new Sign(Math.cos(a)*r,y,z,a+age*.014,Math.sin(a)*.5,
                    .18f+(i%4)*.045f,0,(float)Math.sin(cycle*Math.PI)*.78f);
            shard(base,matrix,s);
        }
        var light=buffers.getBuffer(TianjiangAuraRenderType.LIGHT);
        for(Sign sign:signs)glyph(light,matrix,sign,true);
    }
    private static double fract(double x){return x-Math.floor(x);}
    private static void glyph(VertexConsumer sink,Matrix4f matrix,Sign s,boolean light){
        for(float[][] path:SIGNS[s.kind])for(int i=1;i<path.length;i++){
            double stretch=2.30+s.kind*.15;
            double x=path[i-1][0]*.46,y=path[i-1][1]*stretch,xx=path[i][0]*.46,yy=path[i][1]*stretch;
            double dx=xx-x,dy=yy-y,length=Math.hypot(dx,dy),w=light?.0045:.010;
            double nx=-dy/length*w,ny=dx/length*w,z=light?.014:.010;
            // Taper open ends into fine tips, keeping interior joins continuous.
            double start=i==1?.24:1,end=i==path.length-1?.24:1;
            Vector3f a=p(s,x+nx*start,y+ny*start,z),b=p(s,xx+nx*end,yy+ny*end,z),c=p(s,xx-nx*end,yy-ny*end,z),d=p(s,x-nx*start,y-ny*start,z);
            quad(sink,matrix,a,b,c,d,light?CORE:FACE,s.alpha*(light?.56f:.72f));
            if(!light){
                Vector3f aa=p(s,x+nx*start,y+ny*start,-.012),bb=p(s,xx+nx*end,yy+ny*end,-.012),cc=p(s,xx-nx*end,yy-ny*end,-.012),dd=p(s,x-nx*start,y-ny*start,-.012);
                quad(sink,matrix,aa,bb,cc,dd,SIDE,s.alpha*.78f);
                quad(sink,matrix,a,aa,bb,b,SIDE,s.alpha*.88f);
                quad(sink,matrix,d,c,cc,dd,SIDE,s.alpha*.88f);
                quad(sink,matrix,a,d,dd,aa,SIDE,s.alpha*.88f);
                quad(sink,matrix,b,bb,cc,c,SIDE,s.alpha*.88f);
            }
        }
    }
    private static void shard(VertexConsumer sink,Matrix4f matrix,Sign s){
        var top=p(s,0,.65,0);var right=p(s,.26,0,0);var bottom=p(s,0,-.65,0);var left=p(s,-.26,0,0);var centre=p(s,0,0,.18);
        quad(sink,matrix,top,right,centre,centre,new Vector3f(.35f,.86f,.95f),s.alpha);
        quad(sink,matrix,right,bottom,centre,centre,new Vector3f(.11f,.44f,.57f),s.alpha);
        quad(sink,matrix,bottom,left,centre,centre,new Vector3f(.19f,.60f,.72f),s.alpha);
        quad(sink,matrix,left,top,centre,centre,new Vector3f(.62f,.92f,1f),s.alpha);
    }
    private static Vector3f p(Sign s,double x,double y,double z){
        double u=(x*Math.cos(s.roll)-y*Math.sin(s.roll))*s.size,v=(x*Math.sin(s.roll)+y*Math.cos(s.roll))*s.size;
        return new Vector3f((float)(s.x+u*Math.cos(s.yaw)-z*s.size*Math.sin(s.yaw)),(float)(s.y+v),(float)(s.z+u*Math.sin(s.yaw)+z*s.size*Math.cos(s.yaw)));
    }
    private static void quad(VertexConsumer sink,Matrix4f m,Vector3f a,Vector3f b,Vector3f c,Vector3f d,Vector3f col,float alpha){
        for(Vector3f p:new Vector3f[]{a,b,c,d})sink.vertex(m,p.x,p.y,p.z).color(col.x,col.y,col.z,alpha).uv(.5f,.5f).endVertex();
    }
}
