package com.dynasty.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.Minecraft;
import net.minecraft.client.ParticleStatus;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Mob;
import org.joml.Matrix4f;
import org.joml.Vector3f;

/** Original celestial-command atmosphere, entirely visual; no hit zones or server state. */
final class TianjiangAura {
    static final ResourceLocation GLOW=new ResourceLocation("dynasty","textures/entity/boss_cuboid/nine_heaven_general_aura.png");
    private static final Vector3f GOLD=new Vector3f(.86f,.69f,.38f);
    private static final Vector3f CLOUD=new Vector3f(.52f,.79f,.85f);
    private TianjiangAura(){}

    static float power(Mob mob,float partial,boolean casting){
        // Use the existing synced swing, not a new damage/skill timeline.
        float swing=mob.getAttackAnim(partial);
        return casting?.8f:Mth.sin(swing*Mth.PI)*.85f;
    }
    static float glowAlpha(Mob mob,float partial,boolean casting){
        if(BossHumanAura.suppressed()||mob.isInvisible()||mob.isDeadOrDying())return 0;
        return .29f+.09f*Mth.sin((mob.tickCount+partial)*.055f)+power(mob,partial,casting)*.47f;
    }

    /** Returns actual emissions so the existing shared 16-per-four-tick cap remains authoritative. */
    static int emit(Mob mob,int budget){
        var mc=Minecraft.getInstance();if(mc.level==null||budget<=0)return 0;
        var detail=mc.options.particles().get();if(detail==ParticleStatus.MINIMAL)return 0;
        int count=Math.min(budget,detail==ParticleStatus.DECREASED?1:mob.swinging?4:3),emitted=0;
        double yaw=Math.toRadians(mob.yBodyRot),bx=Math.sin(yaw),bz=-Math.cos(yaw),sx=Math.cos(yaw),sz=Math.sin(yaw);
        for(int i=0;i<count;i++){
            double phase=mob.tickCount*.036+i*2.1,side=Math.cos(phase)*(.64+i*.11);
            double y=1.22+(Math.sin(phase*.7)+1)*.62;
            mc.level.addParticle(new DustParticleOptions(i==1?GOLD:CLOUD,.45f),
                    mob.getX()+bx*.47+sx*side,mob.getY()+y,mob.getZ()+bz*.47+sz*side,
                    -sx*Math.sin(phase)*.006,.016,-sz*Math.sin(phase)*.006);emitted++;
        }
        if(mob.swinging&&emitted<budget&&detail==ParticleStatus.ALL){
            mc.level.addParticle(ParticleTypes.ELECTRIC_SPARK,mob.getX()+bx*.45,mob.getY()+1.75,mob.getZ()+bz*.45,0,.02,0);emitted++;
        }
        return emitted;
    }

    static void draw(PoseStack pose,MultiBufferSource buffers,Mob mob,float partial,boolean casting){
        float age=mob.tickCount+partial,power=power(mob,partial,casting);
        float breathe=.5f+.5f*Mth.sin(age*.045f),z=-.61f;
        var sink=buffers.getBuffer(RenderType.debugQuads());var mat=pose.last().pose();
        // Open crown of command: separate upper arcs leave a clear face/torso window.
        double radius=.94+power*.09,cy=1.96,turn=Math.sin(age*.012)*.035;
        int alpha=(int)(135+breathe*24+power*45);
        for(int i=0;i<8;i++){
            if(i==5||i==6)continue;
            double a=i*Math.PI/4+turn,b=a+Math.PI/4*.71;
            line(sink,mat,Math.cos(a)*radius,cy+Math.sin(a)*radius,z,
                    Math.cos(b)*radius,cy+Math.sin(b)*radius,z,.016f,GOLD,alpha);
        }
        // Paired, angular cloud-current ribbons; their middle stays behind the shoulders.
        for(int side:new int[]{-1,1}){
            double sway=Math.sin(age*.025+side)*.055;
            double[][] points={{side*.68,2.42},{side*.91,2.2},{side*.81,1.94},{side*1.03,1.65},
                    {side*.88,1.38},{side*.94,1.06},{side*.77,.81}};
            for(int j=0;j<points.length-1;j++){
                line(sink,mat,points[j][0]+sway,points[j][1],z-.08,
                        points[j+1][0]+sway,points[j+1][1],z-.08,.012f,CLOUD,65+j*9+(int)(power*55));
            }
            // Two original command glyphs, kept outside the head silhouette.
            double x=side*1.07,y=2.13+Math.sin(age*.024+side)*.065;
            line(sink,mat,x-.085,y+.14,z,x+.085,y+.14,z,.018f,GOLD,alpha);
            line(sink,mat,x,y+.14,z,x,y-.13,z,.018f,GOLD,alpha);
            line(sink,mat,x-.065,y+.015,z,x+.065,y+.015,z,.014f,CLOUD,alpha);
            line(sink,mat,x,y-.13,z,x+side*.08,y-.07,z,.014f,CLOUD,alpha);
            // Three substantial but sparse light slips give the aura a readable mass.
            // They are client quads behind the shoulders, not new armour or collision.
            for(int j=0;j<3;j++){
                double px=side*(1.10+j*.085),py=2.62-j*.43+Math.sin(age*.026+j+side)*.055;
                float width=.044f+(2-j)*.012f;
                shard(sink,mat,px,py,z-.1,.23-j*.025,width,CLOUD,105+(int)(breathe*30+power*60));
                line(sink,mat,px,py+.10,z-.105,px,py-.055,z-.105,.010f,GOLD,185);
            }
        }
        // A restrained travelling bead, not a flashing full-screen pulse.
        for(int i=0;i<3;i++){
            double a=age*.018+i*Math.PI*2/3,x=Math.cos(a)*radius,y=cy+Math.sin(a)*radius;
            line(sink,mat,x-.025,y-.025,z-.01,x+.025,y+.025,z-.01,.018f,CLOUD,185);
        }
    }
    private static void shard(VertexConsumer sink,Matrix4f mat,double x,double y,double z,double height,double width,Vector3f c,int alpha){
        point(sink,mat,x,y+height,z,c,alpha);point(sink,mat,x+width,y,z,c,alpha);
        point(sink,mat,x,y-height*.6,z,c,alpha);point(sink,mat,x-width,y,z,c,alpha);
    }
    private static void line(VertexConsumer sink,Matrix4f mat,double x,double y,double z,double ex,double ey,double ez,float width,Vector3f c,int alpha){
        double dx=ex-x,dy=ey-y,len=Math.hypot(dx,dy);if(len<1e-6)return;
        double nx=-dy/len*width,ny=dx/len*width;
        point(sink,mat,x+nx,y+ny,z,c,alpha);point(sink,mat,ex+nx,ey+ny,ez,c,alpha);
        point(sink,mat,ex-nx,ey-ny,ez,c,alpha);point(sink,mat,x-nx,y-ny,z,c,alpha);
    }
    private static void point(VertexConsumer sink,Matrix4f mat,double x,double y,double z,Vector3f c,int alpha){
        sink.vertex(mat,(float)x,(float)y,(float)z).color((int)(c.x*255),(int)(c.y*255),(int)(c.z*255),alpha).endVertex();
    }
}
