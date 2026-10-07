package com.dynasty.worldevent.client;

import com.dynasty.blueprint.BlueprintEntities;
import com.dynasty.blueprint.TemplateMob;
import com.dynasty.worldevent.WorldEventStatePacket;
import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.*;
import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.renderer.GameRenderer;
import net.minecraft.client.renderer.LightTexture;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.ClientPlayerNetworkEvent;
import net.minecraftforge.client.event.RenderLevelStageEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.*;

/** Bounded render-only companions. No client entity is inserted into a world or has an AI tick. */
@Mod.EventBusSubscriber(modid="dynasty",value=Dist.CLIENT)
public final class WorldEventVisuals {
    private static final Map<UUID,WorldEventStatePacket> STATES=new LinkedHashMap<>();
    private static final Map<UUID,List<TemplateMob>> PHANTOMS=new HashMap<>();
    private static ClientLevel world;
    private static long celestialDraws;
    public static int activeStates(){return STATES.size();}
    public static int phantomCount(){return PHANTOMS.values().stream().mapToInt(List::size).sum();}
    public static boolean has(String id){return STATES.values().stream().anyMatch(p->p.definition().getPath().equals(id));}
    public static boolean hasActive(String id){return STATES.values().stream().anyMatch(p->p.phase()==2&&p.definition().getPath().equals(id));}
    public static long celestialDraws(){return celestialDraws;}
    public static boolean processionFog(){
        var mc=Minecraft.getInstance();return mc.level!=null&&mc.player!=null&&mc.player.isAlive()&&world==mc.level
            &&STATES.values().stream().anyMatch(p->p.definition().getPath().equals("yinbing_jiedao")&&p.phase()<3
                &&p.dimension().equals(mc.level.dimension().location())&&p.center().distToCenterSqr(mc.player.position())<64*64);
    }
    @SubscribeEvent public static void fog(net.minecraftforge.client.event.ViewportEvent.RenderFog event){
        if(!processionFog()||event.getType()!=net.minecraft.world.level.material.FogType.NONE)return;
        // Vanilla recomputes these values for every view. We retain no camera/fog state to restore.
        event.setNearPlaneDistance(Math.min(event.getNearPlaneDistance(),4));
        event.setFarPlaneDistance(Math.min(event.getFarPlaneDistance(),40));event.setCanceled(true);
    }
    public static void receive(WorldEventStatePacket p){
        var mc=Minecraft.getInstance();if(mc.level==null||!mc.level.dimension().location().equals(p.dimension())||p.phase()<0||p.phase()>4)return;
        if(world!=mc.level){clear();world=mc.level;}
        if(p.phase()>=3){STATES.remove(p.uuid());PHANTOMS.remove(p.uuid());return;}
        if(STATES.containsKey(p.uuid())||STATES.size()<3)STATES.put(p.uuid(),p);
    }
    public static void clear(){STATES.clear();PHANTOMS.clear();world=null;celestialDraws=0;}
    @SubscribeEvent public static void logout(ClientPlayerNetworkEvent.LoggingOut e){clear();}
    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent e){
        if(e.phase!=TickEvent.Phase.END)return;var mc=Minecraft.getInstance();
        if(mc.level==null||mc.player==null||mc.level!=world||!mc.player.isAlive()){clear();return;}
        STATES.entrySet().removeIf(entry->{var p=entry.getValue();boolean remove=!p.dimension().equals(mc.level.dimension().location())
            ||mc.level.getGameTime()>=p.expires()||mc.player.blockPosition().distSqr(p.center())>128*128;
            if(remove)PHANTOMS.remove(p.uuid());return remove;});
        if(mc.level.getGameTime()%5!=0)return;
        for(var p:STATES.values())if(p.phase()==2&&mc.player.blockPosition().distSqr(p.center())<64*64){
            if(p.definition().getPath().equals("yinbing_jiedao")){
                double direction=(p.seed()&1)==0?1:-1;
                for(int n=0;n<10;n++)mc.level.addParticle(ParticleTypes.SOUL_FIRE_FLAME,p.center().getX()+direction*n*5,p.center().getY()+.1,p.center().getZ(),0,.005,0);
            }else if(p.definition().getPath().equals("xuanniao_zhige")){
                var random=mc.level.random;
                for(int n=0;n<6;n++)mc.level.addParticle(ParticleTypes.END_ROD,p.center().getX()+random.nextInt(49)-24,p.center().getY()+8+random.nextInt(16),p.center().getZ()+random.nextInt(49)-24,0,-.08,0);
            }
        }
    }
    @SubscribeEvent public static void render(RenderLevelStageEvent event){
        if(event.getStage()!=RenderLevelStageEvent.Stage.AFTER_ENTITIES)return;var mc=Minecraft.getInstance();
        if(mc.level==null||mc.player==null||world!=mc.level||!mc.player.isAlive())return;
        var camera=event.getCamera().getPosition();var pose=event.getPoseStack();var buffers=mc.renderBuffers().bufferSource();
        for(var p:STATES.values()){
            if(p.phase()!=2||p.center().distToCenterSqr(camera)>64*64)continue;
            float age=mc.level.getGameTime()-p.started()+event.getPartialTick();
            if(p.definition().getPath().equals("yinbing_jiedao")){
                var phantom=PHANTOMS.computeIfAbsent(p.uuid(),id->{var mobs=new ArrayList<TemplateMob>();
                    for(int n=0;n<8;n++){var mob=BlueprintEntities.YINBING_GUIZU.get().create(mc.level);if(mob!=null){mob.setNoAi(true);mob.getPersistentData().putBoolean("DynastyEventPhantom",true);mobs.add(mob);}}return mobs;});
                double direction=(p.seed()&1)==0?1:-1;double progress=Math.min(50,Math.max(0,age-160)*.035);
                for(int n=0;n<phantom.size();n++){
                    var mob=phantom.get(n);double x=p.center().getX()+direction*(progress-(n/2)*2),y=p.center().getY(),z=p.center().getZ()+(n%2==0?-2:2);
                    mob.tickCount=(int)age;mob.walkAnimation.update(.3F,.3F);mob.setPos(x,y,z);float yaw=direction>0?-90:90;mob.setYRot(yaw);mob.yBodyRot=yaw;mob.yHeadRot=yaw;
                    mc.getEntityRenderDispatcher().render(mob,x-camera.x,y-camera.y,z-camera.z,yaw,event.getPartialTick(),pose,buffers,LightTexture.FULL_BRIGHT);
                }
            }else if(p.definition().getPath().equals("xuanniao_zhige")){
                buffers.endBatch();pose.pushPose();
                try{pose.translate(p.center().getX()-camera.x+(age-200)*.18,p.center().getY()+32-camera.y,p.center().getZ()-camera.z);
                    bird(pose,age);
                }finally{pose.popPose();}
            }
        }
        buffers.endBatch();
    }
    private static void bird(PoseStack pose,float age){
        celestialDraws++;
        var b=Tesselator.getInstance().getBuilder();var matrix=pose.last().pose();float flap=(float)Math.sin(age*.045)*3;
        RenderSystem.enableBlend();RenderSystem.defaultBlendFunc();RenderSystem.disableCull();RenderSystem.setShader(GameRenderer::getPositionColorShader);
        try{
            b.begin(VertexFormat.Mode.TRIANGLES,DefaultVertexFormat.POSITION_COLOR);
            triangle(b,matrix,0,0,-7,-2,0,2,2,0,2);triangle(b,matrix,-1,0,0,-27,flap,5,-7,1,7);triangle(b,matrix,1,0,0,7,1,7,27,flap,5);
            triangle(b,matrix,-1,0,2,-3,0,15,0,0,10);triangle(b,matrix,1,0,2,0,0,10,3,0,15);
            BufferUploader.drawWithShader(b.end());
        }finally{RenderSystem.enableCull();RenderSystem.disableBlend();}
    }
    private static void triangle(BufferBuilder b,org.joml.Matrix4f matrix,float ax,float ay,float az,float bx,float by,float bz,float cx,float cy,float cz){
        b.vertex(matrix,ax,ay,az).color(1F,.77F,.16F,.68F).endVertex();b.vertex(matrix,bx,by,bz).color(1F,.77F,.16F,.68F).endVertex();b.vertex(matrix,cx,cy,cz).color(1F,.77F,.16F,.68F).endVertex();
    }
    private WorldEventVisuals(){}
}
