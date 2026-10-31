package com.yellowbrossproductions.illageandspillage.client.render;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.mojang.math.Axis;
import com.yellowbrossproductions.illageandspillage.client.model.SpiritcallerModel;
import com.yellowbrossproductions.illageandspillage.client.render.layer.SpiritcallerArmorLayer;
import com.yellowbrossproductions.illageandspillage.client.render.layer.SpiritcallerFakerLayer;
import com.yellowbrossproductions.illageandspillage.client.render.layer.SpiritcallerGlowLayer;
import com.yellowbrossproductions.illageandspillage.entities.SpiritcallerEntity;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.culling.Frustum;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.client.renderer.entity.layers.CustomHeadLayer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import org.joml.Matrix4f;

import java.util.Random;

@OnlyIn(Dist.CLIENT)
public class SpiritcallerRenderer extends MobRenderer<SpiritcallerEntity, SpiritcallerModel<SpiritcallerEntity>> {
    private static final ResourceLocation TEXTURE = new ResourceLocation("illageandspillage", "textures/entity/spiritcaller/spiritcaller_inactive.png");
    private static final ResourceLocation ACTIVE = new ResourceLocation("illageandspillage", "textures/entity/spiritcaller/spiritcaller.png");
    private static final ResourceLocation DEATH = new ResourceLocation("illageandspillage", "textures/entity/spiritcaller/spiritcaller_death.png");
    private static final ResourceLocation NOTHING = new ResourceLocation("illageandspillage", "textures/entity/magispeller/magispeller_nothing.png");
    private static final float HALF_SQRT_3 = (float) (Math.sqrt(3.0) / 2.0);

    public SpiritcallerRenderer(EntityRendererProvider.Context renderManagerIn) {
        super(renderManagerIn, new SpiritcallerModel<>(renderManagerIn.bakeLayer(SpiritcallerModel.LAYER_LOCATION)), 0.5F);
        this.addLayer(new SpiritcallerGlowLayer<>(this));
        this.addLayer(new SpiritcallerArmorLayer<>(this));
        this.addLayer(new SpiritcallerFakerLayer<>(this));
        this.addLayer(new CustomHeadLayer<>(this, renderManagerIn.getModelSet(), renderManagerIn.getItemInHandRenderer()));
    }

    public Vec3 getRenderOffset(SpiritcallerEntity p_114336_, float p_114337_) {
        if (p_114336_.getRitualTicks() > 30 && !p_114336_.isActive()) {
            return new Vec3(p_114336_.getRandom().nextGaussian() * 5.217391304347826E-4 * (double) (p_114336_.getRitualTicks() - 30), 0.0, p_114336_.getRandom().nextGaussian() * 5.217391304347826E-4 * (double) (p_114336_.getRitualTicks() - 30));
        } else if (p_114336_.isDeadOrDying() && p_114336_.isActive()) {
            return new Vec3(p_114336_.getRandom().nextGaussian() * 0.15, p_114336_.getRandom().nextGaussian() * 0.15, p_114336_.getRandom().nextGaussian() * 0.15);
        } else if (p_114336_.isClap()) {
            return new Vec3(p_114336_.getRandom().nextGaussian() * 0.25, p_114336_.getRandom().nextGaussian() * 0.25, p_114336_.getRandom().nextGaussian() * 0.25);
        } else {
            return p_114336_.isShootingLaser() ? new Vec3(p_114336_.getRandom().nextGaussian() * 0.06, p_114336_.getRandom().nextGaussian() * 0.06, p_114336_.getRandom().nextGaussian() * 0.06) : super.getRenderOffset(p_114336_, p_114337_);
        }
    }

    protected float getWhiteOverlayProgress(SpiritcallerEntity caller, float p_114044_) {
        return (float) caller.getSoulPower() / 10.0F;
    }

    protected float getFlipDegrees(SpiritcallerEntity p_115337_) {
        return p_115337_.isActive() ? 0.0F : super.getFlipDegrees(p_115337_);
    }

    protected void scale(SpiritcallerEntity p_115314_, PoseStack p_115315_, float p_115316_) {
        if (p_115314_.isDeadOrDying()) {
            p_115315_.scale(1.0F - (float) (p_115314_.deathTime / 131 / 2), 1.0F - (float) (p_115314_.deathTime / 131 / 2), 1.0F - (float) (p_115314_.deathTime / 131 / 2));
        } else {
            super.scale(p_115314_, p_115315_, p_115316_);
        }

    }

    public void render(SpiritcallerEntity p_115455_, float p_115456_, float p_115457_, PoseStack p_115458_, MultiBufferSource p_115459_, int p_115460_) {
        super.render(p_115455_, p_115456_, p_115457_, p_115458_, p_115459_, p_115460_);
        if (p_115455_.deathTime > 0 && p_115455_.isActive()) {
            float f5 = ((float) p_115455_.deathTime + p_115457_) / 200.0F;
            float f7 = Math.min(f5 > 0.8F ? (f5 - 0.8F) / 0.2F : 0.0F, 1.0F);
            Random random = new Random(432L);
            VertexConsumer vertexconsumer2 = p_115459_.getBuffer(RenderType.lightning());
            p_115458_.pushPose();
            p_115458_.translate(0.0, 1.0, 0.0);
            p_115458_.scale(((float) p_115455_.deathTime + p_115457_) / 131.0F / 2.0F, ((float) p_115455_.deathTime + p_115457_) / 131.0F / 2.0F, ((float) p_115455_.deathTime + p_115457_) / 131.0F / 2.0F);

            for (int i = 0; (float) i < (f5 + f5 * f5) / 2.0F * 60.0F; ++i) {
                p_115458_.mulPose(Axis.XP.rotationDegrees(random.nextFloat() * 360.0F));
                p_115458_.mulPose(Axis.YP.rotationDegrees(random.nextFloat() * 360.0F));
                p_115458_.mulPose(Axis.ZP.rotationDegrees(random.nextFloat() * 360.0F));
                p_115458_.mulPose(Axis.XP.rotationDegrees(random.nextFloat() * 360.0F));
                p_115458_.mulPose(Axis.YP.rotationDegrees(random.nextFloat() * 360.0F));
                p_115458_.mulPose(Axis.ZP.rotationDegrees(random.nextFloat() * 360.0F + f5 * 90.0F));
                float f3 = random.nextFloat() * 20.0F + 5.0F + f7 * 10.0F;
                float f4 = random.nextFloat() * 2.0F + 1.0F + f7 * 2.0F;
                Matrix4f matrix4f = p_115458_.last().pose();
                int j = (int) (255.0F * (1.0F - f7));
                vertex01(vertexconsumer2, matrix4f, j);
                vertex2(vertexconsumer2, matrix4f, f3, f4);
                vertex3(vertexconsumer2, matrix4f, f3, f4);
                vertex01(vertexconsumer2, matrix4f, j);
                vertex3(vertexconsumer2, matrix4f, f3, f4);
                vertex4(vertexconsumer2, matrix4f, f3, f4);
                vertex01(vertexconsumer2, matrix4f, j);
                vertex4(vertexconsumer2, matrix4f, f3, f4);
                vertex2(vertexconsumer2, matrix4f, f3, f4);
            }

            p_115458_.popPose();
        }

    }

    private static void vertex01(VertexConsumer p_114220_, Matrix4f p_114221_, int p_114222_) {
        p_114220_.vertex(p_114221_, 0.0F, 0.0F, 0.0F).color(255, 255, 255, p_114222_).endVertex();
    }

    private static void vertex2(VertexConsumer p_114215_, Matrix4f p_114216_, float p_114217_, float p_114218_) {
        p_114215_.vertex(p_114216_, -HALF_SQRT_3 * p_114218_, p_114217_, -0.5F * p_114218_).color(0, 255, 255, 0).endVertex();
    }

    private static void vertex3(VertexConsumer p_114224_, Matrix4f p_114225_, float p_114226_, float p_114227_) {
        p_114224_.vertex(p_114225_, HALF_SQRT_3 * p_114227_, p_114226_, -0.5F * p_114227_).color(255, 0, 0, 0).endVertex();
    }

    private static void vertex4(VertexConsumer p_114229_, Matrix4f p_114230_, float p_114231_, float p_114232_) {
        p_114229_.vertex(p_114230_, 0.0F, p_114231_, p_114232_).color(255, 255, 255, 0).endVertex();
    }

    @Override
    public boolean shouldRender(SpiritcallerEntity p_115468_, Frustum p_115469_, double p_115470_, double p_115471_, double p_115472_) {
        return !p_115468_.isPhasedOut() && super.shouldRender(p_115468_, p_115469_, p_115470_, p_115471_, p_115472_);
    }

    public ResourceLocation getTextureLocation(SpiritcallerEntity p_110775_1_) {
        if (p_110775_1_.isDeadOrDying() && p_110775_1_.isActive()) {
            return DEATH;
        } else if (p_110775_1_.isFaking()) {
            return NOTHING;
        } else {
            return p_110775_1_.isActive() ? ACTIVE : TEXTURE;
        }
    }
}
