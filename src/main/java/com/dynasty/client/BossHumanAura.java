package com.dynasty.client;

import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.Mob;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;
import org.joml.Vector3f;

/** Sparse, depth-tested client atmosphere. No server actors, sounds, damage or lights. */
@Mod.EventBusSubscriber(modid="dynasty",value=Dist.CLIENT)
public final class BossHumanAura {
    private static boolean reviewSuppressed;
    private static int reviewEmissions;
    private static final boolean REVIEW=Boolean.getBoolean("dynasty.bossHumanPresenceQa");
    public static void setReviewSuppressed(boolean suppressed){if(REVIEW){reviewSuppressed=suppressed;reviewEmissions=0;}}
    public static int reviewEmissions(){return reviewEmissions;}
    private static int kind(String id){return switch(id){case "nine_heaven_general"->0;case "dragon_king"->1;case "dragon_emperor"->2;default->-1;};}
    private static Vector3f color(int k){return k==0?new Vector3f(.87f,.85f,.60f):k==1?new Vector3f(.29f,.72f,.80f):new Vector3f(.76f,.43f,.20f);}

    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent event){
        if(event.phase!=TickEvent.Phase.END||reviewSuppressed)return;
        var mc=Minecraft.getInstance();if(mc.level==null||mc.player==null||mc.isPaused()||mc.level.getGameTime()%4!=0)return;
        int budget=16;
        for(var mob:mc.level.getEntitiesOfClass(Mob.class,mc.player.getBoundingBox().inflate(36),m->!m.isInvisible()&&!m.isDeadOrDying())){
            ResourceLocation key=ForgeRegistries.ENTITY_TYPES.getKey(mob.getType());
            if(key==null||!key.getNamespace().equals("dynasty"))continue;
            int k=kind(key.getPath());if(k<0)continue;
            double phase=(mob.tickCount+mob.getId()%37)*.023;
            double yaw=Math.toRadians(mob.yBodyRot);double bx=Math.sin(yaw),bz=-Math.cos(yaw),sx=Math.cos(yaw),sz=Math.sin(yaw);
            int count=mob.swinging?3:2;
            for(int i=0;i<count&&budget>0;i++,budget--){
                double t=phase+i*Math.PI,side=Math.cos(t)*(.8+k*.06),height=1.85+Math.sin(t)*.55;
                double x=mob.getX()+bx*.79+sx*side,z=mob.getZ()+bz*.79+sz*side;
                mc.level.addParticle(new DustParticleOptions(color(k),mob.swinging?.62f:.42f),x,mob.getY()+height,z,-sx*Math.sin(t)*.004,.009,-sz*Math.sin(t)*.004);
                if(REVIEW)reviewEmissions++;
            }
            if(k==1&&mob.tickCount%20==0&&budget>0){
                mc.level.addParticle(ParticleTypes.DRIPPING_WATER,mob.getX()+bx*.8,mob.getY()+2.35,mob.getZ()+bz*.8,0,0,0);budget--;if(REVIEW)reviewEmissions++;
            }
            if(budget<=0)break;
        }
    }

    static void draw(PoseStack pose,MultiBufferSource buffers,Mob mob,String id,float partial,boolean casting){
        int k=kind(id);if(k<0||reviewSuppressed||mob.isInvisible()||mob.isDeadOrDying())return;
        float age=mob.tickCount+partial,boost=mob.swinging||casting?1.35f:1;
        float centre=k==2?2.02f:1.86f,z=-.92f;double radius=k==2?1.04:.92;
        var sink=buffers.getBuffer(RenderType.debugQuads());var matrix=pose.last().pose();Vector3f col=color(k);
        int alpha=(int)((k==2?145:130)*boost);
        java.util.function.Consumer<double[]> line=segment->{
            double x1=segment[0],y1=segment[1],x2=segment[2],y2=segment[3],dx=x2-x1,dy=y2-y1,len=Math.hypot(dx,dy);
            if(len<1e-6)return;double width=.009*boost,nx=-dy/len*width,ny=dx/len*width;
            vertex(sink,matrix,x1+nx,y1+ny,z,col,alpha);vertex(sink,matrix,x2+nx,y2+ny,z,col,alpha);
            vertex(sink,matrix,x2-nx,y2-ny,z,col,alpha);vertex(sink,matrix,x1-nx,y1-ny,z,col,alpha);
        };
        // Broken angular rune arcs stay behind the body; broad unlit faces remain readable.
        double turn=Math.sin(age*.012)*.07;
        for(int i=0;i<8;i++){
            if(k==0&&i%3==1||k==1&&i%4==0||k==2&&i%2==1)continue;
            double a=i*Math.PI/4+turn,b=a+Math.PI/4*.78;
            line.accept(new double[]{Math.cos(a)*radius,centre+Math.sin(a)*radius,Math.cos(b)*radius,centre+Math.sin(b)*radius});
        }
        for(int s:new int[]{-1,1}){
            double x=s*(k==2?1.18:.98),y=centre+Math.sin(age*.025+s)*.08;
            if(k==0){line.accept(new double[]{x-.07,y+.19,x+.07,y+.19});line.accept(new double[]{x,y+.19,x,y-.17});line.accept(new double[]{x-.05,y-.05,x+.05,y-.05});}
            else if(k==1){line.accept(new double[]{x-.13,y,x-.03,y+.09});line.accept(new double[]{x-.03,y+.09,x+.08,y});line.accept(new double[]{x+.08,y,x+.17,y+.06});}
            else {line.accept(new double[]{x-.06,y-.18,x-.06,y+.18});line.accept(new double[]{x+.06,y-.18,x+.06,y+.18});line.accept(new double[]{x-.06,y+.18,x+.06,y+.18});line.accept(new double[]{x-.03,y,x+.03,y});}
        }
    }
    private static void vertex(com.mojang.blaze3d.vertex.VertexConsumer sink,org.joml.Matrix4f matrix,double x,double y,float z,Vector3f col,int alpha){
        sink.vertex(matrix,(float)x,(float)y,z).color((int)(col.x*255),(int)(col.y*255),(int)(col.z*255),alpha).endVertex();
    }
}
