package com.dynasty.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.Minecraft;
import net.minecraft.client.ParticleStatus;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Mob;
import org.joml.Matrix4f;
import org.joml.Vector3f;
import java.util.ArrayList;
import java.util.List;

/** Two original royal atmospheres. Bounded client quads only, no server actors or damage. */
final class RoyalBossAura {
    private static final Vector3f WATER=new Vector3f(.20f,.76f,.74f),FOAM=new Vector3f(.65f,.94f,.84f),
            GOLD=new Vector3f(.96f,.66f,.26f),EMBER=new Vector3f(.70f,.17f,.12f);
    private RoyalBossAura(){}
    static int emit(Mob mob,int budget,boolean king){
        var mc=Minecraft.getInstance();var detail=mc.options.particles().get();
        if(mc.level==null||budget<=0||detail==ParticleStatus.MINIMAL)return 0;
        int count=Math.min(budget,detail==ParticleStatus.DECREASED?2:mob.swinging?12:8);
        double yaw=Math.toRadians(mob.yBodyRot),bx=Math.sin(yaw),bz=-Math.cos(yaw),sx=Math.cos(yaw),sz=Math.sin(yaw);
        for(int i=0;i<count;i++){
            double a=mob.tickCount*(king?.028:-.012)+i*2.39996,r=1.2+(i%4)*.25;
            double side=Math.cos(a)*r,depth=Math.sin(a)*r*.7;
            double y=king?.45+(i%3)*.6+Math.sin(a)*.22:.3+fract(mob.tickCount*.009+i*.618)*3.0;
            mc.level.addParticle(new DustParticleOptions(king?(i%3==0?FOAM:WATER):(i%3==0?EMBER:GOLD),king?.57f:.50f),
                    mob.getX()+bx*depth+sx*side,mob.getY()+y,mob.getZ()+bz*depth+sz*side,
                    king?-sx*Math.sin(a)*.017:0,king?.007:.023,king?-sz*Math.sin(a)*.017:0);
        }
        return count;
    }
    static void draw(PoseStack pose,MultiBufferSource buffers,Mob mob,float partial,boolean casting,boolean king){
        var mc=Minecraft.getInstance();double distance=mc.gameRenderer.getMainCamera().getPosition().distanceToSqr(mob.position());
        if(distance>4096)return;
        boolean reduced=mc.options.particles().get()!=ParticleStatus.ALL||distance>576;
        boolean minimal=mc.options.particles().get()==ParticleStatus.MINIMAL;
        float age=mob.tickCount+partial,boost=1+Math.max(0,Mth.sin(mob.getAttackAnim(partial)*Mth.PI))*.25f;
        List<Stroke> strokes=new ArrayList<>(160);
        if(king){
            // Low horizontal water sheets orbit the legs and torso, not a pair of cloud wings.
            for(int ring=0;ring<(minimal?1:3);ring++){
                float[][] path=new float[41][3];
                for(int j=0;j<path.length;j++){
                    double a=age*(ring%2==0?.012:-.009)+j/40.0*Math.PI*1.65+ring*1.7;
                    double r=1.35+ring*.31;
                    path[j]=p(Math.cos(a)*r,.42+ring*.65+Math.sin(a*2+age*.02)*.18,Math.sin(a)*r*.74);
                }
                add(strokes,path,(ring==0?.065f:.045f)*boost,WATER,.70f);
            }
            // Paired rising tide curls with open centres. Broad base, narrow crest.
            for(int side:new int[]{-1,1}){
                float[][] path=new float[33][3];
                for(int j=0;j<path.length;j++){
                    double t=j/32.0,a=t*Math.PI*1.6-.5;
                    path[j]=p(side*(1.22+Math.cos(a)*(.95-.35*t)),1.05+t*1.7+Math.sin(a)*.33,-.95+Math.sin(t*4+age*.025+side)*.16);
                }
                add(strokes,path,.072f*boost,WATER,.83f);
                if(!reduced){float[][] crest=new float[15][3];for(int j=0;j<crest.length;j++){var q=path[j+12];crest[j]=p(q[0]+side*.10,q[1]+.08,q[2]-.08);}add(strokes,crest,.015f,FOAM,.75f);}
            }
        }else{
            // Imperial power rises in three separated banners, framed by broken angular rays.
            // These are moving light sheets, not rigid equipment or readable Chinese characters.
            for(int band=0;band<(minimal?1:3);band++){
                float[][] path=new float[33][3];double side=band-1;
                for(int j=0;j<path.length;j++){
                    double t=j/32.0;
                    path[j]=p(side*(.8+t*.65)+Math.sin(t*5-age*.018+band)*.14,.32+t*3.42,-1.02-Math.sin(t*Math.PI)*.20-band*.04);
                }
                add(strokes,path,.065f*boost,EMBER,.68f);
                add(strokes,path,.014f,GOLD,.83f);
            }
            for(int side:new int[]{-1,1})for(int ray=0;ray<(reduced?2:4);ray++){
                double y=.65+ray*.70,x=1.30+Math.sin(ray*.8)*.48;
                add(strokes,new float[][]{p(side*x,y,-1.0),p(side*(x+.28),y+.38,-1.15),p(side*(x+.10),y+.75,-1.25)},.017f,GOLD,.78f);
            }
        }
        // New narrow glyph families: tide hooks vs imperial stem-and-branch inscriptions.
        int count=minimal?8:reduced?20:king?42:48;
        for(int i=0;i<count;i++){
            double a=i*2.39996+age*(king?.006:.002),cycle=fract(i*.618033989+age*(king?.0009:.0018));
            double x,y,z;
            if(king){double r=1.45+fract(i*.4142)*.75;x=Math.cos(a)*r;y=.65+cycle*2.65;z=Math.sin(a)*r*.55-.56;if(z>-.2&&y>1.92)y=.70+cycle*.85;}
            else{x=(i%6-2.5)*.64+Math.sin(age*.012+i)*.12;y=.50+cycle*3.0;z=-1.0-fract(i*.4142)*.65;}
            double size=(king?.55:.64)+fract(i*.321)*.24,lean=Math.sin(i*1.73+age*.009)*.14;
            float[][] shape=king?new float[][]{p(-.05,.48,0),p(-.05,.19,0),p(.04,.10,0),p(.04,-.11,0),p(-.03,-.17,0),p(-.03,-.52,0)}:
                    new float[][]{p(0,.54,0),p(0,.17,0),p(.07,.12,0),p(0,.03,0),p(0,-.52,0)};
            float[][] path=new float[shape.length][3];
            for(int j=0;j<shape.length;j++){var q=shape[j];path[j]=p(x+(q[0]+q[1]*lean)*size,y+q[1]*size,z);}
            float alpha=(float)(.48+.23*Math.sin(cycle*Math.PI));
            add(strokes,path,.0055f,king?FOAM:GOLD,alpha);
            add(strokes,new float[][]{p(x-.09*size,y+.09*size,z),p(x-.04*size,y+.03*size,z),p(x-.04*size,y-.08*size,z)},.0045f,king?WATER:GOLD,alpha);
            if(i%3==0)add(strokes,new float[][]{p(x+.07*size,y-.25*size,z),p(x+.12*size,y-.29*size,z)},.004f,king?FOAM:GOLD,alpha);
        }
        int motes=minimal?6:reduced?22:68;
        for(int i=0;i<motes;i++){
            double c=fract(age*(king?.003:.0025)+i*.61803399),a=i*2.39996+age*(king?.018:.004),r=1.25+fract(i*.4142)*1.12;
            double x=Math.cos(a)*r,y=.12+c*3.25,z=Math.sin(a)*r*.63-.30;
            float opacity=(float)Math.sin(c*Math.PI)*.78f;
            float[][] tail=king?new float[][]{p(x,y+.05,z),p(x-.04,y,z),p(x-.08,y-.09,z)}:new float[][]{p(x,y+.09,z),p(x,y,z),p(x+.025,y-.12,z)};
            add(strokes,tail,king?.018f:.013f,king?FOAM:i%4==0?EMBER:GOLD,opacity);
        }
        renderStrokes(pose,buffers,strokes,age);
    }
    static void drawWeapon(PoseStack pose,MultiBufferSource buffers,Mob mob,float partial,boolean king){
        if(BossHumanAura.suppressed()||mob.isInvisible()||mob.isDeadOrDying()||!mob.getMainHandItem().isEmpty())return;
        var mc=Minecraft.getInstance();if(mc.options.particles().get()==ParticleStatus.MINIMAL||mc.gameRenderer.getMainCamera().getPosition().distanceToSqr(mob.position())>576)return;
        float age=mob.tickCount+partial;List<Stroke> strokes=new ArrayList<>(4);
        for(int s:new int[]{-1,1}){
            float[][] path=new float[25][3];
            for(int j=0;j<path.length;j++){
                double t=j/24.0;
                path[j]=king?p(Math.sin(t*7-age*.05+s)*.08,t*2.45,.10*s):p(s*.20,.65+t*1.8,.08+Math.sin(t*4-age*.04)*.012);
            }
            add(strokes,path,.012f,king?WATER:GOLD,.72f);
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
