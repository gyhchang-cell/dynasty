package com.dynasty.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.Minecraft;
import net.minecraft.client.ParticleStatus;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Mob;
import org.joml.Matrix4f;
import org.joml.Vector3f;
import java.util.ArrayList;
import java.util.List;

/** Original thunder-command mantle. Client visuals only; approved rig and combat stay unchanged. */
final class TianjiangAura {
    static final ResourceLocation GLOW=new ResourceLocation("dynasty","textures/entity/boss_cuboid/nine_heaven_general_aura.png");
    static final ResourceLocation STREAM=new ResourceLocation("dynasty","textures/effect/tianjiang_stream.png");
    private static final Vector3f GOLD=new Vector3f(1f,.77f,.36f),CLOUD=new Vector3f(.22f,.76f,.94f);
    private TianjiangAura(){}
    static float power(Mob mob,float partial,boolean casting){
        return casting?.8f:Math.max(0,Mth.sin(mob.getAttackAnim(partial)*Mth.PI))*.85f;
    }
    static float glowAlpha(Mob mob,float partial,boolean casting){
        if(BossHumanAura.suppressed()||mob.isInvisible()||mob.isDeadOrDying())return 0;
        return .55f+.10f*Mth.sin((mob.tickCount+partial)*.055f)+power(mob,partial,casting)*.37f;
    }
    /** Existing shared emission budget still applies. Rendered streamers are bounded client meshes. */
    static int emit(Mob mob,int budget){
        var mc=Minecraft.getInstance();if(mc.level==null||budget<=0)return 0;
        var detail=mc.options.particles().get();if(detail==ParticleStatus.MINIMAL)return 0;
        int count=Math.min(budget,detail==ParticleStatus.DECREASED?2:mob.swinging?14:10),emitted=0;
        double yaw=Math.toRadians(mob.yBodyRot),bx=Math.sin(yaw),bz=-Math.cos(yaw),sx=Math.cos(yaw),sz=Math.sin(yaw);
        for(int i=0;i<count;i++){
            double phase=mob.tickCount*.033+i*2.399,side=Math.cos(phase)*(1.3+i*.12),depth=Math.sin(phase)*.95;
            double y=.30+((mob.tickCount*.016+i*.39)%1)*3.4;
            mc.level.addParticle(new DustParticleOptions(i%3==0?GOLD:CLOUD,.75f),
                    mob.getX()+bx*depth+sx*side,mob.getY()+y,mob.getZ()+bz*depth+sz*side,
                    -sx*Math.sin(phase)*.015,.026,-sz*Math.sin(phase)*.015);emitted++;
        }
        if(mob.swinging&&emitted<budget&&detail==ParticleStatus.ALL){
            mc.level.addParticle(ParticleTypes.ELECTRIC_SPARK,mob.getX()+bx*.4,mob.getY()+1.8,mob.getZ()+bz*.4,0,.035,0);emitted++;
        }
        return emitted;
    }

    static void draw(PoseStack pose,MultiBufferSource buffers,Mob mob,float partial,boolean casting){
        var mc=Minecraft.getInstance();
        double distance=mc.gameRenderer.getMainCamera().getPosition().distanceToSqr(mob.position());
        if(distance>64*64)return;
        boolean reduced=mc.options.particles().get()!=ParticleStatus.ALL||distance>24*24;
        float age=mob.tickCount+partial,power=power(mob,partial,casting);
        float pulse=.88f+.12f*Mth.sin(age*.045f),boost=1+power*.28f;
        List<Stroke> strokes=new ArrayList<>(150);
        // A large, open command crown; the centre contains no luminous sheet over the face.
        for(int arc=0;arc<8;arc++){
            double start=arc*Math.PI/4+Math.sin(age*.009)*.045;
            float[][] path=new float[7][3];
            for(int j=0;j<path.length;j++){
                double a=start+j/6.0*Math.PI/4*.74;
                path[j]=p(Math.cos(a)*1.62,2.0+Math.sin(a)*1.62,-.73+Math.cos(a)*.14);
            }
            add(strokes,path,.026f,GOLD,.83f*pulse);
        }
        // Four long cloud-lightning currents on each side, widening well beyond the shoulders.
        // Distinct depth and moving roots give a mantle of energy, not another rigid accessory.
        for(int side:new int[]{-1,1})for(int branch=0;branch<(reduced?2:4);branch++){
            float[][] path=new float[17][3];
            for(int j=0;j<path.length;j++){
                double t=j/16.0,arch=Math.sin(t*Math.PI),sway=Math.sin(age*.042-t*7+branch*.8+side)*.23*t;
                double x=side*(.49+t*(2.0-branch*.16)+arch*.35+sway);
                double y=2.1+Math.sin(t*Math.PI*.67)*(1.62-branch*.64)+Math.sin(age*.036-t*6+branch+side*.9)*.22*t;
                double z=-.52-t*(.55+branch*.19)+Math.sin(t*5-age*.033+branch+side)*.30;
                path[j]=p(x,y,z);
            }
            add(strokes,path,(.102f-branch*.012f)*boost,CLOUD,(.88f-branch*.11f)*pulse);
            // Broken secondary filaments follow the current instead of arbitrary all-over sparks.
            if(!reduced&&branch<2){
                float[][] fork=new float[8][3];
                for(int j=0;j<fork.length;j++){
                    var source=path[7+j];fork[j]=p(source[0]+side*j*.028,source[1]-.10-j*.035,source[2]-.10);
                }
                add(strokes,fork,.016f,GOLD,.63f);
            }
        }
        // Moving, tilted arcs surround the actual body in X/Z. The front passage remains below the face.
        for(int orbit=0;orbit<(reduced?1:2);orbit++){
            float[][] path=new float[33][3];
            for(int j=0;j<path.length;j++){
                double a=age*(orbit==0?.012:-.009)+j/32.0*Math.PI*1.57+orbit*2.1;
                double r=orbit==0?1.62:1.26;
                path[j]=p(Math.cos(a)*r,.80+orbit*.88+Math.sin(a)*.29,Math.sin(a)*r*.75);
            }
            add(strokes,path,.031f,orbit==0?CLOUD:GOLD,.78f*pulse);
        }
        // Stable 3-D mote trajectories: bright heads, tapered tails, gentle upward drift.
        // They have no entities, random allocation stream or networking and obey particle LOD.
        int count=mc.options.particles().get()==ParticleStatus.MINIMAL?8:reduced?28:84;
        for(int i=0;i<count;i++){
            double cycle=fract(age*.0035+i*.61803398875),a=i*2.39996+age*.008;
            double r=1.22+(.5+.5*Math.sin(i*4.1))*.95;
            double x=Math.cos(a)*r,y=.18+cycle*3.65,z=Math.sin(a)*r*.69-.32;
            float opacity=(float)(Math.sin(cycle*Math.PI)*.94);
            float len=.07f+(i%4)*.035f;
            add(strokes,new float[][]{p(x,y+.025,z),p(x,y,z),p(x-.035*Math.sin(a),y-len,z-.035*Math.cos(a))},.014f+(i%3)*.004f,i%3==0?GOLD:CLOUD,opacity);
        }
        // Low, broken updrafts ground the power without pretending to mark a damage radius.
        for(int side:new int[]{-1,1}){
            add(strokes,new float[][]{p(side*1.45,.10,-.55),p(side*1.70,.30,-.7),p(side*1.52,.62,-.9),p(side*1.76,.91,-1.0)},.043f,CLOUD,.65f*pulse);
        }
        renderStrokes(pose,buffers,strokes,age);
        TianjiangRuneField.draw(pose,buffers,age,reduced,mc.options.particles().get()==ParticleStatus.MINIMAL);
    }
    /** Grip-local energy follows the real animated pole; it is not a world-space weapon copy. */
    static void drawWeapon(PoseStack pose,MultiBufferSource buffers,Mob mob,float partial){
        if(BossHumanAura.suppressed()||mob.isInvisible()||mob.isDeadOrDying()||!mob.getMainHandItem().isEmpty())return;
        var mc=Minecraft.getInstance();
        if(mc.options.particles().get()==ParticleStatus.MINIMAL
                ||mc.gameRenderer.getMainCamera().getPosition().distanceToSqr(mob.position())>24*24)return;
        float age=mob.tickCount+partial,boost=1+power(mob,partial,false)*.7f;
        List<Stroke> strokes=new ArrayList<>(5);
        for(int coil=0;coil<2;coil++){
            float[][] path=new float[25][3];
            for(int j=0;j<path.length;j++){
                double t=j/24.0,a=t*Math.PI*3-age*.055+coil*Math.PI;
                double radius=.085+Math.sin(t*Math.PI)*.035;
                path[j]=p(Math.cos(a)*radius,t*1.9,Math.sin(a)*radius);
            }
            add(strokes,path,.016f*boost,coil==0?GOLD:CLOUD,.78f);
        }
        // Two energy packets ascend from the palm to the existing jade socket.
        for(int i=0;i<2;i++){
            double t=fract(age*.008+i*.5),a=t*Math.PI*3-age*.055;
            double x=Math.cos(a)*.13,z=Math.sin(a)*.13;
            add(strokes,new float[][]{p(x,t*1.9-.11,z),p(x,t*1.9,z),p(x*.7,t*1.9+.07,z*.7)},
                    .035f*boost,GOLD,(float)Math.sin(t*Math.PI));
        }
        renderStrokes(pose,buffers,strokes,age);
    }
    private static void renderStrokes(PoseStack pose,MultiBufferSource buffers,List<Stroke> strokes,float age){
        Matrix4f mat=pose.last().pose();Vector3f eye=new Matrix4f(mat).invert().transformPosition(new Vector3f());
        // Emit each render type as a batch; retaining consumers across buffer switches corrupts quads.
        for(int pass=0;pass<3;pass++){
            var sink=buffers.getBuffer(pass==0?TianjiangAuraRenderType.VEIL:TianjiangAuraRenderType.LIGHT);
            for(var stroke:strokes)ribbon(sink,mat,eye,stroke,pass,age);
        }
    }
    private record Stroke(float[][] points,float width,Vector3f color,float alpha){}
    private static void add(List<Stroke> list,float[][] points,float width,Vector3f color,float alpha){list.add(new Stroke(points,width,color,alpha));}
    private static float[] p(double x,double y,double z){return new float[]{(float)x,(float)y,(float)z};}
    private static double fract(double x){return x-Math.floor(x);}
    private static void ribbon(VertexConsumer sink,Matrix4f mat,Vector3f eye,Stroke s,int pass,float age){
        float width=s.width*(pass==0?5.0f:pass==1?2.1f:.26f);
        float alpha=s.alpha*(pass==0?.66f:pass==1?.32f:.39f);
        Vector3f color=pass==0?new Vector3f(s.color).mul(.58f):pass==1?s.color:new Vector3f(s.color).lerp(new Vector3f(1,1,1),.35f);
        float[][] path=s.points;
        // Shared joins prevent the dark overlapping rectangles seen in the first native iteration.
        Vector3f[] left=new Vector3f[path.length],right=new Vector3f[path.length];
        for(int j=0;j<path.length;j++){
            var centre=new Vector3f(path[j]);
            var tangent=new Vector3f(path[Math.min(j+1,path.length-1)]).sub(new Vector3f(path[Math.max(0,j-1)]));
            var normal=tangent.cross(new Vector3f(eye).sub(centre));
            if(normal.lengthSquared()<1e-8f)normal.set(1,0,0);normal.normalize();
            double t=j/(double)(path.length-1);
            float taper=path.length==2?1:(float)Math.sin(Math.PI*(.045+.92*t));
            normal.mul(width*taper);
            left[j]=new Vector3f(centre).add(normal);right[j]=new Vector3f(centre).sub(normal);
        }
        for(int j=0;j<path.length-1;j++){
            float flowA=path.length>=17?.76f+.24f*Mth.sin(age*.067f-j*.68f):1;
            float flowB=path.length>=17?.76f+.24f*Mth.sin(age*.067f-(j+1)*.68f):1;
            float a=alpha*flowA*(path.length>2&&j==0?.4f:1),b=alpha*flowB*(path.length>2&&j==path.length-2?.1f:1);
            vertex(sink,mat,left[j],color,a,0,0);
            vertex(sink,mat,left[j+1],color,b,1,0);
            vertex(sink,mat,right[j+1],color,b,1,1);
            vertex(sink,mat,right[j],color,a,0,1);
        }
    }
    private static void vertex(VertexConsumer sink,Matrix4f mat,Vector3f p,Vector3f c,float a,float u,float v){
        sink.vertex(mat,p.x,p.y,p.z).color(c.x,c.y,c.z,Mth.clamp(a,0,1)).uv(u,v).endVertex();
    }
}
