package com.dynasty.blueprint.boss.client;

import com.dynasty.blueprint.boss.*;
import net.minecraft.client.renderer.*;
import net.minecraft.client.renderer.culling.Frustum;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.phys.AABB;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import software.bernie.geckolib.core.object.Color;
import software.bernie.geckolib.model.GeoModel;
import software.bernie.geckolib.renderer.GeoEntityRenderer;

@Mod.EventBusSubscriber(modid="dynasty", bus=Mod.EventBusSubscriber.Bus.MOD, value=Dist.CLIENT)
public final class WoodKiteRenderer extends GeoEntityRenderer<WoodKite> {
    private static ResourceLocation resource(String folder, String id, String suffix) { return new ResourceLocation("dynasty", folder + id + suffix); }
    private static String form(WoodKite kite) { return WoodKite.ID + (kite.form() == 2 && !kite.transition() ? "_metal" : ""); }
    public WoodKiteRenderer(EntityRendererProvider.Context context) {
        super(context, new GeoModel<>() {
            public ResourceLocation getModelResource(WoodKite e) { return resource("geo/blueprint/boss/", form(e), ".geo.json"); }
            public ResourceLocation getTextureResource(WoodKite e) { return resource("textures/entity/blueprint/boss/", form(e), ".png"); }
            public ResourceLocation getAnimationResource(WoodKite e) { return resource("animations/blueprint/boss/", form(e), ".animation.json"); }
        });
        shadowRadius = 1.8F;
    }
    @Override protected float getDeathMaxRotation(WoodKite e) { return 0; }
    @Override public boolean shouldRender(WoodKite e, Frustum frustum, double x, double y, double z) {
        return e.shouldRender(x, y, z) && frustum.isVisible(new AABB(e.getX()-12, e.getY()-9, e.getZ()-12, e.getX()+12, e.getY()+13, e.getZ()+12));
    }
    @Override public RenderType getRenderType(WoodKite e, ResourceLocation texture, MultiBufferSource buffers, float partial) { return RenderType.entityTranslucent(texture); }
    @Override public Color getRenderColor(WoodKite e, float partial, int light) {
        float alpha = 1;
        if (e.skillId() == 526) {
            double age = e.level().getGameTime() - e.skillStart() + partial;
            if (age >= 28 && age < 36) alpha = (float)(1 - (age - 28) / 8);
            else if (age >= 36 && age < 60) alpha = 0;
            else if (age >= 60 && age < 64) alpha = (float)((age - 60) / 4);
        }
        return Color.ofRGBA(1F, 1F, 1F, Math.max(0, Math.min(1, alpha)));
    }
    public static final class BombRenderer extends GeoEntityRenderer<WoodKiteBomb> {
        public BombRenderer(EntityRendererProvider.Context context) {
            super(context, new GeoModel<>() {
                public ResourceLocation getModelResource(WoodKiteBomb e) { return resource("geo/blueprint/boss/", "wood_kite_thunder_bomb", ".geo.json"); }
                public ResourceLocation getTextureResource(WoodKiteBomb e) { return resource("textures/entity/blueprint/boss/", "wood_kite_thunder_bomb", ".png"); }
                public ResourceLocation getAnimationResource(WoodKiteBomb e) { return resource("animations/blueprint/boss/", "wood_kite_thunder_bomb", ".animation.json"); }
            }); shadowRadius = .3F;
        }
    }
    @SubscribeEvent public static void register(EntityRenderersEvent.RegisterRenderers event) {
        event.registerEntityRenderer(WoodKiteContent.KITE.get(), WoodKiteRenderer::new);
        event.registerEntityRenderer(WoodKiteContent.BOMB.get(), BombRenderer::new);
    }
}
