package com.dynasty.client;

import com.dynasty.cod3.Cod3VisualPacket;
import com.mojang.blaze3d.vertex.*;
import com.mojang.math.Axis;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.phys.Vec3;
import software.bernie.geckolib.core.animatable.GeoAnimatable;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.*;
import software.bernie.geckolib.model.GeoModel;
import software.bernie.geckolib.renderer.GeoObjectRenderer;
import software.bernie.geckolib.util.GeckoLibUtil;
import java.util.*;

/** Actual textured GeckoLib rigs for distant non-combat visuals; no Entity/AI/collision registration. */
final class ScenicModels {
    private static final Map<String,GeoObjectRenderer<Actor>> RENDERERS=new HashMap<>();
    private static final Map<Cod3VisualPacket,Actor> ACTORS=new HashMap<>();
    // Own buffer: never flush another renderer's shared MultiBufferSource.
    private static final MultiBufferSource.BufferSource BUFFERS=MultiBufferSource.immediate(new BufferBuilder(65536));
    private static String id(Cod3VisualPacket p){return switch(p.sequence()){
        case "scenic_01"->"azure_dragon";case "scenic_10"->"mountain_xuanwu";case "scenic_25"->"sun_crow";default->null;
    };}
    static boolean supports(Cod3VisualPacket p){return id(p)!=null;}
    static void clear(){ACTORS.clear();}
    static void retain(List<Cod3VisualPacket> active){ACTORS.keySet().retainAll(active);}
    static final class Actor implements GeoAnimatable {
        final String id;final long start;double tick;float alpha=1;String lod="";
        private final AnimatableInstanceCache cache=GeckoLibUtil.createInstanceCache(this);
        Actor(String id,long start){this.id=id;this.start=start;}
        public AnimatableInstanceCache getAnimatableInstanceCache(){return cache;}
        public double getTick(Object ignored){return tick;}
        public void registerControllers(AnimatableManager.ControllerRegistrar registrar){
            registrar.add(new AnimationController<Actor>(this,"scenic",0,state->state.setAndContinue(RawAnimation.begin().thenLoop("animation.scenic.idle"))){
                // Absolute packet progress prevents late observers from restarting the loop.
                @Override protected double adjustTick(double ignored){return Math.max(0,tick);}
            });
        }
    }
    static String lod(double distance,boolean low){return low||distance>96?"_far":distance>32?"_medium":"";}
    static GeoObjectRenderer<Actor> renderer(String id){return renderer(id,"");}
    static GeoObjectRenderer<Actor> renderer(String id,String lod){return RENDERERS.computeIfAbsent(id+lod,key->new GeoObjectRenderer<>(new GeoModel<Actor>(){
        private ResourceLocation at(String folder,String extension){return new ResourceLocation("dynasty",folder+"/scenic/"+id+extension);}
        public ResourceLocation getModelResource(Actor a){return at("geo",lod+".geo.json");}
        public ResourceLocation getTextureResource(Actor a){return at("textures/entity",".png");}
        public ResourceLocation getAnimationResource(Actor a){return at("animations",".animation.json");}
        @Override public void applyMolangQueries(Actor a,double tick){}
    }){
        @Override public software.bernie.geckolib.core.object.Color getRenderColor(Actor a,float partial,int light){
            return software.bernie.geckolib.core.object.Color.ofRGBA(255,255,255,Math.round(255*a.alpha));
        }
    });}
    static void render(List<Cod3VisualPacket> scenes,PoseStack pose,Vec3 camera,float partial){
        var level=Minecraft.getInstance().level;if(level==null)return;
        try{
            for(var p:scenes){
                var actor=ACTORS.computeIfAbsent(p,key->new Actor(id(p),p.start()));actor.tick=level.getGameTime()-p.start()+partial;
                double life=actor.tick/p.duration();if(life<0||life>=1)continue;
                // Smooth lifetime fade, discrete texture values; this does not modify sky, fog or camera.
                float alpha=(float)(.78*Math.min(1,actor.tick/40)*Math.min(1,(p.duration()-actor.tick)/40));
                // Full render applies the actual exported animation and hierarchy.
                pose.pushPose();
                try{
                    double travel=actor.id.equals("mountain_xuanwu")?0:(life-.5)*56;
                    double rise=actor.id.equals("mountain_xuanwu")?-2+Math.sin(Math.min(1,life*4)*Math.PI/2)*3:44;
                    var forward=p.direction().multiply(1,0,1).normalize();if(forward.lengthSqr()<1e-8)forward=new Vec3(0,0,1);
                    var at=p.origin().add(forward.scale(travel)).add(0,rise,0);
                    if(at.distanceToSqr(camera)<16)continue;
                    alpha*=(float)Math.max(0,Math.min(1,(at.distanceTo(camera)-24)/16));
                    if(alpha<=0)continue;
                    // Distance is measured at the packet anchor; the elevated flying rigs remain visible.
                    actor.lod=lod(p.origin().distanceTo(camera),Minecraft.getInstance().options.particles().get()==net.minecraft.client.ParticleStatus.MINIMAL);
                    var renderer=renderer(actor.id,actor.lod);var model=renderer.getGeoModel();
                    var type=Cod3GhostRenderType.of(model.getTextureResource(actor));
                    pose.translate(at.x,at.y,at.z);pose.mulPose(Axis.YP.rotation((float)Math.atan2(forward.x,forward.z)));
                    float scale=(float)p.scale();pose.scale(scale,scale,scale);
                    // renderColor hook reads the per-draw alpha, isolated from other actor instances.
                    actor.alpha=alpha;
                    renderer.render(pose,actor,BUFFERS,type,null,15728880);
                }finally{actor.alpha=1;pose.popPose();}
            }
        }finally{BUFFERS.endBatch();}
    }
    private ScenicModels(){}
}
