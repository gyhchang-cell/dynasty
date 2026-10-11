package com.dynasty.blueprint.elite.client;

import com.dynasty.blueprint.elite.*;
import net.minecraft.client.renderer.entity.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import software.bernie.geckolib.model.GeoModel;
import software.bernie.geckolib.renderer.GeoEntityRenderer;

@Mod.EventBusSubscriber(modid="dynasty",bus=Mod.EventBusSubscriber.Bus.MOD,value=Dist.CLIENT)
public final class AlchemistRenderer extends GeoEntityRenderer<Alchemist> {
    private static ResourceLocation resource(String folder,String id,String suffix){return new ResourceLocation("dynasty",folder+id+suffix);}
    public AlchemistRenderer(EntityRendererProvider.Context context){super(context,new GeoModel<>(){
        @Override public ResourceLocation getModelResource(Alchemist e){return resource("geo/blueprint/elite/",Alchemist.ID,".geo.json");}
        @Override public ResourceLocation getTextureResource(Alchemist e){return resource("textures/entity/blueprint/elite/",Alchemist.ID,".png");}
        @Override public ResourceLocation getAnimationResource(Alchemist e){return resource("animations/blueprint/elite/",Alchemist.ID,".animation.json");}
        @Override public void setCustomAnimations(Alchemist e,long id,software.bernie.geckolib.core.animation.AnimationState<Alchemist> state){super.setCustomAnimations(e,id,state);for(int i=0;i<3;i++)getBone("gold"+i).ifPresent(b->b.setHidden(e.skillId()!=383||e.isDeadOrDying()));}
    });shadowRadius=.75F;}
    @Override protected float getDeathMaxRotation(Alchemist e){return 0;}
    public static final class OrbRenderer extends GeoEntityRenderer<AlchemistOrb> {
        public OrbRenderer(EntityRendererProvider.Context context){super(context,new GeoModel<>(){
            @Override public ResourceLocation getModelResource(AlchemistOrb e){return resource("geo/blueprint/elite/",AlchemistOrb.ID,".geo.json");}
            @Override public ResourceLocation getTextureResource(AlchemistOrb e){return resource("textures/entity/blueprint/elite/",Alchemist.ID,".png");}
            @Override public ResourceLocation getAnimationResource(AlchemistOrb e){return resource("animations/blueprint/elite/",AlchemistOrb.ID,".animation.json");}
            @Override public void setCustomAnimations(AlchemistOrb e,long id,software.bernie.geckolib.core.animation.AnimationState<AlchemistOrb> state){super.setCustomAnimations(e,id,state);for(String name:new String[]{"warm","cold","pill"})getBone(name).ifPresent(b->{boolean shown=e.pill()?name.equals("pill"):name.equals(e.side()>0?"warm":"cold");b.setHidden(!shown);b.setChildrenHidden(!shown);});}
        });shadowRadius=.15F;}
        @Override protected int getBlockLightLevel(AlchemistOrb e,net.minecraft.core.BlockPos pos){return 15;}
    }
    @SubscribeEvent public static void register(EntityRenderersEvent.RegisterRenderers event){event.registerEntityRenderer(EliteContent.ALCHEMIST.get(),AlchemistRenderer::new);event.registerEntityRenderer(EliteContent.ALCHEMIST_ORB.get(),OrbRenderer::new);event.registerEntityRenderer(EliteContent.ALCHEMIST_ZONE.get(),NoopRenderer::new);}
}
