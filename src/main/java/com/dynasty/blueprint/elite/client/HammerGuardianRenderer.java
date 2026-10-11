package com.dynasty.blueprint.elite.client;

import com.dynasty.blueprint.elite.*;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import software.bernie.geckolib.model.GeoModel;
import software.bernie.geckolib.renderer.GeoEntityRenderer;

@Mod.EventBusSubscriber(modid="dynasty",bus=Mod.EventBusSubscriber.Bus.MOD,value=Dist.CLIENT)
public final class HammerGuardianRenderer extends GeoEntityRenderer<HammerGuardian> {
    public HammerGuardianRenderer(EntityRendererProvider.Context context){super(context,new GeoModel<>(){
        @Override public ResourceLocation getModelResource(HammerGuardian e){return resource("geo/blueprint/elite/",HammerGuardian.ID,".geo.json");}
        @Override public ResourceLocation getTextureResource(HammerGuardian e){return resource("textures/entity/blueprint/elite/",HammerGuardian.ID,".png");}
        @Override public ResourceLocation getAnimationResource(HammerGuardian e){return resource("animations/blueprint/elite/",HammerGuardian.ID,".animation.json");}
        @Override public void setCustomAnimations(HammerGuardian e,long instanceId,software.bernie.geckolib.core.animation.AnimationState<HammerGuardian> state){
            super.setCustomAnimations(e,instanceId,state);
            long age=e.level().getGameTime()-e.skillStart();boolean dropped=e.isDeadOrDying()&&age>=12;
            for(String side:new String[]{"left","right"}){boolean thrown=side.equals("right")&&e.skillId()==363&&age>=36&&age<84;
                getBone(side+"_hammer").ifPresent(b->{b.setHidden(dropped||thrown);b.setChildrenHidden(dropped||thrown);});
                getBone("dropped_"+side+"_hammer").ifPresent(b->{b.setHidden(!dropped);b.setChildrenHidden(!dropped);});
            }
        }
    });shadowRadius=1;}
    private static ResourceLocation resource(String folder,String id,String suffix){return new ResourceLocation("dynasty",folder+id+suffix);}
    @Override protected float getDeathMaxRotation(HammerGuardian e){return 0;}
    public static final class ChainRenderer extends GeoEntityRenderer<HammerChain>{
        public ChainRenderer(EntityRendererProvider.Context context){super(context,new GeoModel<>(){
            @Override public ResourceLocation getModelResource(HammerChain e){return resource("geo/blueprint/elite/","hammer_chain",".geo.json");}
            @Override public ResourceLocation getTextureResource(HammerChain e){return resource("textures/entity/blueprint/elite/",HammerGuardian.ID,".png");}
            @Override public ResourceLocation getAnimationResource(HammerChain e){return resource("animations/blueprint/elite/","hammer_chain",".animation.json");}
        });shadowRadius=.25F;}
        @Override public void render(HammerChain e,float yaw,float partial,com.mojang.blaze3d.vertex.PoseStack pose,net.minecraft.client.renderer.MultiBufferSource buffers,int light){
            super.render(e,yaw,partial,pose,buffers,light);
            if(!(e.level().getEntity(e.ownerEntityId()) instanceof HammerGuardian caster)||!caster.isAlive())return;
            var to=caster.getPosition(partial).add(0,1.4,0).subtract(e.getPosition(partial));if(to.lengthSqr()>32*32)return;
            pose.pushPose();try{var entry=pose.last();var vertices=buffers.getBuffer(net.minecraft.client.renderer.RenderType.lines());
                // Eight bounded links sag in world space; no global render-state mutation.
                for(int i=0;i<8;i++){double a=i/8.0,b=(i+1)/8.0;var from=to.scale(a).add(0,-.15*Math.sin(Math.PI*a),0);var end=to.scale(b).add(0,-.15*Math.sin(Math.PI*b),0);var normal=end.subtract(from).normalize();
                    vertices.vertex(entry.pose(),(float)from.x,(float)from.y,(float)from.z).color(112,108,93,255).normal(entry.normal(),(float)normal.x,(float)normal.y,(float)normal.z).endVertex();
                    vertices.vertex(entry.pose(),(float)end.x,(float)end.y,(float)end.z).color(112,108,93,255).normal(entry.normal(),(float)normal.x,(float)normal.y,(float)normal.z).endVertex();
                }
            }finally{pose.popPose();}
        }
    }
    @SubscribeEvent public static void register(EntityRenderersEvent.RegisterRenderers event){event.registerEntityRenderer(EliteContent.HAMMER.get(),HammerGuardianRenderer::new);event.registerEntityRenderer(EliteContent.HAMMER_CHAIN.get(),ChainRenderer::new);}
}
