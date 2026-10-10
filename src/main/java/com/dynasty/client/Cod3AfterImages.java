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
import java.util.*;

/** Six bounded transform samples, reusing the registered entity or baked item model. No visual entities. */
final class Cod3AfterImages {
    private record Frame(Vec3 at,float yaw,float pitch,float swing,ItemStack weapon,long tick) {}
    private static final Map<Cod3VisualPacket,Deque<Frame>> FRAMES=new HashMap<>();
    static boolean supports(Cod3VisualPacket packet){return packet.sequence().equals("mesh_entity")||packet.sequence().equals("mesh_weapon");}
    static void clear(){FRAMES.clear();}
    static void retain(List<Cod3VisualPacket> active){FRAMES.keySet().retainAll(active);}
    static void sample(Cod3VisualPacket packet){
        var mc=Minecraft.getInstance();if(mc.level==null||!supports(packet))return;
        var entity=mc.level.getEntity(packet.entityId());
        if(!(entity instanceof LivingEntity owner)||!owner.isAlive()||owner.getUUID().getLeastSignificantBits()!=packet.seed())return;
        var frames=FRAMES.computeIfAbsent(packet,ignored->new ArrayDeque<>());long now=mc.level.getGameTime();
        if(!frames.isEmpty()&&now-frames.getLast().tick()<2)return;
        Vec3 position=packet.template()==23?packet.origin():owner.position();
        frames.addLast(new Frame(position,owner.yBodyRot,owner.getXRot(),owner.getAttackAnim(0),owner.getMainHandItem().copy(),now));
        while(frames.size()>(packet.template()==23?5:6))frames.removeFirst();
    }
    @SuppressWarnings({"rawtypes","unchecked"})
    static void render(Cod3VisualPacket packet,PoseStack pose,Vec3 camera,float partialTick,double fade,int count){
        var mc=Minecraft.getInstance();var frames=FRAMES.get(packet);if(mc.level==null||frames==null)return;
        var entity=mc.level.getEntity(packet.entityId());
        if(!(entity instanceof LivingEntity owner)||!owner.isAlive()||owner.getUUID().getLeastSignificantBits()!=packet.seed())return;
        // The local body's ghost is hidden in first person. Weapon samples stay outside the near plane.
        if(packet.template()!=29&&owner==mc.player&&mc.options.getCameraType().isFirstPerson())return;
        var renderer=mc.getEntityRenderDispatcher().getRenderer(owner);var buffers=mc.renderBuffers().bufferSource();
        int tint=packet.tint()==0?0xffffff:packet.tint(),index=0,total=frames.size();
        for(var frame:frames){
            if(index++<Math.max(0,total-count)||frame.at().distanceTo(camera)>64||frame.at().distanceTo(camera)<1.4)continue;
            float alpha=(float)(fade*.35*index/total);if(alpha<=0)continue;
            pose.pushPose();
            try{
                pose.translate(frame.at().x,frame.at().y,frame.at().z);pose.mulPose(Axis.YP.rotationDegrees(180-frame.yaw()));
                if(packet.template()==29){
                    pose.translate(.35,owner.getBbHeight()*.7,-.55);pose.mulPose(Axis.XP.rotationDegrees(frame.pitch()));
                    pose.mulPose(Axis.ZP.rotationDegrees(-110*frame.swing()));
                    weapon(frame.weapon(),pose,buffers,tint,alpha);
                }else if(renderer instanceof LivingEntityRenderer living){
                    var model=living.getModel();model.young=owner.isBaby();model.riding=owner.isPassenger();model.attackTime=frame.swing();
                    model.prepareMobModel(owner,owner.walkAnimation.position(partialTick),owner.walkAnimation.speed(partialTick),partialTick);
                    model.setupAnim(owner,owner.walkAnimation.position(partialTick),owner.walkAnimation.speed(partialTick),owner.tickCount+partialTick,owner.getYHeadRot()-frame.yaw(),frame.pitch());
                    pose.scale(-1,-1,1);pose.translate(0,-1.501,0);
                    model.renderToBuffer(pose,buffers.getBuffer(Cod3GhostRenderType.of(renderer.getTextureLocation(owner))),15728880,OverlayTexture.NO_OVERLAY,(tint>>16&255)/255f,(tint>>8&255)/255f,(tint&255)/255f,alpha);
                }else if(renderer instanceof GeoEntityRenderer geo&&owner instanceof software.bernie.geckolib.core.animatable.GeoAnimatable animatable){
                    var model=geo.getGeoModel();var baked=model.getBakedModel(model.getModelResource(animatable));
                    var type=Cod3GhostRenderType.of(renderer.getTextureLocation(owner));
                    geo.reRender(baked,pose,buffers,animatable,type,buffers.getBuffer(type),partialTick,15728880,OverlayTexture.NO_OVERLAY,(tint>>16&255)/255f,(tint>>8&255)/255f,(tint&255)/255f,alpha);
                }
            }finally{pose.popPose();}
        }
        buffers.endBatch();
    }
    /** QA uses the same baked-item path without creating a world or duplicating a model. */
    static void weapon(ItemStack stack,PoseStack pose,MultiBufferSource buffers,int tint,float alpha){
        if(stack.isEmpty())return;
        var consumer=new Tint(buffers.getBuffer(Cod3GhostRenderType.of(TextureAtlas.LOCATION_BLOCKS)),tint,alpha);
        Minecraft.getInstance().getItemRenderer().renderStatic(stack,ItemDisplayContext.THIRD_PERSON_RIGHT_HAND,15728880,OverlayTexture.NO_OVERLAY,pose,type->type.format().equals(DefaultVertexFormat.NEW_ENTITY)?consumer:Discard.INSTANCE,null,0);
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
