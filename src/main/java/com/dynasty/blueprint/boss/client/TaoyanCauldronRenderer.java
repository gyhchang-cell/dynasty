package com.dynasty.blueprint.boss.client;
import com.dynasty.blueprint.boss.*;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.renderer.culling.Frustum;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.phys.*;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import software.bernie.geckolib.model.GeoModel;
import software.bernie.geckolib.renderer.GeoEntityRenderer;

@Mod.EventBusSubscriber(modid="dynasty",bus=Mod.EventBusSubscriber.Bus.MOD,value=Dist.CLIENT)
public final class TaoyanCauldronRenderer extends GeoEntityRenderer<TaoyanCauldron>{
    private static ResourceLocation resource(String folder,String id,String suffix){return new ResourceLocation("dynasty",folder+id+suffix);}
    private static String form(TaoyanCauldron e){return TaoyanCauldron.ID+(e.form()==2?"_phase2":"");}
    public TaoyanCauldronRenderer(EntityRendererProvider.Context c){super(c,new GeoModel<>(){
        public ResourceLocation getModelResource(TaoyanCauldron e){return resource("geo/blueprint/boss/",form(e),".geo.json");}
        public ResourceLocation getTextureResource(TaoyanCauldron e){return resource("textures/entity/blueprint/boss/",(e.form()==2&&e.transition()&&e.level().getGameTime()-e.shifted()<32?TaoyanCauldron.ID:form(e))+"_body",".png");}
        public ResourceLocation getAnimationResource(TaoyanCauldron e){return resource("animations/blueprint/boss/",form(e),".animation.json");}
    });shadowRadius=1.7F;}
    @Override protected float getDeathMaxRotation(TaoyanCauldron e){return 0;}
    @Override public boolean shouldRender(TaoyanCauldron e,Frustum f,double x,double y,double z){return e.shouldRender(x,y,z)&&f.isVisible(new AABB(e.getX()-9,e.getY()-1,e.getZ()-9,e.getX()+9,e.getY()+9,e.getZ()+9));}
    public static final class SpellRenderer extends GeoEntityRenderer<CauldronGroundSpell>{
        public SpellRenderer(EntityRendererProvider.Context c){super(c,new GeoModel<>(){
            public ResourceLocation getModelResource(CauldronGroundSpell e){return resource("geo/blueprint/boss/",e.modelId(),".geo.json");}
            public ResourceLocation getTextureResource(CauldronGroundSpell e){return resource("textures/entity/blueprint/boss/",TaoyanCauldron.ID,".png");}
            public ResourceLocation getAnimationResource(CauldronGroundSpell e){return resource("animations/blueprint/boss/",e.modelId(),".animation.json");}
            @Override public void setCustomAnimations(CauldronGroundSpell e,long id,software.bernie.geckolib.core.animation.AnimationState<CauldronGroundSpell> s){super.setCustomAnimations(e,id,s);if(!e.oil())getBone("root").ifPresent(b->b.setScaleZ(e.length()/16));}
        });shadowRadius=0;}
        @Override protected void applyRotations(CauldronGroundSpell e,PoseStack pose,float age,float yaw,float partial){super.applyRotations(e,pose,age,e.getYRot(),partial);}
        @Override public boolean shouldRender(CauldronGroundSpell e,Frustum f,double x,double y,double z){AABB b;if(e.oil())b=new AABB(e.position(),e.position()).inflate(6.5,1,6.5);else{double a=Math.toRadians(e.getYRot());var end=e.position().add(-Math.sin(a)*e.length(),0,Math.cos(a)*e.length());b=new AABB(e.position(),end).inflate(1,1.5,1);}return e.shouldRender(x,y,z)&&f.isVisible(b);}
    }
    @SubscribeEvent public static void register(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(CauldronPitContent.CAULDRON.get(),TaoyanCauldronRenderer::new);e.registerEntityRenderer(CauldronPitContent.OIL_POOL.get(),SpellRenderer::new);e.registerEntityRenderer(CauldronPitContent.FIRE_CRACK.get(),SpellRenderer::new);}
}
