package com.dynasty.blueprint.client;

import com.dynasty.blueprint.BlueprintEntities;
import com.dynasty.blueprint.TemplateMob;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.ThrownItemRenderer;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.util.Mth;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import software.bernie.geckolib.renderer.GeoEntityRenderer;
import software.bernie.geckolib.core.object.Color;

@Mod.EventBusSubscriber(modid = "dynasty", bus = Mod.EventBusSubscriber.Bus.MOD, value = Dist.CLIENT)
public final class TemplateMobRenderer extends GeoEntityRenderer<TemplateMob> {
    public TemplateMobRenderer(EntityRendererProvider.Context context) {
        super(context, new TemplateMobModel());
        shadowRadius = 0.5F;
    }

    @SubscribeEvent public static void register(EntityRenderersEvent.RegisterRenderers event) {
        event.registerEntityRenderer(BlueprintEntities.ZUWU_DAOSHOU.get(), TemplateMobRenderer::new);
        event.registerEntityRenderer(BlueprintEntities.LUDUN_JIASHI.get(), TemplateMobRenderer::new);
        event.registerEntityRenderer(BlueprintEntities.FUFA_JIJIU.get(), TemplateMobRenderer::new);
        event.registerEntityRenderer(BlueprintEntities.SHANJING_SHANXIAO.get(), TemplateMobRenderer::new);
        event.registerEntityRenderer(BlueprintEntities.JUMA_CHANGQIANGBING.get(), TemplateMobRenderer::new);
        event.registerEntityRenderer(BlueprintEntities.LIANNU_ZHENZU.get(), TemplateMobRenderer::new);
        event.registerEntityRenderer(BlueprintEntities.TIESUO_CHIHOU.get(), TemplateMobRenderer::new);
        event.registerEntityRenderer(BlueprintEntities.KUIJUN_SISHI.get(), TemplateMobRenderer::new);
        event.registerEntityRenderer(BlueprintEntities.ZHENWANG_ZHANGQIGUAN.get(), TemplateMobRenderer::new);
        event.registerEntityRenderer(BlueprintEntities.PIJIA_PANJIANG_HUWEI.get(), TemplateMobRenderer::new);
        event.registerEntityRenderer(BlueprintEntities.YINBING_GUIZU.get(), TemplateMobRenderer::new);
        event.registerEntityRenderer(BlueprintEntities.SHIBIAN_LISHI.get(), TemplateMobRenderer::new);
        event.registerEntityRenderer(BlueprintEntities.FUHUN_BAIBU_TONGZI.get(), TemplateMobRenderer::new);
        event.registerEntityRenderer(BlueprintEntities.ZHIREN_JIANKE.get(), TemplateMobRenderer::new);
        event.registerEntityRenderer(BlueprintEntities.CORPSE_MIASMA.get(), net.minecraft.client.renderer.entity.NoopRenderer::new);
        event.registerEntityRenderer(BlueprintEntities.ARMY_CALTROP.get(), ThrownItemRenderer::new);
        event.registerEntityRenderer(BlueprintEntities.TEMPLATE_PROJECTILE.get(), ThrownItemRenderer::new);
    }

    @Override public void render(TemplateMob mob, float yaw, float partialTick, PoseStack pose,
                                 MultiBufferSource buffers, int light) {
        pose.pushPose();
        try {
            if (mob.isPossessed()) pose.scale(1.15F, 1.15F, 1.15F);
            super.render(mob, yaw, partialTick, pose, buffers, light);
        } finally {
            pose.popPose();
        }
    }

    @Override protected float getDeathMaxRotation(TemplateMob mob) {
        // Authored kneeling/collapse clips own death rotation; vanilla's 90-degree roll would
        // tip the shield cover onto its side for its remaining server-authoritative lifetime.
        return 0;
    }

    @Override protected void applyRotations(TemplateMob mob, PoseStack pose, float age, float bodyYaw, float partialTick) {
        var wall = mob.climbFace();
        if (mob.kind() != TemplateMob.Kind.BEAST || !mob.isAlive() || mob.skillId() != 0
                || !mob.onClimbable() || wall == null) {
            super.applyRotations(mob, pose, age, bodyYaw, partialTick);
            return;
        }
        // Bind the authored ground plane to the measured wall, not to the target's yaw.
        // Model +Y points away from stone; model -Z climbs upward. The .88 rise keeps
        // the short tail above the floor at first contact. This is strictly visual:
        // the server's physical position, navigation and attack origin are untouched.
        double distance = Math.max(0, mob.climbContactDistance() - .02);
        pose.translate(wall.getStepX() * distance, .88, wall.getStepZ() * distance);
        pose.mulPose(Axis.YP.rotationDegrees(180F - wall.toYRot()));
        pose.mulPose(Axis.XP.rotationDegrees(90F));
    }

    @Override public void renderRecursively(PoseStack pose,TemplateMob mob,software.bernie.geckolib.cache.object.GeoBone bone,
            net.minecraft.client.renderer.RenderType type,MultiBufferSource buffers,com.mojang.blaze3d.vertex.VertexConsumer sink,
            boolean rerender,float partial,int light,int overlay,float red,float green,float blue,float alpha) {
        boolean vein=mob.kind()==TemplateMob.Kind.CORPSE&&bone.getName().startsWith("vein_");
        super.renderRecursively(pose,mob,bone,type,buffers,sink,rerender,partial,vein||mob.kind()==TemplateMob.Kind.CHILD&&bone.getName().equals("lantern_flame")?15728880:light,overlay,
            vein?.75F:red,vein?.25F:green,vein?1F:blue,alpha);
    }

    @Override public Color getRenderColor(TemplateMob mob, float partialTick, int light) {
        if (mob.kind() == TemplateMob.Kind.GHOST) return Color.ofRGBA(.55F,.85F,1F,mob.isPhased()?.18F:.65F);
        if (mob.kind() == TemplateMob.Kind.BEAST && mob.isDeadOrDying()) {
            // The native blue-green fur loses its cool hue toward dry charcoal as it curls.
            // Use the synchronized death clock, so late observers do not restart the fade.
            // Vertex tint needs neither a second texture nor an extra render pass/entity.
            float fade = Mth.clamp((mob.actionAge(partialTick) - 6F) / 26F, 0F, 1F);
            return Color.ofRGB(1F - .10F * fade, 1F - .26F * fade, 1F - .46F * fade);
        }
        return super.getRenderColor(mob, partialTick, light);
    }

    @Override public net.minecraft.client.renderer.RenderType getRenderType(TemplateMob mob,
            net.minecraft.resources.ResourceLocation texture,MultiBufferSource buffers,float partialTick){
        return mob.kind()==TemplateMob.Kind.GHOST?net.minecraft.client.renderer.RenderType.entityTranslucent(texture)
            :super.getRenderType(mob,texture,buffers,partialTick);
    }

    @Override public int getPackedOverlay(TemplateMob mob, float u, float partialTick) {
        // The shield remnant is usable cover for ten seconds, not a ten-second hurt flash.
        // Keep the initial vanilla impact flash, then restore its authored metal/wood colours.
        if (mob.isDeadOrDying() && mob.hurtTime <= 0) return OverlayTexture.NO_OVERLAY;
        return super.getPackedOverlay(mob, u, partialTick);
    }
}
