package com.dynasty.client;

import com.dynasty.cod3.Cod3VisualPacket;
import com.mojang.blaze3d.vertex.*;
import com.mojang.math.Axis;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.*;
import net.minecraft.client.renderer.entity.LivingEntityRenderer;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.client.renderer.texture.TextureAtlas;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.*;
import net.minecraft.world.phys.Vec3;
import software.bernie.geckolib.renderer.GeoEntityRenderer;
import software.bernie.geckolib.cache.object.*;
import software.bernie.geckolib.event.GeoRenderEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.api.distmarker.Dist;
import java.util.*;

/** Bounded pose history reuses registered models and restores shared animation state after each ghost. */
@Mod.EventBusSubscriber(modid="dynasty",value=Dist.CLIENT)
final class Cod3AfterImages {
    private record Bone(float x,float y,float z,float rx,float ry,float rz,float sx,float sy,float sz,boolean hidden,boolean children) {
        static Bone of(GeoBone b){return new Bone(b.getPosX(),b.getPosY(),b.getPosZ(),b.getRotX(),b.getRotY(),b.getRotZ(),b.getScaleX(),b.getScaleY(),b.getScaleZ(),b.isHidden(),b.isHidingChildren());}
        void apply(GeoBone b){b.setPosX(x);b.setPosY(y);b.setPosZ(z);b.setRotX(rx);b.setRotY(ry);b.setRotZ(rz);b.setScaleX(sx);b.setScaleY(sy);b.setScaleZ(sz);b.setHidden(hidden);b.setChildrenHidden(children);}
    }
    private record Frame(Vec3 at,float yaw,float pitch,float head,float swing,float walk,float speed,float time,boolean baby,boolean riding,ItemStack weapon,long tick,List<Bone> bones) {
        Frame withBones(List<Bone> saved){return new Frame(at,yaw,pitch,head,swing,walk,speed,time,baby,riding,weapon,tick,saved);}
        Frame at(Vec3 position){return new Frame(position,yaw,pitch,head,swing,walk,speed,time,baby,riding,weapon,tick,bones);}
    }
    private static final Map<Cod3VisualPacket,Deque<Frame>> FRAMES=new HashMap<>();
    private static final Map<UUID,Deque<Frame>> HISTORY=new HashMap<>();
    private static boolean renderingGhost;
    static boolean supports(Cod3VisualPacket packet){return packet.sequence().equals("mesh_entity")||packet.sequence().equals("mesh_weapon")||packet.sequence().equals("mesh_mirror");}
    static void clear(){FRAMES.clear();HISTORY.clear();}
    static void retain(List<Cod3VisualPacket> active){FRAMES.keySet().retainAll(active);}
    static void history(){
        var mc=Minecraft.getInstance();if(mc.level==null||mc.player==null)return;
        var nearby=mc.level.getEntitiesOfClass(LivingEntity.class,mc.player.getBoundingBox().inflate(32),LivingEntity::isAlive);
        nearby.sort(Comparator.comparingDouble(e->e.distanceToSqr(mc.player)));Set<UUID> keep=new HashSet<>();
        for(var owner:nearby.subList(0,Math.min(32,nearby.size()))){
            keep.add(owner.getUUID());var frames=HISTORY.computeIfAbsent(owner.getUUID(),ignored->new ArrayDeque<>());
            long now=mc.level.getGameTime();if(!frames.isEmpty()&&frames.getLast().tick()==now)continue;
            frames.addLast(new Frame(owner.position(),owner.yBodyRot,owner.getXRot(),owner.getYHeadRot(),owner.getAttackAnim(0),owner.walkAnimation.position(0),owner.walkAnimation.speed(0),owner.tickCount,owner.isBaby(),owner.isPassenger(),owner.getMainHandItem().copy(),now,List.of()));
            while(frames.size()>6)frames.removeFirst();
        }
        HISTORY.keySet().retainAll(keep);
    }
    private static List<GeoBone> bones(BakedGeoModel model){
        List<GeoBone> result=new ArrayList<>();for(var root:model.topLevelBones())collect(root,result);return result;
    }
    private static void collect(GeoBone bone,List<GeoBone> result){result.add(bone);for(var child:bone.getChildBones())collect(child,result);}
    @SubscribeEvent public static void capture(GeoRenderEvent.Entity.Post event){
        if(renderingGhost)return;var frames=HISTORY.get(event.getEntity().getUUID());if(frames==null||frames.isEmpty())return;
        var frame=frames.removeLast();var saved=frame.withBones(bones(event.getModel()).stream().map(Bone::of).toList());frames.addLast(saved);
        for(var entry:FRAMES.entrySet())if(entry.getKey().entityId()==event.getEntity().getId()&&entry.getKey().template()!=23){
            var trail=entry.getValue();if(!trail.isEmpty()&&trail.getLast().tick()==saved.tick()){trail.removeLast();trail.addLast(saved);}
        }
    }
    static void sample(Cod3VisualPacket packet){
        var mc=Minecraft.getInstance();if(mc.level==null||!supports(packet))return;
        var entity=mc.level.getEntity(packet.entityId());
        if(!(entity instanceof LivingEntity owner)||!owner.isAlive()||owner.getUUID().getLeastSignificantBits()!=packet.seed())return;
        var frames=FRAMES.computeIfAbsent(packet,ignored->new ArrayDeque<>());var history=HISTORY.get(owner.getUUID());
        if(history==null||history.isEmpty())return;
        if(packet.template()==23){
            // Preserve poses from before teleport; later owner movement cannot mutate this trail.
            if(frames.isEmpty()){
                Vec3 last=history.getLast().at();for(var frame:history)frames.addLast(frame.at(packet.origin().add(frame.at().subtract(last))));
                while(frames.size()>5)frames.removeFirst();
            }return;
        }
        var frame=history.getLast();if(!frames.isEmpty()&&frame.tick()==frames.getLast().tick())return;
        frames.addLast(frame);while(frames.size()>(packet.template()==36?1:6))frames.removeFirst();
    }
    @SuppressWarnings({"rawtypes","unchecked"})
    static void render(Cod3VisualPacket packet,PoseStack pose,Vec3 camera,float partialTick,double fade,int count){
        var mc=Minecraft.getInstance();var frames=FRAMES.get(packet);if(mc.level==null||frames==null)return;
        var entity=mc.level.getEntity(packet.entityId());
        if(!(entity instanceof LivingEntity owner)||!owner.isAlive()||owner.getUUID().getLeastSignificantBits()!=packet.seed())return;
        // The local body's ghost is hidden in first person. Weapon samples stay outside the near plane.
        if(packet.template()!=29&&packet.template()!=36&&owner==mc.player&&mc.options.getCameraType().isFirstPerson())return;
        var renderer=mc.getEntityRenderDispatcher().getRenderer(owner);var buffers=mc.renderBuffers().bufferSource();
        int tint=packet.tint()==0?0xffffff:packet.tint(),index=0,total=frames.size();
        for(var frame:frames){
            if(index++<Math.max(0,total-count)||frame.at().distanceTo(camera)>64||packet.template()!=29&&frame.at().distanceTo(camera)<1.4)continue;
            float alpha=(float)(fade*(packet.template()==23?.3:.35)*index/total);if(alpha<=0)continue;
            pose.pushPose();
            try{
                if(packet.template()==36){
                    double age=mc.level.getGameTime()-packet.start()+partialTick;
                    if(age>=com.dynasty.cod3.VfxTimeline.timing(com.dynasty.cod3.Cod3Catalog.vfx(36),packet.duration()).sustainEnd())continue;
                    pose.translate(packet.origin().x,packet.origin().y+.1,packet.origin().z);pose.mulPose(Axis.YP.rotationDegrees(180-frame.yaw()));
                    pose.translate(0,0,.57);pose.scale(.8f,.8f,-.015f);
                }else{pose.translate(frame.at().x,frame.at().y,frame.at().z);pose.mulPose(Axis.YP.rotationDegrees(180-(packet.template()==29&&owner==mc.player&&mc.options.getCameraType().isFirstPerson()?frame.head():frame.yaw())));}
                if(packet.template()==29){
                    if(owner==mc.player&&mc.options.getCameraType().isFirstPerson()){
                        // Offset in hand space, away from the crosshair and the near plane.
                        pose.translate(.62,owner.getEyeHeight()-.45,-.85);
                        pose.mulPose(Axis.XP.rotationDegrees(frame.pitch()));pose.mulPose(Axis.ZP.rotationDegrees(-110*frame.swing()));
                        weapon(frame.weapon(),pose,buffers,tint,alpha);
                    }else if(renderer instanceof LivingEntityRenderer living&&living.getModel() instanceof net.minecraft.client.model.ArmedModel armed){
                        var model=living.getModel();boolean young=model.young,riding=model.riding;float attack=model.attackTime;
                        try{
                            model.young=frame.baby();model.riding=frame.riding();model.attackTime=frame.swing();
                            model.prepareMobModel(owner,frame.walk(),frame.speed(),0);model.setupAnim(owner,frame.walk(),frame.speed(),frame.time(),frame.head()-frame.yaw(),frame.pitch());
                            pose.scale(-1,-1,1);pose.translate(0,-1.501,0);armed.translateToHand(owner.getMainArm(),pose);
                            pose.mulPose(Axis.XP.rotationDegrees(-90));pose.mulPose(Axis.YP.rotationDegrees(180));
                            boolean left=owner.getMainArm()==net.minecraft.world.entity.HumanoidArm.LEFT;
                            pose.translate(left?-1./16:1./16,.125,-.625);
                            weapon(frame.weapon(),pose,buffers,tint,alpha,left?ItemDisplayContext.THIRD_PERSON_LEFT_HAND:ItemDisplayContext.THIRD_PERSON_RIGHT_HAND);
                        }finally{
                            model.young=young;model.riding=riding;model.attackTime=attack;
                            model.prepareMobModel(owner,owner.walkAnimation.position(partialTick),owner.walkAnimation.speed(partialTick),partialTick);
                            model.setupAnim(owner,owner.walkAnimation.position(partialTick),owner.walkAnimation.speed(partialTick),owner.tickCount+partialTick,owner.getYHeadRot()-owner.yBodyRot,owner.getXRot());
                        }
                    }else{
                        pose.translate(.35,owner.getBbHeight()*.7,-.55);pose.mulPose(Axis.XP.rotationDegrees(frame.pitch()));pose.mulPose(Axis.ZP.rotationDegrees(-110*frame.swing()));
                        weapon(frame.weapon(),pose,buffers,tint,alpha);
                    }
                }else if(renderer instanceof LivingEntityRenderer living){
                    var model=living.getModel();boolean young=model.young,riding=model.riding;float attack=model.attackTime;
                    try{
                        model.young=frame.baby();model.riding=frame.riding();model.attackTime=frame.swing();
                        model.prepareMobModel(owner,frame.walk(),frame.speed(),0);
                        model.setupAnim(owner,frame.walk(),frame.speed(),frame.time(),frame.head()-frame.yaw(),frame.pitch());
                        pose.scale(-1,-1,1);pose.translate(0,-1.501,0);
                        model.renderToBuffer(pose,buffers.getBuffer(Cod3GhostRenderType.of(renderer.getTextureLocation(owner))),15728880,OverlayTexture.NO_OVERLAY,(tint>>16&255)/255f,(tint>>8&255)/255f,(tint&255)/255f,alpha);
                    }finally{
                        model.young=young;model.riding=riding;model.attackTime=attack;
                        model.prepareMobModel(owner,owner.walkAnimation.position(partialTick),owner.walkAnimation.speed(partialTick),partialTick);
                        model.setupAnim(owner,owner.walkAnimation.position(partialTick),owner.walkAnimation.speed(partialTick),owner.tickCount+partialTick,owner.getYHeadRot()-owner.yBodyRot,owner.getXRot());
                    }
                }else if(renderer instanceof GeoEntityRenderer geo&&owner instanceof software.bernie.geckolib.core.animatable.GeoAnimatable animatable){
                    var model=geo.getGeoModel();var baked=(BakedGeoModel)model.getBakedModel(model.getModelResource(animatable));
                    var parts=bones(baked);var restore=parts.stream().map(Bone::of).toList();
                    if(frame.bones().size()!=parts.size())continue;
                    var type=Cod3GhostRenderType.of(renderer.getTextureLocation(owner));
                    try{
                        renderingGhost=true;for(int i=0;i<parts.size();i++)frame.bones().get(i).apply(parts.get(i));
                        geo.reRender(baked,pose,buffers,animatable,type,buffers.getBuffer(type),partialTick,15728880,OverlayTexture.NO_OVERLAY,(tint>>16&255)/255f,(tint>>8&255)/255f,(tint&255)/255f,alpha);
                    }finally{for(int i=0;i<parts.size();i++)restore.get(i).apply(parts.get(i));renderingGhost=false;}

                }
            }finally{pose.popPose();}
        }
        buffers.endBatch();
    }
    /** QA uses the same baked-item path without creating a world or duplicating a model. */
    static void weapon(ItemStack stack,PoseStack pose,MultiBufferSource buffers,int tint,float alpha){
        weapon(stack,pose,buffers,tint,alpha,ItemDisplayContext.THIRD_PERSON_RIGHT_HAND);
    }
    static void weapon(ItemStack stack,PoseStack pose,MultiBufferSource buffers,int tint,float alpha,ItemDisplayContext context){
        if(stack.isEmpty())return;
        var consumer=new Tint(buffers.getBuffer(Cod3GhostRenderType.of(TextureAtlas.LOCATION_BLOCKS)),tint,alpha);
        Minecraft.getInstance().getItemRenderer().renderStatic(stack,context,15728880,OverlayTexture.NO_OVERLAY,pose,type->type.format().equals(DefaultVertexFormat.NEW_ENTITY)?consumer:Discard.INSTANCE,null,0);
    }
    private enum Discard implements VertexConsumer {
        INSTANCE;
        public VertexConsumer vertex(double x,double y,double z){return this;}
        public VertexConsumer color(int r,int g,int b,int a){return this;}
        public VertexConsumer uv(float u,float v){return this;}
        public VertexConsumer overlayCoords(int u,int v){return this;}
        public VertexConsumer uv2(int u,int v){return this;}
        public VertexConsumer normal(float x,float y,float z){return this;}
        public void endVertex(){}
        public void defaultColor(int r,int g,int b,int a){}
        public void unsetDefaultColor(){}
    }
    private record Tint(VertexConsumer delegate,int tint,float alpha) implements VertexConsumer {
        public VertexConsumer vertex(double x,double y,double z){delegate.vertex(x,y,z);return this;}
        public VertexConsumer color(int r,int g,int b,int a){delegate.color(r*(tint>>16&255)/255,g*(tint>>8&255)/255,b*(tint&255)/255,Math.round(a*alpha));return this;}
        public VertexConsumer uv(float u,float v){delegate.uv(u,v);return this;}
        public VertexConsumer overlayCoords(int u,int v){delegate.overlayCoords(u,v);return this;}
        public VertexConsumer uv2(int u,int v){delegate.uv2(u,v);return this;}
        public VertexConsumer normal(float x,float y,float z){delegate.normal(x,y,z);return this;}
        public void endVertex(){delegate.endVertex();}
        public void defaultColor(int r,int g,int b,int a){delegate.defaultColor(r*(tint>>16&255)/255,g*(tint>>8&255)/255,b*(tint&255)/255,Math.round(a*alpha));}
        public void unsetDefaultColor(){delegate.unsetDefaultColor();}
    }
    private Cod3AfterImages(){}
}
