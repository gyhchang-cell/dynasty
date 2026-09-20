package com.dynasty.client;

import com.dynasty.Dynasty;
import com.dynasty.ImperialWeaponEffects;
import com.dynasty.QinglongDescent;
import com.dynasty.network.WeaponImpactPacket;
import com.dynasty.network.DragonDescentPacket;
import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.*;
import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.renderer.GameRenderer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.RenderLevelStageEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.event.TickEvent;
import org.joml.Matrix4f;
import org.lwjgl.opengl.GL11;
import java.util.*;

@Mod.EventBusSubscriber(modid=Dynasty.MODID,value=Dist.CLIENT)
public final class ImperialWeaponRenderer {
    private static final BufferBuilder BUFFER=new BufferBuilder(524288);
    private static final BufferBuilder BODY_BUFFER=new BufferBuilder(1048576);
    private record Face(Vec3 a,Vec3 b,Vec3 c,Vec3 d,int color,double alpha,Vec3 na,Vec3 nb,Vec3 nc,Vec3 nd) {}
    private static final List<Face> FACES=new ArrayList<>();
    private static final List<ImperialDragonRenderer.Instance> DRAGONS=new ArrayList<>();
    private record Impact(WeaponImpactPacket packet,long born) {}
    private record Held(int style,long born) {}
    private record Guardian(Vec3 origin,float yaw,double formed) {}
    private static final List<Impact> IMPACTS=new ArrayList<>();
    private static final Map<UUID,Held> HELD=new HashMap<>();
    private static final Map<Long,Descent> DESCENTS=new LinkedHashMap<>();
    private record PendingGlow(BufferBuilder.RenderedBuffer buffer,ClientLevel level,int tick,float partial,
                               Matrix4f modelView,Matrix4f projection) {}
    private static PendingGlow pendingGlow;
    private static VertexBuffer glowBuffer;
    private static final class Descent {
        final DragonDescentPacket packet;
        Vec3 position;
        double halfHeight=1,headOffset=2.4;
        boolean measured,descentSoundPlayed;
        long finished=-1;
        Descent(DragonDescentPacket packet){this.packet=packet;position=new Vec3(packet.x(),packet.y(),packet.z());}
    }
    private static ClientLevel world;

    private static void updateTarget(Descent effect,float partial) {
        if(effect.finished>=0)return;
        var target=world.getEntity(effect.packet.targetId());
        if(target==null||!target.getUUID().equals(effect.packet.targetUuid())||!target.isAlive())return;
        if(!effect.measured) {
            effect.halfHeight=target.getBbHeight()*.5;
            effect.headOffset=Math.max(2.4,effect.halfHeight+1.1);
            effect.measured=true;
        }
        // Non-player victims are sealed at the packet's initial center. Players are not rooted:
        // preserve normal PvP movement and keep their visual mark attached as before.
        if(target instanceof net.minecraft.world.entity.player.Player)
            effect.position=target.getPosition(partial).add(0,effect.halfHeight,0);
    }

    private static void clean() {
        ClientLevel current=Minecraft.getInstance().level;
        if(current!=world) { discardPendingGlow();IMPACTS.clear(); HELD.clear(); FACES.clear(); DRAGONS.clear(); DESCENTS.clear(); world=current; }
        if(world!=null)IMPACTS.removeIf(e->world.getGameTime()-e.born>=24);
        if(world!=null)DESCENTS.values().removeIf(e->world.getGameTime()-e.packet.started()>60
                || e.finished>=0 && world.getGameTime()-e.finished>12);
    }
    private static void discardPendingGlow() {
        PendingGlow stale=pendingGlow;pendingGlow=null;
        if(stale!=null)stale.buffer.release();
    }
    static void invalidateTransientBuffers() {
        if(!RenderSystem.isOnRenderThread()) {RenderSystem.recordRenderCall(ImperialWeaponRenderer::invalidateTransientBuffers);return;}
        discardPendingGlow();
        if(glowBuffer!=null)glowBuffer.close();glowBuffer=null;
    }
    @SubscribeEvent public static void clientTick(TickEvent.ClientTickEvent event) {
        if(event.phase!=TickEvent.Phase.END)return;
        clean();
        if(world==null || Minecraft.getInstance().isPaused())return;
        for(Descent effect:DESCENTS.values()) {
            long age=world.getGameTime()-effect.packet.started();
            // One cue per strike, independent of FPS; finished/late strikes never replay it.
            if(effect.descentSoundPlayed || effect.finished>=0
                    || age<QinglongDescent.DRAGON_START_TICK || age>=QinglongDescent.WINDUP_TICKS)continue;
            effect.descentSoundPlayed=true;
            updateTarget(effect,0);
            Vec3 sound=effect.position.add(0,effect.headOffset+3,0);
            world.playLocalSound(sound.x,sound.y,sound.z,SoundEvents.ENDER_DRAGON_GROWL,
                    SoundSource.PLAYERS,1.0F,1.15F,false);
            world.playLocalSound(sound.x,sound.y,sound.z,SoundEvents.ENDER_DRAGON_FLAP,
                    SoundSource.PLAYERS,0.8F,0.85F,false);
        }
    }
    public static void receive(DragonDescentPacket packet) {
        clean();
        if(world==null || packet.phase()<0 || packet.phase()>2
                || !Double.isFinite(packet.x()+packet.y()+packet.z()+packet.yaw()))return;
        if(packet.phase()==2){DESCENTS.remove(packet.id());return;}
        Descent effect=DESCENTS.computeIfAbsent(packet.id(),id->new Descent(packet));
        if(packet.phase()==1){effect.position=new Vec3(packet.x(),packet.y(),packet.z());effect.finished=world.getGameTime();}
        if(DESCENTS.size()>8)DESCENTS.remove(DESCENTS.keySet().iterator().next());
    }
    public static void receive(WeaponImpactPacket packet) {
        clean();
        if(world==null || packet.style()<1 || packet.style()>2
                || !Double.isFinite(packet.x()) || !Double.isFinite(packet.y())
                || !Double.isFinite(packet.z()) || !Float.isFinite(packet.yaw()))return;
        IMPACTS.add(new Impact(packet,world.getGameTime()));
        if(IMPACTS.size()>16)IMPACTS.remove(0);
    }

    @SubscribeEvent
    public static void render(RenderLevelStageEvent event) {
        var stage=event.getStage();
        if(stage==RenderLevelStageEvent.Stage.AFTER_SKY||stage==RenderLevelStageEvent.Stage.AFTER_LEVEL) {
            discardPendingGlow();return;
        }
        if(stage==RenderLevelStageEvent.Stage.AFTER_PARTICLES) {drawPendingGlow(event);return;}
        if(stage!=RenderLevelStageEvent.Stage.AFTER_BLOCK_ENTITIES)return;
        // Opaque models precede translucent blocks/particles, including Fabulous depth-target copies.
        // The previous frame may have aborted before AFTER_PARTICLES, so release its CPU packet here.
        discardPendingGlow();
        clean();
        Minecraft mc=Minecraft.getInstance();
        if(world==null || mc.player==null)return;
        Vec3 camera=event.getCamera().getPosition();
        float partial=event.getPartialTick();
        Matrix4f matrix=event.getPoseStack().last().pose();
        List<Guardian> guardians=new ArrayList<>();
        var players=world.players().stream().filter(p->p.isAlive() && !p.isSpectator()
                && !p.isInvisibleTo(mc.player) && p.distanceToSqr(camera)<48*48
                && ImperialWeaponEffects.style(p.getMainHandItem())!=0)
                .sorted(Comparator.comparingDouble(p->p.distanceToSqr(camera))).limit(6).toList();
        Set<UUID> active=new HashSet<>();
        for(var p:players)active.add(p.getUUID());
        HELD.keySet().retainAll(active);
        if(players.isEmpty() && IMPACTS.isEmpty() && DESCENTS.isEmpty())return;
        FACES.clear();
        DRAGONS.clear();
        int attackReservation=visibleAttackReservation(camera,partial);
        try(ImperialRenderState state=new ImperialRenderState()) {
        BUFFER.begin(VertexFormat.Mode.QUADS,DefaultVertexFormat.POSITION_COLOR);
        BufferBuilder.RenderedBuffer glow=null;
        try {
            for(var player:players) {
                int style=ImperialWeaponEffects.style(player.getMainHandItem());
                Held held=HELD.get(player.getUUID());
                if(held==null || held.style!=style) {
                    held=new Held(style,world.getGameTime()); HELD.put(player.getUUID(),held);
                }
                double time=world.getGameTime()+partial;
                double formation=Math.min(1,(time-held.born)/18.0);
                double yaw=Math.toRadians(net.minecraft.util.Mth.rotLerp(partial,player.yRotO,player.getYRot()));
                Vec3 forward=new Vec3(-Math.sin(yaw),0,Math.cos(yaw));
                Vec3 right=new Vec3(Math.cos(yaw),0,Math.sin(yaw));
                Vec3 position=player.getPosition(partial);
                boolean firstPerson=player==mc.player && mc.options.getCameraType().isFirstPerson();
                // Behind the shoulders: readable in third person without covering the crosshair.
                Vec3 back=position.add(0,1.65,0).subtract(forward.scale(.85)).subtract(camera);
                // Reserve mesh budget for active attacks before spending it on decorative auras.
                int auraFaces=ImperialDragonMesh.FACES.size()*(style==1?2:1);
                if(style==2 && guardians.size()<2 && player.distanceToSqr(camera)<32*32) {
                    float facing=net.minecraft.util.Mth.rotLerp(partial,player.yRotO,player.getYRot());
                    guardians.add(new Guardian(com.dynasty.GuanYuAvatarShape.origin(position,facing).subtract(camera),
                            facing,Math.min(1,(time-held.born)/40.0)));
                }
                if(style==1 && !firstPerson && meshFaces()+auraFaces<=120000-attackReservation)
                    geometry(matrix,back,right,new Vec3(0,1,0),forward,.78+.22*formation)
                        .aura(style,time,formation*.72);
                float swing=player.getAttackAnim(partial);
                if(swing>0) {
                    Vec3 aim=player.getViewVector(partial);
                    Vec3 up=aim.cross(right).normalize();
                    Vec3 center=player.getEyePosition(partial).add(aim.scale(1.65)).add(0,-.55,0).subtract(camera);
                    // Lower arc remains below the sight line, with a short fade at both ends.
                    geometry(matrix,center,right,up,aim,1).slash(style,swing,Math.sin(swing*Math.PI)*.8);
                }
            }
            for(Descent effect:DESCENTS.values()) {
                var p=effect.packet;
                updateTarget(effect,partial);
                Vec3 center=effect.position.subtract(camera);
                if(center.lengthSqr()>64*64)continue;
                double age=Math.max(0,world.getGameTime()-p.started()+partial);
                double fade=effect.finished<0?1:Math.max(0,1-(world.getGameTime()-effect.finished+partial)/12.0);
                double yaw=Math.toRadians(p.yaw());
                Vec3 forward=new Vec3(-Math.sin(yaw),0,Math.cos(yaw)),right=new Vec3(Math.cos(yaw),0,Math.sin(yaw));
                var phase=ImperialWeaponGeometry.descentPhase(age,QinglongDescent.DRAGON_START_TICK,QinglongDescent.WINDUP_TICKS);
                double floor=-effect.halfHeight+.045;
                geometry(matrix,center,right,new Vec3(0,1,0),forward,1)
                        .sealCage(age,phase.charge(),phase.connection(),floor,effect.headOffset,
                                ImperialWeaponGeometry.DESCENT_SEAL_RADIUS,fade);
                if(phase.dragonAlpha()>0 && fade>0 && meshFaces()+ImperialDragonMesh.FACES.size()<=120000) {
                    var offset=ImperialWeaponGeometry.descentDragonOrigin(effect.headOffset,phase.travel());
                    Vec3 dragonOrigin=center.add(right.scale(offset.x())).add(0,offset.y(),0).add(forward.scale(offset.z()));
                    geometry(matrix,dragonOrigin,right,new Vec3(0,1,0),forward,1)
                            .dragon(new ImperialWeaponGeometry.P(0,0,0),ImperialWeaponGeometry.DESCENT_DRAGON_SIZE,
                                    Math.PI*.75,age,0x36cbbb,phase.dragonAlpha()*fade);
                }
                if(effect.finished>=0)geometry(matrix,center.add(0,floor,0),right,forward,new Vec3(0,1,0),
                        ImperialWeaponGeometry.DESCENT_SEAL_RADIUS+(1-fade)*.9)
                        .summonSeal(age,fade);
            }
            for(Impact effect:IMPACTS) {
                var p=effect.packet;
                if(p.style()==2 && meshFaces()+ImperialDragonMesh.FACES.size()>120000)continue;
                Vec3 center=new Vec3(p.x(),p.y(),p.z()).subtract(camera);
                if(center.lengthSqr()>48*48)continue;
                double age=world.getGameTime()-effect.born+partial;
                double alpha=Math.min(1,age/3)*Math.max(0,1-age/24);
                // Fixed world orientation; never rotates around the viewer like a billboard decal.
                double yaw=Math.toRadians(p.yaw());
                Vec3 forward=new Vec3(-Math.sin(yaw),0,Math.cos(yaw));
                Vec3 right=new Vec3(Math.cos(yaw),0,Math.sin(yaw));
                geometry(matrix,center,right,new Vec3(0,1,0),forward,1)
                        .impact(p.style(),age/24,alpha);
            }
            glow=BUFFER.end();
            drawFaces(matrix);
            for(Guardian guardian:guardians)HouyiAvatarRenderer.drawGuanYu(matrix,guardian.origin,guardian.yaw,guardian.formed);
            if(glow.isEmpty())glow.release();
            else pendingGlow=new PendingGlow(glow,world,event.getRenderTick(),partial,
                    new Matrix4f(RenderSystem.getModelViewMatrix()),new Matrix4f(event.getProjectionMatrix()));
            glow=null; // Ownership moves to AFTER_PARTICLES, or was released immediately if empty.
        } finally {
            if(BUFFER.building()) {
                var unfinished=BUFFER.endOrDiscardIfEmpty();
                if(unfinished!=null)unfinished.release();
            }
            if(glow!=null)glow.release();
            FACES.clear();DRAGONS.clear();
        }
        }
    }

    private static void drawPendingGlow(RenderLevelStageEvent event) {
        clean();
        PendingGlow ready=pendingGlow;pendingGlow=null;
        if(ready==null)return;
        if(ready.level!=world||ready.tick!=event.getRenderTick()||Float.compare(ready.partial,event.getPartialTick())!=0) {
            ready.buffer.release();return;
        }
        boolean uploaded=false;
        try(ImperialRenderState state=new ImperialRenderState()) {
            RenderSystem.enableDepthTest();RenderSystem.depthMask(false);RenderSystem.disableCull();
            RenderSystem.enableBlend();RenderSystem.blendFunc(GL11.GL_SRC_ALPHA,GL11.GL_ONE);
            if(!ImperialMaterialShader.bindGlow())RenderSystem.setShader(GameRenderer::getPositionColorShader);
            if(glowBuffer==null||glowBuffer.isInvalid())glowBuffer=new VertexBuffer(VertexBuffer.Usage.DYNAMIC);
            glowBuffer.bind();
            try {
                uploaded=true; // VertexBuffer.upload consumes/releases the packet even if upload fails.
                glowBuffer.upload(ready.buffer);
                glowBuffer.drawWithShader(ready.modelView,ready.projection,RenderSystem.getShader());
            } finally {VertexBuffer.unbind();}
        } finally {
            if(!uploaded)ready.buffer.release();
        }
    }

    private static int meshFaces(){return FACES.size()+DRAGONS.size()*ImperialDragonMesh.FACES.size();}
    private static int visibleAttackReservation(Vec3 camera,float partial) {
        int count=0;
        for(Descent effect:DESCENTS.values()) {
            double age=Math.max(0,world.getGameTime()-effect.packet.started()+partial);
            double fade=effect.finished<0?1:Math.max(0,1-(world.getGameTime()-effect.finished+partial)/12.0);
            updateTarget(effect,partial);
            if(age>QinglongDescent.DRAGON_START_TICK&&fade>0&&effect.position.distanceToSqr(camera)<=64*64)count++;
        }
        // Remote, expired and still-only-forming seals must not hide a local pair of golden dragons.
        return Math.min(count,120000/ImperialDragonMesh.FACES.size())*ImperialDragonMesh.FACES.size();
    }

    private static void drawFaces(Matrix4f matrix) {
        if(FACES.isEmpty()&&DRAGONS.isEmpty())return;
        RenderSystem.enableDepthTest();
        RenderSystem.depthMask(true);
        RenderSystem.disableBlend();
        RenderSystem.disableCull();
        for(var dragon:DRAGONS)ImperialDragonRenderer.draw(matrix,dragon);
        if(FACES.isEmpty())return;
        boolean shader=ImperialMaterialShader.bind(matrix,HouyiAvatarRenderer.sceneLight(Vec3.ZERO));
        if(!shader)RenderSystem.setShader(GameRenderer::getPositionColorShader);
        BODY_BUFFER.begin(VertexFormat.Mode.QUADS,shader?DefaultVertexFormat.POSITION_COLOR_NORMAL:DefaultVertexFormat.POSITION_COLOR);
        for(Face face:FACES) {
            float opacity=(float)Math.min(1,face.alpha*1.4);
            bodyVertex(matrix,face.a,face.na,face.color,opacity,shader);
            bodyVertex(matrix,face.b,face.nb,face.color,opacity,shader);
            bodyVertex(matrix,face.c,face.nc,face.color,opacity,shader);
            bodyVertex(matrix,face.d,face.nd,face.color,opacity,shader);
        }
        BufferUploader.drawWithShader(BODY_BUFFER.end());
    }

    private static void bodyVertex(Matrix4f matrix,Vec3 p,Vec3 normal,int color,float alpha,boolean shader) {
        float shade=shader?1:(float)(.35+.65*Math.max(0,normal.dot(new Vec3(-.45,.8,.6).normalize())));
        BODY_BUFFER.vertex(matrix,(float)p.x,(float)p.y,(float)p.z)
                .color(((color>>16)&255)/255f*shade,((color>>8)&255)/255f*shade,(color&255)/255f*shade,alpha);
        if(shader)BODY_BUFFER.normal((float)normal.x,(float)normal.y,(float)normal.z);
        BODY_BUFFER.endVertex();
    }

    private static ImperialWeaponGeometry geometry(Matrix4f matrix,Vec3 origin,Vec3 x,Vec3 y,Vec3 z,double scale) {
        return new ImperialWeaponGeometry((a,b,width,color,alpha)-> {
            Vec3 start=origin.add(x.scale(a.x()*scale)).add(y.scale(a.y()*scale)).add(z.scale(a.z()*scale));
            Vec3 end=origin.add(x.scale(b.x()*scale)).add(y.scale(b.y()*scale)).add(z.scale(b.z()*scale));
            Vec3 side=end.subtract(start).cross(start.add(end).scale(.5));
            if(side.lengthSqr()<1e-10 || width<=0 || alpha<=0)return;
            side=side.normalize();
            for(int pass=0;pass<2;pass++) {
                Vec3 offset=side.scale(width*scale*(pass==0?2.6:1));
                float opacity=(float)Math.min(1,alpha*(pass==0?.12:.72));
                vertex(matrix,start.add(offset),color,opacity);
                vertex(matrix,start.subtract(offset),color,opacity);
                vertex(matrix,end.subtract(offset),color,opacity);
                vertex(matrix,end.add(offset),color,opacity);
            }
        },new ImperialWeaponGeometry.Surface() {
            public boolean dragonInstance(ImperialWeaponGeometry.P local,double size,double angle,int color,double alpha,boolean mirrored) {
                if(!ImperialMaterialShader.available())return false;
                if(alpha<=0||meshFaces()+ImperialDragonMesh.FACES.size()>120000)return true;
                Matrix4f pose=new Matrix4f().m00((float)(x.x*scale)).m01((float)(x.y*scale)).m02((float)(x.z*scale))
                        .m10((float)(y.x*scale)).m11((float)(y.y*scale)).m12((float)(y.z*scale))
                        .m20((float)(z.x*scale)).m21((float)(z.y*scale)).m22((float)(z.z*scale))
                        .m30((float)origin.x).m31((float)origin.y).m32((float)origin.z)
                        .translate((float)local.x(),(float)local.y(),(float)local.z()).rotateZ((float)angle)
                        .scale((float)(mirrored?-size:size),(float)size,(float)size);
                DRAGONS.add(new ImperialDragonRenderer.Instance(pose,((color>>16)&255)<150,(float)Math.min(1,alpha*1.4)));
                return true;
            }
            public void face(ImperialWeaponGeometry.P a,ImperialWeaponGeometry.P b,ImperialWeaponGeometry.P c,
                             ImperialWeaponGeometry.P d,int color,double alpha) {
                Vec3 aa=new Vec3(a.x(),a.y(),a.z()),bb=new Vec3(b.x(),b.y(),b.z()),cc=new Vec3(c.x(),c.y(),c.z());
                Vec3 n=bb.subtract(aa).cross(cc.subtract(aa)).normalize();
                var normal=new ImperialWeaponGeometry.P(n.x,n.y,n.z);
                normalFace(a,b,c,d,color,alpha,normal,normal,normal,normal);
            }
            public void normalFace(ImperialWeaponGeometry.P a,ImperialWeaponGeometry.P b,ImperialWeaponGeometry.P c,
                                   ImperialWeaponGeometry.P d,int color,double alpha,ImperialWeaponGeometry.P na,
                                   ImperialWeaponGeometry.P nb,ImperialWeaponGeometry.P nc,ImperialWeaponGeometry.P nd) {
                if(alpha<=0 || meshFaces()>=120000)return;
                FACES.add(new Face(point(origin,x,y,z,a,scale),point(origin,x,y,z,b,scale),point(origin,x,y,z,c,scale),
                        point(origin,x,y,z,d,scale),color,alpha,point(Vec3.ZERO,x,y,z,na,1),
                        point(Vec3.ZERO,x,y,z,nb,1),point(Vec3.ZERO,x,y,z,nc,1),point(Vec3.ZERO,x,y,z,nd,1)));
            }
        });
    }
    private static Vec3 point(Vec3 origin,Vec3 x,Vec3 y,Vec3 z,ImperialWeaponGeometry.P p,double scale) {
        return origin.add(x.scale(p.x()*scale)).add(y.scale(p.y()*scale)).add(z.scale(p.z()*scale));
    }
    private static void vertex(Matrix4f matrix,Vec3 p,int color,float alpha) {
        BUFFER.vertex(matrix,(float)p.x,(float)p.y,(float)p.z)
                .color(((color>>16)&255)/255f,((color>>8)&255)/255f,(color&255)/255f,alpha).endVertex();
    }
    private ImperialWeaponRenderer() {}
}
