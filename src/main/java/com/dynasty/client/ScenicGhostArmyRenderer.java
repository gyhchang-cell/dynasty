package com.dynasty.client;

import com.dynasty.cod3.*;
import com.mojang.blaze3d.vertex.*;
import com.mojang.blaze3d.systems.RenderSystem;
import net.minecraft.client.*;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.renderer.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.phys.Vec3;
import software.bernie.geckolib.core.animatable.GeoAnimatable;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.*;
import software.bernie.geckolib.model.GeoModel;
import software.bernie.geckolib.renderer.GeoObjectRenderer;
import software.bernie.geckolib.util.GeckoLibUtil;
import java.util.*;

/** Nonphysical world-space procession, independent pose cache per soldier; distant white muster lights. */
final class ScenicGhostArmyRenderer {
    private record Check(long tick,boolean valid){}
    private static final Map<Cod3VisualPacket,Check> CHECKS=new HashMap<>();
    private static final Map<Cod3VisualPacket,List<Actor>> ACTORS=new HashMap<>();
    private static final Map<String,GeoObjectRenderer<Actor>> RENDERERS=new HashMap<>();
    private static final MultiBufferSource.BufferSource MODELS=MultiBufferSource.immediate(new BufferBuilder(262144));
    private static final BufferBuilder LIGHTS=new BufferBuilder(16384);
    private static ClientLevel world;
    static int lastSoldiers,lastWhiteQuads;static String lastLod="";static double lastAge;
    static void clear(){CHECKS.clear();ACTORS.clear();world=null;lastSoldiers=lastWhiteQuads=0;lastLod="";}
    static boolean valid(ClientLevel level,Cod3VisualPacket p){
        if(world!=level){clear();world=level;}if(ScenicGhostArmySite.visibility(level)<=0)return false;
        var old=CHECKS.get(p);long now=level.getGameTime();
        if(old==null||now<old.tick()||now-old.tick()>=20){old=new Check(now,ScenicGhostArmySite.valid(level,p.origin()));CHECKS.put(p,old);}
        return old.valid();
    }
    private static final class Actor implements GeoAnimatable {
        double tick;float alpha;final AnimatableInstanceCache cache=GeckoLibUtil.createInstanceCache(this);
        public AnimatableInstanceCache getAnimatableInstanceCache(){return cache;}
        public double getTick(Object ignored){return tick;}
        public void registerControllers(AnimatableManager.ControllerRegistrar registrar){
            registrar.add(new AnimationController<Actor>(this,"procession",0,state->state.setAndContinue(RawAnimation.begin().thenLoop("animation.scenic.idle"))){
                @Override protected double adjustTick(double ignored){shouldResetTick=false;return Math.max(0,Actor.this.tick)%80;}
            });
        }
    }
    private static GeoObjectRenderer<Actor> renderer(String lod){return RENDERERS.computeIfAbsent(lod,key->new GeoObjectRenderer<>(new GeoModel<Actor>(){
        private ResourceLocation at(String folder,String suffix){return ResourceLocation.fromNamespaceAndPath("dynasty",folder+"/scenic/ghost_army_soldier"+suffix);}
        public ResourceLocation getModelResource(Actor a){return at("geo",lod+".geo.json");}
        public ResourceLocation getTextureResource(Actor a){return at("textures/entity",".png");}
        public ResourceLocation getAnimationResource(Actor a){return at("animations",".animation.json");}
        @Override public void applyMolangQueries(Actor a,double tick){}
    }){
        @Override public void preRender(PoseStack pose,Actor a,software.bernie.geckolib.cache.object.BakedGeoModel model,MultiBufferSource source,VertexConsumer buffer,boolean reRender,float partial,int light,int overlay,float red,float green,float blue,float alpha){
            super.preRender(pose,a,model,source,buffer,reRender,partial,light,overlay,red,green,blue,alpha);
            pose.translate(-.5f,-.51f,-.5f);
        }
        @Override public software.bernie.geckolib.core.object.Color getRenderColor(Actor a,float partial,int light){return software.bernie.geckolib.core.object.Color.ofRGBA(226,237,245,Math.round(255*a.alpha));}
    });}
    static void render(List<Cod3VisualPacket> scenes,PoseStack pose,Vec3 camera,float partial){
        lastSoldiers=lastWhiteQuads=0;lastLod="";var level=Minecraft.getInstance().level;if(level==null)return;
        CHECKS.keySet().retainAll(scenes);ACTORS.keySet().retainAll(scenes);
        var packet=scenes.stream().filter(p->valid(level,p)).min(Comparator.comparingDouble(p->p.origin().distanceToSqr(camera))).orElse(null);if(packet==null)return;
        double age=level.getGameTime()-packet.start()+partial,distance=packet.origin().distanceTo(camera);lastAge=age;if(age<0||age>=packet.duration())return;
        float alpha=(float)ScenicGhostArmySite.alpha(age,packet.duration(),distance,ScenicGhostArmySite.visibility(level));if(alpha<=0)return;
        boolean low=Minecraft.getInstance().options.particles().get()==ParticleStatus.MINIMAL;double far=ScenicGhostArmySite.farBlend(distance,low);
        if(far<1){
            var actors=ACTORS.computeIfAbsent(packet,p->{var list=new ArrayList<Actor>();for(int i=0;i<ScenicGhostArmySite.SOLDIERS;i++)list.add(new Actor());return list;});
            String lod=distance>72?"_far":distance>40?"_medium":"";lastLod=lod.isEmpty()?"full":lod;
            var renderer=renderer(lod);
            try{
                for(int i=0;i<actors.size();i++){
                    var actor=actors.get(i);actor.tick=age+(i/6)*7;actor.alpha=alpha*(float)(1-far);
                    var at=ScenicGhostArmySite.position(packet.origin(),i,age);pose.pushPose();
                    try{pose.translate(at.x,at.y,at.z);var type=Cod3GhostRenderType.of(renderer.getGeoModel().getTextureResource(actor));renderer.render(pose,actor,MODELS,type,MODELS.getBuffer(type),15728880);lastSoldiers++;}
                    finally{actor.alpha=0;pose.popPose();}
                }
            }finally{MODELS.endBatch();}
        }
        if(far>0){
            boolean drawing=false;
            try{
                RenderSystem.setShader(GameRenderer::getPositionColorShader);RenderSystem.enableBlend();RenderSystem.defaultBlendFunc();RenderSystem.depthMask(false);RenderSystem.disableCull();
                LIGHTS.begin(VertexFormat.Mode.TRIANGLES,DefaultVertexFormat.POSITION_COLOR);drawing=true;var matrix=pose.last().pose();
                // Each pair remains tied to a real formation slot. No random positions or full-screen mist.
                for(int i=0;i<ScenicGhostArmySite.SOLDIERS;i++)for(int j=0;j<2;j++){
                    var at=ScenicGhostArmySite.position(packet.origin(),i,age).add(0,j==0?1.1:2.1,0);
                    var right=camera.subtract(at).cross(new Vec3(0,1,0)).normalize().scale(.14);if(right.lengthSqr()<1e-8)right=new Vec3(.14,0,0);
                    var up=new Vec3(0,.14,0);var a=at.subtract(right).subtract(up);var b=at.add(right).subtract(up);var c=at.add(right).add(up);var d=at.subtract(right).add(up);
                    for(var point:List.of(a,b,c,a,c,d))LIGHTS.vertex(matrix,(float)point.x,(float)point.y,(float)point.z).color(235,243,249,Math.round(255*alpha*(float)far)).endVertex();lastWhiteQuads++;
                }
                BufferUploader.drawWithShader(LIGHTS.end());drawing=false;
            }finally{if(drawing)LIGHTS.discard();}
        }
    }
    private ScenicGhostArmyRenderer(){}
}
